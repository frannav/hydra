/**
 * Centralized HTTP client for HYDRA backend.
 *
 * All API calls go through this module. No fetch() calls exist outside this file.
 * Errors are handled safely: no stack traces, no raw error objects, no secrets.
 */

import type {
  ApiError,
  BriefingRequest,
  BriefingResponse,
  DocumentsResponse,
  EvalResultsResponse,
  EvalRunRequest,
  EvalRunResponse,
  NarrativesResponse,
  QueryRequest,
  QueryResponse,
} from "./api-types";
import { getApiBaseUrl } from "./env";

// ─── Helpers ────────────────────────────────────────────────────────────────

/**
 * Build a full URL from the API base and an endpoint path.
 */
function buildUrl(endpoint: string): string {
  const base = getApiBaseUrl();
  // base already has trailing slash stripped by env.ts
  return `${base}${endpoint}`;
}

/**
 * Safe JSON parse that returns null on failure instead of throwing.
 */
function safeJsonParse<T>(body: string): T | null {
  try {
    return JSON.parse(body) as T;
  } catch {
    return null;
  }
}

/**
 * Classify a network-level error into a safe message.
 */
function networkErrorMessage(error: unknown): string {
  if (error instanceof TypeError && "message" in error) {
    const msg = String((error as { message: string }).message);
    if (msg.includes("fetch")) {
      return "No se pudo conectar con el servidor. Verifica que el backend esté en ejecución.";
    }
  }
  return "Error de red. Verifica tu conexión e intenta de nuevo.";
}

/**
 * Extract a safe error message from a response body and status.
 * Returns { code, message } or a safe fallback.
 */
function parseErrorResponse(
  body: string | null,
  status: number,
): { code: string; message: string } {
  // Try to parse the standard error shape
  if (body) {
    const parsed = safeJsonParse<ApiError>(body);
    if (parsed?.error?.message) {
      return {
        code: parsed.error.code || String(status),
        message: parsed.error.message,
      };
    }
  }

  // Fallback: use the status code
  const statusMessages: Record<number, string> = {
    400: "Solicitud inválida",
    404: "Recurso no encontrado",
    408: "Tiempo de espera agotado",
    429: "Demasiadas solicitudes. Intenta de nuevo más tarde.",
    500: "Error del servidor",
    502: "Servidor no disponible",
    503: "Servidor no disponible",
    504: "Tiempo de espera agotado del servidor",
  };

  return {
    code: String(status),
    message: statusMessages[status] || `Error del servidor (${status})`,
  };
}

/**
 * Generic fetch wrapper with safe error handling.
 *
 * Returns { data, error } where exactly one is non-null.
 * `data` is the parsed JSON body (or null for no-body responses).
 * `error` is a safe { code, message } object, or null on success.
 */
async function fetchJson<T>(
  url: string,
  options?: RequestInit,
): Promise<{ data: T | null; error: { code: string; message: string } | null }> {
  try {
    const response = await fetch(url, {
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
      },
      ...options,
    });

    // No content (204)
    if (response.status === 204) {
      return { data: null as unknown as T, error: null };
    }

    const text = await response.text();

    if (!response.ok) {
      const { code, message } = parseErrorResponse(text, response.status);
      return { data: null, error: { code, message } };
    }

    // Try to parse JSON for successful responses
    if (!text.trim()) {
      return { data: null as unknown as T, error: null };
    }

    const parsed = safeJsonParse<T>(text);
    if (parsed === null) {
      // Server returned non-JSON on success — safe fallback
      return {
        data: null,
        error: {
          code: "invalid_response",
          message: "Respuesta del servidor en formato inesperado.",
        },
      };
    }

    return { data: parsed, error: null };
  } catch (err) {
    // Network error, timeout, DNS failure, etc.
    return {
      data: null,
      error: {
        code: "network_error",
        message: networkErrorMessage(err),
      },
    };
  }
}

// ─── Public API ─────────────────────────────────────────────────────────────

/**
 * GET /documents
 */
export async function getDocuments(): Promise<{
  data: DocumentsResponse | null;
  error: { code: string; message: string } | null;
}> {
  return fetchJson<DocumentsResponse>(buildUrl("/documents"));
}

/**
 * GET /narratives
 */
export async function getNarratives(): Promise<{
  data: NarrativesResponse | null;
  error: { code: string; message: string } | null;
}> {
  return fetchJson<NarrativesResponse>(buildUrl("/narratives"));
}

/**
 * POST /query
 */
export async function queryHydra(
  request: QueryRequest,
): Promise<{ data: QueryResponse | null; error: { code: string; message: string } | null }> {
  return fetchJson<QueryResponse>(buildUrl("/query"), {
    method: "POST",
    body: JSON.stringify(request),
  });
}

/**
 * POST /briefing
 */
export async function createBriefing(
  request: BriefingRequest,
): Promise<{ data: BriefingResponse | null; error: { code: string; message: string } | null }> {
  return fetchJson<BriefingResponse>(buildUrl("/briefing"), {
    method: "POST",
    body: JSON.stringify(request),
  });
}

/**
 * POST /evals/run
 */
export async function runEvals(
  request: EvalRunRequest,
): Promise<{ data: EvalRunResponse | null; error: { code: string; message: string } | null }> {
  return fetchJson<EvalRunResponse>(buildUrl("/evals/run"), {
    method: "POST",
    body: JSON.stringify(request),
  });
}

/**
 * GET /evals/results
 */
export async function getEvalResults(): Promise<{
  data: EvalResultsResponse | null;
  error: { code: string; message: string } | null;
}> {
  return fetchJson<EvalResultsResponse>(buildUrl("/evals/results"));
}
