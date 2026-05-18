# Tasks - Base de datos

## Reglas de atomizacion

- Ejecutar estas tareas en orden.
- Cada tarea debe ser verificable por comandos concretos.
- No tocar frontend.
- No crear ni modificar `.env` reales.
- No introducir Neo4j como dependencia del MVP.
- No introducir ORM, SQLAlchemy, Alembic ni otro sistema de migraciones salvo que el SDD cambie o el usuario lo confirme.
- Para el MVP, usar PostgreSQL + pgvector con SQL idempotente y un helper backend minimo.
- Usar `psycopg[binary]` para conexion backend.
- Las tablas usan `JSONB` para payloads estructurados y `vector(4096)` para embeddings.
- No hacer scraping, ingesta, chunking ni embeddings en tareas DB.
- No insertar datos reales ni datos de ejemplo salvo que una tarea futura lo pida.
- No ejecutar borrados destructivos (`DROP TABLE`, `DROP DATABASE`, `docker compose down -v`) salvo confirmacion explicita.
- No imprimir `DATABASE_URL` completa en logs, errores ni reportes.
- No marcar tareas como `done` hasta que Codex/reviewer revise diff, comandos y secretos.

## Lecciones incorporadas antes de la mission DB

- Las tareas deben especificar `Allowed files`, dependencias y comandos de verificacion.
- Las verificaciones deben cubrir idempotencia y edge cases, no solo import/happy path.
- Separar infraestructura Docker, dependencia Python, helper de conexion, schema SQL, inicializacion y documentacion.
- Evitar que Droid invente arquitectura de persistencia: raw SQL idempotente + `psycopg[binary]`.
- Mantener DB desacoplada de schemas canonicos, frontend, Neo4j y proveedores LLM.
- Si Droid necesita cambiar scope, debe parar y explicarlo.

## Milestones sugeridos para Droid Missions

| Milestone | Tareas | Objetivo | Debe parar para review |
|---|---|---|---|
| 1 | TASK-DB-001 a TASK-DB-004 | Docker Compose + Postgres + pgvector vivo | Si Docker no arranca o pgvector no existe |
| 2 | TASK-DB-005 a TASK-DB-008 | Dependencia `psycopg`, URL segura y conexion lazy | Si propone ORM/Alembic o imprime credenciales |
| 3 | TASK-DB-009 a TASK-DB-016 | Schema SQL idempotente, una tabla por tarea | Si rompe orden, acopla Neo4j o cambia dimension |
| 4 | TASK-DB-017 a TASK-DB-020 | Inicializador/CLI e idempotencia real en DB | Si falla init dos veces o no verifica tablas |
| 5 | TASK-DB-021 | Documentacion y env examples | Si toca docs fuera de scope o mete secretos |

## TASK-DB-001: Crear Docker Compose Postgres

Estado: done
Prioridad: must

Objetivo:
Crear la infraestructura local minima de PostgreSQL para desarrollo.

Archivos permitidos:
- `hydra/docker-compose.yml`

Dependencias:
- TASK-REPO-001

Requisitos:
- Crear un servicio `postgres`.
- Usar imagen PostgreSQL con pgvector disponible.
- Usar tag explicito, no `latest`.
- Exponer `5432:5432` para desarrollo local.
- Configurar valores locales no secretos:
  - `POSTGRES_DB=hydra`
  - `POSTGRES_USER=hydra`
  - `POSTGRES_PASSWORD=hydra`
- Definir volumen persistente local para datos Postgres.
- Incluir healthcheck con `pg_isready`.
- No anadir Neo4j ni otros servicios.
- No depender de `.env` real.

Criterios de aceptacion:
- `docker compose config` es valido.
- No se versiona ningun `.env` real.

Comandos de verificacion:
- `docker compose config`
- `git status --short`

## TASK-DB-002: Arrancar Postgres local

Estado: done
Prioridad: must

Objetivo:
Comprobar que el servicio Postgres definido en Compose arranca localmente.

Archivos permitidos:
- Ninguno

Dependencias:
- TASK-DB-001

Requisitos:
- Arrancar solo el servicio `postgres`.
- No ejecutar `docker compose down -v`.
- No modificar codigo.

Criterios de aceptacion:
- El contenedor queda `running` o `healthy`.
- `psql` responde dentro del contenedor.

Comandos de verificacion:
- `docker compose up -d postgres`
- `docker compose ps`
- `docker compose exec -T postgres psql -U hydra -d hydra -c "SELECT current_database(), current_user;"`

## TASK-DB-003: Validar extension pgvector

Estado: done
Prioridad: must

Objetivo:
Confirmar que la extension `vector` existe y puede crearse en la DB local.

Archivos permitidos:
- Ninguno

Dependencias:
- TASK-DB-002

Requisitos:
- Ejecutar `CREATE EXTENSION IF NOT EXISTS vector`.
- Verificar que `vector` aparece en `pg_extension`.
- No modificar codigo.

Criterios de aceptacion:
- La extension `vector` queda instalada en la base `hydra`.

Comandos de verificacion:
- `docker compose exec -T postgres psql -U hydra -d hydra -c "CREATE EXTENSION IF NOT EXISTS vector;"`
- `docker compose exec -T postgres psql -U hydra -d hydra -c "SELECT extname FROM pg_extension WHERE extname = 'vector';"`

## TASK-DB-004: Verificar idempotencia basica de pgvector

Estado: done
Prioridad: must

Objetivo:
Evitar fallos por reejecutar inicializaciones de extension.

Archivos permitidos:
- Ninguno

Dependencias:
- TASK-DB-003

Requisitos:
- Ejecutar dos veces `CREATE EXTENSION IF NOT EXISTS vector`.
- No modificar codigo.
- No usar comandos destructivos.

Criterios de aceptacion:
- Ambas ejecuciones pasan sin error.

Comandos de verificacion:
- `docker compose exec -T postgres psql -U hydra -d hydra -c "CREATE EXTENSION IF NOT EXISTS vector; CREATE EXTENSION IF NOT EXISTS vector;"`

## TASK-DB-005: Anadir dependencia psycopg

Estado: done
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
- No ejecutar builds que dejen artefactos versionables.

Criterios de aceptacion:
- `psycopg` es importable desde el entorno `uv`.
- `pyproject.toml` no contiene SQLAlchemy ni Alembic.

Comandos de verificacion:
- `cd hydra/backend && uv sync`
- `cd hydra/backend && uv run python -c "import psycopg; print(psycopg.__name__)"`
- `cd hydra/backend && uv run python -c "import pathlib; text=pathlib.Path('pyproject.toml').read_text().lower(); assert 'sqlalchemy' not in text and 'alembic' not in text; print('no orm')"`

## TASK-DB-006: Crear normalizador de DATABASE_URL

Estado: done
Prioridad: must

Objetivo:
Convertir el formato canonico del SDD a un DSN aceptado por `psycopg`.

Archivos permitidos:
- `hydra/backend/src/hydra_api/db.py`

Dependencias:
- TASK-BACK-003
- TASK-DB-005

Requisitos:
- Crear `normalize_database_url(database_url: str) -> str`.
- Convertir `postgresql+psycopg://...` a `postgresql://...`.
- Dejar sin cambios `postgresql://...`.
- Preservar usuario, password, host, puerto, database y query string.
- Rechazar o fallar con mensaje claro si el string esta vacio.
- No abrir conexiones en import time.
- No crear tablas en esta tarea.

Criterios de aceptacion:
- El modulo importa sin conectar a la DB.
- La normalizacion funciona para URL canonica y URL ya normalizada.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "from hydra_api.db import normalize_database_url; assert normalize_database_url('postgresql+psycopg://hydra:hydra@localhost:5432/hydra') == 'postgresql://hydra:hydra@localhost:5432/hydra'; print('canonical ok')"`
- `cd hydra/backend && uv run python -c "from hydra_api.db import normalize_database_url; assert normalize_database_url('postgresql://u:p@localhost:5432/db?sslmode=disable') == 'postgresql://u:p@localhost:5432/db?sslmode=disable'; print('plain ok')"`

## TASK-DB-007: Crear redactor seguro de DATABASE_URL

Estado: done
Prioridad: must

Objetivo:
Evitar que credenciales de DB aparezcan en logs, errores o reportes.

Archivos permitidos:
- `hydra/backend/src/hydra_api/db.py`

Dependencias:
- TASK-DB-006

Requisitos:
- Crear `redact_database_url(database_url: str) -> str`.
- Enmascarar password si existe.
- No eliminar host, puerto ni database porque son utiles para diagnostico.
- Soportar URLs con y sin password.
- No imprimir automaticamente la URL.

Criterios de aceptacion:
- Una URL con password no expone el password completo.
- Una URL sin password sigue siendo legible.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "from hydra_api.db import redact_database_url; out = redact_database_url('postgresql+psycopg://hydra:secret_password@localhost:5432/hydra'); print(out); assert 'secret_password' not in out"`
- `cd hydra/backend && uv run python -c "from hydra_api.db import redact_database_url; out = redact_database_url('postgresql://localhost:5432/hydra'); print(out); assert 'localhost' in out"`

## TASK-DB-008: Crear helper de conexion lazy

Estado: done
Prioridad: must

Objetivo:
Crear una funcion reutilizable para abrir conexiones PostgreSQL solo bajo demanda.

Archivos permitidos:
- `hydra/backend/src/hydra_api/db.py`

Dependencias:
- TASK-BACK-003
- TASK-DB-006
- TASK-DB-007

Requisitos:
- Crear `get_connection(database_url: str | None = None)`.
- Si `database_url` es `None`, leerla desde `get_settings()`.
- Usar `normalize_database_url()` antes de conectar.
- No abrir conexiones en import time.
- No imprimir `DATABASE_URL` completa.
- No crear tablas en esta tarea.

Criterios de aceptacion:
- `get_connection` es callable.
- Importar `hydra_api.db` no conecta a la DB.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "from hydra_api.db import get_connection; print(callable(get_connection))"`
- `cd hydra/backend && uv run python -c "import hydra_api.db; print('import ok')"`

## TASK-DB-009: Crear modulo de schema SQL base

Estado: done
Prioridad: must

Objetivo:
Centralizar las sentencias SQL idempotentes del schema MVP.

Archivos permitidos:
- `hydra/backend/src/hydra_api/db_schema.py`

Dependencias:
- TASK-DB-005

Requisitos:
- Definir `SCHEMA_VERSION`.
- Definir `SCHEMA_STATEMENTS` como lista ordenada de sentencias SQL.
- La primera sentencia debe incluir `CREATE EXTENSION IF NOT EXISTS vector`.
- No conectarse a la DB en import time.
- No incluir datos de ejemplo.
- No importar FastAPI, frontend, Neo4j ni clientes de modelos.

Criterios de aceptacion:
- El modulo importa sin tocar la DB.
- Existe una lista de sentencias reutilizable por `db.py`.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "from hydra_api.db_schema import SCHEMA_VERSION, SCHEMA_STATEMENTS; print(SCHEMA_VERSION, isinstance(SCHEMA_STATEMENTS, list), len(SCHEMA_STATEMENTS))"`
- `cd hydra/backend && uv run python -c "from hydra_api.db_schema import SCHEMA_STATEMENTS; assert 'CREATE EXTENSION IF NOT EXISTS vector' in SCHEMA_STATEMENTS[0]; print('extension first')"`

## TASK-DB-010: Definir tabla documents

Estado: done
Prioridad: must

Objetivo:
Definir la tabla canonica de documentos del corpus.

Archivos permitidos:
- `hydra/backend/src/hydra_api/db_schema.py`

Dependencias:
- TASK-DB-009

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
- `ingestion_source` solo permite `local_corpus` o `frontend_upload`.
- `processing_status` solo permite `pending`, `processing`, `processed` o `failed`.
- No anadir campos analiticos que pertenezcan a extracciones.

Criterios de aceptacion:
- La sentencia es idempotente.
- Los campos minimos del SDD estan presentes.
- Hay constraints para estados/fuentes controladas.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "from hydra_api.db_schema import SCHEMA_STATEMENTS; sql='\\n'.join(SCHEMA_STATEMENTS); assert 'CREATE TABLE IF NOT EXISTS documents' in sql and 'content_hash TEXT NOT NULL UNIQUE' in sql and 'local_corpus' in sql and 'frontend_upload' in sql; print('documents ok')"`

## TASK-DB-011: Definir tabla document_chunks

Estado: done
Prioridad: must

Objetivo:
Definir almacenamiento de chunks y embeddings pgvector.

Archivos permitidos:
- `hydra/backend/src/hydra_api/db_schema.py`

Dependencias:
- TASK-DB-010

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
- No crear indices vectoriales avanzados hasta que RAG lo requiera.

Criterios de aceptacion:
- La tabla referencia `documents`.
- `embedding` usa dimension `4096`.
- La sentencia es idempotente.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "from hydra_api.db_schema import SCHEMA_STATEMENTS; sql='\\n'.join(SCHEMA_STATEMENTS); assert 'CREATE TABLE IF NOT EXISTS document_chunks' in sql and 'REFERENCES documents(id) ON DELETE CASCADE' in sql and 'vector(4096)' in sql; print('chunks ok')"`

## TASK-DB-012: Definir tabla extractions

Estado: done
Prioridad: must

Objetivo:
Persistir extracciones estructuradas validadas como artefacto canonico.

Archivos permitidos:
- `hydra/backend/src/hydra_api/db_schema.py`

Dependencias:
- TASK-DB-010

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
- `cd hydra/backend && uv run python -c "from hydra_api.db_schema import SCHEMA_STATEMENTS; sql='\\n'.join(SCHEMA_STATEMENTS); assert 'CREATE TABLE IF NOT EXISTS extractions' in sql and 'extraction_json JSONB NOT NULL' in sql and 'schema_version TEXT NOT NULL' in sql; print('extractions ok')"`

## TASK-DB-013: Definir tabla eval_cases

Estado: done
Prioridad: must

Objetivo:
Persistir casos de evaluacion offline.

Archivos permitidos:
- `hydra/backend/src/hydra_api/db_schema.py`

Dependencias:
- TASK-DB-009

Requisitos:
- Anadir `CREATE TABLE IF NOT EXISTS eval_cases`.
- Campos minimos:
  - `id TEXT PRIMARY KEY`
  - `question TEXT NOT NULL`
  - `expected_documents JSONB NOT NULL DEFAULT '[]'::jsonb`
  - `expected_topics JSONB NOT NULL DEFAULT '[]'::jsonb`
  - `expected_answer_traits JSONB NOT NULL DEFAULT '[]'::jsonb`
  - `tags JSONB NOT NULL DEFAULT '[]'::jsonb`
- No ejecutar evals en esta tarea.

Criterios de aceptacion:
- La sentencia es idempotente.
- Los campos esperados por evals estan presentes.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "from hydra_api.db_schema import SCHEMA_STATEMENTS; sql='\\n'.join(SCHEMA_STATEMENTS); assert 'CREATE TABLE IF NOT EXISTS eval_cases' in sql and 'expected_documents JSONB' in sql and 'expected_answer_traits JSONB' in sql; print('eval_cases ok')"`

## TASK-DB-014: Definir tabla eval_results

Estado: done
Prioridad: must

Objetivo:
Persistir resultados de ejecuciones de evals.

Archivos permitidos:
- `hydra/backend/src/hydra_api/db_schema.py`

Dependencias:
- TASK-DB-013

Requisitos:
- Anadir `CREATE TABLE IF NOT EXISTS eval_results`.
- Campos minimos:
  - `id TEXT PRIMARY KEY`
  - `eval_case_id TEXT NOT NULL REFERENCES eval_cases(id) ON DELETE CASCADE`
  - `trace_id TEXT`
  - `metrics_json JSONB NOT NULL`
  - `passed BOOLEAN NOT NULL DEFAULT false`
  - `created_at TIMESTAMPTZ NOT NULL DEFAULT now()`
- No llamar a Langfuse ni a modelos en esta tarea.

Criterios de aceptacion:
- La tabla referencia `eval_cases`.
- Los resultados guardan `trace_id` y metricas JSON.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "from hydra_api.db_schema import SCHEMA_STATEMENTS; sql='\\n'.join(SCHEMA_STATEMENTS); assert 'CREATE TABLE IF NOT EXISTS eval_results' in sql and 'metrics_json JSONB NOT NULL' in sql and 'trace_id TEXT' in sql; print('eval_results ok')"`

## TASK-DB-015: Definir tabla graph_projection_events

Estado: done
Prioridad: should

Objetivo:
Persistir proyecciones de grafo o estados de sincronizacion con sinks secundarios sin depender de Neo4j.

Archivos permitidos:
- `hydra/backend/src/hydra_api/db_schema.py`

Dependencias:
- TASK-DB-010

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
- No anadir driver Neo4j.
- Permitir que el MVP funcione aunque esta tabla no se use todavia.

Criterios de aceptacion:
- La tabla no introduce dependencia runtime con Neo4j.
- La proyeccion se guarda como JSONB.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "from hydra_api.db_schema import SCHEMA_STATEMENTS; sql='\\n'.join(SCHEMA_STATEMENTS); assert 'CREATE TABLE IF NOT EXISTS graph_projection_events' in sql and 'projection_json JSONB NOT NULL' in sql and 'neo4j' not in sql.lower(); print('graph events ok')"`

## TASK-DB-016: Verificar orden del schema SQL

Estado: done
Prioridad: must

Objetivo:
Evitar errores de foreign keys por orden incorrecto de sentencias.

Archivos permitidos:
- `hydra/backend/src/hydra_api/db_schema.py`

Dependencias:
- TASK-DB-010
- TASK-DB-011
- TASK-DB-012
- TASK-DB-013
- TASK-DB-014

Requisitos:
- Mantener `SCHEMA_STATEMENTS` en orden:
  1. extension vector
  2. `documents`
  3. `document_chunks`
  4. `extractions`
  5. `eval_cases`
  6. `eval_results`
  7. `graph_projection_events` si se implemento TASK-DB-015
- No conectarse a la DB.

Criterios de aceptacion:
- Las tablas referenciadas se crean antes que sus dependientes.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "from hydra_api.db_schema import SCHEMA_STATEMENTS; sql='\\n'.join(SCHEMA_STATEMENTS); assert sql.index('CREATE TABLE IF NOT EXISTS documents') < sql.index('CREATE TABLE IF NOT EXISTS document_chunks'); assert sql.index('CREATE TABLE IF NOT EXISTS documents') < sql.index('CREATE TABLE IF NOT EXISTS extractions'); assert sql.index('CREATE TABLE IF NOT EXISTS eval_cases') < sql.index('CREATE TABLE IF NOT EXISTS eval_results'); print('order ok')"`

## TASK-DB-017: Crear inicializador de schema

Estado: done
Prioridad: must

Objetivo:
Ejecutar el schema SQL idempotente contra la DB local.

Archivos permitidos:
- `hydra/backend/src/hydra_api/db.py`
- `hydra/backend/src/hydra_api/db_schema.py`

Dependencias:
- TASK-DB-008
- TASK-DB-009
- TASK-DB-016

Requisitos:
- Crear `init_db(database_url: str | None = None)`.
- Ejecutar `SCHEMA_STATEMENTS` en orden dentro de una transaccion.
- Usar `get_connection()`.
- Hacer rollback o dejar que la transaccion falle limpia si una sentencia falla.
- No ejecutar inicializacion en import time.
- No imprimir `DATABASE_URL` completa.

Criterios de aceptacion:
- `init_db` es importable y callable.
- Importar `hydra_api.db` no inicializa la DB.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "from hydra_api.db import init_db; print(callable(init_db))"`
- `cd hydra/backend && uv run python -c "import hydra_api.db; print('db import ok')"`

## TASK-DB-018: Crear CLI segura para schema DB

Estado: done
Prioridad: must

Objetivo:
Permitir inicializar o imprimir el schema desde CLI sin scripts sueltos.

Archivos permitidos:
- `hydra/backend/src/hydra_api/db.py`

Dependencias:
- TASK-DB-017

Requisitos:
- Soportar `python -m hydra_api.db --print-schema`.
- Soportar `python -m hydra_api.db --init`.
- `--print-schema` no debe conectar a la DB.
- `--init` debe llamar a `init_db()`.
- Si falta configuracion para `--init`, fallar con mensaje seguro.
- No imprimir `DATABASE_URL` completa.

Criterios de aceptacion:
- `--print-schema` muestra SQL sin requerir Postgres.
- El modulo es ejecutable con `python -m`.

Comandos de verificacion:
- `cd hydra/backend && uv run python -m hydra_api.db --print-schema`
- `cd hydra/backend && uv run python -m hydra_api.db --help`

## TASK-DB-019: Ejecutar inicializacion real de DB

Estado: done
Prioridad: must

Objetivo:
Crear el schema MVP real en PostgreSQL local.

Archivos permitidos:
- Ninguno

Dependencias:
- TASK-DB-002
- TASK-DB-003
- TASK-DB-018

Requisitos:
- Ejecutar `python -m hydra_api.db --init` con `DATABASE_URL` local.
- Ejecutar la inicializacion dos veces para probar idempotencia.
- No modificar codigo.
- No ejecutar comandos destructivos.

Criterios de aceptacion:
- Ambas inicializaciones pasan.
- No se imprime la URL con password completa.

Comandos de verificacion:
- `cd hydra/backend && DATABASE_URL=postgresql+psycopg://hydra:hydra@localhost:5432/hydra uv run python -m hydra_api.db --init`
- `cd hydra/backend && DATABASE_URL=postgresql+psycopg://hydra:hydra@localhost:5432/hydra uv run python -m hydra_api.db --init`

## TASK-DB-020: Verificar tablas en PostgreSQL

Estado: done
Prioridad: must

Objetivo:
Comprobar que el schema MVP existe realmente en la DB local.

Archivos permitidos:
- Ninguno

Dependencias:
- TASK-DB-019

Requisitos:
- Verificar existencia de todas las tablas must.
- Verificar que `document_chunks.embedding` usa pgvector.
- Verificar constraints basicas de `documents`.
- No modificar codigo.

Criterios de aceptacion:
- Existen `documents`, `document_chunks`, `extractions`, `eval_cases` y `eval_results`.
- Si TASK-DB-015 se ejecuto, existe tambien `graph_projection_events`.
- `document_chunks.embedding` aparece como `vector`.

Comandos de verificacion:
- `docker compose exec -T postgres psql -U hydra -d hydra -c "SELECT to_regclass('documents'), to_regclass('document_chunks'), to_regclass('extractions'), to_regclass('eval_cases'), to_regclass('eval_results');"`
- `docker compose exec -T postgres psql -U hydra -d hydra -c "\\d+ document_chunks"`
- `docker compose exec -T postgres psql -U hydra -d hydra -c "\\d+ documents"`

## TASK-DB-021: Documentar DATABASE_URL y comandos DB

Estado: done
Prioridad: must

Objetivo:
Documentar como levantar Postgres y configurar la URL de base de datos local.

Archivos permitidos:
- `hydra/README.md`
- `hydra/.env.example`
- `hydra/backend/.env.example`

Dependencias:
- TASK-DB-001
- TASK-DB-018

Requisitos:
- Documentar `DATABASE_URL`.
- Usar el formato canonico del SDD:
  - `postgresql+psycopg://hydra:hydra@localhost:5432/hydra`
- Explicar que `hydra:hydra` son valores locales/dev y no secretos reales.
- Documentar comandos:
  - `docker compose up -d postgres`
  - `cd backend && uv run python -m hydra_api.db --print-schema`
  - `cd backend && DATABASE_URL=postgresql+psycopg://hydra:hydra@localhost:5432/hydra uv run python -m hydra_api.db --init`
- No incluir credenciales reales.
- No documentar Neo4j como dependencia core.

Criterios de aceptacion:
- README explica como levantar Postgres y configurar `DATABASE_URL`.
- Los `.env.example` contienen valores ficticios/locales seguros.
- No aparecen claves reales ni tokens.

Comandos de verificacion:
- `git diff`
- `git diff --check`
