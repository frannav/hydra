Funciona en 3 capas:

  Ontología
    ↓
  Extracción estructurada
    ↓
  Proyección de grafo

  La idea clave es:

  > El modelo no produce conocimiento libre directamente. Produce una extracción JSON
  > que debe pasar por Pydantic y por la ontología antes de poder usarse para RAG,
  > briefing, evals o grafo.

  ———

  # 1. Ontology

  La ontología está en:

  backend/ontology/hydra_ontology.yaml

  No es una base de conocimiento factual. Es un vocabulario controlado ligero.

  Es decir, no guarda hechos como:

  "Actor X hizo Y"

  Guarda categorías permitidas:

  narrative_frames:
    - id: isolated_incident
    - id: pattern_of_behavior
    - id: coordinated_campaign
    - id: unknown_or_insufficient_evidence

  actor_types:
    - id: government_agency
    - id: media_outlet
    - id: civil_society

  affected_sectors:
    - id: defense
    - id: economy
    - id: political_institutions

  threat_types:
    - id: information_manipulation
    - id: cyber_threat

  Sirve para evitar que el modelo invente etiquetas nuevas.

  Por ejemplo, esto sería válido:

  "narrative_frame_id": "isolated_incident"

  Pero esto fallaría:

  "narrative_frame_id": "mega_campaign_fake"

  porque no existe en la ontología.

  ———

  # 2. Extraction

  La extracción convierte un documento en un JSON estructurado.

  El esquema está en Extraction:

  class Extraction(BaseModel):
      document_id: str
      title: str
      source: str
      date: str | None
      main_topic: str | None
      main_narrative: str | None
      narrative_frame_id: str | None
      secondary_narratives: list[str]
      actors: list[Actor]
      actor_types: list[str]
      locations: list[Location]
      events: list[Event]
      affected_sectors: list[str]
      threat_types: list[str]
      risk_level: RiskLevel
      confidence: Confidence
      evidence_fragments: list[EvidenceFragment]
      analyst_summary: str | None
      limitations: list[str]
      schema_version: str

  El flujo esperado es:

  RawDocument
    ↓
  build_extraction_prompt()
    ↓
  modelo LLM
    ↓
  JSON de extracción
    ↓
  parse_extraction_json()
    ↓
  Pydantic Extraction
    ↓
  validate_extraction_against_ontology()
    ↓
  save_extraction() / export_extraction_json()

  Ejemplo de extracción:

  {
    "document_id": "doc_001",
    "title": "Informe sobre seguridad regional",
    "source": "Fuente X",
    "main_topic": "Seguridad regional",
    "main_narrative": "El documento describe un incidente aislado.",
    "narrative_frame_id": "isolated_incident",
    "actors": [
      {
        "name": "Entidad A",
        "actor_type": "government_agency"
      }
    ],
    "actor_types": ["government_agency"],
    "affected_sectors": ["defense"],
    "threat_types": ["information_manipulation"],
    "risk_level": "medio",
    "confidence": "media",
    "evidence_fragments": [
      {
        "text": "Fragmento que justifica la extracción.",
        "source_document_id": "doc_001",
        "relevance": "high"
      }
    ],
    "limitations": [
      "No hay evidencia suficiente para afirmar coordinación."
    ]
  }

  ## Reglas importantes

  La extracción debe:

  - devolver JSON puro;
  - no usar Markdown;
  - incluir evidencias;
  - incluir limitaciones;
  - usar IDs de la ontología;
  - no afirmar coordinación sin evidencia explícita;
  - no inventar actores, eventos o relaciones.

  Ahora mismo, la parte real de llamar al modelo sobre corpus real está bloqueada hasta
  tener corpus aprobado y claves/modelo. Lo que sí tenemos preparado es:

  - prompt builder;
  - parser JSON;
  - validación Pydantic;
  - validación contra ontología;
  - export JSON;
  - persistencia en tabla extractions.

  ———

  # 3. Grafo

  El grafo no se construye desde texto libre.

  Se construye desde una Extraction ya validada.

  Extraction validada
    ↓
  build_graph_projection()
    ↓
  GraphProjection JSON

  El esquema es:

  class GraphProjection(BaseModel):
      document_id: str
      nodes: list[GraphNode]
      edges: list[GraphEdge]
      evidence_refs: list[str]
      schema_version: str

  ## Nodos posibles

  Document
  Actor
  NarrativeFrame
  Location
  Event
  Sector
  ThreatType

  Ejemplo:

  {
    "id": "doc_xxx",
    "type": "Document",
    "label": "Informe sobre seguridad regional"
  }

  {
    "id": "actor_xxx",
    "type": "Actor",
    "label": "Entidad A"
  }

  ## Relaciones posibles

  MENTIONS
  HAS_NARRATIVE
  OCCURS_IN
  AFFECTS
  SUPPORTED_BY

  En la implementación actual se crean relaciones como:

  Document --HAS_NARRATIVE--> NarrativeFrame
  Document --MENTIONS--> Actor
  Document --MENTIONS--> Location
  Document --MENTIONS--> Event
  Document --AFFECTS--> Sector
  Document --AFFECTS--> ThreatType

  Pero solo se crean edges si hay evidencia.

  Si una extracción no tiene evidence_fragments, entonces:

  edges = []

  Esto es importante: no queremos un grafo lleno de relaciones inventadas.

  ———

  # 4. Evidence refs

  El grafo no mete el texto completo de la evidencia dentro de las relaciones.

  En lugar de eso usa evidence_refs:

  {
    "source": "doc_xxx",
    "target": "actor_xxx",
    "type": "MENTIONS",
    "evidence_refs": ["ev_abc123"]
  }

  Eso permite decir:

  > Esta relación existe porque hay una evidencia asociada.

  Pero sin duplicar textos completos ni convertir evidencia en nodo propio.

  ———

 # 4. ¿Dónde entra el LLM Council?

  El LLM council entra después de tener información estructurada y evidencias, no antes.

  Flujo completo:

  Documento raw
    ↓
  Chunking
    ↓
  Extracción estructurada
    ↓
  Validación Pydantic
    ↓
  Validación contra ontología
    ↓
  GraphProjection / RAG / evidencias
    ↓
  LLM Council
    ↓
  Briefing final

  ## Qué NO hace el council

  El council no decide la ontología.

  No hace esto:

  "Voy a inventar una nueva categoría narrativa"

  Tampoco valida técnicamente el JSON. Eso lo hacen:

  Pydantic + ontology.py

  Tampoco construye directamente el grafo. Eso lo hace:

  graph_projection.py

  El grafo se deriva de extracciones ya validadas.

  ———

  ## Qué SÍ hace el council

  El council revisa la interpretación analítica.

  Por ejemplo:

  ¿La respuesta está soportada por evidencia?
  ¿El riesgo está bien justificado?
  ¿Hay claims no soportadas?
  ¿Se está afirmando coordinación sin evidencia explícita?
  ¿El briefing final debe rebajar una conclusión?

  Es decir, el council entra cuando ya tenemos:

  - chunks recuperados;
  - evidencias;
  - posibles extracciones;
  - narrative frames;
  - actores;
  - riesgo preliminar;
  - limitaciones.

  ———

  # 4.1. Council en extracción

  En la extracción documental básica, lo que hay es:

  LLM extractor
    ↓
  JSON
    ↓
  Pydantic
    ↓
  Ontología

  Eso no es todavía el council.

  Es simplemente un modelo generando una extracción estructurada.

  El council podría usarse en el futuro para revisar extracciones, por ejemplo:

  Extraction Reviewer:
    - ¿La extracción está soportada por evidence_fragments?
    - ¿El narrative_frame_id está justificado?
    - ¿El risk_level es prudente?
    - ¿Hay claims de coordinación injustificados?

  Pero en el MVP actual, la función principal del council está en el briefing, no en
  cada extracción individual.

  ———

  # 4.2. Council en el briefing

  Aquí es donde realmente entra.

  Después de hacer retrieval y recuperar evidencias, el briefing pasa por 4 roles:

  Narrative Analyst
    ↓
  Evidence Reviewer
    ↓
  Risk Reviewer
    ↓
  Final Synthesizer

  ## 1. Narrative Analyst

  Crea un borrador analítico usando la evidencia.

  Pregunta + chunks recuperados + extracciones relevantes
    ↓
  borrador de respuesta

  ## 2. Evidence Reviewer

  Revisa si el borrador está soportado.

  Detecta cosas como:

  "Esta afirmación no aparece en los documentos"
  "Esto es una inferencia demasiado fuerte"
  "No hay evidencia para afirmar coordinación"

  ## 3. Risk Reviewer

  Evalúa el riesgo:

  bajo | medio | alto

  Pero tiene que justificarlo con evidencia.

  ## 4. Final Synthesizer

  Construye el briefing final:

  hallazgos
  evidencias
  riesgo
  limitaciones
  fuentes
  claims no soportadas

  ———

  # 4.3. Council y grafo

  El council no construye el grafo directamente.

  Esto sería peligroso:

  LLM Council
    ↓
  "crea nodos y relaciones"
    ↓
  grafo

  Porque el modelo podría inventar relaciones.

  Lo correcto es:

  Extraction validada
    ↓
  GraphProjection determinista
    ↓
  opcional: council revisa interpretación del grafo

  Por ejemplo, el council puede ayudar a responder:

  ¿Este patrón de relaciones permite hablar de recurrencia?
  ¿Hay evidencia suficiente para decir que varios actores comparten narrativa?
  ¿O solo hay similitud temática?

  Pero no debería crear edges libremente.

  ———

  # 4.4. Diferencia importante

  Hay que separar tres cosas:

  ┌────────────┬──────────────────────────────┬────────────────────────────┐
  │ Capa       │ Función                      │ Quién decide               │
  ├────────────┼──────────────────────────────┼────────────────────────────┤
  │ Ontología  │ Qué categorías existen       │ YAML controlado            │
  │ Extracción │ Qué aparece en un documento  │ LLM + Pydantic + ontología │
  │ Grafo      │ Cómo proyectar la extracción │ Código determinista        │
  │ Council    │ Cómo interpretar evidencias  │ LLM reviewers              │
  └────────────┴──────────────────────────────┴────────────────────────────┘

  ———

  # Resumen corto

  El LLM council entra después de la extracción y del retrieval, principalmente en el
  briefing.

  No reemplaza las validaciones deterministas.

  Su papel es revisar la interpretación:

  ¿Está soportado?
  ¿Es prudente?
  ¿Hay evidencia?
  ¿El riesgo está justificado?
  ¿Se está afirmando coordinación sin base?

  Frase para el TFM:

  > El LLM council no actúa como fuente primaria de verdad ni como constructor directo
  > del grafo. Opera como una capa de revisión analítica sobre evidencias y extracciones
  > ya validadas, reduciendo claims no soportadas y reforzando la trazabilidad del
  > briefing final.


  # 5. Neo4j

  Neo4j no es dependencia core del MVP.

  La decisión actual es:

  GraphProjection JSON primero.
  Neo4j opcional después.

  Es decir:

  Extraction validada
    ↓
  GraphProjection JSON
    ↓
  opcional futuro: sink Neo4j

  Esto mantiene el MVP simple y defendible.

  ———

  # Resumen

  Ontology:
    vocabulario controlado

  Extraction:
    JSON analítico validado con Pydantic + ontología

  Graph:
    proyección derivada de la extracción validada, con evidence_refs

  La frase clave para el TFM sería:

  > HYDRA no construye el grafo directamente desde salidas libres del modelo. Primero
  > valida una extracción estructurada contra un esquema Pydantic y una ontología
  > controlada; solo después deriva una proyección de grafo trazable mediante
  > referencias de evidencia.