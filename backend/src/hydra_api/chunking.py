"""HYDRA API — Deterministic text chunking.

No model calls, no embeddings, no DB connections on import.
"""

from __future__ import annotations

from .schemas import DocumentChunk, RawDocument


def chunk_text(text: str, chunk_size: int = 1200, overlap: int = 150) -> list[str]:
    """Deterministic character-based text chunking.

    Rejects chunk_size <= 0, overlap < 0, overlap >= chunk_size.
    Returns single chunk if text fits.
    """
    if chunk_size <= 0:
        raise ValueError(f"chunk_size must be positive, got: {chunk_size}")
    if overlap < 0:
        raise ValueError(f"overlap must be non-negative, got: {overlap}")
    if overlap >= chunk_size:
        raise ValueError(f"overlap ({overlap}) must be less than chunk_size ({chunk_size})")

    if len(text) <= chunk_size:
        return [text]

    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        if end >= len(text):
            break
        start = end - overlap

    return chunks


def chunk_raw_document(
    raw_document: RawDocument,
    chunk_size: int = 1200,
    overlap: int = 150,
) -> list[DocumentChunk]:
    """Convert a RawDocument into DocumentChunks preserving traceability.

    Chunk IDs follow format: document_id_chunk_000
    Metadata preserves: document_id, title, source, url, published_at, domain, chunk_index
    """
    text_chunks = chunk_text(raw_document.text, chunk_size, overlap)

    metadata_snapshot = {
        "document_id": raw_document.document_id,
        "title": raw_document.metadata.title,
        "source": raw_document.metadata.source,
        "url": raw_document.metadata.url,
        "published_at": raw_document.metadata.published_at,
        "domain": raw_document.metadata.domain,
    }

    chunks: list[DocumentChunk] = []
    for i, chunk_text_str in enumerate(text_chunks):
        chunk_id = f"{raw_document.document_id}_chunk_{i:03d}"
        chunks.append(DocumentChunk(
            id=chunk_id,
            document_id=raw_document.document_id,
            chunk_index=i,
            content=chunk_text_str,
            metadata={**metadata_snapshot, "chunk_index": i},
        ))

    return chunks
