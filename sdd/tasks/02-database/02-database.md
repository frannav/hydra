# Tasks - Base de datos

## Reglas de atomizacion

- Ejecutar estas tareas en orden.
- No tocar frontend.
- No crear ni modificar `.env` reales.
- No introducir Neo4j como dependencia del MVP.
- No introducir ORM, Alembic ni otro sistema de migraciones salvo que el SDD cambie o se pida confirmacion.
- Para el MVP, usar PostgreSQL + pgvector con SQL idempotente y un helper backend minimo.
- Las tablas usan `JSONB` para payloads estructurados y `vector(4096)` para embeddings.
- No marcar tareas como `done` hasta que Codex/reviewer revise diff, comandos y secretos.

## TASK-DB-001: Crear Docker Compose con PostgreSQL + pgvector

Estado: pending
Prioridad: must

Objetivo:
Arrancar una base PostgreSQL local con pgvector para desarrollo y demo.

Archivos permitidos:
- `hydra/docker-compose.yml`
- `hydra/.env.example`

Dependencias:
- TASK-REPO-003

Requisitos:
- Crear un servicio `postgres`.
- Usar una imagen PostgreSQL con pgvector disponible.
- Exponer `5432:5432` para desarrollo local.
- Usar valores locales no secretos para database, user y password (`hydra`).
- Definir volumen persistente local.
- Incluir healthcheck con `pg_isready`.
- No anadir Neo4j ni otros servicios.

Criterios de aceptacion:
- `docker compose config` es valido.
- El servicio `postgres` puede arrancar localmente.
- No se versiona ningun `.env` real.

Comandos de verificacion:
- `docker compose config`
- `docker compose up -d postgres`
- `docker compose ps`

## TASK-DB-002: Validar extension pgvector

Estado: pending
Prioridad: must

Objetivo:
Confirmar que la extension `vector` existe y puede crearse en la DB local.

Archivos permitidos:
- Ninguno

Dependencias:
- TASK-DB-001

Requisitos:
- Ejecutar `CREATE EXTENSION IF NOT EXISTS vector`.
- No modificar codigo.

Criterios de aceptacion:
- La extension `vector` aparece en `pg_extension`.

Comandos de verificacion:
- `docker compose exec -T postgres psql -U hydra -d hydra -c "CREATE EXTENSION IF NOT EXISTS vector;"`
- `docker compose exec -T postgres psql -U hydra -d hydra -c "SELECT extname FROM pg_extension WHERE extname = 'vector';"`

## TASK-DB-003: Anadir dependencia de conexion PostgreSQL

Estado: pending
Prioridad: must

Objetivo:
Preparar el backend para conectarse a PostgreSQL sin introducir ORM.

Archivos permitidos:
- `hydra/backend/pyproject.toml`
- `hydra/backend/uv.lock`

Dependencias:
- TASK-BACK-001

Requisitos:
- Anadir `psycopg[binary]` si no existe.
- No anadir SQLAlchemy, Alembic ni ORMs.
- No modificar codigo de aplicacion en esta tarea.

Criterios de aceptacion:
- `psycopg` es importable desde el entorno `uv`.

Comandos de verificacion:
- `cd hydra/backend && uv sync`
- `cd hydra/backend && uv run python -c "import psycopg; print(psycopg.__name__)"`

## TASK-DB-004: Crear helper de conexion DB

Estado: pending
Prioridad: must

Objetivo:
Crear un modulo de conexion seguro y reutilizable para PostgreSQL.

Archivos permitidos:
- `hydra/backend/src/hydra_api/db.py`

Dependencias:
- TASK-BACK-003
- TASK-DB-003

Requisitos:
- Crear `normalize_database_url(database_url: str) -> str`.
- Soportar `postgresql+psycopg://...` convirtiendolo a `postgresql://...` para `psycopg`.
- Crear `get_connection(database_url: str | None = None)`.
- Si `database_url` es `None`, leerla desde `get_settings()`.
- No abrir conexiones en import time.
- No imprimir `DATABASE_URL` completa en logs ni errores.
- No crear tablas en esta tarea.

Criterios de aceptacion:
- El modulo importa sin conectar a la DB.
- La normalizacion de URL funciona.
- La conexion se crea solo cuando se llama explicitamente a `get_connection`.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "from hydra_api.db import normalize_database_url; print(normalize_database_url('postgresql+psycopg://hydra:hydra@localhost:5432/hydra'))"`
- `cd hydra/backend && uv run python -c "from hydra_api.db import get_connection; print(callable(get_connection))"`

## TASK-DB-005: Crear modulo de schema SQL

Estado: pending
Prioridad: must

Objetivo:
Centralizar las sentencias SQL idempotentes del schema MVP.

Archivos permitidos:
- `hydra/backend/src/hydra_api/db_schema.py`

Dependencias:
- TASK-DB-004

Requisitos:
- Definir `SCHEMA_VERSION`.
- Definir `SCHEMA_STATEMENTS` como lista ordenada de sentencias SQL.
- Incluir `CREATE EXTENSION IF NOT EXISTS vector`.
- No conectarse a la DB en import time.
- No incluir datos de ejemplo.

Criterios de aceptacion:
- El modulo importa sin tocar la DB.
- Existe una lista de sentencias reutilizable por `db.py`.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "from hydra_api.db_schema import SCHEMA_VERSION, SCHEMA_STATEMENTS; print(SCHEMA_VERSION, isinstance(SCHEMA_STATEMENTS, list))"`

## TASK-DB-006: Definir tabla documents

Estado: pending
Prioridad: must

Objetivo:
Definir la tabla canonica de documentos del corpus.

Archivos permitidos:
- `hydra/backend/src/hydra_api/db_schema.py`

Dependencias:
- TASK-DB-005

Requisitos:
- Anadir `CREATE TABLE IF NOT EXISTS documents`.
- Campos minimos:
  - `id TEXT PRIMARY KEY`
  - `title TEXT NOT NULL`
  - `source TEXT NOT NULL`
  - `url TEXT`
  - `published_at DATE`
  - `domain TEXT NOT NULL`
  - `raw_path TEXT NOT NULL`
  - `content_hash TEXT NOT NULL UNIQUE`
  - `ingestion_source TEXT NOT NULL`
  - `processing_status TEXT NOT NULL DEFAULT 'pending'`
- Permitir solo `ingestion_source` `local_corpus` o `frontend_upload`.
- No anadir campos analiticos que pertenezcan a extracciones.

Criterios de aceptacion:
- La sentencia es idempotente.
- Los campos minimos del SDD estan presentes.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "from hydra_api.db_schema import SCHEMA_STATEMENTS; print(any('CREATE TABLE IF NOT EXISTS documents' in s for s in SCHEMA_STATEMENTS))"`

## TASK-DB-007: Definir tabla document_chunks

Estado: pending
Prioridad: must

Objetivo:
Definir almacenamiento de chunks y embeddings pgvector.

Archivos permitidos:
- `hydra/backend/src/hydra_api/db_schema.py`

Dependencias:
- TASK-DB-006

Requisitos:
- Anadir `CREATE TABLE IF NOT EXISTS document_chunks`.
- Campos minimos:
  - `id TEXT PRIMARY KEY`
  - `document_id TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE`
  - `chunk_index INTEGER NOT NULL`
  - `content TEXT NOT NULL`
  - `metadata JSONB NOT NULL DEFAULT '{}'::jsonb`
  - `embedding vector(4096)`
- Anadir `UNIQUE(document_id, chunk_index)`.
- No calcular embeddings en esta tarea.

Criterios de aceptacion:
- La tabla referencia `documents`.
- `embedding` usa dimension `4096`.
- La sentencia es idempotente.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "from hydra_api.db_schema import SCHEMA_STATEMENTS; sql='\\n'.join(SCHEMA_STATEMENTS); print('document_chunks' in sql and 'vector(4096)' in sql)"`

## TASK-DB-008: Definir tabla extractions

Estado: pending
Prioridad: must

Objetivo:
Persistir extracciones estructuradas validadas como artefacto canonico.

Archivos permitidos:
- `hydra/backend/src/hydra_api/db_schema.py`

Dependencias:
- TASK-DB-006

Requisitos:
- Anadir `CREATE TABLE IF NOT EXISTS extractions`.
- Campos minimos:
  - `id TEXT PRIMARY KEY`
  - `document_id TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE`
  - `extraction_json JSONB NOT NULL`
  - `schema_version TEXT NOT NULL`
  - `created_at TIMESTAMPTZ NOT NULL DEFAULT now()`
- No acoplar la tabla a pgvector, Neo4j ni frontend.

Criterios de aceptacion:
- La extraccion se guarda como JSONB validable.
- La tabla referencia `documents`.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "from hydra_api.db_schema import SCHEMA_STATEMENTS; sql='\\n'.join(SCHEMA_STATEMENTS); print('CREATE TABLE IF NOT EXISTS extractions' in sql and 'extraction_json JSONB' in sql)"`

## TASK-DB-009: Definir tabla eval_cases

Estado: pending
Prioridad: must

Objetivo:
Persistir casos de evaluacion offline.

Archivos permitidos:
- `hydra/backend/src/hydra_api/db_schema.py`

Dependencias:
- TASK-DB-005

Requisitos:
- Anadir `CREATE TABLE IF NOT EXISTS eval_cases`.
- Campos minimos:
  - `id TEXT PRIMARY KEY`
  - `question TEXT NOT NULL`
  - `expected_documents JSONB NOT NULL DEFAULT '[]'::jsonb`
  - `expected_topics JSONB NOT NULL DEFAULT '[]'::jsonb`
  - `expected_answer_traits JSONB NOT NULL DEFAULT '[]'::jsonb`
  - `tags JSONB NOT NULL DEFAULT '[]'::jsonb`

Criterios de aceptacion:
- La sentencia es idempotente.
- Los campos esperados por evals estan presentes.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "from hydra_api.db_schema import SCHEMA_STATEMENTS; sql='\\n'.join(SCHEMA_STATEMENTS); print('CREATE TABLE IF NOT EXISTS eval_cases' in sql and 'expected_documents JSONB' in sql)"`

## TASK-DB-010: Definir tabla eval_results

Estado: pending
Prioridad: must

Objetivo:
Persistir resultados de ejecuciones de evals.

Archivos permitidos:
- `hydra/backend/src/hydra_api/db_schema.py`

Dependencias:
- TASK-DB-009

Requisitos:
- Anadir `CREATE TABLE IF NOT EXISTS eval_results`.
- Campos minimos:
  - `id TEXT PRIMARY KEY`
  - `eval_case_id TEXT NOT NULL REFERENCES eval_cases(id) ON DELETE CASCADE`
  - `trace_id TEXT`
  - `metrics_json JSONB NOT NULL`
  - `passed BOOLEAN NOT NULL DEFAULT false`
  - `created_at TIMESTAMPTZ NOT NULL DEFAULT now()`

Criterios de aceptacion:
- La tabla referencia `eval_cases`.
- Los resultados guardan `trace_id` y metricas JSON.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "from hydra_api.db_schema import SCHEMA_STATEMENTS; sql='\\n'.join(SCHEMA_STATEMENTS); print('CREATE TABLE IF NOT EXISTS eval_results' in sql and 'metrics_json JSONB' in sql)"`

## TASK-DB-011: Definir tabla graph_projection_events

Estado: pending
Prioridad: should

Objetivo:
Persistir proyecciones de grafo o estados de sincronizacion con sinks secundarios sin depender de Neo4j.

Archivos permitidos:
- `hydra/backend/src/hydra_api/db_schema.py`

Dependencias:
- TASK-DB-006

Requisitos:
- Anadir `CREATE TABLE IF NOT EXISTS graph_projection_events`.
- Campos minimos:
  - `id TEXT PRIMARY KEY`
  - `document_id TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE`
  - `projection_json JSONB NOT NULL`
  - `schema_version TEXT NOT NULL`
  - `sink_status TEXT NOT NULL DEFAULT 'pending'`
  - `created_at TIMESTAMPTZ NOT NULL DEFAULT now()`
- No conectarse a Neo4j.
- Permitir que el MVP funcione aunque esta tabla no se use todavia.

Criterios de aceptacion:
- La tabla no introduce dependencia runtime con Neo4j.
- La proyeccion se guarda como JSONB.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "from hydra_api.db_schema import SCHEMA_STATEMENTS; sql='\\n'.join(SCHEMA_STATEMENTS); print('CREATE TABLE IF NOT EXISTS graph_projection_events' in sql and 'projection_json JSONB' in sql)"`

## TASK-DB-012: Crear inicializador de schema

Estado: pending
Prioridad: must

Objetivo:
Ejecutar el schema SQL idempotente contra la DB local.

Archivos permitidos:
- `hydra/backend/src/hydra_api/db.py`
- `hydra/backend/src/hydra_api/db_schema.py`

Dependencias:
- TASK-DB-005
- TASK-DB-006
- TASK-DB-007
- TASK-DB-008
- TASK-DB-009
- TASK-DB-010

Requisitos:
- Crear `init_db(database_url: str | None = None)`.
- Ejecutar `SCHEMA_STATEMENTS` en orden dentro de una transaccion.
- Anadir CLI minima con `python -m hydra_api.db --init`.
- Anadir opcion segura `--print-schema` que no conecte a la DB.
- No ejecutar inicializacion en import time.
- No imprimir `DATABASE_URL` completa.

Criterios de aceptacion:
- `init_db` es importable y callable.
- `--print-schema` muestra el schema sin conectar.
- `--init` inicializa tablas cuando Postgres esta arrancado.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "from hydra_api.db import init_db; print(callable(init_db))"`
- `cd hydra/backend && uv run python -m hydra_api.db --print-schema`
- `cd hydra/backend && DATABASE_URL=postgresql+psycopg://hydra:hydra@localhost:5432/hydra uv run python -m hydra_api.db --init`

## TASK-DB-013: Verificar tablas en PostgreSQL

Estado: pending
Prioridad: must

Objetivo:
Comprobar que el schema MVP existe realmente en la DB local.

Archivos permitidos:
- Ninguno

Dependencias:
- TASK-DB-001
- TASK-DB-002
- TASK-DB-012

Requisitos:
- Verificar existencia de todas las tablas must.
- Verificar que `document_chunks.embedding` usa pgvector.
- No modificar codigo.

Criterios de aceptacion:
- Existen `documents`, `document_chunks`, `extractions`, `eval_cases` y `eval_results`.
- Si TASK-DB-011 se ejecuto, existe tambien `graph_projection_events`.
- `document_chunks.embedding` aparece como `vector`.

Comandos de verificacion:
- `docker compose exec -T postgres psql -U hydra -d hydra -c "SELECT to_regclass('documents'), to_regclass('document_chunks'), to_regclass('extractions'), to_regclass('eval_cases'), to_regclass('eval_results');"`
- `docker compose exec -T postgres psql -U hydra -d hydra -c "\\d+ document_chunks"`

## TASK-DB-014: Documentar DATABASE_URL

Estado: pending
Prioridad: must

Objetivo:
Documentar como configurar la URL de base de datos local.

Archivos permitidos:
- `hydra/README.md`
- `hydra/.env.example`
- `hydra/backend/.env.example`

Dependencias:
- TASK-DB-001

Requisitos:
- Documentar `DATABASE_URL`.
- Usar el formato canonico del SDD: `postgresql+psycopg://hydra:hydra@localhost:5432/hydra`.
- Explicar que los valores locales son de desarrollo y no secretos reales.
- No incluir credenciales reales.

Criterios de aceptacion:
- README explica como levantar Postgres y configurar `DATABASE_URL`.
- Los `.env.example` contienen valores ficticios/locales seguros.
- No aparecen claves reales ni tokens.

Comandos de verificacion:
- `git diff`
