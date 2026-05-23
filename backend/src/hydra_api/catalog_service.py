"""HYDRA API — catalog read services for documents and narratives.

Provides safe, lazy PostgreSQL-backed readers for:
- GET /documents
- GET /narratives

No database connection is opened at import time.
"""

from __future__ import annotations

import json
import logging
from collections.abc import Callable
from pathlib import Path
from typing import Any

from hydra_api.db import get_connection
from hydra_api.ontology import load_ontology, validate_ontology
from hydra_api.schemas import (
    Confidence,
    DocumentSummary,
    DocumentsResponse,
    Extraction,
    Narrative,
    NarrativesResponse,
    ProcessingStatus,
    RiskLevel,
)

logger = logging.getLogger(__name__)

DEFAULT_ONTOLOGY_PATH = Path(__file__).resolve().parents[2] / "ontology" / "hydra_ontology.yaml"

_DOCUMENTS_SQL = """
SELECT id, title, source, published_at, processing_status
FROM documents
ORDER BY published_at DESC NULLS LAST, title ASC, id ASC
""".strip()

_NARRATIVES_SQL = """
SELECT id, document_id, extraction_json
FROM extractions
WHERE COALESCE(NULLIF(TRIM(extraction_json->>'narrative_frame_id'), ''), '') <> ''
ORDER BY created_at ASC, document_id ASC, id ASC
""".strip()

_RISK_PRIORITY = {
    RiskLevel.bajo.value: 0,
    RiskLevel.medio.value: 1,
    RiskLevel.alto.value: 2,
}

_CONFIDENCE_PRIORITY = {
    Confidence.baja.value: 0,
    Confidence.media.value: 1,
    Confidence.alta.value: 2,
}


class CatalogService:
    """Read-only service for corpus and narrative catalogue endpoints."""

    def __init__(
        self,
        connection_factory: Callable[[], Any] = get_connection,
        ontology_path: Path = DEFAULT_ONTOLOGY_PATH,
    ) -> None:
        self.connection_factory = connection_factory
        self.ontology_path = ontology_path
        self._narrative_labels: dict[str, str] | None = None

    def list_documents(self) -> DocumentsResponse:
        """Return public document summaries from PostgreSQL."""
        rows = sorted(
            self._fetchall(_DOCUMENTS_SQL),
            key=lambda row: (
                row[3] is None,
                -(row[3].toordinal()) if row[3] is not None else 0,
                str(row[1]),
                str(row[0]),
            ),
        )
        documents: list[DocumentSummary] = []

        for row in rows:
            document_id, title, source, published_at, processing_status = row
            documents.append(
                DocumentSummary(
                    document_id=str(document_id),
                    title=str(title),
                    source=str(source),
                    published_at=(
                        published_at.isoformat() if published_at is not None else None
                    ),
                    processed=str(processing_status) == ProcessingStatus.processed.value,
                )
            )

        return DocumentsResponse(documents=documents)

    def list_narratives(self) -> NarrativesResponse:
        """Return aggregated narrative frames from extraction JSON."""
        narrative_labels = self._load_narrative_labels()
        rows = self._fetchall(_NARRATIVES_SQL)
        grouped: dict[str, dict[str, Any]] = {}

        for extraction_id, fallback_document_id, extraction_json in rows:
            extraction = self._parse_extraction(
                extraction_json=extraction_json,
                extraction_id=str(extraction_id),
            )
            if extraction is None or not extraction.narrative_frame_id:
                continue

            frame_id = extraction.narrative_frame_id
            group = grouped.setdefault(
                frame_id,
                {
                    "label": narrative_labels.get(frame_id, frame_id),
                    "document_ids": set(),
                    "actors": set(),
                    "risk_level": RiskLevel.bajo.value,
                    "confidence": Confidence.alta.value,
                    "evidence_fragments": [],
                    "seen_fragments": set(),
                },
            )

            group["document_ids"].add(extraction.document_id or str(fallback_document_id))

            for actor in extraction.actors:
                actor_name = actor.name.strip()
                if actor_name:
                    group["actors"].add(actor_name)

            risk_level = self._normalize_risk_level(extraction.risk_level)
            if _RISK_PRIORITY[risk_level] > _RISK_PRIORITY[group["risk_level"]]:
                group["risk_level"] = risk_level

            confidence = self._normalize_confidence(extraction.confidence)
            if _CONFIDENCE_PRIORITY[confidence] < _CONFIDENCE_PRIORITY[group["confidence"]]:
                group["confidence"] = confidence

            for fragment in extraction.evidence_fragments:
                text = fragment.text.strip()
                if not text or text in group["seen_fragments"]:
                    continue
                group["seen_fragments"].add(text)
                if len(group["evidence_fragments"]) < 3:
                    group["evidence_fragments"].append(text)

        narratives = [
            Narrative(
                narrative_frame_id=frame_id,
                label=data["label"],
                document_ids=sorted(data["document_ids"]),
                actors=sorted(data["actors"]),
                risk_level=data["risk_level"],
                confidence=data["confidence"],
                evidence_fragments=data["evidence_fragments"],
            )
            for frame_id, data in sorted(grouped.items(), key=lambda item: item[0])
        ]

        return NarrativesResponse(narratives=narratives)

    def _fetchall(self, sql: str) -> list[tuple[Any, ...]]:
        conn = self.connection_factory()
        try:
            with conn.cursor() as cur:
                cur.execute(sql)
                return list(cur.fetchall())
        finally:
            conn.close()

    def _load_narrative_labels(self) -> dict[str, str]:
        if self._narrative_labels is not None:
            return self._narrative_labels

        try:
            ontology = validate_ontology(load_ontology(self.ontology_path))
            labels: dict[str, str] = {}
            for item in ontology.get("narrative_frames", []):
                if not isinstance(item, dict):
                    continue
                item_id = item.get("id")
                label = item.get("label")
                if isinstance(item_id, str):
                    labels[item_id] = str(label) if label else item_id
            self._narrative_labels = labels
        except Exception as exc:
            logger.warning(
                "Narrative label lookup unavailable; using frame ids only (%s)",
                exc.__class__.__name__,
            )
            self._narrative_labels = {}

        return self._narrative_labels

    def _parse_extraction(
        self,
        extraction_json: Any,
        extraction_id: str,
    ) -> Extraction | None:
        try:
            payload = extraction_json
            if isinstance(payload, str):
                payload = json.loads(payload)
            if not isinstance(payload, dict):
                raise ValueError("Extraction payload must be a JSON object")
            return Extraction.model_validate(payload)
        except Exception as exc:
            logger.warning(
                "Skipping invalid extraction row id=%s (%s)",
                extraction_id,
                exc.__class__.__name__,
            )
            return None

    @staticmethod
    def _normalize_risk_level(value: RiskLevel | str | None) -> str:
        raw = value.value if isinstance(value, RiskLevel) else str(value or "").strip().lower()
        return raw if raw in _RISK_PRIORITY else RiskLevel.bajo.value

    @staticmethod
    def _normalize_confidence(value: Confidence | str | None) -> str:
        raw = value.value if isinstance(value, Confidence) else str(value or "").strip().lower()
        return raw if raw in _CONFIDENCE_PRIORITY else Confidence.media.value


def create_catalog_service() -> CatalogService:
    """Create the default PostgreSQL-backed catalog service."""
    return CatalogService(connection_factory=get_connection)
