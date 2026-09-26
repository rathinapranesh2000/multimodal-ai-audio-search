"""Lazy CPU model loaders. Each model is loaded once per process."""

from __future__ import annotations

import os
import threading

from app.core.config import get_settings

_CPU = os.cpu_count() or 4
os.environ.setdefault("OMP_NUM_THREADS", str(max(1, _CPU // 2)))
os.environ.setdefault("MKL_NUM_THREADS", str(max(1, _CPU // 2)))

_lock = threading.Lock()
_whisper = None
_diarization = None
_embedder = None
_reranker = None
_torch_ready = False


def cpu_threads() -> int:
    """Leave half the cores for the sibling speech model during parallel ingest."""
    return max(1, _CPU // 2)


def _prepare_torch() -> None:
    global _torch_ready
    if _torch_ready:
        return
    import torch

    torch.set_num_threads(cpu_threads())
    _torch_ready = True


def get_whisper():
    """Load faster-whisper with int8 weights. beam_size is chosen at transcribe time."""
    global _whisper
    with _lock:
        if _whisper is None:
            _prepare_torch()
            from faster_whisper import WhisperModel

            settings = get_settings()
            _whisper = WhisperModel(
                settings.whisper_model,
                device="cpu",
                compute_type="int8",
                cpu_threads=cpu_threads(),
            )
        return _whisper


def get_diarization():
    """Load pyannote once. num_speakers=2 is passed on each call, not here."""
    global _diarization
    with _lock:
        if _diarization is None:
            _prepare_torch()
            from pyannote.audio import Pipeline

            settings = get_settings()
            token = settings.hf_token.strip()
            if not token:
                raise RuntimeError("HF_TOKEN is not configured")
            pipeline = Pipeline.from_pretrained(settings.diarization_model, token=token)
            if pipeline is None:
                raise RuntimeError(f"Could not load {settings.diarization_model}")
            import torch

            pipeline.to(torch.device("cpu"))
            _diarization = pipeline
        return _diarization


def get_embedder():
    global _embedder
    with _lock:
        if _embedder is None:
            from sentence_transformers import SentenceTransformer

            _embedder = SentenceTransformer(get_settings().embedding_model, device="cpu")
        return _embedder


def get_reranker():
    global _reranker
    with _lock:
        if _reranker is None:
            from sentence_transformers import CrossEncoder

            _reranker = CrossEncoder(get_settings().reranker_model, device="cpu")
        return _reranker
