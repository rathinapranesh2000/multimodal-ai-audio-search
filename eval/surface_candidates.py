"""Write a review sheet of hybrid+rerank hits. Does not assign labels."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from eval.run_eval import retrieve_for_eval

QUERIES_PATH = Path(__file__).resolve().parent / "golden_queries.json"
REVIEW_PATH = Path(__file__).resolve().parent / "candidates_review.md"
SNIPPET_CHARS = 240


def load_queries(path: Path = QUERIES_PATH) -> list[dict]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError("golden_queries.json must be a list")
    return payload


def _snippet(text: str) -> str:
    collapsed = " ".join(text.split())
    if len(collapsed) <= SNIPPET_CHARS:
        return collapsed.replace("|", "/")
    return collapsed[: SNIPPET_CHARS - 1].rstrip().replace("|", "/") + "…"


def _score(chunk) -> str:
    if chunk.rerank_score is not None:
        return f"{chunk.rerank_score:.3f}"
    if chunk.rrf_score is not None:
        return f"rrf {chunk.rrf_score:.4f}"
    return ""


def _section(entry: dict, hits: list) -> str:
    file_hint = entry.get("file_hint")
    lines = [
        f"## {entry['id']}. {entry['query']}",
        "",
        f"- type: {entry.get('query_type')}",
        f"- file_hint: {file_hint if file_hint else 'null'}",
        "",
        "| rank | file | speaker | start_ts | end_ts | score | snippet |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    if not hits:
        lines.append("| | | | | | | no results |")
        lines.append("")
        return "\n".join(lines)
    for rank, chunk in enumerate(hits, start=1):
        lines.append(
            "| {rank} | {file} | {speaker} | {start:.1f} | {end:.1f} | {score} | {snippet} |".format(
                rank=rank,
                file=chunk.filename,
                speaker=chunk.speaker,
                start=chunk.start_ts,
                end=chunk.end_ts,
                score=_score(chunk),
                snippet=_snippet(chunk.content_redacted),
            )
        )
    lines.append("")
    return "\n".join(lines)


def build_review(queries: list[dict]) -> str:
    parts = [
        "# Candidate review",
        "",
        "Hybrid + rerank top 5 over the full ready corpus.",
        "These rows are search candidates for manual labeling. They are not ground truth.",
        "",
    ]
    for entry in queries:
        hits = retrieve_for_eval(str(entry["query"]), "hybrid")
        parts.append(_section(entry, hits[:5]))
    return "\n".join(parts).rstrip() + "\n"


def main() -> int:
    queries = load_queries()
    review = build_review(queries)
    REVIEW_PATH.write_text(review, encoding="utf-8")
    print(f"wrote {REVIEW_PATH} queries={len(queries)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
