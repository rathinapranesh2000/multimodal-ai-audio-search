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

The system will be evaluated using a small golden dataset containing known questions and relevant transcript segments.

Primary retrieval metrics include:

- Recall@1
- Recall@3
- Recall@5
- Precision@5
- Mean Reciprocal Rank (MRR)

Recall@5 is the primary retrieval success criterion.

Evaluation categories include:

- Exact keyword queries
- Semantic/paraphrased queries
- Speaker-specific queries
- Hard-negative queries
- Cross-file ambiguity queries

The evaluation also compares retrieval configurations to determine the contribution of each retrieval stage.

## Retrieval Ablation

The same labeled query set will be evaluated using:

```text
1. Lexical only
2. Semantic only
3. Hybrid / RRF
4. Hybrid / RRF + reranker
```

The purpose of the ablation is to measure the incremental contribution of each retrieval strategy rather than assuming that additional components automatically improve retrieval quality.

The final results will be reported by retrieval configuration and query category.

Example:

```text
                    Recall@1   Recall@3   Recall@5   MRR
Lexical
Semantic
Hybrid / RRF
Hybrid + Reranker
```

Actual values will be populated only after the implementation and evaluation are completed during the official hackathon window.

## Success Criteria

The initial target is:

```text
Recall@5     >= 0.80
Precision@5  >= 0.60
MRR          >= 0.70
```

These are evaluation targets, not pre-existing results.

The final submission will report the actual measured results separately from these target thresholds.

## Planned Demo

The demo flow will be:

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

This repository contains the planned architecture and evaluation methodology before the official hackathon implementation.

The application implementation will be developed during the official hackathon window.

No final retrieval metrics, accuracy measurements, latency measurements, or evaluation results are claimed before the corresponding experiments are actually run.

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

- The golden dataset is relatively small.
- The recordings focus on two-speaker conversations.
- ASR errors can affect transcript quality.
- Diarization errors can affect speaker-specific retrieval.
- Timestamp alignment may be imperfect around overlapping speech.
- Evaluation results may not generalize to all audio domains.
- LLM-based answer evaluation can contain subjective components.
- CPU-only execution increases ingestion latency compared with GPU-based processing.

These limitations will be considered when interpreting the final evaluation.