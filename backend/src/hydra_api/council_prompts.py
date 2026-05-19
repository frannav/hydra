"""HYDRA API — Council prompt builders.

Provides four prompt-building functions for the sequential LLM council:
  1. Narrative Analyst  — grounded draft answer
  2. Evidence Reviewer  — checks evidence support
  3. Risk Reviewer      — risk classification
  4. Final Synthesizer  — assembles final briefing markdown

All imports are lazy so that the module has **no side effects**
at import time (no .env reads, no DB connections, no model calls).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, List

if TYPE_CHECKING:
    from hydra_api.schemas import RetrievedDocument


def _truncate_evidence(text: str, max_chars: int = 500) -> str:
    """Truncate evidence text to *max_chars*, normalising line breaks."""
    if not isinstance(text, str):
        return ""
    # Collapse repeated line breaks.
    import re

    text = re.sub(r"\n{3,}", "\n\n", text)
    if len(text) > max_chars:
        return text[:max_chars] + "..."
    return text


def build_narrative_analyst_prompt(
    question: str,
    retrieved_documents: List[Any],
) -> str:
    """Build the narrative analyst prompt.

    The analyst produces a grounded draft answer from the retrieved
    evidence.  When no documents are available the prompt instructs
    the model to declare a limitation and not invent findings.

    Parameters
    ----------
    question : str
        The user's question.
    retrieved_documents : list[RetrievedDocument | dict]
        Document chunks retrieved for the question.

    Returns
    -------
    str
        A prompt string ready for the chat model.
    """
    if not retrieved_documents:
        return (
            f"Pregunta: {question}\n\n"
            "No se encontraron documentos relevantes en el corpus. "
            "Debes declarar una limitacion de evidencia insuficiente "
            "y NO inventar hallazgos, actores o eventos. "
            "No afirmes que multiples actores estan coordinando sin "
            "evidencia explicita de coordinacion. "
            "Responde indicando que no hay contexto suficiente.\n\n"
            "Respuesta:"
        )

    evidence_sections = []
    for idx, doc in enumerate(retrieved_documents, start=1):
        if hasattr(doc, "document_id"):
            doc_id = doc.document_id
            chunk_id = doc.chunk_id
            title = doc.title
            source = doc.source
            evidence = doc.evidence
            score = doc.score
        else:
            doc_id = doc.get("document_id", "unknown")
            chunk_id = doc.get("chunk_id", "unknown")
            title = doc.get("title", "unknown")
            source = doc.get("source", "unknown")
            evidence = doc.get("evidence", "")
            score = doc.get("score", 0.0)

        evidence_sections.append(
            f"[{idx}] Documento: {doc_id}\n"
            f"    Chunk: {chunk_id}\n"
            f"    Titulo: {title}\n"
            f"    Fuente: {source}\n"
            f"    Puntuacion: {score}\n"
            f"    Evidencia: {_truncate_evidence(evidence)}"
        )

    evidence_block = "\n\n".join(evidence_sections)

    return (
        f"Pregunta: {question}\n\n"
        "Eres el Analista Narrativo del council de HYDRA. "
        "Tu tarea es producir un borrador de respuesta fundamentado "
        "EXCLUSIVAMENTE en la evidencia proporcionada abajo.\n\n"
        "Reglas:\n"
        "1. Usa SOLAMENTE la evidencia proporcionada.\n"
        "2. No afirmes que multiples actores estan coordinando, "
        "actuando en concert o compartiendo objetivos sin evidencia "
        "explicita de coordinacion en el texto. "
        "La coordinacion entre actores debe estar respaldada por "
        "documentacion explicita.\n"
        "3. No inventes hechos, actores, eventos o relaciones.\n"
        "4. Si la evidencia es insuficiente, declara una limitacion.\n"
        "5. Cita las fuentes explicitamente.\n\n"
        f"{evidence_block}\n\n"
        "Borrador de respuesta:"
    )


def build_evidence_reviewer_prompt(
    draft_markdown: str,
    retrieved_documents: List[Any],
) -> str:
    """Build the evidence reviewer prompt.

    The reviewer checks whether the analyst draft is supported by
    the retrieved evidence and identifies unsupported claims.

    Parameters
    ----------
    draft_markdown : str
        The analyst's draft response in markdown.
    retrieved_documents : list[RetrievedDocument | dict]
        Document chunks retrieved for the question.

    Returns
    -------
    str
        A prompt string ready for the chat model.
    """
    if not retrieved_documents:
        return (
            f"Borrador del analista:\n{draft_markdown}\n\n"
            "No se encontraron documentos relevantes en el corpus. "
            "Sin evidencia disponible, TODAS las afirmaciones del "
            "borrador son no soportadas. Indica esto claramente.\n\n"
            "Revise el borrador y devuelva:\n"
            "- evidence_supported: false\n"
            "- unsupported_claims: lista de afirmaciones sin evidencia\n"
            "- risk_review: analisis de riesgo basado en la limitacion\n"
        )

    evidence_sections = []
    for idx, doc in enumerate(retrieved_documents, start=1):
        if hasattr(doc, "document_id"):
            doc_id = doc.document_id
            chunk_id = doc.chunk_id
            title = doc.title
            source = doc.source
            evidence = doc.evidence
        else:
            doc_id = doc.get("document_id", "unknown")
            chunk_id = doc.get("chunk_id", "unknown")
            title = doc.get("title", "unknown")
            source = doc.get("source", "unknown")
            evidence = doc.get("evidence", "")

        evidence_sections.append(
            f"[{idx}] Documento: {doc_id}\n"
            f"    Chunk: {chunk_id}\n"
            f"    Titulo: {title}\n"
            f"    Fuente: {source}\n"
            f"    Evidencia: {_truncate_evidence(evidence)}"
        )

    evidence_block = "\n\n".join(evidence_sections)

    return (
        f"Borrador del analista:\n{draft_markdown}\n\n"
        "Eres el Revisor de Evidencia del council de HYDRA. "
        "Tu tarea es verificar que cada afirmacion del borrador "
        "este respaldada por la evidencia proporcionada.\n\n"
        "Reglas:\n"
        "1. Para cada afirmacion significativa, determine si esta "
        "respaldada por evidencia explicita.\n"
        "2. Marque como unsupported_claims toda afirmacion que no "
        "tenga evidencia directa en los documentos.\n"
        "3. No soportar significa que no hay evidencia directa "
        "que respalde la afirmacion.\n"
        "4. No afirmes que multiples actores estan coordinando "
        "sin evidencia explicita de coordinacion.\n"
        "5. Si no hay evidencia suficiente, evidence_supported debe "
        "ser false.\n\n"
        "Evidencia disponible:\n"
        f"{evidence_block}\n\n"
        "Devuelva:\n"
        "- evidence_supported: true o false\n"
        "- unsupported_claims: lista de afirmaciones sin evidencia\n"
        "- risk_review: breve analisis de riesgo basado en la evidencia\n"
    )


def build_risk_reviewer_prompt(
    draft_markdown: str,
    retrieved_documents: List[Any],
) -> str:
    """Build the risk reviewer prompt.

    The reviewer classifies the risk level as bajo, medio, or alto
    and provides an evidence-based justification.

    Parameters
    ----------
    draft_markdown : str
        The analyst's draft response in markdown.
    retrieved_documents : list[RetrievedDocument | dict]
        Document chunks retrieved for the question.

    Returns
    -------
    str
        A prompt string ready for the chat model.
    """
    if not retrieved_documents:
        return (
            f"Borrador del analista:\n{draft_markdown}\n\n"
            "No se encontraron documentos relevantes en el corpus. "
            "Con evidencia insuficiente, debes declarar una limitacion "
            "y NO inventar un nivel de riesgo. Indica que el analisis "
            "de riesgo no puede realizarse sin evidencia.\n\n"
            "Devuelve:\n"
            "- risk_level: solo uno de bajo, medio, alto — o indica "
            "la limitacion si no hay evidencia\n"
            "- risk_review: justificacion basada en evidencia\n"
        )

    evidence_sections = []
    for idx, doc in enumerate(retrieved_documents, start=1):
        if hasattr(doc, "document_id"):
            doc_id = doc.document_id
            chunk_id = doc.chunk_id
            title = doc.title
            source = doc.source
            evidence = doc.evidence
        else:
            doc_id = doc.get("document_id", "unknown")
            chunk_id = doc.get("chunk_id", "unknown")
            title = doc.get("title", "unknown")
            source = doc.get("source", "unknown")
            evidence = doc.get("evidence", "")

        evidence_sections.append(
            f"[{idx}] Documento: {doc_id}\n"
            f"    Chunk: {chunk_id}\n"
            f"    Titulo: {title}\n"
            f"    Fuente: {source}\n"
            f"    Evidencia: {_truncate_evidence(evidence)}"
        )

    evidence_block = "\n\n".join(evidence_sections)

    return (
        f"Borrador del analista:\n{draft_markdown}\n\n"
        "Eres el Revisor de Riesgo del council de HYDRA. "
        "Tu tarea es clasificar el nivel de riesgo basado en la "
        "evidencia disponible.\n\n"
        "Niveles de riesgo permitidos (solo estos tres):\n"
        "- bajo: sin indicadores de amenaza significativa\n"
        "- medio: indicadores moderados de riesgo\n"
        "- alto: indicadores claros de amenaza o riesgo significativo\n\n"
        "Reglas:\n"
        "1. El nivel de riesgo DEBE estar justificado por evidencia "
        "de los documentos recuperados.\n"
        "2. No inventes niveles de riesgo sin evidencia.\n"
        "3. Si la evidencia es insuficiente, declara una limitacion.\n"
        "4. No afirmes que multiples actores estan coordinando "
        "sin evidencia explicita de coordinacion.\n"
        "5. Proporciona una justificacion basada en evidencia.\n\n"
        "Evidencia disponible:\n"
        f"{evidence_block}\n\n"
        "Devuelve:\n"
        "- risk_level: solo uno de bajo, medio, alto\n"
        "- risk_review: justificacion basada en evidencia\n"
    )


def build_final_synthesizer_prompt(
    question: str,
    analyst_draft: str,
    evidence_review: dict[str, Any],
    risk_review: dict[str, Any],
    retrieved_documents: List[Any],
) -> str:
    """Build the final synthesizer prompt.

    The synthesizer assembles the final briefing markdown,
    incorporating the analyst draft, evidence review, and risk
    assessment.  It removes unsupported claims and includes
    the mandatory corpus limitation.

    Parameters
    ----------
    question : str
        The user's question.
    analyst_draft : str
        The narrative analyst's draft response.
    evidence_review : dict
        Evidence review result with keys like
        ``evidence_supported``, ``unsupported_claims``, ``risk_review``.
    risk_review : dict
        Risk review result with keys like ``risk_level``, ``risk_review``.
    retrieved_documents : list[RetrievedDocument | dict]
        Document chunks retrieved for the question.

    Returns
    -------
    str
        A prompt string ready for the chat model.
    """
    evidence_supported = evidence_review.get("evidence_supported", False)
    unsupported_claims = evidence_review.get("unsupported_claims", [])
    risk_level = risk_review.get("risk_level", "medio")
    risk_text = risk_review.get("risk_review", "")

    # Build unsupported claims section.
    if unsupported_claims:
        unsupported_section = (
            "\nAfirmaciones no soportadas detectadas (deben ser "
            "eliminadas o marcadas como no verificadas):\n"
        )
        for claim in unsupported_claims:
            unsupported_section += f"- {_truncate_evidence(str(claim), 200)}\n"
    else:
        unsupported_section = (
            "\nNo se detectaron afirmaciones no soportadas.\n"
        )

    # Build evidence supported status section.
    if not evidence_supported:
        evidence_status = (
            "\nADVERTENCIA: La evidencia no respalda las afirmaciones "
            "del borrador. Debes corregir o limitar las afirmaciones "
            "no soportadas en el briefing final.\n"
        )
    else:
        evidence_status = (
            "\nLa evidencia respalda las afirmaciones principales del borrador.\n"
        )

    # Build recovered sources section.
    if retrieved_documents:
        sources_lines = []
        for idx, doc in enumerate(retrieved_documents, start=1):
            if hasattr(doc, "document_id"):
                doc_id = doc.document_id
                chunk_id = doc.chunk_id
                title = doc.title
                source = doc.source
                evidence = _truncate_evidence(doc.evidence, 300)
                score = doc.score
            else:
                doc_id = doc.get("document_id", "unknown")
                chunk_id = doc.get("chunk_id", "unknown")
                title = doc.get("title", "unknown")
                source = doc.get("source", "unknown")
                evidence = _truncate_evidence(doc.get("evidence", ""), 300)
                score = doc.get("score", 0.0)

            sources_lines.append(
                f"[{idx}] document_id: {doc_id}, chunk_id: {chunk_id}, "
                f"titulo: {title}, fuente: {source}, score: {score}, "
                f"evidencia: {evidence}"
            )
        sources_block = "\n".join(sources_lines)
    else:
        sources_block = "(sin documentos recuperados)"

    return (
        "Eres el Sintetizador Final del council de HYDRA. "
        "Tu tarea es generar un briefing final en formato markdown "
        "que integre todas las revisiones del council.\n\n"
        f"Pregunta original: {question}\n\n"
        "Secciones requeridas para el briefing:\n"
        "- Pregunta\n"
        "- Hallazgos con evidencia\n"
        "- Riesgo\n"
        "- Limitaciones\n"
        "- Fuentes recuperadas\n\n"
        f"Borrador del analista:\n{analyst_draft}\n\n"
        f"Evidencia respalda afirmaciones: {evidence_supported}\n"
        f"Nivel de riesgo: {risk_level}\n"
        f"Revision de riesgo: {risk_text}\n"
        f"{evidence_status}"
        f"{unsupported_section}"
        "\nFuentes recuperadas:\n"
        f"{sources_block}\n\n"
        "Reglas para el briefing final:\n"
        "1. El briefing debe incluir todas las secciones requeridas.\n"
        "2. Cada hallazgo debe hacer referencia a un document_id y chunk_id, "
        "o convertirse en limitacion.\n"
        "3. Elimina o marca como no verificadas todas las afirmaciones "
        "no soportadas por evidencia.\n"
        "4. Si evidence_supported es false, corrige o limita las "
        "afirmaciones no soportadas.\n"
        "5. Incluye la siguiente limitacion del corpus obligatoriamente:\n"
        "   \"Limitacion del corpus: el presente briefing se basa "
        "exclusivamente en los documentos disponibles en el corpus. "
        "Las conclusiones pueden no reflejar informacion externa no "
        "incluida en este corpus.\"\n"
        "6. No inventes informacion que no este respaldada por la "
        "evidencia.\n"
        "7. No afirmes que multiples actores estan coordinando sin "
        "evidencia explicita de coordinacion.\n"
        "8. El nivel de riesgo debe ser: bajo, medio, o alto.\n\n"
        "Genera el briefing final en formato markdown:\n"
    )
