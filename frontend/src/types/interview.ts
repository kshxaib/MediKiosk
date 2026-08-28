export interface NextQuestion {
  question_id: string | null
  question: string | null
  question_type: string | null
  required: boolean
  reason?: string | null
  category?: string | null
  options?: string[] | Record<string, unknown> | null
  sequence?: number | null
  total_questions: number
  completed_questions: number
  is_last_question: boolean
  completed: boolean
  message?: string | null
}

export interface AnswerPayload {
  patient_id?: string
  question_id?: string | null
  raw_answer?: string | null
  normalized_answer?: Record<string, unknown> | null
  answer_type: string
  source?: string
  confidence?: number | null
}

export interface AnswerSubmissionResponse {
  answer_id: string
  saved: boolean
  next_question_available: boolean
  message: string
}
