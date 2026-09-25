# AudioRAG — Evaluation Plan

## 1. Evaluation Goal

The goal is to measure whether the audio search system retrieves the correct evidence for natural-language questions over speaker-aware audio transcripts.

Evaluation will focus primarily on retrieval quality, followed by answer grounding and latency.

## 2. Golden Dataset

The evaluation dataset should contain approximately 5–6 audio recordings.

Each recording should:

- Contain two speakers.
- Have meaningful conversational content.
- Have sufficient duration for multiple retrieval scenarios.
- Contain distinct topics and facts.
- Include known speaker/timestamp ground truth.

The dataset should support questions where the correct evidence can be identified precisely.

## 3. Query Categories

The evaluation set should include multiple query types.

### A. Exact keyword queries

Questions containing words that appear directly in the transcript.

Example:

```text
"What did they say about PostgreSQL?"
```

### B. Semantic / paraphrase queries

Questions where the wording differs from the transcript.

Example:

```text
"What database technology did they discuss?"
```

### C. Speaker-specific queries

Questions where the correct answer depends on identifying the speaker.

Example:

```text
"What did Speaker 01 say about the deployment?"
```

### D. Hard negatives

Queries containing similar terminology where the incorrect segment may look relevant.

Example:

```text
"What was discussed about the production database?"
```

when multiple segments discuss databases in different contexts.

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

Ground truth should identify the relevant file and timestamp range wherever practical.

## 5. Retrieval Metrics

### Recall@5

Measures whether at least one relevant result appears in the top five retrieved results.

```text
Recall@5 =
queries with relevant result in top 5
--------------------------------------
total queries
```

Target:

```text
>= 0.80
```

### Precision@5

Measures how many of the top five results are relevant.

```text
Precision@5 =
relevant results in top 5
-------------------------
5
```

Target:

```text
>= 0.60
```

### Mean Reciprocal Rank

MRR measures how highly the first relevant result appears.

```text
MRR = average(1 / rank_of_first_relevant_result)
```

Target:

```text
>= 0.70
```

These are target thresholds for evaluation, not existing measurements.

## 6. Retrieval Comparisons

The evaluation should compare multiple retrieval configurations:

```text
1. Lexical only
2. Semantic only
3. Hybrid / RRF
4. Hybrid + reranking
```

This helps identify the contribution of each retrieval stage.

## 7. Generation Evaluation

Retrieval quality is the primary measurement.

Generated answers should additionally be checked for:

### Groundedness

Does the answer follow the retrieved evidence?

### Citation correctness

Do the cited file, speaker, and timestamp correspond to the evidence used?

### Unsupported claims

Does the answer introduce information not supported by retrieved transcript evidence?

### Answer relevance

Does the answer directly address the user's question?

## 8. Error Analysis

For failed queries, classify the failure.

Possible categories:

```text
- ASR error
- Diarization error
- Chunking problem
- Keyword retrieval miss
- Semantic retrieval miss
- RRF ranking issue
- Reranker error
- Insufficient context
- LLM grounding issue
- Incorrect citation
```

This makes it possible to distinguish retrieval problems from generation problems.

## 9. Latency

Measure:

```text
Upload / ingestion latency
Diarization latency
ASR latency
Embedding latency
Search latency
Reranking latency
LLM latency
End-to-end query latency
```

Search latency should be measured separately from one-time ingestion latency.

## 10. Reproducibility

Record:

- Dataset version
- Query set
- Model names
- Embedding model
- Reranker model
- Retrieval parameters
- Top-K values
- RRF parameters
- Runtime environment

The objective is to make the final evaluation repeatable.

## 11. Evaluation Procedure

For each query:

```text
Query
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
Calculate metrics
```

Then evaluate generated answers using the retrieved evidence.

## 12. Final Results

The final hackathon evaluation should report:

```text
Recall@5:
Precision@5:
MRR:

Lexical:
Semantic:
Hybrid:
Hybrid + Reranker:

Average search latency:
Average end-to-end latency:
```

Actual values will be recorded after implementation and evaluation during the hackathon.

## 13. Limitations

The evaluation dataset is expected to be relatively small.

Therefore:

- Results may not generalize to all audio domains.
- Two-speaker recordings do not represent every real-world meeting.
- ASR errors can affect retrieval.
- Diarization errors can affect speaker-specific retrieval.
- LLM evaluation can contain subjective components.

These limitations should be considered when interpreting the final results.