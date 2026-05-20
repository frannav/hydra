/**
 * AnalystResult — Renders the structured response from a HYDRA analyst query.
 *
 * Displays:
 * - answer (escaped text, never HTML)
 * - RetrievedDocuments component for retrieved documents list
 * - EvidencePanel component for evidence fragments
 * - Limitations visibly (or "No hay limitaciones reportadas." if empty/absent)
 * - TraceId via TraceId component (shows "No disponible" if absent)
 *
 * Does NOT expose prompts, internal data, or any fields outside the API contract.
 */

import type { QueryResponse } from "@/lib/api-types";
import RetrievedDocuments from "./RetrievedDocuments";
import EvidencePanel from "./EvidencePanel";
import TraceId from "@/components/TraceId";

interface AnalystResultProps {
  response: QueryResponse;
}

export default function AnalystResult({ response }: AnalystResultProps) {
  return (
    <div className="space-y-6">
      {/* Answer — rendered as escaped text, not HTML */}
      <div>
        <h2 className="mb-2 text-sm font-semibold text-gray-200">Respuesta</h2>
        <div className="rounded-lg border border-gray-800 bg-gray-900/60 p-4 text-sm text-gray-300">
          {response.answer}
        </div>
      </div>

      {/* Retrieved documents */}
      <div>
        <h2 className="mb-2 text-sm font-semibold text-gray-200">
          Documentos recuperados ({(response.retrieved_documents ?? []).length})
        </h2>
        <RetrievedDocuments documents={response.retrieved_documents ?? []} />
      </div>

      {/* Evidence panel */}
      <EvidencePanel documents={response.retrieved_documents} />

      {/* Limitations */}
      <div>
        <h2 className="mb-2 text-sm font-semibold text-gray-200">Limitaciones</h2>
        {response.limitations && response.limitations.length > 0 ? (
          <ul className="list-inside list-disc text-sm text-yellow-400">
            {response.limitations.map((lim, index) => (
              <li key={index}>{lim}</li>
            ))}
          </ul>
        ) : (
          <p className="text-sm text-gray-500">No hay limitaciones reportadas.</p>
        )}
      </div>

      {/* Trace ID */}
      <TraceId traceId={response.trace_id} />
    </div>
  );
}
