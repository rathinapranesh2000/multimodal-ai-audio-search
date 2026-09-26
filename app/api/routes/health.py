"""Process health checks. The plain health route does not open a database connection."""

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.db.connection import get_connection

router = APIRouter(tags=["health"])

_CHUNK_COLUMNS = {
    "id",
    "file_id",
    "speaker",
    "start_ts",
    "end_ts",
    "content",
    "content_redacted",
    "embedding",
    "search_vector",
}


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "app": get_settings().app_name}


@router.get("/health/db")
def health_db():
    try:
        with get_connection() as connection:
            connection.execute("SELECT 1").fetchone()
            connection.commit()
    except Exception as exc:
        return _down(exc)
    return {"status": "ok"}


@router.get("/health/pgvector")
def health_pgvector():
    try:
        with get_connection() as connection:
            row = connection.execute(
                "SELECT extversion FROM pg_extension WHERE extname = 'vector'"
            ).fetchone()
            connection.commit()
    except Exception as exc:
        return _down(exc)
    if row is None:
        return JSONResponse(status_code=503, content={"status": "missing", "detail": "pgvector is not installed"})
    return {"status": "ok", "version": str(row[0])}


@router.get("/health/schema")
def health_schema():
    try:
        with get_connection() as connection:
            rows = connection.execute(
                """
                SELECT column_name
                FROM information_schema.columns
                WHERE table_schema = 'audiorag' AND table_name = 'chunks'
                """
            ).fetchall()
            connection.commit()
    except Exception as exc:
        return _down(exc)
    present = {row[0] for row in rows}
    missing = sorted(_CHUNK_COLUMNS - present)
    if missing:
        return JSONResponse(
            status_code=503,
            content={"status": "incomplete", "missing": missing},
        )
    return {"status": "ok", "table": "chunks"}


def _down(exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=503,
        content={"status": "unavailable", "error": type(exc).__name__},
    )
