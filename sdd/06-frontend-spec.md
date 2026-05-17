# 06 - Frontend Spec

## Decision

Frontend recomendado: Next.js + Tailwind + pnpm.

Fallback: HTML/Tailwind servido por FastAPI si Next bloquea la entrega.

## Variables permitidas

```bash
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

No se permiten secretos en frontend.

## Dependencias de API

- Corpus: `GET /documents`.
- Narrativas: `GET /narratives`.
- HYDRA Analyst: `POST /query`.
- Briefing: `POST /briefing`.
- Evals: `POST /evals/run` y `GET /evals/results`.
- Subida opcional de documentos: `POST /documents/upload`.

## Vistas

### Corpus

- Lista de documentos.
- Fuente.
- Fecha.
- Estado de procesamiento.

### Narrativas

- Tabla de narrativas.
- Actores.
- Sectores.
- Riesgo.
- Confianza.
- Evidencias.

### HYDRA Analyst

- Input de pregunta.
- Estado loading/error.
- Respuesta estructurada.
- Documentos recuperados.
- Evidencias.
- `trace_id`.

### Briefing

- Markdown renderizado.
- Riesgo.
- Limitaciones.
- Council review si existe.

### Evals

- Lista de eval cases.
- Resultados.
- Scores.
- Trace IDs.

### Subida de documentos (extension opcional)

Solo se implementa si el pipeline principal ya funciona.

- Formulario de archivo + metadatos minimos.
- Formatos iniciales: `.txt`, `.md` o `.csv`.
- Envio a `POST /documents/upload`.
- Mostrar `processing_status`.
- No parsear documentos en frontend.
- No hacer chunking, embeddings ni llamadas a modelos desde frontend.
- PDF queda fuera salvo que no bloquee el MVP.

## Reglas UI

- No usar landing page.
- Primera pantalla: experiencia funcional.
- Interfaz densa, clara y orientada a analista.
- No exponer prompts internos ni secretos.
- No exponer claves privadas ni endpoints directos de proveedores LLM.
- La subida de documentos, si existe, es una entrada al pipeline del backend, no un pipeline paralelo.
