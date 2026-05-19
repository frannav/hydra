# Mission Brief - 06 Council y briefing

## Objetivo

Implementar el LLM council y el endpoint `POST /briefing` de HYDRA sobre el servicio RAG existente, generando briefings trazables con evidencias, limitaciones, revision de evidencia/riesgo y `trace_id`, manteniendo las operaciones reales con corpus/DB/modelos en estado bloqueado hasta que existan datos, servicios y claves aprobadas.

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
- `hydra/sdd/tasks/06-council-briefing/06-council-briefing.md`

No usar `docs/hydra-brainstorming.md` como fuente de decisiones.
Usar `docs/hydra-architecture.md` solo si la SDD anterior no es suficiente.

## Allowed files

Para tareas `pending` de esta mission:

- `hydra/backend/src/hydra_api/schemas.py`
- `hydra/backend/src/hydra_api/main.py`
- `hydra/backend/src/hydra_api/errors.py`
- `hydra/backend/src/hydra_api/briefing_config.py`
- `hydra/backend/src/hydra_api/council_prompts.py`
- `hydra/backend/src/hydra_api/council_service.py`
- `hydra/backend/src/hydra_api/briefing_service.py`

Para tareas `blocked` (`TASK-COUNCIL-008` y `TASK-BRIEF-007`):

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
- `hydra/backend/src/hydra_api/rag_store.py`, `rag_retriever.py`, `rag_indexing.py` salvo tarea RAG separada
- Archivos Neo4j o drivers de grafo
- Archivos de observabilidad/evals salvo mission 07 separada
- Cualquier archivo fuera del allowed scope de la tarea activa

## Milestones

| Milestone | Tasks | Resultado esperado |
|---|---|---|
| 1 | TASK-BRIEF-001 a TASK-BRIEF-002 | `BriefingRequest` validado y constantes obligatorias de briefing |
| 2 | TASK-COUNCIL-001 a TASK-COUNCIL-004 | Prompts de analyst, evidence reviewer, risk reviewer y final synthesizer |
| 3 | TASK-COUNCIL-005 a TASK-COUNCIL-007 | Parsers seguros, `CouncilService` inyectable y factory lazy de chains |
| 4 | TASK-BRIEF-003 a TASK-BRIEF-006 | `BriefingService` y endpoint `POST /briefing` verificables con fakes |
| 5 | TASK-COUNCIL-008 y TASK-BRIEF-007 | Bloqueado: smoke real con RAG, corpus, DB y claves |

## Checks por milestone

### Milestone 1

- `cd hydra/backend && uv run python -c "from hydra_api.schemas import BriefingRequest; assert BriefingRequest(question='q').top_k==5; assert BriefingRequest(question='q').use_council is True; print('briefing schema ok')"`
- `cd hydra/backend && uv run python -c "from hydra_api.briefing_config import MANDATORY_CORPUS_LIMITATION, REQUIRED_BRIEFING_SECTIONS; assert 'corpus' in MANDATORY_CORPUS_LIMITATION.lower(); assert REQUIRED_BRIEFING_SECTIONS; print('briefing config ok')"`

### Milestone 2

- `cd hydra/backend && uv run python -c "from hydra_api import council_prompts; print('council prompts import ok')"`
- `cd hydra/backend && uv run python -c "from hydra_api.council_prompts import build_narrative_analyst_prompt, build_evidence_reviewer_prompt, build_risk_reviewer_prompt, build_final_synthesizer_prompt; docs=[{'document_id':'doc1','chunk_id':'c1','title':'T','source':'S','score':0.9,'evidence':'ev'}]; assert 'coordinacion' in build_narrative_analyst_prompt('q', docs).lower(); assert 'unsupported_claims' in build_evidence_reviewer_prompt('draft', docs); assert 'alto' in build_risk_reviewer_prompt('draft', docs).lower(); assert 'briefing' in build_final_synthesizer_prompt('q','draft',{}, {}, docs).lower(); print('council prompts ok')"`

### Milestone 3

- `cd hydra/backend && uv run python -c "from hydra_api.council_service import normalize_risk_level, build_council_review, CouncilService; print('council service imports ok')"`
- `cd hydra/backend && uv run python -c "from hydra_api.council_service import normalize_risk_level; from hydra_api.schemas import RiskLevel; assert normalize_risk_level('critical')==RiskLevel.medio; print('risk parser ok')"`
- `cd hydra/backend && MODEL_API_KEY=fake MODEL_API_BASE_URL=https://example.invalid/v1 uv run python -c "from hydra_api.council_service import create_council_service; service=create_council_service(); assert service is not None; print('council factory ok')"`

### Milestone 4

- `cd hydra/backend && uv run python -c "from hydra_api.briefing_service import build_no_context_briefing_response, build_briefing_draft, BriefingService; print('briefing service imports ok')"`
- `cd hydra/backend && uv run python -c "from hydra_api.briefing_service import build_no_context_briefing_response; r=build_no_context_briefing_response('q','trace-local'); assert r.limitations if hasattr(r, 'limitations') else 'corpus' in r.briefing_markdown.lower(); print('no-context briefing ok')"`
- `cd hydra/backend && uv run python -c "from fastapi.testclient import TestClient; from hydra_api.main import app; assert TestClient(app).get('/health').status_code==200; print('health ok')"`
- `cd hydra/backend && uv run python -c "from fastapi.testclient import TestClient; from hydra_api.main import app; from hydra_api.schemas import BriefingResponse, CouncilReview, RiskLevel; Fake=type('Fake', (), {'brief': lambda self, request: BriefingResponse(briefing_markdown='# Briefing', risk_level=RiskLevel.medio, council_review=CouncilReview(evidence_supported=True, unsupported_claims=[], risk_review='ok'), trace_id='trace-test')}); app.state.briefing_service=Fake(); res=TestClient(app).post('/briefing', json={'question':'q','top_k':5,'use_council':True}); assert res.status_code==200 and res.json()['trace_id']=='trace-test'; del app.state.briefing_service; print('briefing fake endpoint ok')"`

### Milestone 5

No ejecutar hasta resolver bloqueos:

- corpus real aprobado;
- DB local inicializada;
- chunks persistidos con embeddings reales;
- `POST /query` real funcionando;
- `MODEL_API_KEY` real en `.env` local no versionado;
- aprobacion explicita para coste/red.

## Stop conditions

Parar y reportar si ocurre cualquiera de estas condiciones:

- Necesitas cambiar `sdd/03-api-contract.md`, `sdd/02-data-model.md` o `backend/src/hydra_api/db_schema.py`.
- La implementacion de briefing requiere un retriever paralelo al servicio RAG.
- Una verificacion de tarea `pending` requiere DB viva, corpus real, modelo real o Langfuse.
- Falta una dependencia y no esta declarada por la mission RAG.
- Aparece una API key, header, stack trace, prompt completo, respuesta completa del modelo o documento completo en logs/reportes.
- La implementacion toca frontend, Neo4j, `.env` real, evals/observabilidad o archivos fuera de allowed scope.
- `/briefing` devuelve respuesta analitica sin evidencia ni limitaciones.
- El council marca claims unsupported pero el briefing final las conserva como conclusiones.
- Se necesita un risk level distinto de `bajo`, `medio`, `alto`.

## Final report format

Al terminar, Droid debe reportar:

```markdown
## Summary
- [Cambios principales]

## Tasks completed
- TASK-BRIEF-xxx: [resultado]
- TASK-COUNCIL-xxx: [resultado]

## Files changed
- `path`: [motivo]

## Verification commands
- `[comando]` -> [resultado]

## Blocked tasks
- TASK-COUNCIL-008: [sigue bloqueada / desbloqueada con evidencia]
- TASK-BRIEF-007: [sigue bloqueada / desbloqueada con evidencia]

## Security check
- No `.env` reales modificados.
- No secretos, headers, stack traces, prompts completos ni documentos completos en logs/reportes.

## Deviations or blockers
- [Ninguno / detalles]
```
