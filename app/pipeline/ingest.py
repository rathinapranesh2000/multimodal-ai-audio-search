"""Ingestion: normalize, diarize and transcribe together, align, redact, index."""

from __future__ import annotations

import json
import threading
import time
from pathlib import Path

from app.core.config import get_settings
from app.core.logging import get_logger
from app.db.connection import get_connection
from app.db.init_db import ensure_vector_index
from app.pipeline.align import ChunkDraft, SpeakerSpan, Word, build_chunks
from app.pipeline.audio import (
    AudioValidationError,
    normalize_wav,
    normalized_path,
    original_path,
    probe_duration,
)
from app.pipeline.redact import redact_pii
from app.retrieval.search import embed_documents

logger = get_logger(__name__)

_STAGES = (
    "normalizing",
    "diarizing",
    "transcribing",
    "aligning",
    "chunking",
    "indexing",
    "done",
)


def create_file_row(filename: str, speaker_map: dict[str, str]) -> str:
    with get_connection() as connection:
        row = connection.execute(
            """
            INSERT INTO audio_files (filename, status, stage, progress, speaker_map)
            VALUES (%s, 'processing', 'normalizing', %s::jsonb, %s::jsonb)
            RETURNING id::text
            """,
            (filename, json.dumps({stage: "pending" for stage in _STAGES}), json.dumps(speaker_map)),
        ).fetchone()
        connection.commit()
    if row is None:
        raise RuntimeError("Could not store the audio file")
    return str(row[0])


def start_ingest(file_id: str, filename: str, speaker_map: dict[str, str]) -> None:
    """Run the pipeline on a daemon thread so the upload request can return."""
    thread = threading.Thread(
        target=_safe_ingest,
        args=(file_id, filename, speaker_map),
        name=f"ingest-{file_id[:8]}",
        daemon=True,
    )
    thread.start()


def _safe_ingest(file_id: str, filename: str, speaker_map: dict[str, str]) -> None:
    try:
        ingest_file(file_id, filename, speaker_map)
    except Exception as exc:
        logger.exception("ingest_failed file_id=%s", file_id)
        _mark_failed(file_id, _public_error(exc))


def ingest_file(file_id: str, filename: str, speaker_map: dict[str, str]) -> None:
    from uuid import UUID

    source = original_path(UUID(file_id), filename)
    wav = normalized_path(UUID(file_id))
    timings: dict[str, float] = {}

    _stage(file_id, "normalizing", {**_pending(), "normalizing": "running"})
    started = time.perf_counter()
    normalize_wav(source, wav)
    duration = probe_duration(wav)
    timings["normalizing_ms"] = _elapsed(started)
    _save_duration(file_id, duration, timings)

    _stage(
        file_id,
        "diarizing",
        {**_pending(), "normalizing": "done", "diarizing": "running", "transcribing": "running"},
        timings,
    )
    spans, words, speech_timings = _diarize_and_transcribe(wav)
    timings.update(speech_timings)

    _stage(file_id, "aligning", _done_through("transcribing", "aligning"), timings)
    started = time.perf_counter()
    if not words:
        raise AudioValidationError("Speech recognition returned no words")
    if not spans:
        logger.warning("diarization_empty fallback=single_speaker file_id=%s", file_id)
        spans = [SpeakerSpan("SPEAKER_00", 0.0, duration)]
    drafts = build_chunks(words, spans)
    timings["aligning_ms"] = _elapsed(started)
    if not drafts:
        raise AudioValidationError("Alignment produced no speaker chunks")

    _stage(file_id, "chunking", _done_through("aligning", "chunking"), timings)
    started = time.perf_counter()
    allowed = {name for name in speaker_map.values() if name.strip()}
    redacted = [redact_pii(draft.text, allowed) for draft in drafts]
    kept = [
        (draft, clean)
        for draft, clean in zip(drafts, redacted, strict=True)
        if clean.strip()
    ]
    timings["chunking_ms"] = _elapsed(started)
    if not kept:
        raise AudioValidationError("Every chunk was empty after redaction")

    _stage(file_id, "indexing", _done_through("chunking", "indexing"), timings)
    started = time.perf_counter()
    _store_chunks(file_id, kept)
    index_kind = ensure_vector_index()
    timings["indexing_ms"] = _elapsed(started)
    _mark_ready(file_id, len(kept), timings, index_kind)
    logger.info("ingest_ready file_id=%s chunks=%s index=%s", file_id, len(kept), index_kind)


def _diarize_and_transcribe(wav: Path) -> tuple[list[SpeakerSpan], list[Word], dict[str, float]]:
    """Run pyannote and Whisper at the same time. On memory pressure, run them in series."""
    from concurrent.futures import ThreadPoolExecutor

    try:
        return _parallel_speech(wav, ThreadPoolExecutor)
    except MemoryError:
        logger.warning("parallel_speech_oom fallback=sequential")
        return _sequential_speech(wav)


def _parallel_speech(wav: Path, pool_cls) -> tuple[list[SpeakerSpan], list[Word], dict[str, float]]:
    with pool_cls(max_workers=2) as pool:
        diarize_job = pool.submit(_timed, _diarize, wav)
        transcribe_job = pool.submit(_timed, _transcribe, wav)
        spans, diarize_ms, diarize_error = diarize_job.result()
        words, asr_ms, asr_error = transcribe_job.result()
    if isinstance(asr_error, MemoryError) or isinstance(diarize_error, MemoryError):
        raise MemoryError("speech models ran out of memory")
    if asr_error is not None:
        raise asr_error
    if diarize_error is not None:
        _log_diarization_failure(diarize_error)
        spans = []
    else:
        _log_diarization_result(spans)
    return spans, words, {"diarizing_ms": diarize_ms, "transcribing_ms": asr_ms}


def _sequential_speech(wav: Path) -> tuple[list[SpeakerSpan], list[Word], dict[str, float]]:
    spans, diarize_ms, diarize_error = _timed(_diarize, wav)
    words, asr_ms, asr_error = _timed(_transcribe, wav)
    if asr_error is not None:
        raise asr_error
    if diarize_error is not None:
        _log_diarization_failure(diarize_error)
        spans = []
    else:
        _log_diarization_result(spans)
    return spans, words, {"diarizing_ms": diarize_ms, "transcribing_ms": asr_ms}


def _log_diarization_failure(exc: BaseException) -> None:
    detail = str(exc).splitlines()[0][:240]
    logger.warning(
        "diarization_failed fallback=single_speaker error=%s detail=%s",
        type(exc).__name__,
        detail,
    )


def _log_diarization_result(spans: list[SpeakerSpan]) -> None:
    speakers = sorted({span.speaker for span in spans})
    logger.info("diarization_ok spans=%s speakers=%s", len(spans), ",".join(speakers) or "none")


def _timed(func, wav: Path):
    started = time.perf_counter()
    try:
        value = func(wav)
    except Exception as exc:
        return [], _elapsed(started), exc
    return value, _elapsed(started), None


def _load_waveform(wav: Path):
    """Read 16 kHz PCM without TorchCodec.

    Pyannote's file-path loader uses TorchCodec, which needs libavutil shared
    libraries. This machine has a static ffmpeg binary, so that loader raises
    and diarization was being replaced by one SPEAKER_00 span.
    """
    import numpy as np
    import torch
    import wave

    with wave.open(str(wav)) as handle:
        channels = handle.getnchannels()
        sample_width = handle.getsampwidth()
        rate = handle.getframerate()
        frames = handle.readframes(handle.getnframes())
    if sample_width != 2 or rate <= 0 or channels <= 0:
        raise AudioValidationError("Normalized audio must be 16-bit PCM")
    samples = np.frombuffer(frames, dtype="<i2").astype(np.float32) / 32768.0
    samples = samples.reshape(-1, channels).T
    return torch.from_numpy(np.ascontiguousarray(samples)), int(rate)


def _spans_from_output(output) -> list[SpeakerSpan]:
    exclusive = getattr(output, "exclusive_speaker_diarization", None)
    regular = getattr(output, "speaker_diarization", None)
    annotation = exclusive if exclusive is not None and len(list(exclusive.itertracks())) else regular
    if annotation is None:
        annotation = output
    spans = [
        SpeakerSpan(speaker=str(speaker), start=float(turn.start), end=float(turn.end))
        for turn, _, speaker in annotation.itertracks(yield_label=True)
    ]
    spans.sort(key=lambda span: span.start)
    return spans


def _diarize(wav: Path) -> list[SpeakerSpan]:
    from app.models_runtime import get_diarization

    settings = get_settings()
    speakers = settings.diarization_num_speakers
    waveform, sample_rate = _load_waveform(wav)
    pipeline = get_diarization()
    output = pipeline(
        {"waveform": waveform, "sample_rate": sample_rate, "uri": wav.stem},
        num_speakers=speakers,
    )
    return _spans_from_output(output)


def _transcribe(wav: Path) -> list[Word]:
    from app.models_runtime import get_whisper

    settings = get_settings()
    language = settings.whisper_language.strip() or None
    segments, _info = get_whisper().transcribe(
        str(wav),
        language=language,
        task="transcribe",
        beam_size=1,
        vad_filter=True,
        word_timestamps=True,
    )
    words: list[Word] = []
    for segment in segments:
        timed = getattr(segment, "words", None) or []
        if timed:
            for word in timed:
                text = (word.word or "").strip()
                if text and word.start is not None and word.end is not None:
                    words.append(Word(float(word.start), float(word.end), text))
            continue
        text = (segment.text or "").strip()
        if text:
            words.append(Word(float(segment.start), float(segment.end), text))
    return words


def _store_chunks(file_id: str, kept: list[tuple[ChunkDraft, str]]) -> None:
    speakers = [draft.speaker for draft, _clean in kept]
    redacted = [clean for _draft, clean in kept]
    vectors = embed_documents(speakers, redacted)
    with get_connection() as connection:
        connection.execute("DELETE FROM chunks WHERE file_id = %s", (file_id,))
        for (draft, clean), vector in zip(kept, vectors, strict=True):
            if len(vector) != get_settings().embedding_dim:
                raise RuntimeError("Embedding dimension is not 384")
            connection.execute(
                """
                INSERT INTO chunks (
                    file_id, speaker, start_ts, end_ts, content, content_redacted, embedding
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s::vector)
                """,
                (
                    file_id,
                    draft.speaker,
                    draft.start,
                    draft.end,
                    draft.text,
                    clean,
                    _vector_literal(vector),
                ),
            )
        connection.commit()


def _vector_literal(values: list[float]) -> str:
    return "[" + ",".join(f"{float(value):.8f}" for value in values) + "]"


def _pending() -> dict[str, str]:
    return {stage: "pending" for stage in _STAGES}


def _done_through(stage: str, running: str | None = None) -> dict[str, str]:
    progress = _pending()
    for name in _STAGES:
        progress[name] = "done"
        if name == stage:
            break
    if running:
        progress[running] = "running"
    return progress


def _elapsed(started: float) -> float:
    return round((time.perf_counter() - started) * 1000, 1)


def _stage(file_id: str, stage: str, progress: dict[str, str], timings: dict[str, float] | None = None) -> None:
    with get_connection() as connection:
        connection.execute(
            """
            UPDATE audio_files
            SET stage = %s, progress = %s::jsonb, timings = %s::jsonb, updated_at = NOW()
            WHERE id = %s
            """,
            (stage, json.dumps(progress), json.dumps(timings or {}), file_id),
        )
        connection.commit()


def _save_duration(file_id: str, duration: float, timings: dict[str, float]) -> None:
    with get_connection() as connection:
        connection.execute(
            """
            UPDATE audio_files
            SET duration_seconds = %s, timings = %s::jsonb, updated_at = NOW()
            WHERE id = %s
            """,
            (duration, json.dumps(timings), file_id),
        )
        connection.commit()


def _mark_ready(file_id: str, chunk_count: int, timings: dict[str, float], index_kind: str) -> None:
    progress = {stage: "done" for stage in _STAGES}
    with get_connection() as connection:
        connection.execute(
            """
            UPDATE audio_files
            SET status = 'ready', stage = 'done', progress = %s::jsonb,
                timings = %s::jsonb, chunk_count = %s, vector_index = %s,
                error = NULL, updated_at = NOW()
            WHERE id = %s
            """,
            (json.dumps(progress), json.dumps(timings), chunk_count, index_kind, file_id),
        )
        connection.commit()


def record_failure(file_id: str, message: str) -> None:
    """Store a public failure reason for the status endpoint."""
    _mark_failed(file_id, message)


def _mark_failed(file_id: str, message: str) -> None:
    with get_connection() as connection:
        connection.execute(
            """
            UPDATE audio_files
            SET status = 'failed', stage = 'failed', error = %s, updated_at = NOW()
            WHERE id = %s
            """,
            (message[:500], file_id),
        )
        connection.commit()


def _public_error(exc: Exception) -> str:
    if isinstance(exc, AudioValidationError):
        return str(exc)
    if isinstance(exc, ModuleNotFoundError):
        missing = exc.name or "a required package"
        return (
            f"Ingestion failed because Python cannot import {missing}. "
            "Start the API with the project virtualenv: "
            ".venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000"
        )
    return f"Ingestion failed during processing ({type(exc).__name__})"
