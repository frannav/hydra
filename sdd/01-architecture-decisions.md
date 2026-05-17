# 01 - Architecture Decisions

## Decisiones vigentes

| Area | Decision principal | Fallback permitido | No usar en MVP |
|---|---|---|---|
| Frontend | Next.js + Tailwind + pnpm | HTML/Tailwind servido por FastAPI si Next bloquea | Streamlit como UI principal |
| Backend | FastAPI + uv | FastAPI con menos endpoints | Flask, scripts sueltos como producto final |
| RAG DB | PostgreSQL + pgvector | FAISS/Chroma solo si pgvector bloquea la entrega | Neo4j como dependencia core |
| Ingesta | Corpus local con servicio backend desacoplado | Upload frontend si sobra tiempo | No parsing/chunking/modelos en frontend |
| Grafo | GraphProjection JSON desde extracciones validadas | Neo4j como sink secundario | Neo4j como fuente de verdad del MVP |
| Modelos | API de modelos compatible con OpenAI, `qwen3.6`, `qwen3-embedding` | `gemma4` como revisor o mismo `qwen3.6` para todo | Modelos locales pesados |
| Observabilidad | Langfuse Cloud | logs locales + JSON si no hay claves | Langfuse self-hosted como camino principal |
| SDD | Markdown manual en `hydra/sdd/` | checklist reducido si falta tiempo | OpenSpec en esta fase |

## Dependencias obligatorias

- Backend Python con `uv`.
- Frontend con `pnpm`.
- PostgreSQL + pgvector con Docker Compose.
- LangChain / LCEL.
- Pydantic.
- Langfuse Cloud.
- API de modelos compatible con OpenAI.

## Desacoplamiento obligatorio

- El pipeline de ingesta debe aceptar fuentes intercambiables (`local_corpus` primero, `frontend_upload` si sobra tiempo).
- El frontend no ejecuta parsing, chunking, embeddings, extraccion ni llamadas a modelos.
- Las extracciones validadas son el artefacto canonico para RAG, briefing, evals y proyeccion de grafo.
- PostgreSQL/pgvector es el storage principal, pero no debe contaminar los schemas canonicos.
- Neo4j solo puede anadirse como sink secundario de `GraphProjection`, nunca como dependencia core del MVP.

## Secretos

- `hydra/back/.env` para secretos reales del backend.
- `hydra/front/.env.local` solo para variables publicas del frontend.
- Versionar solo `hydra/.env.example`, `hydra/back/.env.example` y `hydra/front/.env.local.example`.
- No colocar `MODEL_API_KEY`, `LANGFUSE_SECRET_KEY` ni `DATABASE_URL` en frontend.

## Variables principales

```bash
MODEL_API_KEY=replace_me
MODEL_API_BASE_URL=https://model-provider.example/v1
HYDRA_CHAT_MODEL=qwen3.6
HYDRA_REVIEW_MODEL=gemma4
HYDRA_EMBEDDING_MODEL=qwen3-embedding

LANGFUSE_PUBLIC_KEY=replace_me
LANGFUSE_SECRET_KEY=replace_me
LANGFUSE_BASE_URL=https://cloud.langfuse.com

DATABASE_URL=postgresql+psycopg://hydra:hydra@localhost:5432/hydra
```
