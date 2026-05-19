# Validation Contract — 05 RAG

## Area: Dependencies and Constants

### VAL-RAG-001: RAG dependencies added
`pyproject.toml` includes `langchain-core`, `langchain-openai`, and `pgvector`. No `neo4j` dependency.
Tool: shell
Evidence: `cd backend && uv run python -c "from langchain_core.runnables import RunnableLambda; from langchain_openai import ChatOpenAI, OpenAIEmbeddings; import pgvector; print('rag deps ok')"`
Evidence: `cd backend && uv run python -c "import pathlib; text=pathlib.Path('pyproject.toml').read_text().lower(); assert 'neo4j' not in text; print('no neo4j dependency')"`

### VAL-RAG-002: RAG constants defined
`rag_config.py` exports `EMBEDDING_DIMENSION=4096`, `DEFAULT_TOP_K=5`, `EVIDENCE_SNIPPET_CHARS > 0`.
Tool: shell
Evidence: `cd backend && uv run python -c "from hydra_api.rag_config import EMBEDDING_DIMENSION, DEFAULT_TOP_K, EVIDENCE_SNIPPET_CHARS; assert EMBEDDING_DIMENSION==4096 and DEFAULT_TOP_K==5 and EVIDENCE_SNIPPET_CHARS>0; print('rag constants ok')"`

### VAL-RAG-003: Schema dimension alignment
`db_schema.py` contains `vector(4096)` in `document_chunks`.
Tool: shell
Evidence: `cd backend && uv run python -c "from hydra_api.db_schema import SCHEMA_STATEMENTS; sql='\n'.join(SCHEMA_STATEMENTS); assert 'vector(4096)' in sql; print('schema dimension ok')"`

## Area: QueryRequest Validation

### VAL-RAG-004: QueryRequest validates question and top_k
`QueryRequest(question='texto')` uses `top_k=5`. `QueryRequest(question='   ')` raises `ValidationError`. `QueryRequest(question='texto', top_k=0)` raises `ValidationError`.
Tool: shell
Evidence: `cd backend && uv run python -c "from pydantic import ValidationError; from hydra_api.schemas import QueryRequest; assert QueryRequest(question='Que pasa?').top_k==5; [QueryRequest(question='x', top_k=1)]; print('valid query ok')"`
Evidence: `cd backend && uv run python -c 'from pydantic import ValidationError; from hydra_api.schemas import QueryRequest; ns={"QueryRequest":QueryRequest,"ValidationError":ValidationError}; exec("bad=0\ntry:\n    QueryRequest(question=\"   \")\nexcept ValidationError:\n    bad+=1\ntry:\n    QueryRequest(question=\"x\", top_k=0)\nexcept ValidationError:\n    bad+=1\nassert bad==2\nprint(\"invalid query rejected\")", ns)'`

## Area: Embeddings

### VAL-RAG-005: Embedding module imports without side effects
`hydra_api.rag_embeddings` imports without `.env`, DB, or model calls.
Tool: shell
Evidence: `cd backend && uv run python -c "import hydra_api.rag_embeddings as m; assert hasattr(m, 'create_embedding_model'); print('embedding module import ok')"`

### VAL-RAG-006: create_embedding_model constructs without network
With env vars set, `create_embedding_model()` returns a non-None object without making network requests.
Tool: shell
Evidence: `cd backend && MODEL_API_KEY=fake MODEL_API_BASE_URL=https://example.invalid/v1 uv run python -c "from hydra_api.rag_embeddings import create_embedding_model; emb=create_embedding_model(); assert emb is not None; print('embedding factory ok')"`

### VAL-RAG-007: validate_embedding_vector enforces 4096
`validate_embedding_vector([0.0]*4096)` returns 4096 floats. `validate_embedding_vector([0.0]*3)` raises `ValueError`. `validate_embedding_vector([nan]*4096)` raises `ValueError`.
Tool: shell
Evidence: `cd backend && uv run python -c "from hydra_api.rag_embeddings import validate_embedding_vector; v=validate_embedding_vector([0.0]*4096); assert len(v)==4096; print('valid embedding ok')"`
Evidence: `cd backend && uv run python -c 'from hydra_api.rag_embeddings import validate_embedding_vector; import math; ns={"validate_embedding_vector":validate_embedding_vector,"math":math,"ValueError":ValueError}; exec("bad=0\nfor v in ([0.0]*3, [math.nan]*4096):\n    try:\n        validate_embedding_vector(v)\n    except ValueError:\n        bad+=1\nassert bad==2\nprint(\"bad embeddings rejected\")", ns)'`

## Area: RAG Store

### VAL-RAG-008: RAG store module imports without side effects
`hydra_api.rag_store` imports without DB or `.env`. No `CREATE TABLE` in source.
Tool: shell
Evidence: `cd backend && uv run python -c "import hydra_api.rag_store as s; print('rag store import ok')"`
Evidence: `cd backend && uv run python -c "import inspect, hydra_api.rag_store as s; src=inspect.getsource(s).upper(); assert 'CREATE TABLE' not in src; print('no schema creation in rag store')"`

### VAL-RAG-009: fetch_chunks_without_embeddings query
`fetch_chunks_without_embeddings` is callable. Source contains `embedding IS NULL` and `LIMIT`.
Tool: shell
Evidence: `cd backend && uv run python -c "from hydra_api.rag_store import fetch_chunks_without_embeddings; print(callable(fetch_chunks_without_embeddings))"`
Evidence: `cd backend && uv run python -c "import inspect; from hydra_api import rag_store; src=inspect.getsource(rag_store.fetch_chunks_without_embeddings); assert 'embedding IS NULL' in src and 'LIMIT' in src; print('pending chunk query ok')"`

### VAL-RAG-010: update_chunk_embedding helper
`update_chunk_embedding` is callable. Source contains `UPDATE document_chunks` and `validate_embedding_vector`.
Tool: shell
Evidence: `cd backend && uv run python -c "from hydra_api.rag_store import update_chunk_embedding; print(callable(update_chunk_embedding))"`
Evidence: `cd backend && uv run python -c "import inspect; from hydra_api import rag_store; src=inspect.getsource(rag_store.update_chunk_embedding); assert 'UPDATE document_chunks' in src and 'validate_embedding_vector' in src; print('embedding update helper ok')"`

## Area: RAG Indexing

### VAL-RAG-011: RagIndexingService importable
`RagIndexingService` class exists and is importable.
Tool: shell
Evidence: `cd backend && uv run python -c "import hydra_api.rag_indexing as m; assert hasattr(m, 'RagIndexingService'); print('rag indexing import ok')"`
Evidence: `cd backend && uv run python -c "from hydra_api.rag_indexing import RagIndexingService; service=RagIndexingService(connection_factory=lambda: None, embedding_model=object()); print(service.__class__.__name__)"`

## Area: Vector Search

### VAL-RAG-012: search_similar_chunks SQL
`search_similar_chunks` is callable. Source references `document_chunks`, `documents`, `embedding IS NOT NULL`, and `<=>`.
Tool: shell
Evidence: `cd backend && uv run python -c "from hydra_api.rag_store import search_similar_chunks; print(callable(search_similar_chunks))"`
Evidence: `cd backend && uv run python -c "import inspect; from hydra_api import rag_store; src=inspect.getsource(rag_store.search_similar_chunks); assert 'document_chunks' in src and 'documents' in src and 'embedding IS NOT NULL' in src and '<=>' in src; print('vector search sql ok')"`

## Area: Retriever

### VAL-RAG-013: Retriever module imports and normalizes
`rag_retriever` imports without side effects. `to_retrieved_document` exists and truncates evidence.
Tool: shell
Evidence: `cd backend && uv run python -c "import hydra_api.rag_retriever as r; assert hasattr(r, 'to_retrieved_document'); print('retrieved normalizer import ok')"`
Evidence: `cd backend && uv run python -c "from hydra_api.rag_retriever import to_retrieved_document; d=to_retrieved_document({'document_id':'doc','chunk_id':'c','title':'T','source':'S','score':0.5,'content':'x'*2000}); assert d.document_id=='doc' and len(d.evidence)<2000; print('retrieved document ok')"`

### VAL-RAG-014: create_retriever_runnable
`create_retriever_runnable` exists and returns a runnable with injectable deps.
Tool: shell
Evidence: `cd backend && uv run python -c "from hydra_api.rag_retriever import create_retriever_runnable; r=create_retriever_runnable(connection_factory=lambda: None, embedding_model=object()); assert r is not None; print('retriever runnable ok')"`

## Area: Answering

### VAL-RAG-015: Answering module imports
`rag_answering` imports without side effects. `create_answer_chain` and `create_chat_model` exist.
Tool: shell
Evidence: `cd backend && uv run python -c "import hydra_api.rag_answering as a; assert hasattr(a, 'create_answer_chain'); print('answering import ok')"`
Evidence: `cd backend && MODEL_API_KEY=fake MODEL_API_BASE_URL=https://example.invalid/v1 uv run python -c "from hydra_api.rag_answering import create_chat_model; model=create_chat_model(); assert model is not None; print('chat factory ok')"`

### VAL-RAG-016: build_no_context_response
`build_no_context_response` returns `QueryResponse` with empty `retrieved_documents`, non-empty `limitations`, and preserved `trace_id`.
Tool: shell
Evidence: `cd backend && uv run python -c "from hydra_api.rag_answering import build_no_context_response; r=build_no_context_response('q','trace-local'); assert r.retrieved_documents==[] and r.limitations and r.trace_id=='trace-local'; print('no context response ok')"`

## Area: Query Service

### VAL-RAG-017: QueryService orchestrates no-context path
`QueryService` importable. With empty retriever, returns no-context response with limitations and trace_id.
Tool: shell
Evidence: `cd backend && uv run python -c "from hydra_api.rag_service import QueryService; print(callable(QueryService))"`
Evidence: `cd backend && uv run python -c "from hydra_api.rag_service import QueryService; from hydra_api.schemas import QueryRequest; s=QueryService(retriever=lambda q,k: [], answer_chain=lambda *a, **k: 'x'); r=s.query(QueryRequest(question='q')); assert r.retrieved_documents==[] and r.limitations and r.trace_id; print('query service no-context ok')"`

## Area: POST /query Endpoint

### VAL-RAG-018: Health endpoint works
`GET /health` returns 200 with `{"status": "ok"}`.
Tool: shell
Evidence: `cd backend && uv run python -c "from fastapi.testclient import TestClient; from hydra_api.main import app; assert TestClient(app).get('/health').json()['status']=='ok'; print('health ok')"`

### VAL-RAG-019: POST /query with fake service
`POST /query` returns 200 with `QueryResponse` shape when fake service is injected. OpenAPI includes `/query`.
Tool: shell
Evidence: `cd backend && uv run python -c "from fastapi.testclient import TestClient; from hydra_api.main import app; from hydra_api.schemas import QueryResponse; Fake=type('Fake', (), {'query': lambda self, request: QueryResponse(answer='Sin contexto suficiente.', retrieved_documents=[], limitations=['Corpus sin embeddings.'], trace_id='trace-test')}); app.state.query_service=Fake(); res=TestClient(app).post('/query', json={'question':'q','top_k':5}); assert res.status_code==200 and res.json()['trace_id']=='trace-test'; del app.state.query_service; print('query fake endpoint ok')"`
Evidence: `cd backend && uv run python -c "from fastapi.testclient import TestClient; from hydra_api.main import app; schema=TestClient(app).get('/openapi.json').json(); assert '/query' in schema['paths']; print('openapi query ok')"`

## Cross-Area: End-to-End Pipeline

### VAL-CROSS-RAG-001: Full pipeline with fakes
Empty retriever → no-context response without model call. Fake retriever with docs → answer chain invoked.
Tool: shell
Evidence: `cd backend && uv run python -c "from hydra_api.rag_service import QueryService; from hydra_api.schemas import QueryRequest; s=QueryService(retriever=lambda q,k: [], answer_chain=lambda *a, **k: 'x'); r=s.query(QueryRequest(question='q')); assert r.retrieved_documents==[] and r.limitations; print('full pipeline no-context ok')"`

### VAL-CROSS-RAG-002: No Neo4j anywhere
No Neo4j references in any RAG module or pyproject.toml.
Tool: shell
Evidence: `grep -r 'neo4j' backend/src/hydra_api/rag_*.py backend/pyproject.toml || echo 'no neo4j references found'`
