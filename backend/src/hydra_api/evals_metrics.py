"""HYDRA API — Evaluation metric functions.

All functions in this module are **deterministic** and have **no
import-time side effects**: no ``.env`` loading, no network calls,
no file I/O.
"""

from __future__ import annotations

from typing import Any

from .schemas import EvalMetrics


# ---------------------------------------------------------------------------
# Precision@k
# ---------------------------------------------------------------------------


def precision_at_k(
    expected_documents: list[str],
    retrieved_documents: list[Any],
    k: int,
) -> float:
    """Compute retrieval Precision@k.

    Parameters
    ----------
    expected_documents : list[str]
        List of expected document IDs.
    retrieved_documents : list[RetrievedDocument | dict]
        List of retrieved documents (objects with a ``document_id``
        attribute or key).
    k : int
        Number of top results to consider.  Must be **>= 1**.

    Returns
    -------
    float
        Precision = (number of expected docs in top-k retrieved) /
        (total number of expected docs).  Returns ``0.0`` when there
        are no expected documents or no retrieved documents.

    Raises
    ------
    ValueError
        When ``k <= 0``.

    Notes
    -----
    - Retrieved documents are **deduplicated by ``document_id``**
      before computing precision, so duplicate chunks from the same
      document do not inflate the score.
    - The metric is **deterministic** for a given input.
    - When ``expected_documents`` is empty, returns ``0.0``.
    """
    if k <= 0:
        raise ValueError(f"precision_at_k: k must be >= 1, got {k}")

    if not expected_documents:
        return 0.0

    if not retrieved_documents:
        return 0.0

    # --- Deduplicate retrieved documents by document_id (preserve order) ---
    seen_ids: set[str] = set()
    deduplicated: list[str] = []
    for doc in retrieved_documents:
        doc_id = doc["document_id"] if isinstance(doc, dict) else doc.document_id
        if doc_id not in seen_ids:
            seen_ids.add(doc_id)
            deduplicated.append(doc_id)

    # --- Take top-k -------------------------------------------------------
    top_k_ids = deduplicated[:k]

    # --- Compute precision -------------------------------------------------
    expected_set = set(expected_documents)
    hits = sum(1 for doc_id in top_k_ids if doc_id in expected_set)
    return hits / len(expected_set)
