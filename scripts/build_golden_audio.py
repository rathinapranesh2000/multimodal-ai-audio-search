"""Build 16 kHz mono interviews from the original scripts.

The script timeline is an aid for labeling. It is not the official golden set.
Official labels are written only after a person checks the transcript.
"""

from __future__ import annotations

import asyncio
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dataset.scripts.catalog import INTERVIEWS

AUDIO_DIR = ROOT / "dataset" / "synthetic_sample"
WORK_DIR = ROOT / "dataset" / "work"
TARGET_SECONDS = 8.5 * 60
MIN_SECONDS = 8 * 60
MAX_SECONDS = 10 * 60


def _run(command: list[str]) -> None:
    completed = subprocess.run(command, capture_output=True, text=True, check=False)
    if completed.returncode != 0:
        tail = (completed.stderr or "command failed").strip().splitlines()
        raise RuntimeError(tail[-1] if tail else "command failed")


def _duration(path: Path) -> float:
    completed = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(f"ffprobe failed for {path.name}")
    return float(completed.stdout.strip())


def _usable(path: Path) -> bool:
    """A zero-byte file is a failed speech attempt, not a finished turn."""
    return path.is_file() and path.stat().st_size > 1000


# These neural voices currently return no audio from the Edge service.
_VOICE_FALLBACK = {
    "en-US-DavisNeural": "en-US-AndrewNeural",
    "en-US-TonyNeural": "en-US-ChristopherNeural",
    "en-US-SaraNeural": "en-US-AvaNeural",
}


async def _speak_once(text: str, voice: str, destination: Path, rate: str) -> None:
    import edge_tts

    if destination.exists():
        destination.unlink()
    communicator = edge_tts.Communicate(text, voice, rate=rate)
    await communicator.save(str(destination))
    if not _usable(destination):
        raise edge_tts.exceptions.NoAudioReceived("empty audio file")


async def _speak(text: str, voice: str, destination: Path) -> str:
    """Speak one turn. Returns the voice that actually produced audio.

    A dead voice is replaced once. Each attempt waits, because the service drops bursts.
    """
    candidates = [voice]
    replacement = _VOICE_FALLBACK.get(voice)
    if replacement and replacement not in candidates:
        candidates.append(replacement)
    last_error: Exception | None = None
    for candidate in candidates:
        for attempt, rate in enumerate(("-12%", "+0%"), start=1):
            try:
                await _speak_once(text, candidate, destination, rate)
                if candidate != voice:
                    print(f"    voice {voice} unavailable, used {candidate}")
                return candidate
            except Exception as exc:
                last_error = exc
                print(
                    f"    speech retry {attempt}/2 voice={candidate} "
                    f"({type(exc).__name__})"
                )
                await asyncio.sleep(2 * attempt)
    raise RuntimeError(f"No audio for voice {voice}") from last_error


def _to_wav(source: Path, destination: Path) -> None:
    _run(
        [
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
    )


def _silence(destination: Path, seconds: float = 0.45) -> None:
    _run(
        [
            "ffmpeg",
            "-y",
            "-f",
            "lavfi",
            "-i",
            "anullsrc=r=16000:cl=mono",
            "-t",
            str(seconds),
            "-c:a",
            "pcm_s16le",
            str(destination),
        ]
    )


def _concat(parts: list[Path], destination: Path) -> None:
    listing = destination.with_suffix(".txt")
    listing.write_text(
        "".join(f"file '{part.resolve()}'\n" for part in parts),
        encoding="utf-8",
    )
    _run(
        [
            "ffmpeg",
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(listing),
            "-c",
            "copy",
            str(destination),
        ]
    )


def _atempo_filter(tempo: float) -> str:
    """ffmpeg accepts atempo only between 0.5 and 2.0, so chain stages when needed."""
    stages: list[str] = []
    remaining = tempo
    while remaining < 0.5:
        stages.append("atempo=0.5")
        remaining /= 0.5
    while remaining > 2.0:
        stages.append("atempo=2.0")
        remaining /= 2.0
    stages.append(f"atempo={remaining:.4f}")
    return ",".join(stages)


def _fit_duration(source: Path, destination: Path) -> float:
    current = _duration(source)
    if MIN_SECONDS <= current <= MAX_SECONDS:
        destination.write_bytes(source.read_bytes())
        return current
    tempo = min(2.0, max(0.25, current / TARGET_SECONDS))
    _run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(source),
            "-filter:a",
            _atempo_filter(tempo),
            "-c:a",
            "pcm_s16le",
            str(destination),
        ]
    )
    return _duration(destination)


async def build_one(interview: dict) -> dict:
    slug = interview["slug"]
    work = WORK_DIR / slug
    work.mkdir(parents=True, exist_ok=True)
    silence = work / "silence.wav"
    _silence(silence)
    parts: list[Path] = []
    timeline = []
    cursor = 0.0
    silence_seconds = _duration(silence)
    turn_index = 0
    for question, answer in interview["pairs"]:
        for speaker, text, voice in (
            ("A", question, interview["voices"][0]),
            ("B", answer, interview["voices"][1]),
        ):
            mp3 = work / f"{turn_index:03d}.mp3"
            wav = work / f"{turn_index:03d}.wav"
            if not _usable(wav):
                if not _usable(mp3):
                    print(f"    turn {turn_index:03d} {voice}")
                    await _speak(text, voice, mp3)
                    await asyncio.sleep(0.6)
                _to_wav(mp3, wav)
            duration = _duration(wav)
            timeline.append(
                {
                    "speaker_role": speaker,
                    "start_ts": round(cursor, 3),
                    "end_ts": round(cursor + duration, 3),
                    "text": text,
                }
            )
            parts.append(wav)
            cursor += duration
            parts.append(silence)
            cursor += silence_seconds
            turn_index += 1
    raw = work / "raw.wav"
    _concat(parts, raw)
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    final = AUDIO_DIR / f"{slug}.wav"
    duration = _fit_duration(raw, final)
    scale = duration / cursor if cursor else 1.0
    for item in timeline:
        item["start_ts"] = round(item["start_ts"] * scale, 3)
        item["end_ts"] = round(item["end_ts"] * scale, 3)
    return {
        "slug": slug,
        "title": interview["title"],
        "file": final.name,
        "duration_seconds": round(duration, 3),
        "voices": interview["voices"],
        "anchors": interview["anchors"],
        "turns": timeline,
    }


async def main() -> None:
    for tool in ("ffmpeg", "ffprobe"):
        if subprocess.run(["bash", "-lc", f"command -v {tool}"], capture_output=True).returncode != 0:
            raise SystemExit(f"{tool} is not on PATH")
    golden = ROOT / "dataset" / "golden"
    golden.mkdir(parents=True, exist_ok=True)
    timeline_path = golden / "script_timeline.json"
    records = []
    for interview in INTERVIEWS:
        print(f"building {interview['slug']}")
        records.append(await build_one(interview))
        print(f"  {records[-1]['duration_seconds']:.1f}s")
        timeline_path.write_text(json.dumps(records, indent=2), encoding="utf-8")
    print(f"wrote {timeline_path}")


if __name__ == "__main__":
    asyncio.run(main())
