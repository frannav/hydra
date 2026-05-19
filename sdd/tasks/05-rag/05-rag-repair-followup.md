# Follow-up Repair Packet — Mission 05 RAG Repair

Task:
Repair the remaining blockers found while reviewing the completed
`05-rag-repair.md` implementation. This is a **repair of the repair**, not a
new RAG feature.

Review verdict:
The Mission 05 repair is **not accepted yet**. All official checks passed, but
two deeper repair requirements still fail:

1. `fetch_chunks_without_embeddings()` does not normalize/reject `metadata`.
2. `POST /query` can return plain FastAPI `Internal Server Error` when the real
   lazy service cannot be constructed.

## Source of truth

- `hydra/sdd/README.md`
- `hydra/sdd/01-architecture-decisions.md`
- `hydra/sdd/02-data-model.md`
- `hydra/sdd/03-api-contract.md`
- `hydra/sdd/rag-pipeline.md`
- `hydra/sdd/tasks/05-rag/05-rag.md`
- `hydra/sdd/tasks/05-rag/05-rag-repair.md`
- Existing DB schema in `hydra/backend/src/hydra_api/db_schema.py`
- Existing canonical schemas in `hydra/backend/src/hydra_api/schemas.py`

## Mission mode

- This is a **minimal follow-up repair**.
- Do not add features.
- Do not change API contracts, schemas, tables, env var names, models, or
  embedding dimension.
- Do not call real LLM providers, embedding providers, Langfuse, network, or a
  live DB in verification.
- Keep `TASK-RAG-018` to `TASK-RAG-020` blocked.
- Do not mark SDD tasks as `done`; Codex/reviewer will do that after
  acceptance.
- Do not commit.

## Allowed files

Primary repair files:

- `hydra/backend/src/hydra_api/main.py`
- `hydra/backend/src/hydra_api/rag_store.py`

Read-only context files:

- `hydra/backend/src/hydra_api/errors.py`
- `hydra/backend/src/hydra_api/rag_service.py`
- `hydra/backend/src/hydra_api/schemas.py`
- `hydra/backend/src/hydra_api/db_schema.py`

## Forbidden

- Do not modify `hydra/frontend/**`.
- Do not modify `hydra/docs/**`.
- Do not modify unrelated `hydra/sdd/**` files.
- Do not modify `hydra/backend/pyproject.toml` or `hydra/backend/uv.lock`.
- Do not create or edit real `.env` files.
- Do not add real corpus documents, metadata, model outputs, or embeddings.
- Do not introduce Neo4j, graph drivers, observability, evals, briefing, or
  frontend upload logic.
- Do not print API keys, headers, full prompts, full responses, embeddings,
  stack traces, DB DSNs, or full documents.

## Repair items

### REPAIR-RAG-FOLLOWUP-001: Normalize and validate pending chunk metadata

Problem:

- `fetch_chunks_without_embeddings()` currently returns `metadata=None` when
  the row metadata is null.
- It also accepts metadata values that are not dictionaries, for example a
  string.
- This violates the original `TASK-RAG-007` edge case and the repair packet:
  metadata must be normalized safely or fail clearly.

Required fix:

- In `hydra/backend/src/hydra_api/rag_store.py`, after fetching rows:
  - convert each row to a dict with keys:
    `id`, `document_id`, `chunk_index`, `content`, `metadata`;
  - if `metadata is None`, set it to `{}`;
  - if `metadata` is not a `dict`, raise a safe `ValueError`;
  - do not include full chunk content in the error message;
  - keep `limit >= 1` validation before SQL;
  - keep `ORDER BY document_id, chunk_index`;
  - keep SQL parameterized.

Acceptance checks:

- `cd hydra/backend && uv run python -c 'from hydra_api.rag_store import fetch_chunks_without_embeddings; ns=globals(); exec("class C:\n    description=[(\"id\",),(\"document_id\",),(\"chunk_index\",),(\"content\",),(\"metadata\",)]\n    def execute(self,*a): pass\n    def fetchall(self): return [(\"c\",\"d\",0,\"text\",None)]\nrows=fetch_chunks_without_embeddings(C(),1); assert rows[0][\"metadata\"]=={}; print(\"metadata none normalized\")", ns)'`
- `cd hydra/backend && uv run python -c 'from hydra_api.rag_store import fetch_chunks_without_embeddings; ns=globals(); exec("class C:\n    description=[(\"id\",),(\"document_id\",),(\"chunk_index\",),(\"content\",),(\"metadata\",)]\n    def execute(self,*a): pass\n    def fetchall(self): return [(\"c\",\"d\",0,\"text\",\"bad\")]\ntry:\n    fetch_chunks_without_embeddings(C(),1)\nexcept ValueError:\n    print(\"metadata non-dict rejected\")\nelse:\n    raise AssertionError(\"metadata non-dict accepted\")", ns)'`
- `cd hydra/backend && uv run python -c "import inspect; from hydra_api import rag_store; src=inspect.getsource(rag_store.fetch_chunks_without_embeddings); assert 'metadata is None' in src and 'isinstance(metadata, dict)' in src; print('metadata handling present')"`

### REPAIR-RAG-FOLLOWUP-002: Return safe HYDRA JSON errors when lazy `/query` service setup fails

Problem:

- `main.query()` constructs the real service before entering the `try` block.
- If `MODEL_API_KEY` or another required setting is missing, FastAPI returns
  plain text `Internal Server Error` instead of HYDRA's safe error envelope:

```json
{
  "error": {
    "code": "...",
    "message": "...",
    "details": {}
  }
}
```

Required fix:

- In `hydra/backend/src/hydra_api/main.py`, move lazy service construction
  inside safe error handling.
- Preserve fake injection via `app.state.query_service`.
- If no fake exists:
  - construct the real service lazily at request time;
  - cache it in `app.state.query_service` only after successful construction;
  - do not call DB/model providers during app import or `/health`.
- Map expected configuration/runtime setup failures to a safe `HTTPException`
  or `HydraError` handled by the existing error handlers.
- The response body must use the existing HYDRA error envelope.
- Do not expose stack traces, exception reprs, headers, keys, prompts, DB DSNs,
  or provider internals.
- Update the stale route docstring if needed; it must not claim the route
  returns 503 merely because no fake is injected.

Acceptance checks:

- `cd hydra/backend && uv run python -c "from fastapi.testclient import TestClient; from hydra_api.main import app; assert TestClient(app).get('/health').json()['status']=='ok'; print('health ok')"`
- `cd hydra/backend && uv run python -c "from fastapi.testclient import TestClient; from hydra_api.main import app; from hydra_api.schemas import QueryResponse; Fake=type('Fake', (), {'query': lambda self, request: QueryResponse(answer='Sin contexto suficiente.', retrieved_documents=[], limitations=['Corpus sin embeddings.'], trace_id='trace-test')}); app.state.query_service=Fake(); res=TestClient(app).post('/query', json={'question':'q','top_k':5}); assert res.status_code==200 and res.json()['trace_id']=='trace-test'; del app.state.query_service; print('query fake endpoint ok')"`
- `cd hydra/backend && uv run python -c "from fastapi.testclient import TestClient; from hydra_api.main import app; app.state.__dict__.pop('query_service', None); client=TestClient(app, raise_server_exceptions=False); res=client.post('/query', json={'question':'q','top_k':5}); body=res.json(); assert res.status_code in (500,503); assert 'error' in body and 'Internal Server Error' not in res.text; assert body['error']['message']; print('query setup error envelope ok')"`
- `cd hydra/backend && MODEL_API_KEY=fake MODEL_API_BASE_URL=https://example.invalid/v1 uv run python -c "from fastapi.testclient import TestClient; from hydra_api.main import app; app.state.__dict__.pop('query_service', None); client=TestClient(app, raise_server_exceptions=False); res=client.post('/query', json={'question':'q','top_k':5}); body=res.json(); assert res.status_code in (500,503); assert 'error' in body; assert 'example.invalid' not in res.text and 'fake' not in res.text; print('query runtime error envelope safe')"`
- `cd hydra/backend && uv run python -c "import inspect; from hydra_api import main; src=inspect.getsource(main.query); assert 'create_query_service' in src and 'app.state.query_service' in src and 'try:' in src; print('query lazy safe handler present')"`

## Verification commands

Run from the workspace root that contains `hydra/`.

### Follow-up repair checks

Run all acceptance checks from `REPAIR-RAG-FOLLOWUP-001` and
`REPAIR-RAG-FOLLOWUP-002`.

### Regression checks from previous repair

At minimum rerun:

```bash
cd hydra/backend && uv run python -c "from hydra_api.rag_service import QueryService; from hydra_api.schemas import QueryRequest; called={'n':0}; s=QueryService(retriever=lambda q,k: [], answer_chain=lambda prompt: called.__setitem__('n', called['n']+1)); r=s.query(QueryRequest(question='q')); assert called['n']==0 and r.retrieved_documents==[] and r.limitations and r.trace_id.startswith('trace-local-'); print('no-context skips model ok')"
cd hydra/backend && uv run python -c "from hydra_api.rag_answering import build_answer_prompt; p=build_answer_prompt('q', [{'evidence':'ev','document_id':'doc','chunk_id':'c','title':'T','source':'S','score':0.9}]); assert 'coordinacion' in p.lower() and 'ev' in p and 'doc' in p and 'c' in p; print('grounded prompt dict ok')"
cd hydra/backend && uv run python -c "from hydra_api.rag_store import fetch_chunks_without_embeddings, search_similar_chunks, update_chunk_embedding; print(callable(fetch_chunks_without_embeddings) and callable(search_similar_chunks) and callable(update_chunk_embedding))"
cd hydra/backend && uv run python -m compileall -q src
```

### Safety checks

```bash
git status --short
git diff --name-only HEAD~1..HEAD
find hydra -name ".env" -o -name ".env.local"
find hydra/backend/data/raw -type f ! -name ".gitkeep"
find hydra/backend/data/metadata/documents -type f 2>/dev/null || true
grep -RIn "neo4j" hydra/backend/src/hydra_api/rag_*.py hydra/backend/pyproject.toml || true
```

Expected:

- Only `hydra/backend/src/hydra_api/main.py` and
  `hydra/backend/src/hydra_api/rag_store.py` need changes.
- No frontend/docs/dependency/lockfile changes.
- No real `.env` files, real corpus files, real metadata documents, or Neo4j.

## Expected final report

```markdown
## Summary
- [What was repaired]

## Repair items completed
- REPAIR-RAG-FOLLOWUP-001: [result]
- REPAIR-RAG-FOLLOWUP-002: [result]

## Files changed
- `backend/src/hydra_api/main.py`: [reason]
- `backend/src/hydra_api/rag_store.py`: [reason]

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
