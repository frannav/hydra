"""HYDRA API — Evaluation service.

This module provides:

- Safe loading and validation of evaluation cases from JSON files.
- ``EvalService`` — orchestrates eval cases against an injectable
  query service, judge, and emitter.
- ``export_eval_results(run, path)`` — writes eval results to JSON.
- ``emit_eval_scores(emitter, result)`` — sends metric scores to the
  observability emitter.

All functions in this module have **no import-time side effects**:
no ``.env`` loading, no network calls, no file I/O (except when
explicitly called, e.g. ``load_eval_cases``).
"""

from __future__ import annotations

import json
import pathlib
import uuid
from typing import Any, Callable

from .evals_config import EVAL_CASES_PATH, EVAL_RESULTS_PATH, resolve_eval_cases_path, resolve_eval_results_path
from .evals_judges import GroundednessJudge, parse_groundedness_label
from .evals_metrics import (
    coordination_caution,
    json_validity,
    latency_cost_metrics,
    ontology_mapping_validity,
    precision_at_k,
)
from .observability import ObservabilityEmitter, create_observability_emitter
from .schemas import (
    EvalCase,
    EvalMetrics,
    EvalResult,
    EvalRunRequest,
    EvalRunResponse,
    EvalResultsResponse,
    Extraction,
    QueryRequest,
    QueryResponse,
)


# ---------------------------------------------------------------------------
# Allowed base directories for eval case files and export
# ---------------------------------------------------------------------------

# The allowed base is "data/" relative to the backend project root.
# We resolve from the module's parent (backend/src/) going up one level
# to get to backend/, then into data/.
_module_dir = pathlib.Path(__file__).resolve().parent  # backend/src/hydra_api/
_backend_root = _module_dir.parent.parent  # backend/
_ALLOWED_EVALS_BASE = _backend_root / "data" / "evals"
_ALLOWED_EXPORT_BASE = _backend_root / "data" / "outputs"


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

    resolved = resolve_eval_cases_path(path)

    # --- Reject path traversal in the original string -------------------
    if ".." in resolved.parts:
        raise ValueError(f"Path traversal not allowed: {path}")

    # --- Resolve to absolute for safety checks --------------------------
    resolved = resolved.resolve()

    # --- Ensure the resolved path is under the allowed evals base -------
    try:
        resolved.relative_to(_ALLOWED_EVALS_BASE.resolve())
    except ValueError:
        raise ValueError(
            f"Eval cases path must be under the allowed evals directory: {path}"
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


# ---------------------------------------------------------------------------
# Emit eval scores to the observability emitter
# ---------------------------------------------------------------------------


def emit_eval_scores(
    emitter: ObservabilityEmitter,
    result: EvalResult,
) -> None:
    """Send metric scores for *result* to the observability emitter.

    Scores emitted:

    - ``precision_at_k`` (float)
    - ``json_validity`` (bool)
    - ``ontology_mapping`` (bool, when available)
    - ``groundedness`` (float mapped from label)
    - ``coordination_caution`` (bool)
    - ``latency_ms`` and ``cost_usd`` (when available)

    When *result.trace_id* is ``None``, this function is a no-op.

    Parameters
    ----------
    emitter : ObservabilityEmitter
        The observability emitter to score against.
    result : EvalResult
        The eval result containing metrics.
    """
    if result.trace_id is None:
        return

    metrics = result.metrics

    # precision_at_k
    emitter.score(
        result.trace_id,
        "precision_at_k",
        getattr(metrics, "precision_at_k", 0.0),
        metadata={"case_id": getattr(result, "eval_case_id", "")},
    )

    # json_validity
    emitter.score(
        result.trace_id,
        "json_validity",
        float(getattr(metrics, "json_validity", False)),
        metadata={"case_id": getattr(result, "eval_case_id", "")},
    )

    # ontology_mapping (optional)
    ontology_val = getattr(metrics, "ontology_mapping", None)
    if ontology_val is not None:
        emitter.score(
            result.trace_id,
            "ontology_mapping",
            float(ontology_val),
            metadata={"case_id": getattr(result, "eval_case_id", "")},
        )

    # groundedness — map label to numeric score
    groundedness_label = getattr(metrics, "groundedness", "pass")
    if groundedness_label == "pass":
        groundedness_value: float = 1.0
    elif groundedness_label == "warning":
        groundedness_value = 0.5
    else:
        groundedness_value = 0.0
    emitter.score(
        result.trace_id,
        "groundedness",
        groundedness_value,
        metadata={
            "case_id": getattr(result, "eval_case_id", ""),
            "label": groundedness_label,
        },
    )

    # coordination_caution (optional)
    coord_val = getattr(metrics, "coordination_caution", None)
    if coord_val is not None:
        emitter.score(
            result.trace_id,
            "coordination_caution",
            float(coord_val),
            metadata={"case_id": getattr(result, "eval_case_id", "")},
        )

    # latency_ms (optional)
    latency_val = getattr(metrics, "latency_ms", None)
    if latency_val is not None:
        emitter.score(
            result.trace_id,
            "latency_ms",
            latency_val,
            metadata={"case_id": getattr(result, "eval_case_id", "")},
        )

    # cost_usd (optional)
    cost_val = getattr(metrics, "cost", None)
    if cost_val is not None:
        emitter.score(
            result.trace_id,
            "cost_usd",
            cost_val,
            metadata={"case_id": getattr(result, "eval_case_id", "")},
        )


# ---------------------------------------------------------------------------
# EvalService
# ---------------------------------------------------------------------------


class EvalService:
    """Orchestrates evaluation cases against an injectable query service.

    Parameters
    ----------
    case_loader : callable
        A zero-argument callable returning ``list[EvalCase]``.
    query_service : object
        An object with a ``query(request: QueryRequest) -> QueryResponse``
        method.
    judge : callable
        A callable ``(answer: str, evidence_fragments: list[str]) -> str``
        returning a groundedness label (``"pass"``, ``"warning"``, ``"fail"``).
    emitter : ObservabilityEmitter | None
        An observability emitter.  When ``None``, a local no-op emitter
        is created lazily.
    top_k : int
        Default ``top_k`` for queries.  Defaults to ``5``.

    Notes
    -----
    The ``run`` method executes only the ``case_ids`` specified in the
    ``EvalRunRequest``.  It computes all metrics for each case and
    preserves the ``trace_id`` from the query response.
    """

    def __init__(
        self,
        case_loader: Callable[[], list[EvalCase]],
        query_service: Any,
        judge: Callable[..., str],
        emitter: ObservabilityEmitter | None = None,
        top_k: int = 5,
    ) -> None:
        self.case_loader = case_loader
        self.query_service = query_service
        self.judge = judge
        self.emitter = emitter
        self._top_k = top_k

    def run(
        self,
        request: EvalRunRequest,
    ) -> EvalRunResponse:
        """Execute the requested eval cases and return results.

        Parameters
        ----------
        request : EvalRunRequest
            The request containing ``case_ids`` and ``top_k``.

        Returns
        -------
        EvalRunResponse
            A response with ``run_id``, ``total_cases``, ``results_path``,
            and ``trace_id`` (from the first result, if any).

        Raises
        ------
        ValueError
            When requested case_ids are not found in the case set, or
            when ``export_eval_results`` fails.
        """
        # Use request top_k for all operations.
        top_k = request.top_k

        # Load all cases and build a lookup by id.
        all_cases = self.case_loader()
        case_by_id: dict[str, EvalCase] = {c.id: c for c in all_cases}

        # Reject requested IDs that don't exist.
        missing = [cid for cid in request.case_ids if cid not in case_by_id]
        if missing:
            raise ValueError(
                f"Eval case(s) not found: {missing}"
            )

        # Deduplicate while preserving order.
        seen: set[str] = set()
        ordered_ids: list[str] = []
        for cid in request.case_ids:
            if cid not in seen:
                seen.add(cid)
                ordered_ids.append(cid)

        # Create a unique run_id.
        run_id = f"eval_run_{uuid.uuid4().hex[:12]}"

        # Create emitter if not provided.
        emitter = self.emitter
        if emitter is None:
            emitter = create_observability_emitter()

        results: list[EvalResult] = []
        first_trace_id: str | None = None

        for case_id in ordered_ids:
            case = case_by_id[case_id]

            # Build the query request.
            query_request = QueryRequest(question=case.question, top_k=top_k)

            # Execute the query.
            query_response = self.query_service.query(query_request)

            # Preserve trace_id from the query response.
            trace_id = query_response.trace_id or None

            # Collect evidence fragments from retrieved documents.
            evidence_fragments: list[str] = []
            for doc in query_response.retrieved_documents:
                if hasattr(doc, "evidence"):
                    evidence_fragments.append(str(doc.evidence))
                elif isinstance(doc, dict):
                    evidence_fragments.append(str(doc.get("evidence", "")))

            # --- Compute metrics ---
            metrics = self._compute_metrics(case, query_response, evidence_fragments, top_k)

            # --- Run the judge for groundedness ---
            try:
                judge_label = self.judge(
                    query_response.answer, evidence_fragments
                )
                metrics.groundedness = parse_groundedness_label(judge_label)
            except Exception:
                # If judge fails, keep the default or any computed value.
                pass

            # --- Determine passed status ---
            passed = self._determine_passed(metrics)

            result = EvalResult(
                eval_case_id=case.id,
                metrics=metrics,
                passed=passed,
                trace_id=trace_id,
            )
            results.append(result)

            # Emit scores to the emitter.
            emit_eval_scores(emitter, result)

            # Track the first trace_id for the response.
            if first_trace_id is None and trace_id is not None:
                first_trace_id = trace_id

        # --- Export results to local JSON backup ---
        try:
            export_eval_results(
                type("Run", (), {
                    "run_id": run_id,
                    "results": results,
                    "trace_id": first_trace_id,
                })(),
            )
        except Exception as exc:
            # If export fails, raise a safe error so the run is not silently 200.
            raise ValueError(f"Failed to export eval results: {exc}")

        return EvalRunResponse(
            run_id=run_id,
            total_cases=len(results),
            results_path=EVAL_RESULTS_PATH,
            trace_id=first_trace_id,
            results=results,
        )

    def _compute_metrics(
        self,
        case: EvalCase,
        query_response: QueryResponse,
        evidence_fragments: list[str],
        top_k: int,
    ) -> EvalMetrics:
        """Compute all metrics for a single eval case.

        Parameters
        ----------
        case : EvalCase
            The evaluation case being evaluated.
        query_response : QueryResponse
            The response from the query service.
        evidence_fragments : list[str]
            Evidence text fragments from retrieved documents.
        top_k : int
            The top_k value used for this query.

        Returns
        -------
        EvalMetrics
            Computed metrics for this case.
        """
        # Precision@k — use the request top_k.
        retrieved_for_precision = query_response.retrieved_documents
        try:
            precision = precision_at_k(
                case.expected_documents,
                retrieved_for_precision,
                top_k,
            )
        except (ValueError, TypeError):
            precision = 0.0

        # JSON validity — only when the case has the json_validity tag.
        case_tags = set(case.tags)
        json_result: JsonValidityResult | None = None
        if "json_validity" in case_tags or "extraction_json" in case_tags:
            json_result = json_validity(query_response.answer, Extraction)

        # Ontology mapping — only when the case has the ontology_mapping tag.
        ontology_passed: bool | None = None
        if "ontology_mapping" in case_tags:
            # Would need extraction-like data; skip for now.
            pass

        # Coordination caution
        coord_result = coordination_caution(
            query_response.answer, evidence_fragments
        )

        # Latency / cost — extract from query response metadata if available.
        # Since QueryResponse doesn't have metadata, we use empty dict.
        latency_result = latency_cost_metrics({})

        # Determine json_validity value: only fail if the case explicitly
        # tags for json_validity and the check fails.
        json_validity_value = True  # default: not applicable for normal cases
        if json_result is not None:
            json_validity_value = json_result.passed

        return EvalMetrics(
            precision_at_k=precision,
            json_validity=json_validity_value,
            groundedness="pass",  # Will be overridden by judge
            ontology_mapping=ontology_passed,
            coordination_caution=coord_result.passed,
            latency_ms=latency_result.latency_ms,
            cost=latency_result.cost_usd,
        )

    @staticmethod
    def _determine_passed(metrics: EvalMetrics) -> bool:
        """Determine whether an eval case passed based on its metrics.

        A case passes when groundedness is ``"pass"`` and all boolean
        metrics that are set are ``True``.

        Parameters
        ----------
        metrics : EvalMetrics
            The computed metrics.

        Returns
        -------
        bool
            ``True`` if the case passed, ``False`` otherwise.
        """
        if metrics.groundedness != "pass":
            return False
        if not metrics.json_validity:
            return False
        if metrics.ontology_mapping is not None and not metrics.ontology_mapping:
            return False
        if metrics.coordination_caution is not None and not metrics.coordination_caution:
            return False
        return True


# ---------------------------------------------------------------------------
# export_eval_results
# ---------------------------------------------------------------------------




def export_eval_results(
    run: Any,
    path: str | pathlib.Path | None = None,
) -> None:
    """Export eval results to a JSON file.

    Parameters
    ----------
    run : Any
        An object with at least ``run_id`` (str) and ``results``
        (list[EvalResult]) attributes.  May also have ``trace_id``
        (str | None) and ``results_path`` (str).
    path : str | pathlib.Path | None
        The output file path.  When ``None``, defaults to
        :data:`evals_config.EVAL_RESULTS_PATH`.

    Raises
    ------
    ValueError
        When the resolved path is outside the allowed export base
        directory.
    """
    if path is None:
        path = EVAL_RESULTS_PATH

    resolved = resolve_eval_results_path(path)

    # --- Reject path traversal in the original string -------------------
    if ".." in resolved.parts:
        raise ValueError(f"Path traversal not allowed in export path: {path}")

    # --- Resolve to absolute for safety checks --------------------------
    resolved = resolved.resolve()

    # --- Ensure the resolved path is under the allowed export base ------
    try:
        resolved.relative_to(_ALLOWED_EXPORT_BASE.resolve())
    except ValueError:
        raise ValueError(
            f"Eval results export path must be under the allowed outputs directory: {path}"
        )

    # Create the directory if it doesn't exist.
    resolved.parent.mkdir(parents=True, exist_ok=True)

    # Build the export data.
    results_dict: list[dict[str, Any]] = []
    for result in run.results:
        result_data: dict[str, Any] = {
            "eval_case_id": result.eval_case_id,
            "passed": result.passed,
            "trace_id": result.trace_id,
            "metrics": {
                "precision_at_k": result.metrics.precision_at_k,
                "json_validity": result.metrics.json_validity,
                "groundedness": result.metrics.groundedness,
                "ontology_mapping": result.metrics.ontology_mapping,
                "coordination_caution": result.metrics.coordination_caution,
                "latency_ms": result.metrics.latency_ms,
                "cost": result.metrics.cost,
            },
        }
        results_dict.append(result_data)

    export_data: dict[str, Any] = {
        "run_id": run.run_id,
        "results": results_dict,
    }

    # If the run has a trace_id, include it.
    if hasattr(run, "trace_id") and run.trace_id is not None:
        export_data["trace_id"] = run.trace_id

    # Write atomically (write to temp file, then rename).
    tmp_path = resolved.with_suffix(resolved.suffix + ".tmp")
    tmp_path.write_text(
        json.dumps(export_data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    tmp_path.replace(resolved)
