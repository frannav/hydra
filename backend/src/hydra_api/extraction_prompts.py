"""HYDRA Extraction prompt builder.

This module provides functions to build extraction prompts for an
OpenAI-compatible language model.  It is deliberately lazy — importing
this module does not read any files, connect to a database, or call
external APIs.

Public API
----------
- EXTRACTION_SYSTEM_INSTRUCTIONS: str
- format_ontology_for_prompt(ontology) -> str
- build_extraction_prompt(raw_document, ontology) -> list[dict[str, str]]
"""

from __future__ import annotations

from typing import Any

from .schemas import RawDocument

# ---------------------------------------------------------------------------
# System instructions for extraction
# ---------------------------------------------------------------------------

EXTRACTION_SYSTEM_INSTRUCTIONS: str = (
    "You are an analytical assistant for HYDRA, a system that produces "
    "structured extractions from a corpus of public documents.\n\n"
    "Respond ONLY with valid JSON that is compatible with the Extraction "
    "Pydantic schema. Do not include markdown fences, code blocks, or "
    "explanatory text outside the JSON object.\n\n"
    "Rules:\n"
    "1. Evidence: Every analytical claim must be supported by a text "
    "fragment from the source document. Include at least one "
    "evidence_fragment for each meaningful assertion.\n"
    "2. Limitations: Always include a limitations list describing what "
    "the document does not cover, what cannot be determined from the "
    "text, and any ambiguities.\n"
    "3. Coordinacion (coordination): Do NOT assert that multiple actors "
    "are coordinating, acting in concert, or sharing objectives unless "
    "the document contains explicit evidence of such coordination. "
    "When evidence is insufficient, assign the narrative frame "
    "'unknown_or_insufficient_evidence'.\n"
    "4. Use only the controlled vocabulary IDs defined in the ontology "
    "section below for narrative_frame_id, actor_types, affected_sectors, "
    "and threat_types.\n"
    "5. When evidence is insufficient to assign a specific category, "
    "use the 'unknown_or_insufficient_evidence' ID.\n"
    "6. Do not invent facts, actors, events, or relationships that are "
    "not present in the source text.\n"
    "7. Keep the output concise and focused on the structured fields.\n"
)


# ---------------------------------------------------------------------------
# format_ontology_for_prompt
# ---------------------------------------------------------------------------

def format_ontology_for_prompt(ontology: dict[str, Any]) -> str:
    """Format a validated ontology dict into a text block for the prompt.

    Parameters
    ----------
    ontology : dict
        A validated ontology dict (output of ``validate_ontology``).

    Returns
    -------
    str
        A human-readable text block listing controlled vocabulary IDs and
        labels, suitable for inclusion in a prompt.
    """
    lines: list[str] = []
    lines.append("Ontology — controlled vocabularies:")
    lines.append("")

    # Analytical sections (list of objects with id/label).
    analytical_sections = [
        "narrative_frames",
        "actor_types",
        "affected_sectors",
        "threat_types",
    ]
    for section in analytical_sections:
        items = ontology.get(section, [])
        if not items:
            continue
        lines.append(f"  {section}:")
        for item in items:
            item_id = item.get("id", "")
            label = item.get("label", "")
            lines.append(f"    - {item_id}: {label}")
        lines.append("")

    # String sections (plain lists of strings).
    string_sections = [
        "graph_node_types",
        "graph_edge_types",
    ]
    for section in string_sections:
        items = ontology.get(section, [])
        if not items:
            continue
        lines.append(f"  {section}:")
        for item in items:
            lines.append(f"    - {item}")
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# build_extraction_prompt
# ---------------------------------------------------------------------------

def build_extraction_prompt(
    raw_document: RawDocument,
    ontology: dict[str, Any],
) -> list[dict[str, str]]:
    """Build an extraction prompt for a single document.

    Parameters
    ----------
    raw_document : RawDocument
        The raw document to extract from.
    ontology : dict
        A validated ontology dict.

    Returns
    -------
    list[dict[str, str]]
        A list of messages with ``role`` and ``content`` keys, compatible
        with an OpenAI-compatible chat API.
    """
    ontology_context = format_ontology_for_prompt(ontology)

    user_content = (
        f"Document metadata:\n"
        f"  document_id: {raw_document.document_id}\n"
        f"  title: {raw_document.metadata.title}\n"
        f"  source: {raw_document.metadata.source}\n"
        f"  domain: {raw_document.metadata.domain}\n"
        f"  source_type: {raw_document.metadata.source_type.value}\n"
        f"\n"
        f"Document text:\n"
        f"{raw_document.text}\n"
        f"\n"
        f"Extract structured information from this document following "
        f"the rules in the system instructions and using the controlled "
        f"vocabularies from the ontology above."
    )

    return [
        {"role": "system", "content": EXTRACTION_SYSTEM_INSTRUCTIONS},
        {"role": "user", "content": user_content},
    ]
