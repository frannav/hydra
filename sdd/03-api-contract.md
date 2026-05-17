# 03 - API Contract

## Principios

- El frontend no llama a proveedores LLM directamente.
- El frontend no parsea documentos, no genera chunks, no calcula embeddings y no ejecuta extracciones.
- Toda entrada de documentos, venga de corpus local o de upload futuro, pasa por el mismo servicio de ingesta del backend.
- Toda respuesta analitica debe incluir evidencias o limitaciones.
- Los errores no deben exponer secretos, headers ni stack traces.

## `GET /health`

Respuesta:

```json
{
  "status": "ok",
  "service": "hydra-api"
}
```

## `GET /documents`

Respuesta:

```json
{
  "documents": [
    {
      "document_id": "doc_001",
      "title": "Titulo",
      "source": "Fuente",
      "published_at": "2026-05-15",
      "processed": true
    }
  ]
}
```

## `GET /narratives`

Respuesta:

```json
{
  "narratives": [
    {
      "narrative_frame_id": "institutional_loss_of_control",
      "label": "Perdida de control institucional",
      "document_ids": ["doc_001"],
      "actors": ["Actor o institucion"],
      "risk_level": "medio",
      "confidence": "media",
      "evidence_fragments": ["Fragmento breve usado como evidencia."]
    }
  ]
}
```

## `POST /ingest`

Uso previsto: ejecucion local o de demo para procesar corpus curado. No debe hacer scraping masivo.

Request:

```json
{
  "source": "local_corpus",
  "dry_run": false
}
```

Respuesta:

```json
{
  "processed_documents": 10,
  "created_chunks": 120,
  "errors": []
}
```

## `POST /documents/upload`

Extension opcional si sobra tiempo. Permite subir documentos desde frontend, pero el procesamiento sigue ocurriendo en backend mediante el mismo pipeline de ingesta.

Formato:

- `multipart/form-data`
- campo `file`: `.txt`, `.md` o `.csv` en MVP extendido;
- campo `metadata`: JSON con metadatos minimos.

Metadata:

```json
{
  "title": "Titulo",
  "source": "Fuente",
  "source_type": "medio",
  "url": "https://...",
  "published_at": "2026-05-15",
  "domain": "migracion_canarias",
  "language": "es",
  "notes": "Motivo de inclusion"
}
```

Respuesta:

```json
{
  "document_id": "doc_021",
  "processing_status": "queued",
  "message": "Documento recibido y pendiente de ingesta."
}
```

Reglas:

- No aceptar archivos sin metadatos minimos.
- No guardar claves ni datos sensibles del usuario.
- No procesar en frontend.
- PDF queda fuera salvo que el pipeline principal ya este estable.

## `POST /query`

Request:

```json
{
  "question": "Que narrativas aparecen sobre migracion y seguridad?",
  "top_k": 5
}
```

Respuesta:

```json
{
  "answer": "Respuesta analitica con evidencias.",
  "retrieved_documents": [
    {
      "document_id": "doc_001",
      "chunk_id": "doc_001_chunk_003",
      "title": "Titulo",
      "source": "Fuente",
      "score": 0.82,
      "evidence": "Fragmento breve usado como evidencia."
    }
  ],
  "limitations": ["El analisis se basa solo en el corpus disponible."],
  "trace_id": "langfuse-trace-id-or-local-id"
}
```

## `POST /briefing`

Request:

```json
{
  "question": "Hay recurrencia narrativa sobre abandono institucional?",
  "top_k": 5,
  "use_council": true
}
```

Respuesta:

```json
{
  "briefing_markdown": "# Briefing de inteligencia narrativa\n...",
  "risk_level": "medio",
  "council_review": {
    "evidence_supported": true,
    "unsupported_claims": [],
    "risk_review": "Riesgo justificado por evidencias recuperadas."
  },
  "trace_id": "langfuse-trace-id-or-local-id"
}
```

## `POST /evals/run`

Request:

```json
{
  "case_ids": ["eval_001"],
  "top_k": 5
}
```

Respuesta:

```json
{
  "run_id": "eval_run_001",
  "total_cases": 1,
  "results_path": "hydra/backend/data/outputs/eval_results.json",
  "trace_id": "langfuse-trace-id-or-local-id"
}
```

## `GET /evals/results`

Respuesta:

```json
{
  "run_id": "eval_run_001",
  "results": [
    {
      "eval_case_id": "eval_001",
      "metrics": {
        "precision_at_k": 0.8,
        "json_validity": true,
        "groundedness": "pass"
      },
      "passed": true,
      "trace_id": "langfuse-trace-id-or-local-id"
    }
  ]
}
```

## Errores

```json
{
  "error": {
    "code": "missing_configuration",
    "message": "Mensaje seguro sin secretos",
    "details": {}
  }
}
```
