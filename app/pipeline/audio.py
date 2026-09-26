"""Upload checks, ffmpeg normalization, and safe on-disk paths."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from uuid import UUID

from app.core.config import get_settings

ALLOWED_SUFFIXES = frozenset({".wav", ".mp3", ".m4a", ".flac", ".ogg", ".aac", ".opus"})


class AudioValidationError(ValueError):
    """The upload cannot enter the pipeline."""


def assert_safe_file_id(file_id: str) -> UUID:
    """Reject anything that is not a UUID so playback cannot escape the audio root."""
    try:
        return UUID(file_id)
    except (ValueError, AttributeError, TypeError) as exc:
        raise AudioValidationError("file_id must be a UUID") from exc


def safe_filename(name: str) -> str:
    """Keep only the final path segment."""
    cleaned = Path(name or "").name.strip()
    if not cleaned or cleaned in {".", ".."}:
        raise AudioValidationError("A file name is required")
    return cleaned


def validate_upload(filename: str, size: int) -> str:
    """Check the name and size before anything is written or inserted."""
    cleaned = safe_filename(filename)
    suffix = Path(cleaned).suffix.lower()
    if suffix not in ALLOWED_SUFFIXES:
        raise AudioValidationError(
            f"Unsupported file type {suffix or '(none)'}. Use wav, mp3, m4a, flac, ogg, aac, or opus."
        )
    if size <= 0:
        raise AudioValidationError("The upload is empty")
    if size > get_settings().max_upload_bytes:
        raise AudioValidationError("The upload exceeds the size limit")
    return cleaned


def require_ffmpeg() -> None:
    """Stop when ffmpeg or ffprobe is missing from PATH. Do not guess a private path."""
    missing = [tool for tool in ("ffmpeg", "ffprobe") if shutil.which(tool) is None]
    if missing:
        raise AudioValidationError(
            f"{', '.join(missing)} is not on PATH. Install a user-space binary and retry."
        )


def normalize_wav(source: Path, destination: Path) -> None:
    """Convert any accepted upload to 16 kHz mono PCM WAV."""
    require_ffmpeg()
    destination.parent.mkdir(parents=True, exist_ok=True)
    command = [
        "ffmpeg",
        "-y",
        "-i",
        str(source),
        "-ac",
        "1",
        "-ar",
        "16000",
        "-c:a",
        "pcm_s16le",
        str(destination),
    ]
    completed = subprocess.run(command, capture_output=True, text=True, check=False)
    if completed.returncode != 0 or not destination.is_file():
        detail = (completed.stderr or "ffmpeg failed").strip().splitlines()
        tail = detail[-1] if detail else "ffmpeg failed"
        raise AudioValidationError(f"Could not normalize audio: {tail}")


def probe_duration(path: Path) -> float:
    """Read duration in seconds with ffprobe."""
    require_ffmpeg()
    command = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        str(path),
    ]
    completed = subprocess.run(command, capture_output=True, text=True, check=False)
    if completed.returncode != 0:
        raise AudioValidationError("ffprobe could not read the audio duration")
    try:
        duration = float(completed.stdout.strip())
    except ValueError as exc:
        raise AudioValidationError("ffprobe returned an unreadable duration") from exc
    settings = get_settings()
    if duration < settings.min_duration_seconds:
        raise AudioValidationError("The recording is too short")
    if duration > settings.max_duration_seconds:
        raise AudioValidationError("The recording is longer than 30 minutes")
    return duration


def recording_dir(file_id: UUID) -> Path:
    """Directory for one upload. The result stays under the audio root."""
    root = get_settings().audio_root.resolve()
    path = (root / str(file_id)).resolve()
    if path == root or not path.is_relative_to(root):
        raise AudioValidationError("Refusing to resolve a path outside the audio directory")
    return path


def normalized_path(file_id: UUID) -> Path:
    """Absolute path of the normalized WAV. The result stays under the audio root."""
    root = get_settings().audio_root.resolve()
    path = (root / str(file_id) / "normalized.wav").resolve()
    if not path.is_relative_to(root):
        raise AudioValidationError("Refusing to resolve a path outside the audio directory")
    return path


def original_path(file_id: UUID, filename: str) -> Path:
    root = get_settings().audio_root.resolve()
    path = (root / str(file_id) / f"original{Path(filename).suffix.lower()}").resolve()
    if not path.is_relative_to(root):
        raise AudioValidationError("Refusing to store a file outside the audio directory")
    return path
