---
name: backend-worker
description: Worker for implementing HYDRA backend RAG pipeline modules
---

# Backend Worker

NOTE: Startup and cleanup are handled by `worker-base`. This skill defines the WORK PROCEDURE.

## When to Use This Skill

Use this worker for all backend RAG implementation tasks:
- RAG dependencies, constants, QueryRequest validation
- Embedding factory and vector validation
- RAG store (pending chunks, embedding update, vector search)
- RAG indexing service
- Retriever (normalizer, LCEL component)
- Answering (prompt, chat model, answer chain, no-context response)
- Query service and POST /query endpoint

## Required Skills, Tools, and Dependencies

- **Skills:** None to invoke during work
- **Tools/CLIs:**
  - `uv run python -c "..."` — For all inline verification
  - `uv sync` — For dependency installation
  - `grep` — For file content verification
  - `inspect.getsource()` — For SQL schema inspection
  - `fastapi.testclient.TestClient` — For FastAPI endpoint testing with fakes
- **Packages/libraries:**
  - `langchain-core` — LCEL abstractions
  - `langchain-openai` — OpenAI-compatible chat/embeddings
  - `pgvector` — PostgreSQL vector extension (SQL-level)
  - `pydantic` — Schema validation
  - `pydantic-settings` — Settings management
  - `fastapi` — API framework (already installed)
  - `httpx` — Test client (already in dev deps)

## Work Procedure

### 1. Read Mission Guidance
- Read `AGENTS.md` for mission boundaries and conventions
- Read the feature description from `features.json`
- Read the validation contract (`validation-contract.md`) for assertions this feature must satisfy
- Read `library/architecture.md` for system context

### 2. Understand Existing Code
- Read `backend/src/hydra_api/schemas.py` for Pydantic schemas (QueryRequest, QueryResponse, RetrievedDocument, Settings, etc.)
- Read `backend/src/hydra_api/db_schema.py` for PostgreSQL schema (document_chunks with vector(4096))
- Read `backend/src/hydra_api/main.py` for existing FastAPI app structure
- Read `backend/src/hydra_api/errors.py` for existing error handling
- Read `backend/src/hydra_api/config.py` for existing Settings
- Check if any files from the allowed list already exist

### 3. Implement Feature
- Follow the task descriptions from `sdd/tasks/05-rag/05-rag.md`
- Respect file boundaries — only create/modify allowed files
- Follow coding conventions: lazy imports, 4096 dimension, parameterized SQL, safe errors
- Use existing Settings vars (`MODEL_API_KEY`, `MODEL_API_BASE_URL`, `HYDRA_EMBEDDING_MODEL`, `HYDRA_CHAT_MODEL`)

### 4. Write Verification Commands
- Run ALL verification commands from the feature's `verificationSteps` in `features.json`
- For negative tests (commands that should fail), verify they exit with non-zero code
- For FastAPI endpoint tests, use `TestClient` with injected fakes
- For SQL schema verification, inspect source code with `inspect.getsource()`
- For Neo4j absence, grep module files for 'neo4j'

### 5. Verify No Violations
- Confirm no frontend files were modified
- Confirm no SDD files were modified
- Confirm no real `.env` files were created
- Confirm no Neo4j references in any created module
- Confirm no secrets in any created file
- Confirm no import-time side effects (modules import cleanly)
- Confirm embedding dimension is exactly 4096
- Confirm `top_k` defaults to 5 and rejects `<= 0`

### 6. Commit Implementation Changes
- Commit all implementation changes with a descriptive message
- Do NOT commit missionDir artifacts

### 7. Prepare Handoff
- Record all verification commands run with exit codes and observations
- Note any discovered issues
- Note any work left undone

## Example Handoff

```json
{
  "salientSummary": "Implemented RAG dependencies and QueryRequest validation. Added langchain-core, langchain-openai, pgvector to pyproject.toml. Created rag_config.py with constants. Enhanced QueryRequest with question/top_k validation. All 4 verification commands passed.",
  "whatWasImplemented": "Added langchain-core, langchain-openai, pgvector to pyproject.toml (no neo4j). Created rag_config.py with EMBEDDING_DIMENSION=4096, DEFAULT_TOP_K=5, EVIDENCE_SNIPPET_CHARS=500. Enhanced QueryRequest in schemas.py: rejects empty/whitespace-only questions, validates top_k >= 1, defaults to 5.",
  "whatWasLeftUndone": "",
  "verification": {
    "commandsRun": [
      {"command": "cd backend && uv sync", "exitCode": 0, "observation": "Dependencies installed successfully"},
      {"command": "cd backend && uv run python -c \"from langchain_core.runnables import RunnableLambda; from langchain_openai import ChatOpenAI, OpenAIEmbeddings; import pgvector; print('rag deps ok')\"", "exitCode": 0, "observation": "RAG dependencies importable"},
      {"command": "cd backend && uv run python -c \"from hydra_api.rag_config import EMBEDDING_DIMENSION, DEFAULT_TOP_K, EVIDENCE_SNIPPET_CHARS; assert EMBEDDING_DIMENSION==4096 and DEFAULT_TOP_K==5 and EVIDENCE_SNIPPET_CHARS>0\"", "exitCode": 0, "observation": "RAG constants correct"},
      {"command": "cd backend && uv run python -c \"from pydantic import ValidationError; from hydra_api.schemas import QueryRequest; assert QueryRequest(question='q').top_k==5\"", "exitCode": 0, "observation": "QueryRequest validation works"}
    ]
  },
  "tests": {"added": []},
  "discoveredIssues": [],
  "commitId": "abc1234",
  "repoPath": "/Users/frannav/dev/master-ia-the-bridge/tfm-project/hydra"
}
```

## When to Return to Orchestrator

- A required dependency from the SDD is missing and cannot be installed
- A verification command fails after reasonable debugging and cannot be fixed
- The feature requires files outside the allowed list
- You discover that db_schema.py columns don't match what the task expects
- The chosen RAG library forces creation of tables parallel to `document_chunks`
