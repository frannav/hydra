# Tasks - Council y briefing

## Reglas de atomizacion

- Ejecutar estas tareas en orden, despues de las tareas core de RAG indicadas como dependencias.
- Mantener council y briefing dentro de `hydra/backend/`; no tocar frontend.
- No crear ni modificar `.env` reales.
- No llamar modelos reales, embeddings, Langfuse, DB viva ni red externa en verificaciones de tareas `pending` salvo que la tarea lo indique explicitamente.
- Usar fakes, callables inyectados o fixtures en verificaciones locales.
- No descargar, scrapear, buscar ni inventar documentos reales.
- No versionar documentos reales salvo aprobacion explicita.
- No crear Neo4j, grafo ni sinks nuevos en esta mission.
- No cambiar nombres de variables de entorno definidos en SDD.
- No cambiar el contrato de `POST /briefing` salvo validaciones seguras compatibles.
- El council son chains secuenciales con roles; no introducir agentes autonomos, memoria externa ni herramientas no especificadas.
- Todo briefing debe incluir evidencias o limitaciones.
- No afirmar coordinacion, intencion, atribucion o causalidad sin evidencia explicita recuperada.
- No imprimir secretos, headers, stack traces, prompts completos, respuestas completas del modelo ni documentos completos.
- No marcar tareas como `done` hasta que Codex/reviewer revise diff, comandos y secretos.

## Contexto importante

Council y briefing consumen artefactos producidos por misiones anteriores:

- `TASK-RAG-016` define el servicio de consulta RAG reutilizable.
- `TASK-RAG-017` expone `POST /query` y permite servicio fake via `app.state.query_service`.
- `BriefingRequest`, `BriefingResponse`, `CouncilReview`, `RiskLevel` y `RetrievedDocument` viven en `hydra/backend/src/hydra_api/schemas.py`.
- El contrato de `POST /briefing` vive en `sdd/03-api-contract.md`.
- El briefing debe reutilizar retrieval/evidencias; no debe crear un pipeline paralelo de busqueda.

Por eso esta carpeta separa:

- prompts y helpers verificables sin red;
- orquestacion de council con fakes;
- endpoint `POST /briefing` con servicio fake;
- smoke tests reales, que quedan bloqueados hasta tener RAG real, corpus, DB y claves aprobadas.

## Lecciones incorporadas antes de la mission council/briefing

- Alinear schemas y respuestas con `sdd/03-api-contract.md` y `backend/src/hydra_api/schemas.py`.
- Mantener clientes de modelo y servicios lazy; nada de llamadas en import time.
- No aceptar preguntas vacias ni `top_k <= 0`.
- No generar briefings analiticos si retrieval no devuelve contexto.
- Incluir siempre limitacion de corpus cerrado y sesgo de seleccion.
- Recortar evidencias; no pasar ni devolver documentos completos.
- Separar prompts, parsers, council service, briefing service y endpoint.
- Permitir inyeccion de fakes para verificaciones locales sin DB ni modelo real.
- Si `use_council=false` se recibe explicitamente, no ejecutar revisores, pero mantener limitaciones y evidencia; por defecto el briefing debe usar council.
- No resetear ni modificar documentos, chunks, embeddings ni extracciones desde esta mission.
- No introducir dependencias nuevas fuera de las ya declaradas por RAG.
- Mantener errores API seguros sin secretos, headers ni stack traces.

## Errores probables a evitar

- Crear un segundo retriever o busqueda SQL distinta de la capa RAG ya definida.
- Llamar al proveedor LLM al importar `main.py`, `council_service.py` o `briefing_service.py`.
- Enviar documentos completos al prompt del council o devolverlos en Markdown.
- Aceptar `question="   "` o `top_k=0` y producir un briefing ambiguo.
- Convertir ausencia de evidencia en una conclusion analitica.
- Tratar `risk_level` como texto libre fuera de `bajo`, `medio`, `alto`.
- Devolver `council_review.evidence_supported=true` si hay claims no respaldadas.
- Usar `use_council=false` como excusa para omitir limitaciones.
- Exponer excepciones de proveedor, prompts completos o respuestas completas en logs/API.
- Tocar `hydra/frontend/`, Neo4j, evals, observabilidad o docs historicos en esta mission.

## Edge cases obligatorios

- Pregunta vacia o solo espacios debe fallar validacion.
- `top_k` omitido debe usar `5`.
- `top_k <= 0` debe fallar validacion antes de llegar al retriever.
- `use_council` omitido debe usar council por defecto.
- Retrieval sin resultados debe devolver briefing con limitaciones, no inventar hallazgos.
- Evidence vacia, muy larga o con saltos de linea debe recortarse y mantenerse legible.
- Claims de coordinacion/intencion/atribucion deben marcarse como no soportadas salvo evidencia explicita.
- Riesgo invalido devuelto por un fake/modelo debe normalizarse a valor seguro o producir limitacion controlada.
- Respuesta vacia de una chain debe producir limitacion o error seguro.
- Endpoint debe poder probarse con un servicio fake sin DB ni modelo real.
- Si no hay Langfuse, `trace_id` debe ser un ID local seguro o reutilizar el `trace_id` de RAG.

## Stop conditions generales

- La tarea requiere cambiar el contrato de `POST /briefing` en `sdd/03-api-contract.md`.
- La tarea requiere cambiar schemas canonicos, tablas, dimension de embeddings o modelo de datos.
- La tarea requiere documentos reales, corpus aprobado, DB viva o claves reales y no esta marcada como `blocked`.
- La tarea requiere llamar un proveedor LLM/embedding o Langfuse en una verificacion local no bloqueada.
- La tarea necesita tocar frontend, Neo4j, `.env` reales, docs historicos o archivos fuera de scope.
- La implementacion no puede reutilizar el servicio RAG existente y necesita un pipeline paralelo.
- La verificacion no puede ejecutarse sin datos o servicios que todavia no existen.
- Se necesita anadir estados de riesgo distintos de `bajo`, `medio`, `alto`.

## Milestones sugeridos para Droid Missions

| Milestone | Tareas | Objetivo | Debe parar para review |
|---|---|---|---|
| 1 | TASK-BRIEF-001 a TASK-BRIEF-002 | Validacion de request y constantes de briefing | Si cambia contrato API o env vars |
| 2 | TASK-COUNCIL-001 a TASK-COUNCIL-004 | Prompts de roles del council | Si el prompt permite claims sin evidencia |
| 3 | TASK-COUNCIL-005 a TASK-COUNCIL-007 | Parsers, servicio inyectable y factories lazy | Si llama modelo real o requiere credenciales en verificacion |
| 4 | TASK-BRIEF-003 a TASK-BRIEF-006 | Servicio y endpoint `POST /briefing` con fakes | Si responde sin evidencias/limitaciones |
| 5 | TASK-COUNCIL-008 y TASK-BRIEF-007 | Operaciones reales bloqueadas | Bloqueado hasta RAG, corpus, DB y claves |

## TASK-BRIEF-001: Validar BriefingRequest

Estado: pending
Prioridad: must

Objetivo:
Asegurar que `POST /briefing` recibe preguntas no vacias, `top_k` valido y usa council por defecto sin cambiar los nombres del contrato.

Archivos permitidos:
- `hydra/backend/src/hydra_api/schemas.py`

Dependencias:
- TASK-RAG-003

Requisitos:
- Mantener campos del contrato: `question`, `top_k`, `use_council`.
- `question` debe rechazarse si esta vacia o solo contiene espacios.
- `top_k` debe tener default `5`.
- `top_k` debe rechazar valores menores que `1`.
- `use_council` debe tener default `True` para alinear con `sdd/rag-pipeline.md`.
- Si el cliente envia `use_council=false`, el request sigue siendo valido.
- No anadir campos nuevos al request.
- No tocar schemas de documentos, extracciones, grafo ni evals.

Criterios de aceptacion:
- `BriefingRequest(question="texto")` usa `top_k=5`.
- `BriefingRequest(question="texto")` usa `use_council=True`.
- `BriefingRequest(question="   ")` falla.
- `BriefingRequest(question="texto", top_k=0)` falla.
- `BriefingRequest(question="texto", use_council=False)` es valido.

Errores probables a evitar:
- Cambiar el nombre de `question`, `top_k` o `use_council`.
- Permitir `top_k=0` y luego devolver contexto vacio ambiguo.
- Hacer obligatorio `use_council` aunque el contrato lo envie como booleano.

Edge cases obligatorios:
- Espacios, tabs y saltos de linea cuentan como pregunta vacia.
- `top_k` omitido debe ser exactamente `5`.
- `use_council=false` explicito no debe convertirse silenciosamente a `true`.

Stop conditions:
- Cambiar el default de `use_council` se considera incompatible con una decision SDD posterior.
- Se necesita cambiar el contrato de `POST /briefing`.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "from pydantic import ValidationError; from hydra_api.schemas import BriefingRequest; assert BriefingRequest(question='q').top_k==5; assert BriefingRequest(question='q').use_council is True; assert BriefingRequest(question='q', use_council=False).use_council is False; print('briefing defaults ok')"`
- `cd hydra/backend && uv run python -c "from pydantic import ValidationError; from hydra_api.schemas import BriefingRequest; bad=[];\nfor payload in ({'question':'   '},{'question':'q','top_k':0}):\n    try: BriefingRequest(**payload)\n    except ValidationError: bad.append(payload)\nassert len(bad)==2; print('briefing validation ok')"`

## TASK-BRIEF-002: Definir constantes de briefing

Estado: pending
Prioridad: must

Objetivo:
Centralizar secciones y limitaciones obligatorias del briefing sin crear nuevas variables de entorno.

Archivos permitidos:
- `hydra/backend/src/hydra_api/briefing_config.py`

Dependencias:
- TASK-BRIEF-001

Requisitos:
- Crear `BRIEFING_TITLE = "Briefing de inteligencia narrativa"`.
- Crear `MANDATORY_CORPUS_LIMITATION` con una frase clara sobre corpus cerrado y sesgo de seleccion.
- Crear `REQUIRED_BRIEFING_SECTIONS` con secciones minimas: pregunta, hallazgos con evidencia, riesgo, limitaciones, fuentes recuperadas.
- Crear un limite de longitud para evidencias usadas en briefing o reutilizar el limite RAG si existe.
- No leer Settings ni entorno en import time.
- No abrir DB ni crear clientes de modelo.

Criterios de aceptacion:
- El modulo es importable sin `.env`.
- La limitacion obligatoria menciona corpus cerrado o corpus disponible.
- Las secciones requeridas incluyen limitaciones y evidencias/fuentes.

Errores probables a evitar:
- Crear variables de entorno nuevas para texto de briefing.
- Colocar prompts largos o documentos de ejemplo en configuracion.

Edge cases obligatorios:
- El limite de evidencia debe ser mayor que cero.
- Las secciones deben ser strings estables y reutilizables por tests.

Stop conditions:
- Se necesita cambiar la estructura publica del response de `POST /briefing`.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "from hydra_api.briefing_config import BRIEFING_TITLE, MANDATORY_CORPUS_LIMITATION, REQUIRED_BRIEFING_SECTIONS, BRIEFING_EVIDENCE_SNIPPET_CHARS; assert 'Briefing' in BRIEFING_TITLE; assert 'corpus' in MANDATORY_CORPUS_LIMITATION.lower(); assert any('limit' in s.lower() for s in REQUIRED_BRIEFING_SECTIONS); assert BRIEFING_EVIDENCE_SNIPPET_CHARS>0; print('briefing config ok')"`

## TASK-COUNCIL-001: Crear prompt de Narrative Analyst

Estado: pending
Prioridad: should

Objetivo:
Definir el prompt del analista narrativo para producir un borrador grounded desde pregunta y evidencias recuperadas.

Archivos permitidos:
- `hydra/backend/src/hydra_api/council_prompts.py`

Dependencias:
- TASK-BRIEF-002
- TASK-RAG-011

Requisitos:
- Crear `build_narrative_analyst_prompt(question, retrieved_documents)` o helper equivalente.
- Incluir la pregunta del usuario.
- Incluir solo evidencias breves con `document_id`, `chunk_id`, titulo/fuente si existen y score si procede.
- Instruir al modelo a distinguir recurrencia, similitud narrativa, amplificacion y coordinacion.
- Prohibir afirmar coordinacion, intencion o atribucion sin evidencia explicita.
- Instruir a declarar limitaciones si la evidencia es insuficiente.
- No imprimir ni loggear el prompt.

Criterios de aceptacion:
- El helper devuelve texto importable y determinista.
- El prompt contiene la pregunta y la evidencia recortada.
- El prompt contiene la regla de no coordinacion sin evidencia.
- Con lista vacia, el prompt no invita a inventar hallazgos.

Errores probables a evitar:
- Pedir inferencias no respaldadas.
- Pasar documentos completos al prompt.
- Omitir metadatos trazables de la evidencia.

Edge cases obligatorios:
- Evidence con saltos de linea debe mantenerse legible.
- Evidence muy larga debe recortarse.
- Lista vacia debe producir instrucciones de limitacion.

Stop conditions:
- Se necesita cambiar la politica analitica del producto.
- El helper requiere DB/modelo real para construirse.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "from hydra_api.council_prompts import build_narrative_analyst_prompt; p=build_narrative_analyst_prompt('q', []); assert 'q' in p and ('limitacion' in p.lower() or 'insuficiente' in p.lower()); print('analyst empty prompt ok')"`
- `cd hydra/backend && uv run python -c "from hydra_api.council_prompts import build_narrative_analyst_prompt; docs=[{'document_id':'doc1','chunk_id':'c1','title':'T','source':'S','score':0.9,'evidence':'ev'}]; p=build_narrative_analyst_prompt('q', docs); assert 'doc1' in p and 'ev' in p and 'coordinacion' in p.lower(); print('analyst prompt ok')"`

## TASK-COUNCIL-002: Crear prompt de Evidence Reviewer

Estado: pending
Prioridad: should

Objetivo:
Definir el prompt que revisa si el borrador analitico esta soportado por las evidencias recuperadas.

Archivos permitidos:
- `hydra/backend/src/hydra_api/council_prompts.py`

Dependencias:
- TASK-COUNCIL-001

Requisitos:
- Crear `build_evidence_reviewer_prompt(draft_markdown, retrieved_documents)` o helper equivalente.
- Pedir salida estructurada con:
  - `evidence_supported` booleano;
  - `unsupported_claims` lista breve;
  - explicacion corta.
- Ordenar marcar como unsupported cualquier claim sin cita/evidencia.
- Ordenar marcar coordinacion/intencion/atribucion como unsupported salvo evidencia explicita.
- Incluir evidencias recortadas, no documentos completos.
- No imprimir ni loggear prompt, draft completo ni documentos completos.

Criterios de aceptacion:
- El prompt contiene el borrador recibido.
- El prompt exige `evidence_supported` y `unsupported_claims`.
- El prompt contiene reglas contra claims no respaldadas.

Errores probables a evitar:
- Pedir al reviewer que mejore el texto en vez de auditar evidencia.
- Hacer que el reviewer pueda aceptar claims sin cita.

Edge cases obligatorios:
- Draft vacio debe ser tratado como no soportado.
- Sin evidencias recuperadas, todo claim analitico debe considerarse no soportado.

Stop conditions:
- Se necesita cambiar el schema publico de `CouncilReview`.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "from hydra_api.council_prompts import build_evidence_reviewer_prompt; p=build_evidence_reviewer_prompt('draft', []); low=p.lower(); assert 'evidence_supported' in p and 'unsupported_claims' in p and ('no soport' in low or 'unsupported' in low); print('evidence reviewer prompt ok')"`

## TASK-COUNCIL-003: Crear prompt de Risk Reviewer

Estado: pending
Prioridad: should

Objetivo:
Definir el prompt que revisa y justifica el nivel de riesgo del briefing usando solo evidencias recuperadas.

Archivos permitidos:
- `hydra/backend/src/hydra_api/council_prompts.py`

Dependencias:
- TASK-COUNCIL-001

Requisitos:
- Crear `build_risk_reviewer_prompt(draft_markdown, retrieved_documents)` o helper equivalente.
- Permitir solo risk levels `bajo`, `medio`, `alto`.
- Exigir justificacion breve basada en evidencias.
- Exigir limitacion si no hay evidencia suficiente para estimar riesgo.
- Prohibir escalar riesgo por intuicion, tono alarmista o claims no respaldadas.
- No imprimir ni loggear prompt, draft completo ni documentos completos.

Criterios de aceptacion:
- El prompt contiene los tres valores permitidos.
- El prompt exige justificar riesgo con evidencia.
- El prompt contiene una instruccion de limitacion por evidencia insuficiente.

Errores probables a evitar:
- Devolver risk level libre como `critical` o `indeterminado` sin actualizar schema.
- Elevar riesgo por especulacion.

Edge cases obligatorios:
- Sin evidencias, el reviewer debe indicar limitacion y no inventar riesgo.
- Si el draft contiene riesgo no soportado, debe pedir correccion.

Stop conditions:
- Se necesita anadir un nuevo valor al enum `RiskLevel`.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "from hydra_api.council_prompts import build_risk_reviewer_prompt; p=build_risk_reviewer_prompt('draft', []); low=p.lower(); assert all(x in low for x in ['bajo','medio','alto']); assert 'evidencia' in low and ('limitacion' in low or 'insuficiente' in low); print('risk reviewer prompt ok')"`

## TASK-COUNCIL-004: Crear prompt de Final Synthesizer

Estado: pending
Prioridad: must

Objetivo:
Definir el prompt que genera el briefing final incorporando revision de evidencia, revision de riesgo y limitaciones obligatorias.

Archivos permitidos:
- `hydra/backend/src/hydra_api/council_prompts.py`

Dependencias:
- TASK-COUNCIL-002
- TASK-COUNCIL-003
- TASK-BRIEF-002

Requisitos:
- Crear `build_final_synthesizer_prompt(question, analyst_draft, evidence_review, risk_review, retrieved_documents)` o helper equivalente.
- Exigir Markdown final con secciones de `REQUIRED_BRIEFING_SECTIONS`.
- Exigir que cada hallazgo tenga referencia a evidencia recuperada o se convierta en limitacion.
- Exigir incluir `MANDATORY_CORPUS_LIMITATION`.
- Exigir eliminar o marcar claims unsupported.
- Prohibir anadir hechos nuevos no presentes en draft/evidencias/reviews.
- No imprimir ni loggear prompt, draft completo, reviews completas ni documentos completos.

Criterios de aceptacion:
- El prompt incluye titulo/secciones de briefing.
- El prompt incluye la limitacion obligatoria de corpus.
- El prompt instruye a eliminar o limitar claims no soportadas.

Errores probables a evitar:
- Usar el final synthesizer para inventar nuevas conclusiones.
- Omitir limitaciones si el reviewer aprueba el draft.

Edge cases obligatorios:
- Si `evidence_supported=false`, el prompt debe pedir correccion o limitacion.
- Si no hay retrieved documents, debe producir briefing de limitacion.

Stop conditions:
- Se necesita cambiar el contrato para devolver un objeto estructurado distinto del Markdown.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "from hydra_api.council_prompts import build_final_synthesizer_prompt; p=build_final_synthesizer_prompt('q','draft',{'evidence_supported':False,'unsupported_claims':['x']},{'risk_level':'medio','risk_review':'r'},[]); low=p.lower(); assert 'briefing' in low and 'limitacion' in low and ('unsupported' in low or 'no soport' in low); print('final synthesizer prompt ok')"`

## TASK-COUNCIL-005: Crear parsers seguros del council

Estado: pending
Prioridad: must

Objetivo:
Convertir salidas de reviewers en estructuras seguras sin confiar en texto libre del modelo.

Archivos permitidos:
- `hydra/backend/src/hydra_api/council_service.py`

Dependencias:
- TASK-COUNCIL-004

Requisitos:
- Crear helpers puros para normalizar `risk_level` a `RiskLevel`.
- Crear helper para construir `CouncilReview` desde dict/texto seguro.
- Si `unsupported_claims` no es lista, convertirlo en lista segura o usar `[]` con explicacion.
- Si `evidence_supported` falta o es ambiguo, usar `False`.
- Si `risk_review` falta o esta vacio, generar mensaje seguro de limitacion.
- No evaluar codigo, no usar `eval`, no ejecutar JSON no confiable como codigo.
- No abrir DB, no crear clientes de modelo y no leer Settings.

Criterios de aceptacion:
- Risk level invalido se normaliza sin romper el schema.
- `CouncilReview` resultante valida con Pydantic.
- Los helpers son importables sin `.env`.

Errores probables a evitar:
- Confiar ciegamente en JSON del modelo.
- Propagar risk levels fuera del enum.
- Exponer texto largo del modelo como error al cliente.

Edge cases obligatorios:
- Dict vacio produce `evidence_supported=False`.
- `unsupported_claims` string se convierte en lista de una entrada breve o se descarta de forma segura.
- `risk_level="critical"` no rompe la respuesta.

Stop conditions:
- Se necesita cambiar `CouncilReview` en `sdd/03-api-contract.md`.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "from hydra_api.council_service import normalize_risk_level, build_council_review; from hydra_api.schemas import RiskLevel, CouncilReview; assert normalize_risk_level('alto')==RiskLevel.alto; assert normalize_risk_level('critical')==RiskLevel.medio; r=build_council_review({}); assert isinstance(r, CouncilReview) and r.evidence_supported is False; print('council parsers ok')"`

## TASK-COUNCIL-006: Crear CouncilService inyectable

Estado: pending
Prioridad: must

Objetivo:
Orquestar analyst, evidence reviewer, risk reviewer y final synthesizer con callables inyectados para pruebas sin modelo real.

Archivos permitidos:
- `hydra/backend/src/hydra_api/council_service.py`

Dependencias:
- TASK-COUNCIL-005

Requisitos:
- Crear `CouncilService` o funcion equivalente.
- Aceptar callables/fakes para:
  - analyst chain;
  - evidence reviewer chain;
  - risk reviewer chain;
  - final synthesizer chain.
- Usar prompts de `council_prompts.py`.
- Devolver resultado interno con:
  - `briefing_markdown`;
  - `risk_level` (`RiskLevel`);
  - `council_review` (`CouncilReview`).
- Si una chain devuelve texto vacio, usar limitacion o error seguro.
- No llamar modelos, DB, Langfuse ni red en import time.
- No imprimir prompts completos, respuestas completas, secretos ni documentos completos.

Criterios de aceptacion:
- Servicio importable sin `.env`.
- Con fakes deterministas devuelve Markdown, risk level y CouncilReview.
- Si evidence reviewer marca unsupported claims, `CouncilReview.evidence_supported` queda `False`.

Errores probables a evitar:
- Instanciar modelo real dentro de `__init__` sin inyeccion.
- Mezclar FastAPI route con logica de council.
- Ocultar unsupported claims.

Edge cases obligatorios:
- Chain fake vacia no debe producir briefing exitoso sin limitacion.
- Excepcion de chain debe poder mapearse a error seguro por el caller.
- Retrieved documents vacios deben activar limitaciones.

Stop conditions:
- Se requiere credencial real para probar el servicio.
- Se necesita memoria externa, herramientas o agentes autonomos.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "from hydra_api.council_service import CouncilService; print(callable(CouncilService))"`
- `cd hydra/backend && uv run python -c "from hydra_api.council_service import CouncilService; f=lambda prompt: 'ok'; s=CouncilService(analyst_chain=f, evidence_reviewer_chain=lambda p: {'evidence_supported': True, 'unsupported_claims': [], 'risk_review': 'ok'}, risk_reviewer_chain=lambda p: {'risk_level':'medio','risk_review':'ok'}, final_synthesizer_chain=lambda p: '# Briefing\n\n## Limitaciones\n- corpus'); r=s.run('q', []); assert r.briefing_markdown and r.council_review.evidence_supported is True and r.risk_level.value=='medio'; print('council service fake ok')"`

## TASK-COUNCIL-007: Crear factories lazy de chains del council

Estado: pending
Prioridad: should

Objetivo:
Construir chains reales del council de forma lazy usando modelos configurados, sin llamadas de red durante import o construccion.

Archivos permitidos:
- `hydra/backend/src/hydra_api/council_service.py`

Dependencias:
- TASK-RAG-001
- TASK-COUNCIL-006

Requisitos:
- Crear `create_council_service(settings=None, chat_model=None, review_model=None)` o factory equivalente.
- Usar `HYDRA_CHAT_MODEL` para analyst/final synthesizer y `HYDRA_REVIEW_MODEL` para reviewers, salvo que se inyecten fakes.
- Usar `MODEL_API_KEY` y `MODEL_API_BASE_URL` existentes; no crear env vars nuevas.
- No llamar proveedor real durante import o construccion.
- Permitir sustituir modelos por fakes en tests.
- No registrar prompts completos ni respuestas completas.

Criterios de aceptacion:
- El modulo importa sin `.env` si no se construye el servicio real.
- Con Settings fake o env fake se puede construir la factory sin red.
- No se anaden dependencias nuevas fuera de RAG.

Errores probables a evitar:
- Usar un modelo distinto de los configurados en Settings.
- Leer secretos en import time.
- Llamar al proveedor durante verificacion local.

Edge cases obligatorios:
- Si falta `MODEL_API_KEY` al construir servicio real, debe fallar con error seguro aguas arriba.
- Si `review_model` no se inyecta, usar el modelo de revision configurado.

Stop conditions:
- El proveedor exige credenciales reales durante construccion.
- Se necesita una dependencia nueva no prevista por RAG.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "import hydra_api.council_service as c; assert hasattr(c, 'create_council_service'); print('council factory import ok')"`
- `cd hydra/backend && MODEL_API_KEY=fake MODEL_API_BASE_URL=https://example.invalid/v1 uv run python -c "from hydra_api.council_service import create_council_service; service=create_council_service(); assert service is not None; print('council factory ok')"`

## TASK-BRIEF-003: Crear respuesta de briefing sin contexto

Estado: pending
Prioridad: must

Objetivo:
Bloquear briefings inventados cuando retrieval no devuelve evidencia util.

Archivos permitidos:
- `hydra/backend/src/hydra_api/briefing_service.py`

Dependencias:
- TASK-BRIEF-002
- TASK-COUNCIL-005

Requisitos:
- Crear `build_no_context_briefing_response(question, trace_id, use_council=True)` o helper equivalente.
- Devolver `BriefingResponse` con:
  - `briefing_markdown` indicando que no hay contexto suficiente;
  - `risk_level` valido;
  - `council_review` seguro si `use_council=True`, o `None` si `use_council=False`;
  - `trace_id` recibido.
- Incluir `MANDATORY_CORPUS_LIMITATION`.
- No llamar chat model si no hay documentos recuperados.
- No mencionar causas no verificadas.

Criterios de aceptacion:
- La respuesta cumple schema `BriefingResponse`.
- Incluye limitacion sobre corpus disponible.
- Preserva el `trace_id` recibido.
- No necesita DB ni modelo real.

Errores probables a evitar:
- Generar un briefing generico no basado en corpus.
- Devolver HTTP error en vez de respuesta con limitacion para ausencia de contexto.
- Marcar `evidence_supported=True` sin evidencias.

Edge cases obligatorios:
- Pregunta valida pero DB sin embeddings debe entrar en este path.
- `use_council=False` debe omitir `council_review` sin omitir limitaciones.
- `trace_id` local debe preservarse.

Stop conditions:
- Producto decide que ausencia de contexto debe ser otro codigo HTTP o un risk level nuevo.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "from hydra_api.briefing_service import build_no_context_briefing_response; r=build_no_context_briefing_response('q','trace-local'); assert 'corpus' in r.briefing_markdown.lower() and r.trace_id=='trace-local' and r.council_review.evidence_supported is False; print('no-context briefing ok')"`
- `cd hydra/backend && uv run python -c "from hydra_api.briefing_service import build_no_context_briefing_response; r=build_no_context_briefing_response('q','trace-local', use_council=False); assert r.council_review is None and r.trace_id=='trace-local'; print('no-context no-council ok')"`

## TASK-BRIEF-004: Crear borrador grounded de briefing

Estado: pending
Prioridad: must

Objetivo:
Crear un borrador de briefing Markdown desde una respuesta RAG ya grounded, sin llamar modelos ni retrieval adicional.

Archivos permitidos:
- `hydra/backend/src/hydra_api/briefing_service.py`

Dependencias:
- TASK-BRIEF-003
- TASK-RAG-016

Requisitos:
- Crear `build_briefing_draft(question, query_response)` o helper equivalente.
- Usar `QueryResponse.answer` solo como borrador grounded.
- Incluir documentos recuperados con `document_id`, `chunk_id`, titulo, fuente, score y evidencia breve.
- Incluir `MANDATORY_CORPUS_LIMITATION`.
- No anadir claims que no esten en la respuesta RAG o evidencias.
- No incluir documentos completos ni prompts.

Criterios de aceptacion:
- Con `QueryResponse` con documentos, el Markdown incluye evidencias y fuentes.
- Con `QueryResponse` sin documentos, delega o recomienda el path sin contexto.
- Incluye seccion de limitaciones.

Errores probables a evitar:
- Tratar la respuesta RAG como verdad sin evidencias.
- Duplicar retrieval dentro del constructor.
- Omitir scores o IDs trazables.

Edge cases obligatorios:
- Evidence muy larga debe recortarse.
- Score ausente o no numerico no debe romper el Markdown si el schema ya valido lo evita.
- Limitaciones existentes de `QueryResponse` deben preservarse.

Stop conditions:
- Se necesita acceder a DB o documentos raw para completar el draft.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "from hydra_api.briefing_service import build_briefing_draft; from hydra_api.schemas import QueryResponse, RetrievedDocument; q=QueryResponse(answer='A', retrieved_documents=[RetrievedDocument(document_id='doc1', chunk_id='c1', title='T', source='S', score=0.8, evidence='ev')], limitations=['lim'], trace_id='t'); md=build_briefing_draft('q', q); assert 'doc1' in md and 'ev' in md and 'lim' in md.lower(); print('briefing draft ok')"`

## TASK-BRIEF-005: Crear BriefingService inyectable

Estado: pending
Prioridad: must

Objetivo:
Orquestar QueryService, borrador grounded, council opcional y respuesta `BriefingResponse` para `POST /briefing`.

Archivos permitidos:
- `hydra/backend/src/hydra_api/briefing_service.py`

Dependencias:
- TASK-BRIEF-004
- TASK-COUNCIL-006
- TASK-RAG-016

Requisitos:
- Crear `BriefingService` o funcion equivalente.
- Aceptar `query_service` y `council_service` inyectables.
- Convertir `BriefingRequest` en consulta RAG sin cambiar pregunta ni `top_k`.
- Reutilizar `trace_id` de `QueryResponse` si existe; si no, generar ID local seguro.
- Si retrieval devuelve `[]`, usar no-context path sin llamar council/modelo.
- Si hay documentos y `use_council=True`, ejecutar council service.
- Si hay documentos y `use_council=False`, devolver borrador grounded con `council_review=None` y limitaciones.
- Construir `BriefingResponse` segun contrato.
- No abrir DB/modelos en import time.
- No imprimir pregunta completa, evidencias completas, secretos ni stack traces.

Criterios de aceptacion:
- Servicio importable sin `.env` ni DB.
- Con query fake vacio devuelve no-context briefing.
- Con query fake con evidencia y council fake devuelve briefing final con `CouncilReview`.
- Con `use_council=False` no llama al council fake.

Errores probables a evitar:
- Mezclar FastAPI route con logica de briefing.
- Crear un retriever alternativo en vez de usar `query_service`.
- Omitir `trace_id`.

Edge cases obligatorios:
- QueryService devuelve documentos pero council devuelve texto vacio: debe producir limitacion o error seguro.
- Excepcion de query/council debe poder mapearse a error seguro en endpoint.
- `use_council=False` no debe omitir limitaciones ni evidencias.

Stop conditions:
- Se requiere Langfuse real para generar `trace_id`.
- Se requiere cambiar `QueryResponse` o `BriefingResponse`.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "from hydra_api.briefing_service import BriefingService; print(callable(BriefingService))"`
- `cd hydra/backend && uv run python -c "from hydra_api.briefing_service import BriefingService; from hydra_api.schemas import BriefingRequest, QueryResponse; Q=type('Q', (), {'query': lambda self, request: QueryResponse(answer='Sin contexto suficiente.', retrieved_documents=[], limitations=['Corpus sin embeddings.'], trace_id='trace-q')}); s=BriefingService(query_service=Q(), council_service=None); r=s.brief(BriefingRequest(question='q')); assert r.trace_id=='trace-q' and r.council_review.evidence_supported is False; print('briefing service no-context ok')"`
- `cd hydra/backend && uv run python -c "from hydra_api.briefing_service import BriefingService; from hydra_api.schemas import BriefingRequest, QueryResponse, RetrievedDocument, CouncilReview, RiskLevel; Q=type('Q', (), {'query': lambda self, request: QueryResponse(answer='A', retrieved_documents=[RetrievedDocument(document_id='doc1', chunk_id='c1', title='T', source='S', score=0.8, evidence='ev')], limitations=['lim'], trace_id='trace-q')}); C=type('C', (), {'run': lambda self, question, retrieved_documents: type('R', (), {'briefing_markdown':'# Briefing', 'risk_level': RiskLevel.medio, 'council_review': CouncilReview(evidence_supported=True, unsupported_claims=[], risk_review='ok')})()}); s=BriefingService(query_service=Q(), council_service=C()); r=s.brief(BriefingRequest(question='q')); assert r.trace_id=='trace-q' and r.council_review.evidence_supported is True; print('briefing service council fake ok')"`

## TASK-BRIEF-006: Exponer POST /briefing en FastAPI

Estado: pending
Prioridad: must

Objetivo:
Conectar el servicio de briefing al endpoint `POST /briefing` respetando el contrato API.

Archivos permitidos:
- `hydra/backend/src/hydra_api/main.py`
- `hydra/backend/src/hydra_api/briefing_service.py`
- `hydra/backend/src/hydra_api/council_service.py`
- `hydra/backend/src/hydra_api/errors.py`

Dependencias:
- TASK-BRIEF-001
- TASK-BRIEF-005
- TASK-COUNCIL-007
- TASK-RAG-017

Requisitos:
- Crear ruta `POST /briefing`.
- Request: `BriefingRequest`.
- Response: `BriefingResponse`.
- Permitir inyectar servicio fake en tests, por ejemplo via `app.state.briefing_service`.
- Si no hay fake, construir servicio real de forma lazy al recibir request.
- Reutilizar el `QueryService` real existente; no crear pipeline paralelo.
- Mapear errores esperados a respuestas seguras sin stack trace.
- No exponer secretos, headers ni detalles internos.
- No tocar otros endpoints salvo imports necesarios.

Criterios de aceptacion:
- `/health` sigue funcionando.
- `/briefing` puede probarse con fake service sin DB ni modelo real.
- OpenAPI incluye `POST /briefing`.
- El response fake valida como `BriefingResponse`.

Errores probables a evitar:
- Crear el servicio real al importar `main.py`.
- Romper handlers de errores existentes.
- Importar o inicializar modelos reales en tests de endpoint fake.

Edge cases obligatorios:
- Body invalido debe devolver error seguro de FastAPI/Pydantic.
- Servicio fake que devuelve `BriefingResponse` debe pasar tal cual.
- Excepcion controlada del servicio no debe filtrar stack trace.

Stop conditions:
- Implementar `/briefing` requiere DB/modelo real para arrancar la app.
- Hace falta cambiar el contrato documentado.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "from fastapi.testclient import TestClient; from hydra_api.main import app; assert TestClient(app).get('/health').json()['status']=='ok'; print('health ok')"`
- `cd hydra/backend && uv run python -c "from fastapi.testclient import TestClient; from hydra_api.main import app; from hydra_api.schemas import BriefingResponse, CouncilReview, RiskLevel; Fake=type('Fake', (), {'brief': lambda self, request: BriefingResponse(briefing_markdown='# Briefing', risk_level=RiskLevel.medio, council_review=CouncilReview(evidence_supported=True, unsupported_claims=[], risk_review='ok'), trace_id='trace-test')}); app.state.briefing_service=Fake(); res=TestClient(app).post('/briefing', json={'question':'q','top_k':5,'use_council':True}); assert res.status_code==200 and res.json()['trace_id']=='trace-test'; del app.state.briefing_service; print('briefing fake endpoint ok')"`
- `cd hydra/backend && uv run python -c "from fastapi.testclient import TestClient; from hydra_api.main import app; schema=TestClient(app).get('/openapi.json').json(); assert '/briefing' in schema['paths']; print('openapi briefing ok')"`

## TASK-COUNCIL-008: Verificar council real con modelo

Estado: blocked
Prioridad: should

Bloqueo:
Depende de RAG implementado, `MODEL_API_KEY` real configurada en `.env` local no versionado, aprobacion explicita para coste/red y un conjunto de evidencias fake o recuperadas aprobado para smoke test.

Objetivo:
Comprobar que las chains reales del council ejecutan analyst, reviewers y synthesizer sin exponer secretos ni documentos completos.

Archivos permitidos:
- Ninguno

Dependencias:
- TASK-COUNCIL-007
- TASK-RAG-020

Requisitos:
- Ejecutar un smoke test controlado con evidencias breves.
- Usar `HYDRA_CHAT_MODEL` y `HYDRA_REVIEW_MODEL` configurados.
- No imprimir API keys, headers, prompts completos, respuestas completas ni documentos completos.
- Reportar solo conteos, `trace_id` si existe, risk level y si hubo claims unsupported.

Criterios de aceptacion:
- Council devuelve `briefing_markdown`, `risk_level` valido y `CouncilReview`.
- Claims unsupported, si existen, quedan listadas de forma breve.
- No hay secretos ni contenido completo en salida.

Errores probables a evitar:
- Ejecutar con corpus no aprobado.
- Versionar `.env` o documentos reales.
- Copiar respuestas completas del modelo al reporte.

Edge cases obligatorios:
- Si el proveedor devuelve salida no parseable, abortar con error seguro.
- Si el modelo rechaza o vacia una respuesta, reportar limitacion.

Stop conditions:
- Falta clave real, aprobacion de coste/red o modelo configurado.
- Hay dudas sobre exponer contenido del corpus.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "from hydra_api.council_service import create_council_service; print('council service ready')"`

## TASK-BRIEF-007: Verificar POST /briefing real

Estado: blocked
Prioridad: must

Bloqueo:
Depende de corpus real aprobado, DB local inicializada, chunks con embeddings reales, `POST /query` real funcionando, `MODEL_API_KEY` real en `.env` local no versionado y aprobacion explicita para coste/red.

Objetivo:
Comprobar que `POST /briefing` devuelve un briefing real trazable con evidencias, limitaciones, council review y `trace_id`.

Archivos permitidos:
- Ninguno

Dependencias:
- TASK-BRIEF-006
- TASK-COUNCIL-008
- TASK-RAG-020

Requisitos:
- Ejecutar una pregunta de prueba del dominio aprobado.
- Confirmar que el response incluye `briefing_markdown`, `risk_level`, `council_review` y `trace_id`.
- Confirmar que el Markdown incluye limitacion de corpus y evidencias breves.
- No imprimir documentos completos, prompts completos, headers ni secretos.
- No afirmar calidad analitica final sin review humano.

Criterios de aceptacion:
- HTTP status 200 para pregunta valida.
- `risk_level` es `bajo`, `medio` o `alto`.
- `council_review.evidence_supported` es booleano.
- `trace_id` no esta vacio.
- El reporte contiene resumen, no contenido completo del briefing si incluye material sensible.

Errores probables a evitar:
- Ejecutar sin embeddings reales y tratar respuesta sin contexto como exito completo.
- Copiar documentos completos o prompts al reporte.
- Ocultar claims unsupported del council.

Edge cases obligatorios:
- Pregunta fuera de dominio debe devolver limitacion, no inventar briefing.
- Si `use_council=false`, debe quedar claro que no hubo council review.
- Si Langfuse no esta disponible, usar trace local seguro.

Stop conditions:
- Falta corpus, DB, embeddings, clave real o aprobacion de coste/red.
- `/query` real no funciona todavia.
- Hay dudas sobre permisos para usar el corpus real.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "from fastapi.testclient import TestClient; from hydra_api.main import app; schema=TestClient(app).get('/openapi.json').json(); assert '/briefing' in schema['paths']; print('briefing endpoint ready')"`
- `cd hydra/backend && uv run python -c "print('real /briefing smoke requires local server, DB, corpus and MODEL_API_KEY; do not run without approval')"`
