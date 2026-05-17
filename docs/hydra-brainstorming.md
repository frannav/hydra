# HYDRA

## Radar OSINT de inteligencia narrativa y amenazas híbridas

> **Nota de estado:** este documento es material de brainstorming y debe conservarse como fuente de ideas, prompts y argumentos de memoria. Las decisiones vigentes de alcance y arquitectura están en `hydra-analysis.md` y `hydra-architecture.md`. Algunas recomendaciones originales, como Streamlit, ChromaDB/FAISS o JSON/CSV como persistencia principal, han sido sustituidas por la arquitectura actual: frontend en `hydra/front/`, backend en `hydra/back/`, FastAPI con `uv`, frontend con `pnpm`, PostgreSQL + pgvector, LangChain, modelos configurables, Langfuse Cloud y evals propios.

> Propuesta de proyecto de fin de máster en Inteligencia Artificial.
>
> **Idea central:** construir una prueba funcional de concepto que use IA generativa, recuperación semántica y extracción estructurada para transformar fuentes públicas no estructuradas en inteligencia narrativa útil para un analista.

---

## 1. Resumen ejecutivo

**HYDRA** es una plataforma OSINT basada en IA generativa para analizar narrativas de desinformación, campañas informativas y señales de amenazas híbridas en el contexto español.

El objetivo **no** es construir un detector automático de noticias falsas. Eso sería una promesa floja para un TFM, porque mezcla veracidad, atribución, intención y coordinación en una sola caja negra. El enfoque serio es otro:

> Dado un corpus cerrado de noticias, informes y documentos públicos, HYDRA identifica narrativas, actores, eventos, sectores afectados, canales de difusión, evidencias textuales y riesgos potenciales, generando finalmente un briefing de inteligencia para el analista.

La versión recomendada para el TFM es una demo funcional acotada:

> **HYDRA: Sistema de inteligencia narrativa para amenazas híbridas sobre un corpus cerrado de fuentes públicas.**

---

## 2. Valor como proyecto de fin de máster en IA

Como TFM de Inteligencia Artificial, HYDRA tiene buen potencial si se presenta con alcance realista y rigor metodológico.

### 2.1. Por qué encaja bien

El proyecto permite demostrar competencias reales de IA aplicada:

- procesamiento de lenguaje natural;
- extracción estructurada de información con LLMs;
- validación de salidas con esquemas de datos;
- embeddings y búsqueda semántica;
- recuperación aumentada por generación, o RAG;
- generación controlada de informes;
- evaluación de respuestas generadas;
- diseño de una aplicación funcional para analistas.

Esto es defendible porque no se limita a “usar ChatGPT”. Hay pipeline, datos, validación, evaluación y producto. Ahí está la diferencia entre un juguete y un TFM serio.

### 2.2. Riesgo principal

El riesgo es venderlo como una plataforma de inteligencia estratégica completa. Eso sería demasiado grande.

HYDRA no debería prometer:

- atribución geopolítica definitiva;
- detección automática de campañas coordinadas;
- análisis en tiempo real;
- scraping masivo;
- monitorización completa de redes sociales;
- reemplazo del analista humano.

La formulación correcta es:

> HYDRA es una prueba funcional de concepto que demuestra cómo la IA generativa puede convertir información pública no estructurada en inteligencia narrativa estructurada, trazable y consultable.

Ese matiz es CLAVE. Si prometés menos pero lo demostrás bien, ganás. Si prometés Palantir en dos semanas, te comen vivo. Es así de fácil.

---

## 3. Problema que resuelve

Las campañas de desinformación y las amenazas híbridas no suelen aparecer como eventos aislados. Normalmente se manifiestan como una combinación de señales dispersas:

- narrativas repetidas;
- actores que amplifican ciertos marcos;
- eventos usados como detonantes;
- sectores sensibles afectados;
- canales de difusión;
- tensión social;
- pérdida de confianza institucional;
- influencia extranjera;
- polarización pública.

El problema es que estas señales aparecen repartidas en múltiples fuentes. Para un analista humano, detectar patrones narrativos exige mucho tiempo y una lectura comparativa constante.

HYDRA busca ayudar a responder preguntas como:

- ¿Qué narrativas están apareciendo sobre un tema concreto?
- ¿Qué actores se repiten?
- ¿Qué sectores se ven afectados?
- ¿Qué eventos han activado una narrativa?
- ¿Hay señales de recurrencia o amplificación?
- ¿Qué riesgos puede generar una narrativa?
- ¿Esta noticia encaja con una narrativa ya detectada?
- ¿Qué evidencias documentales apoyan el análisis?

---

## 4. Qué es y qué no es HYDRA

### 4.1. Qué no es

HYDRA no debería presentarse como:

- un detector automático de verdad o falsedad;
- una herramienta que prueba coordinación real entre actores;
- una plataforma completa de monitorización en tiempo real;
- un sistema de scraping masivo;
- una solución de inteligencia militar completa;
- una réplica de Palantir;
- una herramienta de atribución geopolítica definitiva.

### 4.2. Qué sí es

HYDRA sí puede plantearse como:

- un sistema de análisis OSINT;
- una plataforma de inteligencia narrativa;
- un radar de amenazas híbridas;
- un asistente para analistas;
- una herramienta de exploración de narrativas;
- un sistema RAG especializado;
- un generador de briefings de inteligencia;
- un grafo de relaciones entre narrativas, actores, eventos y riesgos.

---

## 5. Versión recomendada para el TFM

### HYDRA

Dado que el tiempo de entrega es limitado, la versión más realista es una demo funcional sobre un corpus cerrado.

La formulación mínima viable sería:

> Sistema que analiza un conjunto cerrado de noticias e informes sobre un tema sensible en España, extrae narrativas, actores, eventos, sectores afectados y riesgos, y permite al usuario consultar el corpus mediante preguntas en lenguaje natural.

### 5.1. Dominio recomendado

Para una versión rápida y defendible, el dominio recomendado es:

> **Migración y confianza institucional en Canarias/España.**

Motivos:

- tiene contexto español claro;
- permite acotar territorialmente;
- hay suficiente contenido público;
- conecta con desinformación, polarización y narrativa institucional;
- permite analizar actores, sectores, eventos y riesgos;
- genera una demo comprensible para tribunal no técnico.

Alternativa viable:

> **Energía, soberanía y confianza institucional.**

Ventajas:

- narrativa fácil de estructurar;
- conecta con economía, Unión Europea, Gobierno y empresas;
- se presta bien al análisis de riesgo narrativo.

### 5.2. Recomendación arquitectónica de alcance

Para el TFM, conviene elegir **un único dominio** y un corpus pequeño pero bien curado.

| Decisión | Recomendación | Motivo |
|---|---|---|
| Corpus | 10-30 documentos | Suficiente para demo y evaluación manual |
| Dominio | Migración en Canarias/España | Contexto cercano, defendible y acotado |
| Interfaz | Streamlit | Rápida, suficiente y presentable |
| Base de datos | JSON/CSV + vector store | Evita sobreingeniería |
| Grafo | NetworkX/PyVis opcional | Aporta valor visual, pero no debe bloquear |
| Scraping | No en MVP | Consume tiempo y agrega fragilidad |
| Tiempo real | No en MVP | Fuera de alcance |

---

## 6. Objetivos del proyecto

### 6.1. Objetivo general

Diseñar e implementar una prueba funcional de concepto para analizar narrativas en fuentes públicas mediante técnicas de IA generativa, búsqueda semántica y extracción estructurada de información.

### 6.2. Objetivos específicos

1. Construir un corpus cerrado de documentos OSINT sobre un dominio sensible en España.
2. Implementar un pipeline de ingesta y preprocesamiento textual.
3. Extraer información estructurada usando un LLM y validación con esquemas.
4. Generar embeddings para búsqueda semántica sobre el corpus.
5. Agrupar documentos por similitud narrativa.
6. Permitir consultas en lenguaje natural mediante un módulo RAG.
7. Generar briefings de inteligencia narrativa con evidencias.
8. Evaluar la calidad de extracción, recuperación y generación.

---

## 7. Preguntas de investigación

El TFM puede formularse alrededor de estas preguntas:

1. ¿Hasta qué punto un sistema basado en LLMs puede extraer narrativas, actores, eventos y riesgos desde fuentes públicas no estructuradas?
2. ¿Puede la búsqueda semántica mejorar la recuperación de documentos relevantes para una consulta analítica?
3. ¿Qué mecanismos reducen el riesgo de alucinación en briefings generados por IA?
4. ¿Cómo distinguir automáticamente entre recurrencia narrativa y coordinación real sin caer en atribuciones no justificadas?

La cuarta pregunta es importantísima. Ahí hay madurez. No estás diciendo “mi IA descubre conspiraciones”; estás diciendo “mi sistema ayuda al analista sin sobreafirmar”. Fantástico.

---

## 8. Alcance del MVP

El MVP debería incluir:

- carga de documentos;
- procesamiento y limpieza de textos;
- extracción estructurada con LLM;
- validación de JSON con Pydantic;
- agrupación de narrativas similares;
- búsqueda semántica sobre el corpus;
- modo consulta para preguntar por noticias, narrativas, actores o sectores;
- generación automática de briefing;
- visualización básica de resultados;
- grafo simple de relaciones, si da tiempo.

### 8.1. Funcionalidades fuera de alcance

Para llegar a una versión funcional rápido, conviene evitar:

- scraping complejo;
- ingesta en tiempo real;
- integración con redes sociales;
- autenticación de usuarios;
- dashboards sofisticados;
- Neo4j si no es imprescindible;
- agentes autónomos complejos;
- detección automática de coordinación;
- análisis masivo de redes sociales;
- alertas en tiempo real;
- atribución geopolítica fuerte.

Todo eso puede aparecer como trabajo futuro.

---

## 9. Concepto central del sistema

HYDRA debe demostrar el siguiente flujo:

```text
Fuentes públicas
      ↓
Procesamiento de texto
      ↓
Extracción estructurada
      ↓
Identificación de narrativas
      ↓
Relación con actores, eventos y sectores
      ↓
Evaluación de riesgo
      ↓
Consulta del analista
      ↓
Briefing de inteligencia
```

---

## 10. Funcionalidad clave: HYDRA Analyst

Una de las partes más interesantes del proyecto es que el sistema no sea solo un dashboard pasivo, sino un asistente al que el usuario pueda preguntar.

Esta funcionalidad puede llamarse:

- **HYDRA Analyst**;
- Modo Investigación;
- Analyst Mode;
- Consulta de Inteligencia Narrativa;
- Investigación guiada por consulta.

La idea es que el usuario pueda escribir preguntas como:

- ¿Hay una narrativa de desconfianza institucional relacionada con la gestión migratoria en Canarias?
- Analiza esta noticia y dime con qué narrativas se relaciona.
- ¿Qué actores aparecen vinculados a la narrativa de pérdida de soberanía energética?

El sistema entonces trabaja sobre el corpus disponible.

### 10.1. Qué significa que el sistema trabaje

En este proyecto, que el sistema trabaje significa que ejecuta una cadena de análisis:

1. Entiende la pregunta del usuario.
2. Reformula la pregunta como una hipótesis de análisis.
3. Busca documentos relevantes en el corpus.
4. Recupera evidencias textuales.
5. Extrae narrativas, actores, eventos y sectores.
6. Compara la consulta con narrativas ya detectadas.
7. Evalúa el nivel de riesgo.
8. Genera un briefing específico.
9. Muestra las fuentes o fragmentos utilizados.

Flujo conceptual:

```text
Pregunta del usuario
        ↓
Búsqueda semántica en el corpus
        ↓
Recuperación de documentos relevantes
        ↓
Análisis estructurado con LLM
        ↓
Comparación con narrativas existentes
        ↓
Evaluación de riesgo
        ↓
Briefing con evidencias
```

---

## 11. Ejemplos de preguntas soportadas

### 11.1. Preguntas por narrativa

- ¿Existe una narrativa sobre pérdida de confianza en las instituciones?
- ¿Hay una narrativa que vincule inmigración con inseguridad?
- ¿Se detecta una narrativa sobre pérdida de soberanía energética?

### 11.2. Preguntas por actor

- ¿Qué narrativas aparecen asociadas al Gobierno de España?
- ¿Qué actores se repiten en las noticias sobre migración?
- ¿Qué instituciones aparecen más vinculadas a discursos de crisis?

### 11.3. Preguntas por sector

- ¿Qué riesgos narrativos hay alrededor del sector energético?
- ¿Qué sectores aparecen afectados por narrativas de desconfianza institucional?

### 11.4. Preguntas por noticia concreta

- Analiza esta noticia y dime si encaja con alguna narrativa detectada previamente.
- ¿Esta noticia forma parte de una narrativa más amplia?
- ¿Qué actores, eventos y riesgos se extraen de esta noticia?

### 11.5. Preguntas por campaña o recurrencia

- ¿Esta narrativa aparece repetida en varios documentos?
- ¿Hay indicios de amplificación de un mismo marco narrativo?
- ¿Qué documentos comparten una narrativa similar?

---

## 12. Ejemplo de respuesta esperada

### Pregunta del usuario

> ¿Hay indicios de una narrativa coordinada contra la gestión migratoria en Canarias?

### Respuesta esperada del sistema

```markdown
## Análisis de inteligencia narrativa

### Consulta analizada

¿Hay indicios de una narrativa coordinada contra la gestión migratoria en Canarias?

### Documentos relevantes encontrados

Se han recuperado 8 documentos relacionados con migración, Canarias, gestión institucional y presión sobre servicios públicos.

### Narrativa principal detectada

La narrativa dominante vincula el aumento de llegadas migratorias con falta de control institucional, saturación de recursos públicos y deterioro de la seguridad ciudadana.

### Actores mencionados

- Gobierno de España
- Gobierno de Canarias
- Fuerzas de seguridad
- Organizaciones no gubernamentales
- Partidos políticos
- Medios locales

### Eventos asociados

- Aumento de llegadas migratorias.
- Debate sobre recursos asistenciales.
- Declaraciones políticas.
- Episodios puntuales amplificados en medios.
- Tensión institucional entre administraciones.

### Evaluación de riesgo

Riesgo medio-alto.

La narrativa puede contribuir a polarización social, presión sobre instituciones públicas y asociación simplificada entre migración e inseguridad.

### Evaluación de coordinación

Con el corpus actual no puede afirmarse coordinación real entre actores. Sí se observa recurrencia temática y repetición de marcos narrativos similares en varios documentos.

### Evidencias

El sistema identifica fragmentos donde aparecen marcos como:

- “descontrol”;
- “abandono institucional”;
- “saturación”;
- “inseguridad”;
- “efecto llamada”.

### Conclusión

Existe una narrativa recurrente sobre pérdida de control institucional en la gestión migratoria. No hay evidencia suficiente para afirmar una campaña coordinada, pero sí una convergencia narrativa que merece seguimiento.
```

---

## 13. Distinción clave: recurrencia vs. coordinación

Esta distinción es central para que el proyecto sea serio.

HYDRA puede detectar:

- repetición de narrativas;
- similitud semántica;
- actores recurrentes;
- eventos compartidos;
- marcos discursivos similares;
- concentración temporal;
- evidencias documentales.

Pero no debería afirmar automáticamente:

> “Existe una campaña coordinada.”

Lo correcto sería decir:

> “Se detecta recurrencia narrativa y convergencia temática, pero no evidencia suficiente para atribuir coordinación.”

Esta prudencia analítica hace que el sistema sea más creíble y defendible.

---

## 14. Dominios posibles para el corpus

### 14.1. Migración e instituciones

Analizar narrativas sobre:

- gestión migratoria;
- presión sobre servicios públicos;
- seguridad ciudadana;
- Canarias;
- Gobierno central;
- Gobierno autonómico;
- ONG;
- polarización social.

Ventaja: está muy conectado con España y Canarias.

### 14.2. Energía y soberanía

Analizar narrativas sobre:

- dependencia energética;
- precios de la luz;
- decisiones europeas;
- transición energética;
- empresas energéticas;
- pérdida de soberanía;
- impacto económico.

Ventaja: buen campo para amenazas híbridas y confianza institucional.

### 14.3. Ciberseguridad e instituciones

Analizar narrativas sobre:

- ciberataques;
- vulnerabilidad institucional;
- filtraciones;
- servicios públicos;
- seguridad nacional;
- confianza digital.

Ventaja: conecta muy bien con defensa e inteligencia.

### 14.4. Defensa e influencia extranjera

Analizar narrativas sobre:

- OTAN;
- guerra de Ucrania;
- gasto militar;
- influencia rusa;
- propaganda;
- seguridad europea;
- soberanía nacional.

Ventaja: es la versión más cercana a amenazas híbridas.

---

## 15. Entidades que debería extraer el sistema

El extractor estructurado debería identificar:

- narrativa principal;
- narrativas secundarias;
- actores;
- instituciones;
- países;
- regiones;
- eventos;
- sectores afectados;
- canales;
- tono;
- marco narrativo;
- riesgo;
- tipo de amenaza;
- evidencias textuales;
- nivel de confianza;
- fecha del documento;
- fuente;
- resumen analítico.

---

## 16. Esquema de extracción estructurada

Ejemplo de JSON por documento:

```json
{
  "document_id": "doc_001",
  "title": "Título de la noticia o documento",
  "source": "Fuente",
  "date": "2026-05-15",
  "main_topic": "Migración en Canarias",
  "main_narrative": "Las instituciones han perdido el control sobre la gestión migratoria",
  "secondary_narratives": [
    "Saturación de servicios públicos",
    "Relación entre migración e inseguridad",
    "Abandono del Gobierno central"
  ],
  "actors": [
    "Gobierno de España",
    "Gobierno de Canarias",
    "ONG",
    "Fuerzas de seguridad"
  ],
  "locations": [
    "Canarias",
    "España"
  ],
  "events": [
    "Aumento de llegadas migratorias",
    "Debate sobre recursos de acogida"
  ],
  "affected_sectors": [
    "Instituciones públicas",
    "Seguridad",
    "Servicios sociales"
  ],
  "channels": [
    "Medios digitales",
    "Declaraciones políticas"
  ],
  "threat_types": [
    "Desinformación",
    "Polarización social",
    "Erosión de confianza institucional"
  ],
  "risk_level": "medio",
  "confidence": "media",
  "evidence_fragments": [
    "Fragmento textual relevante 1",
    "Fragmento textual relevante 2"
  ],
  "analyst_summary": "El documento refuerza una narrativa de pérdida de control institucional en torno a la gestión migratoria."
}
```

---

## 17. Modelo de datos simplificado

Para el MVP no hace falta una base de datos compleja.

Se puede trabajar con:

- documentos en `.txt`, `.md`, `.pdf` o `.csv`;
- resultados estructurados en `.json`;
- tabla procesada en `.csv`;
- embeddings en ChromaDB o FAISS;
- grafo en NetworkX.

### 17.1. Entidades principales

- `Document`
- `Narrative`
- `Actor`
- `Event`
- `Sector`
- `Location`
- `Risk`
- `Source`
- `Evidence`

### 17.2. Relaciones posibles

- `Document -> contains -> Narrative`
- `Narrative -> mentions -> Actor`
- `Narrative -> affects -> Sector`
- `Narrative -> relates_to -> Event`
- `Event -> occurs_in -> Location`
- `Narrative -> has_risk -> Risk`
- `Actor -> appears_in -> Document`
- `Evidence -> supports -> Narrative`

---

## 18. Grafo de conocimiento

El grafo puede representar relaciones extraídas.

Ejemplo:

```text
Gobierno de España
      ↓ aparece en
Narrativa de pérdida de control institucional
      ↓ afecta a
Confianza institucional
      ↓ genera riesgo de
Polarización social
```

Otro ejemplo:

```text
Migración
   → asociada con → seguridad ciudadana
   → asociada con → presión sobre servicios públicos
   → asociada con → debate político
   → asociada con → Canarias
```

El grafo no tiene que ser complejo. Basta con visualizar relaciones entre:

- narrativas;
- actores;
- sectores;
- eventos;
- riesgos.

---

## 19. Arquitectura técnica propuesta

Arquitectura mínima:

```text
Corpus documental
      ↓
Preprocesado
      ↓
Chunking
      ↓
Embeddings
      ↓
Vector store
      ↓
Extracción estructurada con LLM
      ↓
Validación con Pydantic
      ↓
Agrupación de narrativas
      ↓
Grafo de relaciones
      ↓
RAG para consultas
      ↓
Generador de briefings
      ↓
Interfaz Streamlit
```

---

## 20. Pipeline principal

### 20.1. Fase 1: Ingesta

Entrada:

- noticias;
- informes;
- comunicados;
- artículos;
- documentos públicos.

Salida:

- textos limpios;
- metadatos básicos;
- identificador de documento.

### 20.2. Fase 2: Preprocesado

Tareas:

- limpieza de texto;
- eliminación de ruido;
- segmentación por chunks;
- normalización de fechas;
- extracción de título y fuente si está disponible.

### 20.3. Fase 3: Embeddings

Cada documento o chunk se convierte en un vector semántico.

Esto permite:

- búsqueda por similitud;
- recuperación de documentos relevantes;
- agrupación de narrativas similares;
- comparación entre noticias.

### 20.4. Fase 4: Extracción estructurada

El LLM analiza cada documento y devuelve un JSON validado.

Extrae:

- narrativa;
- actores;
- eventos;
- sectores;
- riesgos;
- evidencias;
- resumen analítico.

### 20.5. Fase 5: Agrupación narrativa

Se agrupan documentos con narrativas similares.

Métodos posibles:

- embeddings más clustering;
- similitud coseno;
- agrupación manual asistida;
- LLM que compare narrativas;
- etiquetas generadas automáticamente.

Para el MVP basta con usar embeddings y similitud semántica.

### 20.6. Fase 6: Consulta inteligente

El usuario pregunta algo.

El sistema:

1. vectoriza la pregunta;
2. busca documentos relevantes;
3. recupera evidencias;
4. analiza los documentos;
5. genera una respuesta estructurada;
6. produce un briefing.

### 20.7. Fase 7: Briefing de inteligencia

El sistema genera un informe final con:

- resumen ejecutivo;
- narrativa detectada;
- actores implicados;
- eventos relacionados;
- sectores afectados;
- nivel de riesgo;
- evidencias;
- limitaciones;
- conclusión analítica.

---

## 21. Stack recomendado para ir rápido

| Capa | Recomendación | Alternativas |
|---|---|---|
| Lenguaje | Python | — |
| Interfaz | Streamlit | Gradio |
| LLM | OpenAI API u otro modelo equivalente | modelo local si el tiempo lo permite |
| Validación de datos | Pydantic | dataclasses + validación manual |
| Persistencia simple | JSON, CSV | SQLite |
| Embeddings/RAG | ChromaDB o FAISS | LlamaIndex, LangChain |
| Grafo | NetworkX + PyVis | Plotly, Graphviz |
| Procesamiento | Pandas, regex | BeautifulSoup, PyMuPDF si hay HTML/PDF |

### 21.1. Recomendación directa

Para no perder tiempo:

- **Streamlit** para la interfaz.
- **Pydantic** para validar salidas.
- **JSON/CSV** para resultados estructurados.
- **ChromaDB o FAISS** para búsqueda semántica.
- **NetworkX/PyVis** solo si el pipeline principal ya funciona.

Primero el flujo completo. Después el maquillaje visual. Ponete las pilas con esto, porque es el típico error: querer hacer un dashboard hermoso sin tener inteligencia funcionando abajo. Una casa no se empieza por la pintura.

---

## 22. Pantallas de la demo

### 22.1. Pantalla 1: Carga o selección del corpus

Permite seleccionar el conjunto de documentos a analizar.

Elementos:

- selector de corpus;
- número de documentos;
- fuente;
- dominio;
- rango de fechas.

### 22.2. Pantalla 2: Narrativas detectadas

Tabla con:

- narrativa principal;
- documentos asociados;
- actores;
- sectores;
- riesgo;
- confianza;
- evidencias.

### 22.3. Pantalla 3: HYDRA Analyst

Caja de texto:

> Pregunta a HYDRA sobre una narrativa, actor, noticia o sector.

Ejemplos sugeridos:

- ¿Qué narrativas aparecen sobre migración y seguridad?
- ¿Qué actores están más asociados a desconfianza institucional?
- ¿Hay recurrencia de una narrativa de abandono del Gobierno central?

### 22.4. Pantalla 4: Briefing

Muestra:

- resumen ejecutivo;
- análisis;
- evidencias;
- nivel de riesgo;
- conclusión.

### 22.5. Pantalla 5: Grafo

Visualización de relaciones entre:

- actores;
- narrativas;
- eventos;
- sectores;
- riesgos.

---

## 23. Plantilla de briefing

```markdown
# Briefing de inteligencia narrativa

## Resumen ejecutivo

Se ha detectado una narrativa recurrente relacionada con [tema principal]. La narrativa aparece asociada a [actores principales] y afecta principalmente a [sectores afectados].

## Narrativa principal

[Descripción de la narrativa detectada]

## Narrativas secundarias

- [Narrativa secundaria 1]
- [Narrativa secundaria 2]
- [Narrativa secundaria 3]

## Actores relevantes

- [Actor 1]
- [Actor 2]
- [Actor 3]

## Eventos asociados

- [Evento 1]
- [Evento 2]

## Sectores afectados

- [Sector 1]
- [Sector 2]

## Evaluación de riesgo

Nivel de riesgo: [bajo / medio / alto]

Justificación:
[Explicación del riesgo]

## Evidencias encontradas

1. [Fragmento o resumen de evidencia]
2. [Fragmento o resumen de evidencia]
3. [Fragmento o resumen de evidencia]

## Evaluación analítica

[Interpretación del sistema]

## Limitaciones

El análisis se basa únicamente en el corpus disponible. No permite afirmar coordinación real entre actores sin evidencias adicionales.

## Conclusión

[Conclusión final]
```

---

## 24. Prompts conceptuales

### 24.1. Prompt de extracción estructurada

```text
Eres un analista de inteligencia especializado en desinformación, narrativas públicas y amenazas híbridas.

Analiza el siguiente documento y extrae información estructurada.

Debes identificar:

- narrativa principal;
- narrativas secundarias;
- actores mencionados;
- instituciones;
- países o regiones;
- eventos relacionados;
- sectores afectados;
- posibles riesgos;
- tipo de amenaza;
- evidencias textuales;
- nivel de confianza.

No afirmes coordinación entre actores si el documento no aporta evidencias suficientes.

Devuelve la respuesta en JSON válido.
```

### 24.2. Prompt para HYDRA Analyst

```text
Eres HYDRA Analyst, un asistente de inteligencia narrativa.

El usuario ha realizado una consulta sobre un corpus de documentos OSINT.

Tu tarea es:

1. Analizar la pregunta.
2. Revisar los documentos recuperados.
3. Identificar narrativas relevantes.
4. Extraer actores, eventos, sectores y riesgos.
5. Citar evidencias textuales.
6. Evaluar si existe recurrencia narrativa.
7. Indicar claramente las limitaciones.
8. Generar un briefing analítico.

No afirmes que existe una campaña coordinada salvo que haya evidencia explícita.
Distingue entre recurrencia, amplificación, similitud narrativa y coordinación.
```

---

## 25. Evaluación del sistema

El proyecto puede evaluarse en cuatro niveles.

### 25.1. Evaluación técnica

- ¿El JSON generado es válido?
- ¿Los campos obligatorios están completos?
- ¿La extracción es consistente entre documentos?
- ¿El sistema recupera documentos relevantes?
- ¿Las respuestas citan evidencias del corpus?

### 25.2. Evaluación analítica

- ¿La narrativa detectada tiene sentido?
- ¿Los actores extraídos son correctos?
- ¿El nivel de riesgo está justificado?
- ¿El briefing es útil para un analista?
- ¿El sistema evita conclusiones no respaldadas?

### 25.3. Evaluación con LLM-as-judge

Se puede usar otro LLM como evaluador para revisar:

- fidelidad al documento;
- calidad de la extracción;
- coherencia del briefing;
- ausencia de alucinaciones;
- justificación del riesgo;
- calidad de las evidencias.

### 25.4. Evaluación humana

Un usuario o evaluador puede revisar una muestra y puntuar:

- precisión;
- utilidad;
- claridad;
- confianza;
- completitud.

### 25.5. Métricas mínimas recomendadas

| Componente | Métrica sugerida | Cómo medirla |
|---|---|---|
| Extracción JSON | % de salidas válidas | Validación Pydantic |
| Recuperación | Precision@k cualitativa | Revisión manual de top-k documentos |
| Evidencias | % respuestas con citas útiles | Muestreo manual |
| Riesgo | Coherencia del nivel asignado | Rúbrica humana o LLM-as-judge |
| Alucinación | Afirmaciones no soportadas | Contraste con corpus |

---

## 26. Riesgos del proyecto y mitigación

### Riesgo 1: alcance demasiado grande

Solución:

- limitar corpus;
- limitar dominio;
- limitar funcionalidades;
- priorizar pipeline completo antes que features extra.

### Riesgo 2: alucinaciones del LLM

Solución:

- obligar a citar evidencias;
- usar JSON estructurado;
- validar con Pydantic;
- incluir campo de confianza;
- advertir limitaciones.

### Riesgo 3: falsas atribuciones de coordinación

Solución:

- distinguir recurrencia de coordinación;
- usar lenguaje prudente;
- exigir evidencia explícita;
- incluir limitaciones en cada briefing.

### Riesgo 4: mala calidad del corpus

Solución:

- seleccionar documentos manualmente;
- usar fuentes claras;
- guardar metadatos;
- trabajar con 10-30 documentos bien elegidos.

### Riesgo 5: exceso de complejidad técnica

Solución:

- Streamlit;
- JSON/CSV;
- ChromaDB o FAISS;
- NetworkX opcional;
- evitar integraciones innecesarias.

---

## 27. Plan de entrega rápida

### Viernes

Objetivo:

- cerrar alcance;
- elegir dominio;
- recopilar corpus;
- definir esquema JSON;
- probar extracción con pocos documentos.

Entregable:

- extractor funcionando sobre 2-3 documentos.

### Sábado

Objetivo:

- procesar todo el corpus;
- guardar resultados estructurados;
- crear embeddings;
- probar búsqueda semántica;
- agrupar narrativas similares.

Entregable:

- dataset estructurado y consultable.

### Domingo

Objetivo:

- construir app en Streamlit;
- añadir HYDRA Analyst;
- mostrar tabla de narrativas;
- generar briefing;
- visualizar evidencias.

Entregable:

- demo funcional.

### Lunes

Objetivo:

- pulir errores;
- preparar memoria;
- capturas;
- README;
- explicación de arquitectura;
- demo guiada.

Entregable:

- versión presentable.

### Martes

Objetivo:

- revisión final;
- no añadir features nuevas;
- probar demo;
- preparar defensa;
- grabar vídeo si hace falta.

Entregable:

- versión final del MVP.

---

## 28. Mínimo defendible

La versión mínima defendible debe hacer esto:

### Input

10-30 documentos sobre un dominio concreto.

### Proceso

- extracción estructurada;
- búsqueda semántica;
- consulta en lenguaje natural;
- generación de briefing.

### Output

- tabla de narrativas;
- actores;
- sectores;
- riesgos;
- evidencias;
- briefing final.

Con eso ya hay un TFM defendible.

---

## 29. Versión ideal pero todavía realista

La versión ideal para la entrega sería **HYDRA** con estas funcionalidades:

1. Corpus cerrado de noticias e informes.
2. Extracción de narrativas, actores, eventos y riesgos.
3. Embeddings para búsqueda semántica.
4. Módulo HYDRA Analyst para preguntas.
5. Briefing automático con evidencias.
6. Tabla de narrativas detectadas.
7. Grafo simple de relaciones.
8. Exportación de resultados en JSON o Markdown.

---

## 30. Posibles títulos del TFM

Opciones recomendadas:

1. **HYDRA España: sistema de inteligencia narrativa basado en IA generativa para el análisis OSINT de amenazas híbridas**
2. **Análisis de narrativas de desinformación mediante IA generativa y recuperación semántica sobre fuentes públicas**
3. **Sistema RAG para extracción y consulta de inteligencia narrativa en documentos OSINT**
4. **Aplicación de modelos generativos al análisis estructurado de narrativas y riesgos en fuentes abiertas**
5. **HYDRA: radar OSINT de narrativas públicas mediante IA generativa**

### Título recomendado

> **HYDRA: sistema RAG para análisis de inteligencia narrativa en fuentes públicas sobre amenazas híbridas**

Es preciso, técnico y defendible. No promete magia. Promete un sistema concreto con IA aplicada.

---

## 31. Conclusión como TFM

HYDRA es una buena idea para un proyecto de fin de máster de IA si se mantiene acotada y se defiende como sistema de apoyo al análisis, no como verdad automática.

La clave del proyecto no está en hacer “una app con un chatbot”. Eso lo hace cualquiera. La clave está en demostrar un pipeline completo:

1. corpus curado;
2. extracción estructurada;
3. validación;
4. búsqueda semántica;
5. generación con evidencias;
6. evaluación;
7. limitaciones explícitas.

Si se implementa así, el proyecto muestra criterio técnico, madurez analítica y comprensión real de los riesgos de la IA generativa. Eso es lo que hace que un TFM sea defendible.

Mi recomendación final:

> Construir HYDRA sobre un corpus cerrado de migración y confianza institucional en Canarias/España, con Streamlit, Pydantic, embeddings, RAG y generación de briefings con evidencias.

Menos humo, más sistema. Menos “IA que descubre campañas”, más trazabilidad, evidencias y límites. Ahí está el diferencial.
