# Documentacion HYDRA Espana Lite

Este directorio contiene la documentacion viva del proyecto.

## Documentos principales

- `hydra-analysis.md`: analisis ejecutivo de factibilidad, alcance y riesgos.
- `hydra-architecture.md`: decisiones tecnicas vigentes y fallbacks.
- `hydra-brainstorming.md`: material historico de ideacion. No es fuente de decisiones vigentes.

## SDD

La especificacion ejecutable vive en `../sdd/`.

- `../sdd/README.md`: convencion de trabajo SDD.
- `../sdd/00-product-scope.md`: alcance funcional y politica de corpus.
- `../sdd/01-architecture-decisions.md`: decisiones tecnicas resumidas para ejecucion.
- `../sdd/02-data-model.md`: metadatos, tablas y esquemas principales.
- `../sdd/03-api-contract.md`: contrato minimo entre frontend y backend.
- `../sdd/04-rag-pipeline.md`: pipeline de ingesta, embeddings, retrieval y briefing.
- `../sdd/05-evals-observability.md`: evals y trazabilidad.
- `../sdd/06-frontend-spec.md`: vistas y comportamiento de UI.
- `../sdd/07-implementation-plan.md`: fases, definition of done y verificacion.
- `../sdd/08-task-checklist.md`: indice de tareas atomicas.
- `../sdd/09-droid-execution-workflow.md`: procedimiento Codex planner -> Droid/Missions executor -> Codex reviewer.
- `../sdd/tasks/`: tareas por dominio, organizadas como `../sdd/tasks/<domain>/<domain>.md`.
- `../sdd/tasks/future-extensions/future-extensions.md`: extensiones opcionales como subida desde frontend y Neo4j como sink secundario.
