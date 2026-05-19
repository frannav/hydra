# Environment

Environment variables, external dependencies, and setup notes.

**What belongs here:** Required env vars, external API keys/services, dependency quirks.
**What does NOT belong here:** Service ports/commands (use `services.yaml`).

---

## Environment Variables

- `MODEL_API_KEY` — Model API key (used by `create_embedding_model`, `create_chat_model`)
- `MODEL_API_BASE_URL` — Model API base URL (default: `https://model-provider.example/v1`)
- `HYDRA_EMBEDDING_MODEL` — Embedding model name (default: `qwen3-embedding`)
- `HYDRA_CHAT_MODEL` — Chat model name (default: `qwen3.6`)
- `DATABASE_URL` — PostgreSQL connection string

No environment variables are required for milestone validation — all testing uses fakes and injectable dependencies.

## Dependencies

- **langchain-core** — LCEL abstractions for retrievers and chains
- **langchain-openai** — OpenAI-compatible chat model and embeddings client
- **pgvector** — PostgreSQL vector similarity extension (used via SQL, not as a Python library dependency for the MVP)
- **PyYAML** — Already added in ontology mission
- **uv** — Package manager for backend (already installed)
- **Python 3.12+** — Required by `pyproject.toml`

## Tooling

- `uv run python -c "..."` — For inline verification commands
- `uv run python -m hydra_api.*` — For CLI verification (if applicable)
- `fastapi.testclient.TestClient` — For FastAPI endpoint testing with fakes
