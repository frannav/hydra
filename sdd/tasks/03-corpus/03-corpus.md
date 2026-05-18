# Tasks - Corpus e ingesta

## Reglas de atomizacion

- Ejecutar estas tareas en orden.
- Cada tarea debe ser verificable por comandos concretos.
- No tocar frontend.
- No crear ni modificar `.env` reales.
- No descargar, scrapear, buscar ni inventar documentos reales en esta fase.
- No versionar documentos reales hasta que el usuario apruebe el corpus.
- No llamar a modelos, embeddings, Langfuse ni proveedores externos.
- No hacer extraccion estructurada en tareas de corpus.
- No introducir Neo4j ni drivers de grafo.
- No crear pipelines paralelos para `frontend_upload`; solo dejar interfaces preparadas.
- No introducir dependencias nuevas salvo que una tarea lo indique explicitamente.
- No ejecutar borrados destructivos ni truncar tablas.
- No imprimir rutas con secretos ni contenido completo de documentos en logs.
- Mantener `local_corpus` como primera fuente soportada.
- El frontend no parsea, no limpia, no trocea y no ingiere documentos.
- No marcar tareas como `done` hasta que Codex/reviewer revise diff, comandos y secretos.

## Contexto importante

El usuario todavia no tiene los documentos reales del corpus. Por eso estas tareas preparan:

- estructura de carpetas;
- plantillas de metadatos;
- validadores;
- loader local;
- chunking determinista;
- servicio de ingesta desacoplado;
- CLI de dry-run.

Las tareas que requieren documentos reales quedan bloqueadas hasta una fase posterior de busqueda y seleccion asistida.

## Lecciones incorporadas antes de la mission corpus

- No pedir a Droid "elige el corpus"; la seleccion de fuentes publicas es una decision humana/reviewer.
- Separar plantillas, validacion, lectura de archivos, chunking, persistencia y documentacion.
- Permitir verificaciones con manifest vacio o fixtures pequenos, nunca con documentos inventados como si fueran corpus real.
- El corpus debe producir `RawDocument + DocumentMetadata` antes de limpieza, chunking o extraccion.
- La ingesta debe poder llamarse desde CLI, endpoint futuro o tests sin depender de frontend.

## Milestones sugeridos para Droid Missions

| Milestone | Tareas | Objetivo | Debe parar para review |
|---|---|---|---|
| 1 | TASK-CORPUS-001 a TASK-CORPUS-005 | Estructura local y plantillas sin documentos reales | Si intenta buscar/descargar/inventar documentos |
| 2 | TASK-CORPUS-006 a TASK-CORPUS-013 | Schemas canonicos y helpers puros | Si acopla schemas a DB, pgvector, frontend o modelos |
| 3 | TASK-CORPUS-014 a TASK-CORPUS-017 | Loader local con manifest vacio o controlado | Si el loader depende de una carpeta hardcodeada |
| 4 | TASK-CORPUS-018 a TASK-CORPUS-020 | Chunking determinista sin embeddings | Si calcula embeddings o llama modelos |
| 5 | TASK-CORPUS-021 a TASK-CORPUS-027 | Servicio/CLI de ingesta desacoplado y documentado | Si imprime documentos completos o requiere datos reales |
| 6 | TASK-CORPUS-028 a TASK-CORPUS-031 | Corpus real futuro | Bloqueado hasta que existan documentos aprobados |

## TASK-CORPUS-001: Crear estructura local de corpus

Estado: done
Prioridad: must

Objetivo:
Crear la estructura minima de carpetas para corpus local sin anadir documentos reales.

Archivos permitidos:
- `hydra/backend/data/raw/.gitkeep`
- `hydra/backend/data/metadata/.gitkeep`
- `hydra/backend/data/fixtures/.gitkeep`

Dependencias:
- TASK-DB-021

Requisitos:
- Crear carpetas si no existen.
- Usar `.gitkeep` para versionar carpetas vacias.
- No anadir documentos reales.
- No anadir metadatos reales.

Criterios de aceptacion:
- Las carpetas existen.
- No hay archivos de documentos reales.

Comandos de verificacion:
- `test -d hydra/backend/data/raw && test -d hydra/backend/data/metadata && test -d hydra/backend/data/fixtures`
- `find hydra/backend/data/raw -type f ! -name ".gitkeep"`
- `git status --short`

## TASK-CORPUS-002: Crear plantilla de metadatos

Estado: done
Prioridad: must

Objetivo:
Definir una plantilla JSON editable para metadatos minimos de documentos.

Archivos permitidos:
- `hydra/backend/data/metadata/metadata_template.json`

Dependencias:
- TASK-CORPUS-001

Requisitos:
- Incluir todos los campos de `sdd/02-data-model.md`:
  - `document_id`
  - `title`
  - `source`
  - `source_type`
  - `url`
  - `published_at`
  - `collected_at`
  - `domain`
  - `language`
  - `ingestion_source`
  - `raw_path`
  - `content_hash`
  - `notes`
- Usar valores placeholder claramente ficticios.
- Usar `ingestion_source="local_corpus"`.
- No incluir URLs reales todavia.

Criterios de aceptacion:
- El JSON es valido.
- La plantilla no se confunde con un documento real.

Comandos de verificacion:
- `cd hydra/backend && uv run python -m json.tool data/metadata/metadata_template.json >/tmp/hydra_metadata_template.json`
- `cd hydra/backend && uv run python -c "import json; data=json.load(open('data/metadata/metadata_template.json')); required={'document_id','title','source','source_type','url','published_at','collected_at','domain','language','ingestion_source','raw_path','content_hash','notes'}; assert required <= set(data); assert data['ingestion_source']=='local_corpus'; print('metadata template ok')"`

## TASK-CORPUS-003: Crear plantilla de candidatos de corpus

Estado: done
Prioridad: must

Objetivo:
Crear un archivo plantilla para que luego Codex/usuario registren candidatos de documentos y decisiones de inclusion/descarte.

Archivos permitidos:
- `hydra/backend/data/metadata/corpus_candidates.template.csv`

Dependencias:
- TASK-CORPUS-001

Requisitos:
- Crear solo cabeceras y una fila placeholder claramente ficticia o comentada.
- Columnas minimas:
  - `candidate_id`
  - `title`
  - `source`
  - `source_type`
  - `url`
  - `published_at`
  - `domain`
  - `language`
  - `include_decision`
  - `reason`
  - `notes`
- No buscar documentos reales.
- No anadir URLs reales.

Criterios de aceptacion:
- El CSV tiene cabeceras esperadas.
- No contiene decisiones reales de corpus.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "import csv; rows=list(csv.DictReader(open('data/metadata/corpus_candidates.template.csv'))); required={'candidate_id','title','source','source_type','url','published_at','domain','language','include_decision','reason','notes'}; assert required <= set(rows[0].keys()); print('candidate template ok')"`

## TASK-CORPUS-004: Crear plantilla de manifest local

Estado: done
Prioridad: must

Objetivo:
Definir el formato que usara el loader local para relacionar archivos raw y metadatos.

Archivos permitidos:
- `hydra/backend/data/metadata/local_corpus.manifest.template.json`

Dependencias:
- TASK-CORPUS-002

Requisitos:
- El manifest debe tener:
  - `corpus_id`
  - `domain`
  - `documents`
- `documents` debe ser una lista vacia en la plantilla.
- No incluir documentos reales.
- No requerir que el manifest real exista todavia.

Criterios de aceptacion:
- El JSON es valido.
- El manifest vacio puede cargarse sin error por tareas futuras.

Comandos de verificacion:
- `cd hydra/backend && uv run python -m json.tool data/metadata/local_corpus.manifest.template.json >/tmp/hydra_manifest_template.json`
- `cd hydra/backend && uv run python -c "import json; data=json.load(open('data/metadata/local_corpus.manifest.template.json')); assert isinstance(data.get('documents'), list) and data['documents']==[]; print('manifest template ok')"`

## TASK-CORPUS-005: Documentar reglas locales del corpus

Estado: done
Prioridad: must

Objetivo:
Documentar como se deben colocar documentos y metadatos locales sin introducir documentos reales.

Archivos permitidos:
- `hydra/backend/data/README.md`

Dependencias:
- TASK-CORPUS-001
- TASK-CORPUS-002
- TASK-CORPUS-004

Requisitos:
- Explicar que `raw/` contendra documentos aprobados en una fase posterior.
- Explicar que `metadata/` contendra templates, manifest y metadatos.
- Explicar que no se deben versionar secretos ni datos sensibles.
- Explicar que no se deben anadir documentos reales hasta que el usuario apruebe el corpus.
- Incluir el limite objetivo de 10-20 documentos para la fase futura.

Criterios de aceptacion:
- La documentacion no promete que el corpus real ya existe.
- No hay URLs reales ni documentos inventados.

Comandos de verificacion:
- `grep -n "10-20" hydra/backend/data/README.md`
- `grep -n "no se deben anadir documentos reales" hydra/backend/data/README.md`

## TASK-CORPUS-006: Anadir schema RawDocument

Estado: done
Prioridad: must

Objetivo:
Representar documentos raw de forma canonica antes de limpieza, chunking o extraccion.

Archivos permitidos:
- `hydra/backend/src/hydra_api/schemas.py`

Dependencias:
- TASK-BACK-010

Requisitos:
- Crear `RawDocument`.
- Campos minimos:
  - `document_id: str`
  - `text: str`
  - `metadata: DocumentMetadata`
- No incluir embeddings.
- No incluir campos de extraccion analitica.
- No acoplar a DB, pgvector, frontend ni Neo4j.

Criterios de aceptacion:
- `RawDocument` importa desde `hydra_api.schemas`.
- Puede instanciarse con `DocumentMetadata`.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "from hydra_api.schemas import DocumentMetadata, RawDocument; doc=RawDocument(document_id='doc_test', text='texto', metadata=DocumentMetadata(title='T', source='S', domain='test')); assert doc.document_id=='doc_test'; print('raw document ok')"`

## TASK-CORPUS-007: Anadir schema IngestedDocument

Estado: done
Prioridad: must

Objetivo:
Representar el resultado normalizado de un documento antes de persistirlo.

Archivos permitidos:
- `hydra/backend/src/hydra_api/schemas.py`

Dependencias:
- TASK-CORPUS-006

Requisitos:
- Crear `IngestedDocument`.
- Campos minimos:
  - `document_id`
  - `metadata`
  - `content_hash`
  - `raw_path`
  - `text`
- No incluir chunks todavia.
- No incluir embeddings ni extracciones.

Criterios de aceptacion:
- `IngestedDocument` importa sin tocar DB.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "from hydra_api.schemas import IngestedDocument; print(IngestedDocument.__name__)"`

## TASK-CORPUS-008: Crear modulo de ingesta sin efectos en import

Estado: done
Prioridad: must

Objetivo:
Crear el modulo base de ingesta sin leer archivos, conectar a DB ni llamar servicios al importarlo.

Archivos permitidos:
- `hydra/backend/src/hydra_api/ingest.py`

Dependencias:
- TASK-CORPUS-006

Requisitos:
- Crear `hydra_api.ingest`.
- Importar solo librerias estandar y schemas necesarios.
- No abrir archivos en import time.
- No conectar a DB en import time.
- No llamar modelos.

Criterios de aceptacion:
- El modulo importa sin efectos externos.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "import hydra_api.ingest; print('ingest import ok')"`

## TASK-CORPUS-009: Crear normalizador de fechas simple

Estado: done
Prioridad: must

Objetivo:
Normalizar fechas de metadatos sin introducir dependencias externas.

Archivos permitidos:
- `hydra/backend/src/hydra_api/ingest.py`

Dependencias:
- TASK-CORPUS-008

Requisitos:
- Crear `normalize_date(value: str | None) -> str | None`.
- Aceptar `None`.
- Aceptar `YYYY-MM-DD`.
- Rechazar formatos ambiguos con `ValueError`.
- No usar `dateutil` ni dependencias nuevas.

Criterios de aceptacion:
- La funcion es determinista.
- No modifica zonas horarias ni interpreta formatos ambiguos.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "from hydra_api.ingest import normalize_date; assert normalize_date(None) is None; assert normalize_date('2026-05-15')=='2026-05-15'; print('date normalize ok')"`
- `cd hydra/backend && ! uv run python -c "from hydra_api.ingest import normalize_date; normalize_date('15/05/2026')" && echo "ambiguous date rejected"`

## TASK-CORPUS-010: Crear normalizador de fuente

Estado: done
Prioridad: must

Objetivo:
Normalizar nombres de fuentes sin cambiar su significado.

Archivos permitidos:
- `hydra/backend/src/hydra_api/ingest.py`

Dependencias:
- TASK-CORPUS-008

Requisitos:
- Crear `normalize_source(value: str) -> str`.
- Hacer `strip`.
- Colapsar espacios repetidos.
- Rechazar string vacio.
- No traducir ni reescribir nombres de medios/instituciones.

Criterios de aceptacion:
- Mantiene la fuente legible.
- Rechaza valores vacios.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "from hydra_api.ingest import normalize_source; assert normalize_source('  Fuente   Publica  ')=='Fuente Publica'; print('source normalize ok')"`
- `cd hydra/backend && ! uv run python -c "from hydra_api.ingest import normalize_source; normalize_source('   ')" && echo "empty source rejected"`

## TASK-CORPUS-011: Crear helper de hash de contenido

Estado: done
Prioridad: must

Objetivo:
Calcular hashes reproducibles para detectar duplicados sin persistir contenido duplicado.

Archivos permitidos:
- `hydra/backend/src/hydra_api/ingest.py`

Dependencias:
- TASK-CORPUS-008

Requisitos:
- Crear `compute_content_hash(text: str) -> str`.
- Usar SHA-256.
- Normalizar saltos de linea a `\n`.
- Rechazar texto vacio o solo espacios.
- No imprimir contenido completo.

Criterios de aceptacion:
- El mismo texto produce el mismo hash.
- Texto vacio falla de forma clara.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "from hydra_api.ingest import compute_content_hash; a=compute_content_hash('hola\\r\\n'); b=compute_content_hash('hola\\n'); assert a==b and len(a)==64; print('hash ok')"`
- `cd hydra/backend && ! uv run python -c "from hydra_api.ingest import compute_content_hash; compute_content_hash('   ')" && echo "empty content rejected"`

## TASK-CORPUS-012: Crear resolver seguro de rutas de corpus

Estado: done
Prioridad: must

Objetivo:
Evitar path traversal al cargar documentos locales desde manifests.

Archivos permitidos:
- `hydra/backend/src/hydra_api/ingest.py`

Dependencias:
- TASK-CORPUS-008

Requisitos:
- Crear `resolve_corpus_path(root: Path, relative_path: str) -> Path`.
- Rechazar rutas absolutas.
- Rechazar `..` que salga de `root`.
- Devolver path resuelto dentro de `root`.
- No leer el archivo en esta funcion.

Criterios de aceptacion:
- Rutas validas quedan bajo `root`.
- Path traversal falla.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "from pathlib import Path; from hydra_api.ingest import resolve_corpus_path; p=resolve_corpus_path(Path('data'), 'raw/doc.txt'); assert str(p).endswith('data/raw/doc.txt'); print('safe path ok')"`
- `cd hydra/backend && ! uv run python -c "from pathlib import Path; from hydra_api.ingest import resolve_corpus_path; resolve_corpus_path(Path('data'), '../secret.txt')" && echo "path traversal rejected"`

## TASK-CORPUS-013: Crear validador de metadatos

Estado: done
Prioridad: must

Objetivo:
Validar metadatos antes de cargar o procesar documentos.

Archivos permitidos:
- `hydra/backend/src/hydra_api/ingest.py`

Dependencias:
- TASK-CORPUS-006
- TASK-CORPUS-009
- TASK-CORPUS-010

Requisitos:
- Crear `validate_metadata_dict(data: dict) -> DocumentMetadata`.
- Usar `DocumentMetadata`.
- Normalizar `published_at` y `collected_at`.
- Normalizar `source`.
- Requerir `title`, `source` y `domain`.
- Rechazar `ingestion_source` distinto de `local_corpus` en esta fase.

Criterios de aceptacion:
- Metadatos validos producen `DocumentMetadata`.
- Falta de campos requeridos falla.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "from hydra_api.ingest import validate_metadata_dict; m=validate_metadata_dict({'title':'T','source':' Fuente ','domain':'d','ingestion_source':'local_corpus'}); assert m.source=='Fuente'; print('metadata validate ok')"`
- `cd hydra/backend && ! uv run python -c "from hydra_api.ingest import validate_metadata_dict; validate_metadata_dict({'title':'T','source':'S','domain':'d','ingestion_source':'frontend_upload'})" && echo "frontend_upload rejected for local loader"`

## TASK-CORPUS-014: Cargar archivo de metadatos JSON

Estado: done
Prioridad: must

Objetivo:
Leer un archivo JSON de metadatos y validarlo.

Archivos permitidos:
- `hydra/backend/src/hydra_api/ingest.py`

Dependencias:
- TASK-CORPUS-013

Requisitos:
- Crear `load_metadata_file(path: Path) -> DocumentMetadata`.
- Leer UTF-8.
- Usar `validate_metadata_dict`.
- No leer documento raw.
- No conectar a DB.

Criterios de aceptacion:
- Puede cargar `metadata_template.json`.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "from pathlib import Path; from hydra_api.ingest import load_metadata_file; m=load_metadata_file(Path('data/metadata/metadata_template.json')); assert m.ingestion_source.value=='local_corpus'; print('metadata file ok')"`

## TASK-CORPUS-015: Cargar texto raw local

Estado: done
Prioridad: must

Objetivo:
Leer documentos `.txt` o `.md` locales de forma controlada.

Archivos permitidos:
- `hydra/backend/src/hydra_api/ingest.py`

Dependencias:
- TASK-CORPUS-012

Requisitos:
- Crear `load_raw_text(path: Path) -> str`.
- Soportar solo `.txt` y `.md`.
- Leer UTF-8.
- Rechazar contenido vacio.
- No parsear PDF, HTML ni CSV en esta tarea.

Criterios de aceptacion:
- Archivo `.txt` valido se carga.
- Extension no permitida falla.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "from pathlib import Path; p=Path('/tmp/hydra_raw_test.txt'); p.write_text('texto', encoding='utf-8'); from hydra_api.ingest import load_raw_text; assert load_raw_text(p)=='texto'; print('raw text ok')"`
- `cd hydra/backend && ! uv run python -c "from pathlib import Path; p=Path('/tmp/hydra_raw_test.pdf'); p.write_text('x', encoding='utf-8'); from hydra_api.ingest import load_raw_text; load_raw_text(p)" && echo "unsupported extension rejected"`

## TASK-CORPUS-016: Construir RawDocument desde archivos locales

Estado: done
Prioridad: must

Objetivo:
Combinar texto raw y metadatos validados en el objeto canonico `RawDocument`.

Archivos permitidos:
- `hydra/backend/src/hydra_api/ingest.py`

Dependencias:
- TASK-CORPUS-006
- TASK-CORPUS-011
- TASK-CORPUS-014
- TASK-CORPUS-015

Requisitos:
- Crear `load_local_document(raw_path: Path, metadata_path: Path) -> RawDocument`.
- Calcular `content_hash` si falta en metadatos.
- Usar `document_id` de metadata si existe.
- Si no existe `document_id`, fallar con mensaje claro.
- No persistir en DB.

Criterios de aceptacion:
- Devuelve `RawDocument`.
- No requiere documentos reales del corpus.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "from pathlib import Path; import json, tempfile; from hydra_api.ingest import load_local_document; d=Path(tempfile.mkdtemp()); raw=d/'doc.txt'; meta=d/'meta.json'; raw.write_text('texto prueba', encoding='utf-8'); meta.write_text(json.dumps({'document_id':'doc_test','title':'T','source':'S','domain':'d','ingestion_source':'local_corpus'}), encoding='utf-8'); doc=load_local_document(raw, meta); assert doc.document_id=='doc_test' and doc.metadata.content_hash; print('local document ok')"`

## TASK-CORPUS-017: Cargar manifest local vacio o controlado

Estado: done
Prioridad: must

Objetivo:
Permitir que la ingesta local lea un manifest sin requerir documentos reales.

Archivos permitidos:
- `hydra/backend/src/hydra_api/ingest.py`

Dependencias:
- TASK-CORPUS-004
- TASK-CORPUS-016

Requisitos:
- Crear `load_local_corpus_manifest(path: Path) -> list[RawDocument]`.
- Aceptar manifest con `documents: []` y devolver lista vacia.
- Para cada entrada futura, usar `raw_path` y `metadata_path` relativos al root del backend/data.
- Rechazar rutas inseguras.
- No crear documentos.

Criterios de aceptacion:
- La plantilla vacia carga sin error.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "from pathlib import Path; from hydra_api.ingest import load_local_corpus_manifest; docs=load_local_corpus_manifest(Path('data/metadata/local_corpus.manifest.template.json')); assert docs==[]; print('empty manifest ok')"`

## TASK-CORPUS-018: Crear modulo de chunking sin efectos en import

Estado: done
Prioridad: must

Objetivo:
Crear un modulo aislado para chunking determinista sin embeddings.

Archivos permitidos:
- `hydra/backend/src/hydra_api/chunking.py`

Dependencias:
- TASK-CORPUS-006

Requisitos:
- Crear `hydra_api.chunking`.
- No importar clientes de modelos.
- No conectar a DB.
- No calcular embeddings.

Criterios de aceptacion:
- El modulo importa sin efectos externos.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "import hydra_api.chunking; print('chunking import ok')"`

## TASK-CORPUS-019: Crear chunking determinista por caracteres

Estado: done
Prioridad: must

Objetivo:
Trocear texto de forma reproducible y simple.

Archivos permitidos:
- `hydra/backend/src/hydra_api/chunking.py`

Dependencias:
- TASK-CORPUS-018

Requisitos:
- Crear `chunk_text(text: str, chunk_size: int = 1200, overlap: int = 150) -> list[str]`.
- Rechazar `chunk_size <= 0`.
- Rechazar `overlap < 0`.
- Rechazar `overlap >= chunk_size`.
- No partir si el texto cabe en un chunk.
- Preservar orden.
- No calcular embeddings.

Criterios de aceptacion:
- El resultado es determinista.
- Textos cortos producen un solo chunk.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "from hydra_api.chunking import chunk_text; assert chunk_text('hola', chunk_size=10, overlap=2)==['hola']; a=chunk_text('abcdef', chunk_size=4, overlap=1); assert a==['abcd','def']; print('chunk text ok')"`
- `cd hydra/backend && ! uv run python -c "from hydra_api.chunking import chunk_text; chunk_text('abc', chunk_size=3, overlap=3)" && echo "bad overlap rejected"`

## TASK-CORPUS-020: Crear chunks con metadatos preservados

Estado: done
Prioridad: must

Objetivo:
Convertir `RawDocument` en `DocumentChunk` conservando trazabilidad.

Archivos permitidos:
- `hydra/backend/src/hydra_api/chunking.py`

Dependencias:
- TASK-CORPUS-006
- TASK-CORPUS-019

Requisitos:
- Crear `chunk_raw_document(raw_document: RawDocument, chunk_size: int = 1200, overlap: int = 150) -> list[DocumentChunk]`.
- IDs de chunks deterministas con formato `document_id_chunk_000`.
- Cada chunk conserva en `metadata`:
  - `document_id`
  - `title`
  - `source`
  - `url`
  - `published_at`
  - `domain`
  - `chunk_index`
- No incluir embeddings.

Criterios de aceptacion:
- Cada chunk conserva document_id, titulo, fuente y URL.
- No hay campos analiticos.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "from hydra_api.schemas import DocumentMetadata, RawDocument; from hydra_api.chunking import chunk_raw_document; doc=RawDocument(document_id='doc_001', text='abcdef', metadata=DocumentMetadata(title='Titulo', source='Fuente', url='https://example.invalid', domain='d')); chunks=chunk_raw_document(doc, chunk_size=4, overlap=1); assert chunks[0].id=='doc_001_chunk_000'; assert chunks[0].metadata['title']=='Titulo'; assert chunks[0].metadata['source']=='Fuente'; print('chunk metadata ok')"`

## TASK-CORPUS-021: Crear resultado interno de ingesta

Estado: done
Prioridad: must

Objetivo:
Representar el resultado detallado de una ingesta sin depender de FastAPI.

Archivos permitidos:
- `hydra/backend/src/hydra_api/schemas.py`

Dependencias:
- TASK-CORPUS-020

Requisitos:
- Crear `IngestionRunResult`.
- Campos minimos:
  - `processed_documents: int`
  - `created_chunks: int`
  - `errors: list[str]`
  - `dry_run: bool`
- No incluir contenido completo de documentos en errores.

Criterios de aceptacion:
- El schema importa y puede instanciarse.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "from hydra_api.schemas import IngestionRunResult; r=IngestionRunResult(processed_documents=0, created_chunks=0, errors=[], dry_run=True); assert r.dry_run is True; print('ingestion result ok')"`

## TASK-CORPUS-022: Crear servicio de ingesta dry-run

Estado: done
Prioridad: must

Objetivo:
Procesar documentos raw a chunks sin persistir ni llamar modelos.

Archivos permitidos:
- `hydra/backend/src/hydra_api/ingest.py`

Dependencias:
- TASK-CORPUS-017
- TASK-CORPUS-020
- TASK-CORPUS-021

Requisitos:
- Crear `IngestionService`.
- Crear metodo `process_documents(documents: list[RawDocument], dry_run: bool = True) -> IngestionRunResult`.
- En `dry_run=True`, solo contar documentos y chunks.
- No persistir en DB en esta tarea.
- No llamar modelos.
- Capturar errores por documento sin abortar todo el lote.
- No incluir texto completo en errores.

Criterios de aceptacion:
- Puede procesar lista vacia.
- Puede procesar un `RawDocument` sintetico en memoria.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "from hydra_api.ingest import IngestionService; service=IngestionService(); result=service.process_documents([], dry_run=True); assert result.processed_documents==0 and result.created_chunks==0; print('empty ingest ok')"`
- `cd hydra/backend && uv run python -c "from hydra_api.schemas import DocumentMetadata, RawDocument; from hydra_api.ingest import IngestionService; doc=RawDocument(document_id='doc_001', text='abcdef', metadata=DocumentMetadata(title='T', source='S', domain='d')); r=IngestionService().process_documents([doc], dry_run=True); assert r.processed_documents==1 and r.created_chunks>=1; print('dry ingest ok')"`

## TASK-CORPUS-023: Crear persistencia de documento en PostgreSQL

Estado: done
Prioridad: must

Objetivo:
Persistir metadatos de documento en la tabla `documents` sin embeddings ni extracciones.

Archivos permitidos:
- `hydra/backend/src/hydra_api/ingest.py`

Dependencias:
- TASK-DB-020
- TASK-CORPUS-016

Requisitos:
- Crear `upsert_document(conn, raw_document: RawDocument) -> None`.
- Usar SQL parametrizado.
- Insertar/actualizar solo campos de `documents`.
- Usar `processing_status='pending'` o mantener valor existente si ya existe.
- No insertar chunks en esta tarea.
- No abrir conexion en import time.

Criterios de aceptacion:
- La funcion es importable.
- No contiene SQL construido con f-strings de valores de usuario.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "from hydra_api.ingest import upsert_document; print(callable(upsert_document))"`
- `cd hydra/backend && uv run python -c "import inspect; from hydra_api import ingest; src=inspect.getsource(ingest.upsert_document); assert '%s' in src or '%(' in src; print('document sql parameterized check')"`

## TASK-CORPUS-024: Crear persistencia de chunks en PostgreSQL

Estado: done
Prioridad: must

Objetivo:
Persistir chunks sin embeddings en la tabla `document_chunks`.

Archivos permitidos:
- `hydra/backend/src/hydra_api/ingest.py`

Dependencias:
- TASK-DB-020
- TASK-CORPUS-020
- TASK-CORPUS-023

Requisitos:
- Crear `upsert_chunks(conn, chunks: list[DocumentChunk]) -> None`.
- Usar SQL parametrizado.
- Guardar `metadata` como JSON serializable.
- Dejar `embedding` como `NULL`.
- No calcular embeddings.
- No borrar chunks fuera del documento procesado.

Criterios de aceptacion:
- La funcion es importable.
- No requiere DB en import time.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "from hydra_api.ingest import upsert_chunks; print(callable(upsert_chunks))"`

## TASK-CORPUS-025: Conectar servicio de ingesta con persistencia opcional

Estado: done
Prioridad: must

Objetivo:
Permitir que el servicio persista documentos/chunks cuando `dry_run=False`.

Archivos permitidos:
- `hydra/backend/src/hydra_api/ingest.py`

Dependencias:
- TASK-CORPUS-022
- TASK-CORPUS-023
- TASK-CORPUS-024

Requisitos:
- Extender `IngestionService`.
- Si `dry_run=True`, no abrir conexion.
- Si `dry_run=False`, usar `get_connection()` de `hydra_api.db`.
- Ejecutar persistencia de documento y chunks en transaccion.
- Rollback limpio si falla un documento.
- No imprimir `DATABASE_URL`.
- No llamar modelos.

Criterios de aceptacion:
- `dry_run=True` sigue funcionando sin DB.
- Importar `hydra_api.ingest` no conecta a DB.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "import hydra_api.ingest; print('ingest import ok')"`
- `cd hydra/backend && uv run python -c "from hydra_api.ingest import IngestionService; r=IngestionService().process_documents([], dry_run=True); assert r.dry_run is True; print('dry run no db ok')"`

## TASK-CORPUS-026: Crear CLI de ingesta local segura

Estado: done
Prioridad: must

Objetivo:
Permitir ejecutar dry-runs de ingesta local sin scripts sueltos.

Archivos permitidos:
- `hydra/backend/src/hydra_api/ingest.py`

Dependencias:
- TASK-CORPUS-017
- TASK-CORPUS-025

Requisitos:
- Soportar `python -m hydra_api.ingest --manifest data/metadata/local_corpus.manifest.template.json --dry-run`.
- Soportar `--init-db` no; la DB se inicializa con `hydra_api.db`.
- `--dry-run` no debe abrir conexion DB.
- Sin `--dry-run`, permitir persistencia usando `DATABASE_URL` via `get_connection()`.
- No imprimir contenido completo de documentos.

Criterios de aceptacion:
- El CLI funciona con manifest vacio y `--dry-run`.
- `--help` funciona.

Comandos de verificacion:
- `cd hydra/backend && uv run python -m hydra_api.ingest --help`
- `cd hydra/backend && uv run python -m hydra_api.ingest --manifest data/metadata/local_corpus.manifest.template.json --dry-run`

## TASK-CORPUS-027: Documentar comandos de ingesta local

Estado: done
Prioridad: must

Objetivo:
Documentar el flujo local de corpus preparado, dejando claro que los documentos reales vendran despues.

Archivos permitidos:
- `hydra/README.md`
- `hydra/backend/data/README.md`

Dependencias:
- TASK-CORPUS-026

Requisitos:
- Documentar estructura:
  - `backend/data/raw/`
  - `backend/data/metadata/`
- Documentar dry-run:
  - `cd backend && uv run python -m hydra_api.ingest --manifest data/metadata/local_corpus.manifest.template.json --dry-run`
- Aclarar que el manifest plantilla esta vacio.
- Aclarar que Codex/usuario seleccionaran documentos reales despues.
- No anadir URLs reales.

Criterios de aceptacion:
- README no afirma que existen 10-20 documentos todavia.
- No hay documentos reales inventados.

Comandos de verificacion:
- `grep -n "local_corpus.manifest.template.json" hydra/README.md hydra/backend/data/README.md`
- `git diff --check`

## TASK-CORPUS-028: Crear lista real de candidatos

Estado: blocked
Prioridad: must

Bloqueo:
El usuario aun no tiene documentos. Codex ayudara a buscarlos y evaluarlos en una fase posterior.

Objetivo:
Crear una lista real de candidatos de corpus a partir de fuentes publicas aprobadas.

Archivos permitidos:
- `hydra/backend/data/metadata/corpus_candidates.csv`

Dependencias:
- TASK-CORPUS-003

Requisitos:
- Usar solo fuentes publicas.
- Registrar motivo de inclusion/descarte.
- No descargar contenido completo sin confirmacion.
- No incluir fuentes dudosas sin marcar limitaciones.

Criterios de aceptacion:
- Hay candidatos suficientes para elegir 10-20 documentos.
- Cada candidato tiene fuente, URL, fecha, dominio y motivo.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "import csv; rows=list(csv.DictReader(open('data/metadata/corpus_candidates.csv'))); assert len(rows)>=10; print('candidate list has rows')"`

## TASK-CORPUS-029: Seleccionar corpus final aprobado

Estado: blocked
Prioridad: must

Bloqueo:
Depende de TASK-CORPUS-028 y de aprobacion humana del usuario.

Objetivo:
Seleccionar el corpus final de 10-20 documentos.

Archivos permitidos:
- `hydra/backend/data/metadata/corpus_selection.md`
- `hydra/backend/data/metadata/local_corpus.manifest.json`

Dependencias:
- TASK-CORPUS-028

Requisitos:
- Seleccionar 10-20 documentos.
- Mantener dominio unico.
- Usar fuentes publicas.
- Documentar exclusiones importantes.
- No afirmar que el corpus es representativo de todo el fenomeno; solo corpus cerrado de demo.

Criterios de aceptacion:
- El usuario aprueba la seleccion.
- Manifest real apunta a documentos y metadatos existentes.

Comandos de verificacion:
- `test -f hydra/backend/data/metadata/local_corpus.manifest.json`
- `grep -n "Limitaciones" hydra/backend/data/metadata/corpus_selection.md`

## TASK-CORPUS-030: Anadir documentos raw aprobados

Estado: blocked
Prioridad: must

Bloqueo:
Depende de corpus final aprobado.

Objetivo:
Anadir al repo los documentos raw aprobados y sus metadatos.

Archivos permitidos:
- `hydra/backend/data/raw/**`
- `hydra/backend/data/metadata/documents/**`
- `hydra/backend/data/metadata/local_corpus.manifest.json`

Dependencias:
- TASK-CORPUS-029

Requisitos:
- Solo documentos aprobados.
- Formatos `.txt` o `.md`.
- Metadatos completos por documento.
- `content_hash` correcto.
- No incluir contenido sensible ni privado.

Criterios de aceptacion:
- Hay 10-20 documentos raw.
- Todos tienen metadata completa.

Comandos de verificacion:
- `find hydra/backend/data/raw -type f \\( -name "*.txt" -o -name "*.md" \\) | wc -l`
- `cd hydra/backend && uv run python -m hydra_api.ingest --manifest data/metadata/local_corpus.manifest.json --dry-run`

## TASK-CORPUS-031: Ejecutar ingesta real del corpus aprobado

Estado: blocked
Prioridad: must

Bloqueo:
Depende de documentos reales aprobados y DB local inicializada.

Objetivo:
Persistir documentos y chunks del corpus aprobado en PostgreSQL.

Archivos permitidos:
- Ninguno

Dependencias:
- TASK-CORPUS-030
- TASK-DB-020

Requisitos:
- Ejecutar ingesta sin `--dry-run`.
- No calcular embeddings.
- No ejecutar extraccion.
- No borrar tablas.

Criterios de aceptacion:
- Documentos y chunks quedan en DB.
- `embedding` permanece `NULL`.

Comandos de verificacion:
- `cd hydra/backend && DATABASE_URL=postgresql+psycopg://hydra:hydra@localhost:5432/hydra uv run python -m hydra_api.ingest --manifest data/metadata/local_corpus.manifest.json`
- `docker compose exec -T postgres psql -U hydra -d hydra -c "SELECT count(*) FROM documents; SELECT count(*) FROM document_chunks;"`
