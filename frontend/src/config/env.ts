/**
 * Typed access to browser-exposed environment variables.
 * Only VITE_-prefixed values exist here; backend secrets must never be added.
 */
const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

export const env = {
  apiBaseUrl,
} as const
