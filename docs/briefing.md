El briefing es el entregable analítico final de HYDRA. No es solo una respuesta del
  LLM: es una respuesta con evidencias, riesgo, revisión del council, limitaciones y
  trazabilidad.

  Consta de 4 partes a nivel API:

  {
    "briefing_markdown": "...",
    "risk_level": "bajo | medio | alto",
    "council_review": {
      "evidence_supported": true,
      "unsupported_claims": [],
      "risk_review": "..."
    },
    "trace_id": "..."
  }

  ## 1. briefing_markdown

  Es el informe final en Markdown.

  Debe incluir:

  1. Pregunta original
  2. Hallazgos principales
  3. Evidencias recuperadas
      - document_id
      - chunk_id
      - título
      - fuente
      - score
      - fragmento breve de evidencia
  4. Nivel de riesgo
  5. Limitaciones
  6. Fuentes recuperadas

  Ejemplo de estructura:

  # Briefing de inteligencia narrativa

  ## Pregunta
  ¿Hay recurrencia narrativa sobre abandono institucional?

  ## Hallazgos con evidencia
  - Se observa una recurrencia del marco narrativo X en los documentos doc_001 y
  doc_004.
  - La evidencia procede de los chunks doc_001_chunk_003 y doc_004_chunk_002.

  ## Riesgo
  Nivel: medio

  Justificación: ...

  ## Limitaciones
  - El análisis se basa únicamente en el corpus disponible.
  - No se puede afirmar coordinación sin evidencia explícita.

  ## Fuentes recuperadas
  - doc_001 / chunk_003 / Fuente X
  - doc_004 / chunk_002 / Fuente Y

  ## 2. risk_level

  Es la clasificación final del riesgo:

  bajo | medio | alto

  No puede ser texto libre.

  El riesgo debe estar justificado por evidencia recuperada, no por intuición del
  modelo.

  ## 3. council_review

  Es la revisión del LLM council.

  Incluye:

  ### evidence_supported

  Indica si las afirmaciones principales están soportadas por la evidencia.

  "evidence_supported": true

  ### unsupported_claims

  Lista claims que el council detecta como no respaldadas.

  "unsupported_claims": [
    "No hay evidencia suficiente para afirmar coordinación entre actores."
  ]

  ### risk_review

  Justificación breve del riesgo.

  "risk_review": "El riesgo medio está justificado por la recurrencia del marco
  narrativo en varias fuentes, pero no hay evidencia de coordinación."

  ## 4. trace_id

  Identificador de trazabilidad.

  Sirve para conectar el briefing con:

  - retrieval usado;
  - chunks recuperados;
  - eventos del council;
  - métricas de eval;
  - Langfuse si está activo;
  - fallback local si no hay Langfuse.

  Ejemplo:

  "trace_id": "local-abc123..."

  En resumen:

  > El briefing consta de una respuesta analítica en Markdown, un nivel de riesgo, una
  > revisión del council y un trace_id que permite auditar todo el proceso.