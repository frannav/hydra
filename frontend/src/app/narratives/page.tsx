/**
 * /narratives — Narratives view page.
 *
 * Fetches narratives via api-client.getNarratives() and displays them
 * in a table. Handles loading, error, and empty states gracefully.
 * Shows narrative_frame_id, label, document_ids, actors, risk_level,
 * confidence, evidence_fragments. No extra fields beyond the contract.
 */

"use client";

import { useEffect, useState } from "react";
import { getNarratives } from "@/lib/api-client";
import type { NarrativesResponse } from "@/lib/api-types";
import StateBlock from "@/components/StateBlock";
import NarrativesTable from "@/components/narratives/NarrativesTable";

export default function NarrativesPage() {
  const [narratives, setNarratives] = useState<NarrativesResponse["narratives"]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchNarratives = async () => {
    setLoading(true);
    setError(null);

    const { data, error: apiError } = await getNarratives();

    if (apiError) {
      setError(apiError.message);
      setLoading(false);
      return;
    }

    if (data) {
      setNarratives(data.narratives);
    } else {
      setNarratives([]);
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchNarratives();
  }, []);

  const state: "loading" | "error" | "empty" | "content" = loading
    ? "loading"
    : error
      ? "error"
      : narratives.length === 0
        ? "empty"
        : "content";

  return (
    <div>
      <h1 className="mb-6 text-xl font-semibold text-gray-100">Narrativas</h1>
      <StateBlock
        state={state}
        errorMessage={error ?? undefined}
        emptyLabel="No hay narrativas disponibles."
        loadingLabel="Cargando narrativas..."
        onRetry={fetchNarratives}
      >
        <NarrativesTable narratives={narratives} />
      </StateBlock>
    </div>
  );
}
