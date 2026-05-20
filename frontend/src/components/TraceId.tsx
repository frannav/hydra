/**
 * TraceId — displays a trace ID or "No disponible" if absent.
 *
 * Handles null, undefined, empty strings, and very long trace IDs gracefully.
 * Long trace IDs are truncated visually with an ellipsis but the full value
 * is preserved in the title attribute for inspection.
 */

interface TraceIdProps {
  /** The trace ID string to display */
  traceId: string | null | undefined;
}

const MAX_DISPLAY_LENGTH = 32;
const NO_TRACE_LABEL = "No disponible";

export default function TraceId({ traceId }: TraceIdProps) {
  if (!traceId || typeof traceId !== "string" || !traceId.trim()) {
    return (
      <span className="text-xs text-gray-500" title={NO_TRACE_LABEL}>
        {NO_TRACE_LABEL}
      </span>
    );
  }

  const trimmed = traceId.trim();

  if (trimmed.length <= MAX_DISPLAY_LENGTH) {
    return (
      <span
        className="whitespace-nowrap font-mono text-xs text-gray-400"
        title={trimmed}
      >
        {trimmed}
      </span>
    );
  }

  // Truncate visually but preserve full value in title
  const display = trimmed.slice(0, MAX_DISPLAY_LENGTH) + "\u2026";

  return (
    <span
      className="whitespace-nowrap font-mono text-xs text-gray-400"
      title={trimmed}
    >
      {display}
    </span>
  );
}
