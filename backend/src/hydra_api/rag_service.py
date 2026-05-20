"""HYDRA API — RAG query service.

Provides ``QueryService`` which orchestrates retrieval and
grounded answering (or no-context fallback).  Dependencies
(retriever callable, answer chain, emitter) are injected for
testability.

All imports are lazy so that the module has **no side effects**
at import time (no DB connections, no model calls).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable

from hydra_api.schemas import QueryRequest, QueryResponse

if TYPE_CHECKING:
    from hydra_api.observability import ObservabilityEmitter
    from hydra_api.rag_answering import create_answer_chain as _create_answer_chain


class QueryService:
    """Orchestrates retrieval and answering for a user question.

    Parameters
    ----------
    retriever : callable
        A function ``retriever(question: str, top_k: int) -> list[RetrievedDocument]``.
    answer_chain : callable
        A callable that takes a prompt string and returns an answer string.
        If ``None``, a default chain factory is used.
    emitter : :class:`ObservabilityEmitter`, optional
        An observability emitter for tracing.  When ``None``,
        a local no-op emitter is created lazily.
    build_no_context : callable, optional
        A function ``(question: str, trace_id: str) -> QueryResponse``.
        Defaults to ``build_no_context_response`` from ``rag_answering``.

    Notes
    -----
    The retriever is called first.  If it returns zero documents,
    the no-context path is taken immediately (no model call).
    Otherwise the answer chain is invoked with a grounded prompt.

    The emitter is used to start a trace, record retrieval metadata,
    and emit a generation event.  Zero-retrieval paths still produce
    a trace with a limitation recorded.
    """

    def __init__(
        self,
        retriever: Callable,
        answer_chain: Callable | None = None,
        emitter: "ObservabilityEmitter | None" = None,
        build_no_context: Callable | None = None,
    ) -> None:
        self.retriever = retriever
        self.answer_chain = answer_chain
        self.emitter = emitter
        self._build_no_context = build_no_context

    def query(self, request: QueryRequest) -> QueryResponse:
        """Execute a full RAG query pipeline.

        Parameters
        ----------
        request : QueryRequest
            The validated user query.

        Returns
        -------
        QueryResponse
            The answer with retrieved documents, limitations, and trace_id.
        """
        # Start a trace via the injected emitter.
        emitter = self.emitter
        if emitter is None:
            from hydra_api.observability import create_observability_emitter

            emitter = create_observability_emitter()

        # Build safe metadata for the trace (no full documents or secrets).
        from hydra_api.observability import safe_preview, MAX_QUESTION_PREVIEW_CHARS

        question_preview = safe_preview(request.question, MAX_QUESTION_PREVIEW_CHARS)
        trace_metadata: dict[str, Any] = {
            "question_preview": question_preview,
            "top_k": request.top_k,
        }

        trace_context = emitter.start_trace("query", trace_metadata)
        trace_id = trace_context.trace_id

        # Step 1: Retrieve relevant documents.
        retrieved_docs = self.retriever(request.question, request.top_k)

        # Record retrieval count in trace metadata (no full documents).
        doc_count = len(retrieved_docs)
        trace_metadata["doc_count"] = doc_count
        emitter.event(trace_id, "retrieval", trace_metadata)

        # Step 2: If no documents, return no-context response.
        if not retrieved_docs:
            no_context_fn = self._build_no_context or _build_no_context_response
            response = no_context_fn(request.question, trace_id)
            # Ensure the response uses the emitter's trace_id.
            response.trace_id = trace_id
            return response

        # Step 3: Build grounded prompt and invoke answer chain.
        from hydra_api.rag_answering import build_answer_prompt

        prompt = build_answer_prompt(request.question, retrieved_docs)

        # If no answer_chain was injected, create a default one.
        if self.answer_chain is None:
            from hydra_api.rag_answering import create_chat_model, create_answer_chain

            chat_model = create_chat_model()
            chain = create_answer_chain(chat_model)
        else:
            chain = self.answer_chain

        # Invoke the chain safely: prefer .invoke() for LCEL, fallback to callable.
        if hasattr(chain, "invoke"):
            raw_response = chain.invoke(prompt)
        else:
            raw_response = chain(prompt)

        # Extract answer text from the response.
        if hasattr(raw_response, "content"):
            answer = str(raw_response.content)
        else:
            answer = str(raw_response)

        # Emit generation event with safe preview (no full prompt/docs).
        answer_preview = safe_preview(answer, MAX_QUESTION_PREVIEW_CHARS)
        emitter.event(
            trace_id,
            "generation",
            {"answer_preview": answer_preview, "prompt_version": "1.0"},
        )

        # Reject empty/whitespace-only answer into a safe limitation.
        if not answer or not answer.strip():
            return QueryResponse(
                answer="No se pudo generar una respuesta con la evidencia disponible.",
                retrieved_documents=retrieved_docs,
                limitations=[
                    "La respuesta del modelo estaba vacia o no pudo generarse.",
                ],
                trace_id=trace_id,
            )

        return QueryResponse(
            answer=answer,
            retrieved_documents=retrieved_docs,
            limitations=[],
            trace_id=trace_id,
        )


def _build_no_context_response(
    question: str,
    trace_id: str,
) -> QueryResponse:
    """Default no-context response builder (module-level fallback)."""
    from hydra_api.rag_answering import build_no_context_response as _bnc

    return _bnc(question, trace_id)


def create_query_service() -> QueryService:
    """Create a real QueryService wired to real dependencies.

    This factory is called lazily at request time in ``main.py``
    when no fake ``query_service`` is injected via ``app.state``.

    Returns
    -------
    QueryService
        A fully wired query service.
    """
    from hydra_api.rag_embeddings import create_embedding_model
    from hydra_api.rag_retriever import create_retriever_runnable
    from hydra_api.rag_answering import create_chat_model, create_answer_chain

    embedding_model = create_embedding_model()

    def connection_factory():
        from hydra_api.db import get_connection

        return get_connection()

    retriever = create_retriever_runnable(
        connection_factory=connection_factory,
        embedding_model=embedding_model,
    )

    chat_model = create_chat_model()
    answer_chain = create_answer_chain(chat_model)

    return QueryService(
        retriever=retriever,
        answer_chain=answer_chain,
    )
