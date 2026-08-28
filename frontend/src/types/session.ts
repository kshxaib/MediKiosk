export interface LanguageOption {
  code: string
  name: string
  native_name: string
  is_default: boolean
  is_active: boolean
}

export interface MedicalStream {
  id: string
  name: string
  code: string
  description?: string | null
  is_active: boolean
  created_at: string
}

export interface Department {
  id: string
  hospital_id: string
  name: string
  code: string
  description?: string | null
  stream_code?: string | null
  is_active: boolean
  created_at: string
}

export interface ConsentRecord {
  id: string
  session_id: string
  patient_id: string
  consent_type: string
  consent_text: string
  language: string
  is_granted: boolean
  consented_at?: string | null
  withdrawn_at?: string | null
  created_at: string
}

export interface IntakeSession {
  id: string
  patient_id: string
  hospital_id: string
  medical_stream_id?: string | null
  department_id?: string | null
  language: string
  status: string
  started_at?: string | null
  completed_at?: string | null
  created_at: string
  updated_at: string
  patient?: {
    id: string
    patient_code: string
    full_name: string
  } | null
  medical_stream?: MedicalStream | null
  department?: Department | null
  consents?: ConsentRecord[]
}

export interface SessionCreatePayload {
  patient_id: string
  hospital_id?: string | null
  medical_stream_id?: string | null
  department_id?: string | null
  language?: string
}

export interface SessionUpdatePayload {
  medical_stream_id?: string | null
  department_id?: string | null
  language?: string | null
  status?: string | null
}

export interface ConsentSubmitPayload {
  patient_id: string
  consent_type: string
  consent_text: string
  language: string
  is_granted: boolean
}
