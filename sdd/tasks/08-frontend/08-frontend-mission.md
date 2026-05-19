# Mission Brief - 08 Frontend

## Objetivo

Implementar el frontend MVP de HYDRA con Next.js, Tailwind y pnpm como una interfaz funcional para analistas que consume solo el backend HYDRA, muestra evidencias/limitaciones/trace IDs y mantiene bloqueada la subida opcional hasta que exista el endpoint backend y el pipeline principal este estable.

## Source of truth

Leer antes de ejecutar:

- `hydra/sdd/README.md`
- `hydra/sdd/01-architecture-decisions.md`
- `hydra/sdd/03-api-contract.md`
- `hydra/sdd/frontend-spec.md`
- `hydra/sdd/07-implementation-plan.md`
- `hydra/sdd/08-task-checklist.md`
- `hydra/sdd/tasks/08-frontend/08-frontend.md`

No usar `docs/hydra-brainstorming.md` como fuente de decisiones.
Usar `docs/hydra-architecture.md` solo si la SDD anterior no es suficiente.

## Allowed files

Para tareas `pending` de esta mission:

- `hydra/frontend/package.json`
- `hydra/frontend/pnpm-lock.yaml`
- `hydra/frontend/.env.local.example`
- `hydra/frontend/next.config.mjs`
- `hydra/frontend/tsconfig.json`
- `hydra/frontend/next-env.d.ts`
- `hydra/frontend/postcss.config.mjs`
- `hydra/frontend/tailwind.config.ts`
- `hydra/frontend/eslint.config.mjs`
- `hydra/frontend/src/app/layout.tsx`
- `hydra/frontend/src/app/page.tsx`
- `hydra/frontend/src/app/globals.css`
- `hydra/frontend/src/app/corpus/page.tsx`
- `hydra/frontend/src/app/narratives/page.tsx`
- `hydra/frontend/src/app/analyst/page.tsx`
- `hydra/frontend/src/app/briefing/page.tsx`
- `hydra/frontend/src/app/evals/page.tsx`
- `hydra/frontend/src/components/AppShell.tsx`
- `hydra/frontend/src/components/MainNavigation.tsx`
- `hydra/frontend/src/components/StatusBadge.tsx`
- `hydra/frontend/src/components/StateBlock.tsx`
- `hydra/frontend/src/components/DataBadge.tsx`
- `hydra/frontend/src/components/TraceId.tsx`
- `hydra/frontend/src/components/corpus/CorpusTable.tsx`
- `hydra/frontend/src/components/narratives/NarrativesTable.tsx`
- `hydra/frontend/src/components/narratives/EvidenceList.tsx`
- `hydra/frontend/src/components/analyst/AnalystForm.tsx`
- `hydra/frontend/src/components/analyst/AnalystResult.tsx`
- `hydra/frontend/src/components/analyst/RetrievedDocuments.tsx`
- `hydra/frontend/src/components/analyst/EvidencePanel.tsx`
- `hydra/frontend/src/components/briefing/BriefingForm.tsx`
- `hydra/frontend/src/components/briefing/BriefingResult.tsx`
- `hydra/frontend/src/components/briefing/CouncilReviewPanel.tsx`
- `hydra/frontend/src/components/evals/EvalsRunForm.tsx`
- `hydra/frontend/src/components/evals/EvalsResultsPanel.tsx`
- `hydra/frontend/src/lib/env.ts`
- `hydra/frontend/src/lib/api-types.ts`
- `hydra/frontend/src/lib/api-client.ts`
- `hydra/frontend/src/lib/formatters.ts`

Para tareas `blocked`, solo cuando se desbloqueen con aprobacion explicita:

- `hydra/frontend/src/app/upload/page.tsx`
- `hydra/frontend/src/components/upload/UploadForm.tsx`
- `hydra/frontend/src/components/MainNavigation.tsx`
- `hydra/frontend/src/lib/api-client.ts`
- `hydra/frontend/src/lib/api-types.ts`
- `hydra/frontend/src/components/StateBlock.tsx`

## Forbidden files

- `hydra/backend/**`
- `hydra/sdd/**` durante la ejecucion de la mission, salvo que Codex/planner apruebe una actualizacion SDD separada
- `hydra/docs/hydra-brainstorming.md`
- `hydra/docs/**` salvo tarea documental separada
- `hydra/frontend/.env.local`
- `hydra/backend/.env`
- `hydra/.env`
- `hydra/frontend/node_modules/**`
- `hydra/frontend/.next/**`
- `hydra/frontend/src/app/api/**`
- `hydra/frontend/public/**` con documentos reales o datos de corpus
- `hydra/backend/data/**`
- Archivos Neo4j, drivers DB, scripts de scraping o clientes de proveedores LLM
- Cualquier archivo fuera del allowed scope de la tarea activa

## Milestones

| Milestone | Tasks | Resultado esperado |
|---|---|---|
| 1 | TASK-FRONT-001 a TASK-FRONT-004 | Next/Tailwind/TypeScript configurado, env publico y cliente API seguro |
| 2 | TASK-FRONT-005 a TASK-FRONT-008 | Shell funcional, estados compartidos, Corpus y Narrativas |
| 3 | TASK-FRONT-009 a TASK-FRONT-013 | HYDRA Analyst y Briefing con evidencias, limitaciones, council review y trace IDs |
| 4 | TASK-FRONT-014 a TASK-FRONT-017 | Evals manuales, resultados, endurecimiento de estados y build/secret scan final |
| 5 | TASK-FRONT-018 a TASK-FRONT-019 | Bloqueado: upload opcional conectado al pipeline backend |

## Checks por milestone

### Milestone 1

- `cd hydra/frontend && pnpm install`
- `cd hydra/frontend && pnpm install --frozen-lockfile`
- `cd hydra/frontend && pnpm typecheck`
- `cd hydra/frontend && pnpm lint`
- `cd hydra/frontend && pnpm build`
- `test ! -d hydra/frontend/src/app/api`
- `cd hydra/frontend && node -e "const text=require('fs').readFileSync('.env.local.example','utf8'); if(/MODEL_API_KEY|LANGFUSE_SECRET_KEY|DATABASE_URL/.test(text)) process.exit(1); console.log('frontend env example ok')"`

### Milestone 2

- `cd hydra/frontend && pnpm typecheck`
- `cd hydra/frontend && pnpm lint`
- `cd hydra/frontend && pnpm build`
- `grep -R "fetch(" -n hydra/frontend/src | grep -v "src/lib/api-client.ts" && exit 1 || true`
- `grep -R "sectors" -n hydra/frontend/src && exit 1 || true`

### Milestone 3

- `cd hydra/frontend && pnpm typecheck`
- `cd hydra/frontend && pnpm lint`
- `cd hydra/frontend && pnpm build`
- `grep -R "dangerouslySetInnerHTML" -n hydra/frontend/src && exit 1 || true`
- `grep -R "MODEL_API_KEY\|LANGFUSE_SECRET_KEY\|DATABASE_URL" -n hydra/frontend/src hydra/frontend/.env.local.example && exit 1 || true`
- `grep -R "console\.log\|console\.error" -n hydra/frontend/src && exit 1 || true`

### Milestone 4

- `cd hydra/frontend && pnpm install --frozen-lockfile`
- `cd hydra/frontend && pnpm typecheck`
- `cd hydra/frontend && pnpm lint`
- `cd hydra/frontend && pnpm build`
- `test ! -d hydra/frontend/src/app/api`
- `grep -R "GET /evals/cases\|evals/cases\|/evals/cases" -n hydra/frontend/src && exit 1 || true`
- `grep -R "MODEL_API_KEY\|LANGFUSE_SECRET_KEY\|DATABASE_URL\|sk-\|Bearer " -n hydra/frontend --exclude-dir=node_modules --exclude-dir=.next && exit 1 || true`
- `git diff --stat`

### Milestone 5

No ejecutar hasta resolver bloqueos:

- backend `POST /documents/upload` implementado y aceptado;
- pipeline principal estable con corpus local, extraccion, RAG, briefing y evals;
- aprobacion explicita para activar extension opcional de upload;
- confirmacion de formatos permitidos `.txt`, `.md`, `.csv` y no PDF.

Cuando se desbloquee:

- `cd hydra/frontend && pnpm typecheck`
- `cd hydra/frontend && pnpm lint`
- `cd hydra/frontend && pnpm build`
- `grep -R "FileReader\|arrayBuffer\|text()\|MODEL_API_KEY\|LANGFUSE_SECRET_KEY\|DATABASE_URL" -n hydra/frontend/src && exit 1 || true`

## Stop conditions

Parar y reportar si ocurre cualquiera de estas condiciones:

- Necesitas cambiar `hydra/sdd/03-api-contract.md`, `hydra/sdd/frontend-spec.md`, stack frontend, nombres de variables o modelos.
- Una pantalla necesita un endpoint no definido por `sdd/03-api-contract.md`.
- Se intenta crear `hydra/frontend/src/app/api/**`, proxy Next, llamada directa a LLM/provider, embedding, Langfuse o DB.
- Se intenta parsear documentos, hacer chunking, calcular embeddings o ejecutar extraccion en frontend.
- La implementacion requiere backend real, DB viva, corpus real, claves reales o Langfuse real para pasar el build.
- Aparece `MODEL_API_KEY`, `LANGFUSE_SECRET_KEY`, `DATABASE_URL`, bearer tokens, headers completos, stack traces, prompts completos o documentos completos en frontend.
- `pnpm install` falla por red o registry y no se puede generar lockfile de forma legitima.
- Una dependencia nueva no esta declarada por la task activa.
- Upload opcional se intenta implementar antes de backend upload aceptado y aprobacion explicita.
- El diff toca backend, SDD, docs, datos reales, `.env` reales, `node_modules` o `.next`.

## Final report format

Al terminar, Droid debe reportar:

```markdown
## Summary
- [Cambios principales]

## Tasks completed
- TASK-FRONT-xxx: [resultado]

## Files changed
- `path`: [motivo]

## Verification commands
- `[comando]` -> [resultado]

## Blocked tasks
- TASK-FRONT-018: [sigue bloqueada / desbloqueada con evidencia]
- TASK-FRONT-019: [sigue bloqueada / desbloqueada con evidencia]

## API contract notes
- No se inventaron endpoints ni campos no contractuales.
- `sectors` no se implemento como campo obligatorio porque no esta en `GET /narratives`.
- Evals usa case IDs manuales porque no existe `GET /evals/cases`.

## Security check
- No `.env` reales modificados.
- No secretos, headers, stack traces, prompts completos, respuestas completas ni documentos completos en frontend.
- No llamadas directas a LLM providers, embeddings, Langfuse ni DB.
- No parsing/chunking/extraccion en frontend.

## Deviations or blockers
- [Ninguno / detalles]
```
