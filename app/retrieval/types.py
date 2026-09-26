"""Retrieved evidence. content (unredacted) is intentionally absent."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RetrievedChunk:
    id: str
    file_id: str
    filename: str
    speaker: str
    start_ts: float
    end_ts: float
    content_redacted: str
    lexical_rank: int | None = None
    semantic_rank: int | None = None
    rrf_score: float | None = None
    rerank_score: float | None = None


def explain(chunk: RetrievedChunk, *, fallback: str | None = None) -> str:
    """Short reason a judge or user can read next to a hit."""
    parts: list[str] = []
    if fallback:
        parts.append(fallback)
    if chunk.lexical_rank is not None:
        parts.append(f"lexical rank {chunk.lexical_rank}")
    if chunk.semantic_rank is not None:
        parts.append(f"semantic rank {chunk.semantic_rank}")
    if chunk.rrf_score is not None:
        parts.append(f"rrf {chunk.rrf_score:.4f}")
    if chunk.rerank_score is not None:
        parts.append(f"rerank {chunk.rerank_score:.3f}")
    return ", ".join(parts) if parts else "retrieved"
