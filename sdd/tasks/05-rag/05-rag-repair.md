# Repair Packet — Mission 05 RAG

Task:
Repair the reviewed implementation of `TASK-RAG-001` to `TASK-RAG-017`
without adding new product scope. Keep `TASK-RAG-018` to `TASK-RAG-020`
blocked until corpus, DB, real model keys, and explicit approval exist.

Review verdict:
Mission 05 is **not accepted yet**. Many shallow import/source checks pass, but
the reviewer found blockers in Settings usage, prompt compatibility, lazy
service construction, LCEL invocation, SQL helper validation, and indexing
edge cases.

## Source of truth

- `hydra/sdd/README.md`
- `hydra/sdd/01-architecture-decisions.md`
- `hydra/sdd/02-data-model.md`
- `hydra/sdd/03-api-contract.md`
- `hydra/sdd/rag-pipeline.md`
- `hydra/sdd/07-implementation-plan.md`
- `hydra/sdd/08-task-checklist.md`
- `hydra/sdd/tasks/05-rag/05-rag.md`
- Existing DB schema in `hydra/backend/src/hydra_api/db_schema.py`
- Existing configuration in `hydra/backend/src/hydra_api/config.py`
- Existing canonical schemas in `hydra/backend/src/hydra_api/schemas.py`

## Mission mode

- This is a **repair**, not a new feature.
- Do not call real LLM providers, embedding providers, Langfuse, or external
  APIs.
- Do not require a live PostgreSQL DB for non-blocked verification.
- Do not use, download, scrape, or invent real corpus documents.
- Do not add Neo4j, graph drivers, frontend upload, observability, evals, or
  briefing logic.
- Do not change API contracts, schema models, table names, environment variable
  names, or embedding dimension.
- Do not mark SDD tasks as `done`; Codex/reviewer will do that after
  acceptance.
- Do not commit.

## Allowed files

Primary repair files:

- `hydra/backend/src/hydra_api/main.py`
- `hydra/backend/src/hydra_api/errors.py`
- `hydra/backend/src/hydra_api/rag_embeddings.py`
- `hydra/backend/src/hydra_api/rag_store.py`
- `hydra/backend/src/hydra_api/rag_indexing.py`
- `hydra/backend/src/hydra_api/rag_retriever.py`
- `hydra/backend/src/hydra_api/rag_answering.py`
- `hydra/backend/src/hydra_api/rag_service.py`

Read-only context files:

- `hydra/backend/src/hydra_api/config.py`
- `hydra/backend/src/hydra_api/db.py`
- `hydra/backend/src/hydra_api/db_schema.py`
- `hydra/backend/src/hydra_api/schemas.py`
- `hydra/backend/pyproject.toml`
- `hydra/backend/uv.lock`

## Forbidden

- Do not modify `hydra/frontend/**`.
- Do not modify `hydra/docs/**`.
- Do not modify `hydra/sdd/**`.
- Do not modify `hydra/backend/pyproject.toml` or `hydra/backend/uv.lock`
  unless a reviewer explicitly confirms a dependency issue. The required RAG
  dependencies are already present.
- Do not create or edit real `.env` files.
- Do not add files under `hydra/backend/data/raw/**` or real metadata under
  `hydra/backend/data/metadata/documents/**`.
- Do not create real model outputs or embedding outputs.
- Do not call real providers from verification commands.
- Do not print API keys, headers, full prompts, full model responses, full
  embeddings, stack traces, or full documents in logs/errors.

## Repair items

### REPAIR-RAG-001: Make model factories Settings-based and keep correct defaults

Problem:

- `create_embedding_model()` and `create_chat_model()` do not accept
  `settings: Settings | None = None`.
- They read `os.environ` directly instead of using existing `Settings`.
- `create_embedding_model()` falls back to `text-embedding-3-small`, which
  violates the SDD default `qwen3-embedding`.

Required fix:

- In `hydra/backend/src/hydra_api/rag_embeddings.py`, implement:
  `create_embedding_model(settings: Settings | None = None)`.
- In `hydra/backend/src/hydra_api/rag_answering.py`, implement:
  `create_chat_model(settings: Settings | None = None)`.
- If `settings` is `None`, call `get_settings()` inside the function only, not
  at import time.
- Use existing settings fields:
  - `settings.model_api_key`
  - `settings.model_api_base_url`
  - `settings.hydra_embedding_model`
  - `settings.hydra_chat_model`
- Keep factories lazy: no provider call at import time or construction time.
- Do not introduce new environment variables.
- Do not print or log model keys or base URLs.

Acceptance checks:

- `cd hydra/backend && uv run python -c "import inspect; from hydra_api.rag_embeddings import create_embedding_model; from hydra_api.rag_answering import create_chat_model; assert 'settings' in inspect.signature(create_embedding_model).parameters; assert 'settings' in inspect.signature(create_chat_model).parameters; print('settings signatures ok')"`
- `cd hydra/backend && MODEL_API_KEY=fake MODEL_API_BASE_URL=https://example.invalid/v1 uv run python -c "from hydra_api.rag_embeddings import create_embedding_model; emb=create_embedding_model(); assert emb is not None; assert getattr(emb, 'model', None)=='qwen3-embedding'; print('embedding factory settings ok')"`
- `cd hydra/backend && MODEL_API_KEY=fake MODEL_API_BASE_URL=https://example.invalid/v1 uv run python -c "from hydra_api.rag_answering import create_chat_model; model=create_chat_model(); assert model is not None; print('chat factory settings ok')"`

### REPAIR-RAG-002: Fix grounded prompt builder compatibility and guardrails

Problem:

- `build_answer_prompt('q', [])` fails the official verification because it
  does not contain Spanish `limitacion` or `contexto`.
- `build_answer_prompt()` assumes every retrieved document has attributes; the
  official check passes dictionaries and currently crashes.
- The prompt uses English `coordination`, while the SDD verification checks for
  Spanish `coordinacion`.

Required fix:

- In `hydra/backend/src/hydra_api/rag_answering.py`, make
  `build_answer_prompt(question, retrieved_documents)` accept both
  `RetrievedDocument` instances and dict-like rows with:
  `document_id`, `chunk_id`, `title`, `source`, `score`, `evidence`.
- For an empty list, return a safe prompt that clearly says there is no
  retrieved context and the answer must state a limitation.
- For non-empty evidence, include:
  - the question;
  - brief evidence only, never full documents;
  - `document_id` and `chunk_id` for traceability;
  - a rule to answer only with retrieved context;
  - a rule to include limitations;
  - the exact Spanish word `coordinacion` in the no-coordination-without-
    evidence rule.
- Re-truncate evidence defensively to `EVIDENCE_SNIPPET_CHARS`.
- Do not log or print prompts.

Acceptance checks:

- `cd hydra/backend && uv run python -c "from hydra_api.rag_answering import build_answer_prompt; p=build_answer_prompt('q', []); assert 'limitacion' in p.lower() or 'contexto' in p.lower(); print('empty prompt safe')"`
- `cd hydra/backend && uv run python -c "from hydra_api.rag_answering import build_answer_prompt; p=build_answer_prompt('q', [{'evidence':'ev','document_id':'doc','chunk_id':'c','title':'T','source':'S','score':0.9}]); assert 'coordinacion' in p.lower() and 'ev' in p and 'doc' in p and 'c' in p; print('grounded prompt dict ok')"`
- `cd hydra/backend && uv run python -c "from hydra_api.rag_answering import build_answer_prompt; from hydra_api.schemas import RetrievedDocument; d=RetrievedDocument(document_id='doc', chunk_id='c', title='T', source='S', score=0.9, evidence='x'*2000); p=build_answer_prompt('q', [d]); assert len(p) < 4000 and 'x'*1000 not in p; print('grounded prompt truncates evidence')"`

### REPAIR-RAG-003: Invoke answer chains correctly and harden QueryService

Problem:

- `QueryService` calls `chain(prompt)`, but LCEL `RunnableSequence` must be
  invoked with `.invoke(prompt)`.
- The real answer path crashes even with fake env vars and fake retrieved docs.
- `trace_id` uses `id(request)`, which is process-local and not a stable safe
  trace identifier.
- Empty answer text is not handled explicitly.

Required fix:

- In `hydra/backend/src/hydra_api/rag_service.py`, keep `QueryService`
  injectable with fake retrievers and fake answer chains.
- Generate a local safe `trace_id`, preferably with `uuid.uuid4()` and prefix
  `trace-local-`.
- If retrieval returns `[]`, call the no-context builder and do **not** invoke
  the answer chain/model.
- If documents are returned:
  - build a grounded prompt with `build_answer_prompt()`;
  - invoke the injected or default answer chain safely:
    - if the chain has `.invoke`, use `chain.invoke(prompt)`;
    - otherwise, call it as a normal callable;
  - if the returned answer has `.content`, extract it;
  - reject or convert empty/whitespace-only answer into a safe limitation
    response, without inventing analysis.
- Return a `QueryResponse` with retrieved documents, `trace_id`, and at least a
  safe corpus limitation when useful.
- Do not log full question, prompt, evidence, or model response.

Acceptance checks:

- `cd hydra/backend && uv run python -c "from hydra_api.rag_service import QueryService; from hydra_api.schemas import QueryRequest; called={'n':0}; s=QueryService(retriever=lambda q,k: [], answer_chain=lambda prompt: called.__setitem__('n', called['n']+1)); r=s.query(QueryRequest(question='q')); assert called['n']==0 and r.retrieved_documents==[] and r.limitations and r.trace_id.startswith('trace-local-'); print('no-context skips model ok')"`
- `cd hydra/backend && uv run python -c "from hydra_api.rag_service import QueryService; from hydra_api.schemas import QueryRequest, RetrievedDocument; called={'n':0}; docs=[RetrievedDocument(document_id='doc', chunk_id='c', title='T', source='S', score=0.9, evidence='ev')]; s=QueryService(retriever=lambda q,k: docs, answer_chain=lambda prompt: (called.__setitem__('n', called['n']+1) or 'answer')); r=s.query(QueryRequest(question='q')); assert called['n']==1 and r.answer=='answer' and r.retrieved_documents and r.trace_id.startswith('trace-local-'); print('callable answer path ok')"`
- `cd hydra/backend && uv run python -c "from hydra_api.rag_service import QueryService; from hydra_api.schemas import QueryRequest, RetrievedDocument; FakeChain=type('FakeChain', (), {'__init__': lambda self: setattr(self, 'called', 0), 'invoke': lambda self, prompt: (setattr(self, 'called', self.called+1) or 'answer via invoke')}); chain=FakeChain(); docs=[RetrievedDocument(document_id='doc', chunk_id='c', title='T', source='S', score=0.9, evidence='ev')]; s=QueryService(retriever=lambda q,k: docs, answer_chain=chain); r=s.query(QueryRequest(question='q')); assert chain.called==1 and r.answer=='answer via invoke'; print('lcel invoke path ok')"`

### REPAIR-RAG-004: Build the real query service lazily in `/query`

Problem:

- `POST /query` returns 503 whenever `app.state.query_service` is not injected.
- `TASK-RAG-017` requires fake injection support **and** lazy construction of a
  real service when no fake is injected.

Required fix:

- In `hydra/backend/src/hydra_api/rag_service.py`, add a small factory such as
  `create_query_service()` or equivalent that wires:
  - `get_connection` as `connection_factory`;
  - `create_embedding_model()` as the embedding model factory result;
  - `create_retriever_runnable(...)`;
  - `create_chat_model()` and `create_answer_chain(...)`.
- The factory must not run at module import time.
- In `hydra/backend/src/hydra_api/main.py`, `POST /query` must:
  - use `app.state.query_service` when present, preserving fake injection;
  - otherwise construct/cache the real service lazily at request time;
  - map expected configuration/runtime errors to safe error responses;
  - never expose stack traces, headers, keys, prompts, or DB DSNs.
- App import and `/health` must still work without `.env`, DB, or model keys.
- Do not call the DB, embeddings provider, or chat provider while importing
  `main.py`.

Acceptance checks:

- `cd hydra/backend && uv run python -c "from fastapi.testclient import TestClient; from hydra_api.main import app; assert TestClient(app).get('/health').json()['status']=='ok'; print('health ok')"`
- `cd hydra/backend && uv run python -c "from fastapi.testclient import TestClient; from hydra_api.main import app; from hydra_api.schemas import QueryResponse; Fake=type('Fake', (), {'query': lambda self, request: QueryResponse(answer='Sin contexto suficiente.', retrieved_documents=[], limitations=['Corpus sin embeddings.'], trace_id='trace-test')}); app.state.query_service=Fake(); res=TestClient(app).post('/query', json={'question':'q','top_k':5}); assert res.status_code==200 and res.json()['trace_id']=='trace-test'; del app.state.query_service; print('query fake endpoint ok')"`
- `cd hydra/backend && uv run python -c "from fastapi.testclient import TestClient; from hydra_api.main import app; schema=TestClient(app).get('/openapi.json').json(); assert '/query' in schema['paths']; print('openapi query ok')"`
- `cd hydra/backend && uv run python -c "import inspect; from hydra_api import main; src=inspect.getsource(main.query); assert 'query_service' in src and ('create_query_service' in src or 'get_query_service' in src); print('query lazy service path present')"`

### REPAIR-RAG-005: Enforce RAG store validations and pending chunk shape

Problem:

- `fetch_chunks_without_embeddings(cur, limit=0)` executes SQL instead of
  failing before SQL.
- It returns only `chunk_id` and `content`, but `TASK-RAG-007` requires:
  `id`, `document_id`, `chunk_index`, `content`, `metadata`.
- It orders by `id`, not by `document_id` and `chunk_index`.
- `update_chunk_embedding(cur, "", vector)` executes SQL instead of rejecting
  empty `chunk_id`.
- `search_similar_chunks(cur, vector, top_k=0)` executes SQL instead of
  rejecting invalid `top_k`.

Required fix:

- In `hydra/backend/src/hydra_api/rag_store.py`, update
  `fetch_chunks_without_embeddings(cur, limit)`:
  - validate `limit >= 1` before `cur.execute`;
  - select exactly the required pending fields:
    `id`, `document_id`, `chunk_index`, `content`, `metadata`;
  - query only `document_chunks` with `embedding IS NULL`;
  - order by `document_id`, `chunk_index`;
  - use parameterized SQL;
  - normalize `metadata=None` to `{}`;
  - fail safely if metadata is not dict-like.
- Update `update_chunk_embedding(cur, chunk_id, embedding)`:
  - reject empty/whitespace `chunk_id` before validation/SQL;
  - validate vector dimension before SQL;
  - update only `document_chunks.embedding`;
  - do not commit.
- Update `search_similar_chunks(cur, query_embedding, top_k)`:
  - reject `top_k < 1` before SQL;
  - validate query embedding dimension before SQL;
  - exclude `dc.embedding IS NOT NULL`;
  - join `documents` for title/source;
  - use `<=>` cosine distance and `1 - distance` score;
  - use parameterized SQL.

Acceptance checks:

- `cd hydra/backend && uv run python -c "import inspect; from hydra_api import rag_store; src=inspect.getsource(rag_store.fetch_chunks_without_embeddings); assert 'embedding IS NULL' in src and 'ORDER BY document_id' in src and 'chunk_index' in src and 'metadata' in src; print('pending chunk query shape ok')"`
- `cd hydra/backend && uv run python -c 'from hydra_api.rag_store import fetch_chunks_without_embeddings, search_similar_chunks, update_chunk_embedding; ns=globals(); exec("class C:\n    description=[]\n    def __init__(self): self.executed=False\n    def execute(self,*a): self.executed=True\n    def fetchall(self): return []\nfor name, fn in [(\"fetch\", lambda c: fetch_chunks_without_embeddings(c,0)), (\"search\", lambda c: search_similar_chunks(c,[0.0]*4096,0)), (\"update\", lambda c: update_chunk_embedding(c,\"\",[0.0]*4096))]:\n    c=C()\n    try:\n        fn(c)\n    except ValueError:\n        assert not c.executed, name\n    else:\n        raise AssertionError(name)\nprint(\"rag_store invalid inputs rejected before sql\")", ns)'`
- `cd hydra/backend && uv run python -c 'from hydra_api.rag_store import update_chunk_embedding; ns=globals(); exec("class C:\n    def __init__(self): self.executed=False\n    def execute(self,*a): self.executed=True\nc=C()\ntry:\n    update_chunk_embedding(c, \"chunk\", [0.0]*3)\nexcept ValueError:\n    assert not c.executed\nelse:\n    raise AssertionError(\"short vector accepted\")\nprint(\"bad embedding rejected before sql\")", ns)'`

### REPAIR-RAG-006: Harden retriever normalization without changing contract

Problem:

- `to_retrieved_document()` assumes all fields exist and `score` is non-null.
- Evidence truncation works for the nominal check but needs safe fallbacks for
  empty evidence/title/source edge cases.

Required fix:

- In `hydra/backend/src/hydra_api/rag_retriever.py`, keep the API contract:
  `RetrievedDocument(document_id, chunk_id, title, source, score, evidence)`.
- Convert scores to `float`.
- If score is `None` or not numeric, fail safely with `ValueError`.
- Truncate evidence to `EVIDENCE_SNIPPET_CHARS`.
- Do not expose metadata or full chunk text.
- Do not invent title/source silently if required data is missing. Either use an
  explicit fallback such as `"unknown"` for nullable DB fields or raise a safe
  error; be consistent.
- Keep `create_retriever_runnable()` importable without DB or `.env`.

Acceptance checks:

- `cd hydra/backend && uv run python -c "from hydra_api.rag_retriever import to_retrieved_document; d=to_retrieved_document({'document_id':'doc','chunk_id':'c','title':'T','source':'S','score':0.5,'content':'x'*2000}); assert d.document_id=='doc' and len(d.evidence)<2000 and isinstance(d.score, float); print('retrieved document ok')"`
- `cd hydra/backend && uv run python -c 'from hydra_api.rag_retriever import to_retrieved_document; ns=globals(); exec("try:\n    to_retrieved_document({\"document_id\":\"doc\",\"chunk_id\":\"c\",\"title\":\"T\",\"source\":\"S\",\"score\":None,\"content\":\"ev\"})\nexcept ValueError:\n    print(\"bad score rejected\")\nelse:\n    raise AssertionError(\"bad score accepted\")", ns)'`

### REPAIR-RAG-007: Harden indexing service with fakes and no partial success

Problem:

- `RagIndexingService` verification is currently shallow.
- It does not validate invalid batch/fetch limits clearly.
- It does not verify that the embedding model returns one vector per chunk.
- Cursor/connection cleanup is fragile if an exception occurs early.

Required fix:

- In `hydra/backend/src/hydra_api/rag_indexing.py`, keep
  `RagIndexingService` injectable.
- Validate constructor inputs:
  - `batch_size >= 1`;
  - `fetch_limit >= 1`.
- Validate `max_batches`, if provided, is `>= 1`.
- Fetch pending chunks using the repaired `fetch_chunks_without_embeddings()`.
- Use the repaired pending chunk key `id` when calling
  `update_chunk_embedding()`.
- For each batch, require `len(embeddings) == len(batch)`.
- Commit only after all updates in a batch succeed.
- Roll back if embedding or update fails.
- Close cursor and connection safely if they expose `.close()`.
- Do not print chunk text or embeddings.

Acceptance checks:

- `cd hydra/backend && uv run python -c "from hydra_api.rag_indexing import RagIndexingService; service=RagIndexingService(connection_factory=lambda: None, embedding_model=object()); print(service.__class__.__name__)"`
- `cd hydra/backend && uv run python -c 'from hydra_api.rag_indexing import RagIndexingService; ns=globals(); exec("for kwargs in ({\"batch_size\":0}, {\"fetch_limit\":0}):\n    try:\n        RagIndexingService(connection_factory=lambda: None, embedding_model=object(), **kwargs)\n    except ValueError:\n        pass\n    else:\n        raise AssertionError(kwargs)\nprint(\"indexing invalid constructor args rejected\")", ns)'`
- `cd hydra/backend && uv run python -c 'from hydra_api.rag_indexing import RagIndexingService; ns=globals(); exec("class Cur:\n    description=[(\"id\",),(\"document_id\",),(\"chunk_index\",),(\"content\",),(\"metadata\",)]\n    def execute(self,*a): pass\n    def fetchall(self): return []\n    def close(self): pass\nclass Conn:\n    def __init__(self): self.commits=0; self.rollbacks=0; self.closed=False\n    def cursor(self): return Cur()\n    def commit(self): self.commits+=1\n    def rollback(self): self.rollbacks+=1\n    def close(self): self.closed=True\nconn=Conn(); service=RagIndexingService(connection_factory=lambda: conn, embedding_model=object()); r=service.index(max_batches=1); assert r[\"chunks_embedded\"]==0 and conn.commits==0 and conn.closed; print(\"indexing empty batch ok\")", ns)'`

## Verification commands

Run from the workspace root that contains `hydra/`.

### Scope and safety checks

```bash
git status --short
git diff --name-only
find hydra/backend/data/raw -type f ! -name ".gitkeep"
find hydra/backend/data/metadata/documents -type f 2>/dev/null || true
find hydra -name ".env" -o -name ".env.local"
grep -RIn "neo4j" hydra/backend/src/hydra_api/rag_*.py hydra/backend/pyproject.toml || true
grep -RInE "sk-[A-Za-z0-9]|LANGFUSE_SECRET_KEY=.*[^replace_me]|MODEL_API_KEY=.*[^replace_me]" hydra/backend hydra/sdd/tasks/05-rag || true
```

Expected:

- No `hydra/frontend/**` changes.
- No `hydra/docs/**` changes.
- No real `.env` or `.env.local` files.
- No real corpus documents.
- No real model-output or embedding-output files.
- No Neo4j dependency, driver, service, or config.
- No real secrets.

### Repair-specific checks

Run the acceptance checks from each repair item.

### Original non-blocked Mission 05 checks

After repair-specific checks pass, rerun all non-blocked checks from:

- `hydra/sdd/tasks/05-rag/05-rag.md`
- `hydra/sdd/tasks/05-rag/05-rag-mission.md`
- `hydra/sdd/tasks/05-rag/validation-contract.md`

Do **not** run `TASK-RAG-018`, `TASK-RAG-019`, or `TASK-RAG-020` checks that
require real corpus, live DB embeddings, real `MODEL_API_KEY`, provider calls,
or cost approval.

## Expected final report

```markdown
## Summary
- [What was repaired]

## Repair items completed
- REPAIR-RAG-001: [result]
- REPAIR-RAG-002: [result]
- REPAIR-RAG-003: [result]
- REPAIR-RAG-004: [result]
- REPAIR-RAG-005: [result]
- REPAIR-RAG-006: [result]
- REPAIR-RAG-007: [result]

## Files changed
- `path`: [reason]

## Verification commands
- `[command]` -> [result]

## Blocked tasks
- TASK-RAG-018: still blocked unless corpus/DB/key/approval are available.
- TASK-RAG-019: still blocked unless TASK-RAG-018 is complete.
- TASK-RAG-020: still blocked unless TASK-RAG-018/019, real key, and explicit
  approval are available.

## Security check
- No real `.env` files modified.
- No secrets, headers, stack traces, full prompts, full responses, embeddings,
  or full documents logged or reported.

## Deviations or blockers
- [None / details]
```
