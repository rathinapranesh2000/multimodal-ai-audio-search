"""Text helpers shared by indexing and lexical fallback. No database imports."""

from __future__ import annotations

import re

QUERY_PREFIX = "Represent this sentence for searching relevant passages: "

_TOKEN = re.compile(r"[a-z0-9]+")
_STOP = frozenset(
    {
        "the", "and", "for", "with", "that", "this", "from", "what", "when", "where",
        "who", "why", "how", "did", "does", "was", "were", "are", "about", "they",
        "them", "their", "have", "has", "had", "say", "said", "tell", "told",
        "into", "your", "you", "our", "not", "but", "can", "could", "would",
        "should", "there", "their", "which", "while", "during", "after", "before",
    }
)


def document_text(speaker: str, content_redacted: str) -> str:
    """Text that is embedded. Speaker is included so similar lines stay separable."""
    return f"{speaker}: {content_redacted}".strip()


def query_text(query: str) -> str:
    """BGE query prefix. Documents must not use this prefix."""
    return f"{QUERY_PREFIX}{query}".strip()


def content_tokens(query: str) -> list[str]:
    """Significant lexical tokens, in order, without stopwords."""
    seen: set[str] = set()
    tokens: list[str] = []
    for token in _TOKEN.findall(query.lower()):
        if len(token) < 3 or token in _STOP or token in seen:
            continue
        seen.add(token)
        tokens.append(token)
    return tokens[:8]


def or_websearch(tokens: list[str]) -> str:
    return " OR ".join(tokens)
