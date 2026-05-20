"""HYDRA API — Groundedness judge for evaluation.

This module provides a fake local judge for evaluating the groundedness
of model answers against retrieved evidence.  It has **no import-time
side effects**: no ``.env`` loading, no network calls, no file I/O.
"""

from __future__ import annotations

from typing import Any

# ---------------------------------------------------------------------------
# Valid groundedness labels
# ---------------------------------------------------------------------------

_VALID_LABELS: frozenset[str] = frozenset({"pass", "fail", "warning"})


# ---------------------------------------------------------------------------
# parse_groundedness_label
# ---------------------------------------------------------------------------


def parse_groundedness_label(label: str) -> str:
    """Normalize and validate a groundedness label.

    Parameters
    ----------
    label : str
        A label string such as ``"PASS"``, ``"fail"``, ``"warning"``.

    Returns
    -------
    str
        The lower-cased, validated label.

    Raises
    ------
    ValueError
        When *label* is not one of the accepted values
        (``"pass"``, ``"fail"``, ``"warning"``).
    """
    normalized = label.strip().lower()
    if normalized not in _VALID_LABELS:
        raise ValueError(
            f"Unknown groundedness label: '{label}'. "
            f"Accepted labels: {sorted(_VALID_LABELS)}"
        )
    return normalized


# ---------------------------------------------------------------------------
# build_groundedness_prompt
# ---------------------------------------------------------------------------


def build_groundedness_prompt(
    answer: str,
    evidence_fragments: list[str],
) -> str:
    """Build a prompt for a groundedness judge.

    The prompt asks the judge to evaluate whether the *answer* is
    grounded in the provided *evidence_fragments* and returns a label
    (``pass``, ``warning``, or ``fail``).

    Answer text is truncated to 1000 characters to avoid oversized prompts.

    Parameters
    ----------
    answer : str
        The model's answer to evaluate.
    evidence_fragments : list[str]
        Evidence fragments retrieved for the answer.

    Returns
    -------
    str
        A prompt string that includes the answer and evidence
        fragments with a request for a groundedness label.
    """
    # Truncate answer to avoid oversized prompts.
    max_answer_chars = 1000
    truncated_answer = answer[:max_answer_chars] + ("..." if len(answer) > max_answer_chars else "")

    evidence_text = "\n".join(
        f"- {frag[:500]}" for frag in evidence_fragments
    ) if evidence_fragments else "(sin evidencia)"

    return (
        "Eres un juez de groundedness (fundamentación). "
        "Evalúa si la respuesta está fundamentada en la evidencia proporcionada.\n\n"
        "Respuesta:\n"
        f"{truncated_answer}\n\n"
        "Evidencia recuperada:\n"
        f"{evidence_text}\n\n"
        "Devuelve UNO de los siguientes labels:\n"
        "- pass: la respuesta está claramente fundamentada en la evidencia.\n"
        "- warning: la respuesta tiene algo de fundamento pero no es completa.\n"
        "- fail: la respuesta no está fundamentada en la evidencia o afirma algo sin respaldo.\n\n"
        "Regla importante: no afirmes coordinación, intención o atribución "
        "sin evidencia explícita en los fragmentos proporcionados."
    )


# ---------------------------------------------------------------------------
# GroundednessJudge
# ---------------------------------------------------------------------------


class GroundednessJudge:
    """A fake local judge for groundedness evaluation.

    This class provides a callable interface that can be injected
    into ``EvalService``.  The default implementation always returns
    ``"pass"`` (fake mode).  It can be subclassed or replaced with
    a real LLM-based judge when approved.
    """

    def __call__(
        self,
        answer: str,
        evidence_fragments: list[str],
        **kwargs: Any,
    ) -> str:
        """Evaluate groundedness and return a label.

        Parameters
        ----------
        answer : str
            The model's answer to evaluate.
        evidence_fragments : list[str]
            Evidence fragments retrieved for the answer.
        **kwargs
            Additional keyword arguments (ignored in fake mode).

        Returns
        -------
        str
            A groundedness label: ``"pass"``, ``"warning"``, or ``"fail"``.
        """
        # With no evidence, default to warning (not pass).
        if not evidence_fragments or not any(str(e).strip() for e in evidence_fragments):
            return "warning"
        # Default fake behavior with evidence: pass.
        return "pass"
