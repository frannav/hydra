"""HYDRA API — FastAPI application."""

from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from hydra_api.errors import HydraError, http_exception_handler, hydra_error_handler
from hydra_api.logging import setup_logging
from hydra_api.schemas import QueryRequest, QueryResponse

setup_logging()

app = FastAPI(title="hydra-api")

# CORS — allow frontend local in development.
# In production, restrict origins via configuration.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(HydraError, hydra_error_handler)
app.add_exception_handler(HTTPException, http_exception_handler)


@app.get("/health")
def healthcheck() -> dict:
    """Health check endpoint."""
    return {"status": "ok", "service": "hydra-api"}


@app.post("/query")
def query(request: QueryRequest) -> QueryResponse:
    """Answer a question using the RAG pipeline.

    The service is injected via ``app.state.query_service`` for
    testability.  When not injected, returns a 503 error.
    """
    query_service = getattr(app.state, "query_service", None)
    if query_service is None:
        from hydra_api.rag_service import create_query_service

        query_service = create_query_service()

    try:
        return query_service.query(request)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="An internal error occurred while processing the query.",
        )
