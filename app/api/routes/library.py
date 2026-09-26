"""Library listing, timestamped audio playback, and recording removal."""

import shutil

from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import FileResponse

from app.db.connection import get_connection
from app.pipeline.audio import (
    AudioValidationError,
    assert_safe_file_id,
    normalized_path,
    recording_dir,
)
from app.schemas import Conversation

router = APIRouter(tags=["library"])


@router.get("/conversations", response_model=list[Conversation])
def conversations() -> list[Conversation]:
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT id::text, filename, status, stage, duration_seconds, chunk_count,
                   to_char(created_at AT TIME ZONE 'UTC', 'YYYY-MM-DD"T"HH24:MI:SS"Z"')
            FROM audio_files
            ORDER BY created_at DESC
            """
        ).fetchall()
        connection.commit()
    return [
        Conversation(
            file_id=row[0],
            filename=row[1],
            status=row[2],
            stage=row[3],
            duration_seconds=None if row[4] is None else float(row[4]),
            chunk_count=int(row[5] or 0),
            created_at=row[6],
        )
        for row in rows
    ]


@router.delete("/conversations/{file_id}", status_code=204)
def delete_conversation(file_id: str) -> Response:
    """Drop the recording, its chunks, and the files stored for that id."""
    try:
        parsed = assert_safe_file_id(file_id)
    except AudioValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    with get_connection() as connection:
        row = connection.execute(
            "DELETE FROM audio_files WHERE id = %s RETURNING id",
            (str(parsed),),
        ).fetchone()
        connection.commit()
    if row is None:
        raise HTTPException(status_code=404, detail="Recording was not found")
    directory = recording_dir(parsed)
    if directory.is_dir():
        shutil.rmtree(directory)
    return Response(status_code=204)


@router.get("/audio/{file_id}")
def audio_file(file_id: str) -> FileResponse:
    """Serve the normalized WAV. The id must be a UUID under the audio root."""
    try:
        parsed = assert_safe_file_id(file_id)
    except AudioValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    path = normalized_path(parsed)
    if not path.is_file():
        raise HTTPException(status_code=404, detail="Audio is not ready")
    return FileResponse(path, media_type="audio/wav", filename=f"{parsed}.wav")
