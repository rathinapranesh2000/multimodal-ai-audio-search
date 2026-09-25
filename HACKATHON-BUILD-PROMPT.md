# G2 AudioRAG — Hackathon Build Prompt

## How to Use This Prompt

Execute **one step at a time**.

After completing each step:

1. Stop.
2. Run the requested validation.
3. Report what changed and whether the validation passed.
4. Wait for the next step.

Do not continue automatically to the next step.

## Permanent Rules

These rules apply to **every step**:

1. **Never print, expose, echo, or commit secrets.**
2. Never paste real API keys, Hugging Face tokens, database passwords, or connection strings into chat.
3. Real secrets belong only in the project-root `.env`.
4. Never commit `.env`.
5. **Do not uninstall, replace, downgrade, or otherwise change an existing working CPU PyTorch installation.**
6. Do not install CUDA.
7. Do not use Docker.
8. Do not use `sudo`.
9. Do not use conda.
10. Do not install a local PostgreSQL server.
11. Do not invent audio recordings, transcripts, ground-truth data, evaluation results, or performance scores.
12. Use the external Supabase PostgreSQL database with pgvector.
13. CPU-only execution.
14. If a required package is already installed and working, reuse it instead of unnecessarily reinstalling it.
15. Do not drop or destroy existing database tables.
16. Follow `ARCHITECTURE.md` unless a technical constraint requires a documented change.

---

# Step 1 — Project Rules and Foundation

Build AudioRAG in the current project folder.

Do not use Docker, sudo, conda, or a local PostgreSQL installation.

The database is external Supabase PostgreSQL with pgvector.

Connect using psycopg 3 through `DATABASE_URL` stored in the project-root `.env`.

Create the initial project structure:

```text
app/
app/db/
db/
dataset/
dataset/audio/
frontend/
```

Create:

```text
.env.example
.gitignore
requirements.txt
README.md
```

The README should briefly state:

- CPU-only requirement
- External Supabase PostgreSQL
- No Docker
- No sudo
- No conda
- No local PostgreSQL
- Secrets remain in `.env`
- Actual implementation is being built during the official hackathon window

Do not implement application functionality yet.

### Stop condition

Stop after the folders and foundation files exist.

Report:

- created files
- created folders
- Python version
- existing PyTorch version, if installed

Do not print secrets.

---

# Step 2 — API and Database Health

Add a FastAPI application:

```text
app/main.py
```

Read these values from the project-root `.env`:

```text
APP_NAME
APP_ENV
DEBUG
DATABASE_URL
GOOGLE_API_KEY
GROQ_API_KEY
HF_TOKEN
```

Add:

```text
GET /health
GET /health/db
```

`/health` should return basic application status.

`/health/db` should test a PostgreSQL connection using psycopg 3.

Use:

```text
sslmode=require
sslnegotiation=postgres
connect_timeout=10
prepare_threshold=None
```

Never log:

- `DATABASE_URL`
- database password
- API keys
- HF token
- complete environment variables

If the database password contains `#`, explain that it must be URL-encoded as `%23`.

### Validation

Start FastAPI and verify:

```text
GET /health
GET /health/db
```

`/health/db` must report a successful database connection.

### Stop condition

Stop only after `/health/db` returns connected.

Do not proceed to Step 3 automatically.

Remember:

- Never print secrets.
- Do not change the CPU PyTorch installation.

---

# Step 3 — Database Schema

Create:

```text
db/schema.sql
app/db/init_db.py
```

Create the `chunks` table according to the architecture.

Required fields:

```text
file_id
speaker
start_ts
end_ts
content
content_redacted
embedding VECTOR(384)
tsv
```

`tsv` should be a generated English PostgreSQL `tsvector` based on `content_redacted`.

Create:

- GIN index on `tsv`
- IVFFlat cosine index on `embedding`

Do not drop existing tables.

Create:

```bash
python -m app.db.init_db
```

The initialization command should safely create missing objects without destroying existing data.

Add:

```text
GET /health/pgvector
GET /health/schema
```

### Validation

Verify:

```text
/health/pgvector
/health/schema
```

and verify that:

- `chunks` exists
- `tsv` exists
- GIN index exists
- vector index exists

### Stop condition

Stop after the schema and indexes are verified.

Remember:

- Never print secrets.
- Do not change the CPU PyTorch installation.

---

# Step 4 — Local CPU Models

First inspect the current environment.

Check:

```text
torch
torchaudio
faster-whisper
pyannote.audio
sentence-transformers
torchcodec
```

If the existing CPU PyTorch installation is working, **do not reinstall, replace, downgrade, or upgrade it unless absolutely required and explicitly confirmed**.

Do not install CUDA.

Install missing CPU-compatible dependencies into:

```text
./venv
```

Required stack:

```text
FastAPI
uvicorn
pydantic
psycopg[binary]
faster-whisper
pyannote.audio
sentence-transformers
torchcodec
```

Required models:

```text
faster-whisper small.en
pyannote/speaker-diarization-community-1
BAAI/bge-small-en-v1.5
BAAI/bge-reranker-base
```

Use CPU.

Models must load lazily and only once per process.

Before the first model load, configure:

```text
OMP_NUM_THREADS
torch.set_num_threads(...)
```

based on the available CPU cores.

Do not print:

- API keys
- HF token
- database credentials

Create a CPU verification script that verifies the required models can load.

### Validation

Run the verification script.

Report only:

```text
model: PASS
device: CPU
```

or an equivalent safe status.

### Stop condition

Stop after each required model has successfully loaded or after clearly reporting which model failed.

Remember:

- Never print secrets.
- Do not change the CPU PyTorch installation.

---

# Step 5 — Audio Indexing

Add:

```text
POST /ingest
```

Supported input formats:

```text
wav
mp3
m4a
flac
ogg
```

Store uploaded recordings under:

```text
dataset/audio/
```

Do not commit recordings to Git.

For non-WAV input, convert to:

```text
mono
16 kHz
```

Use `pyannote/speaker-diarization-community-1` for speaker diarization.

Accept:

```text
num_speakers
```

from the upload request.

Default:

```text
2
```

Transcribe the **whole audio file once** using faster-whisper.

Default model:

```text
small.en
```

Use:

```text
vad_filter=True
beam_size=1
word timestamps=True
```

Assign each ASR word to the speaker turn containing the word midpoint.

Do not run a separate Whisper transcription for every speaker turn.

Merge short turns under 3 seconds into a neighboring same-speaker turn where appropriate.

Redact before indexing:

- email addresses
- phone numbers
- SSNs
- long numeric identifiers

Use regex-based redaction.

Embed `content_redacted` using:

```text
BAAI/bge-small-en-v1.5
```

Store the resulting chunks in PostgreSQL.

## Model Selection

Use this mapping:

```text
Low    = faster-whisper base.en
Medium = faster-whisper small.en  ← default
High   = faster-whisper medium.en
Auto   = choose based on available CPU resources
```

Language:

```text
English
```

is the default.

When running the backend during development, use:

```bash
uvicorn app.main:app --reload --reload-dir app
```

so generated WAV files do not unnecessarily trigger application reloads.

### Validation

Index one short real audio file.

Verify:

- file saved
- diarization completed
- transcription completed
- speaker information exists
- timestamps exist
- chunks inserted
- embeddings inserted

### Stop condition

Stop after one short real file is successfully indexed.

Remember:

- Never print secrets.
- Do not change the CPU PyTorch installation.

---

# Step 6 — Hybrid Search and Answer Generation

Add:

```text
POST /search
```

## Query Guardrail

Before any database search:

Reject the query if it is:

- empty
- longer than 1000 characters
- an obvious instruction-override/prompt-injection attempt

Rejected queries must not execute retrieval.

## Hybrid Retrieval

Run lexical and vector retrieval independently.

Lexical:

```text
PostgreSQL ts_rank_cd
Top 50
```

Semantic:

```text
pgvector cosine similarity
Top 50
```

Run them concurrently where practical.

Combine results using Reciprocal Rank Fusion:

```text
1 / (60 + rank)
```

Keep the top 20 fused results.

If vector search fails:

```text
use lexical results
```

## Reranking

Rerank the fused candidates using:

```text
BAAI/bge-reranker-base
```

Keep the top 5.

If reranking fails:

```text
keep the RRF order
```

## Context Compression

Reduce the selected evidence to the relevant sentences while preserving:

- speaker
- file
- timestamp
- source traceability

## LLM

Primary:

```text
Google Gemini
gemini-2.0-flash
```

Fallback:

```text
Groq
llama-3.3-70b-versatile
```

Use Groq only when Gemini fails.

Treat retrieved transcript evidence as **untrusted data**.

Do not allow transcript content to override system/application instructions.

Require structured output:

```json
{
  "answer": "string",
  "citations": [
    {
      "file": "string",
      "speaker": "string",
      "timestamp": "string"
    }
  ]
}
```

Validate the response using Pydantic.

Retry generation once if structured validation fails.

If generation still fails:

```text
answer = ""
citations = retrieved evidence
```

Add:

```text
GET /audio/{file_id}
```

Block path traversal and ensure the requested file remains inside the configured audio directory.

### Validation

Run one search against the indexed recording.

Verify:

```text
correct file
correct speaker
correct timestamp
```

### Stop condition

Stop after one correct end-to-end search result.

Remember:

- Never print secrets.
- Do not change the CPU PyTorch installation.

---

# Step 7 — Frontend

Create a React + TypeScript Vite application.

Frontend port:

```text
5173
```

Backend:

```text
8000
```

Configure the Vite development proxy for:

```text
/health
/ingest
/search
/audio
/conversations
```

Proxy to:

```text
127.0.0.1:8000
```

If the backend is unavailable, the API must return a JSON error response rather than an empty response.

## Upload UI

Fields:

```text
Speakers:
2 / 3 / 4
Default: 2

Language:
English / Auto-detect
Default: English

Model:
Medium / Low / High / Auto
Default: Medium
```

## Search UI

Display:

- answer
- file
- speaker
- timestamp
- snippet
- citation

Provide an audio player that can seek to the citation `start_ts`.

## Conversations

Add a conversations/indexed-files page showing indexed recordings.

### Validation

Open the frontend in the browser.

Verify:

```text
upload
→ processing
→ search
→ answer
→ citation
→ audio playback
```

### Stop condition

Stop after upload and search work successfully in the browser.

Remember:

- Never print secrets.
- Do not change the CPU PyTorch installation.

---

# Step 8 — FFmpeg Without Root

Do not use sudo.

TorchCodec requires FFmpeg shared libraries.

On Ubuntu 22.04 x86_64, use user-space package extraction.

Download the required Ubuntu Jammy FFmpeg/libav/libsw `.deb` packages using `apt download`.

Extract them with:

```text
dpkg-deb
```

into:

```text
~/ffmpeg/local
```

Set:

```text
LD_LIBRARY_PATH=~/ffmpeg/local/usr/lib/x86_64-linux-gnu
```

Do not modify the system FFmpeg installation.

If `ldd` reports additional missing shared libraries, download the required Jammy packages and extract them into the same local prefix.

### Validation

From the same shell/environment:

```text
import torchcodec
```

Then verify `AudioDecoder` can open a real WAV file.

Restart uvicorn from the same environment without `--reload` for this validation.

### Stop condition

Stop only when `AudioDecoder` successfully opens the WAV.

Remember:

- Never print secrets.
- Do not change the CPU PyTorch installation.

---

# Step 9 — Documentation Only

Update `README.md` with the actual run procedure.

Document:

```text
1. Create/use root venv
2. Configure Supabase DATABASE_URL
3. Configure HF_TOKEN
4. Configure GOOGLE_API_KEY
5. Configure GROQ_API_KEY as fallback
6. Configure LD_LIBRARY_PATH
7. Start backend with uvicorn without --reload
8. Start frontend with npm run dev
```

Do not document or expose actual secret values.

Update `ARCHITECTURE.md`:

```text
Jev is not used in this build.

Logging uses standard-library stage logs with a trace ID.
```

Do not add:

```text
golden_queries.json
eval/test_recall.py
```

yet.

Do not invent:

```text
Recall
Precision
MRR
latency
accuracy
```

Do not add fake evaluation results.

`EVALUATION.md` must contain methodology/targets only until actual evaluation is performed.

---

# Event-Day Evaluation Prompt

After the implementation is complete during the official hackathon window, create:

```text
dataset/audio/
eval/golden_queries.json
eval/test_recall.py
```

Use only the real recordings collected/created during the official hacking window.

Create the golden queries from those recordings.

Do not use pre-existing rehearsal recordings as the hackathon evaluation dataset.

Run the evaluation and record the actual:

```text
Recall@5
Precision@5
MRR
```

Do not fabricate or estimate results.

Document the final methodology and actual measured results.

---

# Final Rules

At every step:

```text
NEVER PRINT SECRETS.
NEVER CHANGE THE CPU PYTORCH INSTALLATION.
```

Do not proceed to the next step until the current step's validation succeeds or the failure is clearly reported.