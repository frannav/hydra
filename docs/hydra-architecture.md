# Arquitectura de HYDRA Espana Lite

Fecha: 16 de mayo de 2026  
Documento complementario a `hydra-analysis.md`

## Decision ejecutiva

La arquitectura recomendada es:

```text
hydra/frontend/ Next.js + Tailwind
  -> hydra/backend/ FastAPI + uv
  -> LangChain / LCEL
  -> PostgreSQL + pgvector
  -> API de modelos compatible con OpenAI
  -> Langfuse Cloud
  -> Evals offline y trazas observables
```

Decisiones principales:

- **Monorepo** con `hydra/frontend/` y `hydra/backend/`, no repositorios separados.
- **uv** como gestor obligatorio para Python en el backend.
- **pnpm** como gestor obligatorio para el frontend.
- **FastAPI** como backend Python para exponer RAG, evals y consultas.
- **Next.js + Tailwind** como frontend recomendado si se puede asumir el coste de una app moderna.
- **PostgreSQL + pgvector** como base de datos RAG.
- **LangChain** para construir el RAG, orquestar chains y coordinar el LLM council.
- **Langfuse Cloud** como opcion por defecto para observabilidad, trazas, datasets y scores de evaluacion.
- **Langfuse self-hosted con Docker** como opcion secundaria si se necesita demo offline, control total de datos o evitar dependencia SaaS.
- **Sistema de evals obligatorio**, con metricas de retrieval, groundedness, extraccion estructurada y calidad de briefing.
- **Proveedor de modelos configurable** para chat y embeddings mediante API compatible con OpenAI.
- **Ontologia ligera** en YAML/JSON para normalizar categorias, no ontologia formal OWL/RDF en el MVP.
- **Gestion estricta de secretos** para evitar subir API keys a GitHub.
- **SDD manual en Markdown**, sin instalar OpenSpec por ahora.

Esta arquitectura es mas ambiciosa que usar ChromaDB + scripts sueltos, pero es defendible academicamente porque cubre RAG, evaluacion, observabilidad, persistencia y orquestacion.

## Vista de alto nivel

```text
Corpus OSINT
  -> Ingesta y limpieza
  -> Chunking
  -> Ontologia ligera
  -> Embeddings
  -> PostgreSQL + pgvector
  -> Retriever LangChain
  -> HYDRA Analyst RAG
  -> LLM council
  -> Briefing final
  -> Langfuse Cloud traces + scores
  -> Evals offline
```

## Desacoplamiento del core

El core debe permitir anadir Neo4j o subida desde frontend sin reescribir el pipeline. La regla es separar **fuentes de entrada**, **modelo canonico**, **procesamiento** y **sinks de salida**.

```text
DocumentSource
  -> RawDocument + DocumentMetadata
  -> IngestionService
  -> ChunkingService
  -> ExtractionService
  -> ValidatedExtraction
  -> Persistence sinks
      -> PostgreSQL documents/extractions
      -> pgvector chunks/embeddings
      -> JSON exports
      -> GraphProjection opcional
      -> Neo4j opcional
```

### Fuentes de entrada

La primera fuente sera un corpus local curado en `hydra/backend/data/raw/`. Si sobra tiempo, la subida desde frontend debe ser otra fuente que entregue el mismo objeto canonico:

```text
RawDocument + DocumentMetadata
```

El frontend no debe parsear documentos, generar chunks, calcular embeddings ni llamar a modelos. Solo puede enviar archivo + metadatos al backend y consultar estado/resultados.

### Modelo canonico

Las piezas centrales deben ser independientes de FastAPI, pgvector, Neo4j y frontend:

- `DocumentMetadata`
- `RawDocument`
- `DocumentChunk`
- `ValidatedExtraction`
- `GraphProjection`

Los schemas Pydantic de dominio deben poder reutilizarse desde CLI, endpoints o jobs internos. Los schemas especificos de API deben ser una capa aparte.

### Sinks de salida

PostgreSQL/pgvector es el storage principal del MVP, pero no debe ser el unico destino imaginable:

- `DocumentRepository`: documentos y metadatos.
- `ChunkRepository` / `VectorStore`: chunks y embeddings.
- `ExtractionRepository`: extracciones validadas.
- `GraphProjectionSink`: JSON primero, Neo4j si sobra tiempo.

Neo4j, si se anade, debe ser un sink secundario que consume `GraphProjection`. No debe recibir salidas LLM sin validar ni convertirse en dependencia para `/query` o `/briefing`.

## Componentes

| Capa | Decision | Motivo |
|---|---|---|
| UI | Next.js + Tailwind + pnpm | Mejor demo web y separacion clara frontend/backend |
| Backend | FastAPI + uv | Python serio, API clara y gestion reproducible |
| Orquestacion | LangChain / LCEL | RAG, retrievers, chains y callbacks |
| Vector DB | PostgreSQL + pgvector | Vectores y metadatos en una base relacional |
| Modelos | Proveedor configurable compatible con OpenAI | Chat, structured outputs y embeddings sin acoplar el MVP a una marca concreta |
| Observabilidad | Langfuse Cloud | Trazas, latencia, tokens, costes, retrieval y scores |
| Evals | Langfuse Cloud datasets + scripts propios | Evaluacion reproducible y demostrable |
| Esquemas | Pydantic | Salidas estructuradas y validacion |
| Ontologia | YAML/JSON | Control semantico sin sobreingenieria |
| LLM council | Chains multirol | Revision critica sin agentes autonomos complejos |

## Decisiones vigentes y fallbacks

El brainstorming inicial queda como documento historico. Para evitar ambiguedades durante la implementacion, estas son las decisiones vigentes:

| Area | Decision principal | Fallback permitido | No usar en MVP |
|---|---|---|---|
| Frontend | Next.js + Tailwind + pnpm | HTML/Tailwind servido por FastAPI si Next bloquea | Streamlit como UI principal |
| Backend | FastAPI + uv | FastAPI con menos endpoints | Flask, scripts sueltos como producto final |
| RAG DB | PostgreSQL + pgvector | FAISS/Chroma solo si pgvector bloquea la entrega | Neo4j como dependencia core |
| Grafo | GraphProjection JSON derivada de extracciones validadas | Neo4j como sink secundario si sobra tiempo | Neo4j como fuente de verdad del MVP |
| Ingesta | Corpus local curado | Upload desde frontend si sobra tiempo | Pipeline paralelo en frontend |
| Modelos | API de modelos compatible con OpenAI, `qwen3.6` y `qwen3-embedding` | `gemma4` como revisor o mismo `qwen3.6` para todo | Modelos locales pesados |
| Observabilidad | Langfuse Cloud | logs locales + JSON si no hay claves | Langfuse self-hosted como camino principal |
| SDD | Markdown manual en `hydra/sdd/` | checklist reducido si falta tiempo | OpenSpec en esta fase |

Un fallback solo se activa si el camino principal amenaza la entrega del MVP. Debe quedar documentado en README y en la memoria como decision de alcance.

## Monorepo y gestion de dependencias

El frontend y el backend deben convivir en el mismo repositorio. La separacion recomendada es por carpetas, no por repositorios.

```text
hydra/frontend/
  package.json
  pnpm-lock.yaml
  src/
hydra/backend/
  pyproject.toml
  uv.lock
  src/
hydra/docker-compose.yml
hydra/README.md
```

## Gestion de secretos y API keys

Las API keys no deben subirse nunca a GitHub. Esto aplica a API de modelos, Langfuse, bases de datos externas y cualquier otro proveedor.

### Reglas obligatorias

- No hardcodear API keys en codigo Python, TypeScript, notebooks, markdown, tests ni scripts.
- Usar archivos `.env` locales para secretos reales.
- Mantener `.env` en `.gitignore`.
- Versionar solo `hydra/.env.example`, `hydra/backend/.env.example` y `hydra/frontend/.env.local.example` con valores ficticios.
- Cargar configuracion desde variables de entorno en `hydra/backend/src/hydra_api/config.py`.
- Validar al arrancar que las variables obligatorias existen.
- No imprimir secretos en logs, trazas de Langfuse, errores ni respuestas de API.
- No guardar prompts, traces o payloads que contengan claves.
- Rotar inmediatamente cualquier clave que se haya pegado por error en un commit, aunque luego se borre.

### Archivos esperados

```text
.gitignore
hydra/.env.example
hydra/frontend/.env.local.example
hydra/backend/.env.example
```

`.gitignore` debe incluir:

```gitignore
.env
.env.*
!hydra/.env.example
!hydra/frontend/.env.local.example
!hydra/backend/.env.example
```

### Variables de entorno principales

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

### Medidas recomendadas

- Anadir `detect-secrets`, `gitleaks` o herramienta equivalente como pre-commit.
- Revisar `git diff` antes de cada commit.
- Evitar copiar respuestas completas de errores de proveedores si pueden contener headers.
- En documentacion, usar siempre `replace_me`, `your_key_here` o valores falsos.
- En Langfuse, usar masking si se detecta que algun campo sensible puede llegar a trazas.

### Criterio de aceptacion

Antes de subir a GitHub:

```bash
git status
git diff
```

Y comprobar que no aparecen valores reales para:

- `MODEL_API_KEY`;
- `LANGFUSE_SECRET_KEY`;
- `LANGFUSE_PUBLIC_KEY`;
- `DATABASE_URL` de produccion;
- cualquier bearer token o password real.

## Politica de corpus y datos

El detalle operativo vive en `../sdd/00-product-scope.md` y `../sdd/02-data-model.md`.

Decisiones vigentes:

- Corpus MVP: 10-20 documentos curados.
- Fuentes publicas con metadatos completos.
- Cada afirmacion del briefing debe enlazar con documento, fuente, fragmento y score si procede.
- No inferir intencion, coordinacion o atribucion geopolitica sin evidencia explicita.

## SDD manual

El detalle SDD se ha movido a `../sdd/` para mantener este documento centrado en arquitectura.

- Convencion general: `../sdd/README.md`
- Alcance de producto: `../sdd/00-product-scope.md`
- Decisiones ejecutables: `../sdd/01-architecture-decisions.md`
- Checklist atomico: `../sdd/08-task-checklist.md`
- Tareas por dominio: `../sdd/tasks/`

## Backend Python con uv

`uv` debe ser el gestor del backend. Esto aporta reproducibilidad y encaja mejor con una entrega tecnica que `pip install` suelto.

Comandos base:

```bash
cd hydra/back
uv sync
uv run fastapi dev src/hydra_api/main.py
uv run python -m hydra_api.evals
```

El backend debe exponer endpoints simples:

```text
GET  /health
GET  /documents
GET  /narratives
POST /ingest
POST /query
POST /briefing
POST /evals/run
GET  /evals/results
```

### Contrato API minimo

El contrato detallado vive en `../sdd/03-api-contract.md`.

Endpoints obligatorios:

```text
GET  /health
GET  /documents
GET  /narratives
POST /ingest
POST /documents/upload  # opcional si sobra tiempo
POST /query
POST /briefing
POST /evals/run
GET  /evals/results
```

Reglas:

- No exponer secretos, headers completos, prompts internos completos ni stack traces al frontend.
- Toda respuesta analitica debe incluir evidencias o limitaciones.
- `POST /query` y `POST /briefing` deben devolver `trace_id`.
- `POST /documents/upload`, si se implementa, debe llamar al mismo `IngestionService` que procesa el corpus local.
- El backend es el unico lugar donde se validan archivos, se guardan raw docs, se trocean documentos, se calculan embeddings y se llama a modelos.

## Frontend con pnpm

`pnpm` debe ser el gestor del frontend. Evita mezclar `npm`, `yarn` y `pnpm` en el mismo proyecto y deja el lockfile claro para la entrega.

Comandos base:

```bash
cd hydra/front
pnpm install
pnpm dev
pnpm build
```

Variables permitidas en frontend:

```bash
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

El frontend no debe contener `MODEL_API_KEY`, `LANGFUSE_SECRET_KEY`, `DATABASE_URL` ni ninguna clave privada. Las llamadas a modelos y observabilidad salen siempre desde el backend.

### Subida de documentos desde frontend

La subida desde frontend es una extension opcional, no un requisito del MVP. Si se implementa:

- el usuario sube archivo y metadatos minimos;
- el frontend llama a `POST /documents/upload`;
- el backend valida formato/metadatos;
- el backend guarda el raw document;
- el backend llama al mismo `IngestionService` que usa el corpus local;
- el frontend solo muestra `processing_status` y errores seguros.

No permitido:

- parsear PDFs o texto en frontend;
- hacer chunking en frontend;
- calcular embeddings en frontend;
- llamar a proveedores LLM desde frontend;
- crear un pipeline paralelo para documentos subidos.

## Decision de UI

### Recomendacion

La opcion recomendada es **Next.js + Tailwind** en `hydra/frontend/` y **FastAPI** en `hydra/backend/`.

Motivos:

- permite una interfaz mas seria que Streamlit;
- separa claramente producto web y pipeline IA;
- facilita pestanas, tablas, chat, evidencias, scores y trazas;
- Tailwind permite avanzar rapido sin disenar CSS desde cero;
- convive bien con un backend Python especializado en LangChain, pgvector y Langfuse Cloud.

### Comparativa

| Opcion | Ventaja | Riesgo | Decision |
|---|---|---|---|
| Next.js + Tailwind | UI moderna, buen estado cliente, demo profesional | Mas setup que Streamlit o HTML puro | Recomendada |
| Astro + Tailwind | Excelente para sitios de contenido y documentacion | Menos natural para dashboard/chat interactivo | No prioritaria |
| HTML + CSS + Tailwind + JS | Muy rapido y pocas dependencias | Peor mantenibilidad si crece la interaccion | Fallback viable |
| Streamlit | Rapidisimo para prototipo Python | Menos producto web, menos separacion frontend/backend | Descartar como principal |

Si el tiempo aprieta, el fallback correcto no es Astro: es HTML/Tailwind servido por FastAPI con JavaScript minimo.

## Modelos y proveedor

### Veredicto

El backend debe hablar con un proveedor de modelos configurable mediante una API compatible con OpenAI. Esto simplifica LangChain y clientes OpenAI-compatible sin acoplar el proyecto a una marca concreta. La URL base se define con `MODEL_API_BASE_URL`.

### Seleccion recomendada

| Uso | Modelo | Motivo |
|---|---|---|
| Chat principal / HYDRA Analyst | `qwen3.6` | Modelo principal, tool calling, reasoning y streaming |
| Extraccion estructurada | `qwen3.6` | Soporta `response_format` con JSON schema strict |
| Revisor del council | `gemma4` o `qwen3.6` | Modelo alternativo util para contraste, si funciona estable |
| Embeddings RAG | `qwen3-embedding` | Embeddings de 4096 dimensiones, orientado a busqueda semantica |
| Audio futuro | `whisper` / `kokoro` | Fuera del MVP salvo demo opcional |

### Implicaciones para pgvector

`qwen3-embedding` devuelve vectores de 4096 dimensiones, asi que pgvector debe configurarse con esa dimension.

```text
embedding_dimension = 4096
distance = cosine
```

### Configuracion

```bash
MODEL_API_KEY=...
MODEL_API_BASE_URL=https://model-provider.example/v1
HYDRA_CHAT_MODEL=qwen3.6
HYDRA_REVIEW_MODEL=gemma4
HYDRA_EMBEDDING_MODEL=qwen3-embedding
```

### Estrategia de uso

- usar `qwen3.6` para RAG y generacion final;
- usar structured outputs con JSON schema para extraccion;
- desactivar reasoning cuando se necesite menor latencia;
- usar `gemma4` como revisor si el coste/latencia lo permite;
- registrar modelo, version de prompt y parametros en Langfuse Cloud.

## PostgreSQL + pgvector

### Veredicto

Usar PostgreSQL con pgvector es una buena decision si se acepta el coste inicial de configuracion. Para un TFM queda mejor que ChromaDB porque permite explicar persistencia, metadatos, consultas relacionales y busqueda vectorial en una unica base.

pgvector permite almacenar vectores junto con el resto de datos en Postgres y soporta busqueda por similitud exacta y aproximada, ademas de varias metricas de distancia como coseno, L2 e inner product.

### Uso recomendado

Usar `langchain-postgres` con `PGVector` como wrapper de LangChain.

Decisiones concretas:

- una coleccion para chunks del corpus;
- metadatos en `JSONB`;
- distancia coseno;
- `k=4` o `k=5` para retrieval;
- ids estables por documento y chunk;
- tablas propias para documentos, extracciones, evals y trazas locales si hace falta.

### Modelo de datos minimo

```text
documents
  id
  title
  source
  url
  published_at
  domain
  raw_path

document_chunks
  id
  document_id
  chunk_index
  content
  metadata
  embedding

extractions
  id
  document_id
  extraction_json
  schema_version
  created_at

eval_cases
  id
  question
  expected_documents
  expected_topics
  expected_answer_traits
  tags

eval_results
  id
  eval_case_id
  trace_id
  metrics_json
  passed
  created_at

graph_projection_events
  id
  document_id
  projection_json
  schema_version
  sink_status
  created_at
```

Si LangChain crea sus propias tablas para `PGVector`, no pasa nada. Las tablas propias pueden convivir para el resto de la aplicacion.

### Preparacion para grafo y Neo4j

El MVP no necesita Neo4j para responder preguntas. Aun asi, las extracciones deben permitir generar una `GraphProjection` desacoplada:

```text
ValidatedExtraction
  -> GraphProjection JSON
  -> JSON export
  -> Neo4j sink opcional
```

Nodos iniciales:

- `Document`
- `Actor`
- `NarrativeFrame`
- `Location`
- `Event`
- `Sector`
- `ThreatType`

Relaciones iniciales:

- `MENTIONS`
- `HAS_NARRATIVE`
- `OCCURS_IN`
- `AFFECTS`
- `SUPPORTED_BY`

Reglas:

- cada relacion analitica debe tener evidencias;
- no crear edges desde afirmaciones no validadas;
- Neo4j no sustituye PostgreSQL/pgvector;
- si Neo4j no esta configurado, el MVP debe seguir funcionando.

### Riesgos

| Riesgo | Mitigacion |
|---|---|
| Configuracion de Postgres consume tiempo | Usar Docker Compose |
| pgvector falla en local | Tener fallback temporal a FAISS o Chroma |
| Esquema demasiado complejo | Empezar con documentos, chunks y extracciones |
| Indices vectoriales quitan tiempo | Para 10-30 documentos, busqueda exacta basta |

## LangChain

### Veredicto

Si se va a usar pgvector y Langfuse Cloud, LangChain tiene sentido. Debe usarse como capa de orquestacion, no como caja negra.

### Usos dentro de HYDRA

- cargar chunks como `Document`;
- conectar embeddings con `PGVector`;
- exponer `retriever = vector_store.as_retriever(...)`;
- construir el RAG con LCEL;
- crear prompts reutilizables;
- invocar modelos con structured output;
- pasar callbacks de Langfuse Cloud;
- ejecutar el LLM council como secuencia de chains.

### Lo que se debe evitar

- agentes autonomos con herramientas dinamicas;
- chains muy anidadas;
- ocultar la logica de dominio dentro de prompts largos;
- depender de LangChain para validaciones que deben vivir en Pydantic.

### RAG recomendado

```text
question
  -> retriever pgvector
  -> context builder
  -> answer chain con Pydantic
  -> council review
  -> final briefing
```

### LLM council con LangChain

Se puede implementar como tres chains simples:

```text
Narrative Analyst Chain
  -> identifica narrativa, actores, eventos y riesgos

Evidence Reviewer Chain
  -> comprueba si las afirmaciones estan soportadas por evidencias

Risk Reviewer Chain
  -> revisa si el nivel de riesgo esta justificado

Final Synthesizer Chain
  -> genera briefing final con limites
```

No hace falta usar modelos distintos. Para el MVP basta con el mismo modelo y prompts de rol diferentes. El council debe ejecutarse en briefings y evals, no necesariamente en cada documento.

## Langfuse

### Veredicto

Langfuse encaja muy bien porque observabilidad y evaluacion forman parte del temario. Ademas se integra con LangChain mediante callbacks y permite ver trazas de LLM, retrievers, inputs, outputs, latencia, tokens y costes.

La decision recomendada para el MVP es **Langfuse Cloud por defecto**. Para llegar al miercoles, reduce infraestructura, evita mantener otro stack de servicios y permite centrarse en el RAG, los evals y la demo.

El modo self-hosted se mantiene como **opcion secundaria**. Langfuse se puede autohostear con Docker Compose, pero esa opcion anade mas piezas de infraestructura y, segun la propia documentacion, el despliegue Docker Compose local/VM esta orientado a pruebas o baja escala y no incluye alta disponibilidad, escalado ni backups. Para el TFM es suficiente mencionarlo y dejar la configuracion preparada mediante `LANGFUSE_BASE_URL`.

### Decision Cloud vs self-hosted

| Opcion | Ventaja | Riesgo | Decision |
|---|---|---|---|
| Langfuse Cloud | Arranque rapido, menos infraestructura, ideal para MVP | Depende de conexion y cuenta externa | Recomendada |
| Self-hosted Docker | Control de datos, demo offline, independencia de SaaS | Mas contenedores, secretos, memoria, almacenamiento y mantenimiento | Fallback / trabajo futuro |

Como el corpus del MVP es OSINT y no contiene datos privados sensibles, no hay una razon fuerte para asumir self-hosting desde el primer dia.

### Que observar

Cada consulta de HYDRA Analyst debe generar una traza con:

- pregunta del usuario;
- parametros de retrieval;
- documentos/chunks recuperados;
- scores de similitud;
- prompt final;
- respuesta del LLM;
- revision del council;
- briefing final;
- latencia;
- tokens;
- coste estimado;
- tags: `rag`, `hydra-analyst`, `migration-canarias`, `mvp`;
- version de prompt y version de esquema.

### Estructura de trazas

```text
trace: hydra_analyst_query
  span: embed_query
  span: pgvector_retrieval
  span: build_context
  generation: analyst_answer
  generation: evidence_reviewer
  generation: risk_reviewer
  generation: final_briefing
  score: faithfulness
  score: context_relevance
  score: answer_quality
```

### Variables de entorno

```bash
LANGFUSE_PUBLIC_KEY=...
LANGFUSE_SECRET_KEY=...
LANGFUSE_BASE_URL=https://cloud.langfuse.com
```

Para self-hosted local, solo deberia cambiar el `base_url`:

```bash
LANGFUSE_BASE_URL=http://localhost:3000
```

Si no hay claves de Langfuse durante la demo, el sistema debe seguir funcionando y registrar logs locales basicos. La observabilidad no debe romper la app.

## Sistema de evals

### Veredicto

Los evals deben ser obligatorios en el MVP. No tienen que ser masivos, pero si reproducibles.

### Dataset minimo

Crear entre 8 y 12 casos de evaluacion:

```json
{
  "id": "eval_001",
  "question": "Hay una narrativa de desconfianza institucional sobre la gestion migratoria en Canarias?",
  "expected_documents": ["doc_001", "doc_004"],
  "expected_topics": ["migracion", "confianza institucional"],
  "expected_answer_traits": [
    "cita evidencias",
    "distingue recurrencia de coordinacion",
    "incluye limitaciones"
  ]
}
```

### Tipos de eval

| Eval | Que mide | Metodo |
|---|---|---|
| Retrieval Precision@k | Si los documentos recuperados son relevantes | expected docs vs top-k |
| Context relevance | Si el contexto recuperado responde a la pregunta | LLM judge o rubrica manual |
| Faithfulness / groundedness | Si la respuesta esta soportada por evidencias | LLM judge + revision humana |
| JSON validity | Si la extraccion cumple esquema | Pydantic |
| Ontology mapping | Si las categorias usan IDs validos | validacion contra YAML/JSON |
| Risk justification | Si el riesgo bajo/medio/alto esta justificado | LLM council |
| Coordination caution | Si evita afirmar coordinacion sin evidencia | regla + LLM judge |
| Latency/cost | Si el flujo es viable para demo | Langfuse trace |

### Niveles de evaluacion

1. **Unit evals**
   - validacion de esquemas;
   - normalizacion ontologica;
   - chunking;
   - carga en pgvector.

2. **Retrieval evals**
   - Precision@3;
   - Precision@5;
   - documentos esperados recuperados;
   - inspeccion de chunks.

3. **Generation evals**
   - respuesta cita evidencias;
   - no inventa fuentes;
   - incluye limitaciones;
   - distingue recurrencia y coordinacion.

4. **Council evals**
   - porcentaje de briefings aprobados;
   - numero de claims no soportados;
   - desacuerdo entre analista y revisor.

### Donde guardar resultados

Guardar los resultados en dos sitios:

- Langfuse Cloud, como scores asociados a trazas o dataset runs.
- `hydra/backend/data/outputs/eval_results.json` para tener backup local y reproducible.

## Arquitectura de carpetas

```text
hydra/frontend/
  package.json
  pnpm-lock.yaml
  src/
    app/
    components/
    lib/
hydra/backend/
  pyproject.toml
  uv.lock
  data/
    raw/
    processed/
    outputs/
      eval_results.json
      graph_projection.json
    evals/
      eval_cases.json
  ontology/
    hydra_ontology.yaml
  src/
    hydra_api/
      main.py
      config.py
      db.py
      ingest.py
      chunking.py
      ontology.py
      schemas.py
      extract.py
      embeddings.py
      retrieval.py
      rag.py
      council.py
      briefing.py
      evals.py
      observability.py
      graph_projection.py      # opcional
      graph_sinks.py           # opcional si Neo4j entra
hydra/docker-compose.yml
hydra/README.md
```

## Plan de implementacion

### Fase 1: Base tecnica

- Crear `hydra/frontend/` y `hydra/backend/` dentro del mismo repo.
- Inicializar backend con `uv`.
- Inicializar frontend con `pnpm`.
- Docker Compose con Postgres + pgvector.
- Conexion desde Python.
- Tablas minimas o wrapper `PGVector`.
- Servicio de ingesta desacoplado de la fuente de documentos.
- Ontologia ligera.
- Esquemas Pydantic.
- Cliente de modelos compatible con OpenAI.

### Fase 2: RAG con LangChain

- Ingesta de documentos.
- Chunking.
- Embeddings con `qwen3-embedding`.
- Carga en pgvector.
- Retriever.
- Chain de respuesta con evidencias usando `qwen3.6`.
- Extraccion canonica reutilizable por RAG, briefing y proyeccion de grafo.

### Fase 3: Observabilidad

- Integrar Langfuse Cloud callback handler.
- Trazar retrieval, LLM calls y council.
- Anadir tags, metadata y prompt versions.
- Guardar trace IDs junto a resultados.

### Fase 4: Evals

- Crear `eval_cases.json`.
- Ejecutar evals offline.
- Calcular metricas.
- Enviar scores a Langfuse Cloud.
- Exportar `eval_results.json`.

### Fase 5: Demo

- Next.js con vistas Corpus, Narrativas, HYDRA Analyst, Briefing y Evals.
- Mostrar trazabilidad: documentos, evidencias, scores y trace id.

## Priorizacion

### Obligatorio

- Backend Python con `uv`.
- Frontend con `pnpm`.
- Monorepo con `hydra/frontend/` y `hydra/backend/`.
- FastAPI funcional.
- Frontend web minimo.
- PostgreSQL + pgvector funcional.
- LangChain RAG basico.
- Langfuse Cloud tracing.
- Dataset minimo de evals.
- Scores basicos de evaluacion.
- Pydantic + ontologia ligera.
- chat + embeddings configurados mediante API de modelos.

### Importante

- Next.js + Tailwind si el tiempo lo permite.
- LLM council para briefing.
- Vista de evals en el frontend.
- Exportacion local de resultados.

### Opcional

- HTML/Tailwind servido por FastAPI si Next se atasca.
- Subida de documentos desde frontend usando el mismo pipeline backend.
- GraphProjection JSON desde extracciones validadas.
- Neo4j como sink secundario de GraphProjection.
- Langfuse self-hosted con Docker Compose.
- Grafo visual.
- LangGraph.
- Ontologia OWL/RDF.
- Evals automaticos avanzados con framework externo.

## Definition of Done del MVP

El detalle vive en `../sdd/07-implementation-plan.md`. En resumen, el MVP esta terminado cuando backend, frontend, pgvector, RAG, evals, observabilidad, corpus, secretos y README funcionan de extremo a extremo.

## Recomendacion final

La combinacion propuesta es buena:

- uv da reproducibilidad al backend Python;
- frontend/backend en el mismo repo mantiene una arquitectura clara sin fragmentar el proyecto;
- Next.js + Tailwind mejora la demo si el tiempo lo permite;
- pgvector da solidez de datos;
- LangChain simplifica RAG e integracion con pgvector/Langfuse Cloud;
- Langfuse Cloud cubre observabilidad y parte de evaluacion con el minimo coste operativo;
- la API de modelos permite chat, structured outputs y embeddings mediante un contrato compatible con OpenAI;
- los evals propios dan rigor academico;
- el LLM council se puede implementar como chains multirol sin disparar complejidad.

El punto critico es no convertir LangChain en un sistema de agentes autonomos. Para el MVP, debe ser una orquestacion explicita y trazable.

## Referencias consultadas

- [Langfuse Observability](https://langfuse.com/docs/observability/overview)
- [Langfuse LangChain integration](https://langfuse.com/integrations/frameworks/langchain)
- [Langfuse Datasets](https://langfuse.com/docs/evaluation/experiments/datasets)
- [pgvector](https://github.com/pgvector/pgvector)
- [LangChain PGVector](https://api.python.langchain.com/en/latest/postgres/vectorstores/langchain_postgres.vectorstores.PGVector.html)
- [NaN Models](https://nan.builders/docs/models)
- [NaN API](https://nan.builders/docs/api)
