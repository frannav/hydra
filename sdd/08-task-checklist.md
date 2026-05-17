# 08 - Task Checklist

Las tareas atomicas estan separadas por dominio numerado en `tasks/` para que el editor las muestre en orden de ejecucion.

## Indice

- `tasks/00-repo-security/00-repo-security.md`
- `tasks/01-backend/01-backend.md`
- `tasks/02-database/02-database.md`
- `tasks/03-corpus/03-corpus.md`
- `tasks/04-ontology-extraction/04-ontology-extraction.md`
- `tasks/05-rag/05-rag.md`
- `tasks/06-council-briefing/06-council-briefing.md`
- `tasks/07-observability-evals/07-observability-evals.md`
- `tasks/08-frontend/08-frontend.md`
- `tasks/09-documentation/09-documentation.md`
- `tasks/10-future-extensions/10-future-extensions.md`

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

Las tareas de `tasks/10-future-extensions/10-future-extensions.md` son `could`. No deben ejecutarse antes de tener funcionando:

- backend base;
- corpus local;
- extraccion validada;
- RAG;
- briefing;
- evals minimos;
- frontend de consulta.

Neo4j y subida desde frontend deben usar los puntos de extension definidos en el SDD, sin crear pipelines paralelos.
