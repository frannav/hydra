/**
 * /briefing — HYDRA Briefing view page.
 *
 * Displays a controlled form (BriefingForm) for submitting briefing requests
 * to POST /briefing. No auto-calls on page load. Handles loading, error,
 * and result states.
 *
 * Result rendering is delegated to the BriefingResult component (TASK-FRONT-013).
 */

"use client";

import { useState, useCallback } from "react";
import { createBriefing } from "@/lib/api-client";
import type { BriefingRequest, BriefingResponse } from "@/lib/api-types";
import StateBlock from "@/components/StateBlock";
import BriefingForm from "@/components/briefing/BriefingForm";

export default function BriefingPage() {
  const [response, setResponse] = useState<BriefingResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = useCallback(
    async (request: BriefingRequest) => {
      setLoading(true);
      setError(null);

      const { data, error: apiError } = await createBriefing(request);

      if (apiError) {
        setError(apiError.message);
        setLoading(false);
        return;
      }

      if (data) {
        setResponse(data);
      }
      setLoading(false);
    },
    [],
  );

  // Determine the rendering state
  const state: "loading" | "error" | "empty" | "content" = loading
    ? "loading"
    : error
      ? "error"
      : response
        ? "content"
        : "empty";

  return (
    <div>
      <h1 className="mb-6 text-xl font-semibold text-gray-100">Briefing</h1>

      <div className="mb-8">
        <BriefingForm onSubmit={handleSubmit} />
      </div>

      <StateBlock
        state={state}
        errorMessage={error ?? undefined}
        emptyLabel="Ingresa una pregunta para generar un briefing de inteligencia narrativa."
        loadingLabel="Generando briefing..."
        onRetry={loading ? undefined : () => {}}
      >
        {response && (
          <div className="space-y-4">
            {/* Placeholder for BriefingResult — rendered in TASK-FRONT-013 */}
            <div className="rounded-lg border border-gray-700 bg-gray-900/40 p-4">
              <p className="text-sm text-gray-400">
                Resultado del briefing (renderizado en TASK-FRONT-013).
              </p>
              <p className="mt-2 text-xs text-gray-500">
                briefing_markdown: {response.briefing_markdown.slice(0, 100)}...
              </p>
              {response.risk_level && (
                <p className="mt-1 text-xs text-gray-500">
                  risk_level: {response.risk_level}
                </p>
              )}
              {response.council_review && (
                <p className="mt-1 text-xs text-gray-500">
                  council_review present: evidence_supported={response.council_review.evidence_supported}
                </p>
              )}
              {response.trace_id && (
                <p className="mt-1 text-xs text-gray-500">
                  trace_id: {response.trace_id}
                </p>
              )}
            </div>
          </div>
        )}
      </StateBlock>
    </div>
  );
}
