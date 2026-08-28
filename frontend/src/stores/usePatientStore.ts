import { create } from 'zustand'
import { apiClient } from '../services/apiClient'
import type {
  FaceEnrollResponse,
  FaceVerifyResponse,
  Patient,
  PatientCreatePayload,
  PatientLookupResponse,
} from '../types'

export interface PatientState {
  currentPatient: Patient | null
  enteredMobile: string
  isEnrollmentFlow: boolean
  lookupStatus: 'idle' | 'searching' | 'found' | 'not_found' | 'error'
  lookupError: string | null
  registrationStatus: 'idle' | 'submitting' | 'success' | 'error'
  registrationError: string | null
  faceStatus: 'idle' | 'processing' | 'verified' | 'enrolled' | 'failed' | 'error'
  faceMessage: string | null

  setEnteredMobile: (mobile: string) => void
  setIsEnrollmentFlow: (isEnrollment: boolean) => void
  setCurrentPatient: (patient: Patient | null) => void
  lookupByMobile: (mobile: string) => Promise<PatientLookupResponse>
  registerPatient: (payload: PatientCreatePayload) => Promise<Patient>
  enrollFace: (imageBase64: string) => Promise<FaceEnrollResponse>
  verifyFace: (imageBase64: string) => Promise<FaceVerifyResponse>
  resetFaceState: () => void
  resetFlow: () => void
}

export const usePatientStore = create<PatientState>((set, get) => ({
  currentPatient: null,
  enteredMobile: '',
  isEnrollmentFlow: false,
  lookupStatus: 'idle',
  lookupError: null,
  registrationStatus: 'idle',
  registrationError: null,
  faceStatus: 'idle',
  faceMessage: null,

  setEnteredMobile: (enteredMobile) => set({ enteredMobile }),
  setIsEnrollmentFlow: (isEnrollmentFlow) => set({ isEnrollmentFlow }),
  setCurrentPatient: (currentPatient) => set({ currentPatient }),

  lookupByMobile: async (mobile: string) => {
    set({ lookupStatus: 'searching', lookupError: null })
    try {
      const { data } = await apiClient.get<PatientLookupResponse>(`/patients/lookup?mobile=${encodeURIComponent(mobile)}`)
      if (data.found && data.patient) {
        set({
          currentPatient: data.patient,
          lookupStatus: 'found',
          isEnrollmentFlow: false,
          lookupError: null,
        })
      } else {
        set({
          currentPatient: null,
          lookupStatus: 'not_found',
          lookupError: null,
        })
      }
      return data
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Lookup failed'
      set({ lookupStatus: 'error', lookupError: msg })
      throw err
    }
  },

  registerPatient: async (payload: PatientCreatePayload) => {
    set({ registrationStatus: 'submitting', registrationError: null })
    try {
      const { data: patient } = await apiClient.post<Patient>('/patients', payload)
      set({
        currentPatient: patient,
        registrationStatus: 'success',
        isEnrollmentFlow: true,
        registrationError: null,
      })
      return patient
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Registration failed'
      set({ registrationStatus: 'error', registrationError: msg })
      throw err
    }
  },

  enrollFace: async (imageBase64: string) => {
    const patient = get().currentPatient
    if (!patient) {
      throw new Error('No patient selected for face enrollment')
    }

    set({ faceStatus: 'processing', faceMessage: 'Detecting face & extracting biometric embedding...' })
    try {
      const { data } = await apiClient.post<FaceEnrollResponse>('/identity/face/enroll', {
        patient_id: patient.id,
        image_base64: imageBase64,
      })
      set({ faceStatus: 'enrolled', faceMessage: data.message })
      return data
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Face enrollment failed'
      set({ faceStatus: 'error', faceMessage: msg })
      throw err
    }
  },

  verifyFace: async (imageBase64: string) => {
    const patient = get().currentPatient
    if (!patient) {
      throw new Error('No patient selected for face verification')
    }

    set({ faceStatus: 'processing', faceMessage: 'Running ArcFace biometric comparison...' })
    try {
      const { data } = await apiClient.post<FaceVerifyResponse>('/identity/face/verify', {
        patient_id: patient.id,
        image_base64: imageBase64,
      })

      if (data.verified) {
        set({ faceStatus: 'verified', faceMessage: data.message })
      } else {
        set({ faceStatus: 'failed', faceMessage: data.message })
      }
      return data
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Face verification failed'
      set({ faceStatus: 'error', faceMessage: msg })
      throw err
    }
  },

  resetFaceState: () => set({ faceStatus: 'idle', faceMessage: null }),

  resetFlow: () =>
    set({
      currentPatient: null,
      enteredMobile: '',
      isEnrollmentFlow: false,
      lookupStatus: 'idle',
      lookupError: null,
      registrationStatus: 'idle',
      registrationError: null,
      faceStatus: 'idle',
      faceMessage: null,
    }),
}))
