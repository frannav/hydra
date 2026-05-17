# 04 - RAG Pipeline

## Flujo

```text
Document source
  -> ingestion service
  -> limpieza
  -> chunking
  -> extraccion estructurada
  -> extraccion canonica validada con Pydantic
  -> sinks de persistencia
      -> PostgreSQL + pgvector
      -> export JSON
      -> proyeccion de grafo opcional
  -> retriever LangChain
  -> HYDRA Analyst
  -> briefing con evidencias
```

## Fuentes de documentos

El pipeline no debe depender de una unica fuente de entrada.

Fuentes permitidas:

- `local_corpus`: carpeta curada en `hydra/back/data/raw/` con metadatos.
- `frontend_upload`: extension opcional que envia archivo + metadatos al backend.

Ambas fuentes deben producir el mismo objeto canonico antes de limpiar, trocear o extraer:

```text
RawDocument + DocumentMetadata
```

El frontend no implementa parsing, chunking, embeddings ni extraccion.

## Sinks de salida

El pipeline no debe depender de un unico destino de persistencia.

Sinks del MVP:

- repositorio de documentos/chunks;
- vector store PostgreSQL + pgvector;
- repositorio de extracciones validadas;
- export local JSON para resultados/evals.

Sinks opcionales:

- `GraphProjection` en JSON;
- Neo4j como sink secundario de `GraphProjection`.

Regla: Neo4j no debe recibir texto libre ni salidas LLM sin validar. Solo debe consumir proyecciones derivadas del esquema Pydantic.

## Configuracion

- `top_k`: 5 por defecto.
- Embeddings: `qwen3-embedding`.
- Dimension: 4096.
- Distancia: coseno.
- Chat principal: `qwen3.6`.
- Revisor opcional: `gemma4` o `qwen3.6`.

## Reglas de respuesta

- No responder con afirmaciones analiticas si no hay contexto suficiente.
- Citar evidencias de chunks recuperados.
- Incluir limitaciones.
- Distinguir recurrencia, similitud narrativa, amplificacion y coordinacion.
- No afirmar coordinacion sin evidencia explicita.

## LLM council

Chains recomendadas:

- Narrative Analyst Chain.
- Evidence Reviewer Chain.
- Risk Reviewer Chain.
- Final Synthesizer Chain.

El council debe usarse en briefings y evals. No es obligatorio para cada documento.
