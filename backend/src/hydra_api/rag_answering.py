"""HYDRA API — RAG answering utilities.

Provides prompt building, chat-model construction, answer-chain
creation, and a no-context response builder.  All imports are
lazy so that the module has **no side effects** at import time
(no .env reads, no DB connections, no model calls).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, List

from hydra_api.rag_config import EVIDENCE_SNIPPET_CHARS
from hydra_api.schemas import QueryResponse, RetrievedDocument

if TYPE_CHECKING:
    from langchain_core.language_models import BaseChatModel


# ---------------------------------------------------------------------------
# Prompt building
# ---------------------------------------------------------------------------

def build_answer_prompt(
    question: str,
    retrieved_docs: List[Any],
) -> str:
    """Build a grounded answering prompt for the LLM.

    Accepts both ``RetrievedDocument`` instances and dict-like rows
    with keys: ``document_id``, ``chunk_id``, ``title``, ``source``,
    ``score``, ``evidence``.

    For an empty list, returns a safe prompt stating there is no
    retrieved context and the answer must state a limitation.

    For non-empty evidence, includes the question, brief evidence
    (never full documents), traceability fields, and the exact
    Spanish word ``coordinacion`` in the no-coordination rule.

    Parameters
    ----------
    question : str
        The user's question.
    retrieved_docs : list[RetrievedDocument | dict]
        Document chunks retrieved for the question.

    Returns
    -------
    str
        A prompt string ready for the chat model.
    """
    if not retrieved_docs:
        return (
            f"Pregunta: {question}\n\n"
            "No se encontraron documentos relevantes en el corpus. "
            "Responde indicando que no hay contexto suficiente para "
            "responder y menciona esta limitacion."
        )

    evidence_sections = []
    for idx, doc in enumerate(retrieved_docs, start=1):
        # Support both RetrievedDocument objects and dict-like rows.
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

        # Defensive truncation to EVIDENCE_SNIPPET_CHARS.
        if evidence and len(evidence) > EVIDENCE_SNIPPET_CHARS:
            evidence = evidence[:EVIDENCE_SNIPPET_CHARS]

        evidence_sections.append(
            f"[{idx}] Documento: {doc_id}\n"
            f"    Chunk: {chunk_id}\n"
            f"    Titulo: {title}\n"
            f"    Fuente: {source}\n"
            f"    Evidencia: {evidence}"
        )

    evidence_block = "\n\n".join(evidence_sections)

    return (
        f"Pregunta: {question}\n\n"
        "Usa SOLAMENTE la siguiente evidencia para responder. "
        "Cita las fuentes explicitamente. Incluye una lista de "
        "limitaciones describiendo lo que el documento no cubre.\n"
        "No afirmes que multiples actores estan coordinando, actuando "
        "en concert o compartiendo objetivos sin evidencia explicita "
        "de coordinacion en el texto. Cuando la evidencia sea "
        "insuficiente, asigna el marco narrativo "
        "'unknown_or_insufficient_evidence'.\n"
        "No inventes hechos, actores, eventos o relaciones que no "
        "estan presentes en el texto fuente.\n\n"
        f"{evidence_block}\n\n"
        "Respuesta:"
    )


# ---------------------------------------------------------------------------
# Chat model factory
# ---------------------------------------------------------------------------

def create_chat_model(
    settings: Any | None = None,
) -> "BaseChatModel":
    """Create a chat model instance for answering.

    If *settings* is ``None``, calls ``get_settings()`` lazily
    (not at import time).  Uses existing Settings fields:
    ``model_api_key``, ``model_api_base_url``, ``hydra_chat_model``.

    Parameters
    ----------
    settings : Settings | None
        Optional Settings instance.  When ``None``, ``get_settings()``
        is called inside this function.

    Returns
    -------
    BaseChatModel
        A configured chat model ready for use.
    """
    # Lazy import to avoid import-time side effects.
    from langchain_openai import ChatOpenAI

    if settings is None:
        from hydra_api.config import get_settings

        settings = get_settings()

    return ChatOpenAI(
        model=settings.hydra_chat_model,
        api_key=settings.model_api_key,
        base_url=settings.model_api_base_url,
    )


# ---------------------------------------------------------------------------
# Answer chain
# ---------------------------------------------------------------------------

def create_answer_chain(chat_model: "BaseChatModel") -> "RunnableSerializable":
    """Create a LangChain LCEL chain for grounded answering.

    Parameters
    ----------
    chat_model : BaseChatModel
        A configured chat model instance.

    Returns
    -------
    RunnableSerializable
        An LCEL chain that accepts a prompt string and returns the
        model's response.
    """
    # Lazy import to avoid import-time side effects.
    from langchain_core.runnables import RunnableLambda

    def extract_answer(response: str) -> str:
        """Extract the answer text from a model response."""
        if hasattr(response, "content"):
            return str(response.content)
        return str(response)

    chain = chat_model | RunnableLambda(extract_answer)
    return chain


# ---------------------------------------------------------------------------
# No-context response
# ---------------------------------------------------------------------------

def build_no_context_response(
    question: str,
    trace_id: str,
) -> QueryResponse:
    """Build a ``QueryResponse`` when no documents were retrieved.

    This path is taken when the retriever returns zero results,
    so no model call is needed.

    Parameters
    ----------
    question : str
        The user's question (preserved for traceability).
    trace_id : str
        A unique identifier for this query.

    Returns
    -------
    QueryResponse
        A response with empty retrieved_documents, a non-empty
        limitations list, and the preserved trace_id.
    """
    return QueryResponse(
        answer="Sin contexto suficiente para responder a esta pregunta.",
        retrieved_documents=[],
        limitations=[
            "Corpus sin embeddings.",
            "No se encontraron documentos relevantes para la pregunta.",
        ],
        trace_id=trace_id,
    )
