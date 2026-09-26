"""API checks. Health, search, and the end-to-end ingest test use the configured database."""

import subprocess
import time
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import create_app

client = TestClient(create_app())

_HIT_FIELDS = ("file", "speaker", "start_ts", "end_ts", "snippet")


def test_health_does_not_require_a_database():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.headers["x-trace-id"]


def test_health_db_pgvector_and_schema():
    database = client.get("/health/db")
    assert database.status_code == 200
    assert database.json()["status"] == "ok"
    vectors = client.get("/health/pgvector")
    assert vectors.status_code == 200
    assert vectors.json()["status"] == "ok"
    assert vectors.json()["version"]
    schema = client.get("/health/schema")
    assert schema.status_code == 200
    assert schema.json() == {"status": "ok", "table": "chunks"}


def test_empty_search_is_rejected_before_retrieval():
    response = client.post("/search", json={"query": "   "})
    assert response.status_code == 400


def _assert_hit_shape(hit: dict) -> None:
    for field in _HIT_FIELDS:
        assert field in hit
    assert hit["file"]
    assert hit["speaker"]
    assert hit["end_ts"] > hit["start_ts"]
    assert isinstance(hit["snippet"], str) and hit["snippet"]


def test_search_returns_file_speaker_and_timestamps():
    response = client.post(
        "/search",
        json={"query": "What are the potential dangers or risks of AI?", "mode": "hybrid"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["results"]
    for hit in body["results"]:
        _assert_hit_shape(hit)
    for citation in body["citations"]:
        assert citation["file"] and citation["speaker"]
        assert citation["end_ts"] > citation["start_ts"]


def test_long_query_is_truncated_then_searched():
    response = client.post("/search", json={"query": "pricing " * 80, "mode": "lexical"})
    assert response.status_code == 200
    body = response.json()
    assert body["query_truncated"] is True
    assert len(body["query"]) <= 500


def test_reranker_failure_still_returns_rrf_results(monkeypatch):
    def explode(_query: str, _chunks: list) -> list[float]:
        raise RuntimeError("reranker offline")

    monkeypatch.setattr("app.retrieval.rerank._model_scores", explode)
    response = client.post(
        "/search",
        json={"query": "What are the potential dangers or risks of AI?", "mode": "hybrid"},
    )
    assert response.status_code == 200
    body = response.json()
    assert "rrf" in (body.get("fallback") or "")
    assert body["results"]
    for hit in body["results"]:
        _assert_hit_shape(hit)


def test_bad_upload_never_starts_ingestion():
    response = client.post(
        "/ingest",
        files={"file": ("malware.exe", b"not-audio", "application/octet-stream")},
    )
    assert response.status_code == 400


def test_empty_upload_is_rejected():
    response = client.post("/ingest", files={"file": ("clip.wav", b"", "audio/wav")})
    assert response.status_code == 400


def test_delete_requires_a_uuid():
    response = client.delete("/conversations/not-a-uuid")
    assert response.status_code == 400


def test_audio_path_must_be_a_uuid():
    response = client.get("/audio/not-a-uuid")
    assert response.status_code == 400
    traversal = client.get("/audio/..%2F..%2Fetc%2Fpasswd")
    assert traversal.status_code in {400, 404}
    assert b"root:" not in traversal.content


def test_upload_indexes_and_search_citations_use_real_offsets(tmp_path: Path):
    """Upload a short clip, wait until it is ready, then check search timestamps against that audio."""
    source = Path("dataset/synthetic_sample/harbor-pricing.wav")
    clip = tmp_path / "e2e-clip.wav"
    completed = subprocess.run(
        ["ffmpeg", "-y", "-i", str(source), "-t", "12", "-ac", "1", "-ar", "16000", str(clip)],
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 0 and clip.is_file()
    with clip.open("rb") as handle:
        accepted = client.post("/ingest", files={"file": ("e2e-clip.wav", handle, "audio/wav")})
    assert accepted.status_code == 202
    file_id = accepted.json()["file_id"]
    status: dict = {}
    deadline = time.time() + 600
    try:
        while time.time() < deadline:
            status = client.get(f"/ingest/{file_id}/status").json()
            if status["status"] in {"ready", "failed"}:
                break
            time.sleep(2)
        assert status.get("status") == "ready", status.get("error")
        from app.db.connection import get_connection

        with get_connection() as connection:
            row = connection.execute(
                """
                SELECT content_redacted, start_ts, end_ts
                FROM chunks
                WHERE file_id = %s
                ORDER BY start_ts
                LIMIT 1
                """,
                (file_id,),
            ).fetchone()
            connection.commit()
        assert row is not None and row[0].strip()
        phrase = " ".join(row[0].split()[:8])
        found = client.post("/search", json={"query": phrase, "mode": "lexical"})
        assert found.status_code == 200
        body = found.json()
        hits = [hit for hit in body["results"] if hit["file_id"] == file_id]
        assert hits, body["results"]
        for hit in hits:
            _assert_hit_shape(hit)
            assert hit["start_ts"] < float(row[2])
            assert hit["end_ts"] > float(row[1])
            assert hit["end_ts"] <= float(status["duration_seconds"]) + 1
        audio = client.get(f"/audio/{file_id}")
        assert audio.status_code == 200
        assert audio.headers["content-type"].startswith("audio/")
        assert len(audio.content) > 1000
    finally:
        client.delete(f"/conversations/{file_id}")
