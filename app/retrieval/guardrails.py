"""Query checks that run before retrieval. Transcript text is never an instruction."""

from __future__ import annotations

import re
from dataclasses import dataclass

_INJECTION = re.compile(
    r"(ignore (all |any )?(previous|prior|above) instructions|"
    r"disregard (the |all )?(system|previous)|"
    r"system prompt|you are now|"
    r"reveal (your|the) (prompt|instructions)|"
    r"\bdrop\s+table\b|\bdatabase_url\b)",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class GuardResult:
    query: str
    truncated: bool
    injection_stripped: bool


def prepare_query(query: str, *, max_chars: int = 500) -> GuardResult:
    """Normalize a user query.

    Empty input is rejected by the route. Over-long input is truncated and still
    searched. Injection phrases are removed, then retrieval runs on what remains.
    """
    text = " ".join(query.split())
    truncated = False
    if len(text) > max_chars:
        text = text[:max_chars].rstrip()
        truncated = True
    stripped = False
    if _INJECTION.search(text):
        text = _INJECTION.sub(" ", text)
        text = " ".join(text.split())
        stripped = True
    return GuardResult(query=text, truncated=truncated, injection_stripped=stripped)


def neutralize_evidence(text: str) -> str:
    """Remove instruction-shaped lines from retrieved transcript text before the LLM sees it."""
    if not _INJECTION.search(text):
        return text
    return _INJECTION.sub("[filtered]", text)
