# Repair Packet — Mission 08 Frontend

## Objetivo

Corregir de forma atomica los bloqueantes detectados en la revision de la
mission frontend para poder ejecutar despues `TASK-FRONT-017` como validacion
final.

## Veredicto de revision

Mission 08 **no queda aprobada** hasta aplicar este repair.

La implementacion actual compila y respeta la mayor parte del contrato, pero
todavia hay incumplimientos pequeños de SDD en shell, evals, retry, timeout y
checks literales.

## Source of truth

Antes de ejecutar, leer solo:

- `hydra/sdd/README.md`
- `hydra/sdd/01-architecture-decisions.md`
- `hydra/sdd/03-api-contract.md`
- `hydra/sdd/frontend-spec.md`
- `hydra/sdd/tasks/08-frontend/08-frontend.md`
- `hydra/sdd/tasks/08-frontend/08-frontend-mission.md`

No usar `docs/hydra-brainstorming.md`.
No cambiar arquitectura, contrato API, stack, variables de entorno ni SDD.

## Task ID

`TASK-REPAIR-FRONT-001`

## Scope atomico

Hacer solo los fixes necesarios para que la mission frontend pase revision:

1. Evitar `AppShell`/navegacion duplicada en `/`.
2. Mostrar `trace_id` de la respuesta de `POST /evals/run`.
3. Quitar botones de retry sin efecto o convertirlos en retry real seguro.
4. Implementar timeout real en el cliente HTTP.
5. Hacer que el grep SDD de `dangerouslySetInnerHTML` pase.

No implementar features nuevas.
No tocar upload opcional.
No tocar `.gitignore`; el diff actual de `.gitignore` queda fuera de este
repair y lo decide Codex/reviewer aparte.

## Archivos permitidos

Solo pueden modificarse:

- `hydra/frontend/src/app/page.tsx`
- `hydra/frontend/src/app/analyst/page.tsx`
- `hydra/frontend/src/app/briefing/page.tsx`
- `hydra/frontend/src/app/evals/page.tsx`
- `hydra/frontend/src/components/briefing/BriefingResult.tsx`
- `hydra/frontend/src/lib/api-client.ts`

## Archivos prohibidos

- `hydra/backend/**`
- `hydra/sdd/**`
- `hydra/docs/**`
- `hydra/frontend/package.json`
- `hydra/frontend/pnpm-lock.yaml`
- `hydra/frontend/.env.local`
- `hydra/.env`
- `hydra/backend/.env`
- `hydra/frontend/src/app/api/**`
- `hydra/frontend/node_modules/**`
- `hydra/frontend/.next/**`
- `.gitignore`
- cualquier archivo fuera de los permitidos

## Requisitos

### 1. Shell sin duplicados

- `RootLayout` ya envuelve la app con `AppShell`.
- En `hydra/frontend/src/app/page.tsx`, eliminar el `AppShell` anidado.
- Mantener el dashboard funcional y los enlaces a:
  - `/corpus`
  - `/narratives`
  - `/analyst`
  - `/briefing`
  - `/evals`
- No añadir enlaces a `/upload`, `/graph`, `/admin` ni rutas inexistentes.

### 2. Evals run traceable

- En `hydra/frontend/src/app/evals/page.tsx`, mostrar `response.trace_id` del
  resultado de `POST /evals/run` usando `TraceId`.
- Si falta `trace_id`, mostrar `No disponible`; no inventar IDs.
- Mantener visible `run_id`, `total_cases` y `results_path`.
- No leer `results_path` desde filesystem.

### 3. Retry seguro

- No dejar `onRetry={() => {}}` ni botones que no hacen nada.
- Para errores de submit en Analyst, Briefing y Evals, elegir una de estas dos
  opciones:
  - retirar `onRetry` para no renderizar boton falso; o
  - guardar la ultima request valida y reejecutarla al pulsar retry.
- Preferencia: retirar `onRetry` en estos formularios para mantener el repair
  pequeño; el usuario puede reenviar desde el formulario preservado.
- No borrar la pregunta/case IDs del usuario en errores.
- No ejecutar llamadas automaticas al cargar Analyst/Briefing/Evals.

### 4. Timeout real en cliente API

- En `hydra/frontend/src/lib/api-client.ts`, implementar timeout con
  `AbortController`.
- Usar un timeout razonable local, por ejemplo `15_000` ms.
- Si expira, devolver error seguro:
  - `code: "timeout"`
  - mensaje sin stack trace, headers, URL completa sensible ni detalles internos.
- Mantener el manejo actual de:
  - error `{ error: { code, message, details } }`;
  - backend caido;
  - JSON invalido;
  - 204/empty body.
- No loggear payloads, preguntas, headers, prompts, respuestas completas ni
  trace IDs.

### 5. Grep literal de HTML inseguro

- El comando SDD `grep -R "dangerouslySetInnerHTML" -n hydra/frontend/src`
  debe no encontrar nada.
- No usar esa API.
- Si existe la cadena solo en comentarios, reescribir el comentario para que no
  contenga el literal.
- Mantener `react-markdown` para render seguro del briefing.

## Criterios de aceptacion

- `/` no renderiza navegacion duplicada.
- `/evals` muestra `trace_id` del run o `No disponible`.
- No hay retry buttons sin efecto.
- El cliente HTTP aborta requests colgadas y muestra error seguro.
- No aparece el literal `dangerouslySetInnerHTML` en `hydra/frontend/src`.
- No se modifica ningun archivo fuera del allowed scope.
- No se introducen dependencias nuevas.
- No hay secretos ni variables privadas en frontend.

## Comandos de verificacion

Ejecutar desde repo root:

```bash
cd hydra/frontend && pnpm typecheck
cd hydra/frontend && pnpm lint
cd hydra/frontend && pnpm build
grep -R "dangerouslySetInnerHTML" -n hydra/frontend/src && exit 1 || true
grep -R "console\.log\|console\.error\|alert(" -n hydra/frontend/src && exit 1 || true
grep -R "fetch(" -n hydra/frontend/src | grep -v "src/lib/api-client.ts" && exit 1 || true
grep -R "GET /evals/cases\|evals/cases\|/evals/cases\|/upload\|/graph" -n hydra/frontend/src && exit 1 || true
grep -R "MODEL_API_KEY\|LANGFUSE_SECRET_KEY\|DATABASE_URL\|sk-\|Bearer " -n hydra/frontend --exclude-dir=node_modules --exclude-dir=.next && exit 1 || true
test ! -d hydra/frontend/src/app/api
git diff --stat
git diff --name-only
```

El `git diff --name-only` debe contener solo los archivos permitidos de este
repair, salvo cambios preexistentes reportados explicitamente como fuera de
scope.

## Stop conditions

Parar y reportar si:

- Hace falta cambiar `sdd/03-api-contract.md`, `frontend-spec.md`, backend o
  nombres de variables.
- Hace falta añadir dependencias o regenerar `pnpm-lock.yaml`.
- Se necesita backend real, DB viva, modelos reales, Langfuse real, corpus real
  o claves reales para pasar la verificacion.
- Una solucion exige Next API routes, proxy frontend, llamadas directas a LLM,
  embeddings, DB, parsing, chunking o extraccion en frontend.
- El diff toca archivos fuera del allowed scope.

## Report back

Droid debe devolver:

```markdown
## Summary
- [Cambios realizados]

## Files changed
- `path`: [motivo]

## Verification commands
- `[comando]` -> [resultado]

## Scope check
- Solo se modificaron archivos permitidos: si/no
- Archivos preexistentes fuera de scope detectados: [lista o ninguno]

## Security/API contract check
- No secretos ni variables privadas en frontend.
- No endpoints inventados.
- No Next API routes.
- No parsing/chunking/extraccion/modelos en frontend.

## Blockers
- [Ninguno / detalles]
```
