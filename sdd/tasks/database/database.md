# Tasks - Base de datos

## TASK-DB-001: Docker Compose con PostgreSQL + pgvector

Estado: pending  
Prioridad: must

Archivos permitidos:
- `hydra/docker-compose.yml`

Criterios de aceptacion:
- Postgres arranca localmente.
- pgvector esta disponible.

## TASK-DB-002: Validar extension vector

Estado: pending  
Prioridad: must

Criterios de aceptacion:
- Se puede ejecutar `CREATE EXTENSION IF NOT EXISTS vector`.

## TASK-DB-003: Crear conexion DB

Estado: pending  
Prioridad: must

Archivos permitidos:
- `hydra/back/src/hydra_api/db.py`

## TASK-DB-004: Crear tabla documents

Estado: pending  
Prioridad: must

Campos minimos:
- `id`
- `title`
- `source`
- `url`
- `published_at`
- `domain`
- `raw_path`
- `content_hash`
- `ingestion_source`
- `processing_status`

## TASK-DB-005: Crear tabla document_chunks

Estado: pending  
Prioridad: must

Campos minimos:
- `id`
- `document_id`
- `chunk_index`
- `content`
- `metadata`
- `embedding vector(4096)`

## TASK-DB-006: Crear tabla extractions

Estado: pending  
Prioridad: must

## TASK-DB-007: Crear tabla eval_cases

Estado: pending  
Prioridad: must

## TASK-DB-008: Crear tabla eval_results

Estado: pending  
Prioridad: must

## TASK-DB-009: Crear tabla graph_projection_events

Estado: pending  
Prioridad: should

Objetivo: persistir proyecciones de grafo o estados de sincronizacion con sinks secundarios.

Requisitos:
- No depender de Neo4j.
- Guardar `projection_json`, `schema_version` y `sink_status`.
- Permitir que el MVP funcione aunque no se use esta tabla.

## TASK-DB-010: Documentar DATABASE_URL

Estado: pending  
Prioridad: must

Archivos permitidos:
- `hydra/README.md`
- `hydra/back/.env.example`
