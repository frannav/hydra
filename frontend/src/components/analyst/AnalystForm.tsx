/**
 * AnalystForm — Controlled form for HYDRA analyst queries.
 *
 * Fields:
 * - question (required): the analyst's query
 * - top_k (number): number of retrieved documents, default 5
 *
 * Validation:
 * - Empty or whitespace-only question does not trigger a request.
 * - top_k <= 0 does not trigger a request.
 * - No auto-calls on mount.
 * - Preserves the user's question on backend error.
 * - Prevents double-submit during loading.
 */

"use client";

import { useState, type FormEvent } from "react";
import type { QueryRequest } from "@/lib/api-types";

interface AnalystFormProps {
  /** Called when a valid query is submitted. Receives the response data or error. */
  onSubmit: (request: QueryRequest) => Promise<void>;
}

export default function AnalystForm({ onSubmit }: AnalystFormProps) {
  const [question, setQuestion] = useState("");
  const [topK, setTopK] = useState(5);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();

    // Prevent double-submit during loading
    if (loading) return;

    // Validate: empty or whitespace-only question
    const trimmedQuestion = question.trim();
    if (!trimmedQuestion) {
      setError("Ingresa una pregunta para enviar.");
      return;
    }

    // Validate: top_k <= 0
    if (topK <= 0) {
      setError("top_k debe ser mayor que 0.");
      return;
    }

    // Clear previous error and start loading
    setError(null);
    setLoading(true);

    const request: QueryRequest = {
      question: trimmedQuestion,
      top_k: topK,
    };

    await onSubmit(request);

    setLoading(false);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {/* Question input */}
      <div>
        <label
          htmlFor="analyst-question"
          className="mb-1 block text-sm font-medium text-gray-300"
        >
          Pregunta
        </label>
        <textarea
          id="analyst-question"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Escribe tu pregunta analítica..."
          rows={3}
          disabled={loading}
          className="w-full rounded-lg border border-gray-700 bg-gray-900 px-3 py-2 text-sm text-gray-100 placeholder-gray-500 transition-colors focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 disabled:opacity-50"
        />
      </div>

      {/* Top-k input */}
      <div>
        <label
          htmlFor="analyst-topk"
          className="mb-1 block text-sm font-medium text-gray-300"
        >
          Top-k (documentos recuperados)
        </label>
        <input
          id="analyst-topk"
          type="number"
          min={1}
          value={topK}
          onChange={(e) => setTopK(Number(e.target.value))}
          disabled={loading}
          className="w-32 rounded-lg border border-gray-700 bg-gray-900 px-3 py-2 text-sm text-gray-100 transition-colors focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 disabled:opacity-50"
        />
      </div>

      {/* Error message */}
      {error && (
        <p className="text-sm text-red-400" role="alert">
          {error}
        </p>
      )}

      {/* Submit button */}
      <button
        type="submit"
        disabled={loading}
        className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-blue-700 disabled:opacity-50"
      >
        {loading ? "Consultando..." : "Consultar"}
      </button>
    </form>
  );
}
