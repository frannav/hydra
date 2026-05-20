  ## 1. Evals: cómo los vamos a hacer

  La idea no es “probar si el modelo responde bonito”, sino medir si HYDRA es trazable,
  grounded y prudente.

  Ya está alineado en SDD con:

  - sdd/evals-observability.md
  - sdd/tasks/07-observability-evals/07-observability-evals.md
  - código actual en:
      - backend/src/hydra_api/evals_service.py
      - backend/src/hydra_api/evals_metrics.py
      - backend/src/hydra_api/evals_judges.py
      - backend/src/hydra_api/observability.py

  ### Capas de evaluación

  Haremos 4 niveles:

  ### A. Evals deterministas offline

  Sin modelo real, sin Langfuse real, sin DB viva.

  Sirven para validar que el sistema no se rompe:

  - EvalRunRequest válido.
  - carga segura de eval_cases.json.
  - rutas seguras sin ...
  - export local a backend/data/outputs/eval_results.json.
  - métricas calculadas sin red.

  ### B. Evals de retrieval

  Dataset cerrado de 8-12 preguntas en:

  backend/data/evals/eval_cases.json

  Cada caso tendrá:

  {
    "id": "eval_001",
    "question": "...",
    "expected_documents": ["doc_001"],
    "expected_topics": ["..."],
    "expected_answer_traits": ["..."],
    "tags": ["retrieval", "groundedness"]
  }

  Métrica principal:

  - documento esperado aparece en top-k;
  - idealmente añadiremos también Recall@k o corregiremos la actual métrica si queremos
    ser estrictos con la definición académica de Precision@k.

  ### C. Evals de calidad analítica

  Mediremos:

  - groundedness: si la respuesta está soportada por evidencias;
  - coordination_caution: si evita afirmar coordinación/intención/atribución sin
    evidencia explícita;
  - json_validity: para salidas estructuradas;
  - ontology_mapping: IDs válidos contra la ontología;
  - limitaciones: si declara límites cuando no hay evidencia.

  Aquí el TFM gana mucho, porque conecta directamente con el objetivo del proyecto:
  inteligencia narrativa trazable, no generación libre.

  ### D. Evals reales finales

  Bloqueados hasta tener:

  - corpus cerrado aprobado;
  - IDs de documentos estables;
  - DB local con chunks/embeddings;
  - modelo configurado;
  - Langfuse opcional;
  - aprobación para coste/red.

  Esto corresponde a:

  - TASK-EVAL-014: crear eval_cases.json real.
  - TASK-EVAL-015: ejecutar evals reales.
  - TASK-OBS-008: verificar trazas reales en Langfuse.

  ———

  ## 2. Observabilidad: cómo la vamos a hacer

  La observabilidad no será solo logs. Será parte del contrato del producto.

  Cada endpoint analítico devuelve trace_id:

  - POST /query
  - POST /briefing
  - POST /evals/run

  La decisión SDD es:

  Langfuse Cloud por defecto.
  Fallback: trace_id local + JSON local.

  ### Qué trazamos

  Para cada consulta:

  - pregunta recortada, no completa si es sensible;
  - top_k;
  - documentos/chunks recuperados;
  - scores;
  - número de resultados;
  - versión de prompt, no prompt completo;
  - respuesta resumida, no respuesta completa si puede contener contenido sensible;
  - eventos del council;
  - métricas de eval;
  - latencia/coste si el proveedor lo devuelve;
  - trace_id.

  ### Qué NO trazamos

  Muy importante para TFM y seguridad:

  - claves;
  - headers;
  - prompts completos;
  - documentos completos;
  - respuestas completas sensibles;
  - stack traces;
  - contenido del corpus entero.

  ### Fallback local

  Si no hay Langfuse o falla:

  - el sistema no se cae;
  - genera local-<uuid>;
  - exporta resultados a:

  backend/data/outputs/eval_results.json

  Eso nos permite demostrar robustez: la observabilidad no es dependencia crítica para
  que HYDRA responda.

  ———

  ## 3. LLM Council: cómo lo realizamos

  El council no será un sistema de agentes autónomos. Según el SDD, debe ser:

  chains secuenciales con roles

  Implementado en:

  - backend/src/hydra_api/council_prompts.py
  - backend/src/hydra_api/council_service.py
  - backend/src/hydra_api/briefing_service.py

  ### Flujo del council

  Para POST /briefing con use_council=true:

  Pregunta
    ↓
  RAG / QueryService
    ↓
  Documentos recuperados + evidencias
    ↓
  Narrative Analyst
    ↓
  Evidence Reviewer
    ↓
  Risk Reviewer
    ↓
  Final Synthesizer
    ↓
  Briefing final + CouncilReview + trace_id

  ### Roles

  #### 1. Narrative Analyst

  Produce un borrador grounded usando solo evidencias recuperadas.

  Reglas:

  - no inventar actores/eventos;
  - no afirmar coordinación sin evidencia explícita;
  - citar documentos/chunks;
  - declarar limitaciones.

  #### 2. Evidence Reviewer

  Revisa si el borrador está soportado.

  Devuelve:

  {
    "evidence_supported": true,
    "unsupported_claims": [],
    "risk_review": "..."
  }

  #### 3. Risk Reviewer

  Clasifica riesgo solo en:

  bajo | medio | alto

  Y debe justificarlo con evidencia.

  #### 4. Final Synthesizer

  Construye el briefing final en Markdown:

  - pregunta;
  - hallazgos;
  - evidencias;
  - riesgo;
  - limitaciones;
  - fuentes recuperadas.

  También elimina o marca claims no soportadas.

  ———

  ## 4. Punto fuerte para el TFM

  La narrativa del TFM debería ser:

  > HYDRA no intenta maximizar fluidez generativa, sino trazabilidad analítica. Cada
  > respuesta queda vinculada a evidencias, traces, métricas y revisiones de un council
  > especializado.

  Eso nos permite defender:

  - reproducibilidad;
  - trazabilidad;
  - control de alucinaciones;
  - prudencia analítica;
  - evaluación medible;
  - observabilidad profesional.

  ———

  ## 5. Próximos pasos recomendados

  1. Cerrar corpus real aprobado.
  2. Asegurar IDs estables de documentos y chunks.
  3. Crear eval_cases.json con 8-12 casos reales.
  4. Ejecutar /evals/run.
  5. Ver eval_results.json.
  6. Activar Langfuse con .env local.
  7. Ejecutar smoke real de /query, /briefing y evals.
  8. Sacar para el TFM:
      - tabla de evals;
      - captura de Langfuse;
      - ejemplo de trace_id;
      - ejemplo de council detectando claims no soportadas;
      - comparación con/sin council.