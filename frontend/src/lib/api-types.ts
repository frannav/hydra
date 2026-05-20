/**
 * TypeScript types derived from sdd/03-api-contract.md.
 *
 * All types are optional where the contract allows fields to be absent.
 * No required fields for domain-specific categorization fields or eval cases.
 */

// ─── Health ────────────────────────────────────────────────────────────────

export interface HealthResponse {
  status: string;
  service: string;
}

// ─── Documents ─────────────────────────────────────────────────────────────

export interface DocumentSummary {
  document_id: string;
  title: string;
  source: string;
  published_at?: string;
  processed?: boolean;
}

export interface DocumentsResponse {
  documents: DocumentSummary[];
}

// ─── Narratives ────────────────────────────────────────────────────────────

export interface NarrativeFrame {
  narrative_frame_id: string;
  label: string;
  document_ids: string[];
  actors: string[];
  risk_level?: string;
  confidence?: string;
  evidence_fragments: string[];
}

export interface NarrativesResponse {
  narratives: NarrativeFrame[];
}

// ─── Ingest ────────────────────────────────────────────────────────────────

export interface IngestRequest {
  source: string;
  dry_run?: boolean;
}

export interface IngestResponse {
  processed_documents: number;
  created_chunks: number;
  errors: string[];
}

// ─── Query ─────────────────────────────────────────────────────────────────

export interface QueryRequest {
  question: string;
  top_k?: number;
}

export interface RetrievedDocument {
  document_id: string;
  chunk_id: string;
  title: string;
  source: string;
  score?: number | null;
  evidence?: string;
}

export interface QueryResponse {
  answer: string;
  retrieved_documents: RetrievedDocument[];
  limitations?: string[];
  trace_id?: string;
}

// ─── Briefing ──────────────────────────────────────────────────────────────

export interface CouncilReview {
  evidence_supported: boolean;
  unsupported_claims: string[];
  risk_review: string;
}

export interface BriefingRequest {
  question: string;
  top_k?: number;
  use_council?: boolean;
}

export interface BriefingResponse {
  briefing_markdown: string;
  risk_level?: string;
  council_review?: CouncilReview;
  trace_id?: string;
}

// ─── Evals ─────────────────────────────────────────────────────────────────

export interface EvalRunRequest {
  case_ids: string[];
  top_k?: number;
}

export interface EvalRunResponse {
  run_id: string;
  total_cases: number;
  results_path: string;
  trace_id?: string;
}

export interface EvalResult {
  eval_case_id: string;
  metrics: Record<string, unknown>;
  passed: boolean;
  trace_id?: string;
}

export interface EvalResultsResponse {
  run_id: string;
  results: EvalResult[];
}

// ─── Upload (optional extension) ───────────────────────────────────────────

export interface UploadMetadata {
  title: string;
  source: string;
  source_type?: string;
  url?: string;
  published_at?: string;
  domain?: string;
  language?: string;
  notes?: string;
}

export interface UploadResponse {
  document_id: string;
  processing_status: string;
  message: string;
}

// ─── Errors ────────────────────────────────────────────────────────────────

export interface ApiError {
  error: {
    code: string;
    message: string;
    details?: Record<string, unknown>;
  };
}
