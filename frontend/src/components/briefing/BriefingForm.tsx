/**
 * BriefingForm — Controlled form for HYDRA briefing requests.
 *
 * Fields:
 * - question (required): the briefing question
 * - top_k (number): number of retrieved documents, default 5
 * - use_council (boolean): whether to use the LLM council, default true
 *
 * Validation:
 * - Empty or whitespace-only question does not trigger a request.
 * - top_k <= 0 does not trigger a request.
 * - No auto-calls on mount.
 * - use_council=false is sent correctly in the request.
 * - Prevents double-submit during loading.
 */

"use client";

import { useState, type FormEvent } from "react";
import type { BriefingRequest } from "@/lib/api-types";

interface BriefingFormProps {
  /** Called when a valid briefing request is submitted. */
  onSubmit: (request: BriefingRequest) => Promise<void>;
}

export default function BriefingForm({ onSubmit }: BriefingFormProps) {
  const [question, setQuestion] = useState("");
  const [topK, setTopK] = useState(5);
  const [useCouncil, setUseCouncil] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();

    // Prevent double-submit during loading
    if (loading) return;

    // Validate: empty or whitespace-only question
    const trimmedQuestion = question.trim();
    if (!trimmedQuestion) {
      setError("Ingresa una pregunta para generar el briefing.");
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

    const request: BriefingRequest = {
      question: trimmedQuestion,
      top_k: topK,
      use_council: useCouncil,
    };

    await onSubmit(request);

    setLoading(false);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {/* Question input */}
      <div>
        <label
          htmlFor="briefing-question"
          className="mb-1 block text-sm font-medium text-gray-300"
        >
          Pregunta
        </label>
        <textarea
          id="briefing-question"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Escribe la pregunta para generar un briefing..."
          rows={3}
          disabled={loading}
          className="w-full rounded-lg border border-gray-700 bg-gray-900 px-3 py-2 text-sm text-gray-100 placeholder-gray-500 transition-colors focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 disabled:opacity-50"
        />
      </div>

      {/* Top-k input */}
      <div>
        <label
          htmlFor="briefing-topk"
          className="mb-1 block text-sm font-medium text-gray-300"
        >
          Top-k (documentos recuperados)
        </label>
        <input
          id="briefing-topk"
          type="number"
          min={1}
          value={topK}
          onChange={(e) => setTopK(Number(e.target.value))}
          disabled={loading}
          className="w-32 rounded-lg border border-gray-700 bg-gray-900 px-3 py-2 text-sm text-gray-100 transition-colors focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 disabled:opacity-50"
        />
      </div>

      {/* Use council toggle */}
      <div className="flex items-center gap-2">
        <input
          id="briefing-use-council"
          type="checkbox"
          checked={useCouncil}
          onChange={(e) => setUseCouncil(e.target.checked)}
          disabled={loading}
          className="h-4 w-4 rounded border-gray-700 bg-gray-900 text-blue-600 focus:ring-blue-500 disabled:opacity-50"
        />
        <label
          htmlFor="briefing-use-council"
          className="text-sm text-gray-300"
        >
          Usar council de LLMs para revisión
        </label>
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
        {loading ? "Generando briefing..." : "Generar briefing"}
      </button>
    </form>
  );
}
