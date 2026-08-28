import { create } from 'zustand'
import { apiClient } from '../services/apiClient'
import type { HealthResponse, PublicConfig } from '../types'

export interface SystemState {
  health: HealthResponse | null
  config: PublicConfig | null
  isLoading: boolean
  error: string | null
  lastChecked: Date | null
  fetchAll: () => Promise<void>
}

export const useSystemStore = create<SystemState>((set) => ({
  health: null,
  config: null,
  isLoading: true,
  error: null,
  lastChecked: null,

  fetchAll: async () => {
    set({ isLoading: true, error: null })
    try {
      const [{ data: health }, { data: config }] = await Promise.all([
        apiClient.get<HealthResponse>('/health'),
        apiClient.get<PublicConfig>('/config/public'),
      ])
      set({ health, config, isLoading: false, error: null, lastChecked: new Date() })
    } catch (err: unknown) {
      set({
        isLoading: false,
        error: err instanceof Error ? err.message : 'Failed to reach backend',
        health: null,
        config: null,
      })
    }
  },
}))
