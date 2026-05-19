# Tasks - Frontend

## Reglas de atomizacion

- Ejecutar estas tareas despues de tener disponibles, al menos con fakes o backend local, los contratos `GET /documents`, `GET /narratives`, `POST /query`, `POST /briefing`, `POST /evals/run` y `GET /evals/results` definidos en `hydra/sdd/03-api-contract.md`.
- Mantener el frontend en `hydra/frontend/` con Next.js, Tailwind y `pnpm`.
- No crear `hydra/hydra/` ni mover archivos de backend, SDD o docs.
- No usar `npm`, `yarn`, `bun` ni mezclas de package managers.
- No crear Next API routes, server actions ni proxies que llamen proveedores LLM, embeddings, Langfuse, DB o parsing de documentos.
- El frontend solo puede llamar al backend HYDRA usando `NEXT_PUBLIC_API_BASE_URL` y los endpoints del contrato.
- No guardar ni mostrar secretos, headers, prompts internos, stack traces, respuestas completas de modelo si no vienen del contrato, ni documentos completos.
- No crear ni modificar `.env` reales; versionar solo `hydra/frontend/.env.local.example` con valores publicos.
- No parsear documentos, no hacer chunking, no calcular embeddings, no ejecutar extracciones y no llamar modelos desde frontend.
- No anadir dependencias salvo que la tarea lo indique explicitamente.
- No tocar backend, corpus, eval datasets, SDD transversal ni docs en estas tareas.
- No marcar tareas como `done` hasta que Codex/reviewer revise diff, verificaciones y secretos.

## Contexto importante

- `hydra/frontend/.env.local.example` ya define `NEXT_PUBLIC_API_BASE_URL=http://localhost:8000`.
- `hydra/sdd/frontend-spec.md` pide una UI funcional, densa y orientada a analista; no landing page.
- `hydra/sdd/03-api-contract.md` es la fuente de verdad para payloads y endpoints.
- `GET /narratives` no define un campo `sectors`, aunque `frontend-spec.md` menciona sectores. En esta mission no se debe inventar ese campo ni cambiar el contrato: mostrar solo `actors`, `risk_level`, `confidence`, `evidence_fragments` y los campos realmente devueltos por el backend.
- No existe endpoint `GET /evals/cases` en el contrato. La vista Evals no debe inventarlo: debe permitir introducir `case_ids` manualmente y mostrar resultados de `GET /evals/results`.
- `POST /documents/upload` es extension opcional y solo se puede implementar cuando el backend la tenga y el pipeline principal ya funcione.

## Lecciones incorporadas antes de la mission frontend

- Alinear tipos frontend con `sdd/03-api-contract.md`; no crear campos obligatorios que no existan en el contrato.
- Centralizar el cliente HTTP para evitar hardcodear endpoints, duplicar parsing de errores o filtrar informacion sensible de forma inconsistente.
- No aceptar silenciosamente payloads incompletos: mostrar estado vacio/error seguro y no romper la pantalla.
- Mantener rutas relativas y variables publicas; no leer rutas absolutas locales ni exponer estructura interna.
- No resetear estado de formularios/resultados existentes por accidente al refrescar datos secundarios.
- Mantener verificaciones locales sin backend real cuando sea posible con typecheck/build; las pruebas de integracion con backend deben ser optativas y explicitas.
- Separar scaffold, cliente API, shell UI, vistas de lectura, vistas interactivas, evals y upload opcional.
- No crear documentacion ni navegacion que apunte a rutas inexistentes.
- No modificar archivos fuera del allowed scope de la tarea activa.

## Errores probables a evitar

- Crear una landing page decorativa en vez de la primera pantalla funcional.
- Poner `MODEL_API_KEY`, `DATABASE_URL`, `LANGFUSE_SECRET_KEY` o URLs directas de proveedores en frontend.
- Usar `fetch` disperso en cada componente con manejo distinto de errores.
- Llamar `POST /query`, `POST /briefing` o evals en render sin accion explicita del usuario.
- Renderizar errores backend crudos con stack traces o detalles internos.
- Usar `dangerouslySetInnerHTML` para briefing markdown.
- Inventar `/evals/cases`, `/analytics`, `/graph` u otros endpoints no definidos.
- Intentar cargar archivos reales en frontend para analizarlos.
- Crear upload UI activa antes de que exista `POST /documents/upload` backend.
- Tocar `hydra/backend/**`, `hydra/sdd/**`, `hydra/docs/**` o `.env` reales durante la implementacion frontend.

## Edge cases obligatorios

- `NEXT_PUBLIC_API_BASE_URL` ausente debe degradar a `http://localhost:8000` o mostrar error seguro sin secretos.
- API base con slash final y sin slash final debe construir URLs correctas.
- Backend caido, timeout, JSON invalido o error con forma `{ error: { code, message, details } }` debe mostrar mensaje seguro.
- Listas vacias de documentos, narrativas, retrieved documents, evidencias, limitations o eval results deben renderizar estado vacio estable.
- Campos opcionales/ausentes en respuestas deben mostrarse como `No disponible`, `Sin evidencias` o equivalente, no romper la UI.
- `published_at` invalido o ausente no debe lanzar excepcion de formato.
- `top_k` omitido debe usar `5`; `top_k <= 0` no debe enviarse.
- Pregunta vacia o solo espacios no debe llamar al backend.
- `case_ids` vacio no debe llamar `/evals/run`.
- `trace_id` ausente debe mostrarse como `No disponible`, no inventarse.
- Markdown de briefing debe renderizarse sin HTML inseguro y sin ejecutar scripts.
- Refrescar resultados de evals no debe borrar el resultado recien devuelto por `/evals/run` hasta que llegue una nueva respuesta valida.

## Stop conditions generales

- Necesitas cambiar `hydra/sdd/03-api-contract.md`, `hydra/sdd/frontend-spec.md`, modelos backend o nombres de variables de entorno.
- Una pantalla requiere un endpoint que no existe en `sdd/03-api-contract.md`.
- La implementacion requiere que el frontend parse documentos, haga chunking, calcule embeddings, ejecute extraccion o llame modelos/proveedores.
- La tarea requiere backend real, DB viva, corpus real, Langfuse real o claves reales y no esta marcada como bloqueada/optativa.
- Se necesita versionar `.env.local`, `.env`, documentos reales, API keys, headers, stack traces, prompts completos o contenido completo de documentos.
- `pnpm install` requiere red y falla; reportar bloqueo tecnico y no falsificar `pnpm-lock.yaml`.
- Una dependencia nueva no esta declarada por la tarea activa.
- Se intenta tocar archivos fuera de `hydra/frontend/**` para una tarea frontend.

## Milestones sugeridos para Droid Missions

| Milestone | Tareas | Objetivo | Debe parar para review |
|---|---|---|---|
| 1 | TASK-FRONT-001 a TASK-FRONT-004 | Scaffold Next/Tailwind, env publico, cliente API y shell base | Si package manager/red bloquea lockfile o cambia stack |
| 2 | TASK-FRONT-005 a TASK-FRONT-008 | Corpus y narrativas con estados seguros | Si necesita campos no contractuales |
| 3 | TASK-FRONT-009 a TASK-FRONT-013 | Analyst y Briefing interactivos con evidencias/trace | Si llama modelos o renderiza HTML inseguro |
| 4 | TASK-FRONT-014 a TASK-FRONT-017 | Evals, estados transversales y build final | Si inventa endpoints o muestra errores crudos |
| 5 | TASK-FRONT-018 a TASK-FRONT-019 | Bloqueado: upload opcional | Bloqueado hasta backend upload y pipeline principal estable |

## TASK-FRONT-001: Inicializar package Next con pnpm

Estado: pending
Prioridad: must

Objetivo:
Crear el `package.json` del frontend y lockfile con Next.js, React, Tailwind, TypeScript y dependencias minimas de UI necesarias para el MVP.

Archivos permitidos:
- `hydra/frontend/package.json`
- `hydra/frontend/pnpm-lock.yaml`

Dependencias:
- Ninguna

Requisitos:
- Usar `pnpm`; no usar `npm`, `yarn` ni `bun`.
- Definir scripts `dev`, `build`, `start`, `typecheck` y `lint`.
- Incluir dependencias runtime para Next.js, React, React DOM y render seguro de markdown (`react-markdown` o alternativa declarada y segura).
- Incluir dev dependencies para TypeScript, tipos React/Node, Tailwind, PostCSS, Autoprefixer y ESLint compatible con Next.
- Generar `pnpm-lock.yaml` con `pnpm`, no editarlo a mano.
- No crear ni modificar `.env` reales.

Criterios de aceptacion:
- `pnpm install --frozen-lockfile` pasa despues de generar el lockfile.
- `package.json` no contiene dependencias de backend, Langfuse, modelos, embeddings, Neo4j, DB drivers ni scraping.
- Los scripts existen y usan `pnpm`/Next, no otro package manager.

Errores probables a evitar:
- Usar `create-next-app` sobre un directorio no vacio borrando `frontend/.env.local.example`.
- Mezclar scaffold con implementacion de pantallas.
- Anadir librerias de estado global, charting o upload no requeridas por esta tarea.

Edge cases obligatorios:
- Si `pnpm install` necesita red y falla, reportar bloqueo tecnico; no inventar lockfile.
- Si `frontend/package.json` ya existe, preservar scripts/dependencias compatibles y no borrar trabajo previo.

Stop conditions:
- La dependencia elegida obliga a cambiar stack, package manager o variables SDD.
- Hace falta tocar archivos fuera de `hydra/frontend/package.json` y `hydra/frontend/pnpm-lock.yaml`.

Comandos de verificacion:
- `cd hydra/frontend && pnpm install`
- `cd hydra/frontend && pnpm install --frozen-lockfile`
- `cd hydra/frontend && pnpm exec next --version`
- `cd hydra/frontend && pnpm exec tsc --version`

## TASK-FRONT-002: Configurar Next, TypeScript, Tailwind y ESLint

Estado: pending
Prioridad: must

Objetivo:
Anadir la configuracion minima de Next App Router, TypeScript, Tailwind y linting sin crear todavia vistas de dominio.

Archivos permitidos:
- `hydra/frontend/next.config.mjs`
- `hydra/frontend/tsconfig.json`
- `hydra/frontend/next-env.d.ts`
- `hydra/frontend/postcss.config.mjs`
- `hydra/frontend/tailwind.config.ts`
- `hydra/frontend/eslint.config.mjs`
- `hydra/frontend/src/app/layout.tsx`
- `hydra/frontend/src/app/page.tsx`
- `hydra/frontend/src/app/globals.css`

Dependencias:
- TASK-FRONT-001

Requisitos:
- Usar App Router en `src/app`.
- Configurar TypeScript estricto o equivalente razonable para evitar `any` innecesario.
- Configurar Tailwind para escanear `src/app`, `src/components` y `src/lib`.
- Crear `layout.tsx`, `page.tsx` y `globals.css` minimos para que `pnpm build` funcione.
- La primera pagina debe apuntar a experiencia funcional, no landing decorativa.
- No crear `src/app/api/**`.

Criterios de aceptacion:
- `pnpm typecheck`, `pnpm lint` y `pnpm build` pasan.
- Tailwind aplica estilos en `globals.css` sin dependencias externas de CDN.
- No hay llamadas al backend ni a proveedores en esta tarea.

Errores probables a evitar:
- Usar configuracion copiada que apunte a carpetas inexistentes.
- Crear `page.tsx` con datos mock que parezcan datos reales.
- Dejar imports absolutos sin configurar alias.

Edge cases obligatorios:
- Si la version instalada de Tailwind no requiere `tailwind.config.ts`, dejarlo minimo o documentar en el reporte sin cambiar el stack.
- Si ESLint requiere formato flat config, usar `eslint.config.mjs`; no crear configs duplicadas contradictorias.

Stop conditions:
- Build requiere datos, backend vivo o variables secretas.
- La configuracion exige cambiar arquitectura o package manager.

Comandos de verificacion:
- `cd hydra/frontend && pnpm typecheck`
- `cd hydra/frontend && pnpm lint`
- `cd hydra/frontend && pnpm build`
- `test ! -d hydra/frontend/src/app/api`

## TASK-FRONT-003: Definir entorno publico y tipos de contrato API

Estado: pending
Prioridad: must

Objetivo:
Centralizar la configuracion publica del backend y los tipos TypeScript derivados del contrato API vigente.

Archivos permitidos:
- `hydra/frontend/.env.local.example`
- `hydra/frontend/src/lib/env.ts`
- `hydra/frontend/src/lib/api-types.ts`

Dependencias:
- TASK-FRONT-002

Requisitos:
- Mantener `NEXT_PUBLIC_API_BASE_URL=http://localhost:8000` en `.env.local.example`.
- No anadir variables privadas ni secretos al frontend.
- Crear helper que devuelva la API base con fallback seguro a `http://localhost:8000`.
- Normalizar slash final para construir URLs.
- Definir tipos para `DocumentSummary`, `NarrativeFrame`, `QueryRequest`, `QueryResponse`, `BriefingRequest`, `BriefingResponse`, `EvalRunRequest`, `EvalRunResponse`, `EvalResultsResponse` y errores seguros segun `sdd/03-api-contract.md`.
- No incluir campos obligatorios no definidos por el contrato, especialmente `sectors` o `eval_cases`.

Criterios de aceptacion:
- TypeScript compila sin `any` innecesarios en los tipos de contrato.
- `.env.local.example` contiene solo variables publicas `NEXT_PUBLIC_*`.
- Las URLs se construyen correctamente con base URL con o sin slash final.

Errores probables a evitar:
- Copiar variables de `hydra/backend/.env.example` al frontend.
- Tipar `trace_id` como obligatorio si una respuesta parcial/fallida puede no traerlo.
- Convertir campos opcionales en obligatorios sin soporte de backend.

Edge cases obligatorios:
- `process.env.NEXT_PUBLIC_API_BASE_URL` vacio, con espacios o con slash final.
- `published_at`, `trace_id`, `limitations`, `evidence_fragments` ausentes o vacios.

Stop conditions:
- Hace falta cambiar el contrato API para tipar una pantalla.
- Alguien pide exponer `MODEL_API_KEY`, `LANGFUSE_SECRET_KEY` o `DATABASE_URL` en frontend.

Comandos de verificacion:
- `cd hydra/frontend && pnpm typecheck`
- `cd hydra/frontend && pnpm lint`
- `cd hydra/frontend && node -e "const text=require('fs').readFileSync('.env.local.example','utf8'); if(/MODEL_API_KEY|LANGFUSE_SECRET_KEY|DATABASE_URL/.test(text)) process.exit(1); console.log('frontend env example ok')"`

## TASK-FRONT-004: Crear cliente HTTP seguro del backend

Estado: pending
Prioridad: must

Objetivo:
Crear un cliente HTTP unico para consumir el backend HYDRA con manejo uniforme de errores seguros.

Archivos permitidos:
- `hydra/frontend/src/lib/api-client.ts`
- `hydra/frontend/src/lib/env.ts`
- `hydra/frontend/src/lib/api-types.ts`

Dependencias:
- TASK-FRONT-003

Requisitos:
- Exponer funciones `getDocuments`, `getNarratives`, `queryHydra`, `createBriefing`, `runEvals` y `getEvalResults` o nombres equivalentes claros.
- Usar solo endpoints definidos en `sdd/03-api-contract.md`.
- Construir URLs desde `NEXT_PUBLIC_API_BASE_URL`.
- Enviar y recibir JSON salvo upload opcional bloqueado.
- Manejar errores backend con forma `{ error: { code, message, details } }` mostrando solo `message` seguro y codigo si existe.
- Manejar timeout/fetch failure/JSON invalido con mensajes seguros sin stack traces.
- No loggear payloads completos, headers, prompts internos ni documentos completos.

Criterios de aceptacion:
- Las funciones del cliente estan tipadas con los tipos de `api-types.ts`.
- No hay `fetch(` fuera de `src/lib/api-client.ts` salvo excepcion justificada en reporte.
- No hay URLs directas a proveedores LLM, Langfuse ni DB.

Errores probables a evitar:
- Duplicar fetch en cada page/component.
- Reenviar headers privados del navegador innecesariamente.
- Usar rutas relativas que apunten a Next en vez del backend FastAPI.

Edge cases obligatorios:
- Backend devuelve HTML o texto en vez de JSON.
- Backend responde 4xx/5xx con y sin objeto `error`.
- Network error o timeout.
- Base URL con slash final.

Stop conditions:
- Se necesita crear un proxy Next o route handler para que funcione el cliente.
- La pantalla requiere un endpoint no documentado.

Comandos de verificacion:
- `cd hydra/frontend && pnpm typecheck`
- `cd hydra/frontend && pnpm lint`
- `grep -R "fetch(" -n hydra/frontend/src | grep -v "src/lib/api-client.ts" && exit 1 || true`
- `grep -R "MODEL_API_KEY\|LANGFUSE_SECRET_KEY\|DATABASE_URL" -n hydra/frontend/src hydra/frontend/.env.local.example && exit 1 || true`

## TASK-FRONT-005: Crear shell funcional y navegacion

Estado: pending
Prioridad: must

Objetivo:
Crear la estructura visual base orientada a analista, con navegacion a las vistas funcionales del MVP.

Archivos permitidos:
- `hydra/frontend/src/app/layout.tsx`
- `hydra/frontend/src/app/page.tsx`
- `hydra/frontend/src/components/AppShell.tsx`
- `hydra/frontend/src/components/MainNavigation.tsx`
- `hydra/frontend/src/components/StatusBadge.tsx`

Dependencias:
- TASK-FRONT-004

Requisitos:
- Primera pantalla: dashboard funcional con enlaces/estado de Corpus, Narrativas, Analyst, Briefing y Evals.
- No usar landing page promocional.
- Navegacion a rutas existentes o planificadas en esta mission: `/`, `/corpus`, `/narratives`, `/analyst`, `/briefing`, `/evals`.
- No enlazar upload mientras este bloqueado.
- Incluir mensaje claro de limitacion: el analisis depende del corpus disponible.
- No mostrar datos inventados como si fueran reales.

Criterios de aceptacion:
- La shell renderiza sin backend vivo.
- No hay enlaces rotos a rutas fuera del scope.
- La UI comunica que evidencias/limitaciones son parte del producto.

Errores probables a evitar:
- Crear marketing copy en vez de interfaz de trabajo.
- Navegar a `/upload`, `/graph` o `/admin` sin tasks activas.
- Mostrar mock data sin etiqueta clara.

Edge cases obligatorios:
- Pantalla usable en ancho movil y desktop.
- Estado activo de navegacion no debe romper en rutas desconocidas.

Stop conditions:
- Hace falta cambiar diseño de producto o agregar vistas no SDD.

Comandos de verificacion:
- `cd hydra/frontend && pnpm typecheck`
- `cd hydra/frontend && pnpm lint`
- `cd hydra/frontend && pnpm build`

## TASK-FRONT-006: Crear componentes de estado y formato seguros

Estado: pending
Prioridad: must

Objetivo:
Crear componentes y helpers reutilizables para loading, error, empty state, fechas, riesgos, confianza y trace IDs.

Archivos permitidos:
- `hydra/frontend/src/components/StateBlock.tsx`
- `hydra/frontend/src/components/DataBadge.tsx`
- `hydra/frontend/src/components/TraceId.tsx`
- `hydra/frontend/src/lib/formatters.ts`

Dependencias:
- TASK-FRONT-005

Requisitos:
- Componentes para loading, error seguro, estado vacio y contenido no disponible.
- Formatear `published_at` sin lanzar si es invalido o ausente.
- Badges para `risk_level` y `confidence` aceptando valores desconocidos.
- `TraceId` debe mostrar `No disponible` si falta y no inventar IDs.
- No renderizar stack traces ni objetos `details` completos del backend.

Criterios de aceptacion:
- Componentes importables desde vistas sin depender del backend.
- Helpers cubren `null`, `undefined`, string vacio y fechas invalidas.
- No hay `dangerouslySetInnerHTML`.

Errores probables a evitar:
- Asumir que todos los campos vienen completos.
- Lanzar excepcion al formatear fechas invalidas.
- Mostrar `JSON.stringify(error)` en UI.

Edge cases obligatorios:
- Valores de riesgo/confianza fuera de catalogo.
- `trace_id` largo, vacio o ausente.
- Mensajes de error con saltos de linea o texto excesivo.

Stop conditions:
- Para formatear se necesita cambiar payload backend o contrato.

Comandos de verificacion:
- `cd hydra/frontend && pnpm typecheck`
- `cd hydra/frontend && pnpm lint`
- `grep -R "dangerouslySetInnerHTML" -n hydra/frontend/src && exit 1 || true`

## TASK-FRONT-007: Crear vista Corpus

Estado: pending
Prioridad: must

Objetivo:
Implementar `/corpus` consumiendo `GET /documents` y mostrando documentos disponibles con estados seguros.

Archivos permitidos:
- `hydra/frontend/src/app/corpus/page.tsx`
- `hydra/frontend/src/components/corpus/CorpusTable.tsx`
- `hydra/frontend/src/lib/api-client.ts`
- `hydra/frontend/src/lib/api-types.ts`
- `hydra/frontend/src/components/StateBlock.tsx`
- `hydra/frontend/src/lib/formatters.ts`

Dependencias:
- TASK-FRONT-006

Requisitos:
- Mostrar `document_id`, `title`, `source`, `published_at` y `processed` segun contrato.
- Usar el cliente API centralizado.
- Manejar loading, error seguro y lista vacia.
- No leer archivos locales ni intentar parsear documentos.
- No mostrar contenido completo de documentos.

Criterios de aceptacion:
- `/corpus` compila y renderiza aunque el backend este caido.
- Si `documents=[]`, muestra estado vacio claro.
- Si un campo falta, no rompe la tabla.

Errores probables a evitar:
- Implementar ingesta o lectura de filesystem en frontend.
- Mostrar source/url como HTML sin escapar.
- Bloquear toda la app si `/documents` falla.

Edge cases obligatorios:
- `published_at` ausente/invalido.
- `processed=false` y `processed` ausente.
- Titulos o fuentes largos.

Stop conditions:
- Se necesita endpoint distinto de `GET /documents` o campos no contractuales.

Comandos de verificacion:
- `cd hydra/frontend && pnpm typecheck`
- `cd hydra/frontend && pnpm lint`
- `cd hydra/frontend && pnpm build`

## TASK-FRONT-008: Crear vista Narrativas

Estado: pending
Prioridad: must

Objetivo:
Implementar `/narratives` consumiendo `GET /narratives` y mostrando marcos narrativos con evidencias.

Archivos permitidos:
- `hydra/frontend/src/app/narratives/page.tsx`
- `hydra/frontend/src/components/narratives/NarrativesTable.tsx`
- `hydra/frontend/src/components/narratives/EvidenceList.tsx`
- `hydra/frontend/src/lib/api-client.ts`
- `hydra/frontend/src/lib/api-types.ts`
- `hydra/frontend/src/components/DataBadge.tsx`
- `hydra/frontend/src/components/StateBlock.tsx`

Dependencias:
- TASK-FRONT-007

Requisitos:
- Mostrar `narrative_frame_id`, `label`, `document_ids`, `actors`, `risk_level`, `confidence` y `evidence_fragments` segun contrato.
- No mostrar `sectors` como campo obligatorio porque no existe en `sdd/03-api-contract.md`.
- Evidencias deben mostrarse como fragmentos breves y escapados.
- Manejar loading, error seguro y lista vacia.
- No afirmar coordinacion, intencion o atribucion adicional desde la UI.

Criterios de aceptacion:
- `/narratives` compila sin exigir campos no contractuales.
- Narrativas sin evidencias muestran `Sin evidencias` o equivalente.
- Riesgo/confianza desconocidos no rompen badges.

Errores probables a evitar:
- Cambiar contrato para anadir `sectors` desde frontend.
- Tratar `document_ids` o `actors` como string en vez de array.
- Presentar evidencias como conclusiones no soportadas.

Edge cases obligatorios:
- `actors=[]`, `document_ids=[]` o `evidence_fragments=[]`.
- `risk_level`/`confidence` ausentes o valores desconocidos.
- Fragmentos largos deben recortarse o mantener layout sin filtrar contenido sensible adicional.

Stop conditions:
- Producto exige sectores obligatorios antes de actualizar API contract.

Comandos de verificacion:
- `cd hydra/frontend && pnpm typecheck`
- `cd hydra/frontend && pnpm lint`
- `cd hydra/frontend && pnpm build`

## TASK-FRONT-009: Crear formulario HYDRA Analyst

Estado: pending
Prioridad: must

Objetivo:
Implementar `/analyst` con formulario controlado para enviar preguntas a `POST /query` sin disparar llamadas automaticas.

Archivos permitidos:
- `hydra/frontend/src/app/analyst/page.tsx`
- `hydra/frontend/src/components/analyst/AnalystForm.tsx`
- `hydra/frontend/src/lib/api-client.ts`
- `hydra/frontend/src/lib/api-types.ts`
- `hydra/frontend/src/components/StateBlock.tsx`

Dependencias:
- TASK-FRONT-008

Requisitos:
- Campo `question` obligatorio.
- Campo `top_k` con valor por defecto `5` y validacion local para no enviar `<= 0`.
- Llamar `POST /query` solo al enviar el formulario.
- Mantener loading y error seguro.
- No llamar modelos ni providers desde frontend.
- No loggear la pregunta completa en consola.

Criterios de aceptacion:
- Pregunta vacia o solo espacios no hace request.
- `top_k <= 0` no hace request.
- Backend caido muestra error seguro y preserva la pregunta del usuario para reintento.

Errores probables a evitar:
- Ejecutar query en cada tecla o render.
- Poner endpoint hardcodeado fuera del cliente API.
- Borrar resultado anterior antes de recibir respuesta valida si el nuevo request falla.

Edge cases obligatorios:
- Pregunta con espacios alrededor.
- Doble submit durante loading.
- Respuesta 4xx/5xx segura.

Stop conditions:
- Se necesita cambiar `POST /query` o anadir streaming no definido por SDD.

Comandos de verificacion:
- `cd hydra/frontend && pnpm typecheck`
- `cd hydra/frontend && pnpm lint`
- `cd hydra/frontend && pnpm build`

## TASK-FRONT-010: Renderizar respuesta estructurada de Analyst

Estado: pending
Prioridad: must

Objetivo:
Mostrar la respuesta de `POST /query` con respuesta analitica, documentos recuperados, limitaciones y estados seguros.

Archivos permitidos:
- `hydra/frontend/src/components/analyst/AnalystResult.tsx`
- `hydra/frontend/src/components/analyst/RetrievedDocuments.tsx`
- `hydra/frontend/src/app/analyst/page.tsx`
- `hydra/frontend/src/components/StateBlock.tsx`
- `hydra/frontend/src/lib/api-types.ts`

Dependencias:
- TASK-FRONT-009

Requisitos:
- Mostrar `answer` como texto escapado.
- Mostrar `retrieved_documents` con `document_id`, `chunk_id`, `title`, `source`, `score` y `evidence`.
- Mostrar `limitations` de forma visible.
- No mostrar prompts internos ni datos no incluidos en el contrato.
- No afirmar que la respuesta esta completamente verificada si hay limitaciones.

Criterios de aceptacion:
- Respuesta sin documentos recuperados muestra estado vacio explicito.
- Limitaciones ausentes o vacias se manejan sin romper.
- Scores ausentes o no numericos no rompen la UI.

Errores probables a evitar:
- Renderizar respuesta como HTML.
- Ocultar limitaciones por defecto.
- Presentar score como porcentaje si no esta normalizado.

Edge cases obligatorios:
- `retrieved_documents=[]`.
- `limitations=[]` o ausente.
- Evidencia larga o ausente.
- `score=0`, `null` o valor fuera de rango esperado.

Stop conditions:
- Se necesita exponer contenido completo de documentos o prompts para mostrar la respuesta.

Comandos de verificacion:
- `cd hydra/frontend && pnpm typecheck`
- `cd hydra/frontend && pnpm lint`
- `grep -R "dangerouslySetInnerHTML" -n hydra/frontend/src && exit 1 || true`

## TASK-FRONT-011: Mostrar evidencias y trace_id en Analyst

Estado: pending
Prioridad: must

Objetivo:
Hacer que `/analyst` destaque evidencias recuperadas y `trace_id` sin filtrar informacion sensible.

Archivos permitidos:
- `hydra/frontend/src/components/analyst/EvidencePanel.tsx`
- `hydra/frontend/src/components/TraceId.tsx`
- `hydra/frontend/src/components/analyst/AnalystResult.tsx`
- `hydra/frontend/src/lib/formatters.ts`

Dependencias:
- TASK-FRONT-010

Requisitos:
- Mostrar evidencia por documento recuperado como fragmento breve.
- Mostrar `trace_id` usando componente reutilizable.
- Si `trace_id` falta, mostrar `No disponible`; no inventar fallback frontend.
- No imprimir `trace_id` ni payload completo en consola.

Criterios de aceptacion:
- Evidencias ausentes muestran estado seguro.
- `trace_id` largo no rompe layout.
- No hay logs de payload completo.

Errores probables a evitar:
- Convertir `trace_id` en link a Langfuse si no hay URL publica definida.
- Mostrar documentos completos bajo el nombre de evidencia.
- Usar `console.log(response)` para depurar y dejarlo versionado.

Edge cases obligatorios:
- Evidencia vacia, duplicada o muy larga.
- `trace_id` ausente, vacio o con caracteres inesperados.

Stop conditions:
- Hace falta exponer Langfuse private URL o claves en frontend.

Comandos de verificacion:
- `cd hydra/frontend && pnpm typecheck`
- `cd hydra/frontend && pnpm lint`
- `grep -R "console\.log\|console\.error" -n hydra/frontend/src && exit 1 || true`

## TASK-FRONT-012: Crear formulario Briefing

Estado: pending
Prioridad: must

Objetivo:
Implementar `/briefing` con formulario para solicitar `POST /briefing` al backend.

Archivos permitidos:
- `hydra/frontend/src/app/briefing/page.tsx`
- `hydra/frontend/src/components/briefing/BriefingForm.tsx`
- `hydra/frontend/src/lib/api-client.ts`
- `hydra/frontend/src/lib/api-types.ts`
- `hydra/frontend/src/components/StateBlock.tsx`

Dependencias:
- TASK-FRONT-011

Requisitos:
- Campo `question` obligatorio.
- Campo `top_k` por defecto `5`, no enviar `<= 0`.
- Campo `use_council` booleano por defecto `true` o valor claro en UI.
- Llamar solo a `POST /briefing`; no reutilizar `/query` para simular briefing.
- Manejar loading, error seguro y retry.

Criterios de aceptacion:
- Pregunta vacia no hace request.
- Backend caido muestra error seguro.
- La UI explica que el briefing depende del corpus y evidencias disponibles.

Errores probables a evitar:
- Generar briefing en frontend con templates propios.
- Ejecutar council o modelos desde frontend.
- Ocultar si `use_council` esta activo/inactivo.

Edge cases obligatorios:
- `use_council=false` debe enviarse correctamente.
- Doble submit durante loading.
- Error backend sin JSON.

Stop conditions:
- Se necesita cambiar contrato de `POST /briefing` o anadir streaming.

Comandos de verificacion:
- `cd hydra/frontend && pnpm typecheck`
- `cd hydra/frontend && pnpm lint`
- `cd hydra/frontend && pnpm build`

## TASK-FRONT-013: Renderizar briefing, riesgo, council review y trace_id

Estado: pending
Prioridad: must

Objetivo:
Mostrar la respuesta de `POST /briefing` de forma legible, segura y trazable.

Archivos permitidos:
- `hydra/frontend/src/components/briefing/BriefingResult.tsx`
- `hydra/frontend/src/components/briefing/CouncilReviewPanel.tsx`
- `hydra/frontend/src/components/TraceId.tsx`
- `hydra/frontend/src/components/DataBadge.tsx`
- `hydra/frontend/src/app/briefing/page.tsx`
- `hydra/frontend/src/lib/api-types.ts`

Dependencias:
- TASK-FRONT-012

Requisitos:
- Renderizar `briefing_markdown` sin `dangerouslySetInnerHTML`; usar `react-markdown` o alternativa segura declarada en TASK-FRONT-001.
- Mostrar `risk_level` como badge tolerante a valores desconocidos.
- Mostrar `council_review.evidence_supported`, `unsupported_claims` y `risk_review` si existen.
- Mostrar `trace_id` con el componente reutilizable.
- No ocultar claims no soportados.

Criterios de aceptacion:
- Markdown con enlaces o HTML embebido no ejecuta scripts.
- `council_review` ausente no rompe la UI.
- `unsupported_claims=[]` muestra estado claro.

Errores probables a evitar:
- Renderizar markdown con HTML crudo inseguro.
- Convertir `risk_level` en conclusion mas fuerte que la respuesta backend.
- Ocultar council review cuando evidence_supported es false.

Edge cases obligatorios:
- `briefing_markdown` vacio o muy largo.
- `council_review=null` o campos ausentes.
- `unsupported_claims` con strings largos.
- `trace_id` ausente.

Stop conditions:
- La solucion requiere HTML no sanitizado o dependencia no declarada.

Comandos de verificacion:
- `cd hydra/frontend && pnpm typecheck`
- `cd hydra/frontend && pnpm lint`
- `grep -R "dangerouslySetInnerHTML" -n hydra/frontend/src && exit 1 || true`

## TASK-FRONT-014: Crear vista Evals para ejecutar casos manuales

Estado: pending
Prioridad: must

Objetivo:
Implementar `/evals` con formulario para lanzar `POST /evals/run` usando `case_ids` introducidos por el usuario.

Archivos permitidos:
- `hydra/frontend/src/app/evals/page.tsx`
- `hydra/frontend/src/components/evals/EvalsRunForm.tsx`
- `hydra/frontend/src/lib/api-client.ts`
- `hydra/frontend/src/lib/api-types.ts`
- `hydra/frontend/src/components/StateBlock.tsx`

Dependencias:
- TASK-FRONT-013

Requisitos:
- No inventar endpoint para listar eval cases.
- Permitir introducir `case_ids` como lista separada por comas o lineas.
- Validar que al menos un `case_id` no vacio se envia.
- Campo `top_k` por defecto `5`, no enviar `<= 0`.
- Mostrar `run_id`, `results_path` y `trace_id` devueltos.
- Explicar que los casos disponibles dependen del dataset backend.

Criterios de aceptacion:
- `case_ids=[]` no hace request.
- IDs con espacios se normalizan sin borrar caracteres internos validos.
- Backend caido o bloqueado muestra error seguro.

Errores probables a evitar:
- Crear `/evals/cases` o fetch a archivo local frontend.
- Enviar evals automaticamente al cargar la vista.
- Ocultar que resultados reales requieren backend/corpus configurado.

Edge cases obligatorios:
- Duplicados en `case_ids` deben preservarse o deduplicarse de forma documentada en UI.
- `top_k` invalido.
- `results_path` ausente.
- `trace_id` ausente.

Stop conditions:
- Producto exige lista automatica de eval cases sin endpoint contractual.

Comandos de verificacion:
- `cd hydra/frontend && pnpm typecheck`
- `cd hydra/frontend && pnpm lint`
- `cd hydra/frontend && pnpm build`

## TASK-FRONT-015: Mostrar resultados de evals

Estado: pending
Prioridad: must

Objetivo:
Consumir `GET /evals/results` y mostrar resultados, metricas, estado passed y trace IDs.

Archivos permitidos:
- `hydra/frontend/src/components/evals/EvalsResultsPanel.tsx`
- `hydra/frontend/src/app/evals/page.tsx`
- `hydra/frontend/src/lib/api-client.ts`
- `hydra/frontend/src/lib/api-types.ts`
- `hydra/frontend/src/components/TraceId.tsx`
- `hydra/frontend/src/components/DataBadge.tsx`
- `hydra/frontend/src/components/StateBlock.tsx`

Dependencias:
- TASK-FRONT-014

Requisitos:
- Boton o accion explicita para refrescar resultados desde `GET /evals/results`.
- Mostrar `run_id`, `eval_case_id`, `metrics`, `passed` y `trace_id`.
- No borrar el resultado de `POST /evals/run` hasta tener nueva respuesta valida de results.
- Manejar lista vacia y backend sin resultados.
- No leer `hydra/backend/data/outputs/eval_results.json` desde frontend.

Criterios de aceptacion:
- Results vacios muestran estado vacio claro.
- Metricas desconocidas se renderizan como pares clave/valor seguros.
- `trace_id` ausente no rompe.

Errores probables a evitar:
- Intentar abrir el path local `results_path` desde el navegador.
- Asumir que todas las metricas son numericas.
- Mostrar objetos completos sin filtrar si backend incluye detalles.

Edge cases obligatorios:
- `results=[]`.
- `metrics={}` o metricas mixtas string/boolean/number.
- `passed=false` debe ser visible, no ocultarse como error de UI.

Stop conditions:
- La vista necesita acceso directo a filesystem backend o a datos no expuestos por API.

Comandos de verificacion:
- `cd hydra/frontend && pnpm typecheck`
- `cd hydra/frontend && pnpm lint`
- `cd hydra/frontend && pnpm build`

## TASK-FRONT-016: Endurecer loading, errores y estados vacios transversales

Estado: pending
Prioridad: must

Objetivo:
Revisar todas las vistas para que loading, errores, retry y empty states sean consistentes y no filtren detalles internos.

Archivos permitidos:
- `hydra/frontend/src/components/StateBlock.tsx`
- `hydra/frontend/src/lib/api-client.ts`
- `hydra/frontend/src/app/corpus/page.tsx`
- `hydra/frontend/src/app/narratives/page.tsx`
- `hydra/frontend/src/app/analyst/page.tsx`
- `hydra/frontend/src/app/briefing/page.tsx`
- `hydra/frontend/src/app/evals/page.tsx`

Dependencias:
- TASK-FRONT-015

Requisitos:
- Cada vista debe tener loading, error seguro, empty state y retry o accion clara.
- Los mensajes de error deben ser cortos y no incluir stack traces, headers ni detalles completos.
- Backend caido no debe romper navegacion.
- No usar `alert()` para errores de producto.
- No dejar `console.log`/`console.error` de payloads.

Criterios de aceptacion:
- Todas las rutas principales construyen en build.
- Grep no encuentra `console.log`, `console.error`, `alert(` ni `dangerouslySetInnerHTML`.
- Errores crudos no se serializan completos en UI.

Errores probables a evitar:
- Manejar errores en una sola pantalla y olvidar otras.
- Mostrar `error.details` completo.
- Hacer retry automatico infinito.

Edge cases obligatorios:
- Timeout o network error.
- Backend devuelve JSON invalido.
- Respuestas 204/empty body inesperadas.
- Usuario navega durante loading.

Stop conditions:
- Para resolver errores se requiere cambiar backend o contrato.

Comandos de verificacion:
- `cd hydra/frontend && pnpm typecheck`
- `cd hydra/frontend && pnpm lint`
- `cd hydra/frontend && pnpm build`
- `grep -R "console\.log\|console\.error\|alert(\|dangerouslySetInnerHTML" -n hydra/frontend/src && exit 1 || true`

## TASK-FRONT-017: Validar build final y ausencia de secretos frontend

Estado: pending
Prioridad: must

Objetivo:
Ejecutar una verificacion final de frontend para confirmar build, rutas, package manager, scope y ausencia de secretos.

Archivos permitidos:
- `hydra/frontend/package.json`
- `hydra/frontend/pnpm-lock.yaml`
- `hydra/frontend/src/app/page.tsx`
- `hydra/frontend/src/app/corpus/page.tsx`
- `hydra/frontend/src/app/narratives/page.tsx`
- `hydra/frontend/src/app/analyst/page.tsx`
- `hydra/frontend/src/app/briefing/page.tsx`
- `hydra/frontend/src/app/evals/page.tsx`
- `hydra/frontend/.env.local.example`

Dependencias:
- TASK-FRONT-016

Requisitos:
- No cambiar funcionalidad salvo fixes pequenos necesarios para pasar verificaciones.
- Confirmar que no existe `hydra/frontend/src/app/api/**`.
- Confirmar que no se tocaron backend, docs, corpus, SDD transversal ni `.env` reales.
- Confirmar que `pnpm-lock.yaml` esta presente y actualizado.
- Confirmar que todas las rutas principales existen.

Criterios de aceptacion:
- `pnpm install --frozen-lockfile`, `pnpm typecheck`, `pnpm lint` y `pnpm build` pasan.
- No hay secretos o variables privadas en `hydra/frontend/**`.
- `git diff --stat` muestra solo archivos frontend esperados.

Errores probables a evitar:
- Hacer refactors grandes de ultima hora.
- Arreglar build tocando backend o contrato.
- Comitear `.next/`, `node_modules/` o `.env.local`.

Edge cases obligatorios:
- Build debe pasar sin backend vivo.
- Secret scan debe cubrir `.env.local.example`, `src` y `package.json`.
- Si `pnpm-lock.yaml` cambia, debe ser por `pnpm install`, no edicion manual.

Stop conditions:
- Una verificacion falla por contradiccion SDD/contrato.
- Aparece secreto real o archivo generado pesado versionado.

Comandos de verificacion:
- `cd hydra/frontend && pnpm install --frozen-lockfile`
- `cd hydra/frontend && pnpm typecheck`
- `cd hydra/frontend && pnpm lint`
- `cd hydra/frontend && pnpm build`
- `test ! -d hydra/frontend/src/app/api`
- `test ! -d hydra/frontend/node_modules || true`
- `grep -R "MODEL_API_KEY\|LANGFUSE_SECRET_KEY\|DATABASE_URL\|sk-\|Bearer " -n hydra/frontend --exclude-dir=node_modules --exclude-dir=.next && exit 1 || true`
- `git diff --stat`

## TASK-FRONT-018: Implementar cliente de upload opcional

Estado: blocked
Prioridad: could

Bloqueo:
Depende de que `POST /documents/upload` este implementado y aceptado en backend, y de que el pipeline principal de corpus local, extraccion, RAG, briefing y evals ya funcione.

Objetivo:
Preparar el cliente frontend para subir documentos al backend sin crear pipeline paralelo.

Archivos permitidos cuando se desbloquee:
- `hydra/frontend/src/lib/api-client.ts`
- `hydra/frontend/src/lib/api-types.ts`

Dependencias:
- TASK-FRONT-017
- Backend `POST /documents/upload` implementado y revisado
- Pipeline principal estable

Requisitos cuando se desbloquee:
- Enviar `multipart/form-data` con campo `file` y `metadata` JSON.
- Soportar solo `.txt`, `.md` y `.csv`.
- No parsear archivo en frontend salvo validaciones superficiales de nombre/tipo/tamano.
- Mostrar error seguro si backend rechaza metadatos o formato.
- No versionar documentos reales.

Criterios de aceptacion cuando se desbloquee:
- El cliente llama solo a `POST /documents/upload` del backend HYDRA.
- No hay parsing, chunking, embeddings ni llamadas a modelos en frontend.
- Errores backend se muestran de forma segura.

Errores probables a evitar:
- Leer contenido completo del archivo para procesarlo en UI.
- Subir PDF aunque no este permitido para MVP extendido.
- Crear endpoint Next intermedio.

Edge cases obligatorios:
- Archivo sin extension, extension no permitida o metadata incompleta.
- Backend devuelve `processing_status="queued"`.
- Network error durante upload.

Stop conditions:
- Backend upload no existe o no esta aceptado.
- Producto exige PDF o procesamiento frontend.

Comandos de verificacion cuando se desbloquee:
- `cd hydra/frontend && pnpm typecheck`
- `cd hydra/frontend && pnpm lint`
- `grep -R "FileReader\|arrayBuffer\|text()" -n hydra/frontend/src && exit 1 || true`

## TASK-FRONT-019: Crear UI de subida opcional

Estado: blocked
Prioridad: could

Bloqueo:
Depende de TASK-FRONT-018 desbloqueada y aceptada, backend upload funcionando y aprobacion explicita para activar la extension opcional.

Objetivo:
Crear la pantalla/formulario de subida manual como entrada al pipeline backend existente.

Archivos permitidos cuando se desbloquee:
- `hydra/frontend/src/app/upload/page.tsx`
- `hydra/frontend/src/components/upload/UploadForm.tsx`
- `hydra/frontend/src/components/MainNavigation.tsx`
- `hydra/frontend/src/lib/api-client.ts`
- `hydra/frontend/src/lib/api-types.ts`
- `hydra/frontend/src/components/StateBlock.tsx`

Dependencias:
- TASK-FRONT-018

Requisitos cuando se desbloquee:
- Formulario con archivo y metadatos minimos: `title`, `source`, `source_type`, `url`, `published_at`, `domain`, `language`, `notes`.
- Mostrar `document_id`, `processing_status` y `message` de respuesta.
- Activar navegacion a `/upload` solo cuando la tarea este desbloqueada.
- No parsear, chunkear, extraer, embeddear ni llamar modelos desde frontend.
- No aceptar `.pdf` salvo nueva decision SDD.

Criterios de aceptacion cuando se desbloquee:
- Formulario no envia si faltan metadatos minimos.
- Backend reject se muestra como error seguro.
- UI deja claro que la ingesta real ocurre en backend.

Errores probables a evitar:
- Crear pipeline paralelo de upload.
- Guardar documentos en `public/` o versionarlos.
- Exponer rutas locales de usuario.

Edge cases obligatorios:
- Metadata con espacios vacios.
- URL opcional/invalida segun backend.
- Archivo demasiado grande rechazado por backend.
- Respuesta `queued` sin procesamiento inmediato.

Stop conditions:
- Falta backend upload aceptado.
- Se necesita cambiar contrato o procesar documento en frontend.

Comandos de verificacion cuando se desbloquee:
- `cd hydra/frontend && pnpm typecheck`
- `cd hydra/frontend && pnpm lint`
- `cd hydra/frontend && pnpm build`
- `grep -R "FileReader\|arrayBuffer\|text()\|MODEL_API_KEY\|LANGFUSE_SECRET_KEY\|DATABASE_URL" -n hydra/frontend/src && exit 1 || true`
