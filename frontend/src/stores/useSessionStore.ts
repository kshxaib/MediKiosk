import { create } from 'zustand'
import { apiClient } from '../services/apiClient'
import type {
  AnswerPayload,
  AnswerSubmissionResponse,
  ConsentRecord,
  ConsentSubmitPayload,
  Department,
  IntakeSession,
  LanguageOption,
  MedicalStream,
  NextQuestion,
  SessionCreatePayload,
  SessionUpdatePayload,
} from '../types'

export interface SessionState {
  currentSession: IntakeSession | null
  selectedLanguage: string
  selectedStream: MedicalStream | null
  selectedDepartment: Department | null
  availableLanguages: LanguageOption[]
  availableStreams: MedicalStream[]
  availableDepartments: Department[]
  consents: ConsentRecord[]
  currentQuestion: NextQuestion | null
  interviewCompleted: boolean
  loading: boolean
  error: string | null

  // Actions
  fetchLanguages: () => Promise<LanguageOption[]>
  setLanguage: (language: string) => void
  fetchStreams: () => Promise<MedicalStream[]>
  fetchDepartments: (streamCode?: string) => Promise<Department[]>
  createSession: (payload: SessionCreatePayload) => Promise<IntakeSession>
  fetchSession: (sessionId: string) => Promise<IntakeSession>
  updateSession: (sessionId: string, payload: SessionUpdatePayload) => Promise<IntakeSession>
  submitConsent: (sessionId: string, payload: ConsentSubmitPayload) => Promise<ConsentRecord>
  setStream: (stream: MedicalStream | null) => void
  setDepartment: (department: Department | null) => void
  startSession: (sessionId: string) => Promise<IntakeSession>
  completeSession: (sessionId: string) => Promise<IntakeSession>
  clearSession: (sessionId: string) => Promise<IntakeSession>
  fetchNextQuestion: (sessionId: string) => Promise<NextQuestion>
  submitAnswer: (sessionId: string, payload: AnswerPayload) => Promise<AnswerSubmissionResponse>
  resetSession: () => void
}

export const useSessionStore = create<SessionState>((set) => ({
  currentSession: null,
  selectedLanguage: 'en',
  selectedStream: null,
  selectedDepartment: null,
  availableLanguages: [],
  availableStreams: [],
  availableDepartments: [],
  consents: [],
  currentQuestion: null,
  interviewCompleted: false,
  loading: false,
  error: null,

  fetchLanguages: async () => {
    try {
      const { data } = await apiClient.get<LanguageOption[]>('/languages')
      set({ availableLanguages: data })
      return data
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to fetch languages'
      set({ error: msg })
      return []
    }
  },

  setLanguage: (selectedLanguage: string) => {
    set({ selectedLanguage })
  },

  fetchStreams: async () => {
    set({ loading: true, error: null })
    try {
      const { data } = await apiClient.get<MedicalStream[]>('/streams')
      set({ availableStreams: data, loading: false })
      return data
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to fetch medical streams'
      set({ error: msg, loading: false })
      return []
    }
  },

  fetchDepartments: async (streamCode?: string) => {
    set({ loading: true, error: null })
    try {
      const url = streamCode
        ? `/departments?stream_code=${encodeURIComponent(streamCode)}`
        : '/departments'
      const { data } = await apiClient.get<Department[]>(url)
      set({ availableDepartments: data, loading: false })
      return data
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to fetch departments'
      set({ error: msg, loading: false })
      return []
    }
  },

  createSession: async (payload: SessionCreatePayload) => {
    set({ loading: true, error: null })
    try {
      const { data } = await apiClient.post<IntakeSession>('/sessions', payload)
      set({ currentSession: data, loading: false, error: null })
      return data
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to create intake session'
      set({ error: msg, loading: false })
      throw err
    }
  },

  fetchSession: async (sessionId: string) => {
    set({ loading: true, error: null })
    try {
      const { data } = await apiClient.get<IntakeSession>(`/sessions/${sessionId}`)
      set({ currentSession: data, loading: false })
      return data
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to fetch session'
      set({ error: msg, loading: false })
      throw err
    }
  },

  updateSession: async (sessionId: string, payload: SessionUpdatePayload) => {
    set({ loading: true, error: null })
    try {
      const { data } = await apiClient.patch<IntakeSession>(`/sessions/${sessionId}`, payload)
      set({ currentSession: data, loading: false })
      return data
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to update session'
      set({ error: msg, loading: false })
      throw err
    }
  },

  submitConsent: async (sessionId: string, payload: ConsentSubmitPayload) => {
    set({ loading: true, error: null })
    try {
      const { data } = await apiClient.post<ConsentRecord>(`/sessions/${sessionId}/consent`, payload)
      const { data: updatedSession } = await apiClient.get<IntakeSession>(`/sessions/${sessionId}`)
      set((state) => ({
        consents: [data, ...state.consents],
        currentSession: updatedSession,
        loading: false,
      }))
      return data
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to submit consent'
      set({ error: msg, loading: false })
      throw err
    }
  },

  setStream: (selectedStream: MedicalStream | null) => {
    set({ selectedStream })
  },

  setDepartment: (selectedDepartment: Department | null) => {
    set({ selectedDepartment })
  },

  startSession: async (sessionId: string) => {
    set({ loading: true, error: null })
    try {
      const { data } = await apiClient.post<IntakeSession>(`/sessions/${sessionId}/start`)
      set({ currentSession: data, loading: false })
      return data
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to start session'
      set({ error: msg, loading: false })
      throw err
    }
  },

  completeSession: async (sessionId: string) => {
    set({ loading: true, error: null })
    try {
      const { data } = await apiClient.post<IntakeSession>(`/sessions/${sessionId}/complete`)
      set({ currentSession: data, loading: false })
      return data
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to complete session'
      set({ error: msg, loading: false })
      throw err
    }
  },

  clearSession: async (sessionId: string) => {
    set({ loading: true, error: null })
    try {
      const { data } = await apiClient.post<IntakeSession>(`/sessions/${sessionId}/clear`)
      set({ currentSession: data, loading: false })
      return data
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to clear session'
      set({ error: msg, loading: false })
      throw err
    }
  },

  fetchNextQuestion: async (sessionId: string) => {
    set({ loading: true, error: null })
    try {
      const { data } = await apiClient.post<NextQuestion>(`/sessions/${sessionId}/ai/next-question`)
      set({
        currentQuestion: data,
        interviewCompleted: data.completed,
        loading: false,
      })
      return data
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to get next question'
      set({ error: msg, loading: false })
      throw err
    }
  },

  submitAnswer: async (sessionId: string, payload: AnswerPayload) => {
    set({ loading: true, error: null })
    try {
      const { data } = await apiClient.post<AnswerSubmissionResponse>(
        `/sessions/${sessionId}/ai/answer`,
        payload,
      )
      set({ loading: false })
      return data
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to submit answer'
      set({ error: msg, loading: false })
      throw err
    }
  },

  resetSession: () => {
    set({
      currentSession: null,
      selectedStream: null,
      selectedDepartment: null,
      consents: [],
      currentQuestion: null,
      interviewCompleted: false,
      loading: false,
      error: null,
    })
  },
}))
