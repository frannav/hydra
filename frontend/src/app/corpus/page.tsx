/**
 * /corpus — Corpus view page.
 *
 * Fetches documents via api-client.getDocuments() and displays them
 * in a table. Handles loading, error, and empty states gracefully.
 * Missing fields (published_at, processed) are handled without breaking.
 */

"use client";

import { useEffect, useState } from "react";
import { getDocuments } from "@/lib/api-client";
import type { DocumentsResponse } from "@/lib/api-types";
import StateBlock from "@/components/StateBlock";
import CorpusTable from "@/components/corpus/CorpusTable";

export default function CorpusPage() {
  const [documents, setDocuments] = useState<DocumentsResponse["documents"]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchDocuments = async () => {
    setLoading(true);
    setError(null);

    const { data, error: apiError } = await getDocuments();

    if (apiError) {
      setError(apiError.message);
      setLoading(false);
      return;
    }

    if (data) {
      setDocuments(data.documents);
    } else {
      setDocuments([]);
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchDocuments();
  }, []);

  const state: "loading" | "error" | "empty" | "content" = loading
    ? "loading"
    : error
      ? "error"
      : documents.length === 0
        ? "empty"
        : "content";

  return (
    <div>
      <h1 className="mb-6 text-xl font-semibold text-gray-100">Corpus</h1>
      <StateBlock
        state={state}
        errorMessage={error ?? undefined}
        emptyLabel="No hay documentos en el corpus."
        loadingLabel="Cargando documentos..."
        onRetry={fetchDocuments}
      >
        <CorpusTable documents={documents} />
      </StateBlock>
    </div>
  );
}
