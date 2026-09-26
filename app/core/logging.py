"""Structured stage logs with a trace id. No log line includes secrets."""

from __future__ import annotations

import contextvars
import logging
import time
from collections.abc import Iterator
from contextlib import contextmanager
from uuid import uuid4

from app.core.config import get_settings

_trace_id: contextvars.ContextVar[str] = contextvars.ContextVar("trace_id", default="-")


def current_trace_id() -> str:
    return _trace_id.get()


def set_trace_id(trace_id: str) -> contextvars.Token[str]:
    return _trace_id.set(trace_id)


def reset_trace_id(token: contextvars.Token[str]) -> None:
    _trace_id.reset(token)


def new_trace_id() -> str:
    return uuid4().hex[:12]


class _TraceFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.trace_id = current_trace_id()
        return True


def configure_logging() -> None:
    """Attach one stdout handler. Safe to call more than once."""
    root = logging.getLogger()
    if getattr(root, "_audiorag_configured", False):
        return
    settings = get_settings()
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s %(levelname)s trace=%(trace_id)s %(name)s %(message)s"
        )
    )
    handler.addFilter(_TraceFilter())
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(settings.log_level.upper())
    root._audiorag_configured = True  # type: ignore[attr-defined]


def get_logger(name: str) -> logging.Logger:
    configure_logging()
    return logging.getLogger(name)


@contextmanager
def trace_stage(logger: logging.Logger, stage: str) -> Iterator[dict[str, float]]:
    """Log start, failure, and elapsed milliseconds for one pipeline stage."""
    started = time.perf_counter()
    logger.info("stage_start stage=%s", stage)
    try:
        yield {"started": started}
    except Exception:
        elapsed_ms = (time.perf_counter() - started) * 1000
        logger.exception("stage_failed stage=%s elapsed_ms=%.1f", stage, elapsed_ms)
        raise
    else:
        elapsed_ms = (time.perf_counter() - started) * 1000
        logger.info("stage_done stage=%s elapsed_ms=%.1f", stage, elapsed_ms)
