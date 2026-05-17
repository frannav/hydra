# Tasks - RAG

## TASK-RAG-001: Crear embeddings

Estado: pending  
Prioridad: must

Modelo:
- `qwen3-embedding`

## TASK-RAG-002: Fijar dimension 4096

Estado: pending  
Prioridad: must

Criterios:
- pgvector usa `vector(4096)`.

## TASK-RAG-003: Insertar chunks embebidos

Estado: pending  
Prioridad: must

## TASK-RAG-004: Crear retriever LangChain

Estado: pending  
Prioridad: must

Requisitos:
- Usar PGVector.
- `top_k` configurable.

## TASK-RAG-005: Crear endpoint POST /query

Estado: pending  
Prioridad: must

Contrato:
- Ver `../../03-api-contract.md`.

## TASK-RAG-006: Devolver documentos y scores

Estado: pending  
Prioridad: must

## TASK-RAG-007: Generar respuesta con evidencias

Estado: pending  
Prioridad: must

Requisitos:
- Incluir fragmentos usados.
- Incluir limitaciones.

## TASK-RAG-008: Bloquear respuestas sin contexto suficiente

Estado: pending  
Prioridad: must

Requisitos:
- Si retrieval no devuelve contexto util, responder con limitacion y no inventar.
