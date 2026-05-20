/**
 * /analyst — HYDRA Analyst view page.
 *
 * Displays a controlled form (AnalystForm) for submitting queries to POST /query.
 * No auto-calls on page load. Handles loading, error, and result states.
 * Preserves the user's question on backend error for retry.
 *
 * Result rendering is delegated to the AnalystResult component.
 */

"use client";

import { useState, useCallback } from "react";
import { queryHydra } from "@/lib/api-client";
import type { QueryRequest, QueryResponse } from "@/lib/api-types";
import StateBlock from "@/components/StateBlock";
import AnalystForm from "@/components/analyst/AnalystForm";
import AnalystResult from "@/components/analyst/AnalystResult";

export default function AnalystPage() {
  const [response, setResponse] = useState<QueryResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = useCallback(
    async (request: QueryRequest) => {
      setLoading(true);
      setError(null);

      const { data, error: apiError } = await queryHydra(request);

      if (apiError) {
        setError(apiError.message);
        // Response is NOT cleared on error — preserves previous result
        // and the form preserves the question for retry
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
      <h1 className="mb-6 text-xl font-semibold text-gray-100">Analyst</h1>

      <div className="mb-8">
        <AnalystForm onSubmit={handleSubmit} />
      </div>

      <StateBlock
        state={state}
        errorMessage={error ?? undefined}
        emptyLabel="Ingresa una pregunta para consultar el analista HYDRA."
        loadingLabel="Consultando..."
        onRetry={loading ? undefined : () => {}}
      >
        {response && <AnalystResult response={response} />}
      </StateBlock>
    </div>
  );
}
