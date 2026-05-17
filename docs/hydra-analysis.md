# Analisis de factibilidad de HYDRA Espana Lite

Fecha de analisis: 16 de mayo de 2026  
Horizonte de entrega asumido: antes del miercoles 20 de mayo de 2026

## Veredicto ejecutivo

El MVP es factible para antes del miercoles 20 de mayo de 2026, pero solo si se construye como una prueba funcional acotada: corpus cerrado, dominio unico, pipeline precomputado, interfaz web sencilla y respuestas siempre apoyadas en evidencias del corpus.

No es factible en ese plazo si se intenta construir una plataforma OSINT completa con scraping, tiempo real, redes sociales, atribucion de campanas coordinadas, dashboard avanzado, Neo4j, autenticacion, despliegue robusto o evaluacion extensiva.

La version defendible para el TFM debe ser:

> HYDRA Espana Lite: sistema RAG para analisis de inteligencia narrativa en fuentes publicas sobre amenazas hibridas, aplicado a un corpus cerrado de documentos.

La clave es venderlo como sistema de apoyo al analista, no como detector automatico de verdad, propaganda o coordinacion.

## Supuestos de factibilidad

Este analisis asume:

- Plazo real de trabajo: desde sabado 16 de mayo hasta martes 19 de mayo, dejando el miercoles 20 como margen de revision, defensa o entrega.
- Dedicacion alta: al menos 6-8 horas efectivas por dia.
- Uso de Python con `uv`, FastAPI, Pydantic, LangChain, PostgreSQL con pgvector y Langfuse Cloud.
- Uso de `pnpm` obligatorio para el frontend.
- Frontend y backend en el mismo repositorio, separados en `hydra/front/` y `hydra/back/`.
- Uso de una API de modelos disponible y estable para extraccion, embeddings y generacion. La implementacion debe quedar desacoplada del proveedor concreto mediante variables de entorno.
- Gestion estricta de secretos: API keys solo en `.env` local, nunca en codigo ni commits.
- SDD manual en Markdown, sin instalar OpenSpec por ahora, con checklist atomico en `../sdd/08-task-checklist.md`.
- Corpus manualmente curado de 10-20 documentos, no recopilado mediante scraping complejo.
- Textos en formato `.txt`, `.md` o `.csv`; PDF solo si se procesan de forma simple y no bloquean.
- Evaluacion ligera pero real: validacion de JSON, revision manual de recuperacion y comprobacion de evidencias.

Si falta una API de LLM, si hay que resolver instalacion de modelos locales pesados, o si la dedicacion diaria es baja, el alcance debe reducirse al minimo: extraccion offline, busqueda semantica basica y briefing desde resultados preprocesados.

## Decision de alcance

### Lo que si debe entrar

El MVP debe incluir obligatoriamente:

- corpus cerrado de 10-20 documentos;
- metadatos basicos por documento: titulo, fuente, fecha, URL si existe, tipo de fuente;
- limpieza e ingesta de texto;
- extraccion estructurada con LLM;
- validacion del JSON con Pydantic;
- almacenamiento de resultados en PostgreSQL y exportacion JSON/CSV;
- embeddings para busqueda semantica;
- observabilidad con Langfuse Cloud;
- sistema de evals reproducible;
- modulo de consulta en lenguaje natural;
- briefing generado con evidencias;
- interfaz web con 3-4 vistas simples;
- contratos API fijados antes de implementar el frontend;
- limitaciones explicitas en cada respuesta.

### Lo que puede entrar si sobra tiempo

Estas funcionalidades aportan valor, pero no deben bloquear:

- grafo simple con NetworkX/PyVis;
- agrupacion automatica de narrativas por similitud;
- exportacion del briefing a Markdown;
- filtros por actor, riesgo, fecha o sector;
- evaluacion LLM-as-judge sobre una muestra pequena.
- subida de documentos desde frontend si reutiliza el pipeline backend;
- Neo4j como sink secundario si ya existe una proyeccion de grafo validada.

### Lo que debe quedar fuera

Para llegar al miercoles, deben quedar fuera:

- scraping masivo;
- ingesta en tiempo real;
- monitorizacion de redes sociales;
- deteccion de bots;
- deteccion automatica de coordinacion;
- atribucion geopolitica fuerte;
- autenticacion de usuarios;
- permisos multiusuario;
- Neo4j;
- arquitectura distribuida;
- despliegue cloud complejo;
- dashboard sofisticado;
- entrenamiento o fine-tuning de modelos.

Matiz importante: Neo4j queda fuera como dependencia core del MVP, no como posibilidad futura. La arquitectura debe permitir anadirlo como sink secundario desde extracciones validadas, sin rehacer RAG, briefing ni evaluacion.

## MVP recomendado

### Nombre

HYDRA Espana Lite

### Pregunta central de demo

> Como puede un sistema basado en IA generativa y recuperacion semantica transformar documentos publicos no estructurados en inteligencia narrativa trazable para un analista?

### Flujo minimo

```text
Corpus cerrado
  -> limpieza de documentos
  -> normalizacion con ontologia ligera
  -> extraccion estructurada con LLM
  -> validacion Pydantic
  -> almacenamiento PostgreSQL + pgvector
  -> embeddings
  -> busqueda semantica
  -> observabilidad y evals
  -> consulta del analista
  -> briefing con evidencias y limitaciones
```

## Producto demo

La demo deberia tener cinco vistas en el frontend:

1. **Corpus**
   - lista de documentos;
   - fuente, fecha y tema;
   - estado de procesamiento.

2. **Narrativas**
   - tabla de narrativas principales;
   - actores;
   - sectores afectados;
   - riesgos;
   - nivel de confianza;
   - evidencias textuales.

3. **HYDRA Analyst**
   - caja de pregunta;
   - recuperacion top-k de documentos;
   - respuesta estructurada;
   - fragmentos citados;
   - advertencia sobre limites del corpus.

4. **Briefing**
   - resumen ejecutivo;
   - narrativa principal;
   - actores y eventos;
   - evaluacion de riesgo;
   - evidencias;
   - conclusion;
   - limitaciones.

5. **Evals**
   - casos de evaluacion;
   - metricas basicas;
   - resultados;
   - trace IDs.

Una sexta vista de grafo seria buena, pero solo si el pipeline principal ya funciona.

La subida de documentos desde frontend tambien debe considerarse una extension. El MVP puede trabajar con corpus local curado; si se anade upload, la UI solo envia archivo + metadatos al backend y no crea un pipeline paralelo.

## Arquitectura tecnica sugerida

### Estructura simple de proyecto

```text
hydra/front/
  package.json
  pnpm-lock.yaml
hydra/back/
  pyproject.toml
  uv.lock
  data/
    raw/
    processed/
    outputs/
  src/
    hydra_api/
      ingest.py
      ontology.py
      schemas.py
      extract.py
      embeddings.py
      retrieval.py
      briefing.py
      council.py
      evals.py
      observability.py
hydra/README.md
```

### Componentes

| Componente | Recomendacion | Motivo |
|---|---|---|
| Interfaz | Next.js + Tailwind + pnpm o HTML/Tailwind + pnpm | Demo web dentro del monorepo |
| Backend | FastAPI + uv | API Python reproducible |
| Esquemas | Pydantic | Valida salidas y da rigor tecnico |
| Persistencia | PostgreSQL + pgvector | Une metadatos, documentos y vectores |
| RAG | LangChain + PGVector | Orquestacion y retrieval trazables |
| LLM | Proveedor configurable compatible con OpenAI | Chat, structured outputs y embeddings sin acoplar el MVP a una marca concreta |
| Ontologia | YAML/JSON + validacion | Aporta capa semantica sin complejidad OWL/RDF |
| Orquestacion | LangChain | RAG, structured output y LLM council |
| Observabilidad | Langfuse Cloud | Trazas, tokens, latencia, costes y debugging |
| Evals | Langfuse Cloud + scripts propios | Evaluacion reproducible del sistema |
| LLM council | Verificacion/evaluacion, no core | Reduce alucinaciones sin bloquear el flujo principal |
| Grafo | NetworkX/PyVis opcional | Aporta visualizacion, no es core |

Las decisiones tecnicas detalladas se desarrollan en `hydra-architecture.md` para mantener este documento como analisis ejecutivo.

## Esquema minimo de extraccion

El extractor deberia devolver una estructura parecida a esta:

```json
{
  "document_id": "doc_001",
  "title": "Titulo del documento",
  "source": "Fuente",
  "date": "2026-05-15",
  "main_topic": "Migracion en Canarias",
  "main_narrative": "Narrativa principal detectada",
  "narrative_frame_id": "institutional_loss_of_control",
  "secondary_narratives": ["Narrativa secundaria"],
  "actors": ["Actor o institucion"],
  "actor_types": ["gobierno central"],
  "locations": ["Canarias", "Espana"],
  "events": ["Evento relacionado"],
  "affected_sectors": ["Instituciones publicas"],
  "threat_types": ["Polarizacion social"],
  "risk_level": "medio",
  "confidence": "media",
  "evidence_fragments": ["Fragmento textual que sustenta el analisis"],
  "analyst_summary": "Resumen analitico breve",
  "limitations": "Limites del analisis para este documento",
  "council_review": {
    "evidence_supported": true,
    "unsupported_claims": [],
    "risk_review": "El nivel de riesgo esta justificado por la recurrencia narrativa y las evidencias citadas."
  }
}
```

Conviene mantener el esquema compacto. Los campos de ontologia ayudan si se limitan a identificadores controlados. El bloque `council_review` puede generarse solo para briefings o para una muestra evaluada, no necesariamente para todos los documentos.

## Sistema de evals obligatorio

Para que no parezca solo una app con chatbot, el TFM necesita una evaluacion pequena pero seria. En este proyecto los evals pasan a ser parte obligatoria del MVP, junto con observabilidad basica en Langfuse Cloud.

### Metricas minimas

| Area | Metrica | Como medir |
|---|---|---|
| Extraccion | porcentaje de JSON valido | validacion Pydantic |
| Completitud | campos obligatorios presentes | conteo automatico |
| Recuperacion | Precision@k cualitativa | revision manual de top 3 o top 5 |
| Evidencias | respuestas con citas utiles | revision manual de muestra |
| Alucinacion | afirmaciones no soportadas | contraste contra fragmentos recuperados |
| Riesgo | coherencia del nivel asignado | rubrica simple bajo/medio/alto |
| Council | porcentaje de respuestas aprobadas por revisor | revision LLM + muestreo humano |
| Ontologia | porcentaje de categorias normalizadas | conteo de campos con IDs validos |
| Observabilidad | porcentaje de consultas trazadas | trazas registradas en Langfuse Cloud |

### Rubrica de revision humana

Usar una escala 1-5 para:

- relevancia de documentos recuperados;
- correccion de actores;
- claridad de narrativa;
- utilidad del briefing;
- trazabilidad de evidencias;
- prudencia analitica sobre coordinacion.

Con 8-12 consultas de prueba y 10-20 documentos basta para demostrar metodologia. Los resultados deben guardarse localmente y, si Langfuse Cloud esta disponible, como scores asociados a trazas o dataset runs.

## Riesgos principales

| Riesgo | Probabilidad | Impacto | Mitigacion |
|---|---:|---:|---|
| Alcance excesivo | Alta | Alto | Congelar MVP y dejar extras como trabajo futuro |
| Mala calidad del corpus | Media | Alto | Curar manualmente menos documentos pero mejores |
| Alucinaciones del LLM | Media | Alto | Forzar evidencias, limitar respuestas al corpus y validar estructura |
| JSON inconsistente | Media | Medio | Pydantic, reintentos y prompts con esquema claro |
| Recuperacion floja | Media | Medio | Metadatos buenos, chunks razonables y prueba de consultas |
| Falta de tiempo para interfaz | Media | Medio | Frontend minimo con HTML/Tailwind si Next.js se atasca |
| Grafo consume demasiado | Alta | Medio | Hacerlo opcional |
| PostgreSQL/pgvector consume configuracion | Media | Medio | Docker Compose y fallback documentado |
| Langfuse Cloud no esta disponible | Baja-media | Medio | App funcional con logs locales y export JSON |
| Self-hosting de Langfuse consume tiempo | Media | Medio | Dejarlo como fallback, no como camino principal del MVP |
| API keys subidas a GitHub | Media | Alto | `.env` en `.gitignore`, `.env.example` sin secretos y revision de `git diff` |
| SDD demasiado pesado | Media | Medio | Markdown ligero con tareas atomicas y criterios de aceptacion |
| LangChain complica la depuracion | Media | Medio | Usarlo solo para RAG, retrieval, council y structured output |
| LLM council aumenta coste y latencia | Media | Medio | Ejecutarlo solo en briefings o evaluacion offline |
| Ontologia demasiado ambiciosa | Media | Medio | Usar YAML/JSON ligero, dejar OWL/RDF como trabajo futuro |
| Debate etico/politico del dominio | Media | Medio | Lenguaje neutral, fuentes publicas y limitaciones claras |
| Atribucion indebida de coordinacion | Media | Alto | Distinguir recurrencia, similitud, amplificacion y coordinacion |

## Plan de trabajo hasta el miercoles

### Sabado 16 de mayo

Objetivo: cerrar el nucleo tecnico.

- Elegir definitivamente el dominio.
- Reunir 10-15 documentos iniciales.
- Crear estructura de datos y metadatos.
- Crear estructura `hydra/front/` y `hydra/back/`.
- Crear estructura `hydra/sdd/` y checklist de tareas atomicas.
- Inicializar backend Python con `uv`.
- Inicializar frontend con `pnpm`.
- Levantar PostgreSQL con pgvector o dejar Docker Compose preparado.
- Definir ontologia ligera de dominio en YAML/JSON.
- Definir `Pydantic` schema.
- Probar extraccion con 2-3 documentos.
- Guardar resultados JSON validados.

Entregable del dia:

- extractor funcionando;
- primeros JSON validos;
- corpus inicial organizado.

### Domingo 17 de mayo

Objetivo: completar pipeline offline.

- Procesar todo el corpus.
- Generar tabla consolidada CSV/JSON.
- Crear embeddings.
- Implementar busqueda semantica sobre pgvector.
- Implementar RAG basico con LangChain.
- Integrar trazas basicas con Langfuse Cloud.
- Probar 5-8 consultas representativas.
- Empezar generador de briefing con evidencias.

Entregable del dia:

- corpus procesado;
- busqueda semantica funcionando;
- briefing inicial desde documentos recuperados.

### Lunes 18 de mayo

Objetivo: convertir el pipeline en demo.

- Construir frontend web.
- Anadir vistas Corpus, Narrativas, HYDRA Analyst, Briefing y Evals.
- Integrar recuperacion top-k en la interfaz.
- Mostrar fragmentos utilizados como evidencias.
- Anadir revision tipo LLM council al briefing si el flujo principal ya funciona.
- Crear dataset minimo de evals.
- Registrar scores basicos en Langfuse Cloud o en export local.
- Anadir mensajes de limitacion y prudencia analitica.
- Preparar consultas demo.

Entregable del dia:

- demo navegable de extremo a extremo.

### Martes 19 de mayo

Objetivo: estabilizar, evaluar y documentar.

- No anadir funcionalidades grandes.
- Ejecutar pruebas manuales de demo.
- Crear tabla de evaluacion minima.
- Revisar trazas de Langfuse Cloud y capturar evidencias de observabilidad.
- Preparar README.
- Capturar pantallas.
- Documentar arquitectura, limitaciones y trabajo futuro.
- Si el grafo no esta hecho, dejarlo fuera.

Entregable del dia:

- MVP final presentable.

### Miercoles 20 de mayo

Objetivo: margen, no desarrollo principal.

- Revisar la demo.
- Corregir errores pequenos.
- Ensayar narrativa de defensa.
- Preparar backup: capturas, video o notebook con outputs precomputados.

## Priorizacion MoSCoW

### Must have

- corpus cerrado;
- extraccion estructurada;
- validacion Pydantic;
- resultados persistidos;
- backend Python con `uv`;
- frontend con `pnpm`;
- estructura monorepo `hydra/front/` y `hydra/back/`;
- SDD manual en `hydra/sdd/`;
- checklist SDD atomico;
- busqueda semantica;
- PostgreSQL + pgvector;
- LangChain para RAG;
- API de modelos configurable para chat y embeddings;
- Langfuse Cloud para observabilidad;
- sistema de evals;
- ontologia ligera de categorias;
- HYDRA Analyst;
- briefing con evidencias;
- limitaciones explicitas;
- README y explicacion metodologica;
- `hydra/.env.example` sin secretos reales y `.gitignore` protegiendo `.env`.

### Should have

- agrupacion de narrativas similares;
- LLM council para revision de briefings;
- filtros por actor, riesgo o sector;
- exportacion Markdown.

### Could have

- grafo visual;
- GraphProjection JSON desde extracciones validadas;
- Neo4j como sink secundario si el core ya funciona;
- LLM-as-judge;
- comparacion entre modelos;
- carga de documentos desde interfaz usando el pipeline backend.

### Won't have en el MVP

- scraping;
- tiempo real;
- redes sociales;
- Neo4j como dependencia core o fuente de verdad;
- ontologia formal OWL/RDF;
- login;
- coordinacion automatica;
- atribucion geopolitica.

## Criterios de exito

El MVP estara listo si puede demostrar en directo:

1. Hay un corpus identificado y trazable.
2. Cada documento produce una extraccion estructurada validada.
3. Las categorias principales se normalizan con una ontologia ligera.
4. El usuario puede preguntar por narrativas, actores o riesgos.
5. El sistema recupera documentos relevantes.
6. La respuesta cita evidencias del corpus.
7. El briefing incluye limitaciones.
8. El sistema evita afirmar coordinacion sin evidencia.
9. Las consultas principales quedan trazadas en Langfuse Cloud o en logs locales equivalentes.
10. No hay secretos reales versionados.
11. Hay una evaluacion minima que mide algo concreto.

## Argumento para defender ante tribunal

El valor del proyecto no esta en afirmar que HYDRA descubre campanas hibridas automaticamente. El valor esta en demostrar una arquitectura de IA aplicada que convierte informacion publica no estructurada en una representacion analitica consultable, trazable y limitada por evidencias.

La defensa deberia apoyarse en cuatro ideas:

- **Rigor tecnico:** esquemas, validacion, embeddings, RAG y evaluacion.
- **Rigor analitico:** diferencia entre recurrencia narrativa y coordinacion.
- **Trazabilidad:** cada conclusion debe apuntar a fragmentos del corpus.
- **Alcance honesto:** PoC funcional, no plataforma de inteligencia completa.

## Recomendacion final

Construir el MVP si se acepta este recorte:

> Un sistema web local, con `hydra/front/` y `hydra/back/` en el mismo repositorio, que trabaja sobre 10-20 documentos curados, extrae narrativas y entidades con LLM, valida la salida con Pydantic, permite consultas RAG y genera briefings con evidencias y limitaciones.

La arquitectura recomendada para ese MVP es FastAPI con `uv`, frontend con `pnpm`, Next.js/Tailwind o HTML/Tailwind si hay que recortar, LangChain, PostgreSQL/pgvector, modelos configurables, Langfuse Cloud y evals propios. Langfuse self-hosted con Docker queda como fallback o trabajo futuro, no como camino principal. No construir todavia scraping, grafo complejo, red social, alertas ni atribucion. Eso se debe presentar como evolucion futura.

Con este enfoque, HYDRA Espana Lite es factible antes del miercoles 20 de mayo de 2026 y puede ser un TFM defendible. Con un alcance mas ambicioso, el riesgo de no llegar o de entregar una demo superficial es alto.
