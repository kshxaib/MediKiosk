export interface Patient {
  id: string
  patient_code: string
  full_name: string
  date_of_birth?: string | null
  age?: number | null
  gender?: string | null
  primary_language?: string | null
  email?: string | null
  is_active: boolean
  created_at: string
}

export interface PatientCreatePayload {
  full_name: string
  mobile_number: string
  date_of_birth?: string | null
  age?: number | null
  gender?: string | null
  primary_language?: string | null
  email?: string | null
}

export interface PatientLookupResponse {
  found: boolean
  patient: Patient | null
  message: string
}

export interface FaceEnrollResponse {
  patient_id: string
  enrollment_status: string
  message: string
}

export interface FaceVerifyResponse {
  verified: boolean
  patient_id: string
  method: string
  message: string
}
