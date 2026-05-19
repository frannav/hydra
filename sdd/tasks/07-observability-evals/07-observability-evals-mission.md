# Mission Brief - 07 Observabilidad y evals

## Objetivo

Implementar observabilidad y evals del MVP de HYDRA con Langfuse Cloud como destino preferido, fallback local seguro y export JSON de resultados, manteniendo dataset real, smokes reales y llamadas externas bloqueadas hasta tener corpus, DB, modelos, claves y aprobacion explicita.

## Source of truth

Leer antes de ejecutar:

- `hydra/sdd/README.md`
- `hydra/sdd/01-architecture-decisions.md`
- `hydra/sdd/02-data-model.md`
- `hydra/sdd/03-api-contract.md`
- `hydra/sdd/rag-pipeline.md`
- `hydra/sdd/evals-observability.md`
- `hydra/sdd/07-implementation-plan.md`
- `hydra/sdd/08-task-checklist.md`
- `hydra/sdd/tasks/05-rag/05-rag.md`
- `hydra/sdd/tasks/06-council-briefing/06-council-briefing.md`
- `hydra/sdd/tasks/07-observability-evals/07-observability-evals.md`

No usar `docs/hydra-brainstorming.md` como fuente de decisiones.
Usar `docs/hydra-architecture.md` solo si la SDD anterior no es suficiente.

## Allowed files

Para tareas `pending` de esta mission:

- `hydra/backend/pyproject.toml`
- `hydra/backend/uv.lock`
- `hydra/backend/src/hydra_api/schemas.py`
- `hydra/backend/src/hydra_api/errors.py`
- `hydra/backend/src/hydra_api/main.py`
- `hydra/backend/src/hydra_api/observability.py`
- `hydra/backend/src/hydra_api/rag_service.py`
- `hydra/backend/src/hydra_api/rag_answering.py`
- `hydra/backend/src/hydra_api/briefing_service.py`
- `hydra/backend/src/hydra_api/council_service.py`
- `hydra/backend/src/hydra_api/evals_config.py`
- `hydra/backend/src/hydra_api/evals_metrics.py`
- `hydra/backend/src/hydra_api/evals_judges.py`
- `hydra/backend/src/hydra_api/evals_service.py`
- `hydra/backend/data/outputs/.gitkeep`
- `hydra/backend/data/outputs/eval_results.json`

Para tareas `blocked`:

- `TASK-OBS-008`: no modificar archivos; solo verificacion operativa con aprobacion.
- `TASK-EVAL-014`: `hydra/backend/data/evals/eval_cases.json` cuando haya corpus aprobado.
- `TASK-EVAL-015`: `hydra/backend/data/outputs/eval_results.json` cuando haya corpus/DB/modelos/claves aprobados.

## Forbidden files

- `hydra/frontend/**`
- `hydra/docs/hydra-brainstorming.md`
- `hydra/backend/.env`
- `hydra/frontend/.env.local`
- `hydra/backend/data/raw/**` salvo aprobacion explicita de corpus real
- `hydra/backend/data/metadata/documents/**` salvo aprobacion explicita de corpus real
- `hydra/backend/src/hydra_api/db_schema.py` salvo que Codex actualice SDD primero y apruebe el cambio
- `hydra/backend/ontology/hydra_ontology.yaml` salvo task separada de ontologia
- Archivos Neo4j o drivers de grafo
- Archivos frontend o upload opcional
- Cualquier archivo fuera del allowed scope de la tarea activa

## Milestones

| Milestone | Tasks | Resultado esperado |
|---|---|---|
| 1 | TASK-OBS-001 a TASK-OBS-004 | SDK Langfuse, helpers seguros, trace local y emitter lazy con fallback |
| 2 | TASK-OBS-005 a TASK-OBS-007 | `/query`, generacion RAG, `/briefing` y council instrumentados con fakes |
| 3 | TASK-EVAL-001 a TASK-EVAL-008 | Validaciones, paths, loader y metricas offline deterministas |
| 4 | TASK-EVAL-009 a TASK-EVAL-013 | Judge inyectable, EvalService, export JSON, endpoints y scores fake/local |
| 5 | TASK-OBS-008, TASK-EVAL-014 y TASK-EVAL-015 | Bloqueado: Langfuse real, dataset real y evals reales |

## Checks por milestone

### Milestone 1

- `cd hydra/backend && uv sync`
- `cd hydra/backend && uv run python -c "import langfuse; print('langfuse import ok')"`
- `cd hydra/backend && uv run python -c "from hydra_api.observability import safe_preview, generate_local_trace_id; assert safe_preview('a'*1000, 10).endswith('...'); assert generate_local_trace_id().startswith('local-'); print('observability helpers ok')"`
- `cd hydra/backend && uv run python -c "from hydra_api.observability import create_observability_emitter; E=create_observability_emitter(settings=type('S',(),{'langfuse_public_key':'','langfuse_secret_key':'','langfuse_base_url':''})()); t=E.start_trace('query', {}); assert t.trace_id.startswith('local-'); print('local emitter ok')"`

### Milestone 2

- `cd hydra/backend && uv run python -c "from hydra_api.rag_service import QueryService; from hydra_api.schemas import QueryRequest; E=type('E',(),{'start_trace':lambda self,*a,**k: type('T',(),{'trace_id':'trace-test','metadata':{}})(), 'event':lambda self,*a,**k: None, 'score':lambda self,*a,**k: None}); s=QueryService(retriever=lambda q,k: [], answer_chain=lambda *a, **k: 'unused', emitter=E()); r=s.query(QueryRequest(question='q')); assert r.trace_id=='trace-test'; print('query trace ok')"`
- `cd hydra/backend && uv run python -c "from hydra_api.briefing_service import BriefingService; print('briefing observability imports ok')"`
- `cd hydra/backend && uv run python -c "from hydra_api.council_service import build_council_review; print('council observability imports ok')"`

### Milestone 3

- `cd hydra/backend && uv run python -c "from pydantic import ValidationError; from hydra_api.schemas import EvalRunRequest; assert EvalRunRequest(case_ids=['eval_001']).top_k==5; print('eval request ok')"`
- `cd hydra/backend && uv run python -c "from hydra_api.evals_config import EVAL_CASES_PATH, EVAL_RESULTS_PATH; assert 'data/evals/eval_cases.json' in EVAL_CASES_PATH; assert 'data/outputs/eval_results.json' in EVAL_RESULTS_PATH; print('eval paths ok')"`
- `cd hydra/backend && uv run python -c "import json, tempfile, pathlib; from hydra_api.evals_service import load_eval_cases; data=[{'id':'eval_001','question':'q','expected_documents':['doc_001'],'expected_topics':['topic'],'expected_answer_traits':['trait'],'tags':['smoke']}]; base=pathlib.Path('data/evals'); base.mkdir(parents=True, exist_ok=True); d=tempfile.TemporaryDirectory(dir=base); p=pathlib.Path(d.name)/'eval_cases.json'; p.write_text(json.dumps(data)); cases=load_eval_cases(p); assert cases[0].id=='eval_001'; print('eval cases loader ok')"`
- `cd hydra/backend && uv run python -c "from hydra_api.evals_metrics import precision_at_k, coordination_caution; assert precision_at_k(['doc_1'], [{'document_id':'doc_1'}], 5)==1.0; assert coordination_caution('Hubo coordinacion.', []).passed is False; print('eval metrics ok')"`

### Milestone 4

- `cd hydra/backend && uv run python -c "from hydra_api.evals_judges import parse_groundedness_label; assert parse_groundedness_label('PASS')=='pass'; print('groundedness parser ok')"`
- `cd hydra/backend && uv run python -c "from hydra_api.evals_service import EvalService; print('eval service import ok')"`
- `cd hydra/backend && uv run python -c "import tempfile, pathlib, json; from hydra_api.evals_service import export_eval_results; run=type('Run',(),{'run_id':'eval_run_test','results':[]})(); base=pathlib.Path('data/outputs'); base.mkdir(parents=True, exist_ok=True); d=tempfile.TemporaryDirectory(dir=base); p=pathlib.Path(d.name)/'eval_results.json'; export_eval_results(run, p); data=json.loads(p.read_text()); assert data['run_id']=='eval_run_test'; print('eval export ok')"`
- `cd hydra/backend && uv run python -c "from fastapi.testclient import TestClient; from hydra_api.main import app; assert TestClient(app).get('/health').status_code==200; print('health ok')"`
- `cd hydra/backend && uv run python -c "from fastapi.testclient import TestClient; from hydra_api.main import app; Fake=type('Fake',(),{'run':lambda self, req: type('Run',(),{'run_id':'eval_run_001','results_path':'hydra/backend/data/outputs/eval_results.json','trace_id':'trace-eval','results':[]})()}); app.state.eval_service=Fake(); res=TestClient(app).post('/evals/run', json={'case_ids':['eval_001'],'top_k':5}); assert res.status_code==200; del app.state.eval_service; print('eval endpoint fake ok')"`

### Milestone 5

No ejecutar hasta resolver bloqueos:

- corpus real aprobado con IDs estables;
- DB local inicializada;
- chunks persistidos con embeddings reales;
- `POST /query` y `POST /briefing` reales funcionando;
- `MODEL_API_KEY`, `LANGFUSE_PUBLIC_KEY` y `LANGFUSE_SECRET_KEY` reales en `.env` local no versionado;
- aprobacion explicita para coste/red;
- aprobacion para versionar `eval_cases.json` real si procede.

## Stop conditions

Parar y reportar si ocurre cualquiera de estas condiciones:

- Necesitas cambiar `sdd/03-api-contract.md`, `sdd/02-data-model.md`, `sdd/evals-observability.md` o `backend/src/hydra_api/db_schema.py`.
- Una verificacion de tarea `pending` requiere DB viva, corpus real, modelo real, embeddings reales o Langfuse real.
- Falta corpus aprobado para crear `eval_cases.json` real.
- Falta una dependencia y no esta declarada por la tarea activa.
- Aparece una API key, header, stack trace, prompt completo, respuesta completa del modelo o documento completo en logs/reportes/traces/results.
- La implementacion toca frontend, Neo4j, `.env` real, documentos reales o archivos fuera de allowed scope.
- `/query`, `/briefing` o `/evals/run` devuelven errores con detalles internos.
- El fallback local no puede producir `trace_id`.
- Los evals crean un pipeline paralelo de retrieval/briefing en vez de reutilizar servicios existentes.

## Final report format

Al terminar, Droid debe reportar:

```markdown
## Summary
- [Cambios principales]

## Tasks completed
- TASK-OBS-xxx: [resultado]
- TASK-EVAL-xxx: [resultado]

## Files changed
- `path`: [motivo]

## Verification commands
- `[comando]` -> [resultado]

## Blocked tasks
- TASK-OBS-008: [sigue bloqueada / desbloqueada con evidencia]
- TASK-EVAL-014: [sigue bloqueada / desbloqueada con evidencia]
- TASK-EVAL-015: [sigue bloqueada / desbloqueada con evidencia]

## Security check
- No `.env` reales modificados.
- No secretos, headers, stack traces, prompts completos, respuestas completas ni documentos completos en logs/reportes/traces/results.

## Deviations or blockers
- [Ninguno / detalles]
```
