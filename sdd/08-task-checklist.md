# 08 - Task Checklist

Las tareas atomicas estan separadas por dominio en `tasks/`.

## Indice

- `tasks/repo-security/repo-security.md`
- `tasks/backend/backend.md`
- `tasks/database/database.md`
- `tasks/corpus/corpus.md`
- `tasks/ontology-extraction/ontology-extraction.md`
- `tasks/rag/rag.md`
- `tasks/council-briefing/council-briefing.md`
- `tasks/observability-evals/observability-evals.md`
- `tasks/frontend/frontend.md`
- `tasks/future-extensions/future-extensions.md`
- `tasks/documentation/documentation.md`

## Flujo de ejecucion

El procedimiento Codex planner -> Droid executor -> Codex reviewer esta definido en:

- `09-droid-execution-workflow.md`

## Regla de ejecucion

Una tarea solo puede pasar a `done` si:

- los archivos modificados estan dentro del alcance;
- se han ejecutado los comandos de verificacion;
- se cumplen los criterios de aceptacion;
- no hay secretos reales;
- no se han cambiado decisiones de arquitectura.

## Extensiones futuras

Las tareas de `tasks/future-extensions/future-extensions.md` son `could`. No deben ejecutarse antes de tener funcionando:

- backend base;
- corpus local;
- extraccion validada;
- RAG;
- briefing;
- evals minimos;
- frontend de consulta.

Neo4j y subida desde frontend deben usar los puntos de extension definidos en el SDD, sin crear pipelines paralelos.
