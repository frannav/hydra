# AGENTS.md — HYDRA RAG Mission

## Mission Boundaries (NEVER VIOLATE)

**Port Range:** 3100-3199. Never start services outside this range.

**External Services:**
- USE existing PostgreSQL on localhost:5432 if available (for SQL verification only)
- DO NOT call any LLM provider API
- DO NOT connect to Neo4j

**Off-Limits:**
- `frontend/**` — never modify
- `docs/**` — never modify
- `sdd/**` — never modify (execution only)
- Any real `.env` file — never create or modify
- Real corpus documents — never download, scrape, or use
- Real extraction outputs from model calls — never create

**Allowed files:**
- `backend/pyproject.toml`, `backend/uv.lock`
- `backend/src/hydra_api/schemas.py`, `errors.py`, `main.py`
- `backend/src/hydra_api/rag_config.py`, `rag_embeddings.py`, `rag_store.py`, `rag_indexing.py`, `rag_retriever.py`, `rag_answering.py`, `rag_service.py`

## Important Coding Conventions

- All modules must be lazy — no import-time side effects (no file reads, DB connections, model calls)
- Use `HYDRA_EMBEDDING_MODEL` via Settings, not `OPENAI_API_KEY`
- Use parameterized SQL (`%s` or `%(name)s`) — never f-strings for SQL values
- Embedding dimension strictly 4096 — validate before persisting or querying
- Cosine distance converted to score: `1 - cosine_distance`
- Evidence truncated to `EVIDENCE_SNIPPET_CHARS` — never return full documents
- `top_k` defaults to 5, rejects `<= 0`
- Empty questions rejected via Pydantic validation
- No-context path returns `QueryResponse` with limitations, no model call
- `trace_id` is local-safe if no Langfuse
- Safe error handling: no secrets, headers, stack traces, prompts, or full LLM outputs

## Testing & Validation Guidance

All verification is done via inline `uv run python -c "..."` commands defined in the SDD tasks.

**For validators:**
- Run all milestone verification commands from the validation contract
- Negative tests (commands that should fail) use `!` prefix — verify they exit with non-zero
- For CLI tests, verify `--help` works and expected output appears
- For SQL schema verification, inspect source code with `inspect.getsource()`
- For Neo4j absence, grep module files for 'neo4j'
- For embedding dimension, verify exactly 4096 floats
- For FastAPI endpoint tests, use `TestClient` with injected fakes

**Resource constraints:**
- Max concurrent validators: 1 (all validators share the same backend directory)
- No web server or browser needed
- No test framework — all verification is inline Python
