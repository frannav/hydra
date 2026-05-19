"""HYDRA API — Evaluation service helpers.

This module provides safe loading and validation of evaluation cases
from JSON files.  It has **no import-time side effects**: no ``.env``
loading, no network calls, no file I/O.
"""

from __future__ import annotations

import json
import pathlib
from typing import Any

from .evals_config import EVAL_CASES_PATH
from .schemas import EvalCase


# ---------------------------------------------------------------------------
# Allowed base directory for eval case files
# ---------------------------------------------------------------------------

_ALLOWED_BASE: pathlib.Path = pathlib.Path("data")


# ---------------------------------------------------------------------------
# load_eval_cases
# ---------------------------------------------------------------------------


def load_eval_cases(path: str | pathlib.Path | None = None) -> list[EvalCase]:
    """Load and validate evaluation cases from a JSON file.

    Parameters
    ----------
    path : str | pathlib.Path | None
        Absolute or relative path to a JSON file containing a list of
        eval case objects.  When ``None``, resolves to
        :data:`evals_config.EVAL_CASES_PATH`.

    Returns
    -------
    list[EvalCase]
        A list of validated :class:`EvalCase` objects.

    Raises
    ------
    ValueError
        When the file cannot be read, JSON is invalid, the top-level
        value is not a list, required fields are missing, IDs are
        duplicated, the list is empty, or ``expected_documents`` is
        empty without a ``no_expected_documents`` tag.
    """
    # --- Resolve path ---------------------------------------------------
    if path is None:
        path = EVAL_CASES_PATH

    resolved = pathlib.Path(path)

    # --- Reject path traversal in the original string -------------------
    if ".." in resolved.parts:
        raise ValueError(f"Path traversal not allowed: {path}")

    # --- Resolve to absolute for safety checks --------------------------
    resolved = resolved.resolve()

    # --- Ensure the resolved path is under the allowed base -------------
    try:
        resolved.relative_to(_ALLOWED_BASE.resolve())
    except ValueError:
        raise ValueError(
            f"Eval cases path must be relative to '{_ALLOWED_BASE}': {path}"
        )

    # --- Read and parse JSON --------------------------------------------
    try:
        text = resolved.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise ValueError(f"Eval cases file not found: {path}")
    except OSError as exc:
        raise ValueError(f"Cannot read eval cases file: {exc}")

    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in eval cases file: {exc}")

    # --- Validate top-level is a list -----------------------------------
    if not isinstance(data, list):
        raise ValueError(
            f"Eval cases file must contain a JSON array, got {type(data).__name__}"
        )

    # --- Reject empty list ----------------------------------------------
    if len(data) == 0:
        raise ValueError("Eval cases list must not be empty")

    # --- Validate each case ---------------------------------------------
    required_fields = {"id", "question", "expected_documents", "expected_topics", "expected_answer_traits", "tags"}
    seen_ids: set[str] = set()
    cases: list[EvalCase] = []

    for index, item in enumerate(data):
        if not isinstance(item, dict):
            raise ValueError(
                f"Eval case at index {index} is not an object (dict)"
            )

        # Check required fields
        missing = required_fields - set(item.keys())
        if missing:
            raise ValueError(
                f"Eval case at index {index} (id='{item.get('id', '<unknown>')}') "
                f"missing required fields: {sorted(missing)}"
            )

        # Reject duplicate IDs
        case_id: str = item["id"]
        if case_id in seen_ids:
            raise ValueError(
                f"Duplicate eval case ID: '{case_id}'"
            )
        seen_ids.add(case_id)

        # Reject expected_documents=[] without limitation tag
        expected_docs = item.get("expected_documents", [])
        tags = item.get("tags", [])
        if not expected_docs and "no_expected_documents" not in tags:
            raise ValueError(
                f"Eval case '{case_id}' has empty expected_documents "
                "without a 'no_expected_documents' tag"
            )

        cases.append(EvalCase(**item))

    return cases
