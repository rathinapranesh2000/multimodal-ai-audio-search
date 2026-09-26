"""Create tables and the best vector index the server will accept."""

from __future__ import annotations

from pathlib import Path

from app.core.logging import get_logger
from app.db.connection import get_connection

logger = get_logger(__name__)
SCHEMA_PATH = Path(__file__).with_name("schema.sql")


def _version_tuple(value: str) -> tuple[int, ...]:
    parts: list[int] = []
    for piece in value.split("."):
        digits = ""
        for character in piece:
            if character.isdigit():
                digits += character
            else:
                break
        if not digits:
            break
        parts.append(int(digits))
    return tuple(parts)


def vector_index_kind(extension_version: str | None) -> str:
    """HNSW arrived in pgvector 0.5.0. Older servers get IVFFlat, then exact scan."""
    if extension_version and _version_tuple(extension_version) >= (0, 5, 0):
        return "hnsw"
    if extension_version:
        return "ivfflat"
    return "exact"


def _apply_schema(connection) -> None:
    connection.execute("CREATE SCHEMA IF NOT EXISTS audiorag")
    connection.execute("SET search_path TO audiorag, public")
    script = SCHEMA_PATH.read_text(encoding="utf-8")
    connection.execute(script)
    connection.commit()


def _extension_version(connection) -> str | None:
    try:
        connection.execute("CREATE EXTENSION IF NOT EXISTS vector")
        connection.commit()
    except Exception as exc:
        connection.rollback()
        logger.warning("vector extension create skipped: %s", type(exc).__name__)
    row = connection.execute(
        "SELECT extversion FROM pg_extension WHERE extname = 'vector'"
    ).fetchone()
    connection.commit()
    return None if row is None else str(row[0])


def _create_vector_index(connection, kind: str) -> str:
    """Create an ANN index when the server supports it. Search can still be exact."""
    connection.execute("DROP INDEX IF EXISTS chunks_embedding_hnsw_idx")
    connection.execute("DROP INDEX IF EXISTS chunks_embedding_ivfflat_idx")
    if kind == "hnsw":
        connection.execute(
            """
            CREATE INDEX chunks_embedding_hnsw_idx
            ON chunks USING hnsw (embedding vector_cosine_ops)
            """
        )
        return "hnsw"
    if kind == "ivfflat":
        connection.execute(
            """
            CREATE INDEX chunks_embedding_ivfflat_idx
            ON chunks USING ivfflat (embedding vector_cosine_ops)
            WITH (lists = 10)
            """
        )
        return "ivfflat"
    return "exact"


def ensure_vector_index() -> str:
    """Create the ANN index once rows exist. An existing embedding index is left in place."""
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT indexdef FROM pg_indexes
            WHERE schemaname = 'audiorag'
              AND tablename = 'chunks'
              AND indexdef ILIKE '%embedding%'
            """
        ).fetchone()
        connection.commit()
        if row is not None:
            definition = str(row[0]).lower()
            if "hnsw" in definition:
                return "hnsw"
            if "ivfflat" in definition:
                return "ivfflat"
        version = _extension_version(connection)
        kind = vector_index_kind(version)
        try:
            created = _create_vector_index(connection, kind)
            connection.commit()
            return created
        except Exception as exc:
            connection.rollback()
            logger.warning(
                "vector index %s failed (%s); search will use exact scan",
                kind,
                type(exc).__name__,
            )
            return "exact"


def initialize_database() -> str:
    """Apply schema.sql and return the vector index kind that was created."""
    with get_connection() as connection:
        _apply_schema(connection)
        version = _extension_version(connection)
        kind = vector_index_kind(version)
        try:
            created = _create_vector_index(connection, kind)
            connection.commit()
        except Exception as exc:
            connection.rollback()
            logger.warning(
                "vector index %s failed (%s); falling back to exact scan",
                kind,
                type(exc).__name__,
            )
            created = "exact"
        logger.info("database_ready vector_index=%s pgvector=%s", created, version or "missing")
        return created


def main() -> None:
    print(f"vector_index={initialize_database()}")


if __name__ == "__main__":
    main()
