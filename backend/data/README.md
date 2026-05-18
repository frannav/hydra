# Corpus Data Directory

## Structure

- `raw/` — will hold approved documents in a future phase. Only `.txt` and `.md` files are supported.
- `metadata/` — holds templates, manifest, and metadata for corpus documents.
- `fixtures/` — reserved for test fixtures.

## Metadata files

- `metadata/metadata_template.json` — template for per-document metadata.
- `metadata/local_corpus.manifest.template.json` — manifest template listing documents with `raw_path` and `metadata_path`. This file is currently **empty** (`"documents": []`). Codex/user will populate it with real documents later.

## Ingestion CLI

Dry-run validation (no database connection):

```bash
cd backend && uv run python -m hydra_api.ingest --manifest data/metadata/local_corpus.manifest.template.json --dry-run
```

## Rules

- **no se deben anadir documentos reales** al repositorio. Los documentos reales se agregan solo tras aprobacion explicita del usuario.
- No se deben versionar secretos ni datos sensibles.
- No hay documentos reales hasta que el usuario los apruebe.
- El objetivo para la fase futura es un corpus de **10-20** documentos.
- Solo se deben versionar archivos de plantilla (`.template.*`, `.gitkeep`).
