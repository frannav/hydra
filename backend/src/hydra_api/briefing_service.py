"""HYDRA API — Briefing service helpers.

Provides:
  - ``build_no_context_briefing_response()`` — returns a BriefingResponse
    with a corpus limitation when no documents are available (no model call).
  - ``build_briefing_draft()`` — builds a Markdown briefing from a
    ``QueryResponse`` with evidence snippets and limitations.

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


def build_briefing_draft(
    question: str,
    query_response: QueryResponse,
) -> str:
    """Build a Markdown briefing draft from a ``QueryResponse``.

    When the query response contains retrieved documents, the draft
    includes the answer, evidence snippets (truncated to
    ``BRIEFING_EVIDENCE_SNIPPET_CHARS``), and source metadata.

    When there are no retrieved documents, delegates to
    ``build_no_context_briefing_response()`` so the output always
    includes the mandatory corpus limitation.

    Parameters
    ----------
    question : str
        The user's question.
    query_response : QueryResponse
        The response from the query service containing the answer,
        retrieved documents, and limitations.

    Returns
    -------
    str
        A Markdown string suitable for inclusion in a briefing.
    """
    from hydra_api.briefing_config import (
        BRIEFING_EVIDENCE_SNIPPET_CHARS,
        BRIEFING_TITLE,
        MANDATORY_CORPUS_LIMITATION,
    )

    retrieved = query_response.retrieved_documents
    limitations = query_response.limitations

    # No documents → delegate to no-context path.
    if not retrieved:
        no_context = build_no_context_briefing_response(
            question,
            query_response.trace_id,
            use_council=True,
        )
        md = no_context.briefing_markdown

        # Append the query response's own limitations so they
        # appear in the output (the no-context path only includes
        # the mandatory corpus limitation).
        if limitations:
            md += "\n## Limitaciones\n\n"
            for lim in limitations:
                md += f"- {lim}\n"

        return md

    # Build the Markdown body with documents.
    lines: list[str] = []
    lines.append(f"# {BRIEFING_TITLE}")
    lines.append("")
    lines.append(f"**Pregunta:** {question}")
    lines.append("")
    lines.append("## Respuesta")
    lines.append("")
    lines.append(query_response.answer)
    lines.append("")

    # Evidence snippets section.
    lines.append("## Evidencia")
    lines.append("")

    for doc in retrieved:
        truncated_evidence = doc.evidence[:BRIEFING_EVIDENCE_SNIPPET_CHARS]
        lines.append(f"- **document_id:** `{doc.document_id}`")
        lines.append(f"  - **chunk_id:** `{doc.chunk_id}`")
        lines.append(f"  - **título:** {doc.title}")
        lines.append(f"  - **fuente:** {doc.source}")
        lines.append(f"  - **score:** {doc.score}")
        lines.append(f"  - **evidencia:** {truncated_evidence}")
        lines.append("")

    # Limitations section.
    lines.append("## Limitaciones")
    lines.append("")

    if limitations:
        for lim in limitations:
            lines.append(f"- {lim}")
    else:
        lines.append(f"- {MANDATORY_CORPUS_LIMITATION}")

    lines.append("")
    return "\n".join(lines)
