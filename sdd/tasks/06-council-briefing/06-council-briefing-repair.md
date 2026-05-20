# Repair - Mission 06 Council y briefing

## Objetivo

Corregir los bloqueantes detectados en la revision de Mission 06 para que `POST /briefing` use el council por defecto cuando `use_council=true`, mantenga evidencia trazable y recortada, preserve limitaciones obligatorias, y siga siendo verificable localmente sin DB, corpus real, red ni modelos reales.

## Veredicto de revision

Mission 06 no queda aprobada hasta aplicar este repair.

Los checks originales con fakes pasan, pero no cubren el comportamiento real del council ni varias reglas SDD obligatorias.

## Source of truth

Antes de ejecutar este repair, leer:

- `hydra/sdd/README.md`
- `hydra/sdd/01-architecture-decisions.md`
- `hydra/sdd/03-api-contract.md`
- `hydra/sdd/07-implementation-plan.md`
- `hydra/sdd/08-task-checklist.md`
- `hydra/sdd/tasks/06-council-briefing/06-council-briefing.md`
- `hydra/sdd/tasks/06-council-briefing/06-council-briefing-mission.md`

No usar `docs/hydra-brainstorming.md`.

## Archivos permitidos

Solo estos archivos pueden modificarse:

- `hydra/backend/src/hydra_api/main.py`
- `hydra/backend/src/hydra_api/briefing_config.py`
- `hydra/backend/src/hydra_api/briefing_service.py`
- `hydra/backend/src/hydra_api/council_prompts.py`
- `hydra/backend/src/hydra_api/council_service.py`
- `hydra/backend/src/hydra_api/model_client.py`
- `hydra/README.md` solo para revertir o alinear la seccion de Mission 06 con el comportamiento real aprobado por SDD.

## Archivos prohibidos

- `hydra/frontend/**`
- `.env`, `.env.local` o cualquier archivo con secretos reales
- `hydra/backend/data/raw/**`
- `hydra/backend/data/metadata/documents/**`
- `hydra/backend/src/hydra_api/db_schema.py`
- `hydra/backend/src/hydra_api/rag_store.py`
- `hydra/backend/src/hydra_api/rag_retriever.py`
- `hydra/backend/src/hydra_api/rag_indexing.py`
- Neo4j, evals, observabilidad o docs historicos

## Bloqueantes a corregir

1. `POST /briefing` construye `BriefingService(query_service=..., council_service=None)` cuando no hay fake, por lo que `use_council=true` puede devolver `council_review=None`.
2. Las chains reales del council devuelven strings, pero `CouncilService.run()` descarta cualquier salida de reviewer que no sea `dict`.
3. Los prompts del council incluyen evidencias completas sin recorte defensivo.
4. `build_final_synthesizer_prompt()` recibe `retrieved_documents` pero no los incluye en el prompt final.
5. `build_briefing_draft()` puede omitir `MANDATORY_CORPUS_LIMITATION` cuando `QueryResponse.limitations` no esta vacio.
6. `REQUIRED_BRIEFING_SECTIONS` no contiene todas las secciones minimas exigidas: pregunta, hallazgos con evidencia, riesgo, limitaciones y fuentes recuperadas.
7. Una chain vacia puede producir un briefing vacio exitoso si `evidence_supported=True`.
8. `create_council_service()` no acepta inyeccion `settings=None`, `chat_model=None`, `review_model=None`.
9. `README.md` fue modificado fuera del scope original y contiene una nota que no coincide con el SDD/codigo.

## Reglas de repair

- No cambiar el contrato de `POST /briefing`.
- No cambiar schemas canonicos salvo que ya estuvieran definidos por Mission 06.
- No crear retriever paralelo ni tocar RAG store/retriever/indexing.
- No llamar modelos reales, DB viva, Langfuse, red externa ni corpus real en verificaciones.
- Mantener servicios y clientes lazy: nada de llamadas de red, DB o Settings en import time.
- Si `use_council=false`, no ejecutar council y devolver briefing grounded con `council_review=None`.
- Si `use_council=true` y hay documentos, construir council lazy y ejecutar revisores.
- Si no hay documentos recuperados, no llamar council/modelo; devolver limitaciones.
- No imprimir prompts completos, respuestas completas, headers, stack traces, secretos ni documentos completos.

## TASK-REPAIR-06-001: Wirear council real en `/briefing`

Estado: pending
Prioridad: must

Objetivo:
Hacer que el endpoint `POST /briefing` construya de forma lazy un `BriefingService` con `QueryService` real y `CouncilService` real cuando no exista fake inyectado.

Archivos permitidos:

- `hydra/backend/src/hydra_api/main.py`
- `hydra/backend/src/hydra_api/briefing_service.py`
- `hydra/backend/src/hydra_api/council_service.py`

Requisitos:

- Mantener `app.state.briefing_service` como mecanismo de fake.
- Si no hay fake, construir `QueryService` con `create_query_service()`.
- Si no hay fake y hay que crear servicio real, conectar tambien `create_council_service()` o un factory lazy equivalente.
- No instanciar `QueryService`, `CouncilService`, DB ni modelos en import time.
- `use_council=true` con documentos debe devolver `CouncilReview`, no `None`.
- `use_council=false` no debe ejecutar council.

Criterios de aceptacion:

- `/health` sigue funcionando sin `.env`.
- `/briefing` con fake service sigue funcionando sin DB/modelo.
- `BriefingService` con query fake con documentos y council fake devuelve `council_review`.
- `BriefingService` con `use_council=false` no llama al council fake.

Comandos de verificacion:

```bash
cd hydra/backend && uv run python -c "from fastapi.testclient import TestClient; from hydra_api.main import app; assert TestClient(app).get('/health').json()['status']=='ok'; print('health ok')"
cd hydra/backend && uv run python -c "from fastapi.testclient import TestClient; from hydra_api.main import app; from hydra_api.schemas import BriefingResponse, CouncilReview, RiskLevel; Fake=type('Fake', (), {'brief': lambda self, request: BriefingResponse(briefing_markdown='# Briefing', risk_level=RiskLevel.medio, council_review=CouncilReview(evidence_supported=True, unsupported_claims=[], risk_review='ok'), trace_id='trace-test')}); app.state.briefing_service=Fake(); res=TestClient(app).post('/briefing', json={'question':'q','top_k':5,'use_council':True}); assert res.status_code==200 and res.json()['trace_id']=='trace-test'; del app.state.briefing_service; print('briefing fake endpoint ok')"
cd hydra/backend && uv run python -c "from hydra_api.briefing_service import BriefingService; from hydra_api.schemas import BriefingRequest, QueryResponse, RetrievedDocument, CouncilReview, RiskLevel; calls={'c':0}; Q=type('Q', (), {'query': lambda self, request: QueryResponse(answer='A', retrieved_documents=[RetrievedDocument(document_id='doc1', chunk_id='c1', title='T', source='S', score=0.8, evidence='ev')], limitations=['lim'], trace_id='trace-q')}); C=type('C', (), {'run': lambda self, question, retrieved_documents: calls.__setitem__('c', calls['c']+1) or type('R', (), {'briefing_markdown':'# Briefing', 'risk_level': RiskLevel.medio, 'council_review': CouncilReview(evidence_supported=True, unsupported_claims=[], risk_review='ok')})()}); s=BriefingService(query_service=Q(), council_service=C()); r=s.brief(BriefingRequest(question='q')); assert calls['c']==1 and r.council_review is not None; print('briefing uses council ok')"
cd hydra/backend && uv run python -c "from hydra_api.briefing_service import BriefingService; from hydra_api.schemas import BriefingRequest, QueryResponse, RetrievedDocument, RiskLevel; calls={'c':0}; Q=type('Q', (), {'query': lambda self, request: QueryResponse(answer='A', retrieved_documents=[RetrievedDocument(document_id='doc1', chunk_id='c1', title='T', source='S', score=0.8, evidence='ev')], limitations=['lim'], trace_id='trace-q')}); C=type('C', (), {'run': lambda self, question, retrieved_documents: calls.__setitem__('c', calls['c']+1)}); s=BriefingService(query_service=Q(), council_service=C()); r=s.brief(BriefingRequest(question='q', use_council=False)); assert calls['c']==0 and r.council_review is None; print('briefing skips council ok')"
```

## TASK-REPAIR-06-002: Parsear salidas reales del council

Estado: pending
Prioridad: must

Objetivo:
Permitir que reviewers reales devuelvan strings JSON o texto estructurado sin que el servicio descarte todo como `{}`.

Archivos permitidos:

- `hydra/backend/src/hydra_api/council_service.py`

Requisitos:

- Crear parser seguro para outputs de chain:
  - si es `dict`, usarlo;
  - si es string JSON valido, parsearlo con `json.loads`;
  - si es string no JSON, extraer campos simples de forma conservadora o devolver dict seguro con limitacion;
  - nunca usar `eval`.
- `build_council_review({})` debe producir `risk_review` no vacio con mensaje de limitacion seguro.
- `unsupported_claims` string debe convertirse en lista breve o descartarse con limitacion segura.
- `risk_level` invalido debe normalizarse a `RiskLevel.medio`.
- Texto largo del modelo debe truncarse antes de incluirse en `unsupported_claims` o `risk_review`.

Criterios de aceptacion:

- Reviewer JSON string con `evidence_supported=true` produce `CouncilReview.evidence_supported is True`.
- Risk reviewer JSON string con `risk_level='alto'` produce `RiskLevel.alto`.
- Dict vacio produce `CouncilReview` valido con `evidence_supported=False` y `risk_review` no vacio.

Comandos de verificacion:

```bash
cd hydra/backend && uv run python -c "from hydra_api.council_service import build_council_review; r=build_council_review({}); assert r.evidence_supported is False and r.risk_review.strip(); print('empty council review safe ok')"
cd hydra/backend && uv run python -c "from hydra_api.council_service import CouncilService; from hydra_api.schemas import RetrievedDocument; s=CouncilService(analyst_chain=lambda p:'draft', evidence_reviewer_chain=lambda p:'{\"evidence_supported\": true, \"unsupported_claims\": [], \"risk_review\": \"ok\"}', risk_reviewer_chain=lambda p:'{\"risk_level\": \"alto\", \"risk_review\": \"alto por evidencia\"}', final_synthesizer_chain=lambda p:'# Briefing\\n\\n## Limitaciones\\n- corpus'); r=s.run('q', [RetrievedDocument(document_id='doc1', chunk_id='c1', title='T', source='S', score=0.8, evidence='ev')]); assert r.council_review.evidence_supported is True and r.risk_level.value=='alto'; print('council string parsers ok')"
```

## TASK-REPAIR-06-003: Recortar evidencia en prompts y briefing

Estado: pending
Prioridad: must

Objetivo:
Garantizar que prompts y Markdown usan solo snippets breves y legibles.

Archivos permitidos:

- `hydra/backend/src/hydra_api/council_prompts.py`
- `hydra/backend/src/hydra_api/briefing_service.py`

Requisitos:

- Centralizar un helper puro para normalizar documentos recuperados a dict seguro.
- Recortar evidencia con `BRIEFING_EVIDENCE_SNIPPET_CHARS` o limite equivalente.
- Sustituir saltos de linea repetidos por espacios o saltos controlados.
- Incluir `document_id`, `chunk_id`, titulo, fuente, score y evidencia recortada.
- No incluir documentos completos.

Criterios de aceptacion:

- Una evidencia de 1000 caracteres no aparece completa en ningun prompt.
- Saltos de linea en evidencia no rompen legibilidad.

Comandos de verificacion:

```bash
cd hydra/backend && uv run python -c "from hydra_api.council_prompts import build_narrative_analyst_prompt, build_evidence_reviewer_prompt, build_risk_reviewer_prompt; long='X'*1000; docs=[{'document_id':'doc1','chunk_id':'c1','title':'T','source':'S','score':0.9,'evidence':long}]; prompts=[build_narrative_analyst_prompt('q', docs), build_evidence_reviewer_prompt('draft', docs), build_risk_reviewer_prompt('draft', docs)]; assert all(long not in p for p in prompts); assert all('doc1' in p for p in prompts); print('prompt evidence truncation ok')"
```

## TASK-REPAIR-06-004: Incluir evidencia en final synthesizer

Estado: pending
Prioridad: must

Objetivo:
Hacer que el prompt del sintetizador final tenga fuentes recuperadas y pueda generar un briefing trazable.

Archivos permitidos:

- `hydra/backend/src/hydra_api/council_prompts.py`
- `hydra/backend/src/hydra_api/briefing_config.py`

Requisitos:

- `build_final_synthesizer_prompt()` debe incluir bloque de evidencias recuperadas recortadas.
- Debe exigir que cada hallazgo tenga referencia a `document_id` y `chunk_id`, o se convierta en limitacion.
- Debe incluir todas las secciones de `REQUIRED_BRIEFING_SECTIONS`.
- `REQUIRED_BRIEFING_SECTIONS` debe cubrir como minimo:
  - pregunta;
  - hallazgos con evidencia;
  - riesgo;
  - limitaciones;
  - fuentes recuperadas.

Criterios de aceptacion:

- El prompt final contiene `document_id`, evidencia recortada y la limitacion obligatoria.
- La lista de secciones requeridas contiene los conceptos minimos.

Comandos de verificacion:

```bash
cd hydra/backend && uv run python -c "from hydra_api.briefing_config import REQUIRED_BRIEFING_SECTIONS; low=' | '.join(REQUIRED_BRIEFING_SECTIONS).lower(); assert all(term in low for term in ['pregunta','hallaz','evidencia','riesgo','limit','fuentes']); print('required sections complete ok')"
cd hydra/backend && uv run python -c "from hydra_api.council_prompts import build_final_synthesizer_prompt; p=build_final_synthesizer_prompt('q','draft',{'evidence_supported':True,'unsupported_claims':[]},{'risk_level':'medio','risk_review':'ok'},[{'document_id':'doc1','chunk_id':'c1','title':'T','source':'S','score':0.9,'evidence':'ev-final'}]); low=p.lower(); assert 'doc1' in p and 'ev-final' in p and 'limitacion' in low; print('final synthesizer evidence ok')"
```

## TASK-REPAIR-06-005: Forzar limitacion obligatoria y salidas no vacias

Estado: pending
Prioridad: must

Objetivo:
Evitar briefings sin la limitacion obligatoria o respuestas exitosas vacias.

Archivos permitidos:

- `hydra/backend/src/hydra_api/briefing_service.py`
- `hydra/backend/src/hydra_api/council_service.py`

Requisitos:

- `build_briefing_draft()` siempre debe incluir `MANDATORY_CORPUS_LIMITATION`, aunque `QueryResponse.limitations` tenga entradas.
- No duplicar la misma limitacion si ya existe.
- Si analyst, reviewer, risk reviewer o final synthesizer devuelve salida vacia, producir limitacion segura.
- Un final synthesizer vacio nunca debe producir `briefing_markdown=""`.
- Si `evidence_supported=False`, mantener o anteponer limitacion clara.

Criterios de aceptacion:

- Draft con documentos y `limitations=['lim']` incluye tambien `MANDATORY_CORPUS_LIMITATION`.
- Final synthesizer vacio devuelve briefing no vacio con limitacion.

Comandos de verificacion:

```bash
cd hydra/backend && uv run python -c "from hydra_api.briefing_service import build_briefing_draft; from hydra_api.briefing_config import MANDATORY_CORPUS_LIMITATION; from hydra_api.schemas import QueryResponse, RetrievedDocument; q=QueryResponse(answer='A', retrieved_documents=[RetrievedDocument(document_id='doc1', chunk_id='c1', title='T', source='S', score=0.8, evidence='ev')], limitations=['lim'], trace_id='t'); md=build_briefing_draft('q', q); assert 'lim' in md and MANDATORY_CORPUS_LIMITATION in md; print('mandatory limitation always included ok')"
cd hydra/backend && uv run python -c "from hydra_api.council_service import CouncilService; from hydra_api.schemas import RetrievedDocument; s=CouncilService(analyst_chain=lambda p:'draft', evidence_reviewer_chain=lambda p:{'evidence_supported': True, 'unsupported_claims': [], 'risk_review':'ok'}, risk_reviewer_chain=lambda p:{'risk_level':'medio','risk_review':'ok'}, final_synthesizer_chain=lambda p:''); r=s.run('q', [RetrievedDocument(document_id='doc1', chunk_id='c1', title='T', source='S', score=0.8, evidence='ev')]); assert r.briefing_markdown.strip() and 'limit' in r.briefing_markdown.lower(); print('empty synthesizer limitation ok')"
```

## TASK-REPAIR-06-006: Hacer factory inyectable

Estado: pending
Prioridad: must

Objetivo:
Alinear `create_council_service()` con los requisitos de Mission 06 y facilitar tests sin credenciales reales.

Archivos permitidos:

- `hydra/backend/src/hydra_api/council_service.py`
- `hydra/backend/src/hydra_api/model_client.py`

Requisitos:

- `create_council_service(settings=None, chat_model=None, review_model=None)` debe existir.
- Si se inyecta `chat_model`, usarlo para analyst/final synthesizer.
- Si se inyecta `review_model`, usarlo para evidence/risk reviewers.
- Si no se inyectan modelos, usar `HYDRA_CHAT_MODEL` y `HYDRA_REVIEW_MODEL` desde Settings.
- No llamar proveedor real durante import o construccion.
- No requerir red para construir con fakes.

Criterios de aceptacion:

- La firma contiene `settings`, `chat_model`, `review_model`.
- Con modelos fake se construye servicio sin leer `.env`.
- Con env fake se construye servicio real sin llamada de red.

Comandos de verificacion:

```bash
cd hydra/backend && uv run python -c "import inspect; from hydra_api.council_service import create_council_service; params=inspect.signature(create_council_service).parameters; assert all(name in params for name in ['settings','chat_model','review_model']); print('council factory signature ok')"
cd hydra/backend && uv run python -c "from hydra_api.council_service import create_council_service; fake=lambda prompt:'ok'; service=create_council_service(chat_model=fake, review_model=fake); assert service is not None; print('council factory injected ok')"
cd hydra/backend && MODEL_API_KEY=fake MODEL_API_BASE_URL=https://example.invalid/v1 uv run python -c "from hydra_api.council_service import create_council_service; service=create_council_service(); assert service is not None; print('council factory env fake ok')"
```

## TASK-REPAIR-06-007: Corregir README o revertir cambio fuera de scope

Estado: pending
Prioridad: should

Objetivo:
Eliminar la desviacion de scope o dejar la documentacion alineada con SDD.

Archivos permitidos:

- `hydra/README.md`

Requisitos:

- Opcion preferida: revertir la seccion "Council y Briefing (Mision 06)" si el usuario quiere mantener Mission 06 sin cambios de README.
- Si se mantiene, la seccion debe indicar que:
  - las verificaciones locales usan fakes;
  - el smoke real sigue bloqueado hasta corpus, DB, claves y aprobacion;
  - el endpoint real construye servicios lazy y no debe llamar modelos en import time;
  - no prometer que sin servicio real devuelve error si el codigo construye lazy.
- No documentar comandos que requieran secretos o red sin advertencia.

Comandos de verificacion:

```bash
cd hydra && git diff -- README.md
```

## Checks finales obligatorios

Despues de aplicar el repair, ejecutar:

```bash
cd hydra/backend && uv run python -c "from pydantic import ValidationError; from hydra_api.schemas import BriefingRequest; assert BriefingRequest(question='q').top_k==5; assert BriefingRequest(question='q').use_council is True; assert BriefingRequest(question='q', use_council=False).use_council is False; print('briefing defaults ok')"
cd hydra/backend && uv run python -c "from hydra_api import council_prompts; print('council prompts import ok')"
cd hydra/backend && uv run python -c "from hydra_api.council_service import normalize_risk_level, build_council_review, CouncilService; print('council service imports ok')"
cd hydra/backend && uv run python -c "from hydra_api.briefing_service import build_no_context_briefing_response, build_briefing_draft, BriefingService; print('briefing service imports ok')"
cd hydra/backend && uv run python -c "from fastapi.testclient import TestClient; from hydra_api.main import app; schema=TestClient(app).get('/openapi.json').json(); assert '/briefing' in schema['paths']; print('openapi briefing ok')"
cd hydra && git diff --check
cd hydra && git status --short
```

## Blocked tasks que siguen bloqueadas

No ejecutar en este repair:

- `TASK-COUNCIL-008`
- `TASK-BRIEF-007`

Siguen bloqueadas hasta tener corpus aprobado, DB local inicializada, chunks con embeddings reales, `POST /query` real funcionando, `MODEL_API_KEY` real en `.env` local no versionado y aprobacion explicita de coste/red.

## Security check obligatorio

Antes de reportar:

- Confirmar que no se modificaron `.env` reales.
- Confirmar que no hay API keys, headers, tokens ni secretos en codigo, Markdown o salidas.
- Confirmar que no se imprimen prompts completos, respuestas completas del modelo ni documentos completos.
- Confirmar que no se tocaron frontend, Neo4j, DB schema, RAG store/retriever/indexing, evals ni observabilidad.

