# Droid Mission Brief — 02 Database

Mission:
Implementar el bloque `02-database` de HYDRA como una Mission larga pero estrictamente acotada al SDD, para que luego Codex y el usuario puedan revisar el diff completo con calma.

Objective:
Completar `TASK-DB-001` a `TASK-DB-021` respetando prioridades, dependencias, alcance de archivos y comandos de verificación definidos en `hydra/sdd/tasks/02-database/02-database.md`.

Source of truth:
- `hydra/sdd/README.md`
- `hydra/sdd/01-architecture-decisions.md`
- `hydra/sdd/02-data-model.md`
- `hydra/sdd/rag-pipeline.md`
- `hydra/sdd/07-implementation-plan.md`
- `hydra/sdd/08-task-checklist.md`
- `hydra/sdd/09-droid-execution-workflow.md`
- `hydra/sdd/tasks/02-database/02-database.md`

Mission mode:
- Esto es una Mission de ejecucion, no de arquitectura.
- No decidas alternativas tecnologicas.
- Si el SDD y la realidad local entran en conflicto, para y reporta.

Non-negotiable decisions:
- Backend Python con `uv`.
- Base de datos MVP: PostgreSQL + pgvector.
- Sin ORM.
- Sin SQLAlchemy.
- Sin Alembic.
- Sin Neo4j como dependencia core.
- Sin parsing, chunking, embeddings ni llamadas a modelos en tareas DB.
- No tocar frontend.
- No crear ni editar `.env` reales.
- No imprimir `DATABASE_URL` completa si contiene credenciales.
- No ejecutar operaciones destructivas como `DROP TABLE`, `DROP DATABASE` o `docker compose down -v`.
- No marcar tareas SDD como `done` ni editar estados en `hydra/sdd/tasks/02-database/02-database.md`.

Allowed files:
- `hydra/docker-compose.yml`
- `hydra/backend/pyproject.toml`
- `hydra/backend/uv.lock`
- `hydra/backend/src/hydra_api/db.py`
- `hydra/backend/src/hydra_api/db_schema.py`
- `hydra/README.md`
- `hydra/.env.example`
- `hydra/backend/.env.example`

Forbidden files and areas:
- `hydra/frontend/**`
- `hydra/sdd/**` excepto este mission brief como referencia; no modificar tareas ni estados
- `hydra/docs/**`
- cualquier `.env` real
- cualquier archivo no listado en `Allowed files`

Execution rules:
- Ejecuta las tareas en orden.
- Respeta dependencias antes de avanzar.
- Si una tarea requiere solo comandos y no cambios de archivos, no modifiques codigo.
- Si una verificacion falla, corrige solo dentro del alcance permitido.
- Si necesitas tocar otro archivo, para y explica por que.
- No hagas commits ni limpiezas destructivas.

Expected prerequisites before starting:
- `TASK-BACK-001` a `TASK-BACK-008` ya estan completadas o revisadas.
- El repo esta en la raiz `hydra/`.
- Docker local existe; si Docker no esta disponible, detener la Mission al llegar a las tareas runtime de Compose.

Milestone 1 — Infraestructura Postgres viva
Tasks:
- `TASK-DB-001`
- `TASK-DB-002`
- `TASK-DB-003`
- `TASK-DB-004`

Goal:
- Dejar `hydra/docker-compose.yml` listo y comprobar que PostgreSQL + pgvector arrancan bien de forma local e idempotente.

Milestone checks:
- `docker compose config`
- `docker compose up -d postgres`
- `docker compose ps`
- `docker compose exec -T postgres psql -U hydra -d hydra -c "SELECT current_database(), current_user;"`
- `docker compose exec -T postgres psql -U hydra -d hydra -c "CREATE EXTENSION IF NOT EXISTS vector;"`
- `docker compose exec -T postgres psql -U hydra -d hydra -c "SELECT extname FROM pg_extension WHERE extname = 'vector';"`
- `docker compose exec -T postgres psql -U hydra -d hydra -c "CREATE EXTENSION IF NOT EXISTS vector; CREATE EXTENSION IF NOT EXISTS vector;"`

Stop immediately if:
- Docker no arranca.
- La imagen no incluye pgvector.
- Necesitas cambiar la arquitectura de storage.
- Para que funcione necesitas añadir otros servicios.

Milestone 2 — Dependencia y helper DB seguro
Tasks:
- `TASK-DB-005`
- `TASK-DB-006`
- `TASK-DB-007`
- `TASK-DB-008`

Goal:
- Añadir `psycopg[binary]` y preparar un helper DB seguro, lazy y sin fugas de credenciales.

Milestone checks:
- `cd hydra/backend && uv sync`
- `cd hydra/backend && uv run python -c "import psycopg; print(psycopg.__name__)"`
- `cd hydra/backend && uv run python -c "import pathlib; text=pathlib.Path('pyproject.toml').read_text().lower(); assert 'sqlalchemy' not in text and 'alembic' not in text; print('no orm')"`
- `cd hydra/backend && uv run python -c "from hydra_api.db import normalize_database_url; assert normalize_database_url('postgresql+psycopg://hydra:hydra@localhost:5432/hydra') == 'postgresql://hydra:hydra@localhost:5432/hydra'; print('canonical ok')"`
- `cd hydra/backend && uv run python -c "from hydra_api.db import normalize_database_url; assert normalize_database_url('postgresql://u:p@localhost:5432/db?sslmode=disable') == 'postgresql://u:p@localhost:5432/db?sslmode=disable'; print('plain ok')"`
- `cd hydra/backend && uv run python -c "from hydra_api.db import redact_database_url; out = redact_database_url('postgresql+psycopg://hydra:secret_password@localhost:5432/hydra'); print(out); assert 'secret_password' not in out"`
- `cd hydra/backend && uv run python -c "from hydra_api.db import redact_database_url; out = redact_database_url('postgresql://localhost:5432/hydra'); print(out); assert 'localhost' in out"`
- `cd hydra/backend && uv run python -c "from hydra_api.db import get_connection; print(callable(get_connection))"`
- `cd hydra/backend && uv run python -c "import hydra_api.db; print('import ok')"`

Stop immediately if:
- Vas a introducir ORM, Alembic o migraciones fuera del SDD.
- El modulo conecta a la DB en import time.
- Se imprime la URL completa con password.

Milestone 3 — Schema SQL MVP idempotente
Tasks:
- `TASK-DB-009`
- `TASK-DB-010`
- `TASK-DB-011`
- `TASK-DB-012`
- `TASK-DB-013`
- `TASK-DB-014`
- `TASK-DB-015` solo si no introduce deriva y sigue siendo de bajo riesgo
- `TASK-DB-016`

Goal:
- Centralizar el schema SQL idempotente del MVP, una tabla por tarea, con orden correcto y sin acoplar frontend, Neo4j ni modelos.

Milestone checks:
- `cd hydra/backend && uv run python -c "from hydra_api.db_schema import SCHEMA_VERSION, SCHEMA_STATEMENTS; print(SCHEMA_VERSION, isinstance(SCHEMA_STATEMENTS, list), len(SCHEMA_STATEMENTS))"`
- `cd hydra/backend && uv run python -c "from hydra_api.db_schema import SCHEMA_STATEMENTS; assert 'CREATE EXTENSION IF NOT EXISTS vector' in SCHEMA_STATEMENTS[0]; print('extension first')"`
- `cd hydra/backend && uv run python -c "from hydra_api.db_schema import SCHEMA_STATEMENTS; sql='\\n'.join(SCHEMA_STATEMENTS); assert 'CREATE TABLE IF NOT EXISTS documents' in sql and 'content_hash TEXT NOT NULL UNIQUE' in sql and 'local_corpus' in sql and 'frontend_upload' in sql; print('documents ok')"`
- `cd hydra/backend && uv run python -c "from hydra_api.db_schema import SCHEMA_STATEMENTS; sql='\\n'.join(SCHEMA_STATEMENTS); assert 'CREATE TABLE IF NOT EXISTS document_chunks' in sql and 'REFERENCES documents(id) ON DELETE CASCADE' in sql and 'vector(4096)' in sql; print('chunks ok')"`
- `cd hydra/backend && uv run python -c "from hydra_api.db_schema import SCHEMA_STATEMENTS; sql='\\n'.join(SCHEMA_STATEMENTS); assert 'CREATE TABLE IF NOT EXISTS extractions' in sql and 'extraction_json JSONB NOT NULL' in sql and 'schema_version TEXT NOT NULL' in sql; print('extractions ok')"`
- `cd hydra/backend && uv run python -c "from hydra_api.db_schema import SCHEMA_STATEMENTS; sql='\\n'.join(SCHEMA_STATEMENTS); assert 'CREATE TABLE IF NOT EXISTS eval_cases' in sql and 'expected_documents JSONB' in sql and 'expected_answer_traits JSONB' in sql; print('eval_cases ok')"`
- `cd hydra/backend && uv run python -c "from hydra_api.db_schema import SCHEMA_STATEMENTS; sql='\\n'.join(SCHEMA_STATEMENTS); assert 'CREATE TABLE IF NOT EXISTS eval_results' in sql and 'metrics_json JSONB NOT NULL' in sql and 'trace_id TEXT' in sql; print('eval_results ok')"`
- `cd hydra/backend && uv run python -c "from hydra_api.db_schema import SCHEMA_STATEMENTS; sql='\\n'.join(SCHEMA_STATEMENTS); assert sql.index('CREATE TABLE IF NOT EXISTS documents') < sql.index('CREATE TABLE IF NOT EXISTS document_chunks'); assert sql.index('CREATE TABLE IF NOT EXISTS documents') < sql.index('CREATE TABLE IF NOT EXISTS extractions'); assert sql.index('CREATE TABLE IF NOT EXISTS eval_cases') < sql.index('CREATE TABLE IF NOT EXISTS eval_results'); print('order ok')"`

Additional conditional check if `TASK-DB-015` is implemented:
- `cd hydra/backend && uv run python -c "from hydra_api.db_schema import SCHEMA_STATEMENTS; sql='\\n'.join(SCHEMA_STATEMENTS); assert 'CREATE TABLE IF NOT EXISTS graph_projection_events' in sql and 'projection_json JSONB NOT NULL' in sql and 'neo4j' not in sql.lower(); print('graph events ok')"`

Stop immediately if:
- Cambias la dimension `4096`.
- Mezclas responsabilidades de corpus, RAG o frontend.
- Introduces dependencia runtime con Neo4j.
- Rompes el orden de foreign keys.

Milestone 4 — Inicializacion real e idempotencia de schema
Tasks:
- `TASK-DB-017`
- `TASK-DB-018`
- `TASK-DB-019`
- `TASK-DB-020`

Goal:
- Crear inicializador y CLI seguros, ejecutar el schema real dos veces y validar que las tablas existen de verdad en PostgreSQL.

Milestone checks:
- `cd hydra/backend && uv run python -c "from hydra_api.db import init_db; print(callable(init_db))"`
- `cd hydra/backend && uv run python -c "import hydra_api.db; print('db import ok')"`
- `cd hydra/backend && uv run python -m hydra_api.db --print-schema`
- `cd hydra/backend && uv run python -m hydra_api.db --help`
- `cd hydra/backend && DATABASE_URL=postgresql+psycopg://hydra:hydra@localhost:5432/hydra uv run python -m hydra_api.db --init`
- `cd hydra/backend && DATABASE_URL=postgresql+psycopg://hydra:hydra@localhost:5432/hydra uv run python -m hydra_api.db --init`
- `docker compose exec -T postgres psql -U hydra -d hydra -c "SELECT to_regclass('documents'), to_regclass('document_chunks'), to_regclass('extractions'), to_regclass('eval_cases'), to_regclass('eval_results');"`
- `docker compose exec -T postgres psql -U hydra -d hydra -c "\\d+ document_chunks"`
- `docker compose exec -T postgres psql -U hydra -d hydra -c "\\d+ documents"`

Stop immediately if:
- `--print-schema` conecta a la DB.
- `--init` no es idempotente.
- Se muestra la URL completa con password.
- Hace falta borrar datos o recrear volúmenes para pasar.

Milestone 5 — Documentacion minima de uso local
Tasks:
- `TASK-DB-021`

Goal:
- Dejar documentado el arranque local de Postgres y el uso de `DATABASE_URL` canonica sin meter secretos.

Milestone checks:
- `git diff`
- `git diff --check`

Documentation requirements:
- Explicar `DATABASE_URL=postgresql+psycopg://hydra:hydra@localhost:5432/hydra`.
- Aclarar que `hydra:hydra` son valores locales/dev.
- Documentar:
  - `docker compose up -d postgres`
  - `cd backend && uv run python -m hydra_api.db --print-schema`
  - `cd backend && DATABASE_URL=postgresql+psycopg://hydra:hydra@localhost:5432/hydra uv run python -m hydra_api.db --init`

Stop immediately if:
- Vas a tocar docs fuera del alcance permitido.
- Vas a introducir credenciales reales.

Validation after each milestone:
- Revisar que solo cambian archivos permitidos.
- Ejecutar todos los comandos de verificacion de ese milestone.
- Confirmar que no hay secretos reales.
- Confirmar que no aparecen dependencias prohibidas.
- Confirmar que no se tocaron `hydra/frontend/`, `hydra/docs/` ni tareas SDD.

Final report back:
- Lista exacta de archivos modificados.
- Lista exacta de comandos ejecutados.
- Resultado de cada verificacion, agrupado por milestone.
- Si `TASK-DB-015` se implemento o se salto, y por que.
- Riesgos, bloqueos o follow-ups detectados.
- Confirmacion explicita de que no se editaron `.env` reales ni archivos fuera de alcance.

Review handoff:
- Deja el diff listo para revision humana.
- No cierres la Mission afirmando que el dominio esta aceptado; eso lo decide Codex + usuario tras revisar diff y comandos.
