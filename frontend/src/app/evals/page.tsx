/**
 * /evals — HYDRA Evals view page.
 *
 * Displays a controlled form (EvalsRunForm) for manually entering case_ids
 * and running evals via POST /evals/run. No auto-calls on page load.
 *
 * Shows run_id, results_path, and trace_id from the POST /evals/run response.
 * EvalsResultsPanel consumes GET /evals/results and shows detailed results.
 * Run result is preserved until new valid results arrive.
 * Does not call any invented endpoints.
 */

"use client";

import { useState, useCallback } from "react";
import { runEvals } from "@/lib/api-client";
import type { EvalRunRequest, EvalRunResponse, EvalResultsResponse } from "@/lib/api-types";
import StateBlock from "@/components/StateBlock";
import EvalsRunForm from "@/components/evals/EvalsRunForm";
import EvalsResultsPanel from "@/components/evals/EvalsResultsPanel";

export default function EvalsPage() {
  const [response, setResponse] = useState<EvalRunResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = useCallback(
    async (request: EvalRunRequest) => {
      setLoading(true);
      setError(null);

      const { data, error: apiError } = await runEvals(request);

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

  // When results are fetched, preserve the run response (don't clear it).
  const handleResultsFetched = useCallback(
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    (_results: EvalResultsResponse) => {
      // Run result preserved — do not clear `response` on successful results fetch.
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
      <h1 className="mb-6 text-xl font-semibold text-gray-100">Evals</h1>

      <div className="mb-8">
        <EvalsRunForm onSubmit={handleSubmit} />
      </div>

      <StateBlock
        state={state}
        errorMessage={error ?? undefined}
        emptyLabel="Ingresa al menos un case_id para ejecutar los evals manualmente."
        loadingLabel="Ejecutando evals..."
        onRetry={loading ? undefined : () => {}}
      >
        {response && (
          <div className="space-y-4 rounded-lg border border-gray-800 bg-gray-900/40 p-4">
            {/* Run ID */}
            <div>
              <h3 className="mb-2 text-sm font-medium text-gray-300">
                Resultado de ejecución
              </h3>
              <dl className="grid grid-cols-1 gap-2 sm:grid-cols-2">
                <div>
                  <dt className="text-xs text-gray-500">Run ID</dt>
                  <dd className="font-mono text-sm text-gray-200">
                    {response.run_id}
                  </dd>
                </div>
                <div>
                  <dt className="text-xs text-gray-500">Total Cases</dt>
                  <dd className="text-sm text-gray-200">
                    {response.total_cases}
                  </dd>
                </div>
                <div className="sm:col-span-2">
                  <dt className="text-xs text-gray-500">Results Path</dt>
                  <dd className="font-mono text-sm text-gray-200">
                    {response.results_path}
                  </dd>
                </div>
              </dl>
            </div>
          </div>
        )}
      </StateBlock>

      {/* Results panel — shows results from GET /evals/results */}
      <div className="mt-8">
        <EvalsResultsPanel
          runId={response?.run_id}
          onResultsFetched={handleResultsFetched}
        />
      </div>
    </div>
  );
}
