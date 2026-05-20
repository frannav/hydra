# Repair - Mission 07 Observabilidad y evals

## Objetivo

Corregir los bloqueantes detectados en la revisión de Mission 07 para que observabilidad y evals queden aceptables en modo MVP local: sin DB viva, sin corpus real, sin modelos reales, sin Langfuse real y sin red externa.

## Veredicto de revisión

Mission 07 **no queda aprobada** hasta aplicar este repair.

La implementación actual tiene helpers útiles y varios checks locales pasan, pero todavía rompe verificaciones SDD y deja el runner de evals desconectado de export, paths seguros, `top_k`, errores controlados y Langfuse lazy.

## Source of truth

Antes de ejecutar este repair, leer:

- `hydra/sdd/README.md`
- `hydra/sdd/01-architecture-decisions.md`
- `hydra/sdd/03-api-contract.md`
- `hydra/sdd/evals-observability.md`
- `hydra/sdd/07-implementation-plan.md`
- `hydra/sdd/08-task-checklist.md`
- `hydra/sdd/tasks/07-observability-evals/07-observability-evals.md`
- `hydra/sdd/tasks/07-observability-evals/07-observability-evals-mission.md`

No usar `docs/hydra-brainstorming.md`.
Usar `docs/hydra-architecture.md` solo si la SDD anterior no basta.

## Archivos permitidos

Solo estos archivos pueden modificarse:

- `hydra/backend/src/hydra_api/schemas.py`
- `hydra/backend/src/hydra_api/errors.py`
- `hydra/backend/src/hydra_api/main.py`
- `hydra/backend/src/hydra_api/observability.py`
- `hydra/backend/src/hydra_api/rag_service.py`
- `hydra/backend/src/hydra_api/briefing_service.py`
- `hydra/backend/src/hydra_api/evals_config.py`
- `hydra/backend/src/hydra_api/evals_metrics.py`
- `hydra/backend/src/hydra_api/evals_judges.py`
- `hydra/backend/src/hydra_api/evals_service.py`
- `hydra/backend/data/outputs/.gitkeep`
- `hydra/backend/data/outputs/eval_results.json` solo si lo crea una verificación fake/local

## Archivos prohibidos

- `hydra/frontend/**`
- `.env`, `.env.local` o cualquier archivo con secretos reales
- `hydra/backend/data/raw/**`
- `hydra/backend/data/metadata/documents/**`
- `hydra/backend/data/evals/eval_cases.json` mientras TASK-EVAL-014 siga bloqueada
- `hydra/backend/src/hydra_api/db_schema.py`
- `hydra/backend/ontology/hydra_ontology.yaml`
- Neo4j, graph sinks, upload frontend o docs históricos

## Bloqueantes a corregir

1. `backend/src/hydra_api/evals_config.py` está sin versionar, pero módulos versionados lo importan.
2. `EVAL_CASES_PATH` y `EVAL_RESULTS_PATH` no respetan el contrato público `hydra/backend/data/...`.
3. El check SDD de `POST /evals/run` con fake falla con `ResponseValidationError` porque el fake no trae `total_cases` y el endpoint devuelve el objeto directamente.
4. `EvalService.run()` propaga `request.top_k` al query, pero calcula `precision_at_k` con `self._top_k`, ignorando el `top_k` solicitado.
5. `EvalService.run()` silencia `case_ids` inexistentes y puede devolver `total_cases=0` sin error.
6. `EvalService.run()` devuelve `results_path`, pero no llama a `export_eval_results()`, por lo que `/evals/results` no queda conectado al run.
7. `EvalService._compute_metrics()` valida siempre respuestas RAG naturales contra `Extraction`; luego `_determine_passed()` exige `json_validity=True`, haciendo fallar evals donde JSON validity no aplica.
8. `load_eval_cases()` permite leer desde cualquier subdirectorio de `data/`; debe limitarse a `data/evals/`.
9. `export_eval_results()` permite escribir en cualquier subdirectorio de `data/`; debe limitarse a `data/outputs/`.
10. `QueryService` y `BriefingService` usan `_LocalEmitter` directamente cuando no se inyecta emitter; con Langfuse configurado no se cablea `create_observability_emitter()`.

## Reglas de repair

- No cambiar el contrato de `POST /query`, `POST /briefing`, `POST /evals/run` ni `GET /evals/results`.
- No crear dataset real `eval_cases.json`.
- No ejecutar evals reales.
- No llamar DB viva, modelos reales, embeddings reales, Langfuse Cloud ni red externa.
- Mantener todo lazy: ningún cliente de DB/modelo/Langfuse en import time.
- Mantener inyección de fakes mediante `app.state.*`.
- No exponer paths absolutos, headers, stack traces, prompts completos, respuestas completas, documentos completos ni secretos.
- Si un error es esperado por input o datos faltantes, devolver error seguro y controlado.

## TASK-REPAIR-07-001: Versionar y corregir configuración de evals

Estado: pending
Prioridad: must

Objetivo:
Hacer que `evals_config.py` forme parte de la implementación y que sus constantes respeten el contrato público sin romper resolución local desde repo root o desde `hydra/backend`.

Archivos permitidos:

- `hydra/backend/src/hydra_api/evals_config.py`
- `hydra/backend/src/hydra_api/evals_service.py`

Requisitos:

- Asegurar que `backend/src/hydra_api/evals_config.py` queda incluido en el diff final.
- Definir:
  - `DEFAULT_EVAL_TOP_K = 5`
  - `EVAL_CASES_PATH = "hydra/backend/data/evals/eval_cases.json"`
  - `EVAL_RESULTS_PATH = "hydra/backend/data/outputs/eval_results.json"`
- Crear helpers internos seguros para resolver paths de disco desde:
  - repo root;
  - `hydra/backend`;
  - paths temporales bajo `data/evals/` y `data/outputs/` usados por verificaciones.
- No crear archivos ni directorios en import time.

Criterios de aceptación:

- `evals_config.py` importa sin `.env`.
- Las constantes públicas coinciden con el contrato.
- Los loaders/exporters siguen funcionando desde `hydra/backend`.

Comandos de verificación:

```bash
cd hydra/backend && uv run python -c "from hydra_api.evals_config import DEFAULT_EVAL_TOP_K, EVAL_CASES_PATH, EVAL_RESULTS_PATH; assert DEFAULT_EVAL_TOP_K==5; assert EVAL_CASES_PATH=='hydra/backend/data/evals/eval_cases.json'; assert EVAL_RESULTS_PATH=='hydra/backend/data/outputs/eval_results.json'; print('eval config contract ok')"
cd hydra && git status --short backend/src/hydra_api/evals_config.py
```

## TASK-REPAIR-07-002: Restringir paths de loader y export

Estado: pending
Prioridad: must

Objetivo:
Impedir lectura/escritura fuera de los directorios permitidos para evals.

Archivos permitidos:

- `hydra/backend/src/hydra_api/evals_service.py`

Requisitos:

- `load_eval_cases(path)` solo puede leer bajo `hydra/backend/data/evals/`.
- `export_eval_results(run, path)` solo puede escribir bajo `hydra/backend/data/outputs/`.
- Rechazar rutas absolutas no controladas y cualquier path con `..`.
- Los errores deben ser seguros: sin paths absolutos ni stack traces.
- Mantener fixtures temporales dentro de `data/evals/` y `data/outputs/`.

Criterios de aceptación:

- Loader acepta fixture temporal bajo `data/evals/`.
- Loader rechaza fixture bajo `data/outputs/`.
- Export acepta destino temporal bajo `data/outputs/`.
- Export rechaza destino bajo `data/evals/`.

Comandos de verificación:

```bash
cd hydra/backend && uv run python -c "import json, tempfile, pathlib; from hydra_api.evals_service import load_eval_cases; base=pathlib.Path('data/evals'); base.mkdir(parents=True, exist_ok=True); d=tempfile.TemporaryDirectory(dir=base); p=pathlib.Path(d.name)/'eval_cases.json'; p.write_text(json.dumps([{'id':'eval_001','question':'q','expected_documents':['doc_001'],'expected_topics':['topic'],'expected_answer_traits':['trait'],'tags':['smoke']}])); assert load_eval_cases(p)[0].id=='eval_001'; d.cleanup(); print('eval loader allowed dir ok')"
cd hydra/backend && uv run python -c "import json, tempfile, pathlib; from hydra_api.evals_service import load_eval_cases; base=pathlib.Path('data/outputs'); base.mkdir(parents=True, exist_ok=True); d=tempfile.TemporaryDirectory(dir=base); p=pathlib.Path(d.name)/'eval_cases.json'; p.write_text(json.dumps([{'id':'eval_001','question':'q','expected_documents':['doc_001'],'expected_topics':['topic'],'expected_answer_traits':['trait'],'tags':['smoke']}])); ok=False\ntry: load_eval_cases(p)\nexcept Exception: ok=True\nassert ok; d.cleanup(); print('eval loader rejects outputs ok')"
cd hydra/backend && uv run python -c "import tempfile, pathlib, json; from hydra_api.evals_service import export_eval_results; run=type('Run',(),{'run_id':'eval_run_test','results':[]})(); base=pathlib.Path('data/outputs'); base.mkdir(parents=True, exist_ok=True); d=tempfile.TemporaryDirectory(dir=base); p=pathlib.Path(d.name)/'eval_results.json'; export_eval_results(run, p); assert json.loads(p.read_text())['run_id']=='eval_run_test'; d.cleanup(); print('eval export allowed dir ok')"
cd hydra/backend && uv run python -c "import tempfile, pathlib; from hydra_api.evals_service import export_eval_results; run=type('Run',(),{'run_id':'eval_run_test','results':[]})(); base=pathlib.Path('data/evals'); base.mkdir(parents=True, exist_ok=True); d=tempfile.TemporaryDirectory(dir=base); p=pathlib.Path(d.name)/'eval_results.json'; ok=False\ntry: export_eval_results(run, p)\nexcept Exception: ok=True\nassert ok; d.cleanup(); print('eval export rejects evals dir ok')"
```

## TASK-REPAIR-07-003: Corregir `EvalService.run()` con IDs, top_k y export

Estado: pending
Prioridad: must

Objetivo:
Hacer que el runner ejecute exactamente los casos solicitados, use `top_k` correctamente y escriba el backup local JSON.

Archivos permitidos:

- `hydra/backend/src/hydra_api/evals_service.py`
- `hydra/backend/src/hydra_api/errors.py` solo si se necesita error tipado seguro

Requisitos:

- Preservar el orden de `request.case_ids`.
- Rechazar IDs duplicados o deduplicarlos explícitamente con comportamiento documentado. Preferencia: rechazar duplicados con error seguro.
- Si algún `case_id` solicitado no existe, fallar con error seguro antes de ejecutar queries.
- Usar `request.top_k` tanto en `QueryRequest` como en `precision_at_k`.
- Llamar a `export_eval_results(run)` antes de devolver `EvalRunResponse`.
- Si export falla, devolver error seguro; no marcar el run como exitoso.
- Mantener `run_id` seguro y único.

Criterios de aceptación:

- `top_k=1` afecta Precision@k.
- Caso inexistente falla.
- Run fake crea `hydra/backend/data/outputs/eval_results.json`.

Comandos de verificación:

```bash
cd hydra/backend && uv run python -c "from hydra_api.evals_service import EvalService; from hydra_api.schemas import EvalCase, QueryResponse, RetrievedDocument, EvalRunRequest; cases=[EvalCase(id='eval_001', question='q', expected_documents=['doc_1'], expected_topics=[], expected_answer_traits=[], tags=[])]; docs=[RetrievedDocument(document_id='doc_2', chunk_id='c2', title='T', source='S', score=0.9, evidence='ev2'), RetrievedDocument(document_id='doc_1', chunk_id='c1', title='T', source='S', score=0.8, evidence='ev1')]; Q=type('Q',(),{'query':lambda self, req: QueryResponse(answer='respuesta analitica', retrieved_documents=docs, limitations=[], trace_id='trace-q')}); svc=EvalService(case_loader=lambda: cases, query_service=Q(), judge=lambda *a, **k:'pass'); run=svc.run(EvalRunRequest(case_ids=['eval_001'], top_k=1)); assert run.results[0].metrics.precision_at_k==0.0; print('eval service request top_k precision ok')"
cd hydra/backend && uv run python -c "from hydra_api.evals_service import EvalService; from hydra_api.schemas import EvalCase, QueryResponse, EvalRunRequest; cases=[EvalCase(id='eval_001', question='q', expected_documents=['doc_1'], expected_topics=[], expected_answer_traits=[], tags=[])]; Q=type('Q',(),{'query':lambda self, req: QueryResponse(answer='a', retrieved_documents=[], limitations=[], trace_id='trace-q')}); svc=EvalService(case_loader=lambda: cases, query_service=Q(), judge=lambda *a, **k:'pass'); ok=False\ntry: svc.run(EvalRunRequest(case_ids=['missing'], top_k=5))\nexcept Exception: ok=True\nassert ok; print('eval service missing case rejected ok')"
cd hydra/backend && uv run python -c "import pathlib, json; from hydra_api.evals_service import EvalService; from hydra_api.schemas import EvalCase, QueryResponse, EvalRunRequest; p=pathlib.Path('data/outputs/eval_results.json'); p.unlink(missing_ok=True); cases=[EvalCase(id='eval_001', question='q', expected_documents=['doc_1'], expected_topics=[], expected_answer_traits=[], tags=[])]; Q=type('Q',(),{'query':lambda self, req: QueryResponse(answer='respuesta analitica', retrieved_documents=[], limitations=[], trace_id='trace-q')}); svc=EvalService(case_loader=lambda: cases, query_service=Q(), judge=lambda *a, **k:'warning'); run=svc.run(EvalRunRequest(case_ids=['eval_001'], top_k=5)); assert p.exists(); data=json.loads(p.read_text()); assert data['run_id']==run.run_id; p.unlink(missing_ok=True); print('eval service export side effect ok')"
```

## TASK-REPAIR-07-004: Hacer JSON validity aplicable solo cuando corresponde

Estado: pending
Prioridad: must

Objetivo:
Evitar que evals normales de `/query` fallen por no ser JSON cuando el caso no está evaluando una extracción JSON.

Archivos permitidos:

- `hydra/backend/src/hydra_api/evals_service.py`
- `hydra/backend/src/hydra_api/evals_metrics.py`
- `hydra/backend/src/hydra_api/schemas.py` solo si se añade campo opcional compatible

Requisitos:

- No eliminar `EvalMetrics.json_validity`.
- JSON validity debe ejecutarse solo si el caso lo pide explícitamente mediante tag controlado, por ejemplo:
  - `json_validity`
  - `extraction_json`
  - `ontology_mapping`
- Para casos RAG normales, dejar `json_validity=True` como valor compatible/no aplicable y no usarlo para fallar.
- Ontology mapping debe ejecutarse solo cuando haya payload de extracción validable, no sobre texto natural.
- No cambiar el contrato público de `/evals/results`.

Criterios de aceptación:

- Respuesta natural con judge `pass` y coordination caution OK puede pasar si precision aplica.
- Caso marcado como `json_validity` falla con JSON inválido.

Comandos de verificación:

```bash
cd hydra/backend && uv run python -c "from hydra_api.evals_service import EvalService; from hydra_api.schemas import EvalCase, QueryResponse, RetrievedDocument, EvalRunRequest; cases=[EvalCase(id='eval_001', question='q', expected_documents=['doc_1'], expected_topics=[], expected_answer_traits=[], tags=[])]; docs=[RetrievedDocument(document_id='doc_1', chunk_id='c1', title='T', source='S', score=0.9, evidence='ev')]; Q=type('Q',(),{'query':lambda self, req: QueryResponse(answer='Respuesta analitica no JSON.', retrieved_documents=docs, limitations=[], trace_id='trace-q')}); svc=EvalService(case_loader=lambda: cases, query_service=Q(), judge=lambda *a, **k:'pass'); run=svc.run(EvalRunRequest(case_ids=['eval_001'], top_k=5)); assert run.results[0].metrics.json_validity is True and run.results[0].passed is True; print('natural answer json not applicable ok')"
cd hydra/backend && uv run python -c "from hydra_api.evals_service import EvalService; from hydra_api.schemas import EvalCase, QueryResponse, EvalRunRequest; cases=[EvalCase(id='eval_json', question='q', expected_documents=['doc_1'], expected_topics=[], expected_answer_traits=[], tags=['json_validity'])]; Q=type('Q',(),{'query':lambda self, req: QueryResponse(answer='{bad', retrieved_documents=[], limitations=[], trace_id='trace-q')}); svc=EvalService(case_loader=lambda: cases, query_service=Q(), judge=lambda *a, **k:'pass'); run=svc.run(EvalRunRequest(case_ids=['eval_json'], top_k=5)); assert run.results[0].metrics.json_validity is False and run.results[0].passed is False; print('json validity tagged case fails invalid json ok')"
```

## TASK-REPAIR-07-005: Normalizar respuesta de `/evals/run` y errores seguros

Estado: pending
Prioridad: must

Objetivo:
Hacer que el endpoint funcione con fakes inyectados, devuelva contrato estable y maneje errores esperados sin stack traces.

Archivos permitidos:

- `hydra/backend/src/hydra_api/main.py`
- `hydra/backend/src/hydra_api/evals_service.py`
- `hydra/backend/src/hydra_api/errors.py`

Requisitos:

- Mantener `app.state.eval_service` como mecanismo de fake.
- Convertir/coaccionar el retorno del servicio a `EvalRunResponse`.
- Si el objeto fake no trae `total_cases`, calcularlo como `len(results)`.
- Si falta `results_path`, usar `EVAL_RESULTS_PATH`.
- Errores por input/casos faltantes deben devolver HTTP 400 o error `invalid_input` seguro.
- Errores internos deben devolver mensaje genérico sin stack trace.
- `GET /evals/results` debe leer el export local y soportar ausencia/corrupción con respuesta segura.

Criterios de aceptación:

- El check SDD de fake endpoint pasa sin modificar el fake.
- `case_ids=[]` sigue devolviendo 422 por Pydantic.
- Caso inexistente no devuelve 200 silencioso.

Comandos de verificación:

```bash
cd hydra/backend && uv run python -c "from fastapi.testclient import TestClient; from hydra_api.main import app; Fake=type('Fake',(),{'run':lambda self, req: type('Run',(),{'run_id':'eval_run_001','results_path':'hydra/backend/data/outputs/eval_results.json','trace_id':'trace-eval','results':[]})()}); app.state.eval_service=Fake(); res=TestClient(app).post('/evals/run', json={'case_ids':['eval_001'],'top_k':5}); assert res.status_code==200 and res.json()['run_id']=='eval_run_001' and res.json()['total_cases']==0; del app.state.eval_service; print('eval run fake endpoint ok')"
cd hydra/backend && uv run python -c "from fastapi.testclient import TestClient; from hydra_api.main import app; res=TestClient(app).post('/evals/run', json={'case_ids':[],'top_k':5}); assert res.status_code==422; print('eval empty case ids 422 ok')"
cd hydra/backend && uv run python -c "from fastapi.testclient import TestClient; from hydra_api.main import app; Fake=type('Fake',(),{'run':lambda self, req: (_ for _ in ()).throw(ValueError('missing eval case'))}); app.state.eval_service=Fake(); res=TestClient(app).post('/evals/run', json={'case_ids':['missing'],'top_k':5}); assert res.status_code in (400,500) and 'traceback' not in res.text.lower(); del app.state.eval_service; print('eval endpoint safe error ok')"
```

## TASK-REPAIR-07-006: Cablear observabilidad lazy en servicios reales

Estado: pending
Prioridad: must

Objetivo:
Usar la factory pública de observabilidad en lugar de depender de `_LocalEmitter`, sin hacer obligatorio Langfuse ni romper fakes.

Archivos permitidos:

- `hydra/backend/src/hydra_api/observability.py`
- `hydra/backend/src/hydra_api/rag_service.py`
- `hydra/backend/src/hydra_api/briefing_service.py`
- `hydra/backend/src/hydra_api/main.py`

Requisitos:

- No importar ni instanciar Langfuse en import time.
- `QueryService` y `BriefingService` deben aceptar emitter inyectado.
- Cuando no se inyecte emitter, usar `create_observability_emitter(...)`, no `_LocalEmitter` directo.
- Si no hay settings o faltan claves, fallback local seguro.
- Si hay settings con claves Langfuse, crear emitter Langfuse lazy y degradar a local si falla.
- `create_query_service()` y la construcción real de `BriefingService` deben poder compartir emitter o al menos usar la misma política de factory.
- Fakes existentes deben seguir funcionando.

Criterios de aceptación:

- Imports funcionan sin `.env`.
- QueryService fake sin emitter sigue produciendo trace local.
- QueryService con emitter fake conserva trace fake.
- BriefingService con emitter fake emite eventos sin crear Langfuse real.

Comandos de verificación:

```bash
cd hydra/backend && uv run python -c "import hydra_api.rag_service, hydra_api.briefing_service, hydra_api.observability; print('observability service imports ok')"
cd hydra/backend && uv run python -c "from hydra_api.rag_service import QueryService; from hydra_api.schemas import QueryRequest; s=QueryService(retriever=lambda q,k: [], answer_chain=lambda *a, **k:'unused'); r=s.query(QueryRequest(question='q')); assert r.trace_id.startswith('local-'); print('query default local emitter ok')"
cd hydra/backend && uv run python -c "from hydra_api.rag_service import QueryService; from hydra_api.schemas import QueryRequest; E=type('E',(),{'start_trace':lambda self,*a,**k: type('T',(),{'trace_id':'trace-test','metadata':{}})(), 'event':lambda self,*a,**k: None, 'score':lambda self,*a,**k: None}); s=QueryService(retriever=lambda q,k: [], answer_chain=lambda *a, **k:'unused', emitter=E()); r=s.query(QueryRequest(question='q')); assert r.trace_id=='trace-test'; print('query fake emitter still ok')"
cd hydra/backend && uv run python -c "from hydra_api.observability import create_observability_emitter; E=create_observability_emitter(settings=type('S',(),{'langfuse_public_key':'','langfuse_secret_key':'','langfuse_base_url':''})()); t=E.start_trace('query', {'top_k':5}); assert t.trace_id.startswith('local-'); print('local emitter factory ok')"
```

## TASK-REPAIR-07-007: Reejecutar checks de Mission 07

Estado: pending
Prioridad: must

Objetivo:
Confirmar que el repair no rompe los checks originales y que los bloqueantes quedan cubiertos.

Archivos permitidos:

- Ninguno, tarea de verificación.

Comandos de verificación:

```bash
cd hydra/backend && uv sync
cd hydra/backend && uv run python -m compileall src
cd hydra/backend && uv run python -c "import langfuse; print('langfuse import ok')"
cd hydra/backend && uv run python -c "from hydra_api.observability import safe_preview, generate_local_trace_id; assert safe_preview('a'*1000, 10).endswith('...'); assert generate_local_trace_id().startswith('local-'); print('observability helpers ok')"
cd hydra/backend && uv run python -c "from hydra_api.rag_service import QueryService; from hydra_api.schemas import QueryRequest; E=type('E',(),{'start_trace':lambda self,*a,**k: type('T',(),{'trace_id':'trace-test','metadata':{}})(), 'event':lambda self,*a,**k: None, 'score':lambda self,*a,**k: None}); s=QueryService(retriever=lambda q,k: [], answer_chain=lambda *a, **k: 'unused', emitter=E()); r=s.query(QueryRequest(question='q')); assert r.trace_id=='trace-test' and r.limitations; print('query trace empty ok')"
cd hydra/backend && uv run python -c "from pydantic import ValidationError; from hydra_api.schemas import EvalRunRequest, EvalMetrics; assert EvalRunRequest(case_ids=['eval_001']).top_k==5; assert EvalMetrics(precision_at_k=0.8, json_validity=True, groundedness='pass'); print('eval schema positive ok')"
cd hydra/backend && uv run python -c "from hydra_api.evals_metrics import precision_at_k, coordination_caution; assert precision_at_k(['doc_1'], [{'document_id':'doc_1'}], 5)==1.0; assert coordination_caution('Hubo coordinacion.', []).passed is False; print('eval metrics ok')"
cd hydra/backend && uv run python -c "from hydra_api.evals_judges import parse_groundedness_label; assert parse_groundedness_label('PASS')=='pass'; print('groundedness parser ok')"
cd hydra/backend && uv run python -c "from fastapi.testclient import TestClient; from hydra_api.main import app; assert TestClient(app).get('/health').status_code==200; print('health ok')"
cd hydra/backend && uv run python -c "from fastapi.testclient import TestClient; from hydra_api.main import app; Fake=type('Fake',(),{'run':lambda self, req: type('Run',(),{'run_id':'eval_run_001','results_path':'hydra/backend/data/outputs/eval_results.json','trace_id':'trace-eval','results':[]})()}); app.state.eval_service=Fake(); res=TestClient(app).post('/evals/run', json={'case_ids':['eval_001'],'top_k':5}); assert res.status_code==200 and res.json()['run_id']=='eval_run_001'; del app.state.eval_service; print('eval run fake endpoint ok')"
```

## Tareas que siguen bloqueadas

No ejecutar en este repair:

- `TASK-OBS-008`: requiere Langfuse real, claves, red y aprobación explícita.
- `TASK-EVAL-014`: requiere corpus real aprobado e IDs estables.
- `TASK-EVAL-015`: requiere eval_cases real, DB, embeddings, modelos/judge y aprobación explícita de coste/red.

## Formato de reporte requerido

Al terminar, reportar:

```markdown
## Summary
- [Cambios principales]

## Repair tasks completed
- TASK-REPAIR-07-001: [resultado]
- TASK-REPAIR-07-002: [resultado]
- ...

## Files changed
- `path`: [motivo]

## Verification commands
- `[comando]` -> [resultado]

## Still blocked
- TASK-OBS-008: [por qué]
- TASK-EVAL-014: [por qué]
- TASK-EVAL-015: [por qué]

## Security check
- No `.env` reales modificados.
- No secretos, headers, stack traces, prompts completos, respuestas completas ni documentos completos en logs/reportes/traces/results.

## Deviations or blockers
- [Ninguno / detalles]
```
