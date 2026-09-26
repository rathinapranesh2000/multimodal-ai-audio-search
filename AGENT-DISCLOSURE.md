# AGENT-DISCLOSURE

Filled during the hacking window from the live request, not reconstructed later.
The human owner has not yet reviewed or accepted this pass.

## 1. Coding Agent Used

Cursor, in the G2-AI-Hackathon session on 26 Sep 2026.

## 2. Prompts / Instructions Given

The human asked for a separate end-to-end AudioRAG build in this repository, using the earlier rehearsal only as a source of problems to avoid. The agent was told to follow `HACKATHON-BUILD-PROMPT.md` and the official task: hybrid keyword and semantic search, local embeddings, file plus speaker plus timestamp, a golden set of 5–6 two-speaker recordings about 8–10 minutes each, automated Recall@k, and a written disclosure of how the agent was directed.

The human also asked for a standard both frontend and backend, strong enough that reviewers can judge the code, and said they would review before starting the servers.

Standing constraints from the build prompt that were followed:

- Canonical pipeline, `chunks` table, redacted text only in search and embeddings.
- Gemini first, Groq only as fallback.
- Do not invent evaluation numbers or official ground-truth labels.
- Do not commit secrets.

## 3. What the Agent Generated

The agent generated the application under `app/`, the React UI under `frontend/`, the interview scripts under `dataset/scripts/`, the audio builder, the label suggester, the metric functions, the unit tests, and `SOLUTION.md`.

## 4. What I Implemented / Changed

Pending human review. Nothing in this pass has been hand-edited by the project owner yet.

## 5. Validation & Testing

The agent ran 19 unit tests that do not need the database or the speech models. All 19 passed. Ingest, diarization, Whisper, live search, and Recall@k were not run. `dataset/golden/queries.json` is unverified on purpose. No retrieval score is claimed.

## 6. Human Decisions

Already fixed before this session, in the repository spec: hybrid RRF with k = 60, BGE small embeddings, BGE reranker, Gemini then Groq, PostgreSQL with pgvector, two speakers, Recall@5 as the primary target.

Left for the owner after review:

- Accept or replace the synthetic interviews with recorded conversations.
- Listen and approve labels before any official score is reported.
- Confirm the pyannote model name still matches the token's granted access.
