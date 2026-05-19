"""HYDRA API — Evaluation metric functions.

All functions in this module are **deterministic** and have **no
import-time side effects**: no ``.env`` loading, no network calls,
no file I/O.
"""

from __future__ import annotations

import json
import pathlib
import re
from dataclasses import dataclass
from typing import Any, Type

import yaml
from pydantic import BaseModel

from .schemas import EvalMetrics


# ---------------------------------------------------------------------------
# Precision@k
# ---------------------------------------------------------------------------


def precision_at_k(
    expected_documents: list[str],
    retrieved_documents: list[Any],
    k: int,
) -> float:
    """Compute retrieval Precision@k.

    Parameters
    ----------
    expected_documents : list[str]
        List of expected document IDs.
    retrieved_documents : list[RetrievedDocument | dict]
        List of retrieved documents (objects with a ``document_id``
        attribute or key).
    k : int
        Number of top results to consider.  Must be **>= 1**.

    Returns
    -------
    float
        Precision = (number of expected docs in top-k retrieved) /
        (total number of expected docs).  Returns ``0.0`` when there
        are no expected documents or no retrieved documents.

    Raises
    ------
    ValueError
        When ``k <= 0``.

    Notes
    -----
    - Retrieved documents are **deduplicated by ``document_id``**
      before computing precision, so duplicate chunks from the same
      document do not inflate the score.
    - The metric is **deterministic** for a given input.
    - When ``expected_documents`` is empty, returns ``0.0``.
    """
    if k <= 0:
        raise ValueError(f"precision_at_k: k must be >= 1, got {k}")

    if not expected_documents:
        return 0.0

    if not retrieved_documents:
        return 0.0

    # --- Deduplicate retrieved documents by document_id (preserve order) ---
    seen_ids: set[str] = set()
    deduplicated: list[str] = []
    for doc in retrieved_documents:
        doc_id = doc["document_id"] if isinstance(doc, dict) else doc.document_id
        if doc_id not in seen_ids:
            seen_ids.add(doc_id)
            deduplicated.append(doc_id)

    # --- Take top-k -------------------------------------------------------
    top_k_ids = deduplicated[:k]

    # --- Compute precision -------------------------------------------------
    expected_set = set(expected_documents)
    hits = sum(1 for doc_id in top_k_ids if doc_id in expected_set)
    return hits / len(expected_set)


# ---------------------------------------------------------------------------
# JSON Validity
# ---------------------------------------------------------------------------


@dataclass
class JsonValidityResult:
    """Result of a JSON validity check."""

    passed: bool


def json_validity(
    payload: str | dict[str, Any],
    schema_model: Type[BaseModel],
) -> JsonValidityResult:
    """Validate that *payload* is valid JSON and conforms to *schema_model*.

    Parameters
    ----------
    payload : str | dict
        A JSON-encoded string or an already-parsed dict.
    schema_model : Type[pydantic.BaseModel]
        A Pydantic model class to validate the parsed payload against.

    Returns
    -------
    JsonValidityResult
        ``passed=True`` only when the payload is valid JSON **and**
        validates successfully against *schema_model*.

    Notes
    -----
    - When *payload* is a string, invalid JSON is reported as ``passed=False``.
    - When *payload* is valid JSON but does not satisfy the Pydantic schema
      (e.g. missing required fields), ``passed=False``.
    - When *payload* is a dict that validates, ``passed=True``.
    """
    # --- Step 1: Parse JSON if given as string ----------------------------
    if isinstance(payload, str):
        try:
            parsed = json.loads(payload)
        except (json.JSONDecodeError, ValueError):
            return JsonValidityResult(passed=False)
    elif isinstance(payload, dict):
        parsed = payload
    else:
        # Non-string, non-dict payloads cannot be validated against a
        # Pydantic model that expects an object.
        return JsonValidityResult(passed=False)

    # --- Step 2: Validate against schema ----------------------------------
    try:
        schema_model.model_validate(parsed)
    except Exception:
        return JsonValidityResult(passed=False)

    return JsonValidityResult(passed=True)


# ---------------------------------------------------------------------------
# Ontology Mapping Validity
# ---------------------------------------------------------------------------


@dataclass
class OntologyMappingResult:
    """Result of an ontology mapping validity check."""

    passed: bool
    unknown_ids: list[str] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.unknown_ids is None:
            self.unknown_ids: list[str] = []


# Default path to the ontology YAML file (relative to backend project root).
_DEFAULT_ONTOLOGY_PATH: pathlib.Path = pathlib.Path(
    "ontology/hydra_ontology.yaml"
)

# Controlled sections and the extraction fields that reference them.
# Each tuple is (ontology_section_name, extraction_field_name).
_CONTROLLED_SECTIONS: list[tuple[str, str]] = [
    ("narrative_frames", "narrative_frame_id"),
    ("actor_types", "actor_types"),
    ("affected_sectors", "affected_sectors"),
    ("threat_types", "threat_types"),
]


def _load_ontology(path: pathlib.Path) -> dict[str, Any]:
    """Load and return the ontology YAML as a dict.

    Uses lazy import — yaml is only imported when this function is called.
    """
    text = path.read_text(encoding="utf-8")
    data = yaml.safe_load(text)
    if not isinstance(data, dict):
        raise ValueError(
            f"Ontology root must be a YAML mapping (dict), got {type(data).__name__}"
        )
    return data


def _collect_unknown_ids(
    extraction: dict[str, Any],
    ontology: dict[str, Any],
) -> list[str]:
    """Collect all IDs from *extraction* that are not in *ontology*.

    Parameters
    ----------
    extraction : dict
        Parsed extraction dict (e.g. from JSON).
    ontology : dict
        Validated ontology dict loaded from YAML.

    Returns
    -------
    list[str]
        List of unknown IDs found.  Each unknown ID is reported once.
    """
    unknown: list[str] = []
    seen: set[str] = set()

    for section_name, field_name in _CONTROLLED_SECTIONS:
        allowed: set[str] = {
            item["id"] for item in ontology.get(section_name, [])
        }

        value = extraction.get(field_name)

        # narrative_frame_id is a single string (or None).
        if field_name == "narrative_frame_id":
            if value is not None and value not in allowed:
                if value not in seen:
                    unknown.append(value)
                    seen.add(value)
        # actor_types, affected_sectors, threat_types are lists.
        else:
            if isinstance(value, list):
                for item_id in value:
                    if item_id not in allowed and item_id not in seen:
                        unknown.append(item_id)
                        seen.add(item_id)

    return unknown


def ontology_mapping_validity(
    extraction: dict[str, Any],
    ontology_path: pathlib.Path | str | None = None,
) -> OntologyMappingResult:
    """Validate that all controlled IDs in *extraction* exist in the ontology.

    Parameters
    ----------
    extraction : dict
        A parsed extraction dict (e.g. from ``json.loads`` or
        ``pathlib.Path.read_text().json()``).
    ontology_path : str | pathlib.Path | None
        Path to the ontology YAML file.  When ``None``, defaults to
        ``ontology/hydra_ontology.yaml`` relative to the backend project
        root.

    Returns
    -------
    OntologyMappingResult
        ``passed=True`` when **all** controlled IDs in the extraction
        are found in the ontology.  ``passed=False`` when one or more
        IDs are unknown; ``unknown_ids`` lists them.

    Notes
    -----
    - This function does **not** modify the ontology YAML.
    - Only the following fields are checked:
      ``narrative_frame_id``, ``actor_types``, ``affected_sectors``,
      ``threat_types``.
    - ``None`` values (e.g. ``narrative_frame_id: null``) are allowed.
    - Empty lists (e.g. ``actor_types: []``) are allowed.
    """
    if ontology_path is None:
        # Resolve relative to the backend project root.
        _base = pathlib.Path(__file__).resolve().parent.parent.parent
        resolved = (_base / _DEFAULT_ONTOLOGY_PATH).resolve()
    else:
        resolved = pathlib.Path(ontology_path).resolve()

    ontology = _load_ontology(resolved)
    unknown_ids = _collect_unknown_ids(extraction, ontology)

    return OntologyMappingResult(
        passed=len(unknown_ids) == 0,
        unknown_ids=unknown_ids,
    )


# ---------------------------------------------------------------------------
# Coordination Caution
# ---------------------------------------------------------------------------


@dataclass
class CoordinationCautionResult:
    """Result of a coordination-caution check."""

    passed: bool


# Patterns that signal a coordination / intention / attribution claim.
# Each tuple is (compiled_regex, fallback_plain).
_COORDINATION_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (
        re.compile(r"\b(coordinación|coordinacion)\b", re.IGNORECASE),
        "coordinación",
    ),
    (
        re.compile(r"\b(coordinar|coordinaron|coordinan)\b", re.IGNORECASE),
        "coordinar",
    ),
    (
        re.compile(r"\b(intención|intencion)\b", re.IGNORECASE),
        "intención",
    ),
    (
        re.compile(r"\b(intencionar|intencionaron)\b", re.IGNORECASE),
        "intencionar",
    ),
    (
        re.compile(r"\b(atribuir|atribuyó|atribuyeron)\b", re.IGNORECASE),
        "atribuir",
    ),
    (
        re.compile(r"\b(consenso|acuerdo tácito|acuerdo_tácito)\b", re.IGNORECASE),
        "consenso",
    ),
    (
        re.compile(
            r"\b(actuar en conjunto|actuar conjuntamente|de manera coordinada)\b",
            re.IGNORECASE,
        ),
        "actuar en conjunto",
    ),
]

# Patterns that signal negation of a claim (word must appear before the
# coordination keyword to cancel it).
_NEGATION_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"\b(no|nunca|ni|nada|nadie|ningún|ninguno|carece|ausente)\b", re.IGNORECASE),
]


def _has_negation_before_claim(text: str, claim_start: int) -> bool:
    """Return True if a negation word appears before *claim_start* in *text*.

    The negation window extends back up to 10 words from the claim keyword.
    """
    # Split the text up to the claim position into words.
    prefix_words = text[:claim_start].split()
    window_size = 10
    window_words = prefix_words[-window_size:] if len(prefix_words) >= window_size else prefix_words
    window_text = " ".join(window_words)
    for pattern in _NEGATION_PATTERNS:
        if pattern.search(window_text):
            return True
    return False


def coordination_caution(
    answer: str,
    evidence_fragments: list[str] | list[Any],
) -> CoordinationCautionResult:
    """Check whether *answer* makes a coordination / intention / attribution
    claim that is **not** supported by any *evidence_fragments*.

    Parameters
    ----------
    answer : str
        The model's answer text to inspect.
    evidence_fragments : list[str] | list[Any]
        Evidence fragments that support the answer.  May be a list of
        strings or a list of dicts / objects with a ``"text"`` key.

    Returns
    -------
    CoordinationCautionResult
        ``passed=True`` when the answer contains no unsupported
        coordination/intention/attribution claim, or when the claim is
        negated (e.g. *"no hay evidencia de coordinación"*).
        ``passed=False`` when the answer asserts coordination/intention/
        attribution without supporting evidence.

    Notes
    -----
    - The check is **case-insensitive**.
    - Negation words (no, nunca, carece, etc.) appearing within 10 words
      before the coordination keyword cancel the claim.
    - When *evidence_fragments* is non-empty, a coordination claim is
      considered supported and the metric passes.
    - When *evidence_fragments* is empty, a coordination claim fails.
    - This function is **deterministic** for a given input.
    """
    # Collect evidence text.
    evidence_texts: list[str] = []
    for frag in evidence_fragments:
        if isinstance(frag, str):
            evidence_texts.append(frag)
        elif isinstance(frag, dict):
            evidence_texts.append(str(frag.get("text", "")))
        else:
            evidence_texts.append(str(getattr(frag, "text", "")))

    has_evidence = any(t.strip() for t in evidence_texts)

    # Normalise the answer for matching.
    answer_lower = answer.lower()

    # First check: does the answer contain a coordination/intention claim?
    has_claim = False
    claim_text = ""

    for pattern, _ in _COORDINATION_PATTERNS:
        match = pattern.search(answer_lower)
        if match:
            has_claim = True
            claim_text = match.group(0)
            claim_start = match.start()
            break

    if not has_claim:
        # No coordination claim detected — nothing to caution about.
        return CoordinationCautionResult(passed=True)

    # Negation check: is the claim negated?
    if _has_negation_before_claim(answer_lower, claim_start):
        return CoordinationCautionResult(passed=True)

    # Claim is asserted — check evidence.
    if has_evidence:
        return CoordinationCautionResult(passed=True)

    return CoordinationCautionResult(passed=False)


# ---------------------------------------------------------------------------
# Latency / Cost Metrics
# ---------------------------------------------------------------------------


@dataclass
class LatencyCostResult:
    """Extracted latency and cost from trace metadata."""

    latency_ms: int | None = None
    cost_usd: float | None = None


def latency_cost_metrics(trace_metadata: dict[str, Any]) -> LatencyCostResult:
    """Extract latency and cost values from *trace_metadata*.

    Parameters
    ----------
    trace_metadata : dict
        A metadata dict (typically from a trace context) that may
        contain ``latency_ms`` and ``cost_usd`` keys.

    Returns
    -------
    LatencyCostResult
        ``latency_ms`` and ``cost_usd`` extracted from the metadata.
        When a key is absent, the corresponding field is ``None``
        (not inferred or defaulted to zero).

    Notes
    -----
    - This function does **not** invent values when metadata is
      incomplete.  Missing fields are ``None``.
    - The function is **deterministic** and has no side effects.
    """
    latency_ms = trace_metadata.get("latency_ms")
    cost_usd = trace_metadata.get("cost_usd")

    return LatencyCostResult(
        latency_ms=latency_ms,
        cost_usd=cost_usd,
    )
