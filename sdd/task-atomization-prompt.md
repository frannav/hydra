# Task Atomization Prompt

Prompt reutilizable para pedir a Codex que revise una carpeta de tareas SDD y la prepare para ejecucion con Droid/Qwen.

Uso recomendado:

```markdown
Usa el prompt de `sdd/task-atomization-prompt.md` para revisar y atomizar:
`sdd/tasks/<NN-domain>/`
```

## Prompt

```markdown
Revisa las tareas SDD de una carpeta concreta y reescribelas para que sean lo mas atomicas, ejecutables y resistentes a errores posible.

Carpeta a revisar:
`sdd/tasks/<NN-domain>/`

Objetivo:
Quiero preparar estas tasks para que Droid/Qwen pueda ejecutarlas con minima ambiguedad, sin decidir arquitectura y sin repetir los errores que ya vimos en missions anteriores.

Instrucciones:

1. Lee solo la documentacion SDD relevante:
   - `sdd/README.md`
   - `sdd/01-architecture-decisions.md`
   - `sdd/02-data-model.md` si aplica
   - `sdd/03-api-contract.md` si aplica
   - `sdd/rag-pipeline.md` si aplica
   - `sdd/07-implementation-plan.md`
   - `sdd/08-task-checklist.md`
   - el archivo de tasks de la carpeta indicada

2. No cambies arquitectura, stack, contratos API, nombres de variables de entorno, modelos ni decisiones SDD sin preguntarme.

3. Reescribe las tasks para que cada una sea:
   - pequena;
   - verificable con comandos concretos;
   - con archivos permitidos explicitos;
   - con dependencias claras;
   - con criterios de aceptacion objetivos;
   - sin mezclar responsabilidades;
   - sin requerir decisiones humanas implicitas;
   - sin depender de documentos, servicios o datos que todavia no existan.

4. Incorpora aprendizajes de repairs anteriores:
   - comprobar que el codigo coincide con schemas/tablas existentes;
   - evitar path traversal y rutas absolutas inseguras;
   - no saltarse helpers de validacion;
   - no aceptar silenciosamente manifests incompletos;
   - no resetear estados existentes por accidente en upserts;
   - no crear documentacion que apunte a secciones inexistentes;
   - no modificar archivos fuera del allowed scope;
   - separar cambios SDD, implementacion y repairs;
   - mantener dry-run sin conexiones externas;
   - no introducir dependencias nuevas salvo que la task lo diga;
   - no llamar modelos, embeddings, Langfuse, DB o servicios externos salvo que la task lo requiera;
   - no imprimir secretos, headers, stack traces ni contenido completo de documentos;
   - no tocar frontend si la task es backend/core;
   - no crear `.env` reales;
   - no versionar documentos reales salvo aprobacion explicita.

5. Anade para cada bloque:
   - `Errores probables a evitar`
   - `Edge cases obligatorios`
   - `Stop conditions`
   - `Comandos de verificacion`

6. Si hay tasks demasiado grandes, dividelas en varias tasks nuevas.
   Manten la nomenclatura del dominio:
   - `TASK-BACK-xxx`
   - `TASK-DB-xxx`
   - `TASK-CORPUS-xxx`
   - `TASK-ONT-xxx`
   - `TASK-EXT-xxx`
   - `TASK-RAG-xxx`
   - etc.

7. Si hay tasks bloqueadas por datos reales, claves, corpus aprobado, DB viva o decisiones humanas, dejalas como `blocked` y explica el bloqueo.

8. Si detectas contradicciones con el SDD, no las resuelvas silenciosamente:
   - explica la contradiccion;
   - propone la correccion;
   - espera confirmacion si cambia arquitectura o contrato.

9. Al final, crea o actualiza tambien un mission brief para Droid en la misma carpeta:
   - `sdd/tasks/<NN-domain>/<NN-domain>-mission.md`
   con:
   - objetivo;
   - source of truth;
   - allowed files;
   - forbidden files;
   - milestones;
   - checks por milestone;
   - stop conditions;
   - final report format.

10. No marques tasks como `done`.
    Dejalas en `pending`, salvo las que dependan de datos o decisiones futuras, que deben quedar `blocked`.

Antes de editar, haz un breve plan de que archivos vas a tocar.
Despues de editar, muestra:
- resumen de cambios;
- tasks divididas o anadidas;
- edge cases incorporados;
- posibles puntos de error cubiertos;
- comandos de verificacion recomendados;
- `git diff --stat`.
```

## Ejemplos

```markdown
Usa el prompt de `sdd/task-atomization-prompt.md` para revisar y atomizar:
`sdd/tasks/05-rag/`
```

```markdown
Usa el prompt de `sdd/task-atomization-prompt.md` para revisar y atomizar:
`sdd/tasks/06-council-briefing/`
```

