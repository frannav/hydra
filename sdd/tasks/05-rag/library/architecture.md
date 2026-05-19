# Architecture

High-level architecture for the RAG pipeline.

---

## Components

### RAG Config (`hydra_api.rag_config`)
Centralized constants: `EMBEDDING_DIMENSION=4096`, `DEFAULT_TOP_K=5`, `EVIDENCE_SNIPPET_CHARS`.

### RAG Embeddings (`hydra_api.rag_embeddings`)
- `create_embedding_model(settings)` — Factory using existing Settings vars, lazy
- `validate_embedding_vector(vector, expected_dimension=4096)` — Enforces 4096 floats, finite, numeric

### RAG Store (`hydra_api.rag_store`)
- `fetch_chunks_without_embeddings(cur, limit)` — SELECT from `document_chunks` WHERE `embedding IS NULL`
- `update_chunk_embedding(cur, chunk_id, embedding)` — UPDATE with dimension validation
- `search_similar_chunks(cur, query_embedding, top_k)` — Vector search using `<=>` coseno distance, JOIN with `documents`

### RAG Indexing (`hydra_api.rag_indexing`)
- `RagIndexingService` — Injectable `connection_factory` and `embedding_model`, batch processing with commit/rollback

### RAG Retriever (`hydra_api.rag_retriever`)
- `to_retrieved_document(row)` — Normalizes SQL results to `RetrievedDocument`, truncates evidence
- `create_retriever_runnable(connection_factory, embedding_model)` — LCEL retriever component

### RAG Answering (`hydra_api.rag_answering`)
- `build_answer_prompt(question, retrieved_documents)` — Grounded prompt with evidence citation, limitations, no coordination without evidence
- `create_chat_model(settings)` — Factory using existing Settings
- `create_answer_chain(chat_model)` — LCEL answer chain
- `build_no_context_response(question, trace_id)` — Returns `QueryResponse` with limitations, no model call

### RAG Service (`hydra_api.rag_service`)
- `QueryService` — Orchestrates validation → retrieval → grounded answer or no-context path, injectable retriever/answer_chain

### POST /query Endpoint (`main.py`)
- FastAPI route using `QueryService`, injectable fake for testing, safe error mapping

## Data Flow

```
POST /query (QueryRequest)
  → QueryRequest validation (question, top_k)
  → QueryService.query()
    → retriever(question, top_k)
      → create_embedding_model(question) → embeddings
      → search_similar_chunks(embedding, top_k)
      → to_retrieved_document(rows)
    → if retrieved_documents == []:
        build_no_context_response(question, trace_id)
      else:
        build_answer_prompt(question, retrieved_documents)
        → create_answer_chain → model.generate()
    → QueryResponse(answer, retrieved_documents, limitations, trace_id)
```

## Invariants

- No import-time side effects in any module
- No Neo4j dependency anywhere
- No real model calls in verification
- Embedding dimension strictly 4096
- `top_k` defaults to 5, rejects `<= 0`
- Empty questions rejected
- No-context path returns QueryResponse with limitations, no model call
- Evidence truncated to `EVIDENCE_SNIPPET_CHARS`
- Cosine distance converted to score (`1 - distance`)
- SQL uses parameterized queries
- Safe error handling: no secrets, headers, stack traces, prompts, or full LLM outputs
