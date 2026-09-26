"""Lexical and semantic retrieval, then RRF. Vector failure keeps lexical hits."""

from __future__ import annotations

from app.core.config import get_settings
from app.core.logging import get_logger
from app.db.connection import get_connection
from app.retrieval.rrf import reciprocal_rank_fusion
from app.retrieval.textutil import content_tokens, document_text, or_websearch, query_text
from app.retrieval.types import RetrievedChunk

logger = get_logger(__name__)

_COLUMNS = """
    c.id::text, c.file_id::text, a.filename, c.speaker,
    c.start_ts, c.end_ts, c.content_redacted
"""


def _row(row: tuple, **ranks: int | None) -> RetrievedChunk:
    return RetrievedChunk(
        id=str(row[0]),
        file_id=str(row[1]),
        filename=str(row[2]),
        speaker=str(row[3]),
        start_ts=float(row[4]),
        end_ts=float(row[5]),
        content_redacted=str(row[6]),
        lexical_rank=ranks.get("lexical_rank"),
        semantic_rank=ranks.get("semantic_rank"),
    )


def lexical_search(query: str, *, speaker: str | None = None, limit: int | None = None) -> list[RetrievedChunk]:
    """Full-text search over content_redacted. A miss retries with OR of content words."""
    settings = get_settings()
    cap = limit or settings.lexical_limit
    hits = _lexical(query, speaker, cap)
    if hits:
        return hits
    tokens = content_tokens(query)
    if len(tokens) < 2:
        return []
    logger.info("lexical_or_fallback tokens=%s", len(tokens))
    return _lexical(or_websearch(tokens), speaker, cap)


def _lexical(query: str, speaker: str | None, limit: int) -> list[RetrievedChunk]:
    with get_connection() as connection:
        rows = connection.execute(
            f"""
            SELECT {_COLUMNS}
            FROM chunks c
            JOIN audio_files a ON a.id = c.file_id
            WHERE a.status = 'ready'
              AND (%s::text IS NULL OR c.speaker = %s)
              AND c.search_vector @@ websearch_to_tsquery('english', %s)
            ORDER BY ts_rank_cd(c.search_vector, websearch_to_tsquery('english', %s)) DESC
            LIMIT %s
            """,
            (speaker, speaker, query, query, limit),
        ).fetchall()
        connection.commit()
    return [_row(row, lexical_rank=rank) for rank, row in enumerate(rows, start=1)]


def semantic_search(query: str, *, speaker: str | None = None, limit: int | None = None) -> list[RetrievedChunk]:
    """Cosine search. Small collections use an exact scan so ANN cannot drop a hit."""
    from app.models_runtime import get_embedder

    settings = get_settings()
    cap = limit or settings.semantic_limit
    vector = get_embedder().encode(query_text(query), normalize_embeddings=True)
    literal = _vector_literal(vector.tolist())
    with get_connection() as connection:
        count_row = connection.execute("SELECT count(*) FROM chunks").fetchone()
        count = int(count_row[0]) if count_row else 0
        exact = count <= settings.exact_scan_max_rows
        if exact:
            connection.execute("SET LOCAL enable_indexscan = off")
            connection.execute("SET LOCAL enable_bitmapscan = off")
        rows = connection.execute(
            f"""
            SELECT {_COLUMNS}
            FROM chunks c
            JOIN audio_files a ON a.id = c.file_id
            WHERE a.status = 'ready'
              AND c.embedding IS NOT NULL
              AND (%s::text IS NULL OR c.speaker = %s)
            ORDER BY c.embedding <=> %s::vector
            LIMIT %s
            """,
            (speaker, speaker, literal, cap),
        ).fetchall()
        connection.commit()
    return [_row(row, semantic_rank=rank) for rank, row in enumerate(rows, start=1)]


def _vector_literal(values: list[float]) -> str:
    return "[" + ",".join(f"{float(value):.8f}" for value in values) + "]"


def embed_documents(speakers: list[str], redacted: list[str]) -> list[list[float]]:
    """Encode redacted speaker-prefixed text. The BGE query prefix is not applied."""
    from app.models_runtime import get_embedder

    encoded = get_embedder().encode(
        [document_text(speaker, text) for speaker, text in zip(speakers, redacted, strict=True)],
        normalize_embeddings=True,
    )
    return [list(map(float, vector)) for vector in encoded]


def retrieve(
    query: str,
    *,
    speaker: str | None = None,
    mode: str = "hybrid",
) -> tuple[list[RetrievedChunk], str | None]:
    """Run the requested retriever. mode is lexical, semantic, hybrid_rrf, or hybrid.

    hybrid adds reranking later. This function stops at fusion.
    Returns (chunks, fallback_name).
    """
    settings = get_settings()
    if mode == "lexical":
        hits = lexical_search(query, speaker=speaker, limit=settings.rrf_limit)
        return hits, None
    if mode == "semantic":
        hits = semantic_search(query, speaker=speaker, limit=settings.rrf_limit)
        return hits, None

    lexical: list[RetrievedChunk] = []
    semantic: list[RetrievedChunk] = []
    lexical_error = False
    vector_error = False
    try:
        lexical = lexical_search(query, speaker=speaker)
    except Exception as exc:
        lexical_error = True
        logger.warning("lexical_failed error=%s", type(exc).__name__)
    try:
        semantic = semantic_search(query, speaker=speaker)
    except Exception as exc:
        vector_error = True
        logger.warning("vector_failed fallback=lexical error=%s", type(exc).__name__)
    if vector_error:
        return lexical[: settings.rrf_limit], "lexical"
    if not semantic:
        logger.info("vector_empty using=lexical")
        return lexical[: settings.rrf_limit], None
    if not lexical:
        logger.info("lexical_empty using=semantic error=%s", lexical_error)
        return semantic[: settings.rrf_limit], "semantic_only" if lexical_error else None
    fused = reciprocal_rank_fusion(
        lexical,
        semantic,
        constant=settings.rrf_k,
        limit=settings.rrf_limit,
    )
    return fused, None
