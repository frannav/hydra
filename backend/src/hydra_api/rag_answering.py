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
    retrieved_docs: List[RetrievedDocument],
) -> str:
    """Build a grounded answering prompt for the LLM.

    The prompt instructs the model to:
    - Answer **only** using the provided evidence.
    - Cite evidence sources explicitly.
    - State limitations when evidence is insufficient.
    - Avoid claiming coordination, intent, or attribution without
      explicit evidence.

    Parameters
    ----------
    question : str
        The user's question.
    retrieved_docs : list[RetrievedDocument]
        Document chunks retrieved for the question.

    Returns
    -------
    str
        A prompt string ready for the chat model.
    """
    if not retrieved_docs:
        return (
            f"Question: {question}\n\n"
            "No relevant documents were found in the corpus. "
            "Respond that there is insufficient context to answer."
        )

    evidence_sections = []
    for idx, doc in enumerate(retrieved_docs, start=1):
        evidence_sections.append(
            f"[{idx}] Document: {doc.title}\n"
            f"    Source: {doc.source}\n"
            f"    Score: {doc.score:.4f}\n"
            f"    Evidence: {doc.evidence}"
        )

    evidence_block = "\n\n".join(evidence_sections)

    return (
        f"Question: {question}\n\n"
        "Use ONLY the following evidence to answer. "
        "Cite sources explicitly. State limitations when evidence is insufficient. "
        "Do not claim coordination, intent, or attribution without explicit evidence.\n\n"
        f"{evidence_block}\n\n"
        "Answer:"
    )


# ---------------------------------------------------------------------------
# Chat model factory
# ---------------------------------------------------------------------------

def create_chat_model() -> "BaseChatModel":
    """Create a chat model instance for answering.

    Reads ``MODEL_API_KEY`` and ``MODEL_API_BASE_URL`` from the
    environment (via ``os.environ``) so that the actual Settings
    object is **not** required at import time.  This keeps the
    module side-effect-free.

    Returns
    -------
    BaseChatModel
        A configured chat model ready for use.
    """
    # Lazy import to avoid import-time side effects.
    from langchain_openai import ChatOpenAI

    import os

    api_key = os.environ.get("MODEL_API_KEY", "")
    api_base = os.environ.get("MODEL_API_BASE_URL", "https://example.invalid/v1")

    return ChatOpenAI(
        model=os.environ.get("HYDRA_CHAT_MODEL", "qwen3.6"),
        api_key=api_key,
        base_url=api_base,
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
