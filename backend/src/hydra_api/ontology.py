"""HYDRA Ontology loader and validator.

This module provides functions to load, validate, and query the HYDRA
ontology YAML file.  It is deliberately lazy — importing this module
does not read any files, connect to a database, or call external APIs.

Public API
----------
- load_ontology(path) -> dict
- validate_ontology(data) -> dict
- allowed_ids(data, section) -> set[str]
- validate_extraction_against_ontology(extraction, ontology) -> Extraction
"""

from __future__ import annotations

import argparse
import pathlib
import re
import sys
from typing import Any

import yaml

# ---------------------------------------------------------------------------
# Snake-case pattern for analytical vocabulary IDs
# ---------------------------------------------------------------------------
_SNAKE_CASE = re.compile(r"^[a-z0-9_]+$")

# ---------------------------------------------------------------------------
# Required sections and their expected formats
# ---------------------------------------------------------------------------
_REQUIRED_SECTIONS = [
    "narrative_frames",
    "actor_types",
    "affected_sectors",
    "threat_types",
    "graph_node_types",
    "graph_edge_types",
]

# Sections that contain list-of-objects with `id`/`label` fields.
_ANALYTICAL_SECTIONS = [
    "narrative_frames",
    "actor_types",
    "affected_sectors",
    "threat_types",
]

# Sections that are plain lists of strings.
_STRING_SECTIONS = [
    "graph_node_types",
    "graph_edge_types",
]


# ---------------------------------------------------------------------------
# load_ontology
# ---------------------------------------------------------------------------

def load_ontology(path: pathlib.Path) -> dict[str, Any]:
    """Load the ontology YAML from *path* and return it as a dict.

    Raises
    ------
    ValueError
        If the file is empty or its root is not a mapping (dict).
    FileNotFoundError
        If the path does not exist.
    """
    text = path.read_text(encoding="utf-8")
    if not text.strip():
        raise ValueError(f"Ontology file is empty: {path}")

    data = yaml.safe_load(text)
    if not isinstance(data, dict):
        raise ValueError(
            f"Ontology root must be a YAML mapping (dict), got {type(data).__name__}: {path}"
        )
    return data


# ---------------------------------------------------------------------------
# validate_ontology
# ---------------------------------------------------------------------------

def validate_ontology(data: dict[str, Any]) -> dict[str, Any]:
    """Validate the structure of an ontology dict.

    Returns *data* unchanged if it is valid.

    Raises
    ------
    ValueError
        If required sections are missing, IDs are duplicated, or IDs are
        not valid snake_case in analytical sections.
    """
    # Check required sections exist and are non-empty.
    for section in _REQUIRED_SECTIONS:
        if section not in data or not data[section]:
            raise ValueError(f"Missing or empty required section: {section}")

    # Validate analytical sections (list of objects with `id`).
    for section in _ANALYTICAL_SECTIONS:
        items = data[section]
        if not isinstance(items, list):
            raise ValueError(
                f"Section '{section}' must be a list of objects"
            )
        seen_ids: set[str] = set()
        for item in items:
            if not isinstance(item, dict) or "id" not in item:
                raise ValueError(
                    f"Each item in '{section}' must be an object with an 'id' field"
                )
            item_id = item["id"]
            if not isinstance(item_id, str):
                raise ValueError(
                    f"ID in '{section}' must be a string, got {type(item_id).__name__}"
                )
            # Duplicate check.
            if item_id in seen_ids:
                raise ValueError(
                    f"Duplicate ID '{item_id}' in section '{section}'"
                )
            seen_ids.add(item_id)
            # Snake-case check.
            if not _SNAKE_CASE.match(item_id):
                raise ValueError(
                    f"ID '{item_id}' in section '{section}' is not valid snake_case"
                )

    # Validate string sections (plain lists of strings).
    for section in _STRING_SECTIONS:
        items = data[section]
        if not isinstance(items, list) or not items:
            raise ValueError(
                f"Section '{section}' must be a non-empty list of strings"
            )
        for item in items:
            if not isinstance(item, str):
                raise ValueError(
                    f"All items in '{section}' must be strings, got {type(item).__name__}"
                )

    return data


# ---------------------------------------------------------------------------
# allowed_ids
# ---------------------------------------------------------------------------

def allowed_ids(data: dict[str, Any], section: str) -> set[str]:
    """Return the set of allowed IDs for a given ontology section.

    Parameters
    ----------
    data : dict
        A validated ontology dict (output of ``validate_ontology``).
    section : str
        The section name (e.g. ``"narrative_frames"``).

    Returns
    -------
    set[str]
        The set of ``id`` values for that section.

    Raises
    ------
    ValueError
        If the section is not a known analytical section.
    """
    if section not in _ANALYTICAL_SECTIONS:
        raise ValueError(f"Unknown section: '{section}'. "
                         f"Expected one of {_ANALYTICAL_SECTIONS}")

    items = data[section]
    return {item["id"] for item in items}


# ---------------------------------------------------------------------------
# validate_extraction_against_ontology
# ---------------------------------------------------------------------------

def validate_extraction_against_ontology(
    extraction: Any,
    ontology: dict[str, Any],
) -> Any:
    """Validate an extraction object against the ontology's controlled IDs.

    Parameters
    ----------
    extraction : Extraction
        A Pydantic ``Extraction`` instance.
    ontology : dict
        A validated ontology dict.

    Returns
    -------
    Extraction
        The same extraction instance if validation passes.

    Raises
    ------
    ValueError
        If any controlled ID in the extraction is not in the ontology.
    """
    # narrative_frame_id — allow None.
    frame_id = getattr(extraction, "narrative_frame_id", None)
    if frame_id is not None:
        allowed = allowed_ids(ontology, "narrative_frames")
        if frame_id not in allowed:
            raise ValueError(
                f"Unknown narrative_frame_id '{frame_id}'. "
                f"Allowed: {sorted(allowed)}"
            )

    # actor_types — allow empty list.
    for at in getattr(extraction, "actor_types", []):
        allowed = allowed_ids(ontology, "actor_types")
        if at not in allowed:
            raise ValueError(
                f"Unknown actor_type '{at}'. "
                f"Allowed: {sorted(allowed)}"
            )

    # affected_sectors — allow empty list.
    for sector in getattr(extraction, "affected_sectors", []):
        allowed = allowed_ids(ontology, "affected_sectors")
        if sector not in allowed:
            raise ValueError(
                f"Unknown affected_sector '{sector}'. "
                f"Allowed: {sorted(allowed)}"
            )

    # threat_types — allow empty list.
    for threat in getattr(extraction, "threat_types", []):
        allowed = allowed_ids(ontology, "threat_types")
        if threat not in allowed:
            raise ValueError(
                f"Unknown threat_type '{threat}'. "
                f"Allowed: {sorted(allowed)}"
            )

    return extraction


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _cli_validate(path: pathlib.Path) -> None:
    """Validate an ontology file and print results."""
    try:
        data = load_ontology(path)
        validate_ontology(data)
        print(f"Ontology '{path}' is valid.")
    except Exception as exc:
        print(f"Ontology validation failed: {exc}", file=sys.stderr)
        sys.exit(1)


def _cli_print_ids(path: pathlib.Path, section: str) -> None:
    """Print allowed IDs for a section."""
    try:
        data = load_ontology(path)
        validate_ontology(data)
        ids = allowed_ids(data, section)
        for item_id in sorted(ids):
            print(item_id)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    """CLI entry point for ``python -m hydra_api.ontology``."""
    parser = argparse.ArgumentParser(
        description="HYDRA ontology loader and validator CLI"
    )
    parser.add_argument(
        "--validate",
        nargs=1,
        metavar="ONTOLOGY_PATH",
        help="Validate the ontology file",
    )
    parser.add_argument(
        "--print-ids",
        nargs=2,
        metavar=("ONTOLOGY_PATH", "SECTION"),
        help="Print allowed IDs for a section",
    )

    args = parser.parse_args()

    if args.validate is not None:
        _cli_validate(pathlib.Path(args.validate[0]))
    elif args.print_ids is not None:
        _cli_print_ids(pathlib.Path(args.print_ids[0]), args.print_ids[1])
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
