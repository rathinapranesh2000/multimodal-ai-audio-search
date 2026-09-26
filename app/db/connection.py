"""Short-lived PostgreSQL connections, including Supabase poolers."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager

import psycopg
from psycopg.conninfo import conninfo_to_dict, make_conninfo

from app.core.config import get_settings

# Supavisor transaction mode rejects named prepared statements.
_PREPARE_THRESHOLD = None


def build_conninfo(database_url: str) -> str:
    """Return a libpq connection string.

    Existing sslmode, sslnegotiation, and connect_timeout values are kept.
    The connection string is never logged.
    """
    parameters = conninfo_to_dict(database_url)
    parameters.setdefault("sslmode", "require")
    # libpq 18 prefers direct TLS. Supabase closes that handshake during startup.
    parameters.setdefault("sslnegotiation", "postgres")
    parameters.setdefault("connect_timeout", "15")
    return make_conninfo(**parameters)


@contextmanager
def get_connection() -> Iterator[psycopg.Connection]:
    """Open one connection and close it when the caller finishes."""
    database_url = get_settings().database_url.strip()
    if not database_url:
        raise RuntimeError("DATABASE_URL is not configured")
    connection = psycopg.connect(
        build_conninfo(database_url),
        prepare_threshold=_PREPARE_THRESHOLD,
    )
    try:
        connection.execute("SET search_path TO audiorag, public")
        yield connection
    finally:
        connection.close()
