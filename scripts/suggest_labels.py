"""Propose draft labels from distinctive phrases in the indexed transcript.

Drafts are not official. A person must listen and set verified_by_human.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dataset.scripts.catalog import INTERVIEWS
from app.db.connection import get_connection

DRAFT_PATH = ROOT / "dataset" / "golden" / "queries.draft.json"


def main() -> int:
    drafts = []
    with get_connection() as connection:
        for interview in INTERVIEWS:
            filename = f"{interview['slug']}.wav"
            for anchor in interview["anchors"]:
                rows = connection.execute(
                    """
                    SELECT c.speaker, c.start_ts, c.end_ts, a.filename
                    FROM chunks c
                    JOIN audio_files a ON a.id = c.file_id
                    WHERE a.filename = %s
                      AND a.status = 'ready'
                      AND c.content_redacted ILIKE %s
                    ORDER BY c.start_ts
                    """,
                    (filename, f"%{anchor['phrase']}%"),
                ).fetchall()
                relevant = [
                    {
                        "file": row[3],
                        "speaker": row[0],
                        "start_ts": float(row[1]),
                        "end_ts": float(row[2]),
                    }
                    for row in rows
                ]
                drafts.append(
                    {
                        "query": anchor["query"],
                        "category": anchor["category"],
                        "anchor_phrase": anchor["phrase"],
                        "relevant": relevant,
                        "needs_human_review": True,
                    }
                )
        connection.commit()
    payload = {
        "verified_by_human": False,
        "note": "Confirm each relevant span by listening. Then copy approved queries into queries.json.",
        "queries": drafts,
    }
    DRAFT_PATH.parent.mkdir(parents=True, exist_ok=True)
    DRAFT_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    missing = sum(1 for item in drafts if not item["relevant"])
    print(f"wrote {DRAFT_PATH} queries={len(drafts)} missing_anchors={missing}")
    return 0 if missing == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
