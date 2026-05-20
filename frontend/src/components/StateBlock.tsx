/**
 * StateBlock — unified loading/error/empty/content state component.
 *
 * Renders one of four states based on the `state` prop:
 * - "loading": a spinner with a message
 * - "error": a safe error message with an optional retry action
 * - "empty": a message when data exists but the list is empty
 * - "content": the actual content (default)
 *
 * All messages are safe — no stack traces, no raw error objects, no secrets.
 */

interface StateBlockProps {
  /** Current state of the data fetching/rendering cycle */
  state: "loading" | "error" | "empty" | "content";
  /** Content to render when state is "content" */
  children?: React.ReactNode;
  /** Error message to display (safe text only, no stack traces) */
  errorMessage?: string;
  /** Label shown in the empty state */
  emptyLabel?: string;
  /** Loading message shown during the loading state */
  loadingLabel?: string;
  /** Optional retry action — when provided, shows a retry button */
  onRetry?: () => void;
}

const DEFAULT_ERROR_MESSAGE = "Error al cargar los datos. Intenta de nuevo.";
const DEFAULT_EMPTY_LABEL = "No hay datos disponibles.";
const DEFAULT_LOADING_LABEL = "Cargando...";

export default function StateBlock({
  state,
  children,
  errorMessage,
  emptyLabel,
  loadingLabel,
  onRetry,
}: StateBlockProps) {
  // ─── Loading ────────────────────────────────────────────────────────────

  if (state === "loading") {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <div className="mx-auto mb-3 h-8 w-8 animate-spin rounded-full border-2 border-gray-600 border-t-blue-500" />
          <p className="text-sm text-gray-400">
            {loadingLabel || DEFAULT_LOADING_LABEL}
          </p>
        </div>
      </div>
    );
  }

  // ─── Error ──────────────────────────────────────────────────────────────

  if (state === "error") {
    return (
      <div className="rounded-lg border border-red-900/50 bg-red-950/30 p-4">
        <p className="text-sm text-red-300">
          {errorMessage || DEFAULT_ERROR_MESSAGE}
        </p>
        {onRetry && (
          <button
            type="button"
            onClick={onRetry}
            className="mt-3 rounded bg-red-800 px-3 py-1.5 text-xs text-red-100 transition-colors hover:bg-red-700"
          >
            Reintentar
          </button>
        )}
      </div>
    );
  }

  // ─── Empty ──────────────────────────────────────────────────────────────

  if (state === "empty") {
    return (
      <div className="rounded-lg border border-gray-800 bg-gray-900/40 p-8 text-center">
        <p className="text-sm text-gray-400">
          {emptyLabel || DEFAULT_EMPTY_LABEL}
        </p>
      </div>
    );
  }

  // ─── Content ────────────────────────────────────────────────────────────

  return <>{children}</>;
}
