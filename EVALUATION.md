# AudioRAG — Evaluation Plan

## 1. Evaluation Goal

The goal is to measure whether the AudioRAG system retrieves the correct evidence for natural-language questions over speaker-aware audio transcripts.

Evaluation focuses primarily on retrieval quality, followed by answer grounding, citation correctness, and latency.

The evaluation is designed not only to measure the final system, but also to determine how individual retrieval stages contribute to overall performance.

---

## 2. Golden Dataset

The evaluation dataset should contain approximately 5–6 audio recordings.

Each recording should:

- Contain two speakers.
- Have meaningful conversational content.
- Have sufficient duration for multiple retrieval scenarios.
- Contain distinct topics and facts.
- Include known speaker and timestamp ground truth.

The dataset should support questions where the correct evidence can be identified precisely.

The final hackathon dataset must consist of recordings collected or created during the official hacking window.

Pre-existing rehearsal recordings must not be used as the final hackathon evaluation dataset.

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
  "query": "What database did they discuss?",
  "relevant": [
    {
      "file": "interview_01.wav",
      "speaker": "SPEAKER_01",
      "start_time": 142.2,
      "end_time": 158.7
    }
  ]
}
```

Ground truth should identify the relevant:

- File
- Speaker
- Timestamp range

wherever practical.

A retrieved result is considered relevant when it overlaps or corresponds to the annotated evidence for the query according to the evaluation matching rules.

The ground-truth annotations must be created from the actual final hackathon recordings.

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

The final evaluation should report results in a table similar to:

```text
                    Recall@1   Recall@3   Recall@5   MRR
Lexical
Semantic
Hybrid / RRF
Hybrid + Reranker
```

Results should also be broken down by query category where the sample size permits:

```text
                    Exact   Paraphrase   Speaker   Hard Negative   Cross-file
Lexical
Semantic
Hybrid / RRF
Hybrid + Reranker
```

The purpose is to measure the contribution of each stage rather than assuming that a more complex pipeline is automatically better.

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

The final hackathon submission should report actual measured values.

Example structure:

```text
Recall@1:
Recall@3:
Recall@5:
Precision@5:
MRR:

Lexical:
Semantic:
Hybrid / RRF:
Hybrid + Reranker:

Average ingestion latency:
Average search latency:
Average end-to-end latency:
```

The final report should also include the results broken down by query category where practical.

No values should be entered until the corresponding evaluation has actually been executed.

---

## 15. Success Criteria

Initial target thresholds:

```text
Recall@5     >= 0.80
Precision@5  >= 0.60
MRR          >= 0.70
```

These are target thresholds rather than existing results.

The final report should clearly distinguish:

```text
Target
Actual measured result
Difference from target
```

---

## 16. Failure Analysis

For queries that fail, document:

```text
Query
Expected evidence
Retrieved evidence
Failure category
Likely cause
Potential improvement
```

Example:

```text
Query:
"What did they say about database migration?"

Expected:
interview_03.wav / SPEAKER_02 / 05:12–05:31

Retrieved:
interview_01.wav / SPEAKER_01 / 02:44–03:02

Failure:
Cross-file ambiguity

Likely cause:
Semantically similar database discussion outranked the migration-specific evidence.
```

This provides evidence for future retrieval improvements and makes the evaluation useful beyond a single aggregate score.

---

## 17. Limitations

The evaluation dataset is expected to be relatively small.

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

These limitations should be considered when interpreting the final results.