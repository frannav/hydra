/**
 * EvalsRunForm — Controlled form for running evals manually.
 *
 * Fields:
 * - case_ids (string): comma-separated list of case IDs, required (at least one non-empty)
 * - top_k (number): number of retrieved documents per case, default 5
 *
 * Validation:
 * - At least one non-empty case_id is required to submit.
 * - top_k <= 0 does not trigger a request.
 * - Spaces in case_ids are normalized (trimmed).
 * - No auto-calls on mount.
 * - Prevents double-submit during loading.
 * - Only calls POST /evals/run (no invented endpoints).
 */

"use client";

import { useState, type FormEvent } from "react";
import type { EvalRunRequest } from "@/lib/api-types";

interface EvalsRunFormProps {
  /** Called when a valid evals request is submitted. */
  onSubmit: (request: EvalRunRequest) => Promise<void>;
}

export default function EvalsRunForm({ onSubmit }: EvalsRunFormProps) {
  const [caseIdsInput, setCaseIdsInput] = useState("");
  const [topK, setTopK] = useState(5);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();

    // Prevent double-submit during loading
    if (loading) return;

    // Parse and normalize case_ids: split by comma or newline, trim, filter empty
    const caseIds = caseIdsInput
      .split(/[\n,]+/)
      .map((id) => id.trim())
      .filter((id) => id.length > 0);

    // Validate: at least one non-empty case_id required
    if (caseIds.length === 0) {
      setError("Ingresa al menos un case_id para ejecutar los evals.");
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

    const request: EvalRunRequest = {
      case_ids: caseIds,
      top_k: topK,
    };

    await onSubmit(request);

    setLoading(false);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {/* Case IDs input (comma-separated) */}
      <div>
        <label
          htmlFor="evals-case-ids"
          className="mb-1 block text-sm font-medium text-gray-300"
        >
          Case IDs (separados por comas)
        </label>
        <textarea
          id="evals-case-ids"
          value={caseIdsInput}
          onChange={(e) => setCaseIdsInput(e.target.value)}
          placeholder="ej: eval_001, eval_002, eval_003"
          rows={3}
          disabled={loading}
          className="w-full rounded-lg border border-gray-700 bg-gray-900 px-3 py-2 text-sm text-gray-100 placeholder-gray-500 transition-colors focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 disabled:opacity-50"
        />
        <p className="mt-1 text-xs text-gray-500">
          Ingresa los case_ids separados por comas o saltos de línea. Los espacios se normalizan automáticamente.
        </p>
      </div>

      {/* Top-k input */}
      <div>
        <label
          htmlFor="evals-topk"
          className="mb-1 block text-sm font-medium text-gray-300"
        >
          Top-k (documentos recuperados)
        </label>
        <input
          id="evals-topk"
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
        {loading ? "Ejecutando evals..." : "Ejecutar evals"}
      </button>
    </form>
  );
}
