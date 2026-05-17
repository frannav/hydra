# Tasks - Backend

## TASK-BACK-001: Inicializar backend con uv

Estado: pending  
Prioridad: must

Archivos permitidos:
- `hydra/back/pyproject.toml`
- `hydra/back/uv.lock`

Criterios de aceptacion:
- `cd hydra/back && uv sync` funciona.

## TASK-BACK-002: Crear paquete hydra_api

Estado: pending  
Prioridad: must

Archivos permitidos:
- `hydra/back/src/hydra_api/__init__.py`

Criterios de aceptacion:
- El paquete es importable.

## TASK-BACK-003: Crear configuracion

Estado: pending  
Prioridad: must

Archivos permitidos:
- `hydra/back/src/hydra_api/config.py`
- `hydra/back/.env.example`

Requisitos:
- Usar Pydantic Settings.
- Leer API de modelos, Langfuse y `DATABASE_URL`.
- No hardcodear secretos.

## TASK-BACK-004: Crear main FastAPI

Estado: pending  
Prioridad: must

Archivos permitidos:
- `hydra/back/src/hydra_api/main.py`

Criterios de aceptacion:
- La app FastAPI arranca.

## TASK-BACK-005: Crear healthcheck

Estado: pending  
Prioridad: must

Endpoint:
- `GET /health`

Criterios de aceptacion:
- Devuelve `{"status":"ok","service":"hydra-api"}`.

## TASK-BACK-006: Configurar CORS

Estado: pending  
Prioridad: must

Requisitos:
- Permitir frontend local.
- No abrir CORS de forma innecesaria en produccion.

## TASK-BACK-007: Manejo comun de errores

Estado: pending  
Prioridad: must

Requisitos:
- Respuesta con `{ "error": { "code", "message", "details" } }`.
- No exponer stack traces ni secretos.

## TASK-BACK-008: Logging seguro

Estado: pending  
Prioridad: must

Requisitos:
- No imprimir API keys.
- No imprimir headers completos.

## TASK-BACK-009: Cliente de modelos

Estado: pending  
Prioridad: must

Requisitos:
- API compatible con OpenAI.
- Leer `MODEL_API_KEY` y `MODEL_API_BASE_URL` desde configuracion.
- No hardcodear proveedor ni URL real.

## TASK-BACK-010: Schemas Pydantic base

Estado: pending  
Prioridad: must

Archivos permitidos:
- `hydra/back/src/hydra_api/schemas.py`

Requisitos:
- Schemas para documentos, metadatos, fuentes de ingesta, narrativas, chunks, query, briefing, errores, extracciones, proyeccion de grafo y evals.
- Separar schemas canonicos del dominio de schemas especificos de API.
- No acoplar schemas de extraccion a pgvector, Neo4j ni frontend.
