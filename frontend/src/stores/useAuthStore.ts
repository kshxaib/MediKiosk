import { create } from 'zustand'
import { apiClient, TOKEN_KEY } from '../services/apiClient'
import type { AuthResponse, LoginCredentials, User } from '../types'

export interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null
  initialize: () => Promise<void>
  login: (credentials: LoginCredentials) => Promise<void>
  logout: () => Promise<void>
  clearError: () => void
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: localStorage.getItem(TOKEN_KEY),
  isAuthenticated: false,
  isLoading: true,
  error: null,

  initialize: async () => {
    const savedToken = localStorage.getItem(TOKEN_KEY)
    if (!savedToken) {
      set({ user: null, token: null, isAuthenticated: false, isLoading: false })
      return
    }
    try {
      const { data: user } = await apiClient.get<User>('/auth/me')
      set({ user, token: savedToken, isAuthenticated: true, isLoading: false, error: null })
    } catch {
      localStorage.removeItem(TOKEN_KEY)
      set({ user: null, token: null, isAuthenticated: false, isLoading: false })
    }
  },

  login: async (credentials: LoginCredentials) => {
    set({ isLoading: true, error: null })
    try {
      const { data } = await apiClient.post<AuthResponse>('/auth/login', credentials)
      localStorage.setItem(TOKEN_KEY, data.access_token)
      set({ token: data.access_token, user: data.user, isAuthenticated: true, isLoading: false, error: null })
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Login failed'
      set({ isLoading: false, error: msg })
      throw err
    }
  },

  logout: async () => {
    try {
      await apiClient.post('/auth/logout')
    } catch {
      // ignore network failure on logout
    } finally {
      localStorage.removeItem(TOKEN_KEY)
      set({ user: null, token: null, isAuthenticated: false, isLoading: false, error: null })
    }
  },

  clearError: () => set({ error: null }),
}))

// Hydrate auth state on application load
useAuthStore.getState().initialize()
