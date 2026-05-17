# SDD manual

No se instalara OpenSpec por ahora. El proyecto seguira un flujo de Specification-Driven Development manual basado en Markdown.

## Objetivo

Crear instrucciones suficientemente precisas para que un modelo ejecutor pueda implementar tareas sin decidir arquitectura.

## Convencion de rutas

El proyecto HYDRA vive dentro de `hydra/`. Todas las tareas, task packets y missions deben usar estas rutas completas:

- `hydra/back/` para backend, datos locales, ontologia y scripts Python.
- `hydra/front/` para frontend.
- `hydra/sdd/` para la especificacion ejecutable.
- `hydra/docs/` para documentacion estable.
- `hydra/docker-compose.yml`, `hydra/.env.example` y `hydra/README.md` para infraestructura y documentacion del entregable.

No crear `back/` ni `front/` en la raiz del workspace.

## Roles

| Rol | Responsabilidad |
|---|---|
| Planner | Define arquitectura, contratos, tareas y criterios de aceptacion |
| Executor | Implementa tareas concretas sin cambiar decisiones de arquitectura |
| Reviewer | Revisa diffs, pruebas, secretos, coherencia y criterios de aceptacion |

Codex actua como planner y reviewer. Qwen 3.6 puede actuar como executor sobre tareas cerradas.

## Formato de tarea

```markdown
## TASK-BACK-001: Crear configuracion del backend

Estado: pending
Prioridad: must
Owner sugerido: executor

Objetivo:
Crear la configuracion base del backend usando variables de entorno.

Archivos permitidos:
- hydra/back/src/hydra_api/config.py
- hydra/back/.env.example

Dependencias:
- Ninguna

Requisitos:
- Usar Pydantic Settings.
- No hardcodear secretos.
- Fallar con mensaje claro si falta una variable obligatoria.

Criterios de aceptacion:
- El comando de verificacion pasa.
- No hay API keys en codigo ni markdown.

Comandos de verificacion:
- `cd hydra/back && uv run python -m hydra_api.config`

Notas:
- No modificar frontend.
```

## Estados

- `pending`: tarea definida, no empezada.
- `in_progress`: tarea en ejecucion.
- `blocked`: tarea bloqueada con causa documentada.
- `review`: implementada, pendiente de revision.
- `done`: revisada y aceptada.

## Reglas del executor

- Implementar solo los archivos listados en `Archivos permitidos`.
- No cambiar arquitectura, modelos, stack ni nombres de variables.
- No instalar dependencias salvo que la tarea lo indique.
- No tocar secretos reales.
- No borrar ni reescribir trabajo ajeno.
- Ejecutar los comandos de verificacion definidos.
- Al terminar, reportar archivos modificados, comandos ejecutados y bloqueos.

## Ejecucion con Droid y Missions

El flujo detallado para ejecutar tareas con Droid/Qwen 3.6, tanto con task packets manuales como con Factory Missions, esta en:

- `09-droid-execution-workflow.md`

## Nomenclatura

```text
TASK-REPO-xxx    configuracion general del repo
TASK-BACK-xxx    backend
TASK-DB-xxx      base de datos
TASK-CORPUS-xxx  corpus e ingesta
TASK-ONT-xxx     ontologia
TASK-EXT-xxx     extraccion estructurada
TASK-RAG-xxx     retrieval, embeddings y pgvector
TASK-COUNCIL-xxx LLM council
TASK-BRIEF-xxx   briefings
TASK-OBS-xxx     observabilidad
TASK-EVAL-xxx    evals
TASK-FRONT-xxx   frontend
TASK-DOC-xxx     documentacion
TASK-GRAPH-xxx   extensiones de grafo / Neo4j opcional
TASK-UPLOAD-xxx  subida opcional desde frontend
```
