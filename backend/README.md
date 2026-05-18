# HYDRA API Backend

FastAPI-based backend for the HYDRA project — a proof of concept for turning a closed corpus of public sources into traceable narrative intelligence.

## Prerequisites

- Python 3.12 or later
- [uv](https://docs.astral.sh/uv/) (Python package manager)

## Setup

```bash
# Install dependencies
uv sync

# Copy the example environment file and fill in real values
cp .env.example .env
```

### Environment Variables

See `.env.example` for the full list. Key variables:

| Variable | Description |
|---|---|
| `MODEL_API_KEY` | API key for the model provider |
| `MODEL_API_BASE_URL` | Base URL for the model API (OpenAI-compatible) |
| `HYDRA_CHAT_MODEL` | Model used for chat completions (default: `qwen3.6`) |
| `HYDRA_REVIEW_MODEL` | Model used for review tasks (default: `gemma4`) |
| `HYDRA_EMBEDDING_MODEL` | Model used for embeddings (default: `qwen3-embedding`) |
| `LANGFUSE_PUBLIC_KEY` | Langfuse tracing public key |
| `LANGFUSE_SECRET_KEY` | Langfuse tracing secret key |
| `LANGFUSE_BASE_URL` | Langfuse API base URL (default: `https://cloud.langfuse.com`) |
| `DATABASE_URL` | PostgreSQL connection string |

## Running

```bash
# Start the development server
uv run uvicorn hydra_api.main:app --reload

# Start with a custom host/port
uv run uvicorn hydra_api.main:app --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`. API documentation (Swagger UI) is at `http://localhost:8000/docs`.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check — returns `{"status": "ok", "service": "hydra-api"}` |

## Testing

```bash
# Verify the app with httpx (included in dev dependencies)
uv run python -c "from fastapi.testclient import TestClient; from hydra_api.main import app; print(TestClient(app).get('/health').json())"
```

## Project Structure

```
backend/
├── src/hydra_api/
│   ├── __init__.py          # Package init
│   ├── config.py            # Settings (pydantic-settings)
│   ├── errors.py            # Custom exceptions and error handlers
│   ├── logging.py           # Safe logging with sensitive value masking
│   ├── main.py              # FastAPI application entry point
│   ├── model_client.py      # OpenAI-compatible model client wrapper
│   └── schemas.py           # Pydantic request/response schemas
├── .env.example             # Example environment variables
├── pyproject.toml           # Project metadata and dependencies
└── uv.lock                  # Locked dependency tree
```

## Security

- Logging uses `_SensitiveFormatter` which masks values when logged through structured dict arguments with sensitive keys (`api_key`, `secret`, `token`, `password`, `authorization`, `key`).
- Masked values show only the first and last 4 characters.
- API keys and secrets must be stored in a local `.env` file and must not be committed.
