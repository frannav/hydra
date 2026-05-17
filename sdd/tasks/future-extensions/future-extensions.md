# Tasks - Extensiones futuras

Estas tareas no pertenecen al MVP obligatorio. Solo deben ejecutarse cuando backend, RAG, evals y demo basica funcionen.

## TASK-GRAPH-001: Exportar GraphProjection a JSON

Estado: pending  
Prioridad: could

Dependencias:
- `TASK-EXT-005`

Objetivo: exportar proyecciones de grafo derivadas de extracciones validadas.

Archivos permitidos:
- `hydra/backend/src/hydra_api/graph_projection.py`
- `hydra/backend/data/outputs/graph_projection.json`

Criterios de aceptacion:
- El JSON incluye nodos, edges y evidencias.
- No contiene relaciones sin evidencia.
- No depende de Neo4j.

## TASK-GRAPH-002: Sink Neo4j opcional

Estado: pending  
Prioridad: could

Dependencias:
- `TASK-GRAPH-001`

Objetivo: cargar `GraphProjection` en Neo4j como persistencia secundaria.

Archivos permitidos:
- `hydra/backend/src/hydra_api/graph_sinks.py`
- `hydra/backend/.env.example`
- `hydra/docker-compose.yml`

Requisitos:
- Neo4j no sustituye PostgreSQL/pgvector.
- Neo4j no es necesario para `POST /query` ni `POST /briefing`.
- Solo consumir `GraphProjection` validada.
- No escribir texto libre ni salidas LLM sin validar.
- Usar variables ficticias en `.env.example`.

Criterios de aceptacion:
- Si Neo4j no esta configurado, el MVP sigue funcionando.
- La carga a Neo4j puede desactivarse por configuracion.

## TASK-UPLOAD-001: Endpoint opcional de subida

Estado: pending  
Prioridad: could

Dependencias:
- `TASK-CORPUS-008`

Objetivo: crear `POST /documents/upload` como entrada alternativa al mismo pipeline de ingesta.

Archivos permitidos:
- `hydra/backend/src/hydra_api/main.py`
- `hydra/backend/src/hydra_api/ingest.py`
- `hydra/backend/src/hydra_api/schemas.py`

Requisitos:
- Aceptar archivo + metadatos minimos.
- Soportar inicialmente `.txt`, `.md` o `.csv`.
- Rechazar archivos sin metadatos completos.
- Guardar en `hydra/backend/data/raw/` o almacenamiento local equivalente.
- Llamar al mismo servicio de ingesta que usa el corpus local.
- No ejecutar parsing ni modelos en frontend.

Criterios de aceptacion:
- Un documento subido entra al mismo flujo que un documento del corpus local.
- La respuesta devuelve `document_id` y `processing_status`.

## TASK-UPLOAD-002: Vista opcional de subida

Estado: pending  
Prioridad: could

Dependencias:
- `TASK-UPLOAD-001`

Objetivo: crear una UI minima para subir documentos y metadatos.

Archivos permitidos:
- `hydra/frontend/**`

Requisitos:
- No contener secretos.
- No llamar a proveedores LLM.
- No parsear documentos en frontend.
- Mostrar errores seguros y estado de procesamiento.
