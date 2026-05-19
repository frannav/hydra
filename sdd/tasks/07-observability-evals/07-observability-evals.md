# Tasks - Observabilidad y evals

## Reglas de atomizacion

- Ejecutar estas tareas en orden, despues de las tareas core de RAG y council/briefing indicadas como dependencias.
- Mantener observabilidad y evals dentro de `hydra/backend/`; no tocar frontend.
- No crear ni modificar `.env` reales.
- Versionar solo cambios de codigo, SDD, lockfiles permitidos y fixtures/eval artifacts explicitamente permitidos por cada tarea.
- No llamar modelos reales, embeddings, Langfuse Cloud, DB viva ni red externa en verificaciones de tareas `pending` salvo que la tarea lo indique explicitamente.
- Usar fakes, emitters inyectados, fixtures temporales o servicios inyectados para verificaciones locales.
- No descargar, scrapear, buscar ni inventar documentos reales.
- No versionar documentos reales salvo aprobacion explicita.
- No crear Neo4j, grafo ni sinks nuevos en esta mission.
- No cambiar nombres de variables de entorno definidos en SDD.
- No cambiar el contrato de `POST /query`, `POST /briefing`, `POST /evals/run` ni `GET /evals/results` salvo validaciones seguras compatibles.
- No crear tablas nuevas ni modificar `db_schema.py`; los evals pueden exportar JSON local y usar las tablas ya definidas solo cuando exista DB viva.
- No registrar documentos completos, prompts completos, respuestas completas del modelo, headers, API keys ni stack traces.
- Si Langfuse no esta configurado, usar fallback local con `trace_id` seguro y export JSON.
- No marcar tareas como `done` hasta que Codex/reviewer revise diff, comandos y secretos.

## Contexto importante

Observabilidad y evals consumen artefactos producidos por misiones anteriores:

- `Settings` ya define `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY` y `LANGFUSE_BASE_URL`.
- `QueryResponse`, `BriefingResponse`, `EvalCase`, `EvalMetrics`, `EvalResult`, `EvalRunRequest`, `EvalRunResponse` y `EvalResultsResponse` viven en `hydra/backend/src/hydra_api/schemas.py`.
- `POST /query` debe devolver `trace_id` y evidencias/limitaciones.
- `POST /briefing` debe devolver `trace_id`, briefing grounded, risk review y limitaciones.
- `sdd/evals-observability.md` exige trazas minimas, 8-12 casos de eval, metricas obligatorias y backup local en `hydra/backend/data/outputs/eval_results.json`.
- El repo actual solo contiene templates/fixtures; no contiene corpus real aprobado ni `eval_cases.json` real. Por eso la creacion del dataset real y los smokes reales quedan `blocked`.

Por eso esta carpeta separa:

- helpers de observabilidad verificables sin Langfuse real;
- instrumentacion de servicios existentes con emitters inyectables;
- metricas y runner de evals verificables con fakes;
- dataset y ejecucion real, bloqueados hasta tener corpus, DB, modelos, Langfuse y aprobacion explicita.

## Lecciones incorporadas antes de la mission observabilidad/evals

- Alinear toda respuesta con `sdd/03-api-contract.md` y `backend/src/hydra_api/schemas.py`.
- Mantener clientes Langfuse/modelo y conexiones DB lazy; nada de llamadas en import time.
- Mantener verificaciones locales sin red, sin DB viva y sin claves reales.
- No aceptar `case_ids=[]`, preguntas vacias ni `top_k <= 0`.
- No aceptar manifests/eval cases incompletos; fallar con error seguro.
- No aceptar rutas absolutas ni `..` para cargar eval cases o escribir results.
- No resetear `processing_status`, chunks, embeddings, extracciones ni tablas existentes al ejecutar evals.
- No crear documentacion o checks que apunten a secciones inexistentes.
- Separar dependencia Langfuse, helpers de trace, instrumentacion, metricas, runner, endpoints y operaciones reales.
- Los evals no deben afirmar coordinacion, intencion o atribucion sin evidencia explicita.
- Groundedness real usa LLM judge + revision humana; la implementacion local debe poder probarse con judge fake.
- Langfuse Cloud es el destino preferido, pero el backup local JSON debe funcionar como fallback.

## Errores probables a evitar

- Importar `Settings` de forma que falle por falta de `MODEL_API_KEY` al importar modulos de observabilidad/evals.
- Crear el cliente Langfuse o llamar a Langfuse al importar `main.py`, `observability.py` o `evals_service.py`.
- Registrar preguntas, evidencias, prompts o respuestas completas sin recorte/redaccion.
- Exponer secretos, headers, stack traces o contenido completo de documentos en logs, traces, eval results o errores API.
- Cambiar nombres de env vars para Langfuse o modelos.
- Cambiar tablas o crear tablas paralelas para evals.
- Ejecutar evals reales con corpus/DB/modelos inexistentes desde una tarea `pending`.
- Crear `eval_cases.json` con documentos inventados o `expected_documents` que no existen en el corpus aprobado.
- Tratar ausencia de Langfuse como fallo fatal del endpoint.
- Enviar scores duplicados o sin `trace_id` cuando existe traza.
- Tocar `hydra/frontend/`, Neo4j, docs historicos o archivos fuera de scope.

## Edge cases obligatorios

- Langfuse sin claves debe producir `trace_id` local y no romper `/query`, `/briefing` ni evals.
- Langfuse configurado pero no disponible debe degradar a fallback local con error seguro.
- `trace_id` debe existir aunque retrieval no devuelva chunks.
- `trace_id` no debe contener secretos, rutas absolutas ni contenido de usuario completo.
- Preguntas vacias o solo espacios deben fallar antes de ejecutar evals.
- `top_k` omitido debe usar `5`; `top_k <= 0` debe fallar validacion.
- `case_ids=[]` debe fallar validacion.
- Eval cases con campos obligatorios ausentes deben fallar antes de ejecutar retrieval/modelos.
- `expected_documents=[]` solo es valido si el caso lo justifica explicitamente con tag de limitacion; si no, parar.
- Precision@k con `expected_documents=[]` o `retrieved_documents=[]` debe ser determinista y documentado.
- JSON validity debe distinguir JSON invalido de JSON valido pero schema invalido.
- Ontology mapping debe fallar IDs desconocidos contra YAML y no ignorarlos silenciosamente.
- Coordination caution debe penalizar claims de coordinacion/intencion/atribucion sin evidencia explicita.
- Latency/cost ausente debe registrarse como `null`/`unknown`, no inventarse.
- Results export debe crear directorio si falta, pero solo bajo `hydra/backend/data/outputs/`.

## Stop conditions generales

- La tarea requiere cambiar `sdd/03-api-contract.md`, `sdd/02-data-model.md`, `sdd/evals-observability.md` o `backend/src/hydra_api/db_schema.py`.
- La tarea requiere cambiar nombres de env vars, modelos o arquitectura de observabilidad.
- La tarea requiere DB viva, corpus real, modelos reales, embeddings reales o Langfuse real y no esta marcada como `blocked`.
- La tarea necesita tocar frontend, Neo4j, `.env` reales, docs historicos o archivos fuera de scope.
- La verificacion local no puede ejecutarse con fakes/fixtures temporales.
- Se necesita versionar documentos reales o resultados con secretos/contenido sensible.
- La implementacion de evals crea un pipeline RAG/briefing paralelo en vez de reutilizar servicios existentes.
- El fallback local no puede emitir `trace_id` seguro.

## Milestones sugeridos para Droid Missions

| Milestone | Tareas | Objetivo | Debe parar para review |
|---|---|---|---|
| 1 | TASK-OBS-001 a TASK-OBS-004 | Dependencia Langfuse, helpers de trace y emisor lazy con fallback local | Si llama Langfuse real o requiere claves en verificacion |
| 2 | TASK-OBS-005 a TASK-OBS-007 | Instrumentar `/query`, generacion RAG, `/briefing` y council | Si registra prompts/documentos completos o cambia contratos |
| 3 | TASK-EVAL-001 a TASK-EVAL-008 | Validaciones, paths, loader y metricas deterministas offline | Si requiere corpus/DB/modelos reales |
| 4 | TASK-EVAL-009 a TASK-EVAL-013 | Judge fake, runner, export JSON, endpoints y scores opcionales | Si ejecuta proveedores reales o escribe fuera de outputs |
| 5 | TASK-OBS-008, TASK-EVAL-014 y TASK-EVAL-015 | Bloqueado: Langfuse/dataset/evals reales | Bloqueado hasta corpus, DB, modelos, claves y aprobacion |

## TASK-OBS-001: Anadir dependencia Langfuse

Estado: pending
Prioridad: must

Objetivo:
Anadir el SDK oficial de Langfuse necesario para trazas Cloud sin mezclarlo con implementacion de observabilidad.

Archivos permitidos:
- `hydra/backend/pyproject.toml`
- `hydra/backend/uv.lock`

Dependencias:
- TASK-BACK-001

Requisitos:
- Anadir dependencia minima para Langfuse Cloud.
- No anadir dependencias de Langfuse self-hosted, frontend, Neo4j, scraping ni dashboards externos.
- No modificar codigo de aplicacion en esta tarea.
- No crear ni modificar `.env` reales.

Criterios de aceptacion:
- El paquete `langfuse` es importable con `uv`.
- `pyproject.toml` no contiene dependencias de Neo4j ni frontend.
- El lockfile queda actualizado por `uv`, no editado a mano.

Errores probables a evitar:
- Mezclar instalacion con cambios en `observability.py`.
- Anadir dependencias no necesarias para el MVP.

Edge cases obligatorios:
- Si `uv` requiere red y falla, reportar bloqueo tecnico; no falsificar `uv.lock`.
- Si el SDK cambia el nombre del import, documentarlo en el reporte antes de continuar.

Stop conditions:
- La dependencia elegida obliga a cambiar arquitectura, env vars o desplegar Langfuse self-hosted.

Comandos de verificacion:
- `cd hydra/backend && uv sync`
- `cd hydra/backend && uv run python -c "import langfuse; print('langfuse import ok')"`
- `cd hydra/backend && uv run python -c "import pathlib; text=pathlib.Path('pyproject.toml').read_text().lower(); assert 'neo4j' not in text; print('no neo4j dependency')"`

## TASK-OBS-002: Definir constantes y redaccion segura de observabilidad

Estado: pending
Prioridad: must

Objetivo:
Crear constantes y helpers puros para recortar/redactar datos antes de logs/traces.

Archivos permitidos:
- `hydra/backend/src/hydra_api/observability.py`

Dependencias:
- TASK-OBS-001

Requisitos:
- Crear constantes para limites seguros de longitud de pregunta, evidencia, prompt version y respuesta resumida.
- Crear `redact_secret_like_values(value)` o helper equivalente para ocultar valores que parezcan API keys, bearer tokens o headers sensibles.
- Crear `safe_preview(text, max_chars)` o helper equivalente que recorte texto y normalice whitespace.
- No leer Settings ni entorno en import time.
- No importar clientes Langfuse/modelos en esta tarea.

Criterios de aceptacion:
- `observability.py` importa sin `.env` ni `MODEL_API_KEY`.
- Los helpers recortan texto largo y eliminan indicios de secretos.
- Los limites son mayores que cero.

Errores probables a evitar:
- Guardar documentos completos o prompts completos como preview.
- Usar regex demasiado amplia que destruya IDs normales como `doc_001`.

Edge cases obligatorios:
- `None`, strings vacios y whitespace deben manejarse sin excepciones.
- Texto multilinea debe quedar en preview de una linea o formato seguro.
- Valores tipo `Bearer abc` o `sk-...` deben redactarse.

Stop conditions:
- Se necesita cambiar politica de logs o exponer contenido completo para depurar.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "from hydra_api.observability import safe_preview; assert safe_preview('a'*1000, 10).endswith('...'); print('preview ok')"`
- `cd hydra/backend && uv run python -c "from hydra_api.observability import redact_secret_like_values; assert 'abc123' not in redact_secret_like_values('Bearer abc123'); print('redaction ok')"`

## TASK-OBS-003: Crear trace_id local y TraceContext

Estado: pending
Prioridad: must

Objetivo:
Crear un fallback local de trazas que genere `trace_id` seguro aunque Langfuse no este configurado.

Archivos permitidos:
- `hydra/backend/src/hydra_api/observability.py`

Dependencias:
- TASK-OBS-002

Requisitos:
- Crear `generate_local_trace_id()` con prefijo estable tipo `local-` y entropia suficiente.
- Crear `TraceContext` o estructura equivalente con `trace_id`, `name`, `metadata`, `started_at` y helper de duracion.
- Crear funciones puras para iniciar/cerrar trace local sin red.
- No depender de Langfuse, DB ni modelo.
- No incluir pregunta completa ni evidencia completa dentro del `trace_id`.

Criterios de aceptacion:
- Dos trace IDs generados consecutivamente son distintos.
- El `trace_id` no contiene espacios, slash, backslash ni `..`.
- Se puede crear/cerrar una traza local sin `.env`.

Errores probables a evitar:
- Usar texto del usuario como parte del ID.
- Usar timestamp solo, generando colisiones.

Edge cases obligatorios:
- Creacion concurrente de traces no debe compartir metadata mutable.
- Metadata ausente debe convertirse en dict vacio seguro.

Stop conditions:
- Se necesita usar IDs de Langfuse reales en verificaciones locales.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "from hydra_api.observability import generate_local_trace_id; a=generate_local_trace_id(); b=generate_local_trace_id(); assert a!=b and a.startswith('local-') and '/' not in a and '..' not in a; print('local trace id ok')"`
- `cd hydra/backend && uv run python -c "from hydra_api.observability import start_local_trace; t=start_local_trace('query', {'top_k':5}); assert t.trace_id and t.metadata['top_k']==5; print('local trace context ok')"`

## TASK-OBS-004: Crear emisor Langfuse lazy con fallback local

Estado: pending
Prioridad: must

Objetivo:
Crear una capa inyectable para emitir traces/scores a Langfuse cuando hay claves y degradar a fallback local cuando no las hay.

Archivos permitidos:
- `hydra/backend/src/hydra_api/observability.py`

Dependencias:
- TASK-OBS-003

Requisitos:
- Crear una clase o protocolo `ObservabilityEmitter` con metodos para trace/event/score.
- Crear `create_observability_emitter(settings=None)` lazy: no debe crear clientes ni leer Settings al importar el modulo.
- Si faltan `LANGFUSE_PUBLIC_KEY` o `LANGFUSE_SECRET_KEY`, devolver emisor local/no-op con `trace_id` local.
- Si Langfuse falla en runtime, capturar error de forma segura y continuar con fallback local.
- No lanzar errores al cliente por fallo de observabilidad.
- No imprimir secretos ni headers.

Criterios de aceptacion:
- El emisor local funciona sin `.env`.
- La factory puede probarse con settings fake sin red.
- Los metodos devuelven/propagan un `trace_id` usable por responses.

Errores probables a evitar:
- Instanciar Langfuse al importar `observability.py`.
- Hacer obligatorio Langfuse para `/query`, `/briefing` o evals.
- Registrar excepciones con stack trace completo en respuesta API.

Edge cases obligatorios:
- Settings fake con claves vacias debe usar no-op.
- Settings fake con base URL invalida no debe hacer red hasta emitir.
- Fallo de emit no debe perder el `trace_id` local.

Stop conditions:
- La factory requiere claves reales para pasar tests locales.
- El SDK Langfuse obliga a cambiar variables de entorno SDD.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "from hydra_api.observability import create_observability_emitter; E=create_observability_emitter(settings=type('S',(),{'langfuse_public_key':'','langfuse_secret_key':'','langfuse_base_url':''})()); t=E.start_trace('query', {'top_k':5}); assert t.trace_id.startswith('local-'); E.score(t.trace_id, 'precision_at_k', 1.0); print('local emitter ok')"`
- `cd hydra/backend && uv run python -c "import hydra_api.observability; print('observability import ok')"`

## TASK-OBS-005: Trazar ciclo de retrieval en `/query`

Estado: pending
Prioridad: must

Objetivo:
Instrumentar el servicio de query para registrar pregunta recortada, parametros de retrieval, documentos/chunks recuperados, scores, latencia y `trace_id` sin cambiar el contrato de `/query`.

Archivos permitidos:
- `hydra/backend/src/hydra_api/observability.py`
- `hydra/backend/src/hydra_api/rag_service.py`

Dependencias:
- TASK-OBS-004
- TASK-RAG-016

Requisitos:
- `QueryService` debe aceptar un emitter inyectable o crear uno lazy en runtime.
- Registrar `question_preview`, `top_k`, cantidad de resultados, `document_id`, `chunk_id` y `score`.
- No registrar evidencia completa; usar preview seguro.
- Si retrieval devuelve cero resultados, emitir trace con limitacion y `trace_id` igualmente.
- `QueryResponse.trace_id` debe usar el `trace_id` de la traza.
- No modificar SQL, embeddings ni DB schema.

Criterios de aceptacion:
- QueryService funciona con emitter fake sin DB ni modelo.
- La respuesta contiene `trace_id` aun sin contexto.
- El emitter recibe metadata recortada y sin documentos completos.

Errores probables a evitar:
- Crear un retriever paralelo para observabilidad.
- Pasar el texto completo de chunks al trace.
- Romper el modo sin contexto suficiente.

Edge cases obligatorios:
- Retrieval vacio.
- Score `None` o no numerico debe registrarse como `unknown` o omitirse de forma segura.
- Evidence con saltos de linea debe recortarse.

Stop conditions:
- Se necesita cambiar el contrato de `POST /query`.
- La instrumentacion requiere DB viva o Langfuse real para pasar tests.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "from hydra_api.rag_service import QueryService; from hydra_api.schemas import QueryRequest; E=type('E',(),{'start_trace':lambda self,*a,**k: type('T',(),{'trace_id':'trace-test','metadata':{}})(), 'event':lambda self,*a,**k: None, 'score':lambda self,*a,**k: None}); s=QueryService(retriever=lambda q,k: [], answer_chain=lambda *a, **k: 'unused', emitter=E()); r=s.query(QueryRequest(question='q')); assert r.trace_id=='trace-test' and r.limitations; print('query trace empty ok')"`

## TASK-OBS-006: Trazar generacion de respuesta RAG

Estado: pending
Prioridad: must

Objetivo:
Registrar la generacion de respuesta grounded sin guardar prompt completo, respuesta completa ni secretos.

Archivos permitidos:
- `hydra/backend/src/hydra_api/observability.py`
- `hydra/backend/src/hydra_api/rag_answering.py`
- `hydra/backend/src/hydra_api/rag_service.py`

Dependencias:
- TASK-OBS-005
- TASK-RAG-015
- TASK-RAG-016

Requisitos:
- Registrar version/nombre del prompt, modelo configurado si esta disponible, latencia y tokens/coste solo si el proveedor lo devuelve.
- Registrar preview seguro de la respuesta, no la respuesta completa.
- Registrar limitaciones producidas por la chain.
- Mantener funcionamiento con answer_chain fake.
- Si el proveedor falla, la respuesta API debe usar error seguro existente, no stack trace.

Criterios de aceptacion:
- Con chain fake, el emitter recibe evento de generacion.
- No se emite prompt completo ni documento completo.
- Tokens/coste ausentes no rompen la traza.

Errores probables a evitar:
- Loggear el prompt final completo.
- Inventar coste/tokens cuando el proveedor no los devuelve.
- Convertir fallo de observabilidad en fallo de generacion.

Edge cases obligatorios:
- Chain devuelve string vacio.
- Chain devuelve metadata sin tokens/coste.
- Error de modelo debe conservar mensaje seguro.

Stop conditions:
- Se necesita modificar prompts SDD o contrato de `/query`.
- La verificacion requiere proveedor real.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "from hydra_api.rag_answering import build_no_context_response; print('rag answering import ok')"`
- `cd hydra/backend && uv run python -c "from hydra_api.rag_service import QueryService; from hydra_api.schemas import QueryRequest; events=[]; E=type('E',(),{'start_trace':lambda self,*a,**k: type('T',(),{'trace_id':'trace-gen','metadata':{}})(), 'event':lambda self,*a,**k: events.append((a,k)), 'score':lambda self,*a,**k: None}); s=QueryService(retriever=lambda q,k: [], answer_chain=lambda *a, **k: 'unused', emitter=E()); s.query(QueryRequest(question='q')); assert events; print('generation trace fake ok')"`

## TASK-OBS-007: Trazar briefing y council

Estado: pending
Prioridad: must

Objetivo:
Instrumentar `POST /briefing` y council para registrar uso de council, risk review, unsupported claims, evidencias recuperadas y latencia sin exponer prompts ni documentos completos.

Archivos permitidos:
- `hydra/backend/src/hydra_api/observability.py`
- `hydra/backend/src/hydra_api/briefing_service.py`
- `hydra/backend/src/hydra_api/council_service.py`

Dependencias:
- TASK-OBS-004
- TASK-BRIEF-006
- TASK-COUNCIL-007

Requisitos:
- `BriefingService` debe aceptar emitter inyectable o crear uno lazy en runtime.
- Reutilizar `trace_id` de RAG si el servicio de query ya lo devuelve; si no, crear uno local.
- Registrar `use_council`, riesgo final, si la evidencia esta soportada y numero de unsupported claims.
- No registrar prompts del council completos ni briefing completo.
- Si `use_council=false`, registrar que el council fue omitido y mantener limitaciones.

Criterios de aceptacion:
- BriefingService funciona con emitter fake.
- `BriefingResponse.trace_id` existe con y sin council.
- Unsupported claims se registran como conteo/lista recortada, no texto sensible completo.

Errores probables a evitar:
- Crear trace nuevo y perder el trace_id de RAG cuando ya existe.
- Registrar briefing Markdown completo en Langfuse/logs.
- Omitir limitaciones cuando `use_council=false`.

Edge cases obligatorios:
- Retrieval sin resultados.
- Council devuelve risk invalido.
- Council devuelve unsupported claims largos o multilinea.

Stop conditions:
- Se necesita cambiar el contrato de `POST /briefing`.
- La instrumentacion requiere modelo real o Langfuse real para pasar tests.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "from hydra_api.briefing_service import BriefingService; print('briefing service import ok')"`
- `cd hydra/backend && uv run python -c "from hydra_api.council_service import build_council_review; print('council service import ok')"`

## TASK-OBS-008: Verificar trazas reales en Langfuse Cloud

Estado: blocked
Prioridad: must

Bloqueo:
Requiere `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, red externa aprobada, RAG/briefing reales funcionando y aprobacion explicita para emitir trazas a Langfuse Cloud.

Objetivo:
Ejecutar smoke test real que confirme que `/query`, `/briefing` y evals generan trazas/scores visibles en Langfuse Cloud.

Archivos permitidos:
- Ninguno; tarea operativa de verificacion.

Dependencias:
- TASK-OBS-007
- TASK-EVAL-013
- TASK-RAG-020
- TASK-BRIEF-007

Requisitos:
- Usar `.env` local no versionado.
- No imprimir claves ni headers.
- Reportar solo IDs de traza y estado de verificacion.
- No subir documentos completos a trazas.

Criterios de aceptacion:
- Hay al menos una traza real de `/query`.
- Hay al menos una traza real de `/briefing`.
- Hay al menos un score de eval asociado a un `trace_id`.

Errores probables a evitar:
- Versionar `.env` o copiar claves al reporte.
- Ejecutar contra Langfuse sin aprobacion de coste/red.

Edge cases obligatorios:
- Si Langfuse esta caido, confirmar fallback local y dejar la tarea bloqueada o en review con evidencia.
- Si un trace no aparece, no reintentar masivamente.

Stop conditions:
- Falta cualquier clave real o aprobacion explicita.
- La traza contiene documentos/prompts/respuestas completas.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "print('Run only after user approves real Langfuse smoke')"`

## TASK-EVAL-001: Validar EvalRunRequest y metricas extendidas

Estado: pending
Prioridad: must

Objetivo:
Asegurar que los requests de evals son seguros y que `EvalMetrics` puede representar las metricas obligatorias sin romper campos existentes.

Archivos permitidos:
- `hydra/backend/src/hydra_api/schemas.py`

Dependencias:
- TASK-BACK-001

Requisitos:
- Mantener campos existentes de `EvalRunRequest`: `case_ids`, `top_k`.
- `case_ids` debe ser lista no vacia.
- `top_k` debe tener default `5` y rechazar valores menores que `1`.
- Mantener campos existentes de `EvalMetrics`: `precision_at_k`, `json_validity`, `groundedness`.
- Anadir solo campos opcionales/compatibles si hacen falta para `ontology_mapping`, `coordination_caution`, `latency_ms` y `cost`.
- No cambiar nombres de `EvalRunResponse` ni `EvalResultsResponse`.

Criterios de aceptacion:
- `EvalRunRequest(case_ids=['eval_001'])` usa `top_k=5`.
- `EvalRunRequest(case_ids=[])` falla.
- `EvalRunRequest(case_ids=['eval_001'], top_k=0)` falla.
- `EvalMetrics` sigue aceptando los campos del contrato actual.

Errores probables a evitar:
- Hacer `case_ids` opcional o permitir lista vacia.
- Eliminar `precision_at_k`, `json_validity` o `groundedness`.
- Cambiar response models de forma incompatible.

Edge cases obligatorios:
- IDs con espacios alrededor deben normalizarse o rechazarse de forma clara.
- IDs duplicados deben deduplicarse en servicio o rechazarse; documentar la decision en codigo.

Stop conditions:
- Se necesita cambiar el contrato publico de `/evals/run` o `/evals/results`.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "from pydantic import ValidationError; from hydra_api.schemas import EvalRunRequest, EvalMetrics; assert EvalRunRequest(case_ids=['eval_001']).top_k==5; assert EvalMetrics(precision_at_k=0.8, json_validity=True, groundedness='pass'); print('eval schema positive ok')"`
- `cd hydra/backend && uv run python -c "exec('from pydantic import ValidationError\nfrom hydra_api.schemas import EvalRunRequest\nbad=[]\nfor payload in ({\"case_ids\":[]},{\"case_ids\":[\"eval_001\"],\"top_k\":0}):\n    try: EvalRunRequest(**payload)\n    except ValidationError: bad.append(payload)\nassert len(bad)==2\nprint(\"eval schema negative ok\")')"`

## TASK-EVAL-002: Definir constantes y rutas de evals

Estado: pending
Prioridad: must

Objetivo:
Centralizar rutas y umbrales de evals sin aceptar rutas arbitrarias desde usuarios.

Archivos permitidos:
- `hydra/backend/src/hydra_api/evals_config.py`

Dependencias:
- TASK-EVAL-001

Requisitos:
- Definir `DEFAULT_EVAL_TOP_K = 5`.
- Definir `EVAL_CASES_PATH = "hydra/backend/data/evals/eval_cases.json"`.
- Definir `EVAL_RESULTS_PATH = "hydra/backend/data/outputs/eval_results.json"`.
- Definir umbrales/labels para precision, groundedness, ontology mapping y coordination caution.
- No leer `.env`, Settings, DB ni Langfuse al importar.
- No crear archivos en import time.

Criterios de aceptacion:
- El modulo importa sin `.env`.
- Las rutas quedan bajo `hydra/backend/data/`.
- `DEFAULT_EVAL_TOP_K` coincide con SDD.

Errores probables a evitar:
- Aceptar path de usuario para leer/escribir resultados.
- Usar rutas absolutas dependientes de la maquina local.

Edge cases obligatorios:
- Las rutas deben poder resolverse desde repo root y desde `hydra/backend` con helper posterior.
- No crear directorios durante import.

Stop conditions:
- Se necesita cambiar paths del contrato API.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "from hydra_api.evals_config import DEFAULT_EVAL_TOP_K, EVAL_CASES_PATH, EVAL_RESULTS_PATH; assert DEFAULT_EVAL_TOP_K==5; assert 'data/evals/eval_cases.json' in EVAL_CASES_PATH; assert 'data/outputs/eval_results.json' in EVAL_RESULTS_PATH; print('eval config ok')"`

## TASK-EVAL-003: Crear loader seguro de eval cases

Estado: pending
Prioridad: must

Objetivo:
Implementar carga y validacion de eval cases desde JSON sin depender todavia del dataset real.

Archivos permitidos:
- `hydra/backend/src/hydra_api/evals_service.py`

Dependencias:
- TASK-EVAL-002

Requisitos:
- Crear helper `load_eval_cases(path=None)` o equivalente.
- Resolver paths solo bajo `hydra/backend/data/evals/`.
- Las fixtures temporales de verificacion deben crearse bajo `hydra/backend/data/evals/` y limpiarse al terminar; no usar rutas absolutas externas.
- Validar cada item con `EvalCase`.
- Rechazar JSON invalido, top-level no lista, IDs duplicados y campos obligatorios ausentes.
- No aceptar `expected_documents=[]` salvo tag explicito de limitacion como `no_expected_documents`.
- No abrir DB ni llamar modelos.
- Permitir tests con archivo temporal dentro de `tmp_path` o fixture controlado.

Criterios de aceptacion:
- Loader carga una lista valida de casos desde fixture temporal.
- Loader falla de forma segura ante JSON invalido o caso incompleto.
- Loader no acepta path traversal.

Errores probables a evitar:
- Crear `eval_cases.json` inventado para pasar la prueba.
- Ignorar silenciosamente casos invalidos.
- Permitir rutas absolutas o `..`.

Edge cases obligatorios:
- Archivo inexistente produce error claro `missing_eval_cases` o equivalente.
- Lista vacia produce error claro.
- IDs repetidos producen error claro.

Stop conditions:
- Se necesita corpus real para implementar el loader.
- Se necesita cambiar el schema `EvalCase`.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "import json, tempfile, pathlib; from hydra_api.evals_service import load_eval_cases; data=[{'id':'eval_001','question':'q','expected_documents':['doc_001'],'expected_topics':['topic'],'expected_answer_traits':['trait'],'tags':['smoke']}]; base=pathlib.Path('data/evals'); base.mkdir(parents=True, exist_ok=True); d=tempfile.TemporaryDirectory(dir=base); p=pathlib.Path(d.name)/'eval_cases.json'; p.write_text(json.dumps(data)); cases=load_eval_cases(p); assert cases[0].id=='eval_001'; print('eval cases loader ok')"`
- `cd hydra/backend && uv run python -c "exec('import tempfile, pathlib\nfrom hydra_api.evals_service import load_eval_cases\nbase=pathlib.Path(\"data/evals\"); base.mkdir(parents=True, exist_ok=True)\nd=tempfile.TemporaryDirectory(dir=base); p=pathlib.Path(d.name)/\"bad.json\"; p.write_text(\"{bad\")\nok=False\ntry: load_eval_cases(p)\nexcept Exception: ok=True\nassert ok\nprint(\"eval cases invalid json rejected\")')"`

## TASK-EVAL-004: Implementar Precision@k

Estado: pending
Prioridad: must

Objetivo:
Calcular retrieval Precision@k comparando documentos esperados contra documentos recuperados.

Archivos permitidos:
- `hydra/backend/src/hydra_api/evals_metrics.py`

Dependencias:
- TASK-EVAL-003
- TASK-RAG-011

Requisitos:
- Crear `precision_at_k(expected_documents, retrieved_documents, k)` o equivalente.
- Aceptar retrieved docs como `RetrievedDocument` o dicts compatibles.
- Usar solo los top-k recuperados.
- Deduplicar por `document_id` de forma determinista.
- Documentar comportamiento cuando no hay expected docs.
- No abrir DB ni llamar retriever.

Criterios de aceptacion:
- Esperado `['doc_1','doc_2']`, recuperado top-2 `doc_1, doc_3` produce `0.5`.
- Recuperados vacios produce `0.0` salvo caso explicitamente sin expected docs.
- `k <= 0` falla.

Errores probables a evitar:
- Dividir por `k` en vez de por numero de documentos esperados sin documentarlo.
- Contar dos chunks del mismo documento como dos aciertos.
- Ignorar `top_k`.

Edge cases obligatorios:
- Duplicados en expected o retrieved.
- `k` mayor que resultados disponibles.
- IDs con espacios deben normalizarse o rechazarse de forma clara.

Stop conditions:
- La metrica requiere cambiar schema de retrieval.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "from hydra_api.evals_metrics import precision_at_k; docs=[{'document_id':'doc_1'},{'document_id':'doc_3'}]; assert precision_at_k(['doc_1','doc_2'], docs, 2)==0.5; assert precision_at_k(['doc_1'], [], 5)==0.0; print('precision@k ok')"`

## TASK-EVAL-005: Implementar JSON validity

Estado: pending
Prioridad: must

Objetivo:
Validar si una salida JSON es parseable y compatible con un schema Pydantic esperado.

Archivos permitidos:
- `hydra/backend/src/hydra_api/evals_metrics.py`

Dependencias:
- TASK-EVAL-004
- TASK-EXT-006

Requisitos:
- Crear helper `json_validity(payload, schema_model)` o equivalente.
- Distinguir estados: JSON invalido, JSON valido pero schema invalido, schema valido.
- Aceptar dict ya parseado y string JSON.
- No aceptar silenciosamente campos obligatorios ausentes.
- No llamar modelos ni leer documentos reales.

Criterios de aceptacion:
- Un fixture de extraccion valida pasa contra `Extraction`.
- Un JSON mal formado falla.
- Un dict sin campos obligatorios falla.

Errores probables a evitar:
- Usar `json.loads` y devolver true sin validar Pydantic.
- Capturar todas las excepciones y reportar pass.

Edge cases obligatorios:
- Payload vacio.
- Lista JSON cuando se espera objeto.
- Campos extra deben seguir la politica del schema existente; no cambiarla aqui.

Stop conditions:
- Se necesita modificar schemas canonicos de extraccion.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "import json, pathlib; from hydra_api.evals_metrics import json_validity; from hydra_api.schemas import Extraction; valid=pathlib.Path('data/fixtures/extraction_valid_minimal.json').read_text(); assert json_validity(valid, Extraction).passed is True; assert json_validity('{bad', Extraction).passed is False; assert json_validity({}, Extraction).passed is False; print('json validity ok')"`

## TASK-EVAL-006: Implementar ontology mapping

Estado: pending
Prioridad: must

Objetivo:
Verificar que IDs/categorias de extracciones pertenecen a la ontologia YAML vigente.

Archivos permitidos:
- `hydra/backend/src/hydra_api/evals_metrics.py`
- `hydra/backend/src/hydra_api/ontology.py`

Dependencias:
- TASK-EVAL-005
- TASK-ONT-012
- TASK-EXT-009

Requisitos:
- Reutilizar helpers existentes de ontologia; no parsear YAML con logica paralela si ya existe helper.
- Validar `narrative_frame_id`, `actor_types`, `affected_sectors` y `threat_types` cuando existan en la extraccion.
- Reportar IDs desconocidos de forma segura.
- No modificar `hydra/backend/ontology/hydra_ontology.yaml` en esta tarea.
- No llamar modelos.

Criterios de aceptacion:
- Fixture valido pasa.
- Fixture con ID desconocido falla.
- El resultado enumera IDs desconocidos sin stack trace.

Errores probables a evitar:
- Ignorar campos vacios sin distinguir `missing` vs `unknown`.
- Hardcodear una segunda ontologia en codigo.
- Aceptar IDs desconocidos por fuzzy matching.

Edge cases obligatorios:
- Extraccion sin campos opcionales debe devolver warning/controlado segun schema, no crash.
- YAML faltante o invalido debe producir error seguro.
- IDs duplicados no deben duplicar errores.

Stop conditions:
- Se necesita cambiar la ontologia YAML o los schemas de extraccion.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "from hydra_api.evals_metrics import ontology_mapping_validity; print(callable(ontology_mapping_validity)); print('ontology metric import ok')"`
- `cd hydra/backend && uv run python -c "import json, pathlib; from hydra_api.evals_metrics import ontology_mapping_validity; data=json.loads(pathlib.Path('data/fixtures/extraction_invalid_unknown_id.json').read_text()); result=ontology_mapping_validity(data); assert result.passed is False; print('ontology unknown rejected')"`

## TASK-EVAL-007: Implementar coordination caution

Estado: pending
Prioridad: must

Objetivo:
Detectar y penalizar respuestas que afirman coordinacion, intencion o atribucion sin evidencia explicita.

Archivos permitidos:
- `hydra/backend/src/hydra_api/evals_metrics.py`

Dependencias:
- TASK-EVAL-004

Requisitos:
- Crear helper `coordination_caution(answer, evidence_fragments)` o equivalente.
- Detectar terminos de riesgo: coordinacion, coordinado, orquestado, intencion, estrategia, atribucion, causalidad fuerte.
- Pasar si la respuesta evita claims fuertes o los acompana de evidencia explicita.
- Fallar o marcar warning si hay claim fuerte sin evidencia.
- No usar LLM para esta regla; el LLM judge queda en TASK-EVAL-009.

Criterios de aceptacion:
- Respuesta con "no hay evidencia suficiente de coordinacion" pasa.
- Respuesta con "hubo coordinacion" y evidencia vacia falla.
- Respuesta neutral con limitaciones pasa.

Errores probables a evitar:
- Penalizar negaciones cautelosas como si fueran afirmaciones.
- Pasar claims fuertes solo porque hay cualquier evidencia no relacionada.

Edge cases obligatorios:
- Mayusculas/minusculas y acentos.
- Frases negativas: "no se puede afirmar coordinacion".
- Evidence vacia, `None` o solo whitespace.

Stop conditions:
- Se necesita cambiar reglas analiticas del SDD.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "from hydra_api.evals_metrics import coordination_caution; assert coordination_caution('No hay evidencia suficiente de coordinacion.', []).passed is True; assert coordination_caution('Hubo coordinacion entre actores.', []).passed is False; print('coordination caution ok')"`

## TASK-EVAL-008: Implementar latency/cost desde traces locales

Estado: pending
Prioridad: must

Objetivo:
Extraer metricas de latencia y coste desde metadata de trazas sin inventar valores cuando faltan.

Archivos permitidos:
- `hydra/backend/src/hydra_api/evals_metrics.py`
- `hydra/backend/src/hydra_api/observability.py`

Dependencias:
- TASK-OBS-004
- TASK-EVAL-007

Requisitos:
- Crear helper `latency_cost_metrics(trace_metadata)` o equivalente.
- Aceptar latencia en ms si esta disponible.
- Aceptar tokens/coste si el proveedor lo devuelve.
- Si falta coste, devolver `None`/`unknown`, no `0` salvo que realmente venga como cero.
- No llamar Langfuse real.

Criterios de aceptacion:
- Metadata con latencia y coste devuelve ambos.
- Metadata sin coste conserva coste desconocido.
- Metadata vacia no falla.

Errores probables a evitar:
- Inventar coste estimado sin fuente.
- Mezclar segundos y milisegundos sin normalizar.

Edge cases obligatorios:
- Latencia negativa debe fallar o ignorarse con warning.
- Coste como string debe normalizarse o rechazarse.
- Tokens ausentes no deben romper eval.

Stop conditions:
- Se necesita consultar Langfuse Cloud real para calcular la metrica local.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "from hydra_api.evals_metrics import latency_cost_metrics; m=latency_cost_metrics({'latency_ms':123,'cost_usd':0.01}); assert m.latency_ms==123; assert m.cost_usd==0.01; assert latency_cost_metrics({}).cost_usd is None; print('latency cost ok')"`

## TASK-EVAL-009: Crear groundedness judge inyectable

Estado: pending
Prioridad: must

Objetivo:
Implementar la interfaz y parser del judge de groundedness para poder evaluar con fake local y usar LLM real solo cuando se apruebe.

Archivos permitidos:
- `hydra/backend/src/hydra_api/evals_judges.py`

Dependencias:
- TASK-EVAL-005
- TASK-COUNCIL-007

Requisitos:
- Crear prompt builder que pida evaluar groundedness contra evidencias recuperadas.
- Crear parser que solo acepte labels controlados: `pass`, `warning`, `fail`.
- Crear `GroundednessJudge` o callable inyectable.
- No llamar modelo real en import time ni en verificaciones locales.
- No enviar documentos completos al prompt; usar evidencias recortadas.

Criterios de aceptacion:
- Judge fake puede devolver `pass`, `warning` o `fail`.
- Parser rechaza labels desconocidos.
- Prompt incluye instrucciones de no afirmar mas alla de evidencias.

Errores probables a evitar:
- Usar el mismo modelo de generacion como judge real sin explicitacion/aprobacion.
- Aceptar texto libre del judge como pass.
- Enviar briefing/respuesta completa si es demasiado larga sin recorte.

Edge cases obligatorios:
- Evidencias vacias deben favorecer `fail` o `warning`, no pass automatico.
- Judge devuelve JSON mal formado.
- Judge devuelve label en mayusculas.

Stop conditions:
- La implementacion requiere llamar modelo real para probar.
- Se necesita cambiar politica de groundedness de SDD.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "exec('from hydra_api.evals_judges import parse_groundedness_label, build_groundedness_prompt\nassert parse_groundedness_label(\"PASS\")==\"pass\"\nok=False\ntry: parse_groundedness_label(\"maybe\")\nexcept Exception: ok=True\nassert ok\nassert \"evidencia\" in build_groundedness_prompt(\"respuesta\", [\"ev\"]).lower()\nprint(\"groundedness judge ok\")')"`

## TASK-EVAL-010: Crear EvalService inyectable

Estado: pending
Prioridad: must

Objetivo:
Orquestar eval cases contra un servicio de query/briefing inyectable, metricas locales y observabilidad sin requerir DB/modelos reales.

Archivos permitidos:
- `hydra/backend/src/hydra_api/evals_service.py`
- `hydra/backend/src/hydra_api/evals_metrics.py`
- `hydra/backend/src/hydra_api/evals_judges.py`
- `hydra/backend/src/hydra_api/observability.py`

Dependencias:
- TASK-EVAL-009
- TASK-OBS-004
- TASK-RAG-016

Requisitos:
- Crear `EvalService` o equivalente con dependencias inyectables: case_loader, query_service, judge, emitter.
- Ejecutar solo los `case_ids` solicitados.
- Propagar `top_k` del request.
- Calcular metricas por caso: precision, JSON validity si aplica, ontology mapping si aplica, groundedness, coordination caution, latency/cost.
- No abrir DB ni llamar modelos reales por defecto.
- Crear `run_id` unico y seguro.

Criterios de aceptacion:
- Con query_service fake y judge fake, se produce al menos un `EvalResult`.
- Se conserva `trace_id` de la respuesta query si existe.
- Casos solicitados inexistentes fallan con error seguro.

Errores probables a evitar:
- Ejecutar todos los casos cuando el request pide subset.
- Ignorar `top_k`.
- Ocultar errores de metricas y marcar `passed=true` por defecto.

Edge cases obligatorios:
- `case_ids` duplicados.
- Query fake devuelve `trace_id=None`.
- Retrieval vacio y expected docs no vacios.
- Judge unavailable debe producir `warning`/limitacion, no crash no controlado.

Stop conditions:
- Se necesita corpus/DB/modelo real para implementar el servicio basico.
- Se necesita cambiar response schema.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "from hydra_api.evals_service import EvalService; from hydra_api.schemas import EvalCase, QueryResponse, EvalRunRequest; cases=[EvalCase(id='eval_001', question='q', expected_documents=['doc_1'], expected_topics=[], expected_answer_traits=[], tags=[])]; FakeQ=type('FakeQ',(),{'query':lambda self, req: QueryResponse(answer='No hay evidencia suficiente de coordinacion.', retrieved_documents=[], limitations=['sin contexto'], trace_id='trace-q')}); svc=EvalService(case_loader=lambda: cases, query_service=FakeQ(), judge=lambda *a, **k: 'warning'); run=svc.run(EvalRunRequest(case_ids=['eval_001'])); assert run.results[0].trace_id=='trace-q'; print('eval service fake ok')"`

## TASK-EVAL-011: Exportar eval_results.json

Estado: pending
Prioridad: must

Objetivo:
Guardar resultados de evals como backup local JSON en la ruta definida por el contrato.

Archivos permitidos:
- `hydra/backend/src/hydra_api/evals_service.py`
- `hydra/backend/data/outputs/.gitkeep`
- `hydra/backend/data/outputs/eval_results.json`

Dependencias:
- TASK-EVAL-010

Requisitos:
- Crear helper `export_eval_results(run, path=None)` o equivalente.
- Escribir solo bajo `hydra/backend/data/outputs/`.
- Crear el directorio si falta.
- Usar escritura atomica o segura para evitar JSON parcial.
- No incluir secretos, headers, prompts completos, respuestas completas ni documentos completos.
- Mantener `results_path` como `hydra/backend/data/outputs/eval_results.json`.

Criterios de aceptacion:
- Export con run fake crea JSON valido.
- JSON contiene `run_id`, `results`, metricas y `trace_id` si existe.
- No escribe fuera de outputs aunque se pase path inseguro.

Errores probables a evitar:
- Exportar todo el objeto response con documentos completos.
- Permitir path traversal para results.
- Sobrescribir `.gitkeep` o borrar outputs previos sin necesidad.

Edge cases obligatorios:
- Outputs directory no existe.
- Results vacios deben ser validos solo si el servicio decidio no ejecutar casos; si no, error.
- Error de escritura debe ser mensaje seguro.

Stop conditions:
- La exportacion requiere una DB viva o almacenamiento externo.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "import tempfile, pathlib, json; from hydra_api.evals_service import export_eval_results; run=type('Run',(),{'run_id':'eval_run_test','results':[]})(); base=pathlib.Path('data/outputs'); base.mkdir(parents=True, exist_ok=True); d=tempfile.TemporaryDirectory(dir=base); p=pathlib.Path(d.name)/'eval_results.json'; export_eval_results(run, p); data=json.loads(p.read_text()); assert data['run_id']=='eval_run_test'; print('eval export ok')"`

## TASK-EVAL-012: Exponer endpoints de evals

Estado: pending
Prioridad: must

Objetivo:
Implementar `POST /evals/run` y `GET /evals/results` usando `EvalService` inyectable y errores seguros.

Archivos permitidos:
- `hydra/backend/src/hydra_api/main.py`
- `hydra/backend/src/hydra_api/evals_service.py`
- `hydra/backend/src/hydra_api/errors.py`

Dependencias:
- TASK-EVAL-011
- TASK-OBS-005

Requisitos:
- `POST /evals/run` debe aceptar `EvalRunRequest` y devolver `EvalRunResponse` del contrato.
- `GET /evals/results` debe devolver `EvalResultsResponse` leyendo el ultimo export local disponible.
- Permitir `app.state.eval_service` fake para tests sin DB/modelos.
- Si falta `eval_cases.json`, devolver error seguro y no stack trace.
- No ejecutar evals reales si faltan casos/datos.

Criterios de aceptacion:
- `/health` sigue funcionando.
- `POST /evals/run` funciona con servicio fake.
- `GET /evals/results` funciona con results fake/export local.
- Errores no exponen paths absolutos, stack traces ni secretos.

Errores probables a evitar:
- Crear servicio real en import time.
- Bloquear arranque de FastAPI por falta de eval_cases.
- Devolver `results_path` distinto al contrato.

Edge cases obligatorios:
- `case_ids=[]` devuelve 422 por validacion.
- Archivo de resultados ausente devuelve respuesta segura vacia o error controlado documentado.
- Results JSON corrupto no crashea con stack trace expuesto.

Stop conditions:
- Se necesita cambiar el contrato API.
- El endpoint requiere DB/modelos reales para pasar test con fake.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "from fastapi.testclient import TestClient; from hydra_api.main import app; assert TestClient(app).get('/health').status_code==200; print('health ok')"`
- `cd hydra/backend && uv run python -c "from fastapi.testclient import TestClient; from hydra_api.main import app; Fake=type('Fake',(),{'run':lambda self, req: type('Run',(),{'run_id':'eval_run_001','results_path':'hydra/backend/data/outputs/eval_results.json','trace_id':'trace-eval','results':[]})()}); app.state.eval_service=Fake(); res=TestClient(app).post('/evals/run', json={'case_ids':['eval_001'],'top_k':5}); assert res.status_code==200 and res.json()['run_id']=='eval_run_001'; del app.state.eval_service; print('eval run fake endpoint ok')"`

## TASK-EVAL-013: Enviar scores a Langfuse de forma opcional

Estado: pending
Prioridad: must

Objetivo:
Enviar scores de evals al emitter de observabilidad cuando existe `trace_id`, manteniendo fallback local/no-op sin Langfuse.

Archivos permitidos:
- `hydra/backend/src/hydra_api/evals_service.py`
- `hydra/backend/src/hydra_api/observability.py`

Dependencias:
- TASK-EVAL-012
- TASK-OBS-004

Requisitos:
- Emitir scores por caso para precision, json_validity, ontology_mapping, groundedness, coordination_caution y latency/cost cuando existan.
- Asociar scores al `trace_id` de cada resultado si existe.
- Si no hay `trace_id`, crear/usar trace local o registrar score local sin fallar.
- No llamar Langfuse real en verificaciones locales.
- No duplicar scores si el mismo run se exporta dos veces en una misma ejecucion.

Criterios de aceptacion:
- Con emitter fake, se reciben scores esperados.
- Sin `trace_id`, el servicio no falla.
- Falla del emitter no cambia `passed` ni rompe el endpoint.

Errores probables a evitar:
- Hacer obligatorio Langfuse para que pasen evals.
- Enviar respuestas completas como metadata de score.
- Enviar scores sin nombres estables.

Edge cases obligatorios:
- Metric value boolean debe convertirse de forma consistente.
- Groundedness `warning` debe mapearse a score interpretable sin perder label original.
- Resultado fallido debe emitir score fallido si hay trace.

Stop conditions:
- Se necesita Langfuse real para probar el codigo basico.
- El SDK exige exponer claves en logs.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "from hydra_api.evals_service import emit_eval_scores; calls=[]; E=type('E',(),{'score':lambda self, trace_id, name, value, **kw: calls.append((trace_id,name,value))})(); result=type('R',(),{'trace_id':'trace-1','metrics':type('M',(),{'precision_at_k':1.0,'json_validity':True,'groundedness':'pass'})(),'passed':True})(); emit_eval_scores(E(), result); assert calls; print('eval score fake ok')"`

## TASK-EVAL-014: Crear eval_cases.json real

Estado: blocked
Prioridad: must

Bloqueo:
Requiere corpus real aprobado con IDs de documentos estables, chunks/indexacion funcionando y decision humana sobre preguntas de evaluacion. El repo actual solo contiene templates/fixtures.

Objetivo:
Crear entre 8 y 12 casos reales de evaluacion en `hydra/backend/data/evals/eval_cases.json` alineados con el corpus cerrado aprobado.

Archivos permitidos:
- `hydra/backend/data/evals/eval_cases.json`

Dependencias:
- TASK-EVAL-003
- TASK-CORPUS-031
- TASK-RAG-018

Requisitos:
- Incluir 8-12 objetos con campos: `id`, `question`, `expected_documents`, `expected_topics`, `expected_answer_traits`, `tags`.
- Usar solo `document_id` existentes en el corpus aprobado.
- No inventar documentos, fuentes ni expected docs.
- Cubrir retrieval, groundedness, ontology mapping, coordination caution y limitaciones.
- No incluir documentos completos ni datos sensibles.

Criterios de aceptacion:
- `load_eval_cases()` carga todos los casos.
- Cada caso tiene expected docs o tag explicito que justifica ausencia.
- Hay entre 8 y 12 casos.
- Los IDs referenciados existen en el corpus aprobado.

Errores probables a evitar:
- Crear casos genericos sin expected docs reales.
- Referenciar docs template o inexistentes.
- Meter contenido completo de articulos en el JSON.

Edge cases obligatorios:
- Al menos un caso debe comprobar limitacion/no evidencia suficiente.
- Al menos un caso debe comprobar caution sobre coordinacion.
- Al menos un caso debe comprobar retrieval de documento esperado.

Stop conditions:
- No hay corpus aprobado o IDs estables.
- El usuario no ha aprobado versionar estos eval cases.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "from hydra_api.evals_service import load_eval_cases; cases=load_eval_cases(); assert 8 <= len(cases) <= 12; print('real eval cases ok')"`

## TASK-EVAL-015: Ejecutar evals reales y revisar resultados

Estado: blocked
Prioridad: must

Bloqueo:
Requiere `eval_cases.json` real, DB local inicializada, chunks con embeddings reales, `/query` funcional, modelo/judge aprobados, Langfuse opcional configurado y aprobacion explicita para coste/red.

Objetivo:
Ejecutar los evals reales del MVP, exportar resultados y revisar fallos antes de demo.

Archivos permitidos:
- `hydra/backend/data/outputs/eval_results.json`

Dependencias:
- TASK-EVAL-014
- TASK-EVAL-013
- TASK-OBS-008
- TASK-RAG-020
- TASK-BRIEF-007

Requisitos:
- Ejecutar evals contra el corpus cerrado aprobado.
- Exportar `hydra/backend/data/outputs/eval_results.json`.
- Enviar scores a Langfuse si hay claves y aprobacion.
- Revisar manualmente casos de groundedness y coordination caution.
- No imprimir secretos, headers, prompts completos, respuestas completas ni documentos completos.

Criterios de aceptacion:
- `eval_results.json` existe y es JSON valido.
- Cada caso tiene metricas y `passed` calculado.
- Fallos quedan explicados con limitacion o task de repair.
- Hay `trace_id` local o Langfuse por caso.

Errores probables a evitar:
- Ejecutar con corpus incompleto y marcar pass.
- Reintentar llamadas reales sin control de coste.
- Subir contenido completo a Langfuse.

Edge cases obligatorios:
- Caso sin documentos recuperados.
- Judge devuelve `warning` o falla.
- Langfuse caido: conservar export local.

Stop conditions:
- Falta corpus, DB, embeddings, modelo, judge o aprobacion.
- Los resultados contienen secretos o documentos completos.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "print('Run real evals only after user approval and local secrets are configured')"`
