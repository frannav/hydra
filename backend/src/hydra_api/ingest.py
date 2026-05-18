"""HYDRA API — Ingestion helpers and service.

Pure functions for document ingestion. No DB, no models, no file I/O on import.
"""

from __future__ import annotations

import argparse
import hashlib
import logging
import re
from pathlib import Path
from typing import Any

from .schemas import DocumentMetadata, DocumentChunk, IngestionRunResult, RawDocument

logger = logging.getLogger(__name__)


def normalize_date(value: str | None) -> str | None:
    """Normalize a date string to YYYY-MM-DD format.

    Accepts None and YYYY-MM-DD. Rejects ambiguous formats with ValueError.
    """
    if value is None:
        return None
    # Only accept YYYY-MM-DD
    if re.match(r'^\d{4}-\d{2}-\d{2}$', value):
        return value
    raise ValueError(f"Ambiguous or unsupported date format: {value!r}. Expected YYYY-MM-DD.")


def normalize_source(value: str) -> str:
    """Normalize a source name.

    Strips whitespace, collapses repeated spaces. Rejects empty strings.
    """
    normalized = re.sub(r'\s+', ' ', value).strip()
    if not normalized:
        raise ValueError("Source name cannot be empty or whitespace-only.")
    return normalized


def compute_content_hash(text: str) -> str:
    """Compute SHA-256 hash of text content.

    Normalizes line endings to \n. Rejects empty or whitespace-only text.
    """
    if not text or not text.strip():
        raise ValueError("Content hash cannot be computed for empty text.")
    normalized = text.replace('\r\n', '\n').replace('\r', '\n')
    return hashlib.sha256(normalized.encode('utf-8')).hexdigest()


def resolve_corpus_path(root: Path, relative_path: str) -> Path:
    """Resolve a corpus file path safely, preventing path traversal.

    Rejects absolute paths and paths that escape the root directory.
    Uses path-aware containment (not string-prefix).
    """
    abs_root = root.resolve()
    # Reject absolute paths
    if relative_path.startswith('/'):
        raise ValueError(f"Absolute paths are not allowed: {relative_path!r}")
    candidate = (abs_root / relative_path).resolve()
    # Use relative_to() for path-aware containment check
    try:
        candidate.relative_to(abs_root)
    except ValueError:
        raise ValueError(f"Path traversal detected: {relative_path!r} escapes root {abs_root}")
    return candidate


def validate_metadata_dict(data: dict[str, Any]) -> DocumentMetadata:
    """Validate and normalize metadata dict into DocumentMetadata.

    Normalizes dates and source. Requires title, source, domain.
    Rejects ingestion_source != local_corpus.
    """
    # Validate required fields
    for field in ('title', 'source', 'domain'):
        if field not in data or not data[field]:
            raise ValueError(f"Required metadata field missing or empty: {field!r}")

    # Validate ingestion_source
    ingestion_source = data.get('ingestion_source', 'local_corpus')
    if ingestion_source != 'local_corpus':
        raise ValueError(f"Local loader only accepts ingestion_source='local_corpus', got: {ingestion_source!r}")

    # Normalize fields
    normalized = dict(data)
    if 'source' in normalized:
        normalized['source'] = normalize_source(normalized['source'])
    if 'published_at' in normalized and normalized['published_at']:
        normalized['published_at'] = normalize_date(normalized['published_at'])
    if 'collected_at' in normalized and normalized['collected_at']:
        normalized['collected_at'] = normalize_date(normalized['collected_at'])

    return DocumentMetadata(**normalized)


def load_metadata_file(path: Path) -> DocumentMetadata:
    """Load and validate a JSON metadata file."""
    text = path.read_text(encoding='utf-8')
    data = __import__('json').loads(text)
    return validate_metadata_dict(data)


def load_raw_text(path: Path) -> str:
    """Load raw text from a .txt or .md file.

    Only supports .txt and .md extensions. UTF-8 encoding.
    """
    if path.suffix not in ('.txt', '.md'):
        raise ValueError(f"Unsupported file extension: {path.suffix!r}. Only .txt and .md are supported.")
    text = path.read_text(encoding='utf-8')
    if not text.strip():
        raise ValueError(f"Raw text file is empty: {path}")
    return text


def load_local_document(raw_path: Path, metadata_path: Path) -> RawDocument:
    """Load a local document combining raw text and validated metadata.

    Uses load_raw_text() for raw text validation. Computes content_hash
    from loaded text when metadata lacks it. Requires document_id in metadata.
    """
    text = load_raw_text(raw_path)

    meta_data = metadata_path.read_text(encoding='utf-8')
    data = __import__('json').loads(meta_data)

    # Require document_id before creating DocumentMetadata
    document_id = data.get('document_id')
    if not document_id:
        raise ValueError("document_id is required in metadata but was missing or empty.")

    metadata = validate_metadata_dict(data)

    # Preserve existing metadata.raw_path when present
    if not metadata.raw_path:
        metadata.raw_path = str(raw_path)

    # Compute content_hash from already-loaded text when metadata lacks it
    if not metadata.content_hash:
        metadata.content_hash = compute_content_hash(text)

    return RawDocument(
        document_id=document_id,
        text=text,
        metadata=metadata,
    )


def load_local_corpus_manifest(path: Path) -> list[RawDocument]:
    """Load a local corpus manifest and return list of RawDocuments.

    Accepts empty documents list and returns [].
    Requires both raw_path and metadata_path in every non-empty entry.
    Uses safe path resolution for all paths.
    """
    text = path.read_text(encoding='utf-8')
    data = __import__('json').loads(text)

    documents = data.get('documents', [])
    if not isinstance(documents, list):
        raise ValueError("Manifest 'documents' field must be a list.")

    if not documents:
        return []

    # Anchor corpus root to the data/ directory
    data_root = Path(path.parent, '..').resolve()
    results: list[RawDocument] = []

    for i, doc_entry in enumerate(documents):
        raw_rel = doc_entry.get('raw_path')
        meta_rel = doc_entry.get('metadata_path')

        # Require both fields, raise ValueError if either missing or empty
        if not raw_rel or not raw_rel.strip():
            raise ValueError(
                f"Manifest entry {i}: 'raw_path' is required and must not be empty."
            )
        if not meta_rel or not meta_rel.strip():
            raise ValueError(
                f"Manifest entry {i}: 'metadata_path' is required and must not be empty."
            )

        safe_raw = resolve_corpus_path(data_root, raw_rel)
        safe_meta = resolve_corpus_path(data_root, meta_rel)
        results.append(load_local_document(safe_raw, safe_meta))

    return results


# ---------------------------------------------------------------------------
# IngestionService (TASK-CORPUS-022, 025)
# ---------------------------------------------------------------------------

class IngestionService:
    """Processes documents into chunks with optional DB persistence."""

    def process_documents(
        self,
        documents: list[RawDocument],
        dry_run: bool = True,
    ) -> IngestionRunResult:
        """Process a list of raw documents into chunks.

        In dry_run mode, only counts documents and chunks.
        In persistence mode, uses get_connection() from hydra_api.db.
        """
        from .chunking import chunk_raw_document

        errors: list[str] = []
        total_chunks = 0

        for doc in documents:
            try:
                chunks = chunk_raw_document(doc)
                total_chunks += len(chunks)
            except Exception as exc:
                # Capture per-document errors without aborting
                errors.append(f"Error processing document {doc.document_id!r}: {exc}")

        if not dry_run:
            # Persist documents and chunks
            try:
                from .db import get_connection
                from .ingest import upsert_document, upsert_chunks

                conn = get_connection()
                try:
                    with conn.cursor() as cur:
                        for doc in documents:
                            upsert_document(cur, doc)
                        for doc in documents:
                            chunks = chunk_raw_document(doc)
                            upsert_chunks(cur, chunks)
                    conn.commit()
                except Exception:
                    conn.rollback()
                    raise
                finally:
                    conn.close()
            except Exception as exc:
                errors.append(f"Database persistence failed: {exc}")

        return IngestionRunResult(
            processed_documents=len(documents),
            created_chunks=total_chunks,
            errors=errors,
            dry_run=dry_run,
        )


# ---------------------------------------------------------------------------
# Persistence helpers (TASK-CORPUS-023, 024)
# ---------------------------------------------------------------------------

def upsert_document(cur, raw_document: RawDocument) -> None:
    """Upsert a document into the documents table.

    Uses SQL parameterized queries. Sets processing_status='pending' on insert.
    On update, does NOT reset an existing non-null processing_status.
    """
    cur.execute(
        """
        INSERT INTO documents (id, title, source, url, published_at, domain, raw_path, content_hash, ingestion_source, processing_status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'pending')
        ON CONFLICT (id) DO UPDATE SET
            title = EXCLUDED.title,
            source = EXCLUDED.source,
            url = EXCLUDED.url,
            published_at = EXCLUDED.published_at,
            domain = EXCLUDED.domain,
            raw_path = EXCLUDED.raw_path,
            content_hash = EXCLUDED.content_hash,
            ingestion_source = EXCLUDED.ingestion_source,
            processing_status = documents.processing_status
        """,
        (
            raw_document.document_id,
            raw_document.metadata.title,
            raw_document.metadata.source,
            raw_document.metadata.url,
            raw_document.metadata.published_at,
            raw_document.metadata.domain,
            raw_document.metadata.raw_path,
            raw_document.metadata.content_hash,
            raw_document.metadata.ingestion_source.value,
        ),
    )


def upsert_chunks(cur, chunks: list[DocumentChunk]) -> None:
    """Upsert chunks into the document_chunks table.

    Uses SQL parameterized queries. Leaves embedding as NULL.
    """
    for chunk in chunks:
        cur.execute(
            """
            INSERT INTO document_chunks (id, document_id, chunk_index, content, metadata, embedding)
            VALUES (%s, %s, %s, %s, %s, NULL)
            ON CONFLICT (id) DO UPDATE SET
                chunk_index = EXCLUDED.chunk_index,
                content = EXCLUDED.content,
                metadata = EXCLUDED.metadata
            """,
            (
                chunk.id,
                chunk.document_id,
                chunk.chunk_index,
                chunk.content,
                __import__('json').dumps(chunk.metadata),
            ),
        )


# ---------------------------------------------------------------------------
# CLI entry point (TASK-CORPUS-026)
# ---------------------------------------------------------------------------

def _main() -> None:
    """CLI entry point for ``python -m hydra_api.ingest``."""
    parser = argparse.ArgumentParser(
        description="HYDRA local corpus ingestion CLI"
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        required=True,
        help="Path to the local corpus manifest JSON file",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Process documents without persisting to the database",
    )

    args = parser.parse_args()

    # Load documents from manifest
    docs = load_local_corpus_manifest(args.manifest)

    # Process
    service = IngestionService()
    result = service.process_documents(docs, dry_run=args.dry_run)

    # Report
    print(f"Processed: {result.processed_documents} document(s)")
    print(f"Created: {result.created_chunks} chunk(s)")
    if result.errors:
        print(f"Errors: {len(result.errors)}")
        for err in result.errors:
            print(f"  - {err}")
    if result.dry_run:
        print("Mode: dry-run (no database persistence)")
    else:
        print("Mode: persisted to database")


if __name__ == "__main__":
    _main()
