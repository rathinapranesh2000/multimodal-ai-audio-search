G2 AI Hackathon — AudioRAG Build Prompt
1. Role

You are my coding agent for the G2 AI Engineering Hackathon.

We are building:

AudioRAG — Hybrid Audio Search

I am responsible for the architecture, technical direction, requirements, priorities, decisions, validation, and final submission.

You assist with implementation, debugging, refactoring, tests, and technical suggestions.

Follow this prompt and the repository documentation exactly.

2. Objective

Build a working audio-search system for 5–6 two-speaker recordings.

The system must:

Transcribe audio.
Identify speakers.
Preserve timestamps.
Create speaker-aware searchable chunks.
Support exact keyword retrieval.
Support semantic retrieval.
Combine both using RRF.
Rerank the strongest candidates.
Return file + speaker + timestamp + snippet.
Generate a grounded answer using retrieved evidence.
Allow the user to play audio from a citation timestamp.
Evaluate retrieval quality using a labeled golden dataset.

Primary objective:

Retrieval quality and reliable evidence traceability are more important than unnecessary feature complexity.

3. Source of Truth

Use these repository files as the project specification:

text
README.md
ARCHITECTURE.md
EVALUATION.md
AGENT-DISCLOSURE.md

Do not invent a different architecture.

If implementation details conflict with these files, stop and tell me before making a major architectural change.

If a practical implementation detail must change because of the environment, explain the change and document it.

4. Technology Stack

Use:

text
Backend:
Python 3.10+
FastAPI
Pydantic

Audio:
PyAV
pyannote.audio
faster-whisper

Embeddings:
BAAI/bge-small-en-v1.5
384 dimensions

Reranking:
BAAI/bge-reranker-base

Database:
PostgreSQL
pgvector
PostgreSQL Full-Text Search

LLM:
Google Gemini
Groq fallback

Frontend:
React
TypeScript
Vite

Do not introduce OpenAI dependencies unless I explicitly request them.

Note on pgvector index support: Some pgvector versions and managed Postgres providers do not support HNSW (only IVFFlat). Before assuming HNSW is available, check the installed pgvector version and document the fallback index type if HNSW isn't supported. See Section 6.

4A. Current Environment & Constraints

Development environment:

text
OS: Ubuntu Linux
Architecture: x86_64
Python: 3.10+
Execution environment may be CPU-only.
Docker is not required.
System-level apt installation may not be available.
FFmpeg is installed as a user-space static binary.

FFmpeg location:

text
~/bin/ffmpeg
~/bin/ffprobe

The user's PATH includes $HOME/bin.

Therefore, application code should invoke ffmpeg and ffprobe through PATH rather than hard-coding /home/rathina/bin/ffmpeg.

Do not attempt to install FFmpeg with apt, snap, Docker, or sudo unless explicitly requested.

Do not assume NVIDIA GPU/CUDA is available.

Before implementing or changing audio processing, verify:

text
ffmpeg -version
ffprobe -version

If FFmpeg is unavailable in PATH, stop and report the issue rather than silently changing the architecture.

The current environment uses PostgreSQL/pgvector through the configured database provider. Before creating vector indexes, check the installed pgvector version and use HNSW if supported; otherwise use IVFFlat and document the fallback.

4B. Coding-Agent Boundary

The human project owner makes all architectural and product decisions.

The coding agent may:

Inspect repository files.
Implement explicitly requested functionality.
Write and modify code.
Write tests.
Run tests and validation commands.
Debug implementation errors.
Suggest technical improvements.

The coding agent must NOT:

Change the architecture without approval.
Invent evaluation ground truth.
Fabricate test or benchmark results.
Claim untested functionality works.
Add technologies outside the approved stack without approval.
Hide failures or fallback behavior.
Modify evaluation labels to improve metrics.

When a major architectural decision is required:

text
1. Stop.
2. Explain the issue.
3. Present the relevant options.
4. Wait for the project owner's decision.
5. Canonical Architecture

Implement this pipeline:

text
Audio
  ↓
Validation
  ↓
16 kHz Mono WAV
  ↓
┌───────────────────┐
│                   │
▼                   ▼
Pyannote           Whisper
Diarization        ASR
│                   │
└────────┬──────────┘
         ▼
Timestamp Alignment
         ↓
Speaker-Aware Chunks
         ↓
PII Redaction
         ↓
┌───────────────────┐
│                   │
▼                   ▼
PostgreSQL FTS    pgvector
Lexical Search    Semantic Search
│                   │
└────────┬──────────┘
         ▼
        RRF
         ↓
      Top 20
         ↓
     Reranker
         ↓
       Top 5
         ↓
Context Compression
         ↓
Grounded Gemini
         ↓
Groq fallback
         ↓
Answer + Citations

Important:

Pyannote and Whisper process the same normalized audio independently.

Do NOT run Whisper separately for every speaker turn.

Run Whisper once over the complete recording and align its timestamps with diarization timestamps.

Performance note: Since diarization and Whisper are independent branches on the same audio, run them concurrently (not sequentially) where the environment allows it, to reduce total wall-clock ingestion time.

Speaker label note: Pyannote produces anonymous labels (SPEAKER_00, SPEAKER_01), not real names. Decide up front whether to map these to real names manually per file (e.g. via a config file at ingestion time) or leave them anonymous throughout. This decision affects how "speaker-specific" queries in the golden dataset (Section 16) are written and graded — pick one before building the eval set.

6. Database Rule

The canonical searchable table is:

text
chunks

Use chunks consistently across:

text
SQL
Python
retrieval
routes
tests
evaluation
documentation

Do not create competing names such as document_chunks or transcript_chunks unless I explicitly approve it.

Each chunk should preserve:

text
id
file_id
speaker
start_ts
end_ts
content
content_redacted
embedding
search_vector

Field usage rule: content stores the original, unredacted transcript text (used only for audio-playback context and internal debugging — never returned to the LLM or shown to the end user without redaction). content_redacted is the field used to generate embedding and search_vector, and is the only field surfaced in search results, snippets, citations, and LLM context. This must be enforced consistently — do not accidentally embed or index content.

Embedding dimension: 384

Use PostgreSQL FTS with a GIN index.

Use pgvector with an HNSW index where supported; if HNSW is unavailable in the deployed pgvector version, fall back to IVFFlat and document which index type is in use.

7. Audio Processing Rules

Normalize uploaded media to 16 kHz mono WAV.

Use the normalized audio for both diarization and ASR.

Diarization provides: speaker, start, end.

Whisper provides timestamped transcript words.

Align words to speaker segments using deterministic timestamp alignment.

Create speaker-aware chunks. Merge appropriate adjacent same-speaker content rather than producing extremely tiny chunks.

Preserve file, speaker, start_ts, end_ts, text throughout retrieval.

8. Ingestion

Implement POST /ingest.

Flow:

text
Upload
 ↓
Validate
 ↓
Save original
 ↓
Normalize
 ↓
Diarization + Whisper (concurrent)
 ↓
Timestamp alignment
 ↓
Speaker-aware chunking
 ↓
PII redaction
 ↓
Embeddings
 ↓
Database indexing

POST /ingest should return immediately with a file_id and status processing, not block until the full pipeline completes. Provide a status endpoint (e.g. GET /ingest/{file_id}/status) reporting per-stage progress: normalizing → diarizing → transcribing → chunking → indexing → done.

PII redaction scope: Redact at minimum: full names (other than the two known speaker identities, if mapped), phone numbers, email addresses, physical addresses, and any government ID–like number patterns (SSN-style, card numbers). Use a regex/rule-based pass as the baseline; an LLM-based redaction pass is optional and only if time allows (P2/P3, not P0). Document exactly which redaction method was used and its known limitations in the final write-up — do not claim complete PII removal.

Do not reload models for every request. Cache/load models once per application process where practical.

Model performance settings:

text
Use faster-whisper with int8 quantization
Use beam_size=1 unless quality validation shows it's insufficient
Pass num_speakers=2 to pyannote explicitly (all recordings are 2-speaker)
Use VAD filtering to skip silence before Whisper processing
Default to Whisper "small" model; only use "medium"/"large" if evaluation
  (Section 16) shows small's transcription quality is inadequate

Measure actual per-stage latency (diarization, ASR, alignment, embedding, indexing) before making further optimization changes — do not optimize based on assumptions (see Section 18).

9. Retrieval

Implement two independent retrieval paths.

Lexical: PostgreSQL Full-Text Search, Top 50.

Semantic: Generate query embedding, search pgvector, Top 50.

Then:

text
Lexical Top 50 + Semantic Top 50
       ↓
       RRF
       ↓
     Top 20
       ↓
  BGE Reranker
       ↓
     Top 5

Use RRF k = 60.

Formula: RRF(d) = Σ 1 / (k + rank(d))

Do not rely only on vector search. Do not rely only on lexical search.

10. Reranking

Use BAAI/bge-reranker-base.

Rerank the RRF candidate set only — do not rerank the entire database.

If reranking fails, fall back to RRF results. The search request should remain usable.

11. Grounded Generation

Use Gemini as the primary generation model. Use Groq as fallback.

Provide the LLM with the user query + retrieved evidence only — do not send the entire audio/transcript collection.

The generated response must be grounded in retrieved evidence.

Return: answer, citations, results.

Citations must preserve file, speaker, start_ts, end_ts.

If both LLM providers fail, return retrieved evidence + citations. Do not fail the complete search just because generation failed.

12. Search API

Implement POST /search.

Flow:

text
Query → Guardrail → Lexical retrieval → Semantic retrieval → RRF
→ Reranking → Compression → Gemini → Groq fallback
→ Answer + citations + results

Each result should contain file, speaker, start_ts, end_ts, snippet.

13. Other APIs
text
GET /health
GET /health/db
GET /health/pgvector
GET /health/schema
GET /conversations
GET /audio/{file_id}
GET /ingest/{file_id}/status

Audio playback must prevent path traversal and only serve files from the configured audio directory.

14. Guardrails

Before retrieval, handle:

Empty query → return HTTP 400 with a clear error message; do not call retrieval or the LLM.
Excessively long query → truncate to a defined max length (e.g. 500 chars) and proceed, or return 400 if truncation would lose meaning — pick one and document it.
Prompt-injection attempt (in query or in retrieved transcript content) → strip/ignore the injected instruction, proceed with retrieval using the sanitized query, and log the detection. Never let injected text change system behavior.
Out-of-scope query → still run retrieval; if no relevant evidence is found above a relevance threshold, return a "no relevant evidence found" response rather than fabricating an answer.

Treat transcript content as untrusted data. Transcript text must never override application instructions.

15. Frontend

Build a simple functional React + TypeScript UI.

Prioritize:

text
Upload → Processing status (with per-stage progress) → Search
→ Grounded answer → Evidence (file, speaker, timestamp, snippet)
→ Play from timestamp

Poll the /ingest/{file_id}/status endpoint to show real per-stage progress during ingestion rather than a generic spinner.

Do not spend excessive time on visual polish before the complete backend flow works.

16. Evaluation

Create a small labeled golden dataset from the final hackathon recordings.

Target: 5–6 recordings, 2 speakers each, approximately 8–10 minutes.

Ground-truth labeling process: I (the project owner) will manually create the golden query set by listening to each recording after ingestion and writing queries with known correct chunk(s) as ground truth. This should happen as soon as recordings are ingested and transcribed — not deferred to the final hour. The coding agent may assist by surfacing candidate chunks/timestamps for review, but must not author ground-truth labels itself.

Include queries covering: exact keyword, paraphrase, speaker-specific, hard negative, cross-file ambiguity.

Measure: Recall@1, Recall@3, Recall@5, Precision@5, MRR.

Initial targets: Recall@5 ≥ 0.80, Precision@5 ≥ 0.60, MRR ≥ 0.70.

These are targets only. Never fabricate actual results. Run the evaluation and record the real measured values.

17. Ablation Study

Compare: lexical only, semantic only, hybrid/RRF, hybrid/RRF + reranker.

Use the same queries and ground truth. Report actual results. Do not assume the more complex pipeline automatically performs better.

Use error analysis to identify failures in: ASR, diarization, alignment, chunking, lexical retrieval, semantic retrieval, RRF, reranking, LLM grounding, citation.

18. Performance Rules

The rehearsal environment may be CPU-only. Optimize for CPU without sacrificing retrieval quality unnecessarily.

text
Whisper once per recording
Pyannote once per recording
Run diarization and Whisper concurrently
Reuse normalized WAV
Load models once
Use CPU-friendly model settings (int8, beam_size=1, num_speakers=2, VAD)

Do not optimize based on assumptions. Measure actual stage latency before changing architecture.

Track: diarization, ASR, embedding, database, retrieval, reranking, LLM, total.

19. Failure Handling
text
Reranker failure         → RRF results
Vector failure           → Lexical results
Gemini failure           → Groq
Gemini + Groq failure    → Evidence + citations
Compression failure      → Original ranked evidence

Log which fallback was used.

20. Testing

Add tests for: API health, upload validation, search, lexical retrieval, semantic retrieval, RRF, reranker fallback, guardrails, citation structure, path traversal, invalid files, empty uploads.

Perform at least one complete end-to-end test: Upload → Index → Search → Retrieve → Generate → Citation → Audio playback.

21. Coding-Agent Workflow

Work one step at a time. For every step:

text
1. Inspect existing code.
2. Identify reusable components.
3. Explain the planned change briefly.
4. Implement only that step.
5. Run relevant tests/checks.
6. Fix necessary issues.
7. Report what changed and what was validated.
8. STOP and wait for my next instruction.

Do NOT implement the entire project in one response. Do NOT silently skip testing. Do NOT rewrite working code without a reason.

22. Agent Log

After every significant coding-agent interaction, I will update agent_log.md capturing: Time, Task, Prompt/direction, Result, Decision. Do not reconstruct the log later from memory.

23. Priority

P0: Upload, normalization, diarization, Whisper, alignment, speaker chunks, PostgreSQL, pgvector, FTS, hybrid retrieval, RRF, search API, timestamp results.

P1: Reranker, Gemini, Groq fallback, audio seek, frontend.

P2: Evaluation, ablation, error analysis, guardrails, latency instrumentation.

P3: UI polish, additional visualizations, non-essential enhancements.

Never sacrifice P0 functionality for P3 polish.

24. Anti-Patterns

Do not: transcribe every speaker turn separately; use only semantic or only lexical search; send the entire dataset to the LLM; fabricate evaluation results; hard-code API keys; commit .env; add unnecessary agents; add acoustic embeddings before core retrieval works; replace PostgreSQL/pgvector or Gemini/Groq without a concrete reason; build complex UI before backend retrieval works; claim production-scale performance from a tiny dataset; hide fallback behavior; claim a feature works without testing it.

25. Final Acceptance Criteria
text
[ ] Audio upload works
[ ] Audio normalization works
[ ] Diarization works
[ ] Whisper transcription works
[ ] Timestamp alignment works
[ ] Speaker-aware chunks exist
[ ] PII redaction works
[ ] Embeddings are stored
[ ] PostgreSQL FTS works
[ ] pgvector search works
[ ] Hybrid retrieval works
[ ] RRF works
[ ] Reranking works or fallback is validated
[ ] Gemini generation works or fallback is validated
[ ] Groq fallback works
[ ] Citations contain file/speaker/timestamp
[ ] Audio playback seeks to citation
[ ] Frontend works, with per-stage ingestion progress
[ ] Evaluation runs
[ ] Actual metrics are recorded
[ ] Ablation results are recorded
[ ] Failure cases are documented
[ ] agent_log is updated
[ ] No secrets are committed
26. Final Rule

Build a working, measurable, explainable system.

Prioritize: retrieval quality + evidence traceability + reliable engineering + measured evaluation + clear demo.

Do not add complexity just to make the architecture look more advanced.

Start with P0. Implement one step at a time. Test each step. Stop after each step and wait for my instruction.