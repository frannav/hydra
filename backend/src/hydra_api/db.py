"""HYDRA API — Database connection helpers.

Safe, lazy helpers for PostgreSQL connections.
No DB connection on import time.
"""

import argparse
import logging
import os
import sys
from urllib.parse import urlparse, urlunparse

import psycopg
from psycopg import Connection

from .config import get_settings
from .db_schema import SCHEMA_STATEMENTS

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


def init_db(database_url: str | None = None) -> None:
    """Execute SCHEMA_STATEMENTS inside a transaction.

    Uses :func:`get_connection` to obtain a lazy PostgreSQL connection.
    All statements are run inside a single transaction so that a failure
    in any statement rolls back the entire schema.

    This function is idempotent — all SQL uses ``CREATE TABLE IF NOT EXISTS``
    and ``CREATE EXTENSION IF NOT EXISTS``, so it can be called repeatedly
    without error.

    No database connection is opened at import time.
    """
    conn = get_connection(database_url)
    try:
        with conn.cursor() as cur:
            for stmt in SCHEMA_STATEMENTS:
                cur.execute(stmt)
        conn.commit()
        logger.info("Schema initialized successfully")
    except Exception:
        conn.rollback()
        logger.exception("Schema initialization failed; transaction rolled back")
        raise
    finally:
        conn.close()


def _main() -> None:
    """CLI entry point for ``python -m hydra_api.db``."""
    parser = argparse.ArgumentParser(
        description="HYDRA database schema initialisation CLI"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--print-schema",
        action="store_true",
        help="Print the SQL schema statements to stdout and exit",
    )
    group.add_argument(
        "--init",
        action="store_true",
        help="Initialise the database schema and exit",
    )

    args = parser.parse_args()

    if args.print_schema:
        print("\n".join(SCHEMA_STATEMENTS))
        return

    if args.init:
        database_url = os.environ.get("DATABASE_URL")
        if not database_url:
            print(
                "Error: DATABASE_URL environment variable is required for --init",
                file=sys.stderr,
            )
            sys.exit(1)
        try:
            init_db(database_url)
        except Exception as exc:
            print(f"Error: {exc}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    _main()
