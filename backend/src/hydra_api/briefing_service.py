"""HYDRA API — Briefing service helpers.

Provides:
  - ``build_no_context_briefing_response()`` — returns a BriefingResponse
    with a corpus limitation when no documents are available (no model call).

All imports are lazy so that the module has **no side effects**
at import time (no .env reads, no DB connections, no model calls).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, Optional

from hydra_api.schemas import BriefingResponse, CouncilReview, RiskLevel

if TYPE_CHECKING:
    from hydra_api.schemas import BriefingRequest, QueryResponse, RetrievedDocument


def build_no_context_briefing_response(
    question: str,
    trace_id: str,
    use_council: bool = True,
) -> BriefingResponse:
    """Build a ``BriefingResponse`` when no documents were retrieved.

    This function performs **no model calls**. It returns a briefing
    that states the analysis is limited to the available corpus.

    Parameters
    ----------
    question : str
        The user's question.
    trace_id : str
        Trace identifier propagated from the query pipeline.
    use_council : bool
        When ``True``, includes a ``CouncilReview`` with
        ``evidence_supported=False``. When ``False``, sets
        ``council_review=None``.

    Returns
    -------
    BriefingResponse
        A response with corpus limitation in the markdown body.
    """
    from hydra_api.briefing_config import MANDATORY_CORPUS_LIMITATION

    briefing_markdown = (
        f"# Respuesta sin contexto\n\n"
        f"No se encontraron documentos relevantes en el corpus "
        f"para la pregunta: \"{question}\"\n\n"
        f"{MANDATORY_CORPUS_LIMITATION}\n"
    )

    if use_council:
        council_review = CouncilReview(
            evidence_supported=False,
            unsupported_claims=[],
            risk_review="No se pudo realizar revisión de riesgo: no hay evidencia disponible.",
        )
    else:
        council_review = None

    return BriefingResponse(
        briefing_markdown=briefing_markdown,
        risk_level=RiskLevel.medio,
        council_review=council_review,
        trace_id=trace_id,
    )
