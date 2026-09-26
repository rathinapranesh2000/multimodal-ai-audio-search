"""Align Whisper words with pyannote turns, then pack speaker-aware chunks."""

from __future__ import annotations

from dataclasses import dataclass

TARGET_SECONDS = 32.0
MAX_SECONDS = 45.0
MIN_WORDS = 12
SAME_SPEAKER_GAP = 0.75


@dataclass(frozen=True)
class Word:
    start: float
    end: float
    text: str


@dataclass(frozen=True)
class SpeakerSpan:
    speaker: str
    start: float
    end: float


@dataclass(frozen=True)
class ChunkDraft:
    speaker: str
    start: float
    end: float
    text: str


def assign_speakers(words: list[Word], spans: list[SpeakerSpan]) -> list[ChunkDraft]:
    """Give each word to the speaker span with the greatest time overlap.

    Words that fall in a gap go to the nearest span within half a second.
    """
    if not words:
        return []
    ordered = sorted(spans, key=lambda span: span.start)
    grouped: list[list[Word]] = []
    speakers: list[str] = []
    for word in words:
        speaker = _speaker_for_word(word, ordered)
        if speaker is None:
            continue
        if speakers and speakers[-1] == speaker:
            grouped[-1].append(word)
        else:
            speakers.append(speaker)
            grouped.append([word])
    drafts = [
        ChunkDraft(
            speaker=speaker,
            start=turn[0].start,
            end=turn[-1].end,
            text=" ".join(word.text for word in turn).strip(),
        )
        for speaker, turn in zip(speakers, grouped, strict=True)
        if turn
    ]
    return [draft for draft in drafts if draft.text]


def _speaker_for_word(word: Word, spans: list[SpeakerSpan]) -> str | None:
    if not spans:
        return "SPEAKER_00"
    best_speaker = None
    best_overlap = 0.0
    midpoint = (word.start + word.end) / 2.0
    nearest = None
    nearest_gap = 10**9
    for span in spans:
        overlap = min(word.end, span.end) - max(word.start, span.start)
        if overlap > best_overlap:
            best_overlap = overlap
            best_speaker = span.speaker
        gap = 0.0 if span.start <= midpoint <= span.end else min(
            abs(midpoint - span.start), abs(midpoint - span.end)
        )
        if gap < nearest_gap:
            nearest_gap = gap
            nearest = span.speaker
    if best_speaker is not None and best_overlap > 0:
        return best_speaker
    if nearest is not None and nearest_gap <= 0.5:
        return nearest
    return None


def merge_same_speaker(drafts: list[ChunkDraft], gap_seconds: float = SAME_SPEAKER_GAP) -> list[ChunkDraft]:
    """Join adjacent turns from the same speaker when the pause is short."""
    merged: list[ChunkDraft] = []
    for draft in drafts:
        if not merged:
            merged.append(draft)
            continue
        previous = merged[-1]
        if previous.speaker == draft.speaker and draft.start - previous.end <= gap_seconds:
            merged[-1] = ChunkDraft(
                speaker=previous.speaker,
                start=previous.start,
                end=max(previous.end, draft.end),
                text=f"{previous.text} {draft.text}".strip(),
            )
        else:
            merged.append(draft)
    return merged


def pack_chunks(drafts: list[ChunkDraft]) -> list[ChunkDraft]:
    """Split long turns on sentence boundaries and keep short fragments with a neighbor."""
    packed: list[ChunkDraft] = []
    for draft in drafts:
        packed.extend(_split_long(draft))
    return _absorb_short(packed)


def _split_long(draft: ChunkDraft) -> list[ChunkDraft]:
    """Break a long turn into ~30 second pieces.

    Whisper often returns no sentence punctuation, so a punctuation-only split
    leaves an entire recording as one chunk. Word count is the fallback cut.
    """
    if draft.end - draft.start <= MAX_SECONDS:
        return [draft]
    words = draft.text.split()
    if len(words) < 2:
        return [draft]
    duration = max(draft.end - draft.start, 0.1)
    seconds_per_word = duration / len(words)
    target_words = max(12, int(TARGET_SECONDS / seconds_per_word))
    pieces: list[ChunkDraft] = []
    cursor = draft.start
    start_index = 0
    while start_index < len(words):
        end_index = min(len(words), start_index + target_words)
        if end_index < len(words):
            end_index = _break_near(words, end_index)
        chunk_words = words[start_index:end_index]
        if end_index >= len(words):
            end = draft.end
        else:
            end = min(draft.end, cursor + len(chunk_words) * seconds_per_word)
        text = " ".join(chunk_words).strip()
        if text:
            pieces.append(ChunkDraft(draft.speaker, cursor, end, text))
        cursor = end
        start_index = end_index
    return pieces or [draft]


def _break_near(words: list[str], end_index: int) -> int:
    """Prefer a nearby punctuation mark over a hard word-count cut."""
    lo = max(1, end_index - 8)
    hi = min(len(words), end_index + 8)
    for index in range(end_index, hi):
        if words[index][-1:] in ".?!":
            return index + 1
    for index in range(end_index - 1, lo - 1, -1):
        if words[index][-1:] in ".?!":
            return index + 1
    return end_index


def _absorb_short(drafts: list[ChunkDraft]) -> list[ChunkDraft]:
    kept: list[ChunkDraft] = []
    for draft in drafts:
        if kept and len(draft.text.split()) < MIN_WORDS and kept[-1].speaker == draft.speaker:
            previous = kept[-1]
            kept[-1] = ChunkDraft(
                previous.speaker,
                previous.start,
                draft.end,
                f"{previous.text} {draft.text}".strip(),
            )
        else:
            kept.append(draft)
    return [draft for draft in kept if draft.text.strip()]


def build_chunks(words: list[Word], spans: list[SpeakerSpan]) -> list[ChunkDraft]:
    """Full alignment path used by ingestion."""
    return pack_chunks(merge_same_speaker(assign_speakers(words, spans)))
