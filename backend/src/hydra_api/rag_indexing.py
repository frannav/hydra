"""HYDRA API — RAG indexing service.

Orchestrates batch embedding of pending chunks using an injectable
database connection factory and an injectable embedding model.

No side effects at import time.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, List, Optional

from hydra_api.rag_store import fetch_chunks_without_embeddings, update_chunk_embedding

if TYPE_CHECKING:
    from langchain_core.embeddings import Embeddings


class RagIndexingService:
    """Batch-embed pending chunks and store the results.

    Parameters
    ----------
    connection_factory : Callable[[], Any]
        A zero-argument callable that returns a new database connection.
        The connection must support ``cursor()``, ``commit()``, and
        ``rollback()`` (e.g. a ``psycopg`` connection).
    embedding_model : Embeddings
        An object providing ``.embed_documents(texts: list[str])``
        that returns a list of embedding vectors.
    batch_size : int
        Number of chunks to embed per batch.
    fetch_limit : int
        Maximum chunks fetched per ``fetch_chunks_without_embeddings`` call.
    """

    def __init__(
        self,
        connection_factory: Callable[[], Any],
        embedding_model: "Embeddings",
        batch_size: int = 32,
        fetch_limit: int = 100,
    ) -> None:
        if batch_size < 1:
            raise ValueError("batch_size must be >= 1")
        if fetch_limit < 1:
            raise ValueError("fetch_limit must be >= 1")

        self.connection_factory = connection_factory
        self.embedding_model = embedding_model
        self.batch_size = batch_size
        self.fetch_limit = fetch_limit

    def index(self, max_batches: Optional[int] = None) -> dict[str, int]:
        """Run one or more indexing batches.

        For each batch:
        1. Fetch pending chunks.
        2. Embed them in bulk.
        3. Write embeddings back to the database (inside a transaction).

        Parameters
        ----------
        max_batches : int | None
            If provided, stop after this many batches.  Must be >= 1.
            ``None`` means continue until no pending chunks remain.

        Returns
        -------
        dict
            ``{"batches": N, "chunks_embedded": M}``.
        """
        if max_batches is not None and max_batches < 1:
            raise ValueError("max_batches must be >= 1")
        batches = 0
        total_embedded = 0

        while True:
            conn = self.connection_factory()
            cur = None
            try:
                cur = conn.cursor()
                chunks = fetch_chunks_without_embeddings(cur, self.fetch_limit)
                if not chunks:
                    break

                for i in range(0, len(chunks), self.batch_size):
                    batch = chunks[i : i + self.batch_size]
                    texts = [c["content"] for c in batch]
                    embeddings = self.embedding_model.embed_documents(texts)

                    if len(embeddings) != len(batch):
                        raise ValueError(
                            f"Expected {len(batch)} embeddings, got {len(embeddings)}"
                        )

                    for chunk, emb in zip(batch, embeddings):
                        update_chunk_embedding(cur, chunk["id"], emb)

                    conn.commit()
                    total_embedded += len(batch)
                    batches += 1

                    if max_batches is not None and batches >= max_batches:
                        return {"batches": batches, "chunks_embedded": total_embedded}

            except Exception:
                if conn:
                    conn.rollback()
                raise
            finally:
                if cur is not None:
                    cur.close()
                if conn:
                    conn.close()

        return {"batches": batches, "chunks_embedded": total_embedded}
