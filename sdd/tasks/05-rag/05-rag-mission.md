# Mission Brief - 05 RAG

## Objetivo

Implementar el pipeline RAG backend de HYDRA para embeddings, retrieval con PostgreSQL + pgvector, respuesta grounded y endpoint `POST /query`, manteniendo las operaciones reales con corpus/DB/modelos en estado bloqueado hasta que existan datos y claves aprobadas.

## Source of truth

Leer antes de ejecutar:

- `hydra/sdd/README.md`
- `hydra/sdd/01-architecture-decisions.md`
- `hydra/sdd/02-data-model.md`
- `hydra/sdd/03-api-contract.md`
- `hydra/sdd/rag-pipeline.md`
- `hydra/sdd/07-implementation-plan.md`
- `hydra/sdd/08-task-checklist.md`
- `hydra/sdd/tasks/05-rag/05-rag.md`

No usar `docs/hydra-brainstorming.md` como fuente de decisiones.

## Allowed files

Para tareas `pending` de esta mission:

- `hydra/backend/pyproject.toml`
- `hydra/backend/uv.lock`
- `hydra/backend/src/hydra_api/schemas.py`
- `hydra/backend/src/hydra_api/errors.py`
- `hydra/backend/src/hydra_api/main.py`
- `hydra/backend/src/hydra_api/rag_config.py`
- `hydra/backend/src/hydra_api/rag_embeddings.py`
- `hydra/backend/src/hydra_api/rag_store.py`
- `hydra/backend/src/hydra_api/rag_indexing.py`
- `hydra/backend/src/hydra_api/rag_retriever.py`
- `hydra/backend/src/hydra_api/rag_answering.py`
- `hydra/backend/src/hydra_api/rag_service.py`

Para tareas `blocked` (`TASK-RAG-018` a `TASK-RAG-020`):

- No modificar archivos.
- Solo ejecutar comandos cuando el bloqueo este resuelto y el usuario lo apruebe.

## Forbidden files

- `hydra/frontend/**`
- `hydra/docs/hydra-brainstorming.md`
- `hydra/backend/.env`
- `hydra/frontend/.env.local`
- `hydra/backend/data/raw/**` salvo aprobacion explicita de corpus real
- `hydra/backend/data/metadata/documents/**` salvo aprobacion explicita de corpus real
- `hydra/backend/src/hydra_api/db_schema.py` salvo que Codex actualice SDD primero y apruebe el cambio
- Archivos Neo4j o drivers de grafo
- Cualquier archivo fuera del allowed scope de la tarea activa

## Milestones

| Milestone | Tasks | Resultado esperado |
|---|---|---|
| 1 | TASK-RAG-001 a TASK-RAG-003 | Dependencias RAG, constantes y validacion de `QueryRequest` |
| 2 | TASK-RAG-004 a TASK-RAG-009 | Embeddings e indexacion con dependencias inyectables y verificaciones sin red |
| 3 | TASK-RAG-010 a TASK-RAG-012 | Busqueda vectorial sobre `document_chunks` y retriever LCEL |
| 4 | TASK-RAG-013 a TASK-RAG-017 | Prompt grounded, servicio `QueryService` y endpoint `POST /query` con fake service |
| 5 | TASK-RAG-018 a TASK-RAG-020 | Bloqueado: carga/smoke real con corpus, DB y claves |

## Checks por milestone

### Milestone 1

- `cd hydra/backend && uv sync`
- `cd hydra/backend && uv run python -c "from langchain_core.runnables import RunnableLambda; from langchain_openai import ChatOpenAI, OpenAIEmbeddings; import pgvector; print('rag deps ok')"`
- `cd hydra/backend && uv run python -c "from hydra_api.rag_config import EMBEDDING_DIMENSION, DEFAULT_TOP_K; assert EMBEDDING_DIMENSION==4096 and DEFAULT_TOP_K==5; print('config ok')"`
- `cd hydra/backend && uv run python -c "from pydantic import ValidationError; from hydra_api.schemas import QueryRequest; assert QueryRequest(question='q').top_k==5; print('schema ok')"`

### Milestone 2

- `cd hydra/backend && uv run python -c "import hydra_api.rag_embeddings, hydra_api.rag_store, hydra_api.rag_indexing; print('rag indexing imports ok')"`
- `cd hydra/backend && uv run python -c "from hydra_api.rag_embeddings import validate_embedding_vector; assert len(validate_embedding_vector([0.0]*4096))==4096; print('embedding validation ok')"`
- `cd hydra/backend && uv run python -c "from hydra_api.rag_indexing import RagIndexingService; print(callable(RagIndexingService))"`

### Milestone 3

- `cd hydra/backend && uv run python -c "from hydra_api.rag_store import search_similar_chunks; from hydra_api.rag_retriever import create_retriever_runnable; print('retriever imports ok')"`
- `cd hydra/backend && uv run python -c "import inspect; from hydra_api import rag_store; src=inspect.getsource(rag_store.search_similar_chunks); assert 'document_chunks' in src and 'embedding IS NOT NULL' in src and '<=>' in src; print('pgvector sql ok')"`

### Milestone 4

- `cd hydra/backend && uv run python -c "import hydra_api.rag_answering, hydra_api.rag_service; print('answer/service imports ok')"`
- `cd hydra/backend && uv run python -c "from hydra_api.rag_service import QueryService; from hydra_api.schemas import QueryRequest; s=QueryService(retriever=lambda q,k: [], answer_chain=lambda *a, **k: 'x'); r=s.query(QueryRequest(question='q')); assert r.limitations and r.trace_id; print('service no-context ok')"`
- `cd hydra/backend && uv run python -c "from fastapi.testclient import TestClient; from hydra_api.main import app; assert TestClient(app).get('/health').status_code==200; print('health ok')"`
- `cd hydra/backend && uv run python -c "from fastapi.testclient import TestClient; from hydra_api.main import app; from hydra_api.schemas import QueryResponse; Fake=type('Fake', (), {'query': lambda self, request: QueryResponse(answer='Sin contexto suficiente.', retrieved_documents=[], limitations=['Corpus sin embeddings.'], trace_id='trace-test')}); app.state.query_service=Fake(); res=TestClient(app).post('/query', json={'question':'q','top_k':5}); assert res.status_code==200 and res.json()['trace_id']=='trace-test'; del app.state.query_service; print('query fake endpoint ok')"`

### Milestone 5

No ejecutar hasta resolver bloqueos:

- corpus real aprobado;
- DB local inicializada;
- chunks persistidos;
- `MODEL_API_KEY` real en `.env` local no versionado;
- aprobacion explicita para coste/red.

## Stop conditions

Parar y reportar si ocurre cualquiera de estas condiciones:

- Necesitas cambiar `sdd/03-api-contract.md`, `sdd/02-data-model.md` o `backend/src/hydra_api/db_schema.py`.
- Una libreria RAG obliga a crear tablas vectoriales paralelas a `document_chunks`.
- Una verificacion de tarea `pending` requiere DB viva, corpus real, modelo real o Langfuse.
- Falta una dependencia y no esta declarada en `TASK-RAG-001`.
- Aparece una API key, header, stack trace, prompt completo, respuesta completa del modelo o documento completo en logs/reportes.
- La implementacion toca frontend, Neo4j, `.env` real o archivos fuera de allowed scope.
- `/query` devuelve respuesta analitica sin evidencia ni limitaciones.
- El modelo de embeddings devuelve una dimension distinta de `4096`.

## Final report format

Al terminar, Droid debe reportar:

```markdown
## Summary
- [Cambios principales]

## Tasks completed
- TASK-RAG-xxx: [resultado]

## Files changed
- `path`: [motivo]

## Verification commands
- `[comando]` -> [resultado]

## Blocked tasks
- TASK-RAG-018: [sigue bloqueada / desbloqueada con evidencia]
- TASK-RAG-019: [sigue bloqueada / desbloqueada con evidencia]
- TASK-RAG-020: [sigue bloqueada / desbloqueada con evidencia]

## Security check
- No `.env` reales modificados.
- No secretos, headers, stack traces ni documentos completos en logs/reportes.

## Deviations or blockers
- [Ninguno / detalles]
```
