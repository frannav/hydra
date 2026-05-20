"""HYDRA API — Evaluation configuration constants.

This module provides module-level constants for evaluation paths,
default parameters, and metric thresholds. It has **no import-time
side effects**: no ``.env`` loading, no network calls, no file I/O.
"""

from __future__ import annotations

import pathlib

# ---------------------------------------------------------------------------
# Paths (relative to the project root / backend working directory)
# ---------------------------------------------------------------------------

EVAL_CASES_PATH: str = "hydra/backend/data/evals/eval_cases.json"
EVAL_RESULTS_PATH: str = "hydra/backend/data/outputs/eval_results.json"

# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------

DEFAULT_EVAL_TOP_K: int = 5

# ---------------------------------------------------------------------------
# Metric thresholds (values >= threshold are considered "passing")
# ---------------------------------------------------------------------------

THRESHOLD_PRECISION_AT_K: float = 0.5
THRESHOLD_JSON_VALIDITY: bool = True
THRESHOLD_GROUNDEDNESS: str = "pass"
THRESHOLD_ONTOLOGY_MAPPING: bool = True
THRESHOLD_COORDINATION_CAUTION: bool = True


# ---------------------------------------------------------------------------
# Path resolution helpers
# ---------------------------------------------------------------------------

# Resolve relative to the backend project root (one level above this module's parent).
# This makes paths deterministic regardless of CWD.
_MODULE_DIR = pathlib.Path(__file__).resolve().parent  # backend/src/hydra_api/
_BACKEND_ROOT = _MODULE_DIR.parent.parent  # backend/


def resolve_eval_cases_path(path: str | pathlib.Path | None = None) -> pathlib.Path:
    """Resolve eval cases path deterministically.

    Uses the backend project root, not CWD.
    """
    if path is None:
        path = EVAL_CASES_PATH
    p = pathlib.Path(path)
    # Strip "hydra/backend/" prefix if present.
    parts = p.parts
    if len(parts) >= 2 and parts[0] == "hydra" and parts[1] == "backend":
        parts = parts[2:]
    elif len(parts) >= 1 and parts[0] == "hydra":
        parts = parts[1:]
    return (_BACKEND_ROOT / pathlib.Path(*parts)).resolve()


def resolve_eval_results_path(path: str | pathlib.Path | None = None) -> pathlib.Path:
    """Resolve eval results path deterministically.

    Uses the backend project root, not CWD.
    """
    if path is None:
        path = EVAL_RESULTS_PATH
    p = pathlib.Path(path)
    parts = p.parts
    if len(parts) >= 2 and parts[0] == "hydra" and parts[1] == "backend":
        parts = parts[2:]
    elif len(parts) >= 1 and parts[0] == "hydra":
        parts = parts[1:]
    return (_BACKEND_ROOT / pathlib.Path(*parts)).resolve()


def _resolve_eval_path(rel_path: str) -> pathlib.Path:
    """Legacy resolver — deprecated, use resolve_eval_cases_path or resolve_eval_results_path."""
    return resolve_eval_results_path(rel_path)
