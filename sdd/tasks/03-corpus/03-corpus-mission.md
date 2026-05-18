# Droid Mission Brief — 03 Corpus and Ingestion

Mission:
Implementar el bloque `03-corpus` de HYDRA como una Mission larga, pero estrictamente limitada a preparar corpus local e ingesta sin documentos reales.

Objective:
Completar `TASK-CORPUS-001` a `TASK-CORPUS-027` respetando prioridades, dependencias, archivos permitidos y verificaciones de `hydra/sdd/tasks/03-corpus/03-corpus.md`.

Important context:
El usuario todavia no tiene los documentos reales del corpus. No busques, descargues, inventes ni anadas documentos reales. Las tareas `TASK-CORPUS-028` a `TASK-CORPUS-031` estan bloqueadas y NO deben ejecutarse en esta mission.

Source of truth:
- `hydra/sdd/README.md`
- `hydra/sdd/01-architecture-decisions.md`
- `hydra/sdd/02-data-model.md`
- `hydra/sdd/03-api-contract.md`
- `hydra/sdd/04-rag-pipeline.md`
- `hydra/sdd/07-implementation-plan.md`
- `hydra/sdd/08-task-checklist.md`
- `hydra/sdd/09-droid-execution-workflow.md`
- `hydra/sdd/tasks/03-corpus/03-corpus.md`

Mission mode:
- Esto es ejecucion, no arquitectura.
- Droid no debe decidir el corpus real.
- Droid no debe seleccionar fuentes.
- Droid no debe cambiar decisiones del SDD.

Non-negotiable decisions:
- Backend Python con `uv`.
- `local_corpus` es la primera fuente soportada.
- `frontend_upload` queda solo preparado como extension futura, sin UI ni pipeline paralelo.
- No tocar frontend.
- No llamar modelos.
- No calcular embeddings.
- No ejecutar extraccion estructurada.
- No introducir Neo4j.
- No descargar, scrapear, buscar ni inventar documentos reales.
- No crear ni editar `.env` reales.
- No hardcodear secretos.
- No imprimir contenido completo de documentos en logs.
- No marcar tareas SDD como `done`.

Allowed files:
- `hydra/backend/data/raw/.gitkeep`
- `hydra/backend/data/metadata/.gitkeep`
- `hydra/backend/data/fixtures/.gitkeep`
- `hydra/backend/data/metadata/metadata_template.json`
- `hydra/backend/data/metadata/corpus_candidates.template.csv`
- `hydra/backend/data/metadata/local_corpus.manifest.template.json`
- `hydra/backend/data/README.md`
- `hydra/backend/src/hydra_api/schemas.py`
- `hydra/backend/src/hydra_api/ingest.py`
- `hydra/backend/src/hydra_api/chunking.py`
- `hydra/README.md`

Forbidden files and areas:
- `hydra/frontend/**`
- `hydra/docs/**`
- `hydra/sdd/**`
- any real `.env` file
- real corpus documents under `hydra/backend/data/raw/**`
- real corpus metadata under `hydra/backend/data/metadata/documents/**`
- model/extraction modules unless a task explicitly allows them
- files outside `Allowed files`

Execution rules:
- Execute tasks in order.
- Stop if a dependency is missing.
- If a task says only templates/fixtures, do not create real data.
- If a verification fails, fix only within the task scope.
- If another file is needed, stop and report why.
- Do not commit.
- Do not run destructive DB commands.

Milestone 1 — Local corpus structure and templates
Tasks:
- `TASK-CORPUS-001`
- `TASK-CORPUS-002`
- `TASK-CORPUS-003`
- `TASK-CORPUS-004`
- `TASK-CORPUS-005`

Goal:
Create empty corpus folders, metadata templates, candidate template, manifest template, and local corpus documentation.

Milestone checks:
- `test -d hydra/backend/data/raw && test -d hydra/backend/data/metadata && test -d hydra/backend/data/fixtures`
- `find hydra/backend/data/raw -type f ! -name ".gitkeep"`
- `cd hydra/backend && uv run python -m json.tool data/metadata/metadata_template.json >/tmp/hydra_metadata_template.json`
- `cd hydra/backend && uv run python -m json.tool data/metadata/local_corpus.manifest.template.json >/tmp/hydra_manifest_template.json`
- `cd hydra/backend && uv run python -c "import csv; rows=list(csv.DictReader(open('data/metadata/corpus_candidates.template.csv'))); required={'candidate_id','title','source','source_type','url','published_at','domain','language','include_decision','reason','notes'}; assert required <= set(rows[0].keys()); print('candidate template ok')"`
- `grep -n "10-20" hydra/backend/data/README.md`

Stop immediately if:
- You add real documents.
- You add real URLs.
- You claim the corpus is already selected.

Milestone 2 — Canonical schemas and pure ingest helpers
Tasks:
- `TASK-CORPUS-006`
- `TASK-CORPUS-007`
- `TASK-CORPUS-008`
- `TASK-CORPUS-009`
- `TASK-CORPUS-010`
- `TASK-CORPUS-011`
- `TASK-CORPUS-012`
- `TASK-CORPUS-013`

Goal:
Add canonical raw/ingested document schemas and pure helpers for date/source normalization, content hashing, path resolution, and metadata validation.

Milestone checks:
- `cd hydra/backend && uv run python -c "from hydra_api.schemas import DocumentMetadata, RawDocument; doc=RawDocument(document_id='doc_test', text='texto', metadata=DocumentMetadata(title='T', source='S', domain='test')); assert doc.document_id=='doc_test'; print('raw document ok')"`
- `cd hydra/backend && uv run python -c "from hydra_api.schemas import IngestedDocument; print(IngestedDocument.__name__)"`
- `cd hydra/backend && uv run python -c "import hydra_api.ingest; print('ingest import ok')"`
- `cd hydra/backend && uv run python -c "from hydra_api.ingest import normalize_date; assert normalize_date(None) is None; assert normalize_date('2026-05-15')=='2026-05-15'; print('date normalize ok')"`
- `cd hydra/backend && uv run python -c "from hydra_api.ingest import normalize_source; assert normalize_source('  Fuente   Publica  ')=='Fuente Publica'; print('source normalize ok')"`
- `cd hydra/backend && uv run python -c "from hydra_api.ingest import compute_content_hash; a=compute_content_hash('hola\\r\\n'); b=compute_content_hash('hola\\n'); assert a==b and len(a)==64; print('hash ok')"`
- `cd hydra/backend && uv run python -c "from pathlib import Path; from hydra_api.ingest import resolve_corpus_path; p=resolve_corpus_path(Path('data'), 'raw/doc.txt'); assert str(p).endswith('data/raw/doc.txt'); print('safe path ok')"`
- `cd hydra/backend && uv run python -c "from hydra_api.ingest import validate_metadata_dict; m=validate_metadata_dict({'title':'T','source':' Fuente ','domain':'d','ingestion_source':'local_corpus'}); assert m.source=='Fuente'; print('metadata validate ok')"`

Stop immediately if:
- Schemas import DB, pgvector, frontend, Neo4j, models, or FastAPI.
- Helpers call external services.
- `frontend_upload` is implemented as a second pipeline.

Milestone 3 — Local loader with empty manifest support
Tasks:
- `TASK-CORPUS-014`
- `TASK-CORPUS-015`
- `TASK-CORPUS-016`
- `TASK-CORPUS-017`

Goal:
Load metadata, raw text, individual local documents, and an empty/local manifest safely.

Milestone checks:
- `cd hydra/backend && uv run python -c "from pathlib import Path; from hydra_api.ingest import load_metadata_file; m=load_metadata_file(Path('data/metadata/metadata_template.json')); assert m.ingestion_source.value=='local_corpus'; print('metadata file ok')"`
- `cd hydra/backend && uv run python -c "from pathlib import Path; p=Path('/tmp/hydra_raw_test.txt'); p.write_text('texto', encoding='utf-8'); from hydra_api.ingest import load_raw_text; assert load_raw_text(p)=='texto'; print('raw text ok')"`
- `cd hydra/backend && uv run python -c "from pathlib import Path; import json, tempfile; from hydra_api.ingest import load_local_document; d=Path(tempfile.mkdtemp()); raw=d/'doc.txt'; meta=d/'meta.json'; raw.write_text('texto prueba', encoding='utf-8'); meta.write_text(json.dumps({'document_id':'doc_test','title':'T','source':'S','domain':'d','ingestion_source':'local_corpus'}), encoding='utf-8'); doc=load_local_document(raw, meta); assert doc.document_id=='doc_test' and doc.metadata.content_hash; print('local document ok')"`
- `cd hydra/backend && uv run python -c "from pathlib import Path; from hydra_api.ingest import load_local_corpus_manifest; docs=load_local_corpus_manifest(Path('data/metadata/local_corpus.manifest.template.json')); assert docs==[]; print('empty manifest ok')"`

Stop immediately if:
- Loader hardcodes only one absolute path.
- Loader requires real documents to pass.
- Loader accepts unsafe paths outside corpus root.

Milestone 4 — Deterministic chunking without embeddings
Tasks:
- `TASK-CORPUS-018`
- `TASK-CORPUS-019`
- `TASK-CORPUS-020`

Goal:
Create deterministic chunking and preserve traceability metadata.

Milestone checks:
- `cd hydra/backend && uv run python -c "import hydra_api.chunking; print('chunking import ok')"`
- `cd hydra/backend && uv run python -c "from hydra_api.chunking import chunk_text; assert chunk_text('hola', chunk_size=10, overlap=2)==['hola']; a=chunk_text('abcdef', chunk_size=4, overlap=1); assert a==['abcd','def']; print('chunk text ok')"`
- `cd hydra/backend && uv run python -c "from hydra_api.schemas import DocumentMetadata, RawDocument; from hydra_api.chunking import chunk_raw_document; doc=RawDocument(document_id='doc_001', text='abcdef', metadata=DocumentMetadata(title='Titulo', source='Fuente', url='https://example.invalid', domain='d')); chunks=chunk_raw_document(doc, chunk_size=4, overlap=1); assert chunks[0].id=='doc_001_chunk_000'; assert chunks[0].metadata['title']=='Titulo'; assert chunks[0].metadata['source']=='Fuente'; print('chunk metadata ok')"`

Stop immediately if:
- You calculate embeddings.
- You call model providers.
- Chunks lose `document_id`, title, source, or URL.

Milestone 5 — Ingestion service, persistence hooks, and CLI
Tasks:
- `TASK-CORPUS-021`
- `TASK-CORPUS-022`
- `TASK-CORPUS-023`
- `TASK-CORPUS-024`
- `TASK-CORPUS-025`
- `TASK-CORPUS-026`
- `TASK-CORPUS-027`

Goal:
Create a dry-run-capable ingestion service, optional DB persistence hooks, a safe CLI, and documentation.

Milestone checks:
- `cd hydra/backend && uv run python -c "from hydra_api.schemas import IngestionRunResult; r=IngestionRunResult(processed_documents=0, created_chunks=0, errors=[], dry_run=True); assert r.dry_run is True; print('ingestion result ok')"`
- `cd hydra/backend && uv run python -c "from hydra_api.ingest import IngestionService; service=IngestionService(); result=service.process_documents([], dry_run=True); assert result.processed_documents==0 and result.created_chunks==0; print('empty ingest ok')"`
- `cd hydra/backend && uv run python -c "from hydra_api.ingest import upsert_document; print(callable(upsert_document))"`
- `cd hydra/backend && uv run python -c "from hydra_api.ingest import upsert_chunks; print(callable(upsert_chunks))"`
- `cd hydra/backend && uv run python -c "import hydra_api.ingest; print('ingest import ok')"`
- `cd hydra/backend && uv run python -m hydra_api.ingest --help`
- `cd hydra/backend && uv run python -m hydra_api.ingest --manifest data/metadata/local_corpus.manifest.template.json --dry-run`
- `grep -n "local_corpus.manifest.template.json" hydra/README.md hydra/backend/data/README.md`
- `git diff --check`

Stop immediately if:
- `dry_run=True` opens a DB connection.
- The CLI requires real documents.
- The CLI prints full document contents.
- The service calls models or embeddings.

Blocked tasks — do not execute in this mission:
- `TASK-CORPUS-028`
- `TASK-CORPUS-029`
- `TASK-CORPUS-030`
- `TASK-CORPUS-031`

Validation after each milestone:
- Confirm only allowed files changed.
- Run all milestone verification commands.
- Confirm no real documents or real URLs were added.
- Confirm no frontend files changed.
- Confirm no `.env` real files changed.
- Confirm no model calls, embeddings, or extraction logic were introduced.

Final report back:
- Exact files modified.
- Commands executed and outputs.
- Confirmation that no real corpus documents were added.
- Confirmation that blocked tasks remained untouched.
- Any blockers or scope questions.

Review handoff:
- Leave diff ready for Codex/user review.
- Do not mark SDD tasks as `done`; Codex/reviewer will do that after acceptance.
