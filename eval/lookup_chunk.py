"""Print lexical and semantic candidates inside one recording.

This surfaces chunks for a person to review. It does not decide correctness.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.db.connection import get_connection
from app.retrieval.search import _COLUMNS, _row, _vector_literal
from app.retrieval.textutil import content_tokens, or_websearch, query_text
from app.retrieval.types import RetrievedChunk

TOP_N = 5


def lexical_in_file(query: str, filename: str, *, limit: int = TOP_N) -> list[RetrievedChunk]:
    hits = _lexical_in_file(query, filename, limit)
    if hits:
        return hits
    tokens = content_tokens(query)
    if len(tokens) < 2:
        return []
    return _lexical_in_file(or_websearch(tokens), filename, limit)


def _lexical_in_file(query: str, filename: str, limit: int) -> list[RetrievedChunk]:
    with get_connection() as connection:
        rows = connection.execute(
            f"""
            SELECT {_COLUMNS}
            FROM chunks c
            JOIN audio_files a ON a.id = c.file_id
            WHERE a.status = 'ready'
              AND a.filename = %s
              AND c.search_vector @@ websearch_to_tsquery('english', %s)
            ORDER BY ts_rank_cd(c.search_vector, websearch_to_tsquery('english', %s)) DESC
            LIMIT %s
            """,
            (filename, query, query, limit),
        ).fetchall()
        connection.commit()
    return [_row(row, lexical_rank=rank) for rank, row in enumerate(rows, start=1)]


def semantic_in_file(query: str, filename: str, *, limit: int = TOP_N) -> list[RetrievedChunk]:
    from app.models_runtime import get_embedder

    vector = get_embedder().encode(query_text(query), normalize_embeddings=True)
    literal = _vector_literal(vector.tolist())
    with get_connection() as connection:
        rows = connection.execute(
            f"""
            SELECT {_COLUMNS}
            FROM chunks c
            JOIN audio_files a ON a.id = c.file_id
            WHERE a.status = 'ready'
              AND a.filename = %s
              AND c.embedding IS NOT NULL
            ORDER BY c.embedding <=> %s::vector
            LIMIT %s
            """,
            (filename, literal, limit),
        ).fetchall()
        connection.commit()
    return [_row(row, semantic_rank=rank) for rank, row in enumerate(rows, start=1)]


def _table(title: str, hits: list[RetrievedChunk]) -> str:
    lines = [title, "rank  chunk_id                              speaker      start_ts   end_ts  content_redacted"]
    if not hits:
        lines.append("(no candidates)")
        return "\n".join(lines)
    for index, hit in enumerate(hits, start=1):
        text = " ".join(hit.content_redacted.split())
        lines.append(
            f"{index:<5} {hit.id:<37} {hit.speaker:<12} {hit.start_ts:>8.1f} {hit.end_ts:>8.1f}  {text}"
        )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Show top lexical and semantic chunks in one file.")
    parser.add_argument("--file", required=True, help="Recording filename, for example harbor-pricing.wav")
    parser.add_argument("--query", required=True, help="Search text")
    args = parser.parse_args(argv)
    print(_table(f"Lexical  file={args.file}", lexical_in_file(args.query, args.file)))
    print()
    print(_table(f"Semantic file={args.file}", semantic_in_file(args.query, args.file)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
