# AudioRAG — Evaluation Plan

## 1. Evaluation Goal

The goal is to measure whether the AudioRAG system retrieves the correct evidence for natural-language questions over speaker-aware audio transcripts.

Evaluation focuses primarily on retrieval quality, followed by answer grounding, citation correctness, and latency.

The evaluation is designed not only to measure the final system, but also to determine how individual retrieval stages contribute to overall performance.

---

## 2. Golden Dataset

The scored set is the five recordings currently indexed in the UI:

| File | Chunks | Duration |
| --- | --- | --- |
| AI_Engineering_Mock_Interview.wav | 20 | 8:00 |
| Google_Coding_Interview.wav | 36 | 8:00 |
| System_Design_of_ChatGPT.wav | 36 | 8:00 |
| Behavioral_mock_Interview.wav | 17 | 6:12 |
| llm_systems_interview.wav | 23 | 8:00 |

Queries live in `eval/golden_queries.json` (23 rows). Labels are under `relevant_chunks`. Queries 8, 22, and 23 are hard negatives with empty label lists and `hard_negative_style: true`. They are excluded from Recall@k.

---

## 3. Query Categories

The evaluation set should contain multiple query types.

### A. Exact Keyword Queries

Questions containing words that appear directly in the transcript.

Example:

```text
"What did they say about PostgreSQL?"
```

These queries test the effectiveness of lexical retrieval.

---

### B. Semantic / Paraphrase Queries

Questions where the wording differs from the transcript while preserving the same meaning.

Example:

```text
"What database technology did they discuss?"
```

when the transcript uses wording such as:

```text
"We decided to use PostgreSQL for the backend."
```

These queries test semantic retrieval.

---

### C. Speaker-Specific Queries

Queries where the correct evidence depends on identifying the speaker.

Example:

```text
"What did Speaker 01 say about the deployment?"
```

These queries test whether speaker identity is correctly preserved and associated with the retrieved evidence.

---

### D. Hard Negatives

Queries where incorrect segments contain similar terminology but discuss a different context.

Example:

```text
"What was discussed about the production database?"
```

when multiple segments discuss databases but only one discusses the production database.

These queries test whether the retrieval system can distinguish topical similarity from actual relevance.

---

### E. Cross-File Ambiguity

Queries where multiple recordings contain related terminology, but only one recording contains the relevant fact.

Example:

```text
"What did they say about database migration?"
```

when several recordings discuss databases but only one discusses database migration.

These queries test whether the system can distinguish relevant evidence across multiple recordings.

---

## 4. Ground Truth

Each evaluation query should have known relevant evidence.

Example:

```json
{
  "id": 5,
  "query": "What did they discuss about the electrical power plan?",
  "query_type": "keyword",
  "file_hint": "Behavioral_mock_Interview.wav",
  "relevant_chunks": [
    {
      "file": "Behavioral_mock_Interview.wav",
      "speaker": "SPEAKER_00",
      "start_ts": 55.58,
      "end_ts": 94.9
    }
  ]
}
```

A hit counts when file, speaker, and time overlap a labeled span. Any shared time counts. The power-plant unit check with this label returns Recall@1 = 1.0 and MRR = 1.0.

---

## 5. Retrieval Metrics

### Recall@K

Recall@K measures whether relevant evidence appears within the top K retrieved results.

For a binary per-query evaluation:

```text
Recall@K =
queries with at least one relevant result in top K
---------------------------------------------------
total evaluation queries
```

The system will measure:

```text
Recall@1
Recall@3
Recall@5
```

Recall@5 is the primary retrieval metric because the application presents a small evidence set to the user.

Target:

```text
Recall@5 >= 0.80
```

---

### Precision@5

Precision@5 measures how many of the top five retrieved results are relevant.

```text
Precision@5 =
relevant results in top 5
-------------------------
5
```

Target:

```text
Precision@5 >= 0.60
```

Precision is useful for identifying cases where the system retrieves relevant evidence but also returns many distracting results.

---

### Mean Reciprocal Rank

MRR measures how highly the first relevant result appears.

```text
MRR =
average(
    1 / rank_of_first_relevant_result
)
```

Target:

```text
MRR >= 0.70
```

MRR complements Recall@5 by measuring ranking quality rather than only whether a relevant result was eventually retrieved.

---

## 6. Retrieval Ablation Study

The evaluation will compare multiple retrieval configurations using the same query set and ground-truth annotations.

### Configuration 1 — Lexical Only

```text
Query
 ↓
PostgreSQL Full-Text Search
 ↓
Top K
```

This measures the performance of exact lexical matching.

---

### Configuration 2 — Semantic Only

```text
Query
 ↓
Embedding
 ↓
pgvector
 ↓
Top K
```

This measures semantic retrieval independently from lexical matching.

---

### Configuration 3 — Hybrid / RRF

```text
             ┌──► Lexical Top 50
Query ───────┤
             └──► Semantic Top 50
                      │
                      ▼
                     RRF
                      │
                   Top 20
```

RRF uses:

```text
RRF(d) = Σ 1 / (60 + rank(d))
```

This configuration measures the benefit of combining complementary lexical and semantic signals.

---

### Configuration 4 — Hybrid + Reranker

```text
Lexical Top 50
      │
      ├────► RRF ───► Top 20 ───► BGE Reranker ───► Top 5
      │
Semantic Top 50
```

This measures whether cross-encoder reranking improves ordering of the strongest hybrid candidates.

---

### Ablation Results

`python -m tests.eval_recall` on 26 Sep 2026. Twenty labeled queries. Hard negatives are not in this table. Full copy: `eval/results.md`.

| mode | Recall@1 | Recall@3 | Recall@5 | Precision@5 | MRR | queries |
| --- | --- | --- | --- | --- | --- | --- |
| lexical | 0.250 | 0.600 | 0.600 | 0.140 | 0.373 | 20 |
| semantic | 0.500 | 0.750 | 0.900 | 0.260 | 0.650 | 20 |
| hybrid_rrf | 0.350 | 0.600 | 0.750 | 0.190 | 0.539 | 20 |
| hybrid | 0.450 | 0.750 | 0.800 | 0.230 | 0.596 | 20 |

Recall@5 by query type:

| query_type | n | lexical | semantic | hybrid_rrf | hybrid |
| --- | --- | --- | --- | --- | --- |
| keyword | 8 | 0.875 | 1.000 | 0.875 | 0.875 |
| paraphrase | 9 | 0.556 | 0.889 | 0.778 | 0.778 |
| cross_file | 2 | 0.500 | 1.000 | 0.500 | 1.000 |
| speaker_specific | 1 | 0.000 | 0.000 | 0.000 | 0.000 |

The speaker_specific row is query 6 only. Query 8 is in the hard-negative table.

| id | query_type | lexical | semantic | hybrid_rrf | hybrid |
| --- | --- | --- | --- | --- | --- |
| 8 | speaker_specific | PASS | PASS | PASS | FAIL |
| 22 | hard_negative | PASS | PASS | PASS | FAIL |
| 23 | hard_negative | PASS | PASS | PASS | FAIL |

A hard negative passes when no top-5 chunk has `rerank_score >= -5.0`. Modes without a rerank score pass. Hybrid fails all three because sigmoid scores are above `-5.0`.

---

## 7. Generation Evaluation

Retrieval quality is the primary measurement.

Generated answers should additionally be checked for:

### Groundedness

Does the generated answer follow the retrieved transcript evidence?

---

### Citation Correctness

Do the cited:

- File
- Speaker
- Timestamp

correspond to the evidence used to produce the answer?

---

### Unsupported Claims

Does the answer introduce information that is not supported by the retrieved transcript evidence?

---

### Answer Relevance

Does the answer directly address the user's question?

---

## 8. Error Analysis

For failed queries, classify the failure.

Possible categories:

```text
ASR error
Diarization error
Timestamp alignment error
Chunking problem
PII redaction issue
Keyword retrieval miss
Semantic retrieval miss
RRF ranking issue
Reranker error
Insufficient context
LLM grounding issue
Incorrect citation
```

The purpose of error analysis is to distinguish failures caused by upstream audio processing from failures caused by retrieval or generation.

For example:

```text
Audio
 ↓
ASR failure
 ↓
Incorrect transcript
 ↓
Correct retrieval becomes impossible
```

should not be classified as a pure vector-search failure.

---

## 9. Latency

Measure ingestion and query latency separately.

### Ingestion

Measure:

```text
Upload/save latency
Audio normalization latency
Diarization latency
ASR latency
Chunking/alignment latency
Embedding latency
Database indexing latency
Total ingestion latency
```

### Search

Measure:

```text
Guardrail latency
Lexical retrieval latency
Semantic retrieval latency
RRF latency
Reranking latency
Compression latency
LLM latency
Total search latency
```

Search latency should be measured separately from one-time ingestion latency because transcription and diarization occur during indexing rather than during every query.

---

## 10. Speaker Retrieval Evaluation

Speaker-specific retrieval should be evaluated separately because it tests both retrieval quality and speaker attribution.

Example:

```text
Query:
"What did Speaker 01 say about deployment?"
```

Expected evidence:

```text
file = interview_02.wav
speaker = SPEAKER_01
timestamp = known ground-truth range
```

A result should only be considered correct when the relevant evidence is associated with the correct speaker.

This helps identify cases where the transcript content is retrieved correctly but speaker attribution is incorrect.

---

## 11. Timestamp Evaluation

Each retrieved result contains:

```text
file
speaker
start_ts
end_ts
```

Timestamp correctness should be checked against the ground-truth evidence range.

The evaluation should distinguish between:

```text
Correct file + correct evidence
```

and:

```text
Correct file + wrong timestamp
```

because a search result that cannot take the user to the relevant location reduces practical usefulness even if the correct recording was identified.

---

## 12. Evaluation Procedure

For each query:

```text
Query
  ↓
Query validation
  ↓
Lexical retrieval
  ↓
Semantic retrieval
  ↓
RRF
  ↓
Reranking
  ↓
Top-5 results
  ↓
Compare with ground truth
  ↓
Calculate Recall@K / Precision@5 / MRR
```

For generation evaluation:

```text
Query
  ↓
Retrieved evidence
  ↓
Context compression
  ↓
Grounded LLM
  ↓
Answer + citations
  ↓
Check grounding
  ↓
Check citation correctness
  ↓
Check answer relevance
```

---

## 13. Evaluation Reproducibility

Record:

- Dataset version
- Query set
- Ground-truth annotations
- ASR model
- Diarization model
- Embedding model
- Reranker model
- Retrieval parameters
- Top-K values
- RRF parameter
- Runtime environment
- Python version
- CPU configuration

The objective is to make the final evaluation repeatable.

---

## 14. Final Results

Measured on the 20 labeled queries. Source: `eval/results.md`.

| mode | Recall@1 | Recall@3 | Recall@5 | Precision@5 | MRR |
| --- | --- | --- | --- | --- | --- |
| lexical | 0.250 | 0.600 | 0.600 | 0.140 | 0.373 |
| semantic | 0.500 | 0.750 | 0.900 | 0.260 | 0.650 |
| hybrid_rrf | 0.350 | 0.600 | 0.750 | 0.190 | 0.539 |
| hybrid | 0.450 | 0.750 | 0.800 | 0.230 | 0.596 |

Ingestion on this CPU, from completed jobs: diarization about 9–10 minutes for an 8-minute file. Transcription runs in parallel and finishes sooner (about 1–2 minutes on the files already indexed). First search in a fresh process spends about 30 seconds loading the embedding and reranker models. Later searches in that process are the retrieval, rerank, and LLM time.

The UI demo query “Why can AI coding agents fail in production?” was run in all four modes against the five ready recordings. Hits include file, speaker, timestamps, rank notes, and Play from. Semantic and Hybrid + rerank also returned chunks from `System_Design_of_ChatGPT.wav` and `llm_systems_interview.wav` beside the `AI_Engineering_Mock_Interview.wav` evidence.

---

## 15. Success Criteria

Initial target thresholds:

```text
Recall@5     >= 0.80
Precision@5  >= 0.60
MRR          >= 0.70
```

Measured against those targets, best mode on each metric:

| metric | target | best measured | mode | meets target |
| --- | --- | --- | --- | --- |
| Recall@5 | 0.80 | 0.900 | semantic | yes |
| Precision@5 | 0.60 | 0.260 | semantic | no |
| MRR | 0.70 | 0.650 | semantic | no |

Hybrid + rerank Recall@5 is 0.800, which meets the Recall@5 target and misses Precision@5 and MRR.

---

## 16. Failure Analysis

Three cases were written up from the score dump in `eval/known_failures.md`. No new search was run for that note.

Query 17, “How should a chatbot maintain conversation history?” The reranker put `AI_Engineering_Mock_Interview.wav` 450.02–479.96 first (cosine similarity 0.722741, rerank 0.500). Two `System_Design_of_ChatGPT.wav` chunks had higher cosine similarity (0.777368 and 0.756799) and lower rerank scores (0.047 and 0.015).

Query 20, “How can a chatbot provide factual and reliable information?” The labeled `System_Design_of_ChatGPT.wav` chunk at 299.62–323.48 was semantic rank 30, RRF rank 7 of 20, and rerank rank 11 with score 0.000156. It missed the top 5. The rank-5 rerank score was 0.001601.

Query 21, “How can a retrieval system combine exact matching with meaning-based matching?” The hybrid-search chunk at 111.83–142.10 had cosine similarity 0.660679 and semantic rank 5. It ranked below `Google_Coding_Interview.wav` 197.21–228.77 (0.683568) and `AI_Engineering_Mock_Interview.wav` 79.36–111.83 (0.683203). Hybrid + rerank top 5 did not include it.

Query 6, the only normal speaker-specific query, has Recall@5 0.000 in every mode. The query text does not name `SPEAKER_00`, and retrieval does not filter by speaker unless the query does.

`relevance_min_logit` remains `-5.0`. Hybrid hard negatives fail that check because sigmoid scores are above it, and the cutoff is intentionally left there. Query 1's genuine top score is 0.000443, which sits between hard-negative maxima 0.0000652 (query 22) and 0.000774 (query 23). An absolute rerank score cannot tell those cases apart. The guard is not tuned further.

---

## 17. Limitations

The evaluation dataset is 23 queries on five recordings.

Therefore:

- Results may not generalize to all audio domains.
- Two-speaker recordings do not represent every real-world meeting.
- ASR errors can affect retrieval.
- Diarization errors can affect speaker-specific retrieval.
- Timestamp alignment can be imperfect around overlapping speech.
- The number of evaluation queries may limit statistical confidence.
- LLM evaluation can contain subjective components.
- CPU-only execution increases ingestion latency.
- A small golden dataset may not represent production-scale query diversity.
- Gemini generation reached the API successfully but was blocked by the free-tier quota limit (20 requests/day); Groq served as the working fallback for the majority of this evaluation.
- The PII redaction regex over-matches on common phrases (e.g. 'I'm currently') as name redactions; this is a known false-positive pattern in the current rule-based approach.

These limitations should be considered when interpreting the final results.