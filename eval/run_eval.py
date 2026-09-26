"""Run the labeled evaluation. Refuses to print official scores for unverified labels."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from eval.metrics import evaluate_rankings

GOLDEN_PATH = ROOT / "dataset" / "golden" / "queries.json"
MODES = ("lexical", "semantic", "hybrid_rrf", "hybrid")


def load_golden(path: Path = GOLDEN_PATH) -> dict:
    if not path.is_file():
        raise FileNotFoundError(f"Missing {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Golden file must be an object with verified_by_human and queries")
    return payload


def ranking_to_dicts(chunks: list) -> list[dict]:
    return [
        {
            "file": chunk.filename,
            "file_id": chunk.file_id,
            "speaker": chunk.speaker,
            "start_ts": chunk.start_ts,
            "end_ts": chunk.end_ts,
        }
        for chunk in chunks
    ]


def retrieve_for_eval(query: str, mode: str) -> list:
    """Same retrievers as the API. hybrid reranks. hybrid_rrf stops after fusion."""
    from app.core.config import get_settings
    from app.retrieval.rerank import rerank
    from app.retrieval.search import retrieve
    from app.retrieval.speakers import parse_speaker_constraint

    speaker, cleaned = parse_speaker_constraint(query)
    text = cleaned or query
    retrieval_mode = "lexical" if mode == "lexical" else "semantic" if mode == "semantic" else "hybrid_rrf"
    chunks, _fallback = retrieve(text, speaker=speaker, mode=retrieval_mode)
    if mode == "hybrid":
        chunks, _rerank_fallback = rerank(text, chunks, limit=get_settings().rerank_limit)
    return chunks


def main() -> int:
    try:
        payload = load_golden()
    except (FileNotFoundError, ValueError) as exc:
        print(exc)
        return 1
    if not payload.get("verified_by_human"):
        print(
            "dataset/golden/queries.json is not verified_by_human. "
            "Listen to the recordings, confirm dataset/golden/queries.draft.json, "
            "then set verified_by_human to true. No scores were computed."
        )
        return 2
    queries = payload.get("queries") or []
    if not queries:
        print("The golden file has no queries.")
        return 1

    report = {"verified_by_human": True, "modes": {}}
    for mode in MODES:
        rankings = [ranking_to_dicts(retrieve_for_eval(item["query"], mode)) for item in queries]
        report["modes"][mode] = evaluate_rankings(rankings, queries)
        summary = report["modes"][mode]
        print(
            f"{mode}: "
            f"Recall@5={summary.get('recall_at_5', 0):.3f} "
            f"Precision@5={summary.get('precision_at_5', 0):.3f} "
            f"MRR={summary.get('reciprocal_rank', 0):.3f}"
        )
    destination = ROOT / "artifacts"
    destination.mkdir(exist_ok=True)
    (destination / "eval_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"wrote {destination / 'eval_report.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
