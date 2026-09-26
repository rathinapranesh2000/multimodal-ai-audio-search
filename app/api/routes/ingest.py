"""Upload and ingestion status."""

from __future__ import annotations

import json
from uuid import UUID

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.core.logging import get_logger
from app.db.connection import get_connection
from app.pipeline.audio import (
    AudioValidationError,
    original_path,
    validate_upload,
)
from app.pipeline.ingest import create_file_row, record_failure, start_ingest
from app.schemas import IngestAccepted, IngestStatus

logger = get_logger(__name__)
router = APIRouter(tags=["ingest"])


@router.post("/ingest", status_code=202, response_model=IngestAccepted)
async def ingest_audio(
    file: UploadFile = File(...),
    speaker_map: str = Form("{}"),
) -> IngestAccepted:
    """Accept an upload and return while diarization and transcription run."""
    payload = await file.read()
    try:
        filename = validate_upload(file.filename or "", len(payload))
        mapping = _speaker_map(speaker_map)
    except (AudioValidationError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    file_id = ""
    try:
        file_id = create_file_row(filename, mapping)
        destination = original_path(UUID(file_id), filename)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(payload)
    except Exception as exc:
        logger.exception("ingest_accept_failed")
        if file_id:
            record_failure(file_id, "Could not store the upload")
        raise HTTPException(status_code=500, detail="Could not store the upload") from exc

    start_ingest(file_id, filename, mapping)
    return IngestAccepted(file_id=file_id, status="processing", stage="normalizing")


@router.get("/ingest/{file_id}/status", response_model=IngestStatus)
def ingest_status(file_id: str) -> IngestStatus:
    from app.pipeline.audio import assert_safe_file_id

    try:
        assert_safe_file_id(file_id)
    except AudioValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT id::text, filename, status, stage, progress, timings, error,
                   duration_seconds, chunk_count
            FROM audio_files
            WHERE id = %s
            """,
            (file_id,),
        ).fetchone()
        connection.commit()
    if row is None:
        raise HTTPException(status_code=404, detail="Recording not found")
    return IngestStatus(
        file_id=row[0],
        filename=row[1],
        status=row[2],
        stage=row[3],
        progress=row[4] or {},
        timings={key: float(value) for key, value in (row[5] or {}).items()},
        error=row[6],
        duration_seconds=None if row[7] is None else float(row[7]),
        chunk_count=int(row[8] or 0),
    )


def _speaker_map(raw: str) -> dict[str, str]:
    if not raw.strip():
        return {}
    parsed = json.loads(raw)
    if not isinstance(parsed, dict):
        raise AudioValidationError("speaker_map must be a JSON object")
    return {str(key): str(value) for key, value in parsed.items()}
