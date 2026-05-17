# 05 - Evals y Observabilidad

## Langfuse

Decision: Langfuse Cloud por defecto.

Fallback:

- logs locales;
- export JSON;
- `trace_id` local.

## Trazas minimas

Cada consulta debe registrar:

- pregunta;
- parametros de retrieval;
- documentos/chunks recuperados;
- scores;
- prompt final o version de prompt;
- respuesta;
- revision del council si existe;
- latencia;
- tokens/coste si el proveedor lo devuelve;
- `trace_id`.

## Dataset minimo

Crear entre 8 y 12 casos en `hydra/back/data/evals/eval_cases.json`.

Campos:

- `id`
- `question`
- `expected_documents`
- `expected_topics`
- `expected_answer_traits`
- `tags`

## Evals obligatorios

| Eval | Metodo |
|---|---|
| Retrieval Precision@k | expected docs vs top-k |
| JSON validity | Pydantic |
| Ontology mapping | IDs validos contra YAML |
| Groundedness | LLM judge + revision humana |
| Coordination caution | regla + LLM judge |
| Latency/cost | Langfuse trace o logs locales |

## Outputs

- Langfuse Cloud scores si esta disponible.
- `hydra/back/data/outputs/eval_results.json` como backup local.
