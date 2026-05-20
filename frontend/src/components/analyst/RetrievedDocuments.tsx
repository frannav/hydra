/**
 * RetrievedDocuments — Renders the list of retrieved documents from a HYDRA query response.
 *
 * Displays document_id, chunk_id, title, source, score, and evidence per document.
 * Shows an explicit empty state when the list is empty or absent.
 * Handles null/0/out-of-range scores gracefully.
 */

import type { RetrievedDocument } from "@/lib/api-types";

interface RetrievedDocumentsProps {
  documents: RetrievedDocument[];
}

export default function RetrievedDocuments({ documents }: RetrievedDocumentsProps) {
  if (!documents || documents.length === 0) {
    return (
      <div className="rounded-lg border border-gray-800 bg-gray-900/40 p-6 text-center">
        <p className="text-sm text-gray-500">
          No se recuperaron documentos para esta consulta.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {documents.map((doc, index) => (
        <div
          key={doc.document_id + doc.chunk_id || `doc-${index}`}
          className="rounded-lg border border-gray-800 bg-gray-900/60 p-3"
        >
          {/* Title and score */}
          <div className="mb-1 flex items-center justify-between">
            <span className="text-sm font-medium text-gray-200">
              {doc.title || doc.document_id}
            </span>
            {typeof doc.score === "number" && (
              <span className="text-xs text-blue-400">
                score: {doc.score.toFixed(2)}
              </span>
            )}
          </div>

          {/* Metadata: document_id, chunk_id, source */}
          <div className="text-xs text-gray-500">
            {doc.document_id}
            {doc.chunk_id && (
              <>
                {" · "}
                {doc.chunk_id}
              </>
            )}
            {doc.source && (
              <>
                {" · "}
                {doc.source}
              </>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
