# 02 - Data Model

## Metadatos minimos

```json
{
  "document_id": "doc_001",
  "title": "Titulo",
  "source": "Fuente",
  "source_type": "medio | institucion | informe | comunicado | otro",
  "url": "https://...",
  "published_at": "2026-05-15",
  "collected_at": "2026-05-16",
  "domain": "migracion_canarias",
  "language": "es",
  "ingestion_source": "local_corpus | frontend_upload",
  "raw_path": "hydra/backend/data/raw/doc_001.txt",
  "content_hash": "sha256...",
  "notes": "Motivo de inclusion"
}
```

## Tablas minimas

```text
documents
  id
  title
  source
  url
  published_at
  domain
  raw_path
  content_hash
  ingestion_source
  processing_status

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

graph_projection_events
  id
  document_id
  projection_json
  schema_version
  sink_status
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
```

## Embeddings

- Modelo: `qwen3-embedding`.
- Dimension: `4096`.
- Distancia: coseno.

## Esquema de extraccion

Campos minimos:

- `document_id`
- `title`
- `source`
- `date`
- `main_topic`
- `main_narrative`
- `narrative_frame_id`
- `secondary_narratives`
- `actors`
- `actor_types`
- `locations`
- `events`
- `affected_sectors`
- `threat_types`
- `risk_level`
- `confidence`
- `evidence_fragments`
- `analyst_summary`
- `limitations`

## Proyeccion de grafo

La proyeccion de grafo es un artefacto derivado de una extraccion validada. No sustituye a `extraction_json` y no debe depender de Neo4j.

Campos minimos:

- `document_id`
- `nodes`
- `edges`
- `evidence_refs`
- `schema_version`

Tipos de nodos permitidos inicialmente:

- `Document`
- `Actor`
- `NarrativeFrame`
- `Location`
- `Event`
- `Sector`
- `ThreatType`

Tipos de relaciones permitidas inicialmente:

- `MENTIONS`
- `HAS_NARRATIVE`
- `OCCURS_IN`
- `AFFECTS`
- `SUPPORTED_BY`

Reglas:

- Cada edge analitica debe incluir `evidence_refs`.
- La proyeccion se genera desde Pydantic validado, no desde texto libre.
- Neo4j, si se incorpora, debe consumir esta proyeccion como sink secundario.
