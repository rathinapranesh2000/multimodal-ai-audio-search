"""Regex PII redaction. This is a baseline, not a claim of complete PII removal."""

from __future__ import annotations

import re

_EMAIL = re.compile(r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b")
_SSN = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
_PHONE = re.compile(
    r"(?:\+?\d{1,3}[\s.-]?)?(?:\(\d{3}\)|\d{3})[\s.-]\d{3}[\s.-]\d{4}\b"
)
_CARD = re.compile(r"\b(?:\d[ -]*?){13,19}\b")
_ADDRESS = re.compile(
    r"\b\d{1,5}\s+(?:[A-Z][a-z]+\s+){1,4}"
    r"(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr)\b\.?",
)
_INTRODUCED_NAME = re.compile(
    r"\b(?:my name is|i am|this is|i'm)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)",
    re.IGNORECASE,
)


def redact_pii(text: str, allowed_names: set[str] | None = None) -> str:
    """Replace common PII patterns. Known speaker names in allowed_names are kept.

    Names are only redacted when someone introduces them ("my name is ...").
    Arbitrary names in running speech are not detected. That limitation is intentional
    for this regex baseline.
    """
    allowed = {name.casefold() for name in (allowed_names or set())}

    def _name(match: re.Match[str]) -> str:
        spoken = match.group(1)
        if spoken.casefold() in allowed:
            return match.group(0)
        prefix = match.group(0)[: match.start(1) - match.start(0)]
        return f"{prefix}[REDACTED_NAME]"

    redacted = _INTRODUCED_NAME.sub(_name, text)
    redacted = _EMAIL.sub("[REDACTED_EMAIL]", redacted)
    redacted = _SSN.sub("[REDACTED_SSN]", redacted)
    redacted = _PHONE.sub("[REDACTED_PHONE]", redacted)
    redacted = _CARD.sub("[REDACTED_NUMBER]", redacted)
    redacted = _ADDRESS.sub("[REDACTED_ADDRESS]", redacted)
    return redacted
