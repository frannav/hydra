"""HYDRA API — RAG embedding utilities.

Provides a factory for creating embedding model instances and a
validator for embedding vectors.  All imports are lazy so that
the module has **no side effects** at import time (no .env reads,
no DB connections, no network calls).
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING, List

from hydra_api.rag_config import EMBEDDING_DIMENSION

if TYPE_CHECKING:
    from langchain_openai import OpenAIEmbeddings


def validate_embedding_vector(
    vector: List[float],
    expected_dimension: int = EMBEDDING_DIMENSION,
) -> List[float]:
    """Validate that *vector* is a list of floats with the expected dimension.

    Raises ``ValueError`` when:
    - The length does not match *expected_dimension*.
    - Any element is not a finite number (NaN or infinity).
    - Any element is not numeric (``int`` or ``float``).
    """
    if len(vector) != expected_dimension:
        raise ValueError(
            f"Embedding dimension mismatch: expected {expected_dimension}, "
            f"got {len(vector)}."
        )

    for idx, val in enumerate(vector):
        if not isinstance(val, (int, float)):
            raise ValueError(
                f"Embedding element at index {idx} is not numeric: {type(val).__name__}."
            )
        if math.isnan(val) or math.isinf(val):
            raise ValueError(
                f"Embedding element at index {idx} is not finite: {val}."
            )

    return [float(v) for v in vector]


def create_embedding_model() -> "OpenAIEmbeddings":
    """Create an OpenAI-compatible embedding model instance.

    Reads ``MODEL_API_KEY`` and ``MODEL_API_BASE_URL`` from the
    environment (via ``os.environ``) so that the actual Settings
    object is **not** required at import time.  This keeps the
    module side-effect-free.

    Returns
    -------
    OpenAIEmbeddings
        A configured embedding model ready for use.
    """
    # Lazy import to avoid import-time side effects.
    from langchain_openai import OpenAIEmbeddings

    import os

    api_key = os.environ.get("MODEL_API_KEY", "")
    api_base = os.environ.get("MODEL_API_BASE_URL", "https://example.invalid/v1")

    return OpenAIEmbeddings(
        model=os.environ.get("HYDRA_EMBEDDING_MODEL", "text-embedding-3-small"),
        api_key=api_key,
        base_url=api_base,
    )
