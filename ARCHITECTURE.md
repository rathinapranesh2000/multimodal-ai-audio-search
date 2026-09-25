# AudioRAG — Architecture

## 1. Architecture Goal

Build a production-oriented hybrid search system for two-speaker audio recordings.

The system should retrieve relevant information from audio using both:

- Lexical matching
- Semantic similarity

The retrieved evidence should remain connected to the original speaker and timestamp so that every generated answer can be verified against the recording.

## 2. High-Level Architecture

```text
                    ┌─────────────────────┐
                    │     Audio Upload    │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │      Validation     │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Speaker Diarization │
                    │      pyannote       │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │        ASR          │
                    │   faster-whisper    │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Speaker-aware       │
                    │ Chunking             │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │     PII Redaction   │
                    └──────────┬──────────┘
                               │
                 ┌─────────────┴─────────────┐
                 │                           │
                 ▼                           ▼
        ┌─────────────────┐        ┌─────────────────┐
        │ Lexical Index   │        │ Vector Index    │
        │ PostgreSQL FTS  │        │    pgvector     │
        └────────┬────────┘        └────────┬────────┘
                 │                          │
                 │       Top Candidates     │
                 └────────────┬─────────────┘
                              ▼
                    ┌─────────────────────┐
                    │   RRF Fusion        │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │      Reranker       │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │    Top Evidence     │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Context Compression │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   Grounded LLM      │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Answer + Citations  │
                    └─────────────────────┘
```

This follows the intended architecture of validation, diarization, ASR, speaker-aware chunking, PII handling, hybrid retrieval, fusion, reranking, and grounded generation.

---

## 3. Ingestion Pipeline

### Step 1 — Audio validation

Validate:

- File type
- File size
- Duration
- Audio readability
- Required audio properties

The system should reject unsupported or malformed files early.

### Step 2 — Speaker diarization

Use `pyannote.audio` to identify speaker turns.

Expected structure:

```text
SPEAKER_00 → 00:00.0 - 00:12.4
SPEAKER_01 → 00:12.4 - 00:21.8
SPEAKER_00 → 00:21.8 - 00:35.1
```

### Step 3 — Speech recognition

Use `faster-whisper` to convert speech into timestamped text.

### Step 4 — Speaker-aware chunking

Associate transcript text with the diarized speaker.

Chunks should preserve:

```text
file_id
speaker
start_time
end_time
text
```

Short adjacent turns may be merged when appropriate to avoid excessively fragmented retrieval units.

### Step 5 — PII redaction

PII should be removed from the text used for indexing.

The original audio and source timing information remain available for citation purposes.

The planned architecture explicitly places PII redaction before indexing.

---

## 4. Storage

PostgreSQL is the primary persistence layer.

The planned storage model contains concepts for:

### Audio file

```text
id
filename
duration
metadata
created_at
```

### Transcript segment

```text
id
audio_file_id
speaker
start_time
end_time
text
```

### Search chunk

```text
id
audio_file_id
speaker
start_time
end_time
text
embedding
search_vector
```

Exact schema and indexes will be implemented and validated during the hackathon.

---

## 5. Lexical Search

PostgreSQL Full-Text Search will provide keyword-oriented retrieval.

This is useful for:

- Exact names
- Product names
- Technical terms
- Numbers
- Rare keywords
- Queries where semantic similarity may be insufficient

A GIN-backed search index is planned.

---

## 6. Semantic Search

Transcript chunks will be converted into dense embeddings.

Planned embedding model:

```text
BAAI/bge-small-en-v1.5
```

Embedding dimension:

```text
384
```

The embeddings will be stored using pgvector.

A vector index will be used for efficient nearest-neighbor retrieval.

---

## 7. Hybrid Retrieval

The system will execute lexical and semantic retrieval independently.

Example:

```text
Query
 │
 ├──→ Lexical Search ──→ Top 50
 │
 └──→ Vector Search ───→ Top 50
```

The two result lists are then combined.

---

## 8. Reciprocal Rank Fusion

The planned fusion method is Reciprocal Rank Fusion.

Conceptually:

```text
RRF(d) = Σ 1 / (k + rank(d))
```

with a configurable constant `k`.

The purpose is to combine the strengths of lexical and semantic retrieval without requiring the two retrieval scores to be directly comparable.

---

## 9. Reranking

After fusion, a smaller candidate set will be passed to a cross-encoder reranker.

Planned model:

```text
BAAI/bge-reranker-base
```

The reranker receives:

```text
(query, candidate_chunk)
```

and produces a relevance score.

The strongest candidates are then selected for answer generation.

---

## 10. Context Compression

Only the most relevant evidence should be passed to the LLM.

The compression stage should:

- Remove redundant context
- Preserve important facts
- Preserve speaker information
- Preserve timestamps
- Maintain traceability to source chunks

---

## 11. Grounded Generation

The LLM should answer using retrieved evidence.

Planned model providers:

```text
Primary: Google Gemini
Fallback: Groq
```

The generated response should contain:

```text
answer
citations
```

The system should avoid generating unsupported facts when relevant evidence is unavailable.

---

## 12. Citation Model

Each citation should identify:

```text
audio_file
speaker
start_time
end_time
```

Example:

```json
{
  "file": "interview_01.wav",
  "speaker": "SPEAKER_01",
  "start_time": 272.4,
  "end_time": 288.7
}
```

The frontend can use these values to seek directly into the corresponding audio.

---

## 13. Guardrails

The planned system includes:

- Input validation
- PII detection/redaction
- Prompt-injection detection
- Out-of-scope query handling
- Evidence-only answer generation
- Citation validation

The architecture specifically defines guardrails around PII, injection, and unsupported queries.

---

## 14. Failure Handling

The system should degrade gracefully.

Planned fallback chain:

```text
Reranker
   ↓ failure
RRF results

Vector search
   ↓ failure
Lexical search

Primary LLM
   ↓ failure
Fallback LLM

LLM generation
   ↓ failure
Evidence + citations
```

The goal is to return useful evidence even when a downstream component fails.

---

## 15. Observability

The implementation should provide sufficient visibility into:

- Upload processing
- Diarization latency
- ASR latency
- Embedding latency
- Lexical retrieval latency
- Vector retrieval latency
- RRF latency
- Reranking latency
- LLM latency
- End-to-end search latency

Structured logging and OpenTelemetry are planned.

---

## 16. Frontend

The frontend will provide:

```text
┌───────────────────────────────────────┐
│             Audio Search              │
├───────────────────────────────────────┤
│ Upload audio                          │
│                                       │
│ [ Search query.................... ]  │
│                                       │
│ Answer                                │
│ ───────────────────────────────────   │
│                                       │
│ Citations                             │
│ • Speaker 01 · 02:14                  │
│ • Speaker 02 · 05:37                  │
│                                       │
│ [▶ Play from timestamp]               │
└───────────────────────────────────────┘
```

The primary UX goal is to move from a natural-language query directly to verifiable audio evidence.

---

## 17. Architecture Principles

1. Retrieval before generation.
2. Hybrid retrieval instead of relying on a single search method.
3. Preserve speaker and timestamp metadata throughout the pipeline.
4. Redact PII before indexing.
5. Ground LLM responses in retrieved evidence.
6. Provide citations for generated answers.
7. Prefer graceful degradation over total failure.
8. Measure retrieval quality rather than relying only on subjective demo results.

---

## 18. Implementation Constraint

This document defines the intended architecture.

The actual application implementation will be developed during the official hackathon window.

Implementation details may change when required by:

- Time constraints
- Hardware limitations
- Library compatibility
- Runtime performance
- Validation results

Any architectural deviation should be documented during the hackathon.