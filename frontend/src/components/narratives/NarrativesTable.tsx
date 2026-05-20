/**
 * NarrativesTable — displays a table of narratives from GET /narratives.
 *
 * Columns: narrative_frame_id, label, document_ids, actors, risk_level,
 * confidence, evidence_fragments.
 *
 * No fields beyond the API contract are displayed.
 * Empty actors/evidence_fragments shows "Sin evidencias" or equivalent.
 * Risk/confidence badges tolerate unknown values.
 */

import type { NarrativeFrame } from "@/lib/api-types";
import DataBadge from "@/components/DataBadge";
import EvidenceList from "@/components/narratives/EvidenceList";

interface NarrativesTableProps {
  narratives: NarrativeFrame[];
}

export default function NarrativesTable({ narratives }: NarrativesTableProps) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-left text-sm">
        <thead>
          <tr className="border-b border-gray-800 text-gray-400">
            <th className="pb-3 pr-4 font-medium">Frame ID</th>
            <th className="pb-3 pr-4 font-medium">Label</th>
            <th className="pb-3 pr-4 font-medium">Documentos</th>
            <th className="pb-3 pr-4 font-medium">Actores</th>
            <th className="pb-3 pr-4 font-medium">Riesgo</th>
            <th className="pb-3 pr-4 font-medium">Confianza</th>
            <th className="pb-3 font-medium">Evidencias</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-800/50">
          {narratives.map((narrative) => (
            <tr
              key={narrative.narrative_frame_id}
              className="transition-colors hover:bg-gray-900/40"
            >
              <td className="pr-4 py-3 font-mono text-xs text-blue-400">
                {narrative.narrative_frame_id}
              </td>
              <td className="pr-4 py-3 text-gray-200">
                {narrative.label || "Sin etiqueta"}
              </td>
              <td className="pr-4 py-3">
                {narrative.document_ids && narrative.document_ids.length > 0 ? (
                  <span className="font-mono text-xs text-gray-300">
                    {narrative.document_ids.join(", ")}
                  </span>
                ) : (
                  <span className="text-xs text-gray-500">Sin documentos</span>
                )}
              </td>
              <td className="pr-4 py-3">
                {narrative.actors && narrative.actors.length > 0 ? (
                  <ul className="list-inside list-disc space-y-0.5 text-xs text-gray-300">
                    {narrative.actors.map((actor, index) => (
                      <li key={index}>{actor}</li>
                    ))}
                  </ul>
                ) : (
                  <span className="text-xs text-gray-500">Sin actores</span>
                )}
              </td>
              <td className="pr-4 py-3">
                <DataBadge value={narrative.risk_level ?? null} type="risk" />
              </td>
              <td className="pr-4 py-3">
                <DataBadge value={narrative.confidence ?? null} type="confidence" />
              </td>
              <td className="py-3">
                <EvidenceList fragments={narrative.evidence_fragments ?? []} />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
