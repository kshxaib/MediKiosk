import { useCallback, useEffect, useState } from 'react'

import { getHealth, getPublicConfig } from '../services/systemService'
import type { HealthResponse, PublicConfig } from '../types/api'

interface SystemHealthState {
  health: HealthResponse | null
  config: PublicConfig | null
  loading: boolean
  error: string | null
  refresh: () => void
}

export function useSystemHealth(): SystemHealthState {
  const [health, setHealth] = useState<HealthResponse | null>(null)
  const [config, setConfig] = useState<PublicConfig | null>(null)
  const [loading, setLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>(null)
  const [reloadToken, setReloadToken] = useState<number>(0)

  useEffect(() => {
    let cancelled = false

    // State is set only from async continuations (never synchronously in the
    // effect body) and guarded so a late response cannot update an unmounted
    // component or clobber a newer request.
    Promise.all([getHealth(), getPublicConfig()])
      .then(([healthResult, configResult]) => {
        if (cancelled) return
        setHealth(healthResult)
        setConfig(configResult)
        setError(null)
      })
      .catch((err: unknown) => {
        if (cancelled) return
        setError(err instanceof Error ? err.message : 'Unknown error')
        setHealth(null)
        setConfig(null)
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })

    return () => {
      cancelled = true
    }
  }, [reloadToken])

  const refresh = useCallback(() => {
    setLoading(true)
    setError(null)
    setReloadToken((token) => token + 1)
  }, [])

  return { health, config, loading, error, refresh }
}
