"""Pure retrieval metrics. These functions do not read a database or invent labels."""

from __future__ import annotations

from collections.abc import Callable, Sequence

KS = (1, 3, 5)


def overlaps(hit_start: float, hit_end: float, expected_start: float, expected_end: float) -> bool:
    return hit_start < expected_end and hit_end > expected_start


def hit_is_relevant(hit: dict, expected_items: Sequence[dict]) -> bool:
    """A hit is relevant when file, speaker, and timestamp overlap a labeled span."""
    for expected in expected_items:
        file_name = expected.get("file")
        file_id = expected.get("file_id")
        file_ok = True
        if file_name or file_id:
            file_ok = hit.get("file") == file_name or hit.get("file_id") == file_id
        speaker = expected.get("speaker")
        speaker_ok = True if not speaker else hit.get("speaker") == speaker
        if expected.get("start_ts") is None or expected.get("end_ts") is None:
            time_ok = True
        else:
            time_ok = overlaps(
                float(hit["start_ts"]),
                float(hit["end_ts"]),
                float(expected["start_ts"]),
                float(expected["end_ts"]),
            )
        if file_ok and speaker_ok and time_ok:
            return True
    return False


def score_query(flags: Sequence[bool]) -> dict[str, float]:
    """Score one ranked list. Precision@5 uses 5 slots, so a short list is not perfect."""
    first = next((index for index, flag in enumerate(flags, start=1) if flag), 0)
    top5 = list(flags[:5])
    relevant_in_top5 = sum(1 for flag in top5 if flag)
    return {
        "reciprocal_rank": 0.0 if first == 0 else 1.0 / first,
        "precision_at_5": relevant_in_top5 / 5,
        **{f"recall_at_{k}": 1.0 if any(flags[:k]) else 0.0 for k in KS},
    }


def aggregate(query_scores: Sequence[dict[str, float]]) -> dict[str, float]:
    total = len(query_scores)
    if total == 0:
        return {}
    keys = query_scores[0].keys()
    return {key: sum(item[key] for item in query_scores) / total for key in keys}


def label_spans(query: dict) -> list:
    """Labels live on relevant_chunks. Older callers used relevant."""
    if "relevant_chunks" in query:
        return list(query.get("relevant_chunks") or [])
    return list(query.get("relevant") or [])


def is_hard_negative_query(query: dict) -> bool:
    """Empty labels that were marked hard-negative are not recall questions."""
    if label_spans(query):
        return False
    return query.get("query_type") == "hard_negative" or query.get("hard_negative_style") is True


def hard_negative_passed(hits: Sequence[dict], *, threshold: float = -5.0) -> bool:
    """Pass when no top-5 chunk has a rerank score at or above the threshold.

    A missing rerank_score does not count as a confident hit. The comparison
    matches answer generation: a score below relevance_min_logit is withheld.
    """
    for hit in list(hits)[:5]:
        score = hit.get("rerank_score")
        if score is None:
            continue
        if float(score) >= threshold:
            return False
    return True


def evaluate_rankings(
    rankings: Sequence[Sequence[dict]],
    queries: Sequence[dict],
    *,
    match: Callable[[dict, Sequence[dict]], bool] = hit_is_relevant,
) -> dict[str, float]:
    """Average Recall@k, Precision@5, and MRR across labeled queries."""
    scores = []
    for ranking, query in zip(rankings, queries, strict=True):
        flags = [match(hit, label_spans(query)) for hit in ranking]
        scores.append(score_query(flags))
    summary = aggregate(scores)
    summary["queries"] = float(len(queries))
    return summary
