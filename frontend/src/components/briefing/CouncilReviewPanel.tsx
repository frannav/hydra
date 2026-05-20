/**
 * CouncilReviewPanel — displays the council review section of a briefing response.
 *
 * Shows:
 * - evidence_supported: boolean indicator
 * - unsupported_claims: list of claims not supported by evidence (visible when non-empty)
 * - risk_review: narrative risk assessment
 *
 * If council_review is absent or null, the component renders nothing (no error).
 */

import type { CouncilReview } from "@/lib/api-types";

interface CouncilReviewPanelProps {
  councilReview: CouncilReview | null | undefined;
}

export default function CouncilReviewPanel({
  councilReview,
}: CouncilReviewPanelProps) {
  // If council_review is absent, render nothing — do not break the UI.
  if (!councilReview) {
    return null;
  }

  const { evidence_supported, unsupported_claims, risk_review } =
    councilReview;

  return (
    <div className="rounded-lg border border-gray-700 bg-gray-900/40 p-4">
      <h3 className="mb-3 text-sm font-semibold text-gray-200">
        Revisión del Council
      </h3>

      {/* Evidence supported indicator */}
      <div className="mb-3 flex items-center gap-2">
        <span className="text-sm text-gray-300">Evidencia soportada:</span>
        {evidence_supported ? (
          <span className="inline-flex items-center rounded border border-green-800/60 bg-green-900/60 px-2 py-0.5 text-xs font-medium text-green-200">
            Sí
          </span>
        ) : (
          <span className="inline-flex items-center rounded border border-red-800/60 bg-red-900/60 px-2 py-0.5 text-xs font-medium text-red-200">
            No
          </span>
        )}
      </div>

      {/* Unsupported claims — displayed visibly when non-empty */}
      <div className="mb-3">
        <h4 className="mb-2 text-xs font-medium uppercase tracking-wide text-gray-400">
          Afirmaciones no soportadas
        </h4>
        {unsupported_claims && unsupported_claims.length > 0 ? (
          <ul className="space-y-1.5">
            {unsupported_claims.map((claim, index) => (
              <li
                key={index}
                className="rounded border border-orange-900/40 bg-orange-950/30 px-3 py-2 text-sm text-orange-200"
              >
                {claim}
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-xs text-gray-500">
            Ninguna afirmación no soportada detectada.
          </p>
        )}
      </div>

      {/* Risk review */}
      {risk_review && (
        <div>
          <h4 className="mb-2 text-xs font-medium uppercase tracking-wide text-gray-400">
            Revisión de riesgo
          </h4>
          <p className="rounded border border-gray-700 bg-gray-800/40 px-3 py-2 text-sm text-gray-300">
            {risk_review}
          </p>
        </div>
      )}
    </div>
  );
}
