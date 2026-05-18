"""HYDRA API — Common error handling."""

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse


class HydraError(Exception):
    """Base exception for HYDRA API errors."""

    def __init__(self, code: str, message: str, details: dict | None = None) -> None:
        self.code = code
        self.message = message
        self.details = details or {}


class MissingConfigurationError(HydraError):
    """Raised when a required configuration variable is missing."""

    def __init__(self, missing: list[str]) -> None:
        super().__init__(
            code="missing_configuration",
            message="Required configuration is missing.",
            details={"missing": missing},
        )


class InvalidInputError(HydraError):
    """Raised when client input is invalid."""

    def __init__(self, message: str, details: dict | None = None) -> None:
        super().__init__(code="invalid_input", message=message, details=details or {})


class NotFoundError(HydraError):
    """Raised when a requested resource is not found."""

    def __init__(self, resource: str) -> None:
        super().__init__(
            code="not_found",
            message=f"Resource '{resource}' not found.",
        )


class InternalError(HydraError):
    """Raised when an unexpected internal error occurs."""

    def __init__(self) -> None:
        super().__init__(
            code="internal_error",
            message="An unexpected internal error occurred.",
        )


def error_response(code: str, message: str, details: dict | None = None) -> dict:
    """Build a standardized error response body."""
    return {"error": {"code": code, "message": message, "details": details or {}}}


async def hydra_error_handler(request: Request, exc: HydraError) -> JSONResponse:
    """Handle HydraError exceptions with a consistent JSON response."""
    status_code = {
        MissingConfigurationError: 500,
        InvalidInputError: 400,
        NotFoundError: 404,
        InternalError: 500,
    }.get(type(exc), 500)

    return JSONResponse(
        status_code=status_code,
        content=error_response(exc.code, exc.message, exc.details),
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Wrap FastAPI HTTPException in the common error format."""
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response(
            code="http_error",
            message=exc.detail if isinstance(exc.detail, str) else str(exc.detail),
        ),
    )
