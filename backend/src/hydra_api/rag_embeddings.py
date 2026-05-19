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


def create_embedding_model(
    settings: Any | None = None,
) -> "OpenAIEmbeddings":
    """Create an OpenAI-compatible embedding model instance.

    If *settings* is ``None``, calls ``get_settings()`` lazily
    (not at import time).  Uses existing Settings fields:
    ``model_api_key``, ``model_api_base_url``, ``hydra_embedding_model``.

    Parameters
    ----------
    settings : Settings | None
        Optional Settings instance.  When ``None``, ``get_settings()``
        is called inside this function.

    Returns
    -------
    OpenAIEmbeddings
        A configured embedding model ready for use.
    """
    # Lazy import to avoid import-time side effects.
    from langchain_openai import OpenAIEmbeddings

    if settings is None:
        from hydra_api.config import get_settings

        settings = get_settings()

    return OpenAIEmbeddings(
        model=settings.hydra_embedding_model,
        api_key=settings.model_api_key,
        base_url=settings.model_api_base_url,
    )
