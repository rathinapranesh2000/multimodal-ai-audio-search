"""API models. Search results expose redacted snippets only."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class Citation(BaseModel):
    file_id: str
    file: str
    speaker: str
    start_ts: float
    end_ts: float


class SearchHit(BaseModel):
    file_id: str
    file: str
    speaker: str
    start_ts: float
    end_ts: float
    snippet: str
    cited: bool = False
    why: str = ""
    lexical_rank: int | None = None
    semantic_rank: int | None = None
    rrf_score: float | None = None
    rerank_score: float | None = None


class SearchRequest(BaseModel):
    query: str
    mode: Literal["hybrid", "lexical", "semantic", "hybrid_rrf"] = "hybrid"


class SearchResponse(BaseModel):
    query: str
    answer: str
    citations: list[Citation]
    results: list[SearchHit]
    fallback: str | None = None
    query_truncated: bool = False
    injection_stripped: bool = False
    speaker_filter: str | None = None
    mode: str
    trace_id: str
    elapsed_ms: float


class IngestAccepted(BaseModel):
    file_id: str
    status: str
    stage: str


class IngestStatus(BaseModel):
    file_id: str
    filename: str
    status: str
    stage: str
    progress: dict[str, str] = Field(default_factory=dict)
    timings: dict[str, float] = Field(default_factory=dict)
    error: str | None = None
    duration_seconds: float | None = None
    chunk_count: int = 0


class Conversation(BaseModel):
    file_id: str
    filename: str
    status: str
    stage: str
    duration_seconds: float | None = None
    chunk_count: int = 0
    created_at: str
