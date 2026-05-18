"""HYDRA API — Database connection helpers.

Safe, lazy helpers for PostgreSQL connections.
No DB connection on import time.
"""

import logging
from urllib.parse import urlparse, urlunparse

import psycopg
from psycopg import Connection

from .config import get_settings

logger = logging.getLogger(__name__)


def normalize_database_url(database_url: str) -> str:
    """Convert a database URL to a canonical psycopg-compatible DSN.

    Converts ``postgresql+psycopg://`` to ``postgresql://`` while
    preserving user, password, host, port, database, and query string.

    Raises ``ValueError`` if *database_url* is empty.
    """
    if not database_url:
        raise ValueError("database_url must not be empty")

    parsed = urlparse(database_url)
    # Strip the driver suffix (e.g. +psycopg) so psycopg can consume it.
    scheme = parsed.scheme.split("+", 1)[0]
    normalized = parsed._replace(scheme=scheme)
    return urlunparse(normalized)


def redact_database_url(database_url: str) -> str:
    """Return a database URL with the password masked.

    Preserves host, port, and database for diagnostic purposes.
    If no password is present the URL is returned unchanged.
    """
    parsed = urlparse(database_url)
    if parsed.password:
        normalized = parsed._replace(
            netloc=parsed.netloc.replace(
                f":{parsed.password}@",
                ":****@",
            )
        )
        return urlunparse(normalized)
    return database_url


def get_connection(database_url: str | None = None) -> Connection:
    """Return a lazy PostgreSQL connection.

    If *database_url* is ``None`` the value is read from
    :func:`.config.get_settings`.  The URL is normalised with
    :func:`normalize_database_url` before passing to ``psycopg``.

    No connection is opened at import time.
    """
    if database_url is None:
        database_url = get_settings().database_url

    normalized = normalize_database_url(database_url)
    return psycopg.connect(normalized)
