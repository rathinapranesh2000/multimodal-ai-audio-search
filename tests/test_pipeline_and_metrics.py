"""Alignment, redaction, path safety, and metric tests."""

from pathlib import Path

from app.pipeline.align import SpeakerSpan, Word, build_chunks
from app.pipeline.audio import AudioValidationError, assert_safe_file_id, validate_upload
from app.pipeline.redact import redact_pii
from eval.metrics import evaluate_rankings, hard_negative_passed, is_hard_negative_query, score_query


def test_unpunctuated_turn_is_split_by_time():
    words = [
        Word(index * 0.4, index * 0.4 + 0.3, f"word{index}")
        for index in range(200)
    ]
    spans = [SpeakerSpan("SPEAKER_00", 0.0, 80.0)]
    chunks = build_chunks(words, spans)
    assert len(chunks) > 1
    assert chunks[0].end - chunks[0].start <= 50
    assert chunks[-1].end > 70


def test_words_follow_the_overlapping_speaker():
    words = [
        Word(0.0, 0.4, "We"),
        Word(0.4, 0.8, "chose"),
        Word(0.8, 1.2, "PostgreSQL."),
        Word(1.5, 1.9, "The"),
        Word(1.9, 2.4, "price"),
        Word(2.4, 2.8, "changed."),
    ]
    spans = [
        SpeakerSpan("SPEAKER_00", 0.0, 1.3),
        SpeakerSpan("SPEAKER_01", 1.4, 3.0),
    ]
    chunks = build_chunks(words, spans)
    assert [chunk.speaker for chunk in chunks] == ["SPEAKER_00", "SPEAKER_01"]
    assert "PostgreSQL" in chunks[0].text
    assert "price" in chunks[1].text


def test_same_speaker_gap_is_merged():
    words = [
        Word(0.0, 0.5, "First sentence."),
        Word(0.8, 1.2, "Second sentence."),
    ]
    spans = [SpeakerSpan("SPEAKER_00", 0.0, 2.0)]
    chunks = build_chunks(words, spans)
    assert len(chunks) == 1
    assert "First" in chunks[0].text and "Second" in chunks[0].text


def test_redaction_covers_contact_details_and_keeps_allowed_names():
    raw = (
        "Email ada@example.com or call 415-555-0199. "
        "SSN 123-45-6789. Card 4111 1111 1111 1111. "
        "Office 10 Market Street. My name is Jordan Lee. My name is Alex Kim."
    )
    cleaned = redact_pii(raw, {"Alex Kim"})
    assert "ada@example.com" not in cleaned
    assert "415-555-0199" not in cleaned
    assert "123-45-6789" not in cleaned
    assert "4111" not in cleaned
    assert "Market Street" not in cleaned
    assert "[REDACTED_NAME]" in cleaned
    assert "Alex Kim" in cleaned


def _raises(exc_type, fn):
    try:
        fn()
    except exc_type:
        return
    raise AssertionError(f"expected {exc_type.__name__}")


def test_path_and_upload_guards():
    _raises(AudioValidationError, lambda: assert_safe_file_id("../etc/passwd"))
    _raises(AudioValidationError, lambda: assert_safe_file_id("not-a-uuid"))
    _raises(AudioValidationError, lambda: validate_upload("notes.exe", 12))
    _raises(AudioValidationError, lambda: validate_upload("empty.wav", 0))
    assert validate_upload("interview.wav", 32) == "interview.wav"
    assert validate_upload("../secret/interview.mp3", 32) == "interview.mp3"


def test_schema_indexes_redacted_text_only():
    schema = (Path(__file__).resolve().parents[1] / "app" / "db" / "schema.sql").read_text(encoding="utf-8")
    assert "to_tsvector('english', content_redacted)" in schema
    assert "to_tsvector('english', content)" not in schema
    assert "CREATE TABLE IF NOT EXISTS chunks" in schema
    assert "document_chunks" not in schema


def test_failure_log_keeps_only_top5_misses():
    from tests.eval_recall import failure_log

    class Chunk:
        def __init__(self, filename, speaker, start, end):
            self.filename = filename
            self.speaker = speaker
            self.start_ts = start
            self.end_ts = end
            self.lexical_rank = 1
            self.semantic_rank = 1
            self.rrf_score = 0.02
            self.rerank_score = 0.4
            self.content_redacted = "sample"

    hit = Chunk("harbor.wav", "SPEAKER_01", 10.0, 20.0)
    miss = Chunk("other.wav", "SPEAKER_00", 0.0, 5.0)
    queries = [
        {
            "query": "kept",
            "query_type": "keyword",
            "relevant": [{"file": "harbor.wav", "speaker": "SPEAKER_01", "start_ts": 12, "end_ts": 18}],
        },
        {
            "query": "missed",
            "query_type": "paraphrase",
            "relevant_chunks": [{"file": "harbor.wav", "speaker": "SPEAKER_01", "start_ts": 40, "end_ts": 50}],
        },
    ]
    rows = failure_log(queries, [[hit], [miss]])
    assert len(rows) == 1
    assert rows[0]["query"] == "missed"
    assert rows[0]["query_type"] == "paraphrase"
    assert rows[0]["returned_top5"][0]["file"] == "other.wav"
    assert rows[0]["labeled"][0]["start_ts"] == 40


def test_relevant_chunks_key_scores_power_plant_span():
    hit = {
        "file": "Behavioral_mock_Interview.wav",
        "speaker": "SPEAKER_00",
        "start_ts": 55.58,
        "end_ts": 94.9,
    }
    query = {
        "query": "What did they discuss about the electrical power plan?",
        "relevant_chunks": [
            {
                "file": "Behavioral_mock_Interview.wav",
                "speaker": "SPEAKER_00",
                "start_ts": 55.58,
                "end_ts": 94.9,
            }
        ],
    }
    summary = evaluate_rankings([[hit]], [query])
    assert summary["recall_at_1"] == 1.0
    assert summary["recall_at_5"] == 1.0
    assert summary["reciprocal_rank"] == 1.0


def test_hard_negative_uses_rerank_threshold_not_recall():
    query = {"query_type": "hard_negative", "hard_negative_style": True, "relevant_chunks": []}
    assert is_hard_negative_query(query) is True
    labeled = {"query_type": "keyword", "relevant_chunks": [{"file": "a.wav", "speaker": "SPEAKER_00", "start_ts": 0, "end_ts": 1}]}
    assert is_hard_negative_query(labeled) is False
    confident = [{"file": "a.wav", "speaker": "SPEAKER_00", "start_ts": 0, "end_ts": 1, "rerank_score": 0.4}]
    withheld = [{"file": "a.wav", "speaker": "SPEAKER_00", "start_ts": 0, "end_ts": 1, "rerank_score": -6.0}]
    unscored = [{"file": "a.wav", "speaker": "SPEAKER_00", "start_ts": 0, "end_ts": 1, "rerank_score": None}]
    assert hard_negative_passed(confident, threshold=-5.0) is False
    assert hard_negative_passed(withheld, threshold=-5.0) is True
    assert hard_negative_passed(unscored, threshold=-5.0) is True


def test_recall_and_mrr_use_rank_position():
    flags = [False, True, False, False, False]
    scored = score_query(flags)
    assert scored["recall_at_1"] == 0.0
    assert scored["recall_at_3"] == 1.0
    assert scored["recall_at_5"] == 1.0
    assert scored["reciprocal_rank"] == 0.5
    assert scored["precision_at_5"] == 0.2


def test_evaluation_average_and_unverified_gate(tmp_path: Path):
    rankings = [
        [{"file": "a.wav", "file_id": "1", "speaker": "SPEAKER_01", "start_ts": 10, "end_ts": 20}],
        [{"file": "b.wav", "file_id": "2", "speaker": "SPEAKER_00", "start_ts": 0, "end_ts": 5}],
    ]
    queries = [
        {"query": "one", "relevant": [{"file": "a.wav", "speaker": "SPEAKER_01", "start_ts": 12, "end_ts": 18}]},
        {"query": "two", "relevant": [{"file": "missing.wav", "speaker": "SPEAKER_00", "start_ts": 1, "end_ts": 2}]},
    ]
    summary = evaluate_rankings(rankings, queries)
    assert summary["queries"] == 2
    assert summary["recall_at_5"] == 0.5

    golden = tmp_path / "queries.json"
    golden.write_text('{"verified_by_human": false, "queries": []}', encoding="utf-8")
    from eval.run_eval import load_golden

    payload = load_golden(golden)
    assert payload["verified_by_human"] is False
