# AudioRAG — Hybrid Audio Search

## Problem

Audio recordings such as interviews, meetings, podcasts, and customer conversations contain valuable information, but searching them effectively is difficult.

A useful audio search system should be able to:

- Understand what was said.
- Identify which speaker said it.
- Retrieve information using both exact keywords and semantic meaning.
- Return precise timestamps so users can verify the result directly in the recording.
- Handle paraphrased queries, speaker-specific queries, and ambiguous terms.
- Provide grounded answers instead of unsupported LLM responses.

## Proposed Solution

AudioRAG is a hybrid audio-search system that converts two-speaker audio recordings into searchable, speaker-aware transcript chunks.

The system combines local speech processing, speaker diarization, PostgreSQL full-text search, pgvector semantic retrieval, reciprocal rank fusion, cross-encoder reranking, and grounded answer generation.

The core ingestion and retrieval pipeline is:

```text
                         Audio
                           │
                       Validation
                           │
                    16 kHz Mono WAV
                           │
              ┌────────────┴────────────┐
              │                         │
              ▼                         ▼
          Pyannote                   Whisper
       Speaker + Time              Text + Time
              │                         │
              └────────────┬────────────┘
                           ▼
                  Timestamp Alignment
                           │
                           ▼
                 Speaker-Aware Chunks
                           │
                     PII Redaction
                           │
              ┌────────────┴────────────┐
              ▼                         ▼
       Lexical Search             Vector Search
       PostgreSQL FTS                pgvector
              │                         │
              └────────────┬────────────┘
                           ▼
                       RRF Fusion
                           │
                       Reranking
                           │
                    Top-K Evidence
                           │
                  Context Compression
                           │
                     Grounded LLM
                           │
                  Answer + Citations
```

Pyannote and Whisper independently process the normalized audio. Pyannote provides speaker/time segments, while Whisper provides transcript words with timestamps. The two timestamp streams are aligned to create speaker-aware transcript chunks.

## Core Engineering Hypothesis

The system is designed around the hypothesis that combining lexical and semantic retrieval improves retrieval quality across a mixed query workload.

Lexical retrieval is expected to be useful when the query contains exact terms appearing in the transcript.

Semantic retrieval is expected to be useful when the query uses different wording or paraphrases the underlying statement.

Hybrid retrieval combines both signals using Reciprocal Rank Fusion (RRF), while cross-encoder reranking is used to improve ordering among the strongest candidates.

The evaluation therefore compares:

- Lexical-only retrieval
- Semantic-only retrieval
- Hybrid retrieval with RRF
- Hybrid retrieval with RRF followed by reranking

The goal is not only to build a working search system, but to measure how each retrieval stage affects retrieval quality.

## Key Features

### 1. Speaker-aware transcription

The system identifies speaker turns during ingestion and aligns them with word-level ASR timestamps.

Each searchable chunk preserves:

- Audio file
- Speaker
- Transcript
- Start timestamp
- End timestamp
- Redacted content
- Embedding
- Lexical search representation

Speaker identity is part of the searchable evidence rather than only display metadata. This allows the system to distinguish semantically similar statements made by different speakers and support speaker-specific queries.

Example:

```text
File: customer_interview.wav
Speaker: SPEAKER_01
Time: 04:32 – 04:48

"We were concerned about the pricing model..."
```

### 2. Hybrid retrieval

Search combines:

- PostgreSQL Full-Text Search for lexical matching
- pgvector for semantic similarity
- Reciprocal Rank Fusion (RRF) to combine rankings
- Cross-encoder reranking for final candidate ordering

The retrieval pipeline is:

```text
Query
  │
  ├──► PostgreSQL FTS ──────► Top 50
  │
  └──► pgvector ────────────► Top 50
                    │
                    ▼
                  RRF
                    │
                 Top 20
                    │
                    ▼
              BGE Reranker
                    │
                  Top 5
```

If semantic retrieval fails, the system can fall back to lexical results.

If reranking fails, the RRF ordering is retained.

### 3. Speaker-aware retrieval

Speaker information is preserved throughout the retrieval pipeline.

This enables queries such as:

```text
"What did Speaker 01 say about deployment?"
```

and helps distinguish similar statements made by different speakers or across different recordings.

Speaker, file, and timestamp information remain attached to each retrieved evidence chunk.

### 4. Grounded answers

The LLM receives retrieved evidence rather than the entire recording.

The answer-generation stage is expected to:

- Use only retrieved evidence.
- Avoid unsupported claims.
- Preserve source traceability.
- Return citations for the evidence used.
- Fall back to retrieved evidence and citations if generation fails.

Retrieved transcript content is treated as untrusted data and must not override application instructions.

### 5. Timestamp-based citations

Each result can point back to the relevant location in the original audio.

Example:

```text
File: customer_interview.wav
Speaker: SPEAKER_01
Time: 04:32 – 04:48
```

The frontend can use the timestamp to seek directly into the recording.

### 6. Safety and reliability

The planned system includes:

- PII redaction before indexing
- Prompt-injection protection
- Out-of-scope query handling
- Evidence-grounded generation
- Structured output validation
- Retrieval fallback behavior
- Reranking fallback behavior
- LLM fallback behavior
- Path traversal protection for audio playback

## Technology Stack

### Backend

- Python
- FastAPI
- Pydantic

### Audio / AI

- pyannote.audio — speaker diarization
- faster-whisper — speech recognition
- sentence-transformers — embeddings
- BAAI/bge-small-en-v1.5 — 384-dimensional text embeddings
- BAAI/bge-reranker-base — candidate reranking

### Database

- PostgreSQL
- pgvector
- PostgreSQL Full-Text Search

The searchable chunk representation contains:

```text
file_id
speaker
start_ts
end_ts
content
content_redacted
embedding
tsv
```

The database uses:

- GIN indexing for PostgreSQL Full-Text Search
- pgvector cosine-similarity indexing for semantic retrieval

### LLM

- Google Gemini — primary generation model
- Groq — fallback generation model

### Frontend

- React
- TypeScript
- Vite

### Observability

- Structured stage logging
- Trace IDs
- OpenTelemetry where practical

## Retrieval Strategy

For each query:

1. Validate the query using guardrails.
2. Run lexical search.
3. Run semantic vector search.
4. Retrieve the top candidate set from each.
5. Combine rankings using Reciprocal Rank Fusion.
6. Keep the strongest fused candidates.
7. Rerank candidates using a cross-encoder.
8. Select the strongest evidence.
9. Compress evidence when required.
10. Generate a grounded answer with citations.

The RRF score is:

```text
RRF(d) = Σ 1 / (k + rank(d))
```

with:

```text
k = 60
```

The detailed retrieval and failure-handling design follows the architecture document.

## Evaluation

The labeled set is `eval/golden_queries.json`: 23 queries over the five indexed interviews. Twenty queries have `relevant_chunks` spans. Three are hard negatives (queries 8, 22, and 23) and are not averaged into Recall@k.

A hit matches a label when the file, speaker, and time overlap. Any shared time counts. The scorer reads `relevant_chunks`.

Primary retrieval metrics:

- Recall@1
- Recall@3
- Recall@5
- Precision@5
- Mean Reciprocal Rank (MRR)

The harness is `python -m tests.eval_recall`. It writes `eval/results.md`.

Indexed recordings used for that run:

| File | Chunks | Duration |
| --- | --- | --- |
| AI_Engineering_Mock_Interview.wav | 20 | 8:00 |
| Google_Coding_Interview.wav | 36 | 8:00 |
| System_Design_of_ChatGPT.wav | 36 | 8:00 |
| Behavioral_mock_Interview.wav | 17 | 6:12 |
| llm_systems_interview.wav | 23 | 8:00 |

llm_systems_interview.wav is an excerpt from a publicly released podcast episode discussing AI systems and safety; it is included in this dataset solely for hackathon evaluation and educational purposes, and speaker names within it are redacted in all indexed and displayed transcript output per this project's PII redaction policy.

## Retrieval Ablation

The same 20 labeled queries were run in four modes:

| mode | Recall@1 | Recall@3 | Recall@5 | Precision@5 | MRR | queries |
| --- | --- | --- | --- | --- | --- | --- |
| lexical | 0.250 | 0.600 | 0.600 | 0.140 | 0.373 | 20 |
| semantic | 0.500 | 0.750 | 0.900 | 0.260 | 0.650 | 20 |
| hybrid_rrf | 0.350 | 0.600 | 0.750 | 0.190 | 0.539 | 20 |
| hybrid | 0.450 | 0.750 | 0.800 | 0.230 | 0.596 | 20 |

On this set, semantic retrieval has the highest Recall@5 (0.900), Precision@5 (0.260), and MRR (0.650). Hybrid + rerank is above lexical and hybrid/RRF on Recall@1 and MRR, and below semantic on Recall@5.

Hard negatives, scored separately. A pass means no top-5 chunk has `rerank_score >= -5.0`. Lexical, semantic, and hybrid/RRF do not set a rerank score, so they pass. Hybrid + rerank fails all three because the cross-encoder returns sigmoid scores in `(0, 1)`, which are always above `-5.0`.

| id | query_type | lexical | semantic | hybrid_rrf | hybrid |
| --- | --- | --- | --- | --- | --- |
| 8 | speaker_specific | PASS | PASS | PASS | FAIL |
| 22 | hard_negative | PASS | PASS | PASS | FAIL |
| 23 | hard_negative | PASS | PASS | PASS | FAIL |

`relevance_min_logit` stays at `-5.0` so none of the 20 labeled queries are withheld. A single absolute cutoff cannot separate them from hard negatives: query 1's genuine top score is 0.000443, between hard-negative maxima 0.0000652 and 0.000774. Rerank scores only rank candidates inside one query. See `eval/known_failures.md` for queries 17, 20, and 21.

## Success Criteria

The initial target is:

```text
Recall@5     >= 0.80
Precision@5  >= 0.60
MRR          >= 0.70
```

These are targets. On the 20 labeled queries, semantic retrieval reaches Recall@5 0.900 and misses Precision@5 (0.260) and MRR (0.650). Hybrid + rerank reaches Recall@5 0.800 and misses the other two targets. The full comparison is in the ablation table above.

## Demo

The UI at `http://127.0.0.1:5173` already runs this flow. The search control selects Lexical only, Semantic only, Hybrid / RRF, or Hybrid + rerank. Each hit shows the file, speaker, timestamps, and a Play from button on one shared audio element.

```text
Upload audio
      ↓
Process recording
      ↓
Speaker-aware indexing
      ↓
Search transcript
      ↓
Hybrid retrieval
      ↓
Reranking
      ↓
Show grounded answer
      ↓
Display file + speaker + timestamp
      ↓
Play audio from citation timestamp
```

A representative search result should make it possible to answer:

```text
What was said?
Who said it?
Which recording contained it?
Where in the recording did it occur?
Why was it retrieved?
```

## Project Status

Ingestion, search, and the React UI are running. Diarization is fixed at 2 speakers and Whisper is fixed to English. Pyannote receives an in-memory waveform. Answers try Gemini (`gemini-3.8-flash`), then Groq, then evidence with citations.

Measured retrieval numbers are in `eval/results.md` and in the ablation table above. They come from `python -m tests.eval_recall` on `eval/golden_queries.json`. They are not targets. Semantic Recall@5 is 0.900, which meets the 0.80 Recall@5 target. Precision@5 and MRR stay below their targets in every mode.

## Coding Agent Transparency

If an AI coding agent is used during implementation, its usage, human direction, generated changes, validation, and important architectural decisions will be documented in the project disclosure and agent log.

See:

- `AGENT-DISCLOSURE.md`
- `agent_log.md`

The agent log is intended to record significant prompts and decisions during the official hacking window rather than reconstructing interactions afterward.

## Architecture Constraint

The implementation should preserve the core architecture:

```text
Diarization
→ ASR
→ Timestamp Alignment
→ Speaker-aware chunks
→ PII redaction
→ Lexical + Vector retrieval
→ RRF
→ Reranking
→ Evidence compression
→ Grounded generation
→ Citations
```

Implementation details may evolve during the hackathon based on time, environment, and validation results.

Any significant architectural deviation should be documented along with the reason and validation outcome.

## Limitations

The initial system has several known limitations:

- The golden set is 23 queries on five recordings.
- The one normal speaker-specific query (query 6) has Recall@5 of 0.000 in all four modes. Speaker is stored on every chunk and filters retrieval only when the query names a speaker.
- Query 17: the reranker promoted a chunk with cosine similarity 0.723 over System_Design chunks at 0.777 and 0.757.
- Query 20: the labeled chunk was semantic rank 30 and rerank rank 11, so it missed the top 5.
- Query 21: the hybrid-search chunk had cosine similarity 0.661 and semantic rank 5, behind two higher-scoring chunks.
- Rerank scores are only a ranking inside one query. Query 1's real top score (0.000443) sits between hard-negative maxima (0.0000652 and 0.000774), so `relevance_min_logit` stays at `-5.0` and does not withhold. A later guard would need an LLM check of the top hit, or a top-1 versus top-2 gap, not a lower absolute cutoff.
- ASR and diarization errors still change the text that is indexed.
- CPU diarization of an 8-minute file takes about 9–10 minutes.

These limitations will be considered when interpreting the final evaluation.