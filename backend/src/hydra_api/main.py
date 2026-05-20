"""HYDRA API — FastAPI application."""

from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from hydra_api.errors import HydraError, http_exception_handler, hydra_error_handler
from hydra_api.evals_config import EVAL_RESULTS_PATH
from hydra_api.logging import setup_logging
from hydra_api.schemas import (
    BriefingRequest,
    BriefingResponse,
    EvalRunRequest,
    EvalRunResponse,
    EvalResultsResponse,
    QueryRequest,
    QueryResponse,
)

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
    testability.  When not injected, constructs the real service
    lazily at request time.
    """
    query_service = getattr(app.state, "query_service", None)
    try:
        if query_service is None:
            from hydra_api.rag_service import create_query_service

            query_service = create_query_service()
            app.state.query_service = query_service

        return query_service.query(request)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="An internal error occurred while processing the query.",
        )


@app.post("/briefing", response_model=BriefingResponse)
def briefing(request: BriefingRequest) -> BriefingResponse:
    """Build a traceable briefing for a question.

    The service is injected via ``app.state.briefing_service`` for
    testability.  When not injected, constructs the real service
    lazily at request time.

    Errors are surfaced with a generic message — no stack traces
    or internal details are exposed to the client.
    """
    briefing_service = getattr(app.state, "briefing_service", None)
    try:
        if briefing_service is None:
            from hydra_api.briefing_service import BriefingService
            from hydra_api.council_service import create_council_service
            from hydra_api.rag_service import create_query_service

            query_service = create_query_service()
            council_service = create_council_service()
            briefing_service = BriefingService(
                query_service=query_service,
                council_service=council_service,
            )
            app.state.briefing_service = briefing_service

        return briefing_service.brief(request)
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="An internal error occurred while building the briefing.",
        )


@app.post("/evals/run", response_model=EvalRunResponse)
def evals_run(request: EvalRunRequest) -> EvalRunResponse:
    """Run evaluation cases.

    The service is injected via ``app.state.eval_service`` for
    testability.  When not injected, returns a safe error.

    Errors are surfaced with a generic message — no stack traces
    or internal details are exposed to the client.
    """
    eval_service = getattr(app.state, "eval_service", None)
    try:
        if eval_service is None:
            raise HTTPException(
                status_code=500,
                detail="Eval service is not configured.",
            )
        result = eval_service.run(request)

        # Coerce the result to a proper EvalRunResponse.
        # Handle fakes that may not have all fields.
        results = getattr(result, "results", [])
        total_cases = getattr(result, "total_cases", len(results))
        results_path = getattr(result, "results_path", EVAL_RESULTS_PATH)
        trace_id = getattr(result, "trace_id", None)
        run_id = getattr(result, "run_id", "")

        return EvalRunResponse(
            run_id=run_id,
            total_cases=total_cases,
            results_path=results_path,
            trace_id=trace_id,
            results=results,
        )
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="An internal error occurred while running evals.",
        )


@app.get("/evals/results", response_model=EvalResultsResponse)
def evals_results() -> EvalResultsResponse:
    """Return the last exported eval results.

    Reads the last exported ``eval_results.json`` from disk.
    When no results file exists, returns an empty response.

    Errors are surfaced with a generic message — no stack traces
    or internal details are exposed to the client.
    """
    from hydra_api.evals_config import resolve_eval_results_path

    try:
        import json

        results_path = resolve_eval_results_path()
        if not results_path.exists():
            return EvalResultsResponse(run_id="", results=[])

        text = results_path.read_text(encoding="utf-8")
        data = json.loads(text)

        run_id = data.get("run_id", "")
        results_data = data.get("results", [])

        # Reconstruct EvalResult objects from dicts.
        from hydra_api.schemas import EvalMetrics, EvalResult

        results = []
        for r in results_data:
            metrics_data = r.get("metrics", {})
            metrics = EvalMetrics(
                precision_at_k=metrics_data.get("precision_at_k", 0.0),
                json_validity=metrics_data.get("json_validity", True),
                groundedness=metrics_data.get("groundedness", "pass"),
                ontology_mapping=metrics_data.get("ontology_mapping"),
                coordination_caution=metrics_data.get("coordination_caution"),
                latency_ms=metrics_data.get("latency_ms"),
                cost=metrics_data.get("cost"),
            )
            results.append(
                EvalResult(
                    eval_case_id=r.get("eval_case_id", ""),
                    metrics=metrics,
                    passed=r.get("passed", True),
                    trace_id=r.get("trace_id"),
                )
            )

        return EvalResultsResponse(run_id=run_id, results=results)
    except Exception:
        return EvalResultsResponse(run_id="", results=[])
