/**
 * EvidencePanel — Shows evidence fragments per retrieved document.
 *
 * Displays the evidence text (escaped, not HTML) for each document that has one.
 * Handles missing or empty evidence gracefully.
 */

import type { RetrievedDocument } from "@/lib/api-types";

interface EvidencePanelProps {
  documents: RetrievedDocument[];
}

export default function EvidencePanel({ documents }: EvidencePanelProps) {
  const documentsWithEvidence = documents.filter(
    (doc) => doc.evidence && doc.evidence.trim().length > 0,
  );

  if (documentsWithEvidence.length === 0) {
    return null;
  }

  return (
    <div className="space-y-3">
      <h3 className="text-sm font-semibold text-gray-300">Evidencias</h3>
      {documentsWithEvidence.map((doc, index) => (
        <div
          key={doc.document_id + doc.chunk_id || `evidence-${index}`}
          className="rounded-lg border border-gray-800 bg-gray-900/40 p-3"
        >
          <p className="mb-1 text-xs font-medium text-gray-400">
            {doc.title || doc.document_id}
          </p>
          <p className="text-sm text-gray-300 italic">
            &quot;{doc.evidence}&quot;
          </p>
        </div>
      ))}
    </div>
  );
}
