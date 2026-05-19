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

    # Always include the mandatory corpus limitation, unless already present.
    has_corpus_limit = any(
        "corpus" in lim.lower() for lim in limitations
    )
    if limitations:
        for lim in limitations:
            lines.append(f"- {lim}")
    if not has_corpus_limit:
        lines.append(f"- {MANDATORY_CORPUS_LIMITATION}")

    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# BriefingService
# ---------------------------------------------------------------------------


class BriefingService:
    """Orchestrates QueryService + CouncilService for the briefing pipeline.

    All dependencies are injected at construction time, which makes the
    class fully testable without any real LLM or DB calls.

    Parameters
    ----------
    query_service : object
        An object with a ``query(request: BriefingRequest) -> QueryResponse``
        method.  Reuses the same ``QueryService`` that powers ``POST /query``.
    council_service : object or None
        An object with a ``run(question, retrieved_documents)`` method that
        returns an object with ``briefing_markdown``, ``risk_level``, and
        ``council_review`` attributes.  When ``None``, the council path is
        skipped.
    """

    def __init__(
        self,
        query_service: Any,
        council_service: Any | None = None,
    ) -> None:
        self.query_service = query_service
        self.council_service = council_service

    def brief(self, request: BriefingRequest) -> BriefingResponse:
        """Execute the full briefing pipeline.

        Data flow:
          1. Call ``query_service.query(request)`` → ``QueryResponse``
          2. If no retrieved documents → no-context path
          3. If documents and ``use_council=True`` → draft + council
          4. If documents and ``use_council=False`` → draft only

        The ``trace_id`` from the ``QueryResponse`` is preserved in the
        final ``BriefingResponse``.

        Parameters
        ----------
        request : BriefingRequest
            The validated briefing request.

        Returns
        -------
        BriefingResponse
            The final briefing with markdown, risk level, council review,
            and trace id.
        """
        # Step 1: retrieve documents and answer via QueryService.
        query_response: QueryResponse = self.query_service.query(request)

        retrieved = query_response.retrieved_documents
        trace_id = query_response.trace_id

        # Step 2: No documents → no-context path (skips council and models).
        if not retrieved:
            return build_no_context_briefing_response(
                request.question,
                trace_id,
                use_council=request.use_council,
            )

        # Step 3: With documents.
        if request.use_council and self.council_service is not None:
            # Council path: build draft, run council, use council result.
            draft = build_briefing_draft(request.question, query_response)

            council_result = self.council_service.run(
                request.question,
                retrieved,
            )

            return BriefingResponse(
                briefing_markdown=council_result.briefing_markdown,
                risk_level=council_result.risk_level,
                council_review=council_result.council_review,
                trace_id=trace_id,
            )

        # No-council path: use draft directly.
        draft = build_briefing_draft(request.question, query_response)

        return BriefingResponse(
            briefing_markdown=draft,
            risk_level=RiskLevel.medio,
            council_review=None,
            trace_id=trace_id,
        )
