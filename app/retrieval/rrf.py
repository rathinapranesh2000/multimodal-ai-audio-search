"""Reciprocal rank fusion. Scores from the two retrievers are never compared directly."""

from __future__ import annotations

from dataclasses import replace

from app.retrieval.types import RetrievedChunk


def reciprocal_rank_fusion(
    lexical: list[RetrievedChunk],
    semantic: list[RetrievedChunk],
    *,
    constant: int = 60,
    limit: int = 20,
) -> list[RetrievedChunk]:
    """RRF(d) = sum 1 / (k + rank). Rank is 1-based."""
    scores: dict[str, float] = {}
    chosen: dict[str, RetrievedChunk] = {}
    for rank, chunk in enumerate(lexical, start=1):
        scores[chunk.id] = scores.get(chunk.id, 0.0) + 1.0 / (constant + rank)
        current = chosen.get(chunk.id, chunk)
        chosen[chunk.id] = replace(
            current,
            lexical_rank=rank,
            semantic_rank=current.semantic_rank,
            rrf_score=scores[chunk.id],
        )
    for rank, chunk in enumerate(semantic, start=1):
        scores[chunk.id] = scores.get(chunk.id, 0.0) + 1.0 / (constant + rank)
        current = chosen.get(chunk.id, chunk)
        chosen[chunk.id] = replace(
            current,
            lexical_rank=current.lexical_rank,
            semantic_rank=rank,
            rrf_score=scores[chunk.id],
        )
    ordered = sorted(chosen, key=lambda chunk_id: scores[chunk_id], reverse=True)
    return [chosen[chunk_id] for chunk_id in ordered[:limit]]
