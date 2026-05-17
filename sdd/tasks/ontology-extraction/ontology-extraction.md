# Tasks - Ontologia y extraccion

## TASK-ONT-001: Crear ontologia ligera

Estado: pending  
Prioridad: must

Archivos permitidos:
- `hydra/backend/ontology/hydra_ontology.yaml`

## TASK-ONT-002: Crear loader de ontologia

Estado: pending  
Prioridad: must

Archivos permitidos:
- `hydra/backend/src/hydra_api/ontology.py`

## TASK-ONT-003: Validar IDs permitidos

Estado: pending  
Prioridad: must

Requisitos:
- Fallar si el LLM devuelve categorias fuera de vocabulario cuando el campo exige ID controlado.

## TASK-EXT-001: Crear prompt de extraccion estructurada

Estado: pending  
Prioridad: must

Requisitos:
- Incluir instruccion de no afirmar coordinacion sin evidencia.
- Incluir ontologia ligera.

## TASK-EXT-002: Integrar structured output con Pydantic

Estado: pending  
Prioridad: must

Requisitos:
- Validar JSON.
- Reintentar o marcar error si la salida es invalida.

## TASK-EXT-003: Extraer 2-3 documentos de prueba

Estado: pending  
Prioridad: must

Criterios:
- Salidas validas.
- Evidencias presentes.

## TASK-EXT-004: Guardar extracciones validadas

Estado: pending  
Prioridad: must

Requisitos:
- Persistir en DB.
- Export opcional JSON.

## TASK-EXT-005: Crear proyeccion de grafo desde extraccion validada

Estado: pending  
Prioridad: should

Objetivo: dejar preparado un artefacto intermedio para grafo sin introducir Neo4j como dependencia core.

Archivos permitidos:
- `hydra/backend/src/hydra_api/schemas.py`
- `hydra/backend/src/hydra_api/graph_projection.py`

Requisitos:
- Generar `GraphProjection` desde una extraccion Pydantic valida.
- Incluir nodos, edges y referencias a evidencias.
- No generar relaciones sin evidencia.
- No llamar a Neo4j.
- No depender de un driver de grafo.

Criterios de aceptacion:
- La proyeccion puede exportarse como JSON.
- Un sink futuro de Neo4j podria consumirla sin cambiar la extraccion.
