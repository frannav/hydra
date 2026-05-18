# Repair Packet — Mission 03 Corpus

Task:
Repair the reviewed implementation of `TASK-CORPUS-001` to `TASK-CORPUS-027` without adding new product scope.

Review verdict:
Mission 03 is **not accepted yet**. Most nominal checks passed, but the reviewer found blockers in DB persistence, path safety, loader validation, CLI semantics, and documentation scope.

## Source of truth

- `hydra/sdd/README.md`
- `hydra/sdd/01-architecture-decisions.md`
- `hydra/sdd/02-data-model.md`
- `hydra/sdd/03-api-contract.md`
- `hydra/sdd/rag-pipeline.md`
- `hydra/sdd/tasks/03-corpus/03-corpus.md`
- Existing DB schema in `hydra/backend/src/hydra_api/db_schema.py`

## Mission mode

- This is a **repair**, not a new feature.
- Do not decide or select the real corpus.
- Do not mark SDD tasks as `done`; Codex/reviewer will do that after acceptance.
- Do not commit.

## Allowed files

Primary repair files:

- `hydra/backend/src/hydra_api/ingest.py`
- `hydra/backend/data/README.md`
- `hydra/README.md`

Cleanup-only file:

- `hydra/backend/README.md`

Rules for `hydra/backend/README.md`:

- Use it only to remove/revert Mission 03 corpus additions that were outside the original allowed file list.
- Do not add new corpus documentation there.
- Required corpus documentation belongs in `hydra/README.md` and `hydra/backend/data/README.md`.

Read-only context files:

- `hydra/backend/src/hydra_api/db_schema.py`
- `hydra/backend/src/hydra_api/chunking.py`
- `hydra/backend/src/hydra_api/schemas.py`
- `hydra/backend/data/metadata/local_corpus.manifest.template.json`
- `hydra/backend/data/metadata/metadata_template.json`

## Forbidden

- Do not modify `hydra/frontend/**`.
- Do not modify `hydra/docs/**`.
- Do not modify `hydra/sdd/**`.
- Do not create or edit real `.env` files.
- Do not add real documents under `hydra/backend/data/raw/**`.
- Do not create real corpus metadata under `hydra/backend/data/metadata/documents/**`.
- Do not create `local_corpus.manifest.json`.
- Do not call models, embeddings, Langfuse, external APIs, scraping, or downloads.
- Do not introduce Neo4j, graph drivers, new dependencies, or frontend upload pipeline logic.

## Repair items

### REPAIR-CORPUS-001: Align document persistence with DB schema

Problem:

- `upsert_document()` inserts into `documents(document_id, ...)`, but `db_schema.py` defines the primary key column as `documents.id`.
- Non-dry-run ingestion would fail against PostgreSQL.

Required fix:

- Change `upsert_document(cur, raw_document)` to insert into `documents(id, title, source, url, published_at, domain, raw_path, content_hash, ingestion_source, processing_status)`.
- Use `raw_document.document_id` as the value for `documents.id`.
- Use `ON CONFLICT (id)`.
- Do not insert into a non-existent `document_id` column.
- Use only parameterized SQL.
- Do not reset an existing non-null `processing_status` on update; set `pending` on insert.
- Ensure persisted documents have non-null `raw_path` and `content_hash`, matching `db_schema.py`.
- Do not insert chunks in this function.

Acceptance checks:

- Static inspection shows `INSERT INTO documents (id, ...`.
- Static inspection shows `ON CONFLICT (id)`.
- Static inspection shows no insert target named `documents(document_id`.

### REPAIR-CORPUS-002: Harden `resolve_corpus_path`

Problem:

- `resolve_corpus_path()` uses string `startswith`.
- It accepts absolute paths inside the root.
- It can accept sibling-prefix traversal paths.

Required fix:

- Reject absolute `relative_path` values with `ValueError`.
- Resolve `root` and candidate paths.
- Ensure the candidate is actually inside root using `Path.relative_to()` or equivalent path-aware containment.
- Reject any path that escapes `root`.
- Do not read files in this function.
- Do not use string-prefix containment.

Acceptance checks:

- `resolve_corpus_path(Path("data"), "raw/doc.txt")` succeeds.
- `resolve_corpus_path(Path("data"), "../secret.txt")` fails.
- Absolute paths fail even if they point inside `data/`.
- Sibling-prefix traversal fails.

### REPAIR-CORPUS-003: Make local document loading reuse raw-text validation

Problem:

- `load_local_document()` reads `raw_path` directly.
- It bypasses `load_raw_text()`, so unsupported extensions like `.pdf` are accepted.
- It reads the raw file more than once.

Required fix:

- `load_local_document(raw_path, metadata_path)` must use `load_raw_text(raw_path)` exactly as the source of document text.
- `.txt` and `.md` remain the only accepted raw extensions.
- Empty raw files still fail.
- Compute `content_hash` from the already-loaded text when metadata lacks `content_hash`.
- Require `document_id` in metadata with a clear error.
- Preserve existing `metadata.raw_path` when present.
- If `metadata.raw_path` is missing, set it from `raw_path` so persistence has a non-null raw path.
- Do not persist to DB in this function.

Acceptance checks:

- A temporary `.txt` file loads.
- A temporary `.pdf` file is rejected.
- Missing `document_id` fails clearly.
- Result metadata contains `content_hash`.

### REPAIR-CORPUS-004: Validate manifest entries instead of skipping them

Problem:

- `load_local_corpus_manifest()` silently skips entries missing `raw_path` or `metadata_path`.

Required fix:

- Accept `documents: []` and return `[]`.
- For every non-empty entry, require both `raw_path` and `metadata_path`.
- If either is missing or empty, raise `ValueError`.
- Resolve both paths through `resolve_corpus_path()`.
- Keep the corpus root anchored to the `data/` directory for `data/metadata/local_corpus.manifest.template.json`.
- Do not create documents, raw files, or metadata files.

Acceptance checks:

- Empty template manifest returns `[]`.
- Entry missing `metadata_path` fails.
- Unsafe raw or metadata paths fail.

### REPAIR-CORPUS-005: Fix CLI semantics

Problem:

- TASK-CORPUS-026 says `--dry-run` must avoid DB access, and without `--dry-run` the CLI should allow persistence via `DATABASE_URL`.
- Current implementation adds `--persist`, which is not part of the task contract.

Required fix:

- Keep support for:
  - `python -m hydra_api.ingest --manifest data/metadata/local_corpus.manifest.template.json --dry-run`
  - `python -m hydra_api.ingest --help`
- Remove the need for `--persist`.
- `--dry-run` means `dry_run=True`.
- Absence of `--dry-run` means `dry_run=False` and may use `get_connection()` through `IngestionService`.
- `--dry-run` must not open a DB connection.
- Do not add `--init-db`.
- Do not print full document contents.

Acceptance checks:

- Help contains `--dry-run`.
- Help does not advertise `--persist`.
- Empty manifest with `--dry-run` runs without DB.

### REPAIR-CORPUS-006: Fix documentation and scope drift

Problem:

- `backend/data/README.md` does not document the manifest template and dry-run command required by TASK-CORPUS-027.
- `backend/data/README.md` fails the exact grep check for lowercase `no se deben anadir documentos reales`.
- `backend/README.md` was modified even though it was outside Mission 03 allowed files.

Required fix:

- In `hydra/backend/data/README.md`, document:
  - `backend/data/raw/`
  - `backend/data/metadata/`
  - `backend/data/metadata/local_corpus.manifest.template.json`
  - dry-run command:
    `cd backend && uv run python -m hydra_api.ingest --manifest data/metadata/local_corpus.manifest.template.json --dry-run`
  - the template manifest is empty.
  - Codex/user will select real documents later.
  - exact phrase: `no se deben anadir documentos reales`
  - target future corpus size of `10-20` documents.
- In `hydra/README.md`, keep only root-level corpus documentation required by TASK-CORPUS-027.
- Remove/revert Mission 03 corpus additions from `hydra/backend/README.md`.
- Do not claim that the real corpus already exists.
- Do not add real URLs.

Acceptance checks:

- Required greps pass.
- `backend/README.md` has no remaining Mission 03 corpus diff.

## Verification commands

Run from the workspace root that contains `hydra/`.

### Nominal corpus checks

```bash
test -d hydra/backend/data/raw && test -d hydra/backend/data/metadata && test -d hydra/backend/data/fixtures
find hydra/backend/data/raw -type f ! -name ".gitkeep"

cd hydra/backend && uv run python -m json.tool data/metadata/metadata_template.json >/tmp/hydra_metadata_template.json
cd hydra/backend && uv run python -c "import json; data=json.load(open('data/metadata/metadata_template.json')); required={'document_id','title','source','source_type','url','published_at','collected_at','domain','language','ingestion_source','raw_path','content_hash','notes'}; assert required <= set(data); assert data['ingestion_source']=='local_corpus'; print('metadata template ok')"
cd hydra/backend && uv run python -m json.tool data/metadata/local_corpus.manifest.template.json >/tmp/hydra_manifest_template.json
cd hydra/backend && uv run python -c "import json; data=json.load(open('data/metadata/local_corpus.manifest.template.json')); assert isinstance(data.get('documents'), list) and data['documents']==[]; print('manifest template ok')"

cd hydra/backend && uv run python -c "from hydra_api.ingest import load_local_corpus_manifest; from pathlib import Path; docs=load_local_corpus_manifest(Path('data/metadata/local_corpus.manifest.template.json')); assert docs==[]; print('empty manifest ok')"
cd hydra/backend && uv run python -c "from hydra_api.ingest import IngestionService; r=IngestionService().process_documents([], dry_run=True); assert r.processed_documents==0 and r.created_chunks==0 and r.dry_run is True; print('empty dry-run ok')"
cd hydra/backend && uv run python -m hydra_api.ingest --help
cd hydra/backend && uv run python -m hydra_api.ingest --manifest data/metadata/local_corpus.manifest.template.json --dry-run
```

### Repair-specific checks

```bash
cd hydra/backend && uv run python - <<'PY'
import inspect
from hydra_api import ingest

src = inspect.getsource(ingest.upsert_document)
assert "INSERT INTO documents (id," in src
assert "ON CONFLICT (id)" in src
assert "INSERT INTO documents (document_id" not in src
assert "%s" in src or "%(" in src
print("document upsert matches db schema")
PY

cd hydra/backend && uv run python - <<'PY'
from pathlib import Path
from hydra_api.ingest import resolve_corpus_path

p = resolve_corpus_path(Path("data"), "raw/doc.txt")
assert str(p).endswith("data/raw/doc.txt")

for bad in ["../secret.txt", str((Path("data") / "raw" / "doc.txt").resolve())]:
    try:
        resolve_corpus_path(Path("data"), bad)
    except ValueError:
        pass
    else:
        raise AssertionError(f"unsafe path accepted: {bad}")

root = Path("/tmp/hydra_path_root")
root.mkdir(exist_ok=True)
try:
    resolve_corpus_path(root, "../hydra_path_root_evil/doc.txt")
except ValueError:
    pass
else:
    raise AssertionError("sibling-prefix traversal accepted")

print("path safety ok")
PY

cd hydra/backend && uv run python - <<'PY'
from pathlib import Path
import json
import tempfile
from hydra_api.ingest import load_local_document

d = Path(tempfile.mkdtemp())
raw = d / "doc.txt"
meta = d / "meta.json"
raw.write_text("texto prueba", encoding="utf-8")
meta.write_text(json.dumps({"document_id":"doc_test","title":"T","source":"S","domain":"d","ingestion_source":"local_corpus"}), encoding="utf-8")
doc = load_local_document(raw, meta)
assert doc.document_id == "doc_test"
assert doc.text == "texto prueba"
assert doc.metadata.content_hash
assert doc.metadata.raw_path

bad_raw = d / "doc.pdf"
bad_raw.write_text("texto prueba", encoding="utf-8")
try:
    load_local_document(bad_raw, meta)
except ValueError:
    pass
else:
    raise AssertionError("unsupported raw extension accepted")

print("local document validation ok")
PY

cd hydra/backend && uv run python - <<'PY'
from pathlib import Path
import json
import tempfile
from hydra_api.ingest import load_local_corpus_manifest

d = Path(tempfile.mkdtemp())
manifest = d / "manifest.json"
manifest.write_text(json.dumps({"corpus_id":"x","domain":"d","documents":[{"raw_path":"raw/doc.txt"}]}), encoding="utf-8")
try:
    load_local_corpus_manifest(manifest)
except ValueError:
    pass
else:
    raise AssertionError("manifest entry missing metadata_path was accepted")

print("manifest validation ok")
PY

cd hydra/backend && uv run python - <<'PY'
import subprocess
import sys

help_text = subprocess.check_output([sys.executable, "-m", "hydra_api.ingest", "--help"], text=True)
assert "--dry-run" in help_text
assert "--persist" not in help_text
print("cli flags ok")
PY
```

### Documentation and scope checks

```bash
grep -n "10-20" hydra/backend/data/README.md
grep -n "no se deben anadir documentos reales" hydra/backend/data/README.md
grep -n "local_corpus.manifest.template.json" hydra/README.md hydra/backend/data/README.md

test -z "$(git diff --name-only -- hydra/backend/README.md)"
git diff --check
git status --short
```

## Final report back

Report exactly:

- Files modified.
- Verification commands executed.
- Output summary for each verification group.
- Confirmation that no real corpus documents were added.
- Confirmation that no `.env` files were changed.
- Confirmation that no frontend files were changed.
- Confirmation that SDD task statuses were not changed.
- Any blocker that remains.

