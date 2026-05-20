/**
 * BriefingResult — renders the response from POST /briefing.
 *
 * Renders:
 * - briefing_markdown via react-markdown (safe, no dangerouslySetInnerHTML)
 * - risk_level badge (tolerates unknown values)
 * - CouncilReviewPanel (evidence_supported, unsupported_claims, risk_review)
 * - TraceId component
 *
 * Handles empty markdown, absent council_review, and missing trace_id gracefully.
 */

import ReactMarkdown from "react-markdown";
import type { BriefingResponse } from "@/lib/api-types";
import CouncilReviewPanel from "./CouncilReviewPanel";
import DataBadge from "@/components/DataBadge";
import TraceId from "@/components/TraceId";

interface BriefingResultProps {
  response: BriefingResponse;
}

export default function BriefingResult({ response }: BriefingResultProps) {
  const { briefing_markdown, risk_level, council_review, trace_id } = response;

  return (
    <div className="space-y-4">
      {/* Risk level badge */}
      {risk_level && (
        <div className="flex items-center gap-2">
          <span className="text-sm text-gray-300">Nivel de riesgo:</span>
          <DataBadge value={risk_level} type="risk" label="" />
        </div>
      )}

      {/* Briefing markdown — rendered safely via react-markdown */}
      {briefing_markdown && briefing_markdown.trim() ? (
        <div className="prose prose-invert prose-sm max-w-none">
          <ReactMarkdown
            components={{
              // Ensure no scripts or unsafe elements are rendered
              // react-markdown by default strips <script> tags
              a: ({ href, children }) => (
                <a
                  href={href}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  {children}
                </a>
              ),
            }}
          >
            {briefing_markdown}
          </ReactMarkdown>
        </div>
      ) : (
        <p className="text-sm text-gray-500">
          No hay contenido de briefing disponible.
        </p>
      )}

      {/* Council review panel — absent council_review renders nothing */}
      <CouncilReviewPanel councilReview={council_review} />

      {/* Trace ID */}
      <div className="flex items-center gap-2">
        <span className="text-sm text-gray-400">Trace ID:</span>
        <TraceId traceId={trace_id} />
      </div>
    </div>
  );
}
