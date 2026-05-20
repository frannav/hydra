/**
 * EvidencePanel — Shows evidence fragments per retrieved document.
 *
 * Displays the evidence text (escaped, not HTML) for each document that has one.
 * Shows a safe empty state when no documents have evidence.
 * Handles missing, empty, or very long evidence gracefully.
 * Long evidence is truncated visually with an ellipsis but the full value
 * is preserved in the title attribute for inspection.
 */

import type { RetrievedDocument } from "@/lib/api-types";

interface EvidencePanelProps {
  documents: RetrievedDocument[];
}

const MAX_EVIDENCE_LENGTH = 200;

export default function EvidencePanel({ documents }: EvidencePanelProps) {
  const documentsWithEvidence = documents.filter(
    (doc) => doc.evidence && doc.evidence.trim().length > 0,
  );

  if (documentsWithEvidence.length === 0) {
    return (
      <div className="rounded-lg border border-gray-800 bg-gray-900/40 p-3">
        <p className="text-sm text-gray-500">Sin evidencias disponibles.</p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <h3 className="text-sm font-semibold text-gray-300">Evidencias</h3>
      {documentsWithEvidence.map((doc, index) => {
        const trimmedEvidence = doc.evidence?.trim() ?? "";
        const displayEvidence =
          trimmedEvidence.length > MAX_EVIDENCE_LENGTH
            ? trimmedEvidence.slice(0, MAX_EVIDENCE_LENGTH) + "\u2026"
            : trimmedEvidence;

        return (
          <div
            key={doc.document_id + doc.chunk_id || `evidence-${index}`}
            className="rounded-lg border border-gray-800 bg-gray-900/40 p-3"
          >
            <p className="mb-1 text-xs font-medium text-gray-400">
              {doc.title || doc.document_id}
            </p>
            <p
              className="text-sm text-gray-300 italic"
              title={trimmedEvidence}
            >
              &ldquo;{displayEvidence}&rdquo;
            </p>
          </div>
        );
      })}
    </div>
  );
}
