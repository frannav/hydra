# 07 - Implementation Plan

## Fases

### Fase 1: Base tecnica

- Monorepo `hydra/frontend/` y `hydra/backend/`.
- Backend con `uv`.
- Frontend con `pnpm`.
- Docker Compose con Postgres + pgvector.
- Configuracion y secretos.
- Cliente de modelos.
- Servicio de ingesta desacoplado de la fuente de documentos.

### Fase 2: Corpus y extraccion

- Corpus curado.
- Metadatos.
- Ontologia ligera.
- Pydantic schemas.
- Extraccion de prueba.
- Extraccion canonica validada reutilizable por storage, RAG, briefing y grafo futuro.

### Fase 3: RAG

- Chunking.
- Embeddings.
- Carga en pgvector.
- Retriever.
- `/query`.

### Fase 4: Observabilidad y evals

- Langfuse Cloud.
- Evals offline.
- Scores.
- Export JSON.

### Fase 5: Demo

- Frontend.
- Briefing.
- Evidencias.
- README.
- Guion de demo.

### Fase 6: Extensiones opcionales si sobra tiempo

- Subida de documentos desde frontend usando el mismo pipeline backend.
- GraphProjection JSON desde extracciones validadas.
- Neo4j como sink secundario, no como dependencia core.

## Definition of Done

- `hydra/backend/` arranca con `uv`.
- `hydra/frontend/` arranca con `pnpm`.
- PostgreSQL + pgvector arranca con Docker Compose.
- Hay 10-20 documentos con metadatos completos.
- Los chunks se insertan en pgvector con embeddings de 4096 dimensiones.
- La ingesta puede ejecutarse desde corpus local y queda preparada para upload sin pipeline paralelo.
- Las extracciones validadas no dependen de pgvector, Neo4j ni frontend.
- `POST /query` devuelve respuesta, evidencias, documentos recuperados y `trace_id`.
- `POST /briefing` devuelve briefing con limitaciones.
- Hay al menos 8 casos en `hydra/backend/data/evals/eval_cases.json`.
- Los evals exportan `hydra/backend/data/outputs/eval_results.json`.
- Las consultas principales se trazan en Langfuse Cloud o logs locales.
- `.env` no esta versionado y los `.env.example` no contienen secretos.
- La demo puede ejecutarse siguiendo el README.
