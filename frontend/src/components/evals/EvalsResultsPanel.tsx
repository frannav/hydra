/**
 * EvalsResultsPanel — displays evaluation results from GET /evals/results.
 *
 * Shows run_id, eval_case_id, metrics (as key-value pairs), passed, and trace_id.
 * Provides a refresh button to re-fetch results.
 * Preserves the run result from POST /evals/run until new valid results arrive.
 * passed=false is displayed visibly (not hidden as a UI error).
 * Empty results show a clear empty state.
 *
 * Does not access results_path directly from the filesystem.
 */

"use client";

import { useState, useCallback, useEffect } from "react";
import { getEvalResults } from "@/lib/api-client";
import type { EvalResultsResponse } from "@/lib/api-types";
import StateBlock from "@/components/StateBlock";
import TraceId from "@/components/TraceId";

interface EvalsResultsPanelProps {
  /** The run_id from the POST /evals/run response — used for context display. */
  runId?: string;
  /** Called when results are successfully fetched, receives the full response. */
  onResultsFetched?: (results: EvalResultsResponse) => void;
}

/**
 * Render a single metric value as safe text, tolerating string/number/boolean.
 */
function MetricValue({ value }: { value: unknown }) {
  if (value === null || value === undefined) {
    return <span className="text-gray-500">No disponible</span>;
  }

  if (typeof value === "boolean") {
    return (
      <span
        className={`font-medium ${value ? "text-green-400" : "text-red-400"}`}
      >
        {value ? "true" : "false"}
      </span>
    );
  }

  if (typeof value === "number") {
    return <span className="text-gray-200">{value}</span>;
  }

  // Fallback: stringify safely
  return <span className="text-gray-200">{String(value)}</span>;
}

export default function EvalsResultsPanel({
  runId,
  onResultsFetched,
}: EvalsResultsPanelProps) {
  const [results, setResults] = useState<EvalResultsResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchResults = useCallback(async () => {
    setLoading(true);
    setError(null);

    const { data, error: apiError } = await getEvalResults();

    if (apiError) {
      setError(apiError.message);
      setLoading(false);
      return;
    }

    if (data) {
      setResults(data);
      onResultsFetched?.(data);
    }
    setLoading(false);
  }, [onResultsFetched]);

  // Fetch results on mount
  useEffect(() => {
    void fetchResults();
  }, [fetchResults]);

  // Determine the rendering state
  const state: "loading" | "error" | "empty" | "content" = loading
    ? "loading"
    : error
      ? "error"
      : results && results.results.length > 0
        ? "content"
        : "empty";

  return (
    <div>
      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-lg font-semibold text-gray-100">Resultados de Evals</h2>
        <button
          type="button"
          onClick={fetchResults}
          disabled={loading}
          className="rounded-lg border border-gray-700 bg-gray-800 px-3 py-1.5 text-xs font-medium text-gray-300 transition-colors hover:bg-gray-700 disabled:opacity-50"
        >
          {loading ? "Actualizando..." : "Actualizar"}
        </button>
      </div>

      {/* Run context */}
      {runId && (
        <div className="mb-4 rounded-lg border border-gray-800 bg-gray-900/40 p-3">
          <dl className="grid grid-cols-1 gap-2 sm:grid-cols-2">
            <div>
              <dt className="text-xs text-gray-500">Run ID</dt>
              <dd className="font-mono text-sm text-gray-200">{runId}</dd>
            </div>
          </dl>
        </div>
      )}

      <StateBlock
        state={state}
        errorMessage={error ?? undefined}
        emptyLabel={
          results
            ? "No hay resultados para los casos evaluados."
            : "Ejecuta los evals primero para ver los resultados."
        }
        loadingLabel="Cargando resultados..."
        onRetry={error ? fetchResults : undefined}
      >
        {results && results.results.length > 0 && (
          <div className="space-y-4">
            {results.results.map((result, index) => (
              <div
                key={result.eval_case_id || index}
                className="rounded-lg border border-gray-800 bg-gray-900/40 p-4"
              >
                {/* Header: eval_case_id and passed status */}
                <div className="mb-3 flex items-center justify-between">
                  <h3 className="text-sm font-medium text-gray-200">
                    {result.eval_case_id || `Resultado ${index + 1}`}
                  </h3>
                  <span
                    className={`rounded border px-2 py-0.5 text-xs font-medium ${
                      result.passed
                        ? "bg-green-900/60 text-green-200 border-green-800/60"
                        : "bg-red-900/60 text-red-200 border-red-800/60"
                    }`}
                  >
                    {result.passed ? "Aprobado" : "No aprobado"}
                  </span>
                </div>

                {/* Metrics as key-value pairs */}
                {result.metrics && Object.keys(result.metrics).length > 0 && (
                  <div className="mb-3">
                    <h4 className="mb-2 text-xs font-medium text-gray-400">
                      Métricas
                    </h4>
                    <dl className="grid grid-cols-1 gap-2 sm:grid-cols-2">
                      {Object.entries(result.metrics).map(([key, value]) => (
                        <div key={key} className="sm:col-span-1">
                          <dt className="text-xs text-gray-500">{key}</dt>
                          <dd>
                            <MetricValue value={value} />
                          </dd>
                        </div>
                      ))}
                    </dl>
                  </div>
                )}

                {/* Trace ID */}
                <div className="pt-2">
                  <dt className="text-xs text-gray-500">Trace ID</dt>
                  <dd>
                    <TraceId traceId={result.trace_id} />
                  </dd>
                </div>
              </div>
            ))}
          </div>
        )}
      </StateBlock>
    </div>
  );
}
