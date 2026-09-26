"""Cross-encoder rerank of the fused candidate set only."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import replace

from app.core.logging import get_logger
from app.retrieval.types import RetrievedChunk

logger = get_logger(__name__)


def _model_scores(query: str, chunks: list[RetrievedChunk]) -> list[float]:
    from app.models_runtime import get_reranker

    pairs = [(query, chunk.content_redacted) for chunk in chunks]
    raw = get_reranker().predict(pairs)
    return [float(score) for score in raw]


def rerank(
    query: str,
    chunks: list[RetrievedChunk],
    *,
    limit: int = 5,
    score_fn: Callable[[str, list[RetrievedChunk]], list[float]] | None = None,
) -> tuple[list[RetrievedChunk], str | None]:
    """Reorder the RRF set. A model failure keeps RRF order and reports the fallback."""
    if not chunks:
        return [], None
    if len(chunks) == 1:
        return chunks[:limit], None
    try:
        scores = (score_fn or _model_scores)(query, chunks)
        ordered = sorted(
            (replace(chunk, rerank_score=score) for chunk, score in zip(chunks, scores, strict=True)),
            key=lambda chunk: chunk.rerank_score or 0.0,
            reverse=True,
        )
        return ordered[:limit], None
    except Exception as exc:
        logger.warning("rerank_failed fallback=rrf error=%s", type(exc).__name__)
        return chunks[:limit], "rrf"
