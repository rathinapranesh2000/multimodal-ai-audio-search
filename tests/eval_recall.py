"""Score eval/golden_queries.json in four retrieval modes.

Normal queries report Recall@k, Precision@5, and MRR. Hard-negative queries
are pass/fail on the rerank threshold and are not averaged into recall.
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from eval.metrics import evaluate_rankings, hard_negative_passed, hit_is_relevant, is_hard_negative_query
from eval.run_eval import retrieve_for_eval

GOLDEN_PATH = ROOT / "eval" / "golden_queries.json"
RESULTS_PATH = ROOT / "eval" / "results.md"
MODES = ("lexical", "semantic", "hybrid_rrf", "hybrid")
RELEVANCE_MIN_LOGIT = -5.0


def expected_spans(query: dict) -> list[dict]:
    if "relevant_chunks" in query:
        return list(query.get("relevant_chunks") or [])
    return list(query.get("relevant") or [])


def load_queries(path: Path = GOLDEN_PATH) -> list[dict]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError("eval/golden_queries.json must be a list")
    return payload


def hit_dict(chunk) -> dict:
    return {
        "file": chunk.filename,
        "file_id": chunk.file_id,
        "speaker": chunk.speaker,
        "start_ts": chunk.start_ts,
        "end_ts": chunk.end_ts,
        "rerank_score": chunk.rerank_score,
    }


def hit_row(chunk) -> dict:
    return {
        "file": chunk.filename,
        "speaker": chunk.speaker,
        "start_ts": chunk.start_ts,
        "end_ts": chunk.end_ts,
        "lexical_rank": chunk.lexical_rank,
        "semantic_rank": chunk.semantic_rank,
        "rrf_score": chunk.rrf_score,
        "rerank_score": chunk.rerank_score,
        "snippet": chunk.content_redacted,
    }


def failure_log(queries: list[dict], rankings: list[list]) -> list[dict]:
    """Keep queries whose hybrid+rerank top 5 miss every labeled span."""
    rows = []
    for query, ranking in zip(queries, rankings, strict=True):
        if is_hard_negative_query(query):
            continue
        expected = expected_spans(query)
        top5 = ranking[:5]
        if any(hit_is_relevant(hit_row(chunk), expected) for chunk in top5):
            continue
        rows.append(
            {
                "query": query.get("query", ""),
                "query_type": query.get("query_type", ""),
                "returned_top5": [hit_row(chunk) for chunk in top5],
                "labeled": expected,
            }
        )
    return rows


def format_log(rows: list[dict]) -> str:
    if not rows:
        return "Failure log: no misses. Either every labeled span is in the top 5, or there are no labeled queries."
    blocks = []
    for index, row in enumerate(rows, start=1):
        lines = [
            f"Miss {index}",
            f"query: {row['query']}",
            f"query_type: {row['query_type'] or '(none)'}",
            "returned top 5:",
        ]
        if not row["returned_top5"]:
            lines.append("  (none)")
        for rank, hit in enumerate(row["returned_top5"], start=1):
            lines.append(
                "  "
                f"{rank}. {hit['file']} {hit['speaker']} "
                f"{hit['start_ts']:.2f}-{hit['end_ts']:.2f} "
                f"lexical={hit['lexical_rank']} semantic={hit['semantic_rank']} "
                f"rrf={hit['rrf_score']} rerank={hit['rerank_score']}"
            )
            lines.append(f"     {hit['snippet']}")
        lines.append("labeled:")
        if not row["labeled"]:
            lines.append("  (none)")
        for span in row["labeled"]:
            lines.append(
                "  "
                f"{span.get('file')} {span.get('speaker')} "
                f"{span.get('start_ts')}-{span.get('end_ts')}"
            )
        blocks.append("\n".join(lines))
    return "\n\n".join(blocks)


def _metric_row(mode: str, summary: dict) -> str:
    return (
        f"| {mode} | {summary.get('recall_at_1', 0):.3f} | {summary.get('recall_at_3', 0):.3f} | "
        f"{summary.get('recall_at_5', 0):.3f} | {summary.get('precision_at_5', 0):.3f} | "
        f"{summary.get('reciprocal_rank', 0):.3f} | {int(summary.get('queries', 0))} |"
    )


def _by_type(queries: list[dict], rankings: list[list[dict]]) -> dict[str, dict]:
    grouped_q: dict[str, list[dict]] = defaultdict(list)
    grouped_r: dict[str, list[list[dict]]] = defaultdict(list)
    for query, ranking in zip(queries, rankings, strict=True):
        grouped_q[str(query.get("query_type") or "(none)")].append(query)
        grouped_r[str(query.get("query_type") or "(none)")].append(ranking)
    return {
        name: evaluate_rankings(grouped_r[name], grouped_q[name])
        for name in sorted(grouped_q)
    }


def render_results(queries: list[dict], by_mode: dict[str, list[list[dict]]]) -> str:
    normal = [query for query in queries if not is_hard_negative_query(query)]
    hard = [query for query in queries if is_hard_negative_query(query)]
    lines = [
        "# Retrieval results",
        "",
        "Normal queries are the ones with labeled spans. Hard-negative queries are excluded from Recall@k, Precision@5, and MRR.",
        "",
        f"A hard-negative query passes when no top-5 chunk has `rerank_score >= {RELEVANCE_MIN_LOGIT}`. A missing rerank score does not count as a confident hit.",
        "",
        f"Normal queries: {len(normal)}. Hard-negative queries: {len(hard)}.",
        "",
        "## Normal queries",
        "",
        "| mode | Recall@1 | Recall@3 | Recall@5 | Precision@5 | MRR | queries |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    type_sections = ["", "## By query_type", ""]
    for mode in MODES:
        paired = list(zip(queries, by_mode[mode], strict=True))
        normal_rankings = [ranking for query, ranking in paired if not is_hard_negative_query(query)]
        summary = evaluate_rankings(normal_rankings, normal)
        lines.append(_metric_row(mode, summary))
        type_sections.append(f"### {mode}")
        type_sections.append("")
        type_sections.append("| query_type | Recall@1 | Recall@3 | Recall@5 | Precision@5 | MRR | queries |")
        type_sections.append("| --- | --- | --- | --- | --- | --- | --- |")
        for name, type_summary in _by_type(normal, normal_rankings).items():
            type_sections.append(_metric_row(name, type_summary))
        type_sections.append("")
    lines.extend(type_sections)
    lines.extend(
        [
            "## Hard negatives",
            "",
            "| id | query_type | lexical | semantic | hybrid_rrf | hybrid |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )
    for query in hard:
        cells = []
        for mode in MODES:
            ranking = by_mode[mode][queries.index(query)]
            passed = hard_negative_passed(ranking, threshold=RELEVANCE_MIN_LOGIT)
            cells.append("PASS" if passed else "FAIL")
        lines.append(
            f"| {query.get('id')} | {query.get('query_type')} | {cells[0]} | {cells[1]} | {cells[2]} | {cells[3]} |"
        )
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    queries = load_queries()
    by_mode: dict[str, list[list[dict]]] = {}
    for mode in MODES:
        by_mode[mode] = [list(map(hit_dict, retrieve_for_eval(item["query"], mode))) for item in queries]
    report = render_results(queries, by_mode)
    RESULTS_PATH.write_text(report, encoding="utf-8")
    print(report)
    print(f"wrote {RESULTS_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
