# Tasks - Repo y seguridad

## TASK-REPO-001: Crear estructura base

Estado: done  
Prioridad: must

Objetivo: crear `hydra/frontend/`, `hydra/backend/` y `hydra/sdd/`.

Archivos permitidos:
- `hydra/frontend/`
- `hydra/backend/`
- `hydra/sdd/`

Criterios de aceptacion:
- Las carpetas existen.
- No se crean secretos reales.

## TASK-REPO-002: Crear gitignore

Estado: done  
Prioridad: must

Objetivo: proteger `.env` y artefactos locales.

Archivos permitidos:
- `.gitignore`

Criterios de aceptacion:
- `.env` y `.env.*` quedan ignorados.
- `hydra/.env.example`, `hydra/frontend/.env.local.example` y `hydra/backend/.env.example` no quedan ignorados.

## TASK-REPO-003: Crear env example raiz

Estado: done  
Prioridad: should

Objetivo: documentar variables compartidas por Docker o infraestructura.

Archivos permitidos:
- `hydra/.env.example`

Criterios de aceptacion:
- No contiene secretos reales.

## TASK-REPO-004: Crear env example backend

Estado: done  
Prioridad: must

Archivos permitidos:
- `hydra/backend/.env.example`

Criterios de aceptacion:
- Incluye API de modelos, Langfuse y `DATABASE_URL` con valores ficticios.

## TASK-REPO-005: Crear env example frontend

Estado: done  
Prioridad: must

Archivos permitidos:
- `hydra/frontend/.env.local.example`

Criterios de aceptacion:
- Solo incluye `NEXT_PUBLIC_API_BASE_URL`.
- No incluye claves privadas.

## TASK-REPO-006: Documentar gestion de secretos

Estado: done  
Prioridad: must

Archivos permitidos:
- `hydra/README.md`

Criterios de aceptacion:
- Explica `.env`, `.env.example` y prohibicion de subir claves.

## TASK-REPO-007: Revisar secretos

Estado: done  
Prioridad: must

Objetivo: verificar antes de publicar.

Comandos de verificacion:
- `git diff`

Criterios de aceptacion:
- No aparecen claves reales ni tokens.
