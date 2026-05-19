# User Testing

## Validation Surface

This mission has no user-facing UI surface. All validation is through:

- **CLI tools:** `uv run python -c "..."` for inline verification
- **Import checks:** Modules must import without side effects
- **Fake service testing:** FastAPI TestClient with injected fakes
- **SQL schema alignment:** Source code inspection for SQL correctness
- **Vector dimension validation:** Inline Python checks for 4096 floats

## Validation Prerequisites

- `uv` installed and functional
- Python 3.12+ available
- `langchain-core`, `langchain-openai`, `pgvector` available after TASK-RAG-002 adds them

All verification commands use `uv run python -c "..."` or `fastapi.testclient.TestClient`.

## Validation Concurrency

**Max concurrent validators: 1**

This mission is entirely backend Python with no web server, browser, or TUI surface. Validators run `uv run python -c` commands sequentially. There is no resource contention concern — concurrency is limited to 1 because all validators share the same `backend/` directory and Python environment, and parallel `uv run` invocations could conflict on dependency resolution.
