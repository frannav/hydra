/**
 * API base URL helper.
 *
 * Reads NEXT_PUBLIC_API_BASE_URL from environment, falls back to
 * http://localhost:8000 if the variable is empty or whitespace.
 * Strips any trailing slash so callers can safely append `/endpoint`.
 */

const DEFAULT_API_BASE = "http://localhost:8000";

export function getApiBaseUrl(): string {
  const raw =
    typeof process !== "undefined" && process.env
      ? process.env.NEXT_PUBLIC_API_BASE_URL
      : "";

  if (!raw || !raw.trim()) {
    return DEFAULT_API_BASE;
  }

  return raw.trim().replace(/\/+$/, "");
}
