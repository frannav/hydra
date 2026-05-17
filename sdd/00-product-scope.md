# 00 - Product Scope

## Objetivo

Construir HYDRA Espana Lite como prueba funcional de concepto para convertir un corpus cerrado de fuentes publicas en inteligencia narrativa trazable.

## Dominio

Migracion, Canarias y confianza institucional.

## Must have

- Corpus cerrado de 10-20 documentos.
- Extraccion estructurada validada con Pydantic.
- Ontologia ligera de categorias.
- RAG sobre PostgreSQL + pgvector.
- HYDRA Analyst para consultas.
- Briefing con evidencias y limitaciones.
- Evals minimos reproducibles.
- Observabilidad con Langfuse Cloud o logs locales.
- Frontend y backend en monorepo.

## Fuera de alcance

- Scraping masivo.
- Ingesta en tiempo real.
- Redes sociales.
- Deteccion de bots.
- Coordinacion automatica.
- Atribucion geopolitica.
- Autenticacion.
- Neo4j como dependencia core del MVP.
- Subida de documentos desde frontend como flujo obligatorio del MVP.
- Fine-tuning.

## Extensiones permitidas si sobra tiempo

Estas extensiones no deben bloquear el MVP ni cambiar el contrato del core:

- Subida de documentos desde frontend, siempre pasando por el mismo servicio de ingesta del backend.
- Grafo ligero derivado de extracciones validadas.
- Neo4j como sink secundario de grafo, no como fuente de verdad ni dependencia necesaria para RAG.

## Regla de desacoplamiento

El core debe estar desacoplado desde el principio:

- La ingesta recibe documentos desde fuentes intercambiables: corpus local primero, upload frontend despues.
- El frontend nunca parsea, trocea, embebe ni llama a modelos; solo envia archivos/metadatos al backend y consulta estado/resultados.
- La extraccion estructurada produce un JSON/Pydantic canonico independiente de la persistencia.
- PostgreSQL/pgvector es el storage principal del MVP, pero las extracciones validadas deben poder proyectarse a otros sinks.
- Neo4j, si se anade, consume una proyeccion de grafo derivada de extracciones validadas; no recibe texto libre ni salidas LLM sin validar.

## Politica de corpus

- Usar un unico dominio.
- Priorizar fuentes publicas con autor, medio/institucion, fecha y URL.
- Guardar metadatos completos aunque el texto venga de `.txt`, `.md`, `.csv` o PDF.
- Evitar datos personales innecesarios.
- No presentar el corpus como muestra representativa de toda la realidad informativa.
- Mantener una lista de documentos incluidos y descartados con motivo breve.
- No inferir intencion, coordinacion o atribucion geopolitica sin evidencia explicita.

## Trazabilidad

Cada afirmacion del briefing debe poder rastrearse hasta:

- `document_id`;
- titulo y fuente;
- URL si existe;
- fragmento o chunk usado;
- score de recuperacion si procede.

## Consideraciones eticas

- Citar siempre la fuente.
- Mostrar fragmentos breves y enlaces cuando sea posible.
- Incluir limitacion metodologica sobre sesgo de seleccion del corpus.
- Evitar lenguaje que estigmatice colectivos o atribuya intenciones no demostradas.
