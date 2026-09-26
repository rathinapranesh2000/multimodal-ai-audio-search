"""Pull an explicit speaker constraint out of a question before retrieval."""

from __future__ import annotations

import re

_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"\bspeaker[\s_-]*0*0\b|\bspeaker\s+zero\b|\bfirst speaker\b", re.I), "SPEAKER_00"),
    (re.compile(r"\bspeaker[\s_-]*0*1\b|\bspeaker\s+one\b|\bsecond speaker\b", re.I), "SPEAKER_01"),
)


def parse_speaker_constraint(query: str) -> tuple[str | None, str]:
    """Return (SPEAKER_00|SPEAKER_01|None, query with that mention removed).

    "Speaker 01" and "speaker 1" map to SPEAKER_01, matching pyannote labels.
    "Speaker 00", "speaker 0", and "first speaker" map to SPEAKER_00.
    """
    speaker = None
    cleaned = query
    for pattern, label in _PATTERNS:
        if pattern.search(cleaned):
            speaker = label
            cleaned = pattern.sub(" ", cleaned)
            break
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return speaker, cleaned
