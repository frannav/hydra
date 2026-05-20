/**
 * DataBadge — renders a small badge for risk_level, confidence, or any
 * categorical data value.
 *
 * Tolerates unknown values gracefully — falls back to a neutral appearance
 * when the value doesn't match a known category.
 */

interface DataBadgeProps {
  /** The value to display */
  value: string | null | undefined;
  /** Badge type: "risk" for risk_level, "confidence" for confidence, or "default" */
  type?: "risk" | "confidence" | "default";
  /** Optional label prefix shown before the value */
  label?: string;
}

/**
 * Map risk level values to Tailwind color classes.
 */
const RISK_COLORS: Record<string, string> = {
  alto: "bg-red-900/60 text-red-200 border-red-800/60",
  medio: "bg-yellow-900/60 text-yellow-200 border-yellow-800/60",
  bajo: "bg-green-900/60 text-green-200 border-green-800/60",
  alto_riesgo: "bg-red-900/60 text-red-200 border-red-800/60",
  medio_riesgo: "bg-yellow-900/60 text-yellow-200 border-yellow-800/60",
  bajo_riesgo: "bg-green-900/60 text-green-200 border-green-800/60",
};

/**
 * Map confidence values to Tailwind color classes.
 */
const CONFIDENCE_COLORS: Record<string, string> = {
  alta: "bg-green-900/60 text-green-200 border-green-800/60",
  media: "bg-yellow-900/60 text-yellow-200 border-yellow-800/60",
  baja: "bg-red-900/60 text-red-200 border-red-800/60",
  alta_confianza: "bg-green-900/60 text-green-200 border-green-800/60",
  media_confianza: "bg-yellow-900/60 text-yellow-200 border-yellow-800/60",
  baja_confianza: "bg-red-900/60 text-red-200 border-red-800/60",
};

/**
 * Get color classes for a badge value based on its type.
 * Returns the neutral fallback for unknown values.
 */
function getBadgeClasses(
  value: string | null | undefined,
  type: "risk" | "confidence" | "default",
): string {
  const neutral =
    "bg-gray-800/60 text-gray-300 border-gray-700/60";

  if (!value || typeof value !== "string" || !value.trim()) {
    return neutral;
  }

  const normalized = value.trim().toLowerCase();

  if (type === "risk") {
    return RISK_COLORS[normalized] ?? neutral;
  }

  if (type === "confidence") {
    return CONFIDENCE_COLORS[normalized] ?? neutral;
  }

  return neutral;
}

export default function DataBadge({
  value,
  type = "default",
  label,
}: DataBadgeProps) {
  const displayValue =
    !value || typeof value !== "string" || !value.trim()
      ? "Desconocido"
      : value.trim();

  const classes = getBadgeClasses(value, type);

  return (
    <span
      className={`inline-flex items-center rounded border px-2 py-0.5 text-xs font-medium ${classes}`}
    >
      {label && (
        <span className="mr-1 text-gray-400">{label}</span>
      )}
      {displayValue}
    </span>
  );
}
