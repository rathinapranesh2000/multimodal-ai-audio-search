"""Environment-backed settings. Secrets stay in the environment, never in code."""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """Runtime configuration loaded from the process environment and a local .env file."""

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "AudioRAG"
    app_env: str = "development"
    debug: bool = False
    log_level: str = "INFO"

    database_url: str = ""
    google_api_key: str = ""
    groq_api_key: str = ""
    hf_token: str = ""

    gemini_model: str = "gemini-3.8-flash"
    groq_model: str = "llama-3.3-70b-versatile"
    whisper_model: str = "small"
    # Fixed language skips Whisper's language-detection pass.
    whisper_language: str = "en"
    # Fixed speaker count skips pyannote's speaker-count search.
    diarization_num_speakers: int = 2
    embedding_model: str = "BAAI/bge-small-en-v1.5"
    embedding_dim: int = 384
    reranker_model: str = "BAAI/bge-reranker-base"
    diarization_model: str = "pyannote/speaker-diarization-community-1"

    audio_root: Path = PROJECT_ROOT / "uploads"
    max_upload_bytes: int = 80 * 1024 * 1024
    min_duration_seconds: float = 5.0
    max_duration_seconds: float = 30 * 60

    max_query_chars: int = 500
    rrf_k: int = 60
    lexical_limit: int = 50
    semantic_limit: int = 50
    rrf_limit: int = 20
    rerank_limit: int = 5
    # Left at -5.0 so generation is not withheld on this reranker.
    # CrossEncoder.predict applies a sigmoid, so rerank_score is in (0, 1).
    # Those scores only rank candidates inside one query. They are not an
    # absolute confidence that can be compared across queries. Query 1's
    # genuine top score (0.000443) sits between hard-negative maxima
    # (0.0000652 and 0.000774), so no single cutoff can separate "nothing
    # relevant exists" from "a relevant chunk scored low." A later guard
    # would need an LLM check of the top hit, or a within-query gap such as
    # top-1 versus top-2, not a lower absolute cutoff.
    relevance_min_logit: float = -5.0
    # At golden-dataset scale, exact cosine is more reliable than ANN.
    exact_scan_max_rows: int = 20000

    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    """Return the process-wide settings object."""
    return Settings()
