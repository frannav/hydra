# Follow-up Repair - Mission 07 Observabilidad y evals

## Objetivo

Corregir los bloqueantes que quedan tras aplicar el primer repair de Mission 07. La implementación actual ya arregla parte del runner, pero todavía no queda aceptada porque `GET /evals/results` lee una ruta distinta a la ruta exportada, se han creado artefactos fuera de scope y algunos fallos siguen ocultándose.

## Veredicto de revisión

Mission 07 sigue **no aprobada** hasta aplicar este follow-up.

## Source of truth

Leer antes de ejecutar:

- `hydra/sdd/README.md`
- `hydra/sdd/01-architecture-decisions.md`
- `hydra/sdd/03-api-contract.md`
- `hydra/sdd/evals-observability.md`
- `hydra/sdd/tasks/07-observability-evals/07-observability-evals.md`
- `hydra/sdd/tasks/07-observability-evals/07-observability-evals-repair.md`

## Archivos permitidos

- `hydra/backend/src/hydra_api/evals_config.py`
- `hydra/backend/src/hydra_api/evals_service.py`
- `hydra/backend/src/hydra_api/main.py`
- `hydra/backend/src/hydra_api/observability.py`
- `hydra/backend/src/hydra_api/rag_service.py`
- `hydra/backend/src/hydra_api/briefing_service.py`
- `hydra/backend/src/hydra_api/evals_judges.py`
- `hydra/backend/data/outputs/.gitkeep`
- `hydra/backend/data/outputs/eval_results.json` solo si se decide versionar un fixture fake explícitamente

## Archivos/directorios que deben eliminarse si existen

- `hydra/backend/hydra/**`

Este directorio es un artefacto incorrecto creado por resolver mal `hydra/backend/data/...` desde `hydra/backend`. No pertenece al repo.

## Archivos prohibidos

- `hydra/frontend/**`
- `.env`, `.env.local` o cualquier secreto real
- `hydra/backend/data/evals/eval_cases.json` mientras `TASK-EVAL-014` siga bloqueada
- `hydra/backend/data/raw/**`
- `hydra/backend/data/metadata/documents/**`
- `hydra/backend/src/hydra_api/db_schema.py`
- `hydra/backend/ontology/hydra_ontology.yaml`
- Neo4j, graph sinks o upload frontend

## Bloqueantes restantes

1. `GET /evals/results` usa `pathlib.Path(EVAL_RESULTS_PATH)` directamente. Desde `hydra/backend`, eso apunta a `hydra/backend/data/outputs/eval_results.json` dentro de `backend/hydra/...`, no a `backend/data/outputs/eval_results.json`.
2. Existe el artefacto fuera de scope `backend/hydra/backend/data/outputs/eval_results.json`.
3. `EvalService.run()` oculta errores de export con `except Exception: pass`; puede devolver 200 aunque no se haya escrito el backup JSON.
4. `_resolve_eval_path()` depende de `exists()` para elegir candidato. Desde repo root, si el archivo de salida todavía no existe, puede resolver a una ruta errónea.
5. Los errores de path incluyen rutas absolutas como `/Users/...` y pueden acabar en respuestas API via `ValueError`.
6. `create_observability_emitter()` llamado sin `settings` sigue devolviendo local aunque existan claves Langfuse; los servicios reales no pasan settings a la factory.
7. `GroundednessJudge` por defecto devuelve `pass` incluso sin evidencias, contradiciendo el edge case de Mission 07.
8. `backend/src/hydra_api/evals_config.py` sigue sin estar versionado si aparece como `??` en `git status`.

## TASK-REPAIR-07-FU-001: Resolver rutas de evals de forma determinista

Estado: pending
Prioridad: must

Objetivo:
Eliminar la ambigüedad entre rutas de contrato (`hydra/backend/data/...`) y rutas físicas ejecutadas desde repo root o `hydra/backend`.

Requisitos:

- Crear helper público o interno claro, por ejemplo `resolve_eval_cases_path(path=None)` y `resolve_eval_results_path(path=None)`.
- La resolución debe basarse en la ubicación del módulo o backend root, no en si el archivo existe.
- `EVAL_CASES_PATH` y `EVAL_RESULTS_PATH` deben conservar los strings del contrato:
  - `hydra/backend/data/evals/eval_cases.json`
  - `hydra/backend/data/outputs/eval_results.json`
- Desde `hydra/backend`, `resolve_eval_results_path()` debe resolver a `hydra/backend/data/outputs/eval_results.json` físico, es decir `backend/data/outputs/eval_results.json`.
- Desde repo root, debe resolver al mismo archivo físico.
- Rechazar `..` y rutas absolutas fuera de los directorios permitidos.
- Los mensajes de error no deben incluir rutas absolutas.

Comandos de verificación:

```bash
cd hydra/backend && uv run python -c "from hydra_api.evals_service import resolve_eval_results_path, resolve_eval_cases_path; assert str(resolve_eval_results_path()).endswith('backend/data/outputs/eval_results.json'); assert str(resolve_eval_cases_path()).endswith('backend/data/evals/eval_cases.json'); print('backend cwd eval path resolution ok')"
cd hydra && uv --directory backend run python -c "from hydra_api.evals_service import resolve_eval_results_path, resolve_eval_cases_path; assert str(resolve_eval_results_path()).endswith('backend/data/outputs/eval_results.json'); assert str(resolve_eval_cases_path()).endswith('backend/data/evals/eval_cases.json'); print('repo cwd eval path resolution ok')"
```

## TASK-REPAIR-07-FU-002: Conectar export y results al mismo archivo

Estado: pending
Prioridad: must

Objetivo:
Garantizar que `EvalService.run()` exporta y `GET /evals/results` lee exactamente el mismo backup JSON.

Requisitos:

- `export_eval_results()` debe usar `resolve_eval_results_path()`.
- `GET /evals/results` no debe usar `pathlib.Path(EVAL_RESULTS_PATH)` directamente; debe usar el mismo resolver o un helper `load_latest_eval_results()`.
- Si el archivo no existe, `GET /evals/results` puede devolver `{ "run_id": "", "results": [] }`.
- Si el JSON está corrupto, devolver respuesta segura vacía o error controlado, sin stack trace.
- No leer desde `backend/hydra/**`.

Comandos de verificación:

```bash
cd hydra/backend && uv run python -c "import json, pathlib; from fastapi.testclient import TestClient; from hydra_api.main import app; from hydra_api.evals_service import resolve_eval_results_path; p=resolve_eval_results_path(); old=p.read_text() if p.exists() else None; p.parent.mkdir(parents=True, exist_ok=True); p.write_text(json.dumps({'run_id':'eval_run_sentinel_backend','results':[]})); res=TestClient(app).get('/evals/results'); assert res.status_code==200 and res.json()['run_id']=='eval_run_sentinel_backend', res.json(); p.write_text(old) if old is not None else p.unlink(missing_ok=True); print('eval results endpoint reads exported path ok')"
```

## TASK-REPAIR-07-FU-003: No ocultar errores de export

Estado: pending
Prioridad: must

Objetivo:
Evitar falsos positivos de eval run cuando no se pudo escribir `eval_results.json`.

Requisitos:

- Eliminar `except Exception: pass` alrededor de `export_eval_results()`.
- Si export falla, lanzar `ValueError`/error seguro con mensaje genérico.
- `/evals/run` debe devolver error seguro, no 200, cuando export falla.
- No incluir rutas absolutas ni stack traces.

Comandos de verificación:

```bash
cd hydra/backend && uv run python -c "from hydra_api.evals_service import export_eval_results; ok=False\ntry: export_eval_results(type('Run',(),{'run_id':'r','results':[]})(), '../bad/eval_results.json')\nexcept Exception as exc: ok=True; assert '/Users/' not in str(exc)\nassert ok; print('export unsafe path fails safely ok')"
```

## TASK-REPAIR-07-FU-004: Limpiar artefactos fuera de scope

Estado: pending
Prioridad: must

Objetivo:
Eliminar archivos generados en rutas incorrectas.

Requisitos:

- Borrar `hydra/backend/hydra/**` si existe.
- No borrar datos reales ni `.env`.
- Si `hydra/backend/data/outputs/eval_results.json` queda versionado, justificar que es fixture fake/local. Si no, dejarlo fuera del commit.

Comandos de verificación:

```bash
cd hydra && test ! -e backend/hydra && echo 'no nested backend/hydra artifact ok'
```

## TASK-REPAIR-07-FU-005: Cablear Langfuse lazy con settings reales cuando existan

Estado: pending
Prioridad: must

Objetivo:
Conservar fallback local, pero permitir que servicios reales usen Langfuse cuando settings válidos existen.

Requisitos:

- No cargar settings en import time.
- Si `create_observability_emitter(settings=None)` no puede cargar settings porque falta `MODEL_API_KEY`, debe volver a local sin fallar.
- Si hay settings válidos con `LANGFUSE_PUBLIC_KEY` y `LANGFUSE_SECRET_KEY`, debe crear emitter Langfuse lazy.
- `create_query_service()` y la construcción real de `BriefingService` deben pasar settings/emitter de forma explícita cuando ya están creando modelos reales.
- Fakes inyectados deben seguir funcionando sin settings.

Comandos de verificación:

```bash
cd hydra/backend && uv run python -c "from hydra_api.observability import create_observability_emitter; e=create_observability_emitter(); t=e.start_trace('query',{}); assert t.trace_id.startswith('local-') or t.trace_id; print('observability factory no env safe ok')"
cd hydra/backend && MODEL_API_KEY=fake MODEL_API_BASE_URL=https://example.invalid/v1 LANGFUSE_PUBLIC_KEY=pk_fake LANGFUSE_SECRET_KEY=sk_fake uv run python -c "from hydra_api.config import get_settings; from hydra_api.observability import create_observability_emitter; s=get_settings(); e=create_observability_emitter(settings=s); t=e.start_trace('query',{}); assert t.trace_id; print('observability factory with settings ok')"
```

## TASK-REPAIR-07-FU-006: Ajustar fake judge de groundedness

Estado: pending
Prioridad: should

Objetivo:
Evitar que el judge local marque `pass` cuando no hay evidencias.

Requisitos:

- `GroundednessJudge().__call__(answer, [])` debe devolver `warning` o `fail`.
- Con evidencias no vacías puede devolver `pass` en modo fake.
- `build_groundedness_prompt()` debe recortar respuesta y evidencias, no incluir textos completos largos.

Comandos de verificación:

```bash
cd hydra/backend && uv run python -c "from hydra_api.evals_judges import GroundednessJudge; assert GroundednessJudge()('respuesta', []) in {'warning','fail'}; assert GroundednessJudge()('respuesta', ['ev'])=='pass'; print('groundedness fake evidence behavior ok')"
```

## TASK-REPAIR-07-FU-007: Reejecutar checks finales

Estado: pending
Prioridad: must

Comandos de verificación:

```bash
cd hydra/backend && uv sync
cd hydra/backend && uv run python -m compileall src
cd hydra/backend && uv run python -c "import langfuse; print('langfuse import ok')"
cd hydra/backend && uv run python -c "from fastapi.testclient import TestClient; from hydra_api.main import app; assert TestClient(app).get('/health').status_code==200; print('health ok')"
cd hydra/backend && uv run python -c "from fastapi.testclient import TestClient; from hydra_api.main import app; Fake=type('Fake',(),{'run':lambda self, req: type('Run',(),{'run_id':'eval_run_001','results_path':'hydra/backend/data/outputs/eval_results.json','trace_id':'trace-eval','results':[]})()}); app.state.eval_service=Fake(); res=TestClient(app).post('/evals/run', json={'case_ids':['eval_001'],'top_k':5}); assert res.status_code==200 and res.json()['total_cases']==0; del app.state.eval_service; print('eval run fake endpoint ok')"
cd hydra/backend && uv run python -c "from hydra_api.rag_service import QueryService; from hydra_api.schemas import QueryRequest; r=QueryService(retriever=lambda q,k: [], answer_chain=lambda *a, **k:'unused').query(QueryRequest(question='q')); assert r.trace_id; print('query trace ok')"
cd hydra && git status --short
```

## Tareas que siguen bloqueadas

- `TASK-OBS-008`: requiere Langfuse real, claves, red y aprobación explícita.
- `TASK-EVAL-014`: requiere corpus real aprobado e IDs estables.
- `TASK-EVAL-015`: requiere eval_cases real, DB, embeddings, modelos/judge y aprobación explícita de coste/red.
