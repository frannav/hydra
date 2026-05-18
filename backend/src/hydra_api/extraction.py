"""HYDRA Extraction parser, validator, service, and persistence.

This module provides functions to parse, validate, and persist extraction
data from documents.  It is deliberately lazy — importing this module
does not call models, connect to a database, or load the ontology at import time.

Public API
----------
- parse_extraction_json(text) -> dict
- validate_extraction_payload(payload) -> Extraction
- validate_extraction_payload_with_ontology(payload, ontology) -> Extraction
- ExtractionService
- ExtractionValidationError
- safe_extraction_error(exc) -> str
- save_extraction(conn, extraction) -> None
- export_extraction_json(extraction, output_dir) -> Path
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
from typing import Any

from .schemas import Extraction

# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class ExtractionValidationError(Exception):
    """Raised when extraction parsing or validation fails."""


# ---------------------------------------------------------------------------
# JSON parsing
# ---------------------------------------------------------------------------

def parse_extraction_json(text: str) -> dict[str, Any]:
    """Parse extraction JSON text and return a dict.

    Parameters
    ----------
    text : str
        A JSON string. Must be a JSON object (dict), not an array or scalar.

    Returns
    -------
    dict[str, Any]
        The parsed JSON object.

    Raises
    ------
    ValueError
        If the text is empty, not valid JSON, the root is not an object,
        or the text appears to be markdown-wrapped.
    """
    if not text or not text.strip():
        raise ValueError("Extraction JSON text is empty")

    stripped = text.strip()

    # Reject markdown-wrapped JSON (e.g. ```json ... ```).
    if stripped.startswith("```"):
        raise ValueError(
            "Extraction JSON must not be wrapped in markdown fences"
        )

    try:
        data = json.loads(stripped)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON: {exc}") from exc

    if not isinstance(data, dict):
        raise ValueError(
            f"Extraction JSON root must be an object (dict), "
            f"got {type(data).__name__}"
        )

    return data


# ---------------------------------------------------------------------------
# Pydantic validation
# ---------------------------------------------------------------------------

def validate_extraction_payload(payload: Any) -> Extraction:
    """Validate a dict payload against the Extraction Pydantic schema.

    Parameters
    ----------
    payload : Any
        A dict with at least ``document_id``, ``title``, and ``source``.

    Returns
    -------
    Extraction
        A validated Extraction instance.

    Raises
    ------
    ValueError
        If the payload is not a dict or required fields are missing.
    """
    if not isinstance(payload, dict):
        raise ValueError(
            f"Extraction payload must be a dict, got {type(payload).__name__}"
        )

    try:
        return Extraction(**payload)
    except Exception as exc:
        raise ValueError(
            f"Extraction payload validation failed: {exc}"
        ) from exc


# ---------------------------------------------------------------------------
# Ontology-aware validation
# ---------------------------------------------------------------------------

def validate_extraction_payload_with_ontology(
    payload: dict[str, Any],
    ontology: dict[str, Any],
) -> Extraction:
    """Validate a dict payload against the Extraction schema and ontology.

    First validates with Pydantic, then validates controlled IDs against
    the ontology.

    Parameters
    ----------
    payload : dict
        A dict with at least ``document_id``, ``title``, and ``source``.
    ontology : dict
        A validated ontology dict.

    Returns
    -------
    Extraction
        A validated Extraction instance.

    Raises
    ------
    ValueError
        If Pydantic validation or ontology validation fails.
    """
    extraction = validate_extraction_payload(payload)

    # Import here to avoid import-time dependency on ontology module.
    from .ontology import validate_extraction_against_ontology

    validate_extraction_against_ontology(extraction, ontology)
    return extraction


# ---------------------------------------------------------------------------
# Extraction service
# ---------------------------------------------------------------------------

class ExtractionService:
    """Service for extraction operations.

    Parameters
    ----------
    model_client : Any, optional
        An optional model client for running extractions. If not provided,
        only validation of existing JSON is supported.
    """

    def __init__(self, model_client: Any = None) -> None:
        self.model_client = model_client

    def validate_model_output(
        self,
        text: str,
        ontology: dict[str, Any],
    ) -> Extraction:
        """Validate extraction JSON text against the ontology.

        Parameters
        ----------
        text : str
            JSON text from a model output.
        ontology : dict
            A validated ontology dict.

        Returns
        -------
        Extraction
            A validated Extraction instance.
        """
        data = parse_extraction_json(text)
        return validate_extraction_payload_with_ontology(data, ontology)


# ---------------------------------------------------------------------------
# Safe error handling
# ---------------------------------------------------------------------------

def safe_extraction_error(exc: Exception) -> str:
    """Return a short, safe error message for extraction failures.

    The message does not include the original exception text, payload
    content, or prompts.

    Parameters
    ----------
    exc : Exception
        The original exception.

    Returns
    -------
    str
        A short safe error message.
    """
    return (
        f"Extraction error: {type(exc).__name__}. "
        "See logs for details."
    )


# ---------------------------------------------------------------------------
# Persistence
# ---------------------------------------------------------------------------

def save_extraction(
    conn: Any,
    extraction: Extraction,
) -> None:
    """Save a validated extraction to PostgreSQL.

    Uses parameterized queries aligned with the ``extractions`` table
    schema in ``db_schema.py``.

    Parameters
    ----------
    conn : psycopg connection
        A database connection.
    extraction : Extraction
        A validated Extraction instance.

    Raises
    ------
    ExtractionValidationError
        If the extraction is not valid.
    """
    if not isinstance(extraction, Extraction):
        raise ExtractionValidationError("extraction must be an Extraction instance")

    # Generate a deterministic id from document_id and schema_version.
    extraction_id = f"{extraction.document_id}_extraction_{extraction.schema_version}"

    sql = (
        "INSERT INTO extractions (id, document_id, extraction_json, schema_version) "
        "VALUES (%s, %s, %s, %s) "
        "ON CONFLICT (id) DO UPDATE SET "
        "extraction_json = EXCLUDED.extraction_json, "
        "schema_version = EXCLUDED.schema_version"
    )

    conn.execute(
        sql,
        (
            extraction_id,
            extraction.document_id,
            json.dumps(extraction.model_dump(), ensure_ascii=False),
            extraction.schema_version,
        ),
    )


# ---------------------------------------------------------------------------
# Export
# ---------------------------------------------------------------------------

def export_extraction_json(
    extraction: Extraction,
    output_dir: pathlib.Path,
) -> pathlib.Path:
    """Export an extraction to a JSON file.

    Parameters
    ----------
    extraction : Extraction
        A validated Extraction instance.
    output_dir : Path
        The directory to write the file to (created if it does not exist).

    Returns
    -------
    Path
        The path to the written file.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    file_path = output_dir / f"{extraction.document_id}.extraction.json"
    file_path.write_text(
        json.dumps(extraction.model_dump(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return file_path


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _cli_validate_json(
    json_path: pathlib.Path,
    ontology_path: pathlib.Path | None,
    export_dir: pathlib.Path | None,
) -> None:
    """Validate a JSON extraction file, optionally against an ontology."""
    try:
        text = json_path.read_text(encoding="utf-8")
        data = parse_extraction_json(text)
        extraction = validate_extraction_payload(data)
        print(f"Extraction '{json_path}' passes Pydantic validation.")

        if ontology_path is not None:
            from .ontology import load_ontology, validate_ontology
            ont = validate_ontology(load_ontology(ontology_path))
            extraction = validate_extraction_payload_with_ontology(data, ont)
            print(f"Extraction '{json_path}' passes ontology validation.")

        if export_dir is not None:
            path = export_extraction_json(extraction, export_dir)
            print(f"Exported to {path}")

    except Exception as exc:
        print(f"Validation failed: {exc}", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    """CLI entry point for ``python -m hydra_api.extraction``."""
    parser = argparse.ArgumentParser(
        description="HYDRA extraction parser, validator, and exporter CLI"
    )
    parser.add_argument(
        "--validate-json",
        metavar="JSON_PATH",
        help="Validate a JSON extraction file",
    )
    parser.add_argument(
        "--ontology",
        metavar="ONTOLOGY_PATH",
        help="Path to ontology YAML for controlled ID validation",
    )
    parser.add_argument(
        "--export-dir",
        metavar="EXPORT_DIR",
        help="Directory to export validated extractions to",
    )

    args = parser.parse_args()

    if args.validate_json is not None:
        _cli_validate_json(
            pathlib.Path(args.validate_json),
            pathlib.Path(args.ontology) if args.ontology else None,
            pathlib.Path(args.export_dir) if args.export_dir else None,
        )
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
