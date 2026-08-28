import { env } from '../config/env'

interface RequestOptions {
  method?: string
  signal?: AbortSignal
}

/**
 * Minimal fetch wrapper for the MediKiosk API. Centralizes the base URL and
 * error handling so feature services stay small. Expanded in later phases
 * (auth headers, interceptors) — kept intentionally simple for Phase 1.
 */
export async function apiRequest<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const url = `${env.apiBaseUrl}${path}`

  let response: Response
  try {
    response = await fetch(url, {
      method: options.method ?? 'GET',
      headers: { Accept: 'application/json' },
      signal: options.signal,
    })
  } catch {
    throw new Error('Network request failed')
  }

  if (!response.ok) {
    throw new Error(`Request failed with status ${response.status}`)
  }

  return (await response.json()) as T
}
