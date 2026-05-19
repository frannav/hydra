"""HYDRA API — Council service: parsers, orchestrator, and factory.

Provides:
  - ``normalize_risk_level()`` — safe string → RiskLevel mapping
  - ``build_council_review()`` — safe dict → CouncilReview builder
  - ``CouncilService`` — injectable 4-chain orchestrator
  - ``create_council_service()`` — lazy factory using Settings

All imports are lazy so that the module has **no side effects**
at import time (no .env reads, no DB connections, no model calls).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, Optional

from hydra_api.schemas import CouncilReview, RiskLevel

if TYPE_CHECKING:
    from hydra_api.schemas import RetrievedDocument

# ---------------------------------------------------------------------------
# Parsers
# ---------------------------------------------------------------------------


def normalize_risk_level(value: str) -> RiskLevel:
    """Convert a string to a RiskLevel enum.

    Known values ('bajo', 'medio', 'alto') map directly.
    Any unknown or invalid value falls back to ``RiskLevel.medio``.

    Parameters
    ----------
    value : str
        The raw risk level string from an LLM response or dict.

    Returns
    -------
    RiskLevel
        The corresponding enum value, or ``medio`` as a safe fallback.
    """
    if not isinstance(value, str):
        return RiskLevel.medio

    normalized = value.strip().lower()
    try:
        return RiskLevel(normalized)
    except ValueError:
        return RiskLevel.medio


def build_council_review(data: dict[str, Any]) -> CouncilReview:
    """Build a ``CouncilReview`` from a dict safely.

    Missing or invalid fields receive safe defaults:
      - ``evidence_supported`` defaults to ``False``
      - ``unsupported_claims`` defaults to ``[]``
      - ``risk_review`` defaults to ``""``

    Parameters
    ----------
    data : dict
        Raw data from an LLM response or chain output.

    Returns
    -------
    CouncilReview
        A validated council review instance.
    """
    if not isinstance(data, dict):
        return CouncilReview(
            evidence_supported=False,
            unsupported_claims=[],
            risk_review="",
        )

    evidence_supported = data.get("evidence_supported", False)
    if not isinstance(evidence_supported, bool):
        evidence_supported = False

    unsupported_claims = data.get("unsupported_claims", [])
    if not isinstance(unsupported_claims, list):
        unsupported_claims = []

    risk_review = data.get("risk_review", "")
    if not isinstance(risk_review, str):
        risk_review = ""

    return CouncilReview(
        evidence_supported=evidence_supported,
        unsupported_claims=unsupported_claims,
        risk_review=risk_review,
    )


# ---------------------------------------------------------------------------
# CouncilService
# ---------------------------------------------------------------------------


class CouncilService:
    """Orchestrates the 4-step LLM council chain.

    All four chain callables are injected at construction time,
    which makes the class fully testable without any real LLM calls.

    Parameters
    ----------
    analyst_chain : callable
        ``(prompt: str) -> str`` — produces the narrative analyst draft.
    evidence_reviewer_chain : callable
        ``(prompt: str) -> dict`` — produces the evidence review dict.
    risk_reviewer_chain : callable
        ``(prompt: str) -> dict`` — produces the risk review dict.
    final_synthesizer_chain : callable
        ``(prompt: str) -> str`` — produces the final briefing markdown.
    """

    def __init__(
        self,
        analyst_chain: Callable[[str], str],
        evidence_reviewer_chain: Callable[[str], dict[str, Any]],
        risk_reviewer_chain: Callable[[str], dict[str, Any]],
        final_synthesizer_chain: Callable[[str], str],
    ) -> None:
        self.analyst_chain = analyst_chain
        self.evidence_reviewer_chain = evidence_reviewer_chain
        self.risk_reviewer_chain = risk_reviewer_chain
        self.final_synthesizer_chain = final_synthesizer_chain

    def run(
        self,
        question: str,
        retrieved_documents: list[RetrievedDocument | dict],
    ) -> Any:
        """Execute the full 4-step council chain.

        Returns an object with ``briefing_markdown``, ``risk_level``,
        and ``council_review`` attributes.

        If any chain returns empty / falsy output, the result is
        treated as a limitation (``evidence_supported=False``).

        Parameters
        ----------
        question : str
            The user's question.
        retrieved_documents : list
            Retrieved document chunks (``RetrievedDocument`` or dict).

        Returns
        -------
        Any
            An object with ``briefing_markdown``, ``risk_level``,
            and ``council_review`` attributes.
        """
        from hydra_api.council_prompts import (
            build_evidence_reviewer_prompt,
            build_final_synthesizer_prompt,
            build_narrative_analyst_prompt,
            build_risk_reviewer_prompt,
        )

        # Step 1: Narrative Analyst
        analyst_prompt = build_narrative_analyst_prompt(
            question, retrieved_documents
        )
        analyst_draft = self.analyst_chain(analyst_prompt)
        if not analyst_draft:
            analyst_draft = ""

        # Step 2: Evidence Reviewer
        evidence_prompt = build_evidence_reviewer_prompt(
            analyst_draft, retrieved_documents
        )
        evidence_review = self.evidence_reviewer_chain(evidence_prompt)
        if not isinstance(evidence_review, dict):
            evidence_review = {}

        # Step 3: Risk Reviewer
        risk_prompt = build_risk_reviewer_prompt(
            analyst_draft, retrieved_documents
        )
        risk_review = self.risk_reviewer_chain(risk_prompt)
        if not isinstance(risk_review, dict):
            risk_review = {}

        # Extract risk level with safe fallback.
        risk_level = normalize_risk_level(
            risk_review.get("risk_level", "medio")
        )

        # Build council review safely.
        council_review = build_council_review(evidence_review)

        # Step 4: Final Synthesizer
        synthesizer_prompt = build_final_synthesizer_prompt(
            question,
            analyst_draft,
            evidence_review,
            risk_review,
            retrieved_documents,
        )
        briefing_markdown = self.final_synthesizer_chain(synthesizer_prompt)
        if not briefing_markdown:
            briefing_markdown = ""

        # If evidence is unsupported, add a limitation note.
        if not council_review.evidence_supported:
            if "limitacion" not in briefing_markdown.lower():
                briefing_markdown = (
                    "# Limitación\n\n"
                    "No se pudo respaldar la evidencia para las "
                    "afirmaciones principales.\n\n" + briefing_markdown
                )

        # Return a simple object-like result.
        class CouncilResult:
            briefing_markdown: str
            risk_level: RiskLevel
            council_review: CouncilReview

            def __init__(
                self,
                briefing_markdown: str,
                risk_level: RiskLevel,
                council_review: CouncilReview,
            ) -> None:
                self.briefing_markdown = briefing_markdown
                self.risk_level = risk_level
                self.council_review = council_review

        return CouncilResult(
            briefing_markdown=briefing_markdown,
            risk_level=risk_level,
            council_review=council_review,
        )


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def create_council_service() -> CouncilService:
    """Lazy factory that constructs a real ``CouncilService``.

    Uses ``HYDRA_CHAT_MODEL`` for the analyst and synthesizer chains,
    and ``HYDRA_REVIEW_MODEL`` for the reviewer chains.
    Reads ``MODEL_API_KEY`` and ``MODEL_API_BASE_URL`` from the
    existing ``Settings`` class.

    This function is safe to call without a ``.env`` file — it
    will raise if required configuration is missing, but it
    does **not** perform any network calls at import time.
    """
    from hydra_api.config import get_settings
    from hydra_api.model_client import build_chain

    settings = get_settings()

    # Build LangChain chains for each council role.
    analyst_chain = build_chain(
        prompt_builder=None,  # prompt built inline in CouncilService.run
        model_name=settings.hydra_chat_model,
    )
    evidence_reviewer_chain = build_chain(
        prompt_builder=None,
        model_name=settings.hydra_review_model,
    )
    risk_reviewer_chain = build_chain(
        prompt_builder=None,
        model_name=settings.hydra_review_model,
    )
    final_synthesizer_chain = build_chain(
        prompt_builder=None,
        model_name=settings.hydra_chat_model,
    )

    return CouncilService(
        analyst_chain=analyst_chain,
        evidence_reviewer_chain=evidence_reviewer_chain,
        risk_reviewer_chain=risk_reviewer_chain,
        final_synthesizer_chain=final_synthesizer_chain,
    )
