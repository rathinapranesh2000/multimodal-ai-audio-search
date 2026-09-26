"""Keep the sentences that overlap the query. Failure returns the original redacted text."""

from __future__ import annotations

import re

from app.core.logging import get_logger
from app.retrieval.types import RetrievedChunk

logger = get_logger(__name__)
_SENTENCE = re.compile(r"[^.!?\n]+[.!?]?")
_TOKEN = re.compile(r"[a-z0-9']+")


def _tokens(text: str) -> set[str]:
    return {token for token in _TOKEN.findall(text.lower()) if len(token) > 2}


def compress_chunk(query: str, chunk: RetrievedChunk) -> str:
    sentences = [part.strip() for part in _SENTENCE.findall(chunk.content_redacted) if part.strip()]
    if not sentences:
        return chunk.content_redacted.strip()
    query_tokens = _tokens(query)
    ranked = sorted(
        sentences,
        key=lambda sentence: len(query_tokens & _tokens(sentence)),
        reverse=True,
    )
    chosen = [sentence for sentence in ranked[:3] if query_tokens & _tokens(sentence)]
    if not chosen:
        chosen = sentences[:2]
    return " ".join(chosen)


def compress(
    query: str, chunks: list[RetrievedChunk]
) -> tuple[list[tuple[RetrievedChunk, str]], str | None]:
    """Return evidence snippets. On failure, return the full redacted chunk text."""
    try:
        return [(chunk, compress_chunk(query, chunk)) for chunk in chunks], None
    except Exception as exc:
        logger.warning("compression_failed fallback=original error=%s", type(exc).__name__)
        return [(chunk, chunk.content_redacted) for chunk in chunks], "compression_failed"
