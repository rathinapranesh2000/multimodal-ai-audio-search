# AudioRAG — solution

## What this is

AudioRAG searches two-speaker recordings by exact words and by meaning. A result always carries the file, the speaker, a timestamp, and a redacted snippet. The answer is written only from those snippets. If the language model fails, the evidence is still returned.

This file is the engineering write-up. It does not report retrieval scores. Those numbers are produced only by `python -m eval.run_eval` after a person verifies the labels.

## Design

```text
Upload
  → validate
  → 16 kHz mono WAV
  → pyannote and Whisper at the same time
  → align words to speakers
  → speaker-aware chunks
  → regex PII redaction
  → PostgreSQL full-text on the redacted text
  → pgvector embedding of the redacted text
  → reciprocal rank fusion (k = 60)
  → cross-encoder rerank of the fused top 20
  → top 5 evidence
  → Gemini, then Groq, then the evidence itself
```

Whisper runs once on the whole file. It is not run once per speaker turn. Diarization and transcription read the same normalized WAV. If running them together exhausts memory, the job retries them one after the other. If diarization fails, the transcript is kept under `SPEAKER_00` and the failure is logged. If transcription fails, the job fails.

### Why hybrid retrieval

Lexical search keeps rare strings such as `ticket 4812`, `March twelfth`, and `forty-two dollars`. Semantic search keeps paraphrases such as "how is the price calculated" for "seat-based billing". The two scores are not averaged. Reciprocal rank fusion adds `1 / (60 + rank)` from each list, so a chunk that both lists like rises without a hand-tuned weight.

The cross-encoder then reads the query and each surviving chunk together. It only sees the fused top 20, not the whole table. If it fails, the fused order is kept.

### Retrieval choices that matter on a five-file set

- Query embeddings use the BGE prefix `Represent this sentence for searching relevant passages:`. Document embeddings do not. Documents are stored as `SPEAKER_01: ...` so two speakers saying similar words stay apart.
- Full-text search uses `websearch_to_tsquery` on `content_redacted`. If that misses, the query is retried as an OR of the content words.
- A question that names Speaker 00 or Speaker 01 is filtered to that speaker before both searches. `Speaker 01` and `speaker 1` map to `SPEAKER_01`. `first speaker` maps to `SPEAKER_00`.
- Below 20,000 chunks the vector query disables index scans and computes exact cosine. An approximate index can drop the one correct chunk on a tiny corpus. An HNSW index is still created when pgvector is at least 0.5.0, and IVFFlat is the fallback. The index kind is stored on the file row.
- The original transcript is stored in `content` and is not indexed, embedded, or returned. `search_vector` is a generated column of `content_redacted` only.

### Grounding

The model receives the question and a few evidence blocks. Evidence is wrapped so a sentence inside a transcript cannot change the instructions. Injection phrasing in the question is stripped, then search continues. An empty question is rejected with HTTP 400. A question longer than 500 characters is truncated and still searched.

Gemini is called first. Groq is called only after Gemini throws. If both fail, the response is the evidence and the citations. Citations are chunk ids the model picked, and only if those ids were actually retrieved. Otherwise the citations are the evidence that was shown to the model.

Each hit includes a short `why` line: lexical rank, semantic rank, fusion score, rerank score. That is the audit trail for "why this moment."

### Data isolation

Tables live in the PostgreSQL schema `audiorag`. The rehearsal project used a `chunks` table elsewhere on the same server. This project does not write that table. Connections set `search_path` to `audiorag, public` so the `vector` type still resolves.

### PII

Redaction is regex, applied before indexing. It covers email addresses, phone numbers, US Social Security number shapes, long card numbers, a simple street-address shape, and names that follow "my name is" unless that name is on the speaker allowlist. It does not find arbitrary names in running speech. It is not a complete PII removal.

### Golden set

The 5 files in `dataset/audio/` are the real golden dataset actually used for evaluation. The synthetic TTS set in `dataset/synthetic_sample/` was an early placeholder used only for initial pipeline testing before real recordings were available, and is retained only for the one API smoke test.

`dataset/scripts/catalog.py` still holds the six placeholder interview scripts. `scripts/build_golden_audio.py` speaks them with a distinct voice pair per file and writes the result to `dataset/synthetic_sample/`. The indexed text for the real recordings still comes from Whisper and pyannote. Those scripts are not copied into the database.

`dataset/golden/script_timeline.json` is the timeline for that synthetic placeholder. It is not the official label set. Official evaluation queries live in `eval/golden_queries.json`.

### What success means

Targets, not results:

| Metric | Target |
| --- | --- |
| Recall@5 | at least 0.80 |
| Precision@5 | at least 0.60 |
| MRR | at least 0.70 |

Recall@5 asks whether a labeled span appears in the five chunks a person would see. Precision@5 divides relevant hits in those five slots by five, so a short list is not treated as perfect. MRR uses the rank of the first labeled hit. The same labels are scored four ways: lexical, semantic, fusion, and fusion plus rerank.

## What was checked while writing this

Unit tests cover fusion math, speaker parsing, redaction, alignment, path checks, the metric formulas, empty-query rejection, and bad uploads. Nineteen of those tests passed in this session. They do not call the database or the speech models. End-to-end ingest, model latency, and Recall@5 have not been run yet. Do not describe those as done until the commands below have been executed and the numbers written down from the report.

## How to run

From this directory, with `.env` already filled:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python -m app.db.init_db
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

In another shell:

```bash
cd frontend
npm install
npm run dev
```

Open `http://127.0.0.1:5173`. Upload each of the five real recordings in `dataset/audio/`. After every file is `ready`:

```bash
python -m scripts.suggest_labels
```

Listen, edit `dataset/golden/queries.json`, set `verified_by_human` to true, then:

```bash
python -m eval.run_eval
pytest
```

`ffmpeg` and `ffprobe` must be on `PATH`. The Hugging Face token must be allowed to download the pyannote model. Embeddings and the reranker run on CPU. Whisper uses int8 and `beam_size=1`.

## Limits

- Five short interviews cannot stand in for production scale. Exact scan is the right choice here and the wrong choice at millions of chunks.
- CPU diarization and Whisper are slow. Stage timings are stored on the file row so the slow stage can be measured before any model is swapped.
- Speaker labels can flip between files. Draft labels that assume a voice is `SPEAKER_00` are unsafe until the transcript is checked.
- Regex redaction misses many names and can miss local phone formats.
- Time-fitting the synthetic placeholder audio changes speaking rate. That set is not the evaluation dataset. The pipeline does not care how a WAV was made.
- Answer quality is not the primary metric. A fluent wrong answer is a failure if the citation does not support it.

## Collaboration

A coding agent in Cursor wrote this implementation from `HACKATHON-BUILD-PROMPT.md`, `ARCHITECTURE.md`, `EVALUATION.md`, and the hackathon task statement, after the rehearsal mistakes were identified. The human owner still has to review the code, run the servers, listen to the audio, and approve the labels. See `AGENT-DISCLOSURE.md` and `agent_log.md`.
