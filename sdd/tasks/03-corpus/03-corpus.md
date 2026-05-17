# Tasks - Corpus e ingesta

## TASK-CORPUS-001: Definir plantilla de metadatos

Estado: pending  
Prioridad: must

Archivos permitidos:
- `hydra/backend/data/metadata_template.json`

## TASK-CORPUS-002: Crear lista de candidatos

Estado: pending  
Prioridad: must

Objetivo: documentar posibles documentos y motivo de inclusion o descarte.

## TASK-CORPUS-003: Seleccionar corpus final

Estado: pending  
Prioridad: must

Criterios:
- 10-20 documentos.
- Dominio unico.
- Fuentes publicas.
- Metadatos completos.

## TASK-CORPUS-004: Crear loader de documentos raw

Estado: pending  
Prioridad: must

Archivos permitidos:
- `hydra/backend/src/hydra_api/ingest.py`

Requisitos:
- El loader debe producir `RawDocument` + `DocumentMetadata`.
- No acoplar la limpieza/chunking a una carpeta concreta.
- Preparar el diseno para soportar `local_corpus` primero y `frontend_upload` despues.

## TASK-CORPUS-005: Normalizar fechas y fuentes

Estado: pending  
Prioridad: must

## TASK-CORPUS-006: Crear chunking determinista

Estado: pending  
Prioridad: must

Archivos permitidos:
- `hydra/backend/src/hydra_api/chunking.py`

## TASK-CORPUS-007: Guardar chunks con metadatos

Estado: pending  
Prioridad: must

Criterios de aceptacion:
- Cada chunk conserva `document_id`, titulo, fuente y URL.

## TASK-CORPUS-008: Crear servicio de ingesta desacoplado

Estado: pending  
Prioridad: must

Objetivo: separar la fuente de documentos del pipeline de procesamiento.

Archivos permitidos:
- `hydra/backend/src/hydra_api/ingest.py`
- `hydra/backend/src/hydra_api/schemas.py`

Requisitos:
- Exponer una funcion o clase de servicio que acepte `RawDocument` + `DocumentMetadata`.
- Soportar `local_corpus` sin depender de frontend.
- Dejar preparado un adaptador futuro `frontend_upload` sin implementar UI todavia.
- No llamar a modelos desde el adaptador de entrada.
- No guardar nada en Neo4j ni depender de Neo4j.

Criterios de aceptacion:
- El mismo servicio puede ser llamado por CLI/script, endpoint `POST /ingest` o futuro `POST /documents/upload`.
