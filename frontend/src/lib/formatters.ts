/**
 * Safe formatting helpers for dates, risk levels, and confidence values.
 *
 * All functions handle null, undefined, empty string, and invalid values
 * gracefully — they never throw.
 */

/**
 * Format an ISO date string to a locale-friendly date.
 *
 * Returns "No disponible" for null, undefined, empty string, or invalid dates.
 */
export function formatDate(value: string | null | undefined): string {
  if (!value || typeof value !== "string" || !value.trim()) {
    return "No disponible";
  }

  const date = new Date(value);

  if (isNaN(date.getTime())) {
    return "No disponible";
  }

  return date.toLocaleDateString("es-ES", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

/**
 * Format a risk level value into a display string.
 *
 * Returns the value as-is (lowercased) for known values, or "Desconocido"
 * for unknown/missing values.
 */
export function formatRiskLevel(value: string | null | undefined): string {
  if (!value || typeof value !== "string" || !value.trim()) {
    return "Desconocido";
  }

  const normalized = value.trim().toLowerCase();

  // Known values are displayed as-is in lowercase
  return normalized;
}

/**
 * Format a confidence level value into a display string.
 *
 * Returns the value as-is (lowercased) for known values, or "Desconocido"
 * for unknown/missing values.
 */
export function formatConfidence(
  value: string | null | undefined,
): string {
  if (!value || typeof value !== "string" || !value.trim()) {
    return "Desconocido";
  }

  const normalized = value.trim().toLowerCase();

  return normalized;
}
