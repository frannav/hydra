/**
 * CorpusTable — displays a table of documents from GET /documents.
 *
 * Columns: document_id, title, source, published_at, processed.
 * Missing fields are handled gracefully (shows "No disponible").
 * No document content is displayed.
 */

import type { DocumentSummary } from "@/lib/api-types";
import { formatDate } from "@/lib/formatters";

interface CorpusTableProps {
  documents: DocumentSummary[];
}

export default function CorpusTable({ documents }: CorpusTableProps) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-left text-sm">
        <thead>
          <tr className="border-b border-gray-800 text-gray-400">
            <th className="pb-3 pr-4 font-medium">Document ID</th>
            <th className="pb-3 pr-4 font-medium">Title</th>
            <th className="pb-3 pr-4 font-medium">Source</th>
            <th className="pb-3 pr-4 font-medium">Published</th>
            <th className="pb-3 font-medium">Processed</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-800/50">
          {documents.map((doc) => (
            <tr key={doc.document_id} className="transition-colors hover:bg-gray-900/40">
              <td className="pr-4 py-3 font-mono text-xs text-blue-400">
                {doc.document_id}
              </td>
              <td className="pr-4 py-3 text-gray-200">
                {doc.title || "Sin título"}
              </td>
              <td className="pr-4 py-3 text-gray-300">
                {doc.source || "Sin fuente"}
              </td>
              <td className="pr-4 py-3 text-gray-300">
                {formatDate(doc.published_at ?? null)}
              </td>
              <td className="py-3">
                {doc.processed === undefined ? (
                  <span className="text-gray-500">No disponible</span>
                ) : doc.processed ? (
                  <span className="inline-flex items-center rounded bg-green-900/30 px-2 py-0.5 text-xs text-green-300">
                    Sí
                  </span>
                ) : (
                  <span className="inline-flex items-center rounded bg-yellow-900/30 px-2 py-0.5 text-xs text-yellow-300">
                    No
                  </span>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
