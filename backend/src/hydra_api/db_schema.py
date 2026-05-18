"""HYDRA API — Idempotent SQL schema for the MVP.

Centralises all CREATE TABLE statements for the HYDRA database.
No database connection is opened at import time.

Tables are ordered so that referenced tables are created before
any table that references them via foreign keys.
"""

SCHEMA_VERSION = "2026.05.01"

SCHEMA_STATEMENTS: list[str] = [
    # ── 1. Vector extension (pgvector) ──────────────────────────────
    "CREATE EXTENSION IF NOT EXISTS vector",

    # ── 2. documents ────────────────────────────────────────────────
    """CREATE TABLE IF NOT EXISTS documents (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        source TEXT NOT NULL,
        url TEXT,
        published_at DATE,
        domain TEXT NOT NULL,
        raw_path TEXT NOT NULL,
        content_hash TEXT NOT NULL UNIQUE,
        ingestion_source TEXT NOT NULL,
        processing_status TEXT NOT NULL DEFAULT 'pending',
        CHECK (ingestion_source IN ('local_corpus', 'frontend_upload')),
        CHECK (processing_status IN ('pending', 'processing', 'processed', 'failed'))
    )""",

    # ── 3. document_chunks (FK → documents) ─────────────────────────
    """CREATE TABLE IF NOT EXISTS document_chunks (
        id TEXT PRIMARY KEY,
        document_id TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
        chunk_index INTEGER NOT NULL,
        content TEXT NOT NULL,
        metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
        embedding vector(4096),
        UNIQUE (document_id, chunk_index)
    )""",

    # ── 4. extractions (FK → documents) ─────────────────────────────
    """CREATE TABLE IF NOT EXISTS extractions (
        id TEXT PRIMARY KEY,
        document_id TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
        extraction_json JSONB NOT NULL,
        schema_version TEXT NOT NULL,
        created_at TIMESTAMPTZ NOT NULL DEFAULT now()
    )""",

    # ── 5. eval_cases (no FK) ───────────────────────────────────────
    """CREATE TABLE IF NOT EXISTS eval_cases (
        id TEXT PRIMARY KEY,
        question TEXT NOT NULL,
        expected_documents JSONB NOT NULL DEFAULT '[]'::jsonb,
        expected_topics JSONB NOT NULL DEFAULT '[]'::jsonb,
        expected_answer_traits JSONB NOT NULL DEFAULT '[]'::jsonb,
        tags JSONB NOT NULL DEFAULT '[]'::jsonb
    )""",

    # ── 6. eval_results (FK → eval_cases) ───────────────────────────
    """CREATE TABLE IF NOT EXISTS eval_results (
        id TEXT PRIMARY KEY,
        eval_case_id TEXT NOT NULL REFERENCES eval_cases(id) ON DELETE CASCADE,
        trace_id TEXT,
        metrics_json JSONB NOT NULL,
        passed BOOLEAN NOT NULL DEFAULT false,
        created_at TIMESTAMPTZ NOT NULL DEFAULT now()
    )""",

    # ── 7. graph_projection_events (FK → documents) ─────────────────
    """CREATE TABLE IF NOT EXISTS graph_projection_events (
        id TEXT PRIMARY KEY,
        document_id TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
        projection_json JSONB NOT NULL,
        schema_version TEXT NOT NULL,
        sink_status TEXT NOT NULL DEFAULT 'pending',
        created_at TIMESTAMPTZ NOT NULL DEFAULT now()
    )""",
]
