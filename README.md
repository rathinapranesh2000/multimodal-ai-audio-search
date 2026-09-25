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

The planned pipeline is:

```text
Audio
  ↓
Validation
  ↓
Speaker Diarization
  ↓
Speech-to-Text
  ↓
Speaker-Aware Chunking
  ↓
PII Redaction
  ↓
 ┌───────────────────┐
 │                   │
Lexical Search    Vector Search
 │                   │
 └─────────┬─────────┘
           ↓
      RRF Fusion
           ↓
       Reranking
           ↓
     Top-K Evidence
           ↓
 Context Compression
           ↓
    Grounded LLM
           ↓
 Answer + Citations
```

The architecture is designed around hybrid retrieval, combining keyword matching with semantic similarity before reranking.

## Key Features

### 1. Speaker-aware transcription

The system identifies speaker turns during ingestion so search results can include:

- Audio file
- Speaker
- Transcript
- Start timestamp
- End timestamp

### 2. Hybrid retrieval

Search combines:

- PostgreSQL full-text search for lexical matching
- pgvector semantic search for meaning-based retrieval
- Reciprocal Rank Fusion (RRF) to combine both result sets
- Cross-encoder reranking for the final candidates

### 3. Grounded answers

The LLM receives retrieved evidence rather than the entire recording.

Answers are expected to be grounded in retrieved transcript segments and accompanied by citations.

### 4. Timestamp-based citations

Each result can point back to the relevant location in the original audio.

Example:

```text
File: customer_interview.wav
Speaker: SPEAKER_01
Time: 04:32 – 04:48
```

The frontend can use the timestamp to seek directly into the recording.

### 5. Safety and reliability

The planned system includes:

- PII redaction before indexing
- Prompt-injection protection
- Out-of-scope query handling
- Evidence-grounded generation
- Fallback behavior when individual retrieval or generation components fail

## Technology Stack

### Backend

- Python
- FastAPI
- Pydantic

### Audio / AI

- pyannote.audio — speaker diarization
- faster-whisper — speech recognition
- sentence-transformers — embeddings
- BGE reranker — candidate reranking

### Database

- PostgreSQL
- pgvector
- PostgreSQL Full-Text Search

### LLM

- Google Gemini
- Groq fallback

### Frontend

- React
- TypeScript

### Observability

- Structured logging
- OpenTelemetry

## Retrieval Strategy

For each query:

1. Run lexical search.
2. Run semantic vector search.
3. Retrieve the top candidate set from each.
4. Combine rankings using Reciprocal Rank Fusion.
5. Rerank the fused candidates.
6. Select the strongest evidence.
7. Compress the evidence when required.
8. Generate a grounded answer with citations.

The detailed retrieval and failure-handling design follows the planned architecture document.

## Evaluation

The system will be evaluated using a small golden dataset containing known questions and relevant transcript segments.

Primary retrieval metrics:

- Recall@5
- Precision@5
- Mean Reciprocal Rank (MRR)

Evaluation categories include:

- Exact keyword queries
- Semantic/paraphrased queries
- Speaker-specific queries
- Hard-negative queries

The system will also compare retrieval stages such as lexical search, semantic search, hybrid retrieval, and reranking.

## Success Criteria

The initial target is:

```text
Recall@5     >= 0.80
Precision@5  >= 0.60
MRR          >= 0.70
```

These are evaluation targets, not pre-existing results.

## Planned Demo

The demo flow will be:

```text
Upload audio
      ↓
Process recording
      ↓
Search transcript
      ↓
Retrieve relevant speaker segments
      ↓
Show grounded answer
      ↓
Display citations
      ↓
Play audio from citation timestamp
```

## Project Status

This repository contains the planned architecture and evaluation methodology before the official hackathon implementation.

The application implementation will be developed during the official hackathon window.

## Coding Agent Transparency

If an AI coding agent is used during implementation, its usage, human direction, generated changes, validation, and important decisions will be documented in the project disclosure/log.

See:

- `AGENT-DISCLOSURE.md`
- `agent_log.md`

## Architecture Constraint

The implementation should preserve the core architecture:

```text
Diarization
→ ASR
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