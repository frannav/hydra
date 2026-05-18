"""HYDRA API — Canonical Pydantic schemas.

These schemas are domain-level and must not be coupled to
pgvector, Neo4j, or the frontend. API-specific wrappers
live alongside the endpoint handlers.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class SourceType(str, Enum):
    """Types of document sources."""

    medio = "medio"
    institucion = "institucion"
    informe = "informe"
    comunicado = "comunicado"
    otro = "otro"


class IngestionSource(str, Enum):
    """Where a document came from."""

    local_corpus = "local_corpus"
    frontend_upload = "frontend_upload"


class ProcessingStatus(str, Enum):
    """Document processing lifecycle."""

    pending = "pending"
    processing = "processing"
    processed = "processed"
    failed = "failed"


class RiskLevel(str, Enum):
    """Risk classification."""

    bajo = "bajo"
    medio = "medio"
    alto = "alto"


class Confidence(str, Enum):
    """Confidence classification."""

    baja = "baja"
    media = "media"
    alta = "alta"


# ---------------------------------------------------------------------------
# Metadata
# ---------------------------------------------------------------------------

class DocumentMetadata(BaseModel):
    """Minimal metadata for a document."""

    title: str
    source: str
    source_type: SourceType = SourceType.otro
    url: str | None = None
    published_at: str | None = None
    collected_at: str | None = None
    domain: str
    language: str = "es"
    ingestion_source: IngestionSource = IngestionSource.local_corpus
    raw_path: str | None = None
    content_hash: str | None = None
    notes: str | None = None


# ---------------------------------------------------------------------------
# Document
# ---------------------------------------------------------------------------

class Document(BaseModel):
    """Canonical document record."""

    document_id: str
    title: str
    source: str
    url: str | None = None
    published_at: str | None = None
    domain: str
    raw_path: str | None = None
    content_hash: str | None = None
    ingestion_source: IngestionSource = IngestionSource.local_corpus
    processing_status: ProcessingStatus = ProcessingStatus.pending
    processed: bool = False


# ---------------------------------------------------------------------------
# Chunks
# ---------------------------------------------------------------------------

class DocumentChunk(BaseModel):
    """A chunk derived from a document, ready for embedding."""

    id: str
    document_id: str
    chunk_index: int
    content: str
    metadata: dict[str, Any] = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# Ingestion pipeline
# ---------------------------------------------------------------------------

class RawDocument(BaseModel):
    """Raw document before cleaning, chunking, or extraction."""

    document_id: str
    text: str
    metadata: DocumentMetadata


class IngestedDocument(BaseModel):
    """Normalized document result before persistence."""

    document_id: str
    metadata: DocumentMetadata
    content_hash: str
    raw_path: str | None = None
    text: str


class IngestionRunResult(BaseModel):
    """Result of an ingestion run."""

    processed_documents: int
    created_chunks: int
    errors: list[str] = Field(default_factory=list)
    dry_run: bool = False


# ---------------------------------------------------------------------------
# Query
# ---------------------------------------------------------------------------

class QueryRequest(BaseModel):
    """Request body for POST /query."""

    question: str
    top_k: int = 5


class RetrievedDocument(BaseModel):
    """A document chunk retrieved for a query."""

    document_id: str
    chunk_id: str
    title: str
    source: str
    score: float
    evidence: str


class QueryResponse(BaseModel):
    """Response body for POST /query."""

    answer: str
    retrieved_documents: list[RetrievedDocument] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    trace_id: str


# ---------------------------------------------------------------------------
# Briefing
# ---------------------------------------------------------------------------

class CouncilReview(BaseModel):
    """Council review section of a briefing."""

    evidence_supported: bool
    unsupported_claims: list[str] = Field(default_factory=list)
    risk_review: str


class BriefingRequest(BaseModel):
    """Request body for POST /briefing."""

    question: str
    top_k: int = 5
    use_council: bool = False


class BriefingResponse(BaseModel):
    """Response body for POST /briefing."""

    briefing_markdown: str
    risk_level: RiskLevel = RiskLevel.medio
    council_review: CouncilReview | None = None
    trace_id: str


# ---------------------------------------------------------------------------
# Extractions
# ---------------------------------------------------------------------------

class EvidenceFragment(BaseModel):
    """A text fragment used as evidence."""

    text: str
    source_document_id: str
    relevance: str | None = None


class Actor(BaseModel):
    """An actor extracted from a document."""

    name: str
    actor_type: str | None = None


class Location(BaseModel):
    """A location extracted from a document."""

    name: str
    type: str | None = None


class Event(BaseModel):
    """An event extracted from a document."""

    description: str
    date: str | None = None
    location: str | None = None


class Extraction(BaseModel):
    """Canonical extraction from a document, validated via Pydantic."""

    document_id: str
    title: str
    source: str
    date: str | None = None
    main_topic: str | None = None
    main_narrative: str | None = None
    narrative_frame_id: str | None = None
    secondary_narratives: list[str] = Field(default_factory=list)
    actors: list[Actor] = Field(default_factory=list)
    actor_types: list[str] = Field(default_factory=list)
    locations: list[Location] = Field(default_factory=list)
    events: list[Event] = Field(default_factory=list)
    affected_sectors: list[str] = Field(default_factory=list)
    threat_types: list[str] = Field(default_factory=list)
    risk_level: RiskLevel = RiskLevel.medio
    confidence: Confidence = Confidence.media
    evidence_fragments: list[EvidenceFragment] = Field(default_factory=list)
    analyst_summary: str | None = None
    limitations: list[str] = Field(default_factory=list)
    schema_version: str = "1.0"


# ---------------------------------------------------------------------------
# Graph Projection
# ---------------------------------------------------------------------------

class GraphNode(BaseModel):
    """A node in the graph projection."""

    id: str
    type: str  # Document, Actor, NarrativeFrame, Location, Event, Sector, ThreatType
    label: str


class GraphEdge(BaseModel):
    """An edge in the graph projection."""

    source: str
    target: str
    type: str  # MENTIONS, HAS_NARRATIVE, OCCURS_IN, AFFECTS, SUPPORTED_BY
    evidence_refs: list[str] = Field(default_factory=list)


class GraphProjection(BaseModel):
    """Derived graph projection from a validated extraction."""

    document_id: str
    nodes: list[GraphNode] = Field(default_factory=list)
    edges: list[GraphEdge] = Field(default_factory=list)
    evidence_refs: list[str] = Field(default_factory=list)
    schema_version: str = "1.0"


# ---------------------------------------------------------------------------
# Evals
# ---------------------------------------------------------------------------

class EvalCase(BaseModel):
    """A single evaluation case."""

    id: str
    question: str
    expected_documents: list[str] = Field(default_factory=list)
    expected_topics: list[str] = Field(default_factory=list)
    expected_answer_traits: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)


class EvalMetrics(BaseModel):
    """Metrics for a single eval result."""

    precision_at_k: float = 0.0
    json_validity: bool = True
    groundedness: str = "pass"


class EvalResult(BaseModel):
    """Result of running an eval case."""

    eval_case_id: str
    metrics: EvalMetrics = Field(default_factory=EvalMetrics)
    passed: bool = True
    trace_id: str | None = None


class EvalRunRequest(BaseModel):
    """Request body for POST /evals/run."""

    case_ids: list[str]
    top_k: int = 5


class EvalRunResponse(BaseModel):
    """Response body for POST /evals/run."""

    run_id: str
    total_cases: int
    results_path: str
    trace_id: str | None = None


class EvalResultsResponse(BaseModel):
    """Response body for GET /evals/results."""

    run_id: str
    results: list[EvalResult] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Ingest
# ---------------------------------------------------------------------------

class IngestRequest(BaseModel):
    """Request body for POST /ingest."""

    source: IngestionSource = IngestionSource.local_corpus
    dry_run: bool = False


class IngestResponse(BaseModel):
    """Response body for POST /ingest."""

    processed_documents: int
    created_chunks: int
    errors: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Documents list response
# ---------------------------------------------------------------------------

class DocumentsResponse(BaseModel):
    """Response body for GET /documents."""

    documents: list[Document] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Narratives
# ---------------------------------------------------------------------------

class Narrative(BaseModel):
    """A narrative frame derived from extractions."""

    narrative_frame_id: str
    label: str
    document_ids: list[str] = Field(default_factory=list)
    actors: list[str] = Field(default_factory=list)
    risk_level: RiskLevel = RiskLevel.medio
    confidence: Confidence = Confidence.media
    evidence_fragments: list[str] = Field(default_factory=list)


class NarrativesResponse(BaseModel):
    """Response body for GET /narratives."""

    narratives: list[Narrative] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

class HealthResponse(BaseModel):
    """Response body for GET /health."""

    status: str
    service: str


# ---------------------------------------------------------------------------
# Error
# ---------------------------------------------------------------------------

class ErrorDetails(BaseModel):
    """Standard error response body."""

    error: dict[str, Any] = Field(default_factory=dict)
