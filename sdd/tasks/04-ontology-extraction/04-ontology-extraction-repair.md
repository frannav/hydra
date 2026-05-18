# Repair Packet — Mission 04 Ontology and Extraction

Task:
Repair the reviewed implementation of `TASK-ONT-001` to `TASK-ONT-012` and
`TASK-EXT-001` to `TASK-EXT-019` without adding new product scope.

Review verdict:
Mission 04 is **not accepted yet**. Most nominal checks passed, but the
reviewer found blockers in documentation exact checks, controlled-vocabulary
validation, GraphProjection consistency, prompt context, and scope drift.

## Source of truth

- `hydra/sdd/README.md`
- `hydra/sdd/01-architecture-decisions.md`
- `hydra/sdd/02-data-model.md`
- `hydra/sdd/03-api-contract.md`
- `hydra/sdd/rag-pipeline.md`
- `hydra/sdd/07-implementation-plan.md`
- `hydra/sdd/08-task-checklist.md`
- `hydra/sdd/tasks/04-ontology-extraction/04-ontology-extraction.md`
- Existing DB schema in `hydra/backend/src/hydra_api/db_schema.py`
- Existing canonical schemas in `hydra/backend/src/hydra_api/schemas.py`

## Mission mode

- This is a **repair**, not a new feature.
- Do not execute real extractions.
- Do not call models.
- Do not use real corpus documents.
- Do not add Neo4j, graph drivers, embeddings, frontend upload, or RAG logic.
- Do not mark SDD tasks as `done`; Codex/reviewer will do that after
  acceptance.
- Do not commit.

## Allowed files

Primary repair files:

- `hydra/backend/src/hydra_api/ontology.py`
- `hydra/backend/src/hydra_api/extraction_prompts.py`
- `hydra/backend/src/hydra_api/graph_projection.py`
- `hydra/README.md`
- `hydra/backend/ontology/README.md`

Cleanup-only files:

- `hydra/backend/src/hydra_api/config.py`
- `hydra/backend/src/hydra_api/schemas.py`

Rules for cleanup-only files:

- Use them only to revert out-of-scope cleanup diffs introduced during Mission
  04 review/implementation.
- Do not change schemas, fields, defaults, enum values, API contracts, settings
  names, or behavior.
- If there is no diff in one of these files when you start, do not edit it.

Read-only context files:

- `hydra/backend/ontology/hydra_ontology.yaml`
- `hydra/backend/src/hydra_api/extraction.py`
- `hydra/backend/src/hydra_api/db_schema.py`
- `hydra/backend/data/fixtures/extraction_valid_minimal.json`
- `hydra/backend/data/fixtures/extraction_invalid_unknown_id.json`

## Forbidden

- Do not modify `hydra/frontend/**`.
- Do not modify `hydra/docs/**`.
- Do not modify `hydra/sdd/**`.
- Do not create or edit real `.env` files.
- Do not add real documents under `hydra/backend/data/raw/**`.
- Do not create real extraction outputs from model calls.
- Do not add model calls, embeddings, Langfuse calls, scraping, downloads, or
  network calls.
- Do not introduce Neo4j config, drivers, services, or dependency entries.
- Do not persist prompts, invalid LLM outputs, or payloads of failed validation.
- Do not print complete prompts, complete LLM outputs, or full evidence text in
  errors/logs.

## Repair items

### REPAIR-ONTEXT-001: Fix exact documentation checks

Problem:

- The Mission 04 check expects this exact lowercase phrase:
  `no ejecuta modelos`.
- `hydra/README.md` currently uses capitalized `No ejecuta modelos`.
- `hydra/backend/ontology/README.md` explains the same rule in English, so the
  exact grep does not match both files.

Required fix:

- In `hydra/README.md`, include the exact lowercase phrase
  `no ejecuta modelos` in the ontology/extraction section.
- In `hydra/backend/ontology/README.md`, include the exact lowercase phrase
  `no ejecuta modelos`.
- Keep the meaning clear: ontology and fixture validation must not call models
  or networks.
- Do not claim real extractions already exist.
- Do not add secrets or real corpus data.

Acceptance checks:

- `grep -n "hydra_api.ontology --validate" hydra/README.md hydra/backend/ontology/README.md`
- `grep -n "no ejecuta modelos" hydra/README.md hydra/backend/ontology/README.md`

### REPAIR-ONTEXT-002: Ensure extraction prompt includes ontology context

Problem:

- `format_ontology_for_prompt()` may be correct, but `build_extraction_prompt()`
  must include that formatted ontology context in the actual user message sent
  to the model.
- If the ontology context is only computed and not inserted, `TASK-EXT-002` and
  `TASK-EXT-003` are incomplete.

Required fix:

- In `hydra/backend/src/hydra_api/extraction_prompts.py`, ensure
  `build_extraction_prompt(raw_document, ontology)` includes the output of
  `format_ontology_for_prompt(ontology)` in the returned user message.
- The returned user message must contain at least `narrative_frames`.
- Keep the system instruction guardrails:
  - JSON only;
  - cite evidence;
  - include limitations;
  - do not assert coordination without explicit evidence;
  - use `unknown_or_insufficient_evidence` when evidence is insufficient.
- Do not call models.
- Do not load files at import time.

Acceptance checks:

- `cd hydra/backend && uv run python -c "from pathlib import Path; from hydra_api.schemas import DocumentMetadata, RawDocument; from hydra_api.ontology import load_ontology, validate_ontology; from hydra_api.extraction_prompts import build_extraction_prompt; ont=validate_ontology(load_ontology(Path('ontology/hydra_ontology.yaml'))); doc=RawDocument(document_id='d', text='texto', metadata=DocumentMetadata(title='T', source='S', domain='x')); msgs=build_extraction_prompt(doc, ont); assert msgs[0]['role']=='system' and msgs[1]['role']=='user'; assert 'narrative_frames' in msgs[1]['content']; print('prompt includes ontology context')"`

### REPAIR-ONTEXT-003: Validate nested `Actor.actor_type`

Problem:

- `validate_extraction_against_ontology()` validates top-level
  `Extraction.actor_types`, but not nested `Actor.actor_type`.
- A payload can currently include `actors=[{"actor_type": "not_allowed"}]` and
  pass ontology validation if top-level `actor_types` is empty.
- This violates the Mission 04 rule that every controlled category must be
  validated against the ontology.

Required fix:

- In `hydra/backend/src/hydra_api/ontology.py`, validate each non-null
  `actor.actor_type` in `extraction.actors` against the ontology `actor_types`
  IDs.
- Allow `actor.actor_type=None`.
- Allow empty `actors`.
- Fail with a clear and safe `ValueError` for unknown nested actor types.
- Do not change the `Actor` or `Extraction` schemas.
- Do not validate free-text actor names against ontology; only validate the
  controlled `actor_type` value.

Acceptance checks:

- `cd hydra/backend && uv run python -c "from pathlib import Path; from hydra_api.schemas import Extraction, Actor; from hydra_api.ontology import load_ontology, validate_ontology, validate_extraction_against_ontology; ont=validate_ontology(load_ontology(Path('ontology/hydra_ontology.yaml'))); e=Extraction(document_id='d', title='T', source='S', actors=[Actor(name='Actor sintetico', actor_type='government_agency')]); assert validate_extraction_against_ontology(e, ont) is e; print('nested actor_type valid ok')"`
- `cd hydra/backend && ! uv run python -c "from pathlib import Path; from hydra_api.schemas import Extraction, Actor; from hydra_api.ontology import load_ontology, validate_ontology, validate_extraction_against_ontology; ont=validate_ontology(load_ontology(Path('ontology/hydra_ontology.yaml'))); validate_extraction_against_ontology(Extraction(document_id='d', title='T', source='S', actors=[Actor(name='Actor sintetico', actor_type='not_allowed')]), ont)" && echo "nested actor_type rejected"`

### REPAIR-ONTEXT-004: Remove dangling GraphProjection edge endpoints

Problem:

- `build_graph_edges()` creates `SUPPORTED_BY` edges using `source=<evidence_ref>`.
- Evidence refs are not GraphProjection nodes because `Evidence` is not an
  allowed node type in the current SDD.
- This creates dangling edge endpoints and makes the GraphProjection internally
  inconsistent.

Required fix:

- In `hydra/backend/src/hydra_api/graph_projection.py`, ensure every
  `GraphEdge.source` and `GraphEdge.target` exists in `GraphProjection.nodes`.
- Do **not** add a new `Evidence` node type unless the SDD is changed first.
- Prefer removing `SUPPORTED_BY` edges for now and preserving evidence support
  through each analytical edge's `evidence_refs` plus
  `GraphProjection.evidence_refs`.
- Continue to create no edges when `evidence_fragments` is empty.
- Continue to create analytical edges only when evidence exists.
- Continue to ensure every edge has non-empty `evidence_refs`.
- Do not store full evidence text in `evidence_refs`.
- Do not infer coordination or add graph relationships not present in the
  validated extraction.
- Do not mention or import Neo4j.

Acceptance checks:

- `cd hydra/backend && uv run python -c "from hydra_api.schemas import Extraction; from hydra_api.graph_projection import build_graph_edges; assert build_graph_edges(Extraction(document_id='d', title='T', source='S'))==[]; print('no evidence no edges ok')"`
- `cd hydra/backend && uv run python -c "from hydra_api.schemas import Extraction, EvidenceFragment; from hydra_api.graph_projection import build_graph_edges; e=Extraction(document_id='d', title='T', source='S', narrative_frame_id='frame', evidence_fragments=[EvidenceFragment(text='evidencia sintetica', source_document_id='d')]); edges=build_graph_edges(e); assert edges and all(edge.evidence_refs for edge in edges); assert 'evidencia sintetica' not in str([edge.evidence_refs for edge in edges]); print('evidence edges ok')"`
- `cd hydra/backend && uv run python -c "from hydra_api.schemas import Extraction, EvidenceFragment; from hydra_api.graph_projection import build_graph_projection; e=Extraction(document_id='d', title='T', source='S', narrative_frame_id='frame', evidence_fragments=[EvidenceFragment(text='evidencia sintetica', source_document_id='d')]); gp=build_graph_projection(e); node_ids={n.id for n in gp.nodes}; assert gp.edges; assert all(edge.source in node_ids and edge.target in node_ids for edge in gp.edges); assert gp.evidence_refs; print('graph edges endpoints ok')"`
- `cd hydra/backend && uv run python -c "import pathlib; text=pathlib.Path('src/hydra_api/graph_projection.py').read_text().lower(); assert 'neo4j' not in text; print('no neo4j in graph projection')"`

### REPAIR-ONTEXT-005: Revert out-of-scope cleanup diffs

Problem:

- Mission 04 allowed files did not include `config.py` or `schemas.py`.
- The reviewed diff showed one-line cleanup changes in:
  - `hydra/backend/src/hydra_api/config.py`
  - `hydra/backend/src/hydra_api/schemas.py`
- Even if harmless, they are outside Mission 04 scope.

Required fix:

- If `hydra/backend/src/hydra_api/config.py` has a Mission 04 cleanup-only diff,
  revert that diff.
- If `hydra/backend/src/hydra_api/schemas.py` has a Mission 04 cleanup-only diff,
  revert that diff.
- Do not change schema fields, enum values, settings names, or behavior.
- Do not use this repair to refactor unrelated imports.

Acceptance checks:

- `git diff -- hydra/backend/src/hydra_api/config.py`
- `git diff -- hydra/backend/src/hydra_api/schemas.py`
- Both commands should show no Mission 04 repair diff unless Codex/user
  explicitly accepted a cleanup-only exception.

## Verification commands

Run from the workspace root that contains `hydra/`.

### Scope and safety checks

```bash
git status --short
git diff --name-only
find hydra/backend/data/raw -type f ! -name ".gitkeep"
find hydra/backend/data/outputs -type f ! -name ".gitkeep"
find hydra -name ".env" -o -name ".env.local"
grep -R "neo4j" -n hydra/backend/src/hydra_api hydra/backend/pyproject.toml hydra/backend/uv.lock || true
```

Expected:

- No `hydra/frontend/**` changes.
- No `hydra/docs/**` changes.
- No real `.env` or `.env.local` files.
- No real corpus documents.
- No real model-output extraction files.
- No Neo4j dependency, driver, service, or config.

### Repair-specific checks

```bash
grep -n "hydra_api.ontology --validate" hydra/README.md hydra/backend/ontology/README.md
grep -n "no ejecuta modelos" hydra/README.md hydra/backend/ontology/README.md

cd hydra/backend && uv run python -c "from pathlib import Path; from hydra_api.schemas import DocumentMetadata, RawDocument; from hydra_api.ontology import load_ontology, validate_ontology; from hydra_api.extraction_prompts import build_extraction_prompt; ont=validate_ontology(load_ontology(Path('ontology/hydra_ontology.yaml'))); doc=RawDocument(document_id='d', text='texto', metadata=DocumentMetadata(title='T', source='S', domain='x')); msgs=build_extraction_prompt(doc, ont); assert msgs[0]['role']=='system' and msgs[1]['role']=='user'; assert 'narrative_frames' in msgs[1]['content']; print('prompt includes ontology context')"

cd hydra/backend && uv run python -c "from pathlib import Path; from hydra_api.schemas import Extraction, Actor; from hydra_api.ontology import load_ontology, validate_ontology, validate_extraction_against_ontology; ont=validate_ontology(load_ontology(Path('ontology/hydra_ontology.yaml'))); e=Extraction(document_id='d', title='T', source='S', actors=[Actor(name='Actor sintetico', actor_type='government_agency')]); assert validate_extraction_against_ontology(e, ont) is e; print('nested actor_type valid ok')"
cd hydra/backend && ! uv run python -c "from pathlib import Path; from hydra_api.schemas import Extraction, Actor; from hydra_api.ontology import load_ontology, validate_ontology, validate_extraction_against_ontology; ont=validate_ontology(load_ontology(Path('ontology/hydra_ontology.yaml'))); validate_extraction_against_ontology(Extraction(document_id='d', title='T', source='S', actors=[Actor(name='Actor sintetico', actor_type='not_allowed')]), ont)" && echo "nested actor_type rejected"

cd hydra/backend && uv run python -c "from hydra_api.schemas import Extraction; from hydra_api.graph_projection import build_graph_edges; assert build_graph_edges(Extraction(document_id='d', title='T', source='S'))==[]; print('no evidence no edges ok')"
cd hydra/backend && uv run python -c "from hydra_api.schemas import Extraction, EvidenceFragment; from hydra_api.graph_projection import build_graph_edges; e=Extraction(document_id='d', title='T', source='S', narrative_frame_id='frame', evidence_fragments=[EvidenceFragment(text='evidencia sintetica', source_document_id='d')]); edges=build_graph_edges(e); assert edges and all(edge.evidence_refs for edge in edges); assert 'evidencia sintetica' not in str([edge.evidence_refs for edge in edges]); print('evidence edges ok')"
cd hydra/backend && uv run python -c "from hydra_api.schemas import Extraction, EvidenceFragment; from hydra_api.graph_projection import build_graph_projection; e=Extraction(document_id='d', title='T', source='S', narrative_frame_id='frame', evidence_fragments=[EvidenceFragment(text='evidencia sintetica', source_document_id='d')]); gp=build_graph_projection(e); node_ids={n.id for n in gp.nodes}; assert gp.edges; assert all(edge.source in node_ids and edge.target in node_ids for edge in gp.edges); assert gp.evidence_refs; print('graph edges endpoints ok')"
cd hydra/backend && uv run python -c "import pathlib; text=pathlib.Path('src/hydra_api/graph_projection.py').read_text().lower(); assert 'neo4j' not in text; print('no neo4j in graph projection')"
```

### Mission 04 regression checks

```bash
cd hydra/backend && uv sync
cd hydra/backend && uv run python -c "import yaml; print(yaml.__name__)"
cd hydra/backend && uv run python -m hydra_api.ontology --validate ontology/hydra_ontology.yaml
cd hydra/backend && uv run python -m hydra_api.ontology --print-ids ontology/hydra_ontology.yaml narrative_frames

cd hydra/backend && uv run python -c "import hydra_api.extraction; print('extraction import ok')"
cd hydra/backend && uv run python -c "from hydra_api.extraction import parse_extraction_json; assert parse_extraction_json('{\"document_id\":\"d\"}')['document_id']=='d'; print('parse json ok')"
cd hydra/backend && ! uv run python -c "from hydra_api.extraction import parse_extraction_json; parse_extraction_json('[1,2,3]')" && echo "json list root rejected"
cd hydra/backend && ! uv run python -c "from hydra_api.extraction import parse_extraction_json; parse_extraction_json(chr(96)*3 + 'json {} ' + chr(96)*3)" && echo "markdown wrapper rejected"
cd hydra/backend && uv run python -c "from hydra_api.extraction import safe_extraction_error; msg=safe_extraction_error(ValueError('secret payload abcdef')); assert 'abcdef' not in msg and 'secret payload' not in msg and len(msg) < 120; print('safe extraction error ok')"

cd hydra/backend && uv run python -m hydra_api.extraction --help
cd hydra/backend && uv run python -m hydra_api.extraction --validate-json data/fixtures/extraction_valid_minimal.json --ontology ontology/hydra_ontology.yaml --export-dir /tmp/hydra_extraction_cli
cd hydra/backend && ! uv run python -m hydra_api.extraction --validate-json data/fixtures/extraction_invalid_unknown_id.json --ontology ontology/hydra_ontology.yaml --export-dir /tmp/hydra_extraction_cli_invalid && echo "invalid extraction cli rejected"

cd hydra/backend && uv run python -c "import hydra_api.graph_projection; print('graph projection import ok')"
cd hydra/backend && uv run python -c "from pathlib import Path; from hydra_api.schemas import GraphProjection; from hydra_api.graph_projection import export_graph_projection_json; p=export_graph_projection_json(GraphProjection(document_id='doc_tmp'), Path('/tmp/hydra_graph_projection')); assert p.exists(); print('graph export ok')"
```

## Final report back

Report exactly:

- Files modified.
- Commands executed and whether they passed.
- Confirmation that no real model calls were made.
- Confirmation that no real corpus documents were used.
- Confirmation that no `.env` real files were created or edited.
- Confirmation that no frontend files changed.
- Confirmation that no Neo4j dependency/config/service was added.
- Any blocker that remains.

