# Tasks - Frontend

## TASK-FRONT-001: Inicializar frontend con pnpm

Estado: pending  
Prioridad: must

Archivos permitidos:
- `hydra/front/package.json`
- `hydra/front/pnpm-lock.yaml`

## TASK-FRONT-002: Configurar Tailwind

Estado: pending  
Prioridad: must

## TASK-FRONT-003: Crear layout base

Estado: pending  
Prioridad: must

## TASK-FRONT-004: Crear navegacion

Estado: pending  
Prioridad: must

## TASK-FRONT-005: Crear vista Corpus

Estado: pending  
Prioridad: must

## TASK-FRONT-006: Crear vista Narrativas

Estado: pending  
Prioridad: must

## TASK-FRONT-007: Crear vista HYDRA Analyst

Estado: pending  
Prioridad: must

## TASK-FRONT-008: Mostrar respuesta estructurada

Estado: pending  
Prioridad: must

## TASK-FRONT-009: Mostrar evidencias

Estado: pending  
Prioridad: must

## TASK-FRONT-010: Mostrar trace_id

Estado: pending  
Prioridad: must

## TASK-FRONT-011: Crear vista Evals

Estado: pending  
Prioridad: must

## TASK-FRONT-012: Manejar loading y errores

Estado: pending  
Prioridad: must

## TASK-FRONT-013: Subida de documentos desde UI

Estado: pending  
Prioridad: could

Objetivo: permitir subida manual de documentos solo si el pipeline principal ya funciona.

Dependencias:
- `POST /documents/upload` implementado en backend.
- Servicio de ingesta desacoplado.

Requisitos:
- Formulario de archivo + metadatos minimos.
- Soportar inicialmente `.txt`, `.md` o `.csv`.
- Enviar archivo y metadatos al backend.
- Mostrar estado de procesamiento.
- No parsear documentos en frontend.
- No hacer chunking, embeddings ni llamadas a modelos desde frontend.
- No exponer claves ni endpoints privados.

Criterios de aceptacion:
- La UI usa el mismo pipeline backend que el corpus local.
- Si el backend rechaza metadatos o formato, se muestra error seguro.
