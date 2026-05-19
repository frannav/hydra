# Tasks - Ontologia y extraccion

## Reglas de atomizacion

- Ejecutar estas tareas en orden.
- Cada tarea debe ser verificable por comandos concretos.
- No tocar frontend.
- No crear ni modificar `.env` reales.
- No descargar, scrapear, buscar ni inventar documentos reales.
- No llamar modelos reales en verificaciones salvo que una tarea futura lo indique explicitamente.
- No ejecutar extracciones sobre corpus real hasta que el corpus este aprobado.
- No introducir Neo4j ni drivers de grafo.
- No acoplar schemas canonicos a PostgreSQL, pgvector, Neo4j ni frontend.
- No calcular embeddings.
- No afirmar coordinacion, intencion o atribucion sin evidencia explicita.
- Toda extraccion debe tener evidencias o limitaciones.
- Toda categoria controlada debe validarse contra la ontologia.
- No imprimir prompts completos con contenido sensible ni salidas LLM completas en logs.
- No marcar tareas como `done` hasta que Codex/reviewer revise diff, comandos y secretos.

## Contexto importante

El usuario todavia no tiene documentos reales del corpus. Por eso estas tareas preparan:

- ontologia ligera;
- loader/validador de ontologia;
- builders de prompt;
- parsing y validacion Pydantic;
- validacion de vocabularios controlados;
- persistencia/export de extracciones validadas;
- proyeccion de grafo JSON sin Neo4j;
- fixtures sinteticos para verificacion.

Las tareas que requieren documentos reales o llamadas reales a modelos quedan bloqueadas hasta una fase posterior.

## Lecciones incorporadas antes de la mission ontologia/extraccion

- Separar ontologia, loader, validacion, prompt, parseo, servicio, persistencia y grafo.
- Verificar con fixtures sinteticos pequenos, no con documentos inventados como si fueran corpus real.
- Mantener la ontologia como vocabulario ligero, no como una base de conocimiento.
- La proyeccion de grafo es un artefacto derivado de extracciones validadas; Neo4j es solo sink futuro.
- El prompt debe incluir reglas de prudencia analitica y prohibir coordinacion sin evidencia.
- Alinear SQL con `backend/src/hydra_api/db_schema.py`; no inventar columnas ni nombres de PK.
- No aceptar silenciosamente JSON/YAML con forma incorrecta: root debe ser objeto cuando el helper espere objeto.
- No resetear estados ni sobrescribir artefactos validados sin que la tarea lo pida.
- Los errores seguros no deben incluir payloads completos, prompts completos, salidas LLM completas, secretos ni fragmentos largos.
- La documentacion debe apuntar a comandos y secciones existentes.

## Errores probables a evitar

- Convertir la ontologia en una KB factual con actores reales o hechos del corpus.
- Usar `yaml.load` en vez de `yaml.safe_load`.
- Leer archivos, abrir conexiones, crear clientes LLM o cargar ontologia en import time.
- Llamar modelos reales desde verificaciones o fixtures.
- Aceptar markdown fenced JSON como si fuera JSON puro cuando el parser todavia no lo soporta.
- Persistir prompts, salidas LLM invalidas o errores con contenido sensible.
- Insertar en columnas inexistentes de `extractions` o construir SQL con f-strings de payloads.
- Crear edges de grafo sin `evidence_refs` o inferir coordinacion/atribucion.
- Anadir dependencias de Neo4j, embeddings, LangChain/RAG o frontend en esta mission.
- Modificar SDD/statuses desde Droid.

## Edge cases obligatorios

- Ontologia YAML vacia o cuyo root no sea objeto debe fallar.
- IDs duplicados o no `snake_case` en vocabularios analiticos deben fallar.
- Seccion de ontologia desconocida debe fallar en `allowed_ids`.
- `narrative_frame_id=None` y listas controladas vacias deben ser validos.
- ID controlado desconocido en una extraccion debe fallar.
- JSON vacio, JSON invalido, root JSON no objeto y markdown fenced JSON deben fallar.
- Fixture invalido no debe exportarse como artefacto canonico.
- Servicio sin `model_client` debe poder validar fixtures sin red.
- Extraccion sin evidencias debe producir cero edges.
- Extraccion con evidencias solo puede producir edges con `evidence_refs`.

## Stop conditions generales

- La tarea necesita cambiar schemas canonicos o contrato API.
- La tarea necesita documentos reales, corpus aprobado o claves reales.
- La tarea necesita llamar un proveedor LLM, embeddings, Langfuse o red externa.
- La tarea necesita tocar frontend, docs historicos, `.env` reales o archivos fuera de scope.
- La tarea necesita modificar DB schema fuera de lo ya definido en `TASK-DB-*`.
- La verificacion no puede ejecutarse sin datos o servicios que no existen.

## Milestones sugeridos para Droid Missions

| Milestone | Tareas | Objetivo | Debe parar para review |
|---|---|---|---|
| 1 | TASK-ONT-001 a TASK-ONT-006 | Ontologia YAML atomica por secciones | Si inventa una ontologia compleja o introduce Neo4j |
| 2 | TASK-ONT-007 a TASK-ONT-012 | Loader, validacion y CLI de ontologia | Si requiere DB/modelos para validar vocabulario |
| 3 | TASK-EXT-001 a TASK-EXT-008 | Prompt, parseo y validacion con fixtures | Si llama modelos reales o usa documentos reales |
| 4 | TASK-EXT-009 a TASK-EXT-014 | Servicio, persistencia/export de extracciones | Si imprime prompts/salidas completas o acopla pgvector |
| 5 | TASK-EXT-015 a TASK-EXT-019 | GraphProjection JSON sin Neo4j | Si anade driver Neo4j o relaciones sin evidencia |
| 6 | TASK-EXT-020 a TASK-EXT-022 | Extraccion real futura | Bloqueado hasta corpus aprobado y claves configuradas |

## TASK-ONT-001: Crear estructura de ontologia

Estado: pending
Prioridad: must

Objetivo:
Crear la estructura minima para la ontologia ligera.

Archivos permitidos:
- `hydra/backend/ontology/.gitkeep`
- `hydra/backend/ontology/README.md`

Dependencias:
- TASK-BACK-010

Requisitos:
- Crear carpeta `hydra/backend/ontology/`.
- Documentar que la ontologia es vocabulario controlado ligero, no fuente de verdad factual.
- No incluir Neo4j.
- No incluir documentos reales.

Criterios de aceptacion:
- La carpeta existe.
- La documentacion limita el alcance de la ontologia.

Comandos de verificacion:
- `test -d hydra/backend/ontology`
- `grep -n "vocabulario controlado" hydra/backend/ontology/README.md`

## TASK-ONT-002: Anadir dependencia YAML

Estado: pending
Prioridad: must

Objetivo:
Permitir cargar ontologia YAML sin crear parsers manuales fragiles.

Archivos permitidos:
- `hydra/backend/pyproject.toml`
- `hydra/backend/uv.lock`

Dependencias:
- TASK-BACK-001

Requisitos:
- Anadir `PyYAML` si no existe.
- No anadir frameworks de ontologia.
- No anadir Neo4j.
- No modificar codigo de aplicacion en esta tarea.

Criterios de aceptacion:
- `yaml` es importable con `uv`.
- No aparece `neo4j` en dependencias.

Comandos de verificacion:
- `cd hydra/backend && uv sync`
- `cd hydra/backend && uv run python -c "import yaml; print(yaml.__name__)"`
- `cd hydra/backend && uv run python -c "import pathlib; text=pathlib.Path('pyproject.toml').read_text().lower(); assert 'neo4j' not in text; print('no neo4j dependency')"`

## TASK-ONT-003: Definir metadatos de ontologia YAML

Estado: pending
Prioridad: must

Objetivo:
Crear el archivo YAML base con version y descripcion.

Archivos permitidos:
- `hydra/backend/ontology/hydra_ontology.yaml`

Dependencias:
- TASK-ONT-001

Requisitos:
- Crear `version`.
- Crear `description`.
- Crear `language`.
- Crear secciones vacias o iniciales para vocabularios controlados.
- No incluir hechos sobre documentos reales.

Criterios de aceptacion:
- YAML valido.
- Incluye version.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "import yaml; data=yaml.safe_load(open('ontology/hydra_ontology.yaml')); assert data['version']; print('ontology metadata ok')"`

## TASK-ONT-004: Definir narrative_frames controlados

Estado: pending
Prioridad: must

Objetivo:
Definir IDs controlados de marcos narrativos de forma ligera.

Archivos permitidos:
- `hydra/backend/ontology/hydra_ontology.yaml`

Dependencias:
- TASK-ONT-003

Requisitos:
- Crear seccion `narrative_frames`.
- Cada item debe tener:
  - `id`
  - `label`
  - `description`
- IDs en `snake_case`.
- Incluir un item generico `unknown_or_insufficient_evidence`.
- No afirmar que esos frames son exhaustivos.

Criterios de aceptacion:
- Hay al menos 4 narrative frames.
- Todos tienen IDs unicos.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "import yaml; items=yaml.safe_load(open('ontology/hydra_ontology.yaml'))['narrative_frames']; ids=[x['id'] for x in items]; assert len(items)>=4 and len(ids)==len(set(ids)) and 'unknown_or_insufficient_evidence' in ids; print('narrative frames ok')"`

## TASK-ONT-005: Definir actor_types, sectors y threat_types

Estado: pending
Prioridad: must

Objetivo:
Definir vocabularios controlados basicos para categorias analiticas.

Archivos permitidos:
- `hydra/backend/ontology/hydra_ontology.yaml`

Dependencias:
- TASK-ONT-004

Requisitos:
- Crear secciones:
  - `actor_types`
  - `affected_sectors`
  - `threat_types`
- Cada item debe tener:
  - `id`
  - `label`
- IDs en `snake_case`.
- Incluir `unknown_or_insufficient_evidence` donde aplique.
- No incluir actores reales como vocabulario controlado.

Criterios de aceptacion:
- Las tres secciones existen.
- IDs no estan duplicados dentro de cada seccion.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "import yaml; data=yaml.safe_load(open('ontology/hydra_ontology.yaml')); sections=['actor_types','affected_sectors','threat_types']; assert all(data.get(s) and len([x['id'] for x in data[s]])==len({x['id'] for x in data[s]}) for s in sections); print('controlled categories ok')"`

## TASK-ONT-006: Definir tipos permitidos de GraphProjection

Estado: pending
Prioridad: should

Objetivo:
Mantener los tipos de grafo permitidos como vocabulario controlado sin introducir Neo4j.

Archivos permitidos:
- `hydra/backend/ontology/hydra_ontology.yaml`

Dependencias:
- TASK-ONT-003

Requisitos:
- Crear secciones:
  - `graph_node_types`
  - `graph_edge_types`
- Node types permitidos inicialmente:
  - `Document`
  - `Actor`
  - `NarrativeFrame`
  - `Location`
  - `Event`
  - `Sector`
  - `ThreatType`
- Edge types permitidos inicialmente:
  - `MENTIONS`
  - `HAS_NARRATIVE`
  - `OCCURS_IN`
  - `AFFECTS`
  - `SUPPORTED_BY`
- No mencionar Neo4j como dependencia runtime.

Criterios de aceptacion:
- Los tipos coinciden con `sdd/02-data-model.md`.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "import yaml; data=yaml.safe_load(open('ontology/hydra_ontology.yaml')); assert 'Document' in data['graph_node_types']; assert 'SUPPORTED_BY' in data['graph_edge_types']; print('graph vocab ok')"`

## TASK-ONT-007: Crear modulo de ontologia sin efectos en import

Estado: pending
Prioridad: must

Objetivo:
Crear modulo Python para cargar y validar la ontologia sin efectos externos.

Archivos permitidos:
- `hydra/backend/src/hydra_api/ontology.py`

Dependencias:
- TASK-ONT-002

Requisitos:
- Crear `hydra_api.ontology`.
- No cargar archivos en import time.
- No conectar a DB.
- No llamar modelos.
- No importar FastAPI.

Criterios de aceptacion:
- El modulo importa sin leer la ontologia.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "import hydra_api.ontology; print('ontology import ok')"`

## TASK-ONT-008: Crear loader de ontologia YAML

Estado: pending
Prioridad: must

Objetivo:
Cargar YAML de ontologia desde path explicito.

Archivos permitidos:
- `hydra/backend/src/hydra_api/ontology.py`

Dependencias:
- TASK-ONT-003
- TASK-ONT-007

Requisitos:
- Crear `load_ontology(path: Path) -> dict`.
- Usar `yaml.safe_load`.
- Rechazar archivo vacio.
- Rechazar root que no sea objeto/dict.
- No hacer fallback silencioso.
- No resolver rutas magicas ni usar una ruta hardcodeada.

Criterios de aceptacion:
- Carga `backend/ontology/hydra_ontology.yaml`.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "from pathlib import Path; from hydra_api.ontology import load_ontology; data=load_ontology(Path('ontology/hydra_ontology.yaml')); assert isinstance(data, dict); print('ontology load ok')"`
- `cd hydra/backend && ! uv run python -c "from pathlib import Path; p=Path('/tmp/hydra_empty_ontology.yaml'); p.write_text('', encoding='utf-8'); from hydra_api.ontology import load_ontology; load_ontology(p)" && echo "empty ontology rejected"`
- `cd hydra/backend && ! uv run python -c "from pathlib import Path; p=Path('/tmp/hydra_list_ontology.yaml'); p.write_text('- item\\n', encoding='utf-8'); from hydra_api.ontology import load_ontology; load_ontology(p)" && echo "non-object ontology rejected"`

## TASK-ONT-009: Validar estructura de ontologia

Estado: pending
Prioridad: must

Objetivo:
Detectar secciones faltantes, IDs duplicados y objetos incompletos.

Archivos permitidos:
- `hydra/backend/src/hydra_api/ontology.py`

Dependencias:
- TASK-ONT-008

Requisitos:
- Crear `validate_ontology(data: dict) -> dict`.
- Requerir secciones:
  - `narrative_frames`
  - `actor_types`
  - `affected_sectors`
  - `threat_types`
  - `graph_node_types`
  - `graph_edge_types`
- En secciones de objetos, validar que cada item tiene `id`.
- En secciones de objetos, validar IDs unicos por seccion.
- En secciones de objetos, validar IDs `snake_case` para vocabularios analiticos.
- Validar que `graph_node_types` y `graph_edge_types` son listas no vacias de strings.
- Devolver el mismo dict si es valido.

Criterios de aceptacion:
- Ontologia valida pasa.
- Duplicados fallan.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "from pathlib import Path; from hydra_api.ontology import load_ontology, validate_ontology; data=validate_ontology(load_ontology(Path('ontology/hydra_ontology.yaml'))); assert data['narrative_frames']; print('ontology validate ok')"`
- `cd hydra/backend && ! uv run python -c "from hydra_api.ontology import validate_ontology; validate_ontology({'narrative_frames':[{'id':'a'},{'id':'a'}], 'actor_types':[], 'affected_sectors':[], 'threat_types':[], 'graph_node_types':['Document'], 'graph_edge_types':['SUPPORTED_BY']})" && echo "duplicate ontology ids rejected"`
- `cd hydra/backend && ! uv run python -c "from hydra_api.ontology import validate_ontology; validate_ontology({'narrative_frames':[{'id':'Bad-ID'}], 'actor_types':[], 'affected_sectors':[], 'threat_types':[], 'graph_node_types':['Document'], 'graph_edge_types':['SUPPORTED_BY']})" && echo "bad ontology id rejected"`

## TASK-ONT-010: Obtener IDs permitidos por seccion

Estado: pending
Prioridad: must

Objetivo:
Exponer vocabularios controlados para validacion de extracciones.

Archivos permitidos:
- `hydra/backend/src/hydra_api/ontology.py`

Dependencias:
- TASK-ONT-009

Requisitos:
- Crear `allowed_ids(data: dict, section: str) -> set[str]`.
- Fallar si la seccion no existe.
- Devolver set de IDs.
- No modificar la ontologia.
- Rechazar secciones cuyo formato no sea lista de objetos con `id`.

Criterios de aceptacion:
- Funciona para `narrative_frames`.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "from pathlib import Path; from hydra_api.ontology import load_ontology, validate_ontology, allowed_ids; data=validate_ontology(load_ontology(Path('ontology/hydra_ontology.yaml'))); ids=allowed_ids(data,'narrative_frames'); assert ids; print('allowed ids ok')"`
- `cd hydra/backend && ! uv run python -c "from pathlib import Path; from hydra_api.ontology import load_ontology, validate_ontology, allowed_ids; data=validate_ontology(load_ontology(Path('ontology/hydra_ontology.yaml'))); allowed_ids(data,'missing_section')" && echo "missing section rejected"`

## TASK-ONT-011: Validar IDs controlados de una extraccion

Estado: pending
Prioridad: must

Objetivo:
Rechazar salidas LLM que usen categorias fuera de vocabulario.

Archivos permitidos:
- `hydra/backend/src/hydra_api/ontology.py`

Dependencias:
- TASK-ONT-010
- TASK-BACK-010

Requisitos:
- Crear `validate_extraction_against_ontology(extraction: Extraction, ontology: dict) -> Extraction`.
- Validar:
  - `narrative_frame_id` contra `narrative_frames`
  - `actor_types` contra `actor_types`
  - `affected_sectors` contra `affected_sectors`
  - `threat_types` contra `threat_types`
- Permitir `narrative_frame_id=None`.
- Permitir listas vacias.
- Fallar con mensaje claro y seguro si hay ID desconocido.

Criterios de aceptacion:
- IDs validos pasan.
- IDs desconocidos fallan.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "from pathlib import Path; from hydra_api.schemas import Extraction; from hydra_api.ontology import load_ontology, validate_ontology, validate_extraction_against_ontology, allowed_ids; ont=validate_ontology(load_ontology(Path('ontology/hydra_ontology.yaml'))); frame=next(iter(allowed_ids(ont,'narrative_frames'))); e=Extraction(document_id='d', title='T', source='S', narrative_frame_id=frame); assert validate_extraction_against_ontology(e, ont) is e; print('extraction ontology valid ok')"`
- `cd hydra/backend && uv run python -c "from pathlib import Path; from hydra_api.schemas import Extraction; from hydra_api.ontology import load_ontology, validate_ontology, validate_extraction_against_ontology; ont=validate_ontology(load_ontology(Path('ontology/hydra_ontology.yaml'))); e=Extraction(document_id='d', title='T', source='S'); assert validate_extraction_against_ontology(e, ont) is e; print('empty controlled ids ok')"`
- `cd hydra/backend && ! uv run python -c "from pathlib import Path; from hydra_api.schemas import Extraction; from hydra_api.ontology import load_ontology, validate_ontology, validate_extraction_against_ontology; ont=validate_ontology(load_ontology(Path('ontology/hydra_ontology.yaml'))); validate_extraction_against_ontology(Extraction(document_id='d', title='T', source='S', narrative_frame_id='not_allowed'), ont)" && echo "unknown extraction id rejected"`

## TASK-ONT-012: Crear CLI de validacion de ontologia

Estado: pending
Prioridad: must

Objetivo:
Permitir validar la ontologia desde CLI sin scripts sueltos.

Archivos permitidos:
- `hydra/backend/src/hydra_api/ontology.py`

Dependencias:
- TASK-ONT-011

Requisitos:
- Soportar `python -m hydra_api.ontology --validate ontology/hydra_ontology.yaml`.
- Soportar `python -m hydra_api.ontology --print-ids ontology/hydra_ontology.yaml narrative_frames`.
- No conectar a DB.
- No llamar modelos.

Criterios de aceptacion:
- CLI valida ontologia.
- CLI imprime IDs de seccion.

Comandos de verificacion:
- `cd hydra/backend && uv run python -m hydra_api.ontology --validate ontology/hydra_ontology.yaml`
- `cd hydra/backend && uv run python -m hydra_api.ontology --print-ids ontology/hydra_ontology.yaml narrative_frames`

## TASK-EXT-001: Crear modulo de prompts de extraccion

Estado: pending
Prioridad: must

Objetivo:
Centralizar instrucciones de extraccion estructurada sin llamar modelos.

Archivos permitidos:
- `hydra/backend/src/hydra_api/extraction_prompts.py`

Dependencias:
- TASK-ONT-012

Requisitos:
- Crear modulo `hydra_api.extraction_prompts`.
- Incluir instrucciones:
  - responder solo JSON compatible con `Extraction`;
  - citar evidencia;
  - incluir limitaciones;
  - no afirmar coordinacion sin evidencia explicita;
  - usar `unknown_or_insufficient_evidence` cuando no haya evidencia suficiente.
- No llamar modelos en import time.

Criterios de aceptacion:
- El modulo importa.
- El texto incluye la regla de coordinacion.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "import hydra_api.extraction_prompts as p; text=p.EXTRACTION_SYSTEM_INSTRUCTIONS.lower(); assert 'coordinacion' in text or 'coordinación' in text; print('prompt instructions ok')"`

## TASK-EXT-002: Crear contexto textual de ontologia para prompt

Estado: pending
Prioridad: must

Objetivo:
Convertir la ontologia validada en un contexto compacto para el prompt.

Archivos permitidos:
- `hydra/backend/src/hydra_api/extraction_prompts.py`

Dependencias:
- TASK-EXT-001
- TASK-ONT-010

Requisitos:
- Crear `format_ontology_for_prompt(ontology: dict) -> str`.
- Incluir IDs y labels de secciones controladas.
- No incluir YAML completo si no hace falta.
- No incluir documentos reales.

Criterios de aceptacion:
- Devuelve texto con `narrative_frames`.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "from pathlib import Path; from hydra_api.ontology import load_ontology, validate_ontology; from hydra_api.extraction_prompts import format_ontology_for_prompt; text=format_ontology_for_prompt(validate_ontology(load_ontology(Path('ontology/hydra_ontology.yaml')))); assert 'narrative_frames' in text; print('ontology prompt context ok')"`

## TASK-EXT-003: Construir prompt de extraccion por documento

Estado: pending
Prioridad: must

Objetivo:
Crear un builder que combine instrucciones, ontologia y documento raw.

Archivos permitidos:
- `hydra/backend/src/hydra_api/extraction_prompts.py`

Dependencias:
- TASK-CORPUS-006
- TASK-EXT-002

Requisitos:
- Crear `build_extraction_prompt(raw_document: RawDocument, ontology: dict) -> list[dict[str, str]]`.
- Devolver mensajes compatibles con API OpenAI-compatible (`role`, `content`).
- Incluir metadatos basicos del documento.
- Incluir texto del documento.
- No truncar silenciosamente en esta tarea.
- No llamar modelos.

Criterios de aceptacion:
- Devuelve al menos mensaje system y user.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "from pathlib import Path; from hydra_api.schemas import DocumentMetadata, RawDocument; from hydra_api.ontology import load_ontology, validate_ontology; from hydra_api.extraction_prompts import build_extraction_prompt; ont=validate_ontology(load_ontology(Path('ontology/hydra_ontology.yaml'))); doc=RawDocument(document_id='d', text='texto', metadata=DocumentMetadata(title='T', source='S', domain='x')); msgs=build_extraction_prompt(doc, ont); assert msgs[0]['role']=='system' and msgs[1]['role']=='user'; print('prompt build ok')"`

## TASK-EXT-004: Crear modulo de extraccion sin efectos en import

Estado: pending
Prioridad: must

Objetivo:
Crear modulo para parseo, validacion y servicio de extraccion sin efectos externos.

Archivos permitidos:
- `hydra/backend/src/hydra_api/extraction.py`

Dependencias:
- TASK-BACK-010

Requisitos:
- Crear `hydra_api.extraction`.
- No llamar modelos en import time.
- No conectar a DB en import time.
- No cargar ontologia en import time.

Criterios de aceptacion:
- El modulo importa sin efectos externos.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "import hydra_api.extraction; print('extraction import ok')"`

## TASK-EXT-005: Parsear JSON de salida LLM

Estado: pending
Prioridad: must

Objetivo:
Parsear salidas JSON de forma controlada antes de validarlas con Pydantic.

Archivos permitidos:
- `hydra/backend/src/hydra_api/extraction.py`

Dependencias:
- TASK-EXT-004

Requisitos:
- Crear `parse_extraction_json(text: str) -> dict`.
- Aceptar JSON puro.
- Rechazar string vacio.
- Rechazar root JSON que no sea objeto/dict.
- Rechazar markdown con texto fuera del JSON por ahora.
- No ejecutar codigo.

Criterios de aceptacion:
- JSON valido produce dict.
- JSON invalido falla con `ValueError`.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "from hydra_api.extraction import parse_extraction_json; assert parse_extraction_json('{\"document_id\":\"d\"}')['document_id']=='d'; print('parse json ok')"`
- `cd hydra/backend && ! uv run python -c "from hydra_api.extraction import parse_extraction_json; parse_extraction_json('[1,2,3]')" && echo "json list root rejected"`
- `cd hydra/backend && ! uv run python -c "from hydra_api.extraction import parse_extraction_json; parse_extraction_json(chr(96)*3 + 'json {} ' + chr(96)*3)" && echo "markdown wrapper rejected"`

## TASK-EXT-006: Validar JSON como Extraction Pydantic

Estado: pending
Prioridad: must

Objetivo:
Convertir dict JSON en `Extraction` canonica validada.

Archivos permitidos:
- `hydra/backend/src/hydra_api/extraction.py`

Dependencias:
- TASK-EXT-005

Requisitos:
- Crear `validate_extraction_payload(payload: dict) -> Extraction`.
- Usar schema `Extraction`.
- Requerir `document_id`, `title` y `source`.
- No modificar vocabularios controlados en esta tarea.
- Rechazar payloads que no sean dict con `ValueError` seguro.

Criterios de aceptacion:
- Payload minimo valido pasa.
- Payload sin `document_id` falla.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "from hydra_api.extraction import validate_extraction_payload; e=validate_extraction_payload({'document_id':'d','title':'T','source':'S'}); assert e.document_id=='d'; print('validate extraction ok')"`
- `cd hydra/backend && ! uv run python -c "from hydra_api.extraction import validate_extraction_payload; validate_extraction_payload(['not','dict'])" && echo "non-dict payload rejected"`
- `cd hydra/backend && ! uv run python -c "from hydra_api.extraction import validate_extraction_payload; validate_extraction_payload({'title':'T','source':'S'})" && echo "missing document_id rejected"`

## TASK-EXT-007: Validar extraccion contra ontologia

Estado: pending
Prioridad: must

Objetivo:
Integrar validacion Pydantic y vocabulario controlado en un solo helper.

Archivos permitidos:
- `hydra/backend/src/hydra_api/extraction.py`

Dependencias:
- TASK-EXT-006
- TASK-ONT-011

Requisitos:
- Crear `validate_extraction_payload_with_ontology(payload: dict, ontology: dict) -> Extraction`.
- Primero validar Pydantic.
- Luego validar IDs controlados.
- Devolver `Extraction`.

Criterios de aceptacion:
- Payload valido pasa.
- ID controlado desconocido falla.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "from pathlib import Path; from hydra_api.ontology import load_ontology, validate_ontology, allowed_ids; from hydra_api.extraction import validate_extraction_payload_with_ontology; ont=validate_ontology(load_ontology(Path('ontology/hydra_ontology.yaml'))); frame=next(iter(allowed_ids(ont,'narrative_frames'))); e=validate_extraction_payload_with_ontology({'document_id':'d','title':'T','source':'S','narrative_frame_id':frame}, ont); assert e.narrative_frame_id==frame; print('payload ontology ok')"`

## TASK-EXT-008: Crear fixtures sinteticos de extraccion

Estado: pending
Prioridad: must

Objetivo:
Permitir verificar parseo/validacion sin corpus real ni llamada a modelos.

Archivos permitidos:
- `hydra/backend/data/fixtures/extraction_valid_minimal.json`
- `hydra/backend/data/fixtures/extraction_invalid_unknown_id.json`

Dependencias:
- TASK-EXT-007

Requisitos:
- Crear fixture valido minimo.
- Crear fixture invalido con ID controlado desconocido.
- Usar contenido sintetico claramente no perteneciente al corpus real.
- Incluir al menos un `evidence_fragments` sintetico en el fixture valido para probar GraphProjection con evidencia.
- Incluir `limitations` en el fixture valido.
- No incluir URLs reales.

Criterios de aceptacion:
- Fixture valido pasa Pydantic.
- Fixture invalido falla por ontologia.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "import json; from pathlib import Path; from hydra_api.ontology import load_ontology, validate_ontology; from hydra_api.extraction import validate_extraction_payload_with_ontology; ont=validate_ontology(load_ontology(Path('ontology/hydra_ontology.yaml'))); validate_extraction_payload_with_ontology(json.load(open('data/fixtures/extraction_valid_minimal.json')), ont); print('valid fixture ok')"`
- `cd hydra/backend && ! uv run python -c "import json; from pathlib import Path; from hydra_api.ontology import load_ontology, validate_ontology; from hydra_api.extraction import validate_extraction_payload_with_ontology; ont=validate_ontology(load_ontology(Path('ontology/hydra_ontology.yaml'))); validate_extraction_payload_with_ontology(json.load(open('data/fixtures/extraction_invalid_unknown_id.json')), ont)" && echo "invalid fixture rejected"`

## TASK-EXT-009: Crear servicio de extraccion lazy

Estado: pending
Prioridad: must

Objetivo:
Preparar una clase de servicio que pueda llamar modelos en el futuro sin llamadas en import time.

Archivos permitidos:
- `hydra/backend/src/hydra_api/extraction.py`

Dependencias:
- TASK-EXT-003
- TASK-EXT-007
- TASK-BACK-009

Requisitos:
- Crear `ExtractionService`.
- Constructor acepta `model_client` opcional.
- No crear cliente de modelo si no se llama extraccion real.
- Exponer metodo `validate_model_output(text: str, ontology: dict) -> Extraction`.
- No hacer llamadas de red en verificaciones.

Criterios de aceptacion:
- El servicio puede validar fixture JSON sin cliente.
- Importar modulo no llama modelos.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "import json; from pathlib import Path; from hydra_api.ontology import load_ontology, validate_ontology; from hydra_api.extraction import ExtractionService; ont=validate_ontology(load_ontology(Path('ontology/hydra_ontology.yaml'))); text=open('data/fixtures/extraction_valid_minimal.json').read(); e=ExtractionService().validate_model_output(text, ont); assert e.document_id; print('service validate ok')"`

## TASK-EXT-010: Definir politica simple de errores de extraccion

Estado: pending
Prioridad: must

Objetivo:
Evitar errores inseguros o confusos cuando falla parseo o validacion.

Archivos permitidos:
- `hydra/backend/src/hydra_api/extraction.py`

Dependencias:
- TASK-EXT-009

Requisitos:
- Crear excepcion `ExtractionValidationError`.
- Crear helper `safe_extraction_error(exc: Exception) -> str`.
- No incluir prompt completo.
- No incluir salida LLM completa.
- Incluir solo tipo de fallo y mensaje corto.
- No devolver tokens de prueba, payloads largos ni el texto completo de la excepcion original.

Criterios de aceptacion:
- Error seguro no contiene payload completo.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "from hydra_api.extraction import safe_extraction_error; msg=safe_extraction_error(ValueError('secret payload abcdef')); assert 'abcdef' not in msg and 'secret payload' not in msg and len(msg) < 120; print('safe extraction error ok')"`

## TASK-EXT-011: Persistir extraccion validada en PostgreSQL

Estado: pending
Prioridad: must

Objetivo:
Guardar extracciones validadas como artefacto canonico.

Archivos permitidos:
- `hydra/backend/src/hydra_api/extraction.py`

Dependencias:
- TASK-DB-020
- TASK-EXT-007

Requisitos:
- Crear `save_extraction(conn, extraction: Extraction) -> None`.
- Usar SQL parametrizado.
- Insertar en tabla `extractions`.
- Alinear columnas con `backend/src/hydra_api/db_schema.py`: `id`, `document_id`, `extraction_json`, `schema_version`.
- Generar `id` determinista a partir de `document_id` y `schema_version`, por ejemplo `document_id_extraction_schema_version`.
- Usar `ON CONFLICT (id)` para actualizar solo `extraction_json` y `schema_version`.
- Guardar `extraction_json` como JSONB.
- No guardar prompts.
- No guardar respuestas LLM invalidas.
- No abrir conexion en import time.
- No construir SQL con f-strings de valores de usuario.

Criterios de aceptacion:
- Funcion importable.
- No requiere DB al import.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "from hydra_api.extraction import save_extraction; print(callable(save_extraction))"`
- `cd hydra/backend && uv run python -c "import inspect; from hydra_api import extraction; src=inspect.getsource(extraction.save_extraction); assert 'INSERT INTO extractions (id, document_id, extraction_json, schema_version)' in src; assert 'ON CONFLICT (id)' in src; assert '%s' in src or '%(' in src; print('extraction sql schema ok')"`

## TASK-EXT-012: Exportar extraccion validada a JSON local

Estado: pending
Prioridad: must

Objetivo:
Crear export local reproducible para demo/evals sin depender solo de DB.

Archivos permitidos:
- `hydra/backend/src/hydra_api/extraction.py`
- `hydra/backend/data/outputs/.gitkeep`

Dependencias:
- TASK-EXT-007

Requisitos:
- Crear `export_extraction_json(extraction: Extraction, output_dir: Path) -> Path`.
- Crear `output_dir` si no existe.
- Escribir `document_id.extraction.json`.
- No exportar prompts ni claves.
- Usar JSON indentado y UTF-8.

Criterios de aceptacion:
- Puede exportar fixture validado a `/tmp`.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "from pathlib import Path; from hydra_api.schemas import Extraction; from hydra_api.extraction import export_extraction_json; p=export_extraction_json(Extraction(document_id='doc_tmp', title='T', source='S'), Path('/tmp/hydra_extractions')); assert p.exists(); print('export extraction ok')"`

## TASK-EXT-013: Crear CLI de validacion/export de extraccion

Estado: pending
Prioridad: must

Objetivo:
Permitir validar fixtures y exportar JSON sin llamadas de red.

Archivos permitidos:
- `hydra/backend/src/hydra_api/extraction.py`

Dependencias:
- TASK-EXT-008
- TASK-EXT-012

Requisitos:
- Soportar `python -m hydra_api.extraction --validate-json data/fixtures/extraction_valid_minimal.json --ontology ontology/hydra_ontology.yaml`.
- Soportar `--export-dir`.
- No llamar modelos.
- No conectar a DB.
- Si la validacion falla, salir con codigo distinto de cero y no exportar artefacto.

Criterios de aceptacion:
- Valida fixture.
- `--help` funciona.

Comandos de verificacion:
- `cd hydra/backend && uv run python -m hydra_api.extraction --help`
- `cd hydra/backend && uv run python -m hydra_api.extraction --validate-json data/fixtures/extraction_valid_minimal.json --ontology ontology/hydra_ontology.yaml --export-dir /tmp/hydra_extraction_cli`
- `cd hydra/backend && ! uv run python -m hydra_api.extraction --validate-json data/fixtures/extraction_invalid_unknown_id.json --ontology ontology/hydra_ontology.yaml --export-dir /tmp/hydra_extraction_cli_invalid && echo "invalid extraction cli rejected"`

## TASK-EXT-014: Documentar flujo de extraccion sin corpus real

Estado: pending
Prioridad: must

Objetivo:
Documentar como validar ontologia y fixtures mientras no hay documentos reales.

Archivos permitidos:
- `hydra/README.md`
- `hydra/backend/ontology/README.md`

Dependencias:
- TASK-ONT-012
- TASK-EXT-013

Requisitos:
- Documentar:
  - `cd backend && uv run python -m hydra_api.ontology --validate ontology/hydra_ontology.yaml`
  - `cd backend && uv run python -m hydra_api.extraction --validate-json data/fixtures/extraction_valid_minimal.json --ontology ontology/hydra_ontology.yaml`
- Aclarar que no ejecuta modelos.
- Aclarar que la extraccion real espera corpus aprobado.

Criterios de aceptacion:
- README no afirma que ya hay extracciones reales.
- No incluye secretos.

Comandos de verificacion:
- `grep -n "hydra_api.ontology --validate" hydra/README.md hydra/backend/ontology/README.md`
- `grep -n "no ejecuta modelos" hydra/README.md hydra/backend/ontology/README.md`

## TASK-EXT-015: Crear modulo GraphProjection sin efectos en import

Estado: pending
Prioridad: should

Objetivo:
Preparar proyeccion de grafo JSON derivada de extraccion validada sin Neo4j.

Archivos permitidos:
- `hydra/backend/src/hydra_api/graph_projection.py`

Dependencias:
- TASK-BACK-010

Requisitos:
- Crear `hydra_api.graph_projection`.
- No importar Neo4j.
- No conectar a DB.
- No llamar modelos.

Criterios de aceptacion:
- El modulo importa.
- No aparece `neo4j` en el modulo.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "import hydra_api.graph_projection; print('graph projection import ok')"`
- `cd hydra/backend && uv run python -c "import pathlib; text=pathlib.Path('src/hydra_api/graph_projection.py').read_text().lower(); assert 'neo4j' not in text; print('no neo4j in graph projection')"`

## TASK-EXT-016: Crear nodos base de GraphProjection

Estado: pending
Prioridad: should

Objetivo:
Crear nodos derivados de documento y extraccion validada.

Archivos permitidos:
- `hydra/backend/src/hydra_api/graph_projection.py`

Dependencias:
- TASK-EXT-015

Requisitos:
- Crear `build_graph_nodes(extraction: Extraction) -> list[GraphNode]`.
- Incluir nodo `Document`.
- Incluir nodo `NarrativeFrame` si hay `narrative_frame_id`.
- Incluir nodos `Actor`, `Location`, `Event`, `Sector`, `ThreatType` cuando existan.
- IDs deterministas.
- No crear nodos desde texto libre fuera del schema.

Criterios de aceptacion:
- Fixture valido produce al menos nodo Document.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "import json; from hydra_api.extraction import validate_extraction_payload; from hydra_api.graph_projection import build_graph_nodes; e=validate_extraction_payload(json.load(open('data/fixtures/extraction_valid_minimal.json'))); nodes=build_graph_nodes(e); assert any(n.type=='Document' for n in nodes); print('graph nodes ok')"`

## TASK-EXT-017: Crear edges con evidencia obligatoria

Estado: pending
Prioridad: should

Objetivo:
Crear relaciones de grafo solo cuando existan referencias de evidencia.

Archivos permitidos:
- `hydra/backend/src/hydra_api/graph_projection.py`

Dependencias:
- TASK-EXT-016

Requisitos:
- Crear `build_graph_edges(extraction: Extraction) -> list[GraphEdge]`.
- No crear edges si `evidence_fragments` esta vacio.
- Toda edge debe tener `evidence_refs`.
- `evidence_refs` debe referenciar indices o IDs deterministas de `evidence_fragments`, no texto completo.
- Tipos permitidos:
  - `MENTIONS`
  - `HAS_NARRATIVE`
  - `OCCURS_IN`
  - `AFFECTS`
  - `SUPPORTED_BY`
- No inferir coordinacion.

Criterios de aceptacion:
- Extraccion sin evidencias produce cero edges.
- Extraccion con evidencias produce edges con `evidence_refs`.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "from hydra_api.schemas import Extraction; from hydra_api.graph_projection import build_graph_edges; assert build_graph_edges(Extraction(document_id='d', title='T', source='S'))==[]; print('no evidence no edges ok')"`
- `cd hydra/backend && uv run python -c "from hydra_api.schemas import Extraction, EvidenceFragment; from hydra_api.graph_projection import build_graph_edges; e=Extraction(document_id='d', title='T', source='S', narrative_frame_id='frame', evidence_fragments=[EvidenceFragment(text='evidencia sintetica', source_document_id='d')]); edges=build_graph_edges(e); assert edges and all(edge.evidence_refs for edge in edges); assert 'evidencia sintetica' not in str([edge.evidence_refs for edge in edges]); print('evidence edges ok')"`

## TASK-EXT-018: Crear GraphProjection completo

Estado: pending
Prioridad: should

Objetivo:
Construir `GraphProjection` desde una extraccion Pydantic valida.

Archivos permitidos:
- `hydra/backend/src/hydra_api/graph_projection.py`

Dependencias:
- TASK-EXT-016
- TASK-EXT-017

Requisitos:
- Crear `build_graph_projection(extraction: Extraction) -> GraphProjection`.
- Usar `build_graph_nodes`.
- Usar `build_graph_edges`.
- Incluir `document_id`.
- Incluir `evidence_refs`.
- `evidence_refs` del projection debe derivarse de las edges, no inventarse.
- No llamar Neo4j.

Criterios de aceptacion:
- Devuelve `GraphProjection`.
- Puede serializarse a JSON.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "from hydra_api.schemas import Extraction; from hydra_api.graph_projection import build_graph_projection; gp=build_graph_projection(Extraction(document_id='d', title='T', source='S')); assert gp.document_id=='d'; print(gp.model_dump_json()); print('graph projection ok')"`
- `cd hydra/backend && uv run python -c "from hydra_api.schemas import Extraction, EvidenceFragment; from hydra_api.graph_projection import build_graph_projection; e=Extraction(document_id='d', title='T', source='S', narrative_frame_id='frame', evidence_fragments=[EvidenceFragment(text='evidencia sintetica', source_document_id='d')]); gp=build_graph_projection(e); assert gp.edges and gp.evidence_refs; print('graph projection evidence refs ok')"`

## TASK-EXT-019: Exportar GraphProjection JSON

Estado: pending
Prioridad: should

Objetivo:
Dejar un artefacto exportable para sinks futuros sin acoplar Neo4j.

Archivos permitidos:
- `hydra/backend/src/hydra_api/graph_projection.py`
- `hydra/backend/data/outputs/.gitkeep`

Dependencias:
- TASK-EXT-018

Requisitos:
- Crear `export_graph_projection_json(projection: GraphProjection, output_dir: Path) -> Path`.
- Escribir `document_id.graph_projection.json`.
- No conectar a Neo4j.
- No depender de driver de grafo.

Criterios de aceptacion:
- Exporta JSON a `/tmp`.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "from pathlib import Path; from hydra_api.schemas import GraphProjection; from hydra_api.graph_projection import export_graph_projection_json; p=export_graph_projection_json(GraphProjection(document_id='doc_tmp'), Path('/tmp/hydra_graph_projection')); assert p.exists(); print('graph export ok')"`

## TASK-EXT-020: Ejecutar extraccion real sobre 2-3 documentos

Estado: blocked
Prioridad: must

Bloqueo:
Depende de corpus real aprobado y claves de modelo configuradas localmente.

Objetivo:
Extraer 2-3 documentos reales de prueba para validar el flujo end-to-end.

Archivos permitidos:
- `hydra/backend/data/outputs/extractions/**`

Dependencias:
- TASK-CORPUS-030
- TASK-EXT-014

Requisitos:
- Usar documentos aprobados.
- Llamar modelo solo desde backend.
- Validar Pydantic.
- Validar ontologia.
- Incluir evidencias.
- Incluir limitaciones.
- No afirmar coordinacion sin evidencia explicita.

Criterios de aceptacion:
- 2-3 extracciones validas.
- No hay salidas LLM invalidas versionadas.

Comandos de verificacion:
- `cd hydra/backend && uv run python -m hydra_api.extraction --help`

## TASK-EXT-021: Persistir extracciones reales validadas

Estado: blocked
Prioridad: must

Bloqueo:
Depende de TASK-EXT-020.

Objetivo:
Guardar extracciones reales validadas en PostgreSQL.

Archivos permitidos:
- Ninguno

Dependencias:
- TASK-EXT-020
- TASK-EXT-011
- TASK-DB-020

Requisitos:
- Persistir solo extracciones validas.
- No guardar prompts.
- No guardar salidas invalidas.
- No borrar datos.

Criterios de aceptacion:
- Tabla `extractions` tiene filas para documentos procesados.

Comandos de verificacion:
- `docker compose exec -T postgres psql -U hydra -d hydra -c "SELECT count(*) FROM extractions;"`

## TASK-EXT-022: Revisar evidencias de extracciones reales

Estado: blocked
Prioridad: must

Bloqueo:
Depende de extracciones reales.

Objetivo:
Revisar manualmente que las extracciones reales estan fundamentadas en evidencias.

Archivos permitidos:
- `hydra/backend/data/outputs/extraction_review.md`

Dependencias:
- TASK-EXT-020

Requisitos:
- Revisar que cada afirmacion analitica importante tiene evidencia.
- Marcar limitaciones.
- Marcar cualquier afirmacion de coordinacion como invalida si no hay evidencia explicita.
- No cambiar extracciones sin tarea de repair.

Criterios de aceptacion:
- Existe revision humana/Codex de 2-3 extracciones.

Comandos de verificacion:
- `grep -n "Limitaciones" hydra/backend/data/outputs/extraction_review.md`
