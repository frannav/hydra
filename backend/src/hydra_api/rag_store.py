"""HYDRA API — RAG store helpers for pending chunks and embedding updates.

All SQL is parameterized.  Schema DDL lives in ``db_schema.py``.
No database connection is opened at import time.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List

if TYPE_CHECKING:
    from psycopg import Cursor

from hydra_api.rag_embeddings import validate_embedding_vector


# ---------------------------------------------------------------------------
# Pending chunks
# ---------------------------------------------------------------------------

def fetch_chunks_without_embeddings(
    cur: "Cursor",
    limit: int = 100,
) -> List[Dict[str, Any]]:
    """Return chunks that do not yet have an embedding.

    Parameters
    ----------
    cur : Cursor
        An open database cursor.
    limit : int
        Maximum number of rows to return.

    Returns
    -------
    list[dict]
        Each dict contains ``chunk_id`` and ``content``.
    """
    cur.execute(
        """
        SELECT id AS chunk_id, content
        FROM document_chunks
        WHERE embedding IS NULL
        ORDER BY id
        LIMIT %s
        """,
        (limit,),
    )
    rows = cur.fetchall()
    columns = [desc[0] for desc in cur.description]
    return [dict(zip(columns, row)) for row in rows]


# ---------------------------------------------------------------------------
# Embedding update
# ---------------------------------------------------------------------------

def update_chunk_embedding(
    cur: "Cursor",
    chunk_id: str,
    embedding: List[float],
) -> None:
    """Store an embedding vector for a single chunk.

    Parameters
    ----------
    cur : Cursor
        An open database cursor.
    chunk_id : str
        Primary-key of the chunk row.
    embedding : list[float]
        Embedding vector (validated to 4096 dimensions).
    """
    validated = validate_embedding_vector(embedding)

    cur.execute(
        """
        UPDATE document_chunks
        SET embedding = %s::vector
        WHERE id = %s
        """,
        (validated, chunk_id),
    )


# ---------------------------------------------------------------------------
# Vector search
# ---------------------------------------------------------------------------

def search_similar_chunks(
    cur: "Cursor",
    query_embedding: List[float],
    top_k: int = 5,
) -> List[Dict[str, Any]]:
    """Search for chunks similar to *query_embedding* using cosine distance.

    Joins ``document_chunks`` with ``documents`` so that title and source
    are available in the result.  Only chunks with a non-NULL embedding
    are considered.

    Parameters
    ----------
    cur : Cursor
        An open database cursor.
    query_embedding : list[float]
        The query embedding vector (4096 dimensions).
    top_k : int
        Number of closest results to return.

    Returns
    -------
    list[dict]
        Each dict contains ``document_id``, ``chunk_id``, ``title``,
        ``source``, ``content``, and ``score`` (``1 - distance``).
    """
    validated = validate_embedding_vector(query_embedding)

    cur.execute(
        """
        SELECT
            d.id            AS document_id,
            dc.id           AS chunk_id,
            d.title,
            d.source,
            dc.content,
            1 - (dc.embedding <=> %s::vector) AS score
        FROM document_chunks dc
        JOIN documents d ON d.id = dc.document_id
        WHERE dc.embedding IS NOT NULL
        ORDER BY dc.embedding <=> %s::vector
        LIMIT %s
        """,
        (validated, validated, top_k),
    )
    rows = cur.fetchall()
    columns = [desc[0] for desc in cur.description]
    return [dict(zip(columns, row)) for row in rows]
