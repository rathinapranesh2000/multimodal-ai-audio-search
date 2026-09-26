"""Search orchestration: guardrails, retrieval, rerank, compression, grounded answer."""

from __future__ import annotations

import time

from app.core.config import get_settings
from app.core.logging import get_logger
from app.retrieval.compress import compress
from app.retrieval.generate import generate_answer
from app.retrieval.guardrails import prepare_query
from app.retrieval.rerank import rerank
from app.retrieval.search import retrieve
from app.retrieval.speakers import parse_speaker_constraint
from app.retrieval.types import RetrievedChunk, explain
from app.schemas import Citation, SearchHit, SearchResponse

logger = get_logger(__name__)


class EmptyQuery(ValueError):
    """The caller sent a blank question."""


def run_search(query: str, *, mode: str = "hybrid", trace_id: str) -> SearchResponse:
    """Execute one search. mode selects the ablation configuration."""
    started = time.perf_counter()
    settings = get_settings()
    guarded = prepare_query(query, max_chars=settings.max_query_chars)
    if not guarded.query:
        raise EmptyQuery("Enter a search query")
    if guarded.injection_stripped:
        logger.warning("injection_stripped")
    speaker, lexical_query = parse_speaker_constraint(guarded.query)
    search_query = lexical_query or guarded.query

    stage = time.perf_counter()
    chunks, retrieval_fallback = retrieve(search_query, speaker=speaker, mode=mode)
    retrieval_ms = (time.perf_counter() - stage) * 1000
    rerank_fallback = None
    stage = time.perf_counter()
    if mode == "hybrid":
        chunks, rerank_fallback = rerank(search_query, chunks, limit=settings.rerank_limit)
    else:
        chunks = chunks[: settings.rerank_limit]
    rerank_ms = (time.perf_counter() - stage) * 1000

    below = _below_threshold(chunks)
    fallbacks = [name for name in (retrieval_fallback, rerank_fallback) if name]
    if below:
        answer = "No relevant evidence found."
        citations: list[RetrievedChunk] = []
        snippets: list[tuple[RetrievedChunk, str]] = [(chunk, chunk.content_redacted) for chunk in chunks]
        fallbacks.append("no_evidence")
    else:
        snippets, compression_fallback = compress(search_query, chunks)
        if compression_fallback:
            fallbacks.append(compression_fallback)
        answer, citations, generation_fallback = generate_answer(guarded.query, snippets)
        if generation_fallback:
            fallbacks.append(generation_fallback)

    elapsed_ms = (time.perf_counter() - started) * 1000
    logger.info(
        "search_stages retrieval_ms=%.1f rerank_ms=%.1f total_ms=%.1f",
        retrieval_ms,
        rerank_ms,
        elapsed_ms,
    )
    logger.info(
        "search_done mode=%s hits=%s fallback=%s elapsed_ms=%.1f",
        mode,
        len(chunks),
        ",".join(fallbacks) or "none",
        elapsed_ms,
    )
    citation_ids = {chunk.id for chunk in citations}
    return SearchResponse(
        query=guarded.query,
        answer=answer,
        citations=[_citation(chunk) for chunk in citations],
        results=[
            _hit(chunk, snippet, cited=chunk.id in citation_ids, fallback=retrieval_fallback)
            for chunk, snippet in snippets
        ],
        fallback=",".join(fallbacks) or None,
        query_truncated=guarded.truncated,
        injection_stripped=guarded.injection_stripped,
        speaker_filter=speaker,
        mode=mode,
        trace_id=trace_id,
        elapsed_ms=round(elapsed_ms, 1),
    )


def _below_threshold(chunks: list[RetrievedChunk]) -> bool:
    if not chunks:
        return True
    settings = get_settings()
    scores = [chunk.rerank_score for chunk in chunks if chunk.rerank_score is not None]
    if not scores:
        return False
    return max(scores) < settings.relevance_min_logit


def _citation(chunk: RetrievedChunk) -> Citation:
    return Citation(
        file_id=chunk.file_id,
        file=chunk.filename,
        speaker=chunk.speaker,
        start_ts=chunk.start_ts,
        end_ts=chunk.end_ts,
    )


def _hit(
    chunk: RetrievedChunk,
    snippet: str,
    *,
    cited: bool,
    fallback: str | None,
) -> SearchHit:
    return SearchHit(
        file_id=chunk.file_id,
        file=chunk.filename,
        speaker=chunk.speaker,
        start_ts=chunk.start_ts,
        end_ts=chunk.end_ts,
        snippet=snippet,
        cited=cited,
        why=explain(chunk, fallback="vector search failed; lexical fallback" if fallback == "lexical" else None),
        lexical_rank=chunk.lexical_rank,
        semantic_rank=chunk.semantic_rank,
        rrf_score=chunk.rrf_score,
        rerank_score=chunk.rerank_score,
    )
