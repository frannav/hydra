"""HYDRA API — FastAPI application."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from hydra_api.errors import HydraError, http_exception_handler, hydra_error_handler
from hydra_api.logging import setup_logging

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
