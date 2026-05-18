# HYDRA

Plataforma experimental de análisis documental que combina extracción estructurada, búsqueda semántica, generación de briefings y evaluación reproducible sobre un corpus cerrado de fuentes públicas.

## Objetivo

Prueba funcional de concepto para un TFM de IA. El MVP busca demostrar cómo un sistema basado en IA generativa, recuperación semántica y evaluación reproducible puede ayudar a explorar narrativas en documentos públicos.

## Alcance del MVP

- corpus cerrado de 10-20 documentos;
- metadatos completos por documento;
- extracción estructurada validada con Pydantic;
- ontología ligera;
- RAG sobre PostgreSQL + pgvector;
- endpoints FastAPI para consultas, briefing y evals;
- frontend analítico mínimo;
- trazabilidad con Langfuse Cloud o logs locales;
- evals reproducibles;
- respuestas con evidencias y limitaciones.

Fuera de alcance para el MVP:

- scraping masivo;
- ingesta en tiempo real;
- redes sociales;
- detección de bots;
- atribución geopolítica;
- autenticación;
- Neo4j;
- fine-tuning.

## Stack previsto

- Backend: Python, `uv`, FastAPI, Pydantic.
- Frontend: Next.js, TypeScript, Tailwind, `pnpm`.
- RAG: LangChain / LCEL, PostgreSQL + pgvector.
- Modelos: Qwen 3.6 + Gemma 4.
- Observabilidad: Langfuse Cloud.
- Evals: Langfuse Cloud.
- Ontología: YAML/JSON.
- Spec-driven development

## Estructura del repositorio

Este repositorio Git está inicializado dentro de la carpeta `hydra/`. Por eso, desde este README las rutas son relativas a esta raíz:

```text
docs/                 Documentación estable del proyecto
sdd/                  Especificación ejecutable y tareas atómicas
backend/                 Backend FastAPI previsto
frontend/                Frontend previsto
docker-compose.yml    PostgreSQL + pgvector previsto
```

## Documentación principal

- `docs/hydra-analysis.md`: análisis ejecutivo, alcance y riesgos.
- `docs/hydra-architecture.md`: arquitectura vigente y decisiones técnicas.
- `docs/hydra-brainstorming.md`: material histórico de ideación.
- `sdd/README.md`: convención de trabajo Specification-Driven Development.
- `sdd/03-api-contract.md`: contrato API mínimo.
- `sdd/07-implementation-plan.md`: fases de implementación.
- `sdd/09-droid-execution-workflow.md`: workflow Codex planner/reviewer -> Droid executor.

## Workflow de implementación

El flujo de trabajo previsto es:

1. Definir el bloque funcional a implementar.
2. Revisar el SDD como fuente de verdad.
3. Dividir el trabajo en tareas atómicas.
4. Crear un Task Packet o Mission Brief para Droid.
5. Ejecutar Droid solo sobre archivos permitidos.
6. Revisar diff, comandos, secretos y criterios de aceptación.
7. Integrar o crear una repair task si algo falla.

Orden recomendado:

```text
1. Repo y seguridad
2. Backend base
3. Database
4. Corpus
5. Ontología y extracción
6. RAG
7. Observabilidad
8. Evals
9. Briefing / council
10. Frontend
11. Documentación y demo
```

## Base de datos (PostgreSQL + pgvector)

### Arranque

HYDRA usa PostgreSQL con la extensión pgvector para almacenamiento vectorial.
El contenedor se inicia con:

```bash
docker compose up -d postgres
```

Verificar que el contenedor está en marcha:

```bash
docker compose ps
```

### DATABASE_URL

La variable `DATABASE_URL` define la cadena de conexión a PostgreSQL.
El formato canónico es:

```
postgresql+psycopg://<usuario>:<contraseña>@<host>:<puerto>/<base_de_datos>
```

Ejemplo para desarrollo local:

```
DATABASE_URL=postgresql+psycopg://hydra:hydra@localhost:5432/hydra
```

> `hydra:hydra` son valores locales/dev, no secretos reales.

El backend normaliza automáticamente el prefijo `postgresql+psycopg://` a `postgresql://`.

### CLI de inicialización

Inicializa el esquema de base de datos (tablas y extensiones):

```bash
cd backend && DATABASE_URL=postgresql+psycopg://hydra:hydra@localhost:5432/hydra uv run python -m hydra_api.db --init
```

Imprime las sentencias SQL sin conectar a la base de datos:

```bash
cd backend && uv run python -m hydra_api.db --print-schema
```

Ambas operaciones son idempotentes: pueden ejecutarse repetidamente sin error.

## Ontología y extracción (sin corpus real)

Estos comandos validan la ontología y los fixtures de extracción
sin ejecutar modelos ni conectar a una base de datos.

Validar la ontología YAML:

```bash
cd backend && uv run python -m hydra_api.ontology --validate ontology/hydra_ontology.yaml
```

Validar un fixture de extracción (Pydantic + ontología) y exportar:

```bash
cd backend && uv run python -m hydra_api.extraction --validate-json data/fixtures/extraction_valid_minimal.json --ontology ontology/hydra_ontology.yaml --export-dir /tmp/hydra_extraction_cli
```

> **no ejecuta modelos**: estos comandos solo validan la estructura
> de la ontología y los fixtures sintéticos. La extracción real
> requiere un corpus aprobado y claves de modelo configuradas.

## Corpus

HYDRA usa un corpus cerrado de documentos públicos. La ingesta se basa en un archivo de manifiesto:

- `backend/data/metadata/local_corpus.manifest.template.json` — plantilla del manifiesto del corpus local.
- `backend/data/metadata/metadata_template.json` — plantilla de metadatos por documento.
- `backend/data/metadata/corpus_candidates.template.csv` — lista de candidatos a incluir en el corpus.

Los documentos reales se agregan manualmente tras aprobación del usuario. No se deben versionar documentos reales en el repositorio.

Para más detalles, ver `backend/data/README.md`.

## Seguridad y secretos

Reglas obligatorias:

- no subir API keys al repositorio;
- no hardcodear secretos en código, Markdown, tests ni scripts;
- usar `.env` locales para secretos reales;
- versionar solo archivos `.env.example` con valores ficticios;
- no exponer secretos en logs, errores, trazas ni respuestas API.

Variables previstas para backend:

```bash
MODEL_API_KEY=replace_me
MODEL_API_BASE_URL=https://model-provider.example/v1
HYDRA_CHAT_MODEL=qwen3.6
HYDRA_REVIEW_MODEL=gemma4
HYDRA_EMBEDDING_MODEL=qwen3-embedding

LANGFUSE_PUBLIC_KEY=replace_me
LANGFUSE_SECRET_KEY=replace_me
LANGFUSE_BASE_URL=https://cloud.langfuse.com

DATABASE_URL=postgresql+psycopg://hydra:hydra@localhost:5432/hydra
```

Variable pública prevista para frontend:

```bash
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```