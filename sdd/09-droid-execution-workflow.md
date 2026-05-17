# 09 - Droid Execution Workflow

Este documento define el procedimiento de construccion cuando Codex actua como planner/reviewer y Droid, usando Qwen 3.6, actua como executor.

## Principio general

Droid no debe decidir arquitectura. Droid debe ejecutar una tarea atomica ya especificada.

La arquitectura, contratos, modelos, rutas, variables de entorno, criterios de aceptacion y archivos permitidos se deciden antes de llamar a Droid.

## Modos de ejecucion

Hay dos formas validas de trabajar con Droid:

| Modo | Uso recomendado | Riesgo | Decision |
|---|---|---|---|
| Task Packet manual | Tareas atomicas, control maximo, cambios pequenos | Mas coordinacion manual | Modo por defecto |
| Factory Missions | Milestones multi-feature con validacion por hito | Mas autonomia, posible drift si el plan no es preciso | Usar cuando el SDD este cerrado |

Missions no sustituye el SDD. Missions debe consumir nuestro SDD como fuente de verdad.

## Roles

| Rol | Responsable | Responsabilidad |
|---|---|---|
| Planner | Codex | Descompone trabajo, escribe tarea atomica, fija criterios de aceptacion |
| Executor | Droid / Qwen 3.6 | Implementa solo la tarea indicada |
| Reviewer | Codex + usuario | Revisa diff, pruebas, secretos, alcance y coherencia |
| Integrator | Codex + usuario | Decide si se acepta, corrige o divide la tarea |

## Flujo operativo

### Modo A: Task Packet manual

```text
1. Elegir siguiente tarea
2. Codex redacta task packet
3. Usuario lanza Droid en el repo
4. Usuario pega task packet a Droid
5. Droid propone/implementa cambios
6. Usuario revisa diff basico
7. Codex revisa resultado
8. Si pasa, tarea -> done
9. Si falla, Codex crea repair task
```

### Modo B: Factory Missions

Factory Missions puede ser util para ejecutar un grupo de tareas relacionadas como milestone. Segun la documentacion de Factory, Missions permite planificar y ejecutar proyectos multi-feature con orquestacion estructurada, milestones y validacion. Se inicia con `/missions` o `/mission`.

Flujo recomendado:

```text
1. Codex define mission brief desde el SDD
2. Usuario abre Droid y ejecuta /missions
3. Usuario pega mission brief
4. Droid propone plan y milestones
5. Usuario compara plan contra SDD
6. Si se ajusta, se aprueba la mission
7. Mission Control ejecuta
8. Usuario interviene si hay drift
9. Codex revisa milestone completado
```

Regla critica: no aprobar una Mission si Droid cambia arquitectura, tecnologias, rutas o prioridades del SDD.

## Paso 1: elegir tarea

La fuente de verdad es:

- `08-task-checklist.md`
- `tasks/<nn-domain>/<nn-domain>.md`

Reglas:

- Ejecutar primero tareas `must`.
- No empezar tareas que dependan de otra pendiente.
- No mezclar dominios si no hace falta.
- No pedir a Droid "implementa el backend"; pedir una tarea concreta.

## Paso 2: Codex crea el task packet

Antes de usar Droid, Codex debe generar un bloque listo para pegar.

Formato obligatorio:

```markdown
# Droid Task Packet

Task ID:
TASK-BACK-005

Title:
Crear endpoint GET /health

Context:
Estamos construyendo HYDRA Espana Lite. Sigue las decisiones de:
- hydra/docs/hydra-architecture.md
- hydra/sdd/03-api-contract.md
- hydra/sdd/tasks/01-backend/01-backend.md

Scope:
Implementa solo esta tarea.

Allowed files:
- hydra/backend/src/hydra_api/main.py
- hydra/backend/src/hydra_api/schemas.py

Do not modify:
- hydra/frontend/
- hydra/sdd/
- hydra/docs/
- archivos .env reales

Requirements:
- Crear endpoint GET /health.
- Devolver {"status": "ok", "service": "hydra-api"}.
- Mantener FastAPI simple.
- No introducir secretos.

Acceptance criteria:
- El endpoint responde con status 200.
- La respuesta coincide con el contrato.
- No se modifican archivos fuera de alcance.

Verification commands:
- cd hydra/backend && uv run fastapi dev src/hydra_api/main.py

Report back:
- Archivos modificados.
- Comandos ejecutados.
- Resultado de verificacion.
- Cualquier bloqueo.
```

## Mission brief

Cuando se use `/missions`, Codex debe crear un mission brief. No debe ser una peticion abierta como "construye HYDRA". Debe limitar milestones, fuentes de verdad y criterios de validacion.

Formato recomendado:

```markdown
# Droid Mission Brief

Mission:
Construir el bloque Backend Base de HYDRA Espana Lite.

Source of truth:
- hydra/docs/hydra-architecture.md
- hydra/sdd/01-architecture-decisions.md
- hydra/sdd/03-api-contract.md
- hydra/sdd/tasks/01-backend/01-backend.md

Non-negotiable decisions:
- Backend Python con uv.
- FastAPI.
- No cambiar modelos ni arquitectura.
- No tocar frontend.
- No crear ni modificar .env reales.
- No hardcodear secretos.

Milestone 1:
Implementar TASK-BACK-001 a TASK-BACK-005.

Milestone 2:
Implementar TASK-BACK-006 a TASK-BACK-010.

Validation after each milestone:
- Revisar archivos modificados.
- Ejecutar comandos de verificacion.
- Confirmar que no hay secretos.
- Confirmar que no se modifican archivos fuera de alcance.

Allowed files:
- hydra/backend/pyproject.toml
- hydra/backend/uv.lock
- hydra/backend/src/hydra_api/**
- hydra/backend/.env.example

Forbidden:
- hydra/frontend/**
- hydra/docs/**
- hydra/sdd/**
- .env reales

Stop conditions:
- Necesitas cambiar arquitectura.
- Necesitas tocar archivos fuera de alcance.
- Falla una decision del SDD.
- No puedes ejecutar una verificacion.
```

## Cuando usar Missions

Usar Missions para:

- backend base completo;
- base de datos + RAG si el contrato ya esta cerrado;
- frontend minimo si la API ya existe;
- evals + observabilidad si los endpoints ya funcionan.

No usar Missions para:

- decidir arquitectura;
- investigar opciones tecnologicas;
- tareas con secretos;
- cambios que mezclen demasiados dominios;
- fases donde aun no sabemos el contrato exacto.

## Milestones recomendados para Missions

| Mission | Milestones | Fuente SDD |
|---|---|---|
| Repo setup | seguridad, estructura, env examples | `tasks/00-repo-security/` |
| Backend base | uv/FastAPI/config/health/CORS/errors | `tasks/01-backend/` |
| DB + corpus | pgvector/tablas/metadata/chunking | `tasks/02-database/`, `tasks/03-corpus/` |
| RAG core | embeddings/retriever/query/evidencias | `tasks/05-rag/` |
| Evals + observability | Langfuse/eval cases/scores | `tasks/07-observability-evals/` |
| Frontend | layout/vistas/query/evidencias/evals | `tasks/08-frontend/` |
| Future extensions | upload frontend, GraphProjection, Neo4j sink | `tasks/10-future-extensions/` |

Cada Mission debe tener validacion al final de cada milestone.

## Paso 3: ejecutar Droid

Segun la documentacion de Factory, Droid CLI se instala en macOS/Linux con:

```bash
curl -fsSL https://app.factory.ai/cli | sh
```

Despues:

```bash
cd /path/to/repo
droid
```

En la sesion interactiva:

- pegar el task packet;
- revisar el plan que proponga Droid;
- aprobar solo si respeta archivos permitidos y criterios;
- usar `/model` si hay que confirmar o cambiar modelo;
- usar `/review` cuando haya cambios listos para revisar.

## Paso 4: reglas para Droid

Cada prompt a Droid debe incluir estas restricciones:

- No cambies arquitectura.
- No cambies decisiones de stack.
- No modifiques archivos fuera de `Allowed files`.
- No crees ni edites `.env` reales.
- No hardcodees API keys.
- No instales dependencias salvo que la tarea lo indique.
- Si necesitas modificar otro archivo, detente y explica por que.
- Si una verificacion no puede ejecutarse, reportalo.

## Paso 5: revision despues de Droid

Despues de que Droid implemente, el usuario debe traer a Codex:

- diff o resumen de archivos modificados;
- salida de comandos;
- errores;
- si Droid cambio archivos fuera de alcance.

Codex revisa:

- criterios de aceptacion;
- secretos;
- coherencia con arquitectura;
- rutas;
- contratos API;
- que no haya sobreimplementacion;
- que no se hayan anadido dependencias innecesarias.

## Paso 6: estados de tarea

- Si todo pasa: marcar tarea como `done`.
- Si hay errores pequenos: crear repair task.
- Si Droid cambio arquitectura: revertir o aislar cambios antes de continuar.
- Si la tarea era demasiado grande: dividirla en subtareas.

## Repair task

Si Droid falla, no se le debe pedir "arreglalo" de forma generica. Codex debe crear un repair packet:

```markdown
# Droid Repair Packet

Original task:
TASK-BACK-005

Problem:
El endpoint devuelve service="api" en lugar de "hydra-api".

Allowed files:
- hydra/backend/src/hydra_api/main.py

Fix:
Cambiar solo el valor de service.

Verification:
- Probar GET /health.
```

## Batch size

Recomendacion:

- 1 task packet por ejecucion de Droid.
- Maximo 2-3 tareas si son triviales y del mismo dominio.
- No mezclar frontend + backend + DB en el mismo prompt.
- No pedir a Droid que haga planificacion general.

Si se usa Missions:

- 1 mission por dominio o bloque cohesivo.
- 2-3 milestones maximo por mission para el MVP.
- Validacion obligatoria por milestone.
- Pausar la mission si aparece drift.

## Orden recomendado de construccion

1. Repo y seguridad.
2. Backend base.
3. Database.
4. Corpus.
5. Ontologia y extraccion.
6. RAG.
7. Observabilidad.
8. Evals.
9. Briefing/council.
10. Frontend.
11. Documentacion y demo.
12. Extensiones opcionales: upload frontend, GraphProjection, Neo4j sink.

## Prompts prohibidos

No usar:

```text
Implementa todo el backend.
Construye el proyecto entero.
Haz lo que veas necesario.
Arregla todos los errores.
Refactoriza la arquitectura.
```

Usar:

```text
Implementa TASK-BACK-005 siguiendo este task packet.
No modifiques archivos fuera de Allowed files.
Si necesitas cambiar alcance, detente y pregunta.
```

Para Missions, usar:

```text
/missions

Usa este Mission Brief. No cambies arquitectura ni tecnologias.
Si tu plan difiere del SDD, detente y pregunta.
```

## Criterio de avance

No se empieza una nueva tarea si:

- la anterior no esta revisada;
- hay cambios sin entender;
- hay secretos en diff;
- los comandos de verificacion fallan;
- Droid modifico archivos fuera de alcance.

## Uso de Git

Recomendacion:

- commit pequeno por tarea o grupo pequeno de tareas relacionadas;
- mensaje con task ID;
- revisar `git diff` antes de commit;
- no commitear `.env`, outputs pesados ni datos sensibles.

Ejemplo:

```bash
git add hydra/backend/src/hydra_api/main.py
git commit -m "TASK-BACK-005 add health endpoint"
```
