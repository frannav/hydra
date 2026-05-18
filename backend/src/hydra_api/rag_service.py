"""HYDRA API — RAG query service.

Provides ``QueryService`` which orchestrates retrieval and
grounded answering (or no-context fallback).  Dependencies
(retriever callable, answer chain) are injected for testability.

All imports are lazy so that the module has **no side effects**
at import time (no DB connections, no model calls).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable

from hydra_api.schemas import QueryRequest, QueryResponse

if TYPE_CHECKING:
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
    build_no_context : callable, optional
        A function ``(question: str, trace_id: str) -> QueryResponse``.
        Defaults to ``build_no_context_response`` from ``rag_answering``.

    Notes
    -----
    The retriever is called first.  If it returns zero documents,
    the no-context path is taken immediately (no model call).
    Otherwise the answer chain is invoked with a grounded prompt.
    """

    def __init__(
        self,
        retriever: Callable,
        answer_chain: Callable | None = None,
        build_no_context: Callable | None = None,
    ) -> None:
        self.retriever = retriever
        self.answer_chain = answer_chain
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
        # Generate a local trace_id if no Langfuse is configured.
        trace_id = f"trace-local-{id(request)}"

        # Step 1: Retrieve relevant documents.
        retrieved_docs = self.retriever(request.question, request.top_k)

        # Step 2: If no documents, return no-context response.
        if not retrieved_docs:
            no_context_fn = self._build_no_context or _build_no_context_response
            return no_context_fn(request.question, trace_id)

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

        answer = chain(prompt)

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
