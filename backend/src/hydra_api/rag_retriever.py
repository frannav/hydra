"""HYDRA API — RAG retriever normalizer and LCEL component.

Provides a normalizer that converts raw SQL search results into
``RetrievedDocument`` instances with truncated evidence, and an
LCEL-based retriever runnable with injectable dependencies.

All imports are lazy so that the module has **no side effects**
at import time (no DB connections, no model calls).
"""

from __future__ import annotations

from typing import Any, Callable, List

from hydra_api.rag_config import EVIDENCE_SNIPPET_CHARS
from hydra_api.schemas import RetrievedDocument


def to_retrieved_document(row: dict[str, Any]) -> RetrievedDocument:
    """Convert a raw search-result dict to a ``RetrievedDocument``.

    Parameters
    ----------
    row : dict
        A dictionary containing at least ``document_id``, ``chunk_id``,
        ``title``, ``source``, ``score``, and ``content`` (as returned
        by ``search_similar_chunks``).

    Returns
    -------
    RetrievedDocument
        A validated Pydantic model with evidence truncated to
        ``EVIDENCE_SNIPPET_CHARS`` characters.
    """
    content = row.get("content", "")
    evidence = content[:EVIDENCE_SNIPPET_CHARS] if content else ""

    return RetrievedDocument(
        document_id=row["document_id"],
        chunk_id=row["chunk_id"],
        title=row["title"],
        source=row["source"],
        score=float(row["score"]),
        evidence=evidence,
    )


def create_retriever_runnable(
    connection_factory: Callable,
    embedding_model: Any,
) -> Callable:
    """Create a retriever callable suitable for LCEL pipelines.

    The returned callable accepts a ``question: str`` and an optional
    ``top_k: int`` (default ``5``), embeds the question, executes a
    vector search, and returns a list of ``RetrievedDocument`` instances.

    Parameters
    ----------
    connection_factory : Callable
        A zero-argument callable that returns a DB connection (real or
        fake).  The connection is opened and closed for each invocation.
    embedding_model : Any
        An embedding model instance (real or fake) with an ``embed_query``
        method that accepts a string and returns a list of floats.

    Returns
    -------
    callable
        A function ``retriever(question: str, top_k: int = 5) -> list[RetrievedDocument]``
        that can be wired into a LangChain LCEL chain.

    Notes
    -----
    This function does **not** open any connections or call the model
    at construction time.  All work happens at call time, making it
    safe to use with fakes during testing.
    """
    from hydra_api.rag_store import search_similar_chunks

    def retriever(question: str, top_k: int = 5) -> List[RetrievedDocument]:
        """Retrieve relevant document chunks for *question*.

        Parameters
        ----------
        question : str
            The user's question to embed and search.
        top_k : int
            Number of results to return (must be >= 1).

        Returns
        -------
        list[RetrievedDocument]
            The most relevant chunks, normalized to ``RetrievedDocument``.
        """
        if top_k < 1:
            raise ValueError("top_k must be >= 1")

        # Embed the question.
        query_embedding = embedding_model.embed_query(question)

        # Open a DB connection and search.
        conn = connection_factory()
        try:
            cur = conn.cursor()
            rows = search_similar_chunks(cur, query_embedding, top_k)
            return [to_retrieved_document(row) for row in rows]
        finally:
            conn.close()

    return retriever
