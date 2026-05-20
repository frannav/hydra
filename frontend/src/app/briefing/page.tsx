/**
 * /briefing — HYDRA Briefing view page.
 *
 * Displays a controlled form (BriefingForm) for submitting briefing requests
 * to POST /briefing. No auto-calls on page load. Handles loading, error,
 * and result states.
 *
 * Result rendering is handled by the BriefingResult component.
 */

"use client";

import { useState, useCallback } from "react";
import { createBriefing } from "@/lib/api-client";
import type { BriefingRequest, BriefingResponse } from "@/lib/api-types";
import StateBlock from "@/components/StateBlock";
import BriefingForm from "@/components/briefing/BriefingForm";
import BriefingResult from "@/components/briefing/BriefingResult";

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
        {response && <BriefingResult response={response} />}
      </StateBlock>
    </div>
  );
}
