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

import json
from typing import TYPE_CHECKING, Any, Callable, Optional

from hydra_api.schemas import CouncilReview, RiskLevel

if TYPE_CHECKING:
    from hydra_api.schemas import RetrievedDocument

# ---------------------------------------------------------------------------
# Parsers
# ---------------------------------------------------------------------------


def _safe_parse_chain_output(value: Any) -> dict[str, Any]:
    """Safely parse a chain output into a dict.

    - If already a dict, return it.
    - If a string, try JSON parse; on failure extract safe defaults.
    - Never uses ``eval``.

    Parameters
    ----------
    value : Any
        Raw output from a chain callable.

    Returns
    -------
    dict
        A safe dict with ``evidence_supported``, ``unsupported_claims``,
        ``risk_level``, ``risk_review`` keys (may be missing).
    """
    if isinstance(value, dict):
        return value

    if isinstance(value, str):
        value = value.strip()
        if not value:
            return {}
        try:
            parsed = json.loads(value)
            if isinstance(parsed, dict):
                return parsed
        except (json.JSONDecodeError, ValueError):
            pass
        # Not JSON — return empty dict (will get safe defaults).
        return {}

    return {}


def _truncate(value: str, max_len: int = 200) -> str:
    """Truncate a string to *max_len* characters."""
    if not isinstance(value, str):
        return ""
    if len(value) > max_len:
        return value[:max_len] + "..."
    return value


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
      - ``risk_review`` defaults to a safe limitation message

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
            risk_review="No se pudo analizar la revision del council.",
        )

    evidence_supported = data.get("evidence_supported", False)
    if not isinstance(evidence_supported, bool):
        evidence_supported = False

    unsupported_claims = data.get("unsupported_claims", [])
    if not isinstance(unsupported_claims, list):
        # Convert string to a brief list.
        if isinstance(unsupported_claims, str):
            unsupported_claims = [_truncate(unsupported_claims, 200)]
        else:
            unsupported_claims = []

    risk_review = data.get("risk_review", "")
    if not isinstance(risk_review, str):
        risk_review = ""

    # Ensure risk_review is non-empty.
    if not risk_review.strip():
        risk_review = "No se pudo realizar revision de riesgo: evidencia insuficiente o respuesta del modelo vacia."

    # Truncate long strings.
    risk_review = _truncate(risk_review, 500)
    unsupported_claims = [_truncate(c, 200) for c in unsupported_claims]

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

    @staticmethod
    def _invoke_chain(chain: Any, prompt: str) -> str:
        """Invoke a chain safely, supporting fakes and LangChain objects.

        - If the chain has ``.invoke()``, call ``chain.invoke(prompt)``.
        - Otherwise call ``chain(prompt)`` (for fake callables).
        - Extract ``.content`` from the response if present.
        - Fall back to ``str(response)`` for non-textual outputs.

        Parameters
        ----------
        chain : Any
            A callable or LangChain Runnable.
        prompt : str
            The prompt string to send.

        Returns
        -------
        str
            The response text.
        """
        if hasattr(chain, "invoke"):
            response = chain.invoke(prompt)
        else:
            response = chain(prompt)

        if hasattr(response, "content"):
            return str(response.content)
        return str(response)

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
        analyst_draft = self._invoke_chain(self.analyst_chain, analyst_prompt)
        if not analyst_draft:
            analyst_draft = ""

        # Step 2: Evidence Reviewer
        evidence_prompt = build_evidence_reviewer_prompt(
            analyst_draft, retrieved_documents
        )
        evidence_raw = self._invoke_chain(self.evidence_reviewer_chain, evidence_prompt)
        evidence_review = _safe_parse_chain_output(evidence_raw)

        # Step 3: Risk Reviewer
        risk_prompt = build_risk_reviewer_prompt(
            analyst_draft, retrieved_documents
        )
        risk_raw = self._invoke_chain(self.risk_reviewer_chain, risk_prompt)
        risk_review = _safe_parse_chain_output(risk_raw)

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
        briefing_markdown = self._invoke_chain(self.final_synthesizer_chain, synthesizer_prompt)
        if not briefing_markdown or not str(briefing_markdown).strip():
            from hydra_api.briefing_config import MANDATORY_CORPUS_LIMITATION

            briefing_markdown = (
                "# Limitación\n\n"
                "No se pudo generar el briefing final. "
                "La respuesta del sintetizador estaba vacía.\n\n"
                f"{MANDATORY_CORPUS_LIMITATION}"
            )

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


def create_council_service(
    settings: Any = None,
    chat_model: Any = None,
    review_model: Any = None,
) -> CouncilService:
    """Lazy factory that constructs a real ``CouncilService``.

    Parameters
    ----------
    settings : Settings | None
        Optional Settings instance.  When ``None``, ``get_settings()``
        is called inside this function (only if models are not injected).
    chat_model : object | None
        Optional chat model instance for analyst/final synthesizer.
        When ``None``, uses ``HYDRA_CHAT_MODEL`` from Settings.
    review_model : object | None
        Optional chat model instance for evidence/risk reviewers.
        When ``None``, uses ``HYDRA_REVIEW_MODEL`` from Settings.

    Returns
    -------
    CouncilService
        A fully wired council service.

    Notes
    -----
    This function is safe to call without a ``.env`` file — it
    will raise if required configuration is missing, but it
    does **not** perform any network calls at import time.
    """
    from hydra_api.model_client import create_chat_model

    needs_settings = (chat_model is None or review_model is None)

    if needs_settings:
        from hydra_api.config import get_settings
        settings = get_settings()

    # Build LangChain chains for each council role.
    if chat_model is not None:
        analyst_chain = chat_model
        final_synthesizer_chain = chat_model
    else:
        analyst_chain = create_chat_model(
            model_name=settings.hydra_chat_model,
            settings=settings,
        )
        final_synthesizer_chain = analyst_chain

    if review_model is not None:
        evidence_reviewer_chain = review_model
        risk_reviewer_chain = review_model
    else:
        review_model_inst = create_chat_model(
            model_name=settings.hydra_review_model,
            settings=settings,
        )
        evidence_reviewer_chain = review_model_inst
        risk_reviewer_chain = review_model_inst

    return CouncilService(
        analyst_chain=analyst_chain,
        evidence_reviewer_chain=evidence_reviewer_chain,
        risk_reviewer_chain=risk_reviewer_chain,
        final_synthesizer_chain=final_synthesizer_chain,
    )
