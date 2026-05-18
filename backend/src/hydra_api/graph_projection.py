"""HYDRA GraphProjection builder.

This module builds a derived graph projection from a validated Extraction.
It is deliberately lazy — importing this module does not read any files,
connect to a database, or call external APIs.

No graph database dependencies are used.  The graph projection
is serialised to JSON for downstream sinks.

Public API
----------
- build_graph_nodes(extraction) -> list[GraphNode]
- build_graph_edges(extraction) -> list[GraphEdge]
- build_graph_projection(extraction) -> GraphProjection
- export_graph_projection_json(projection, output_dir) -> Path
"""

from __future__ import annotations

import hashlib
import json
import pathlib
from typing import Any

from .schemas import (
    Actor,
    EvidenceFragment,
    Event,
    Extraction,
    GraphEdge,
    GraphNode,
    GraphProjection,
    Location,
)

# ---------------------------------------------------------------------------
# Deterministic ID helpers
# ---------------------------------------------------------------------------


def _deterministic_id(prefix: str, *parts: str) -> str:
    """Return a deterministic ID from a prefix and string parts.

    Parameters
    ----------
    prefix : str
        A short prefix for the ID namespace (e.g. "doc", "actor").
    *parts : str
        Variable number of string parts to hash together.

    Returns
    -------
    str
        A hex digest of the first 12 characters of SHA-256 of the
        concatenation of prefix + parts, prefixed with the namespace.
    """
    raw = "".join([prefix] + list(parts))
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:12]
    return f"{prefix}_{digest}"


# ---------------------------------------------------------------------------
# build_graph_nodes
# ---------------------------------------------------------------------------


def build_graph_nodes(extraction: Extraction) -> list[GraphNode]:
    """Build graph nodes from a validated extraction.

    Always creates at least a ``Document`` node.  Optionally creates
    ``NarrativeFrame``, ``Actor``, ``Location``, ``Event``, ``Sector``,
    and ``ThreatType`` nodes when the corresponding fields are populated.

    Parameters
    ----------
    extraction : Extraction
        A validated Extraction instance.

    Returns
    -------
    list[GraphNode]
        A list of graph nodes derived from the extraction.
    """
    nodes: list[GraphNode] = []

    # Always create a Document node.
    nodes.append(
        GraphNode(
            id=_deterministic_id("doc", extraction.document_id),
            type="Document",
            label=extraction.title,
        )
    )

    # NarrativeFrame node if present.
    if extraction.narrative_frame_id:
        nodes.append(
            GraphNode(
                id=_deterministic_id("frame", extraction.narrative_frame_id),
                type="NarrativeFrame",
                label=extraction.narrative_frame_id,
            )
        )

    # Actor nodes.
    for actor in extraction.actors:
        nodes.append(
            GraphNode(
                id=_deterministic_id("actor", actor.name),
                type="Actor",
                label=actor.name,
            )
        )

    # Location nodes.
    for loc in extraction.locations:
        nodes.append(
            GraphNode(
                id=_deterministic_id("loc", loc.name),
                type="Location",
                label=loc.name,
            )
        )

    # Event nodes.
    for event in extraction.events:
        event_label = event.description if event.description else "Event"
        nodes.append(
            GraphNode(
                id=_deterministic_id("event", event_label),
                type="Event",
                label=event_label,
            )
        )

    # Sector nodes (controlled vocabulary).
    for sector in extraction.affected_sectors:
        nodes.append(
            GraphNode(
                id=_deterministic_id("sector", sector),
                type="Sector",
                label=sector,
            )
        )

    # ThreatType nodes (controlled vocabulary).
    for threat in extraction.threat_types:
        nodes.append(
            GraphNode(
                id=_deterministic_id("threat", threat),
                type="ThreatType",
                label=threat,
            )
        )

    return nodes


# ---------------------------------------------------------------------------
# build_graph_edges
# ---------------------------------------------------------------------------


def build_graph_edges(extraction: Extraction) -> list[GraphEdge]:
    """Build graph edges from a validated extraction.

    Edges are only created when ``evidence_fragments`` is non-empty.
    Every edge includes ``evidence_refs`` that reference deterministic
    identifiers for the evidence fragments — never the full text.

    Parameters
    ----------
    extraction : Extraction
        A validated Extraction instance.

    Returns
    -------
    list[GraphEdge]
        A list of graph edges.  Empty list when ``evidence_fragments``
        is empty.
    """
    if not extraction.evidence_fragments:
        return []

    nodes = build_graph_nodes(extraction)
    nodes_by_type: dict[str, list[GraphNode]] = {}
    for node in nodes:
        nodes_by_type.setdefault(node.type, []).append(node)

    edges: list[GraphEdge] = []

    # Build deterministic evidence refs from the fragments.
    evidence_refs: list[str] = []
    for i, frag in enumerate(extraction.evidence_fragments):
        ref = _deterministic_id("ev", extraction.document_id, str(i), frag.text[:50])
        evidence_refs.append(ref)

    # Document -> NarrativeFrame (HAS_NARRATIVE) when both exist.
    if extraction.narrative_frame_id:
        doc_node = nodes_by_type.get("Document", [None])[0]
        frame_nodes = nodes_by_type.get("NarrativeFrame", [])
        if doc_node and frame_nodes:
            edges.append(
                GraphEdge(
                    source=doc_node.id,
                    target=frame_nodes[0].id,
                    type="HAS_NARRATIVE",
                    evidence_refs=[evidence_refs[0]] if evidence_refs else [],
                )
            )

    # Document -> Actor (MENTIONS) for each actor.
    doc_node = nodes_by_type.get("Document", [None])[0]
    if doc_node and "Actor" in nodes_by_type:
        for actor_node in nodes_by_type["Actor"]:
            edges.append(
                GraphEdge(
                    source=doc_node.id,
                    target=actor_node.id,
                    type="MENTIONS",
                    evidence_refs=[evidence_refs[0]] if evidence_refs else [],
                )
            )

    # Document -> Location (MENTIONS) for each location.
    if doc_node and "Location" in nodes_by_type:
        for loc_node in nodes_by_type["Location"]:
            edges.append(
                GraphEdge(
                    source=doc_node.id,
                    target=loc_node.id,
                    type="MENTIONS",
                    evidence_refs=[evidence_refs[0]] if evidence_refs else [],
                )
            )

    # Document -> Event (MENTIONS) for each event.
    if doc_node and "Event" in nodes_by_type:
        for event_node in nodes_by_type["Event"]:
            edges.append(
                GraphEdge(
                    source=doc_node.id,
                    target=event_node.id,
                    type="MENTIONS",
                    evidence_refs=[evidence_refs[0]] if evidence_refs else [],
                )
            )

    # Document -> Sector (AFFECTS) for each sector.
    if doc_node and "Sector" in nodes_by_type:
        for sector_node in nodes_by_type["Sector"]:
            edges.append(
                GraphEdge(
                    source=doc_node.id,
                    target=sector_node.id,
                    type="AFFECTS",
                    evidence_refs=[evidence_refs[0]] if evidence_refs else [],
                )
            )

    # Document -> ThreatType (AFFECTS) for each threat type.
    if doc_node and "ThreatType" in nodes_by_type:
        for threat_node in nodes_by_type["ThreatType"]:
            edges.append(
                GraphEdge(
                    source=doc_node.id,
                    target=threat_node.id,
                    type="AFFECTS",
                    evidence_refs=[evidence_refs[0]] if evidence_refs else [],
                )
            )

    # Note: SUPPORTED_BY edges are intentionally not created here because
    # Evidence is not an allowed node type in the SDD. Evidence support is
    # tracked through each analytical edge's evidence_refs and through
    # GraphProjection.evidence_refs.

    return edges


# ---------------------------------------------------------------------------
# build_graph_projection
# ---------------------------------------------------------------------------


def build_graph_projection(extraction: Extraction) -> GraphProjection:
    """Build a complete GraphProjection from a validated extraction.

    Parameters
    ----------
    extraction : Extraction
        A validated Extraction instance.

    Returns
    -------
    GraphProjection
        A graph projection containing nodes, edges, and evidence refs.
    """
    nodes = build_graph_nodes(extraction)
    edges = build_graph_edges(extraction)

    # Collect all unique evidence refs from edges.
    evidence_refs: list[str] = []
    seen: set[str] = set()
    for edge in edges:
        for ref in edge.evidence_refs:
            if ref not in seen:
                evidence_refs.append(ref)
                seen.add(ref)

    return GraphProjection(
        document_id=extraction.document_id,
        nodes=nodes,
        edges=edges,
        evidence_refs=evidence_refs,
        schema_version=extraction.schema_version,
    )


# ---------------------------------------------------------------------------
# export_graph_projection_json
# ---------------------------------------------------------------------------


def export_graph_projection_json(
    projection: GraphProjection,
    output_dir: pathlib.Path,
) -> pathlib.Path:
    """Export a graph projection to a JSON file.

    Parameters
    ----------
    projection : GraphProjection
        A validated GraphProjection instance.
    output_dir : Path
        The directory to write the file to (created if it does not exist).

    Returns
    -------
    Path
        The path to the written file.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    file_path = output_dir / f"{projection.document_id}.graph_projection.json"
    file_path.write_text(
        json.dumps(
            projection.model_dump(),
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    return file_path
