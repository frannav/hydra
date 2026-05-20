/**
 * /analyst — HYDRA Analyst view page.
 *
 * Displays a controlled form (AnalystForm) for submitting queries to POST /query.
 * No auto-calls on page load. Handles loading, error, and result states.
 * Preserves the user's question on backend error for retry.
 */

"use client";

import { useState, useCallback } from "react";
import { queryHydra } from "@/lib/api-client";
import type { QueryRequest, QueryResponse } from "@/lib/api-types";
import StateBlock from "@/components/StateBlock";
import AnalystForm from "@/components/analyst/AnalystForm";

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
        {response && (
          <div className="space-y-6">
            {/* Answer */}
            <div>
              <h2 className="mb-2 text-sm font-semibold text-gray-200">
                Respuesta
              </h2>
              <div className="rounded-lg border border-gray-800 bg-gray-900/60 p-4 text-sm text-gray-300">
                {response.answer}
              </div>
            </div>

            {/* Retrieved documents */}
            <div>
              <h2 className="mb-2 text-sm font-semibold text-gray-200">
                Documentos recuperados ({response.retrieved_documents.length})
              </h2>
              {response.retrieved_documents.length === 0 ? (
                <p className="text-sm text-gray-500">
                  No se recuperaron documentos para esta consulta.
                </p>
              ) : (
                <div className="space-y-3">
                  {response.retrieved_documents.map((doc, index) => (
                    <div
                      key={doc.document_id + doc.chunk_id || index}
                      className="rounded-lg border border-gray-800 bg-gray-900/60 p-3"
                    >
                      <div className="mb-1 flex items-center justify-between">
                        <span className="text-sm font-medium text-gray-200">
                          {doc.title || doc.document_id}
                        </span>
                        {doc.score !== null && doc.score !== undefined && (
                          <span className="text-xs text-blue-400">
                            score: {doc.score.toFixed(2)}
                          </span>
                        )}
                      </div>
                      <div className="text-xs text-gray-500">
                        {doc.document_id}
                        {doc.chunk_id && (
                          <>
                            {" · "}
                            {doc.chunk_id}
                          </>
                        )}
                        {doc.source && (
                          <>
                            {" · "}
                            {doc.source}
                          </>
                        )}
                      </div>
                      {doc.evidence && (
                        <p className="mt-2 text-xs text-gray-400 italic">
                          &quot;{doc.evidence}&quot;
                        </p>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Limitations */}
            <div>
              <h2 className="mb-2 text-sm font-semibold text-gray-200">
                Limitaciones
              </h2>
              {response.limitations && response.limitations.length > 0 ? (
                <ul className="list-inside list-disc text-sm text-yellow-400">
                  {response.limitations.map((lim, index) => (
                    <li key={index}>{lim}</li>
                  ))}
                </ul>
              ) : (
                <p className="text-sm text-gray-500">
                  No hay limitaciones reportadas.
                </p>
              )}
            </div>

            {/* Trace ID */}
            {response.trace_id && (
              <div className="text-xs text-gray-500">
                Trace ID: {response.trace_id}
              </div>
            )}
            {!response.trace_id && (
              <div className="text-xs text-gray-600">
                Trace ID: No disponible
              </div>
            )}
          </div>
        )}
      </StateBlock>
    </div>
  );
}
