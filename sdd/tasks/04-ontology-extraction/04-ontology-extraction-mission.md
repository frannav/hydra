# Droid Mission Brief — 04 Ontology and Extraction

Mission:
Implementar el bloque `04-ontology-extraction` de HYDRA como una Mission larga, pero estrictamente limitada a ontologia ligera, validacion, prompts, fixtures sinteticos, persistencia/export y GraphProjection JSON sin documentos reales.

Objective:
Completar `TASK-ONT-001` a `TASK-ONT-012` y `TASK-EXT-001` a `TASK-EXT-019` respetando prioridades, dependencias, archivos permitidos y verificaciones de `hydra/sdd/tasks/04-ontology-extraction/04-ontology-extraction.md`.

Important context:
El usuario todavia no tiene documentos reales del corpus. No ejecutes extracciones reales. No llames modelos reales. Las tareas `TASK-EXT-020` a `TASK-EXT-022` estan bloqueadas y NO deben ejecutarse en esta mission.

Source of truth:
- `hydra/sdd/README.md`
- `hydra/sdd/01-architecture-decisions.md`
- `hydra/sdd/02-data-model.md`
- `hydra/sdd/03-api-contract.md`
- `hydra/sdd/rag-pipeline.md`
- `hydra/sdd/07-implementation-plan.md`
- `hydra/sdd/08-task-checklist.md`
- `hydra/sdd/09-droid-execution-workflow.md`
- `hydra/sdd/tasks/04-ontology-extraction/04-ontology-extraction.md`

Mission mode:
- Esto es ejecucion, no arquitectura.
- Droid no debe decidir una ontologia compleja.
- Droid no debe llamar modelos.
- Droid no debe cambiar decisiones del SDD.

Non-negotiable decisions:
- Backend Python con `uv`.
- Ontologia ligera en YAML.
- Extracciones validadas con Pydantic.
- No tocar frontend.
- No usar Neo4j.
- No anadir driver Neo4j.
- No calcular embeddings.
- No ejecutar extracciones reales.
- No llamar proveedores LLM en verificaciones.
- No guardar prompts ni salidas invalidas como artefactos canonicos.
- No afirmar coordinacion, intencion o atribucion sin evidencia explicita.
- No crear ni editar `.env` reales.
- No hardcodear secretos.
- No marcar tareas SDD como `done`.

Allowed files:
- `hydra/backend/pyproject.toml`
- `hydra/backend/uv.lock`
- `hydra/backend/ontology/.gitkeep`
- `hydra/backend/ontology/README.md`
- `hydra/backend/ontology/hydra_ontology.yaml`
- `hydra/backend/src/hydra_api/ontology.py`
- `hydra/backend/src/hydra_api/extraction_prompts.py`
- `hydra/backend/src/hydra_api/extraction.py`
- `hydra/backend/src/hydra_api/graph_projection.py`
- `hydra/backend/data/fixtures/extraction_valid_minimal.json`
- `hydra/backend/data/fixtures/extraction_invalid_unknown_id.json`
- `hydra/backend/data/outputs/.gitkeep`
- `hydra/README.md`

Forbidden files and areas:
- `hydra/frontend/**`
- `hydra/docs/**`
- `hydra/sdd/**`
- any real `.env` file
- real corpus documents
- real extraction outputs from model calls
- Neo4j config, drivers, or services
- files outside `Allowed files`

Execution rules:
- Execute tasks in order.
- Stop if a dependency is missing.
- Use only synthetic fixtures for validation.
- If a verification fails, fix only within the task scope.
- If another file is needed, stop and report why.
- Do not commit.
- Do not run destructive DB commands.

Milestone 1 — Lightweight ontology YAML
Tasks:
- `TASK-ONT-001`
- `TASK-ONT-002`
- `TASK-ONT-003`
- `TASK-ONT-004`
- `TASK-ONT-005`
- `TASK-ONT-006`

Goal:
Create ontology structure, add YAML dependency, and define small controlled vocabularies.

Milestone checks:
- `test -d hydra/backend/ontology`
- `grep -n "vocabulario controlado" hydra/backend/ontology/README.md`
- `cd hydra/backend && uv sync`
- `cd hydra/backend && uv run python -c "import yaml; print(yaml.__name__)"`
- `cd hydra/backend && uv run python -c "import yaml; data=yaml.safe_load(open('ontology/hydra_ontology.yaml')); assert data['version']; print('ontology metadata ok')"`
- `cd hydra/backend && uv run python -c "import yaml; items=yaml.safe_load(open('ontology/hydra_ontology.yaml'))['narrative_frames']; ids=[x['id'] for x in items]; assert len(items)>=4 and len(ids)==len(set(ids)) and 'unknown_or_insufficient_evidence' in ids; print('narrative frames ok')"`
- `cd hydra/backend && uv run python -c "import yaml; data=yaml.safe_load(open('ontology/hydra_ontology.yaml')); assert 'Document' in data['graph_node_types']; assert 'SUPPORTED_BY' in data['graph_edge_types']; print('graph vocab ok')"`

Stop immediately if:
- Ontology becomes a factual knowledge base.
- You add real actors as controlled vocabulary.
- You add Neo4j dependency.

Milestone 2 — Ontology loader, validator, and CLI
Tasks:
- `TASK-ONT-007`
- `TASK-ONT-008`
- `TASK-ONT-009`
- `TASK-ONT-010`
- `TASK-ONT-011`
- `TASK-ONT-012`

Goal:
Load, validate, query, and apply ontology constraints without DB/model calls.

Milestone checks:
- `cd hydra/backend && uv run python -c "import hydra_api.ontology; print('ontology import ok')"`
- `cd hydra/backend && uv run python -c "from pathlib import Path; from hydra_api.ontology import load_ontology; data=load_ontology(Path('ontology/hydra_ontology.yaml')); assert isinstance(data, dict); print('ontology load ok')"`
- `cd hydra/backend && uv run python -c "from pathlib import Path; from hydra_api.ontology import load_ontology, validate_ontology; data=validate_ontology(load_ontology(Path('ontology/hydra_ontology.yaml'))); assert data['narrative_frames']; print('ontology validate ok')"`
- `cd hydra/backend && uv run python -c "from pathlib import Path; from hydra_api.ontology import load_ontology, validate_ontology, allowed_ids; data=validate_ontology(load_ontology(Path('ontology/hydra_ontology.yaml'))); ids=allowed_ids(data,'narrative_frames'); assert ids; print('allowed ids ok')"`
- `cd hydra/backend && uv run python -m hydra_api.ontology --validate ontology/hydra_ontology.yaml`
- `cd hydra/backend && uv run python -m hydra_api.ontology --print-ids ontology/hydra_ontology.yaml narrative_frames`

Stop immediately if:
- The loader reads ontology at import time.
- Validation requires DB/model calls.
- Unknown controlled IDs pass silently.

Milestone 3 — Prompt builder, parser, validation, and fixtures
Tasks:
- `TASK-EXT-001`
- `TASK-EXT-002`
- `TASK-EXT-003`
- `TASK-EXT-004`
- `TASK-EXT-005`
- `TASK-EXT-006`
- `TASK-EXT-007`
- `TASK-EXT-008`

Goal:
Prepare structured extraction prompts and validation using synthetic fixtures only.

Milestone checks:
- `cd hydra/backend && uv run python -c "import hydra_api.extraction_prompts as p; text=p.EXTRACTION_SYSTEM_INSTRUCTIONS.lower(); assert 'coordinacion' in text or 'coordinación' in text; print('prompt instructions ok')"`
- `cd hydra/backend && uv run python -c "from pathlib import Path; from hydra_api.ontology import load_ontology, validate_ontology; from hydra_api.extraction_prompts import format_ontology_for_prompt; text=format_ontology_for_prompt(validate_ontology(load_ontology(Path('ontology/hydra_ontology.yaml')))); assert 'narrative_frames' in text; print('ontology prompt context ok')"`
- `cd hydra/backend && uv run python -c "from pathlib import Path; from hydra_api.schemas import DocumentMetadata, RawDocument; from hydra_api.ontology import load_ontology, validate_ontology; from hydra_api.extraction_prompts import build_extraction_prompt; ont=validate_ontology(load_ontology(Path('ontology/hydra_ontology.yaml'))); doc=RawDocument(document_id='d', text='texto', metadata=DocumentMetadata(title='T', source='S', domain='x')); msgs=build_extraction_prompt(doc, ont); assert msgs[0]['role']=='system' and msgs[1]['role']=='user'; print('prompt build ok')"`
- `cd hydra/backend && uv run python -c "import hydra_api.extraction; print('extraction import ok')"`
- `cd hydra/backend && uv run python -c "from hydra_api.extraction import parse_extraction_json; assert parse_extraction_json('{\"document_id\":\"d\"}')['document_id']=='d'; print('parse json ok')"`
- `cd hydra/backend && uv run python -c "from hydra_api.extraction import validate_extraction_payload; e=validate_extraction_payload({'document_id':'d','title':'T','source':'S'}); assert e.document_id=='d'; print('validate extraction ok')"`
- `cd hydra/backend && uv run python -c "import json; from pathlib import Path; from hydra_api.ontology import load_ontology, validate_ontology; from hydra_api.extraction import validate_extraction_payload_with_ontology; ont=validate_ontology(load_ontology(Path('ontology/hydra_ontology.yaml'))); validate_extraction_payload_with_ontology(json.load(open('data/fixtures/extraction_valid_minimal.json')), ont); print('valid fixture ok')"`

Stop immediately if:
- You call a real model.
- You use real corpus documents.
- Prompt rules omit evidence/limitations/coordinacion guardrails.

Milestone 4 — Extraction service, safe errors, persistence, export, and docs
Tasks:
- `TASK-EXT-009`
- `TASK-EXT-010`
- `TASK-EXT-011`
- `TASK-EXT-012`
- `TASK-EXT-013`
- `TASK-EXT-014`

Goal:
Create a lazy extraction service, safe errors, validated persistence/export helpers, CLI fixture validation, and docs.

Milestone checks:
- `cd hydra/backend && uv run python -c "import json; from pathlib import Path; from hydra_api.ontology import load_ontology, validate_ontology; from hydra_api.extraction import ExtractionService; ont=validate_ontology(load_ontology(Path('ontology/hydra_ontology.yaml'))); text=open('data/fixtures/extraction_valid_minimal.json').read(); e=ExtractionService().validate_model_output(text, ont); assert e.document_id; print('service validate ok')"`
- `cd hydra/backend && uv run python -c "from hydra_api.extraction import safe_extraction_error; msg=safe_extraction_error(ValueError('secret payload abcdef')); assert 'abcdef' not in msg or len(msg) < 120; print('safe extraction error ok')"`
- `cd hydra/backend && uv run python -c "from hydra_api.extraction import save_extraction; print(callable(save_extraction))"`
- `cd hydra/backend && uv run python -c "from pathlib import Path; from hydra_api.schemas import Extraction; from hydra_api.extraction import export_extraction_json; p=export_extraction_json(Extraction(document_id='doc_tmp', title='T', source='S'), Path('/tmp/hydra_extractions')); assert p.exists(); print('export extraction ok')"`
- `cd hydra/backend && uv run python -m hydra_api.extraction --help`
- `cd hydra/backend && uv run python -m hydra_api.extraction --validate-json data/fixtures/extraction_valid_minimal.json --ontology ontology/hydra_ontology.yaml --export-dir /tmp/hydra_extraction_cli`
- `grep -n "hydra_api.ontology --validate" hydra/README.md hydra/backend/ontology/README.md`

Stop immediately if:
- The service creates a model client in constructor by default.
- Any verification needs a real API key.
- Persistence stores prompts or invalid outputs.

Milestone 5 — GraphProjection JSON without Neo4j
Tasks:
- `TASK-EXT-015`
- `TASK-EXT-016`
- `TASK-EXT-017`
- `TASK-EXT-018`
- `TASK-EXT-019`

Goal:
Create deterministic GraphProjection JSON from validated extractions without Neo4j.

Milestone checks:
- `cd hydra/backend && uv run python -c "import hydra_api.graph_projection; print('graph projection import ok')"`
- `cd hydra/backend && uv run python -c "import pathlib; text=pathlib.Path('src/hydra_api/graph_projection.py').read_text().lower(); assert 'neo4j' not in text; print('no neo4j in graph projection')"`
- `cd hydra/backend && uv run python -c "import json; from hydra_api.extraction import validate_extraction_payload; from hydra_api.graph_projection import build_graph_nodes; e=validate_extraction_payload(json.load(open('data/fixtures/extraction_valid_minimal.json'))); nodes=build_graph_nodes(e); assert any(n.type=='Document' for n in nodes); print('graph nodes ok')"`
- `cd hydra/backend && uv run python -c "from hydra_api.schemas import Extraction; from hydra_api.graph_projection import build_graph_edges; assert build_graph_edges(Extraction(document_id='d', title='T', source='S'))==[]; print('no evidence no edges ok')"`
- `cd hydra/backend && uv run python -c "from hydra_api.schemas import Extraction; from hydra_api.graph_projection import build_graph_projection; gp=build_graph_projection(Extraction(document_id='d', title='T', source='S')); assert gp.document_id=='d'; print(gp.model_dump_json()); print('graph projection ok')"`
- `cd hydra/backend && uv run python -c "from pathlib import Path; from hydra_api.schemas import GraphProjection; from hydra_api.graph_projection import export_graph_projection_json; p=export_graph_projection_json(GraphProjection(document_id='doc_tmp'), Path('/tmp/hydra_graph_projection')); assert p.exists(); print('graph export ok')"`

Stop immediately if:
- You add Neo4j.
- You create graph edges without evidence.
- You infer coordination.

Blocked tasks — do not execute in this mission:
- `TASK-EXT-020`
- `TASK-EXT-021`
- `TASK-EXT-022`

Validation after each milestone:
- Confirm only allowed files changed.
- Run all milestone verification commands.
- Confirm no real corpus documents were used.
- Confirm no real model calls were made.
- Confirm no frontend files changed.
- Confirm no `.env` real files changed.
- Confirm no Neo4j dependency or config was added.

Final report back:
- Exact files modified.
- Commands executed and outputs.
- Confirmation that no model calls were made.
- Confirmation that blocked tasks remained untouched.
- Any blockers or scope questions.

Review handoff:
- Leave diff ready for Codex/user review.
- Do not mark SDD tasks as `done`; Codex/reviewer will do that after acceptance.
