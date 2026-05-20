La ingesta en HYDRA funciona así:

  documento raw
    ↓
  metadata
    ↓
  manifest local
    ↓
  RawDocument
    ↓
  chunking determinista
    ↓
  DocumentChunk
    ↓
  persistencia opcional en PostgreSQL
    ↓
  embeddings / RAG en fase posterior

  ## 1. Dónde entran los documentos raw

  Los documentos aprobados irán en:

  backend/data/raw/

  Solo se soporta por ahora:

  .txt
  .md

  No PDF, no HTML, no scraping, no frontend.

  Cada documento debe tener metadata en JSON, por ejemplo:

  {
    "document_id": "doc_001",
    "title": "Título",
    "source": "Fuente",
    "source_type": "medio",
    "url": "https://...",
    "published_at": "2026-01-01",
    "domain": "migracion_canarias",
    "language": "es",
    "ingestion_source": "local_corpus"
  }

 ## 1.5. ¿Por qué usamos un manifest?

  El manifest existe para que HYDRA no ingiera documentos “a ciegas” solo porque están
  dentro de una carpeta.

  Es decir, no queremos que el sistema haga esto:

  backend/data/raw/
    → coger todo lo que encuentre
    → procesarlo automáticamente

  Porque eso sería peligroso y poco trazable.

  El manifest actúa como una lista explícita y aprobada de documentos que forman parte
  del corpus.

  Es como decirle al sistema:

  > “Estos son exactamente los documentos que pertenecen al corpus cerrado. Para cada
  > documento, este es su archivo raw y este es su archivo de metadatos.”

  Ejemplo:

  {
    "documents": [
      {
        "raw_path": "raw/doc_001.txt",
        "metadata_path": "metadata/documents/doc_001.json"
      }
    ]
  }

  Esto nos da varias ventajas:

  ### 1. Control humano del corpus

  Solo se ingieren documentos que han sido seleccionados y aprobados.

  Si un archivo está en raw/ pero no aparece en el manifest, HYDRA no debería
  procesarlo.

  ### 2. Trazabilidad

  Cada documento raw queda unido explícitamente a sus metadatos:

  raw/doc_001.txt
  metadata/documents/doc_001.json

  Así sabemos:

  - qué texto se procesó;
  - qué fuente tenía;
  - qué fecha;
  - qué URL;
  - qué dominio;
  - qué document_id.

  ### 3. Reproducibilidad

  Si mañana volvemos a ejecutar la ingesta con el mismo manifest, deberíamos obtener el
  mismo conjunto de documentos y chunks.

  Esto es clave para el TFM.

  ### 4. Seguridad

  Evita procesar por error:

  - archivos temporales;
  - documentos no aprobados;
  - borradores;
  - archivos privados;
  - paths peligrosos con ../.

  ### 5. Evals estables

  Los evals necesitan documentos con IDs estables:

  doc_001
  doc_002
  doc_003

  El manifest ayuda a fijar esos IDs y a mantener estable el corpus cerrado.

  ———

  En resumen:

  > El manifest es el contrato explícito del corpus. Define qué documentos entran en
  > HYDRA, dónde está su texto raw y qué metadatos los describen. Sin manifest, la
  > ingesta sería menos controlada, menos reproducible y menos defendible en el TFM.

  ## 2. Manifest

  La ingesta no recorre carpetas a ciegas. Usa un manifest:

  backend/data/metadata/local_corpus.manifest.json

  Ejemplo futuro:

  {
    "corpus_id": "corpus_migracion_canarias",
    "domain": "migracion_canarias",
    "documents": [
      {
        "raw_path": "raw/doc_001.txt",
        "metadata_path": "metadata/documents/doc_001.json"
      }
    ]
  }

  Ahora mismo solo existe la plantilla vacía:

  backend/data/metadata/local_corpus.manifest.template.json

  ## 3. Carga del documento

  El loader hace esto:

  1. Lee el manifest.
  2. Resuelve rutas de forma segura.
  3. Rechaza rutas absolutas o ...
  4. Lee el .txt o .md en UTF-8.
  5. Rechaza archivos vacíos.
  6. Lee metadata JSON.
  7. Valida campos mínimos:
      - title
      - source
      - domain
      - document_id
  8. Normaliza fechas a YYYY-MM-DD.
  9. Normaliza espacios en source.
  10. Calcula content_hash SHA-256 si falta.

  Resultado interno:

  RawDocument(
      document_id="doc_001",
      text="texto completo...",
      metadata=DocumentMetadata(...)
  )

  ## 4. Chunking

  El chunking actual está en:

  backend/src/hydra_api/chunking.py

  Es determinista por caracteres:

  chunk_size = 1200
  overlap = 150

  Ejemplo conceptual:

  chunk 0: caracteres 0-1200
  chunk 1: caracteres 1050-2250
  chunk 2: caracteres 2100-3300
  ...

  El solape de 150 caracteres evita cortar demasiado el contexto entre chunks.

  Cada chunk queda así:

  DocumentChunk(
      id="doc_001_chunk_000",
      document_id="doc_001",
      chunk_index=0,
      content="fragmento...",
      metadata={
          "document_id": "doc_001",
          "title": "...",
          "source": "...",
          "url": "...",
          "published_at": "...",
          "domain": "...",
          "chunk_index": 0
      }
  )

  ## 5. Persistencia

  En dry_run=True:

  solo cuenta documentos y chunks
  no abre DB
  no persiste nada

  En dry_run=False:

  - inserta/actualiza en tabla documents;
  - inserta/actualiza chunks en document_chunks;
  - deja embedding = NULL;
  - no llama modelos;
  - no calcula embeddings;
  - no hace extracción estructurada todavía.

  Tabla relevante:

  documents
  document_chunks

  Los embeddings vienen después, en la fase RAG/indexing.

  ## 6. Cómo se ejecuta

  Dry-run:

  cd backend
  uv run python -m hydra_api.ingest \
    --manifest data/metadata/local_corpus.manifest.template.json \
    --dry-run

  Con corpus real aprobado:

  cd backend
  uv run python -m hydra_api.ingest \
    --manifest data/metadata/local_corpus.manifest.json

  ## Punto importante

  El contrato SDD contempla POST /ingest, pero ahora mismo la ingesta operativa está
  implementada como servicio backend + CLI, no como endpoint FastAPI expuesto todavía.

  Para el TFM esto se puede explicar como:

  > HYDRA separa la selección del corpus, la carga raw, el chunking, la persistencia,
  > los embeddings y el análisis. Esto permite trazabilidad completa desde documento
  > original hasta chunk recuperado y evidencia usada en briefing.