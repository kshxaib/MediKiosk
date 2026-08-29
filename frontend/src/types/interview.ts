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
  /** Backend telemetry. Not rendered in the kiosk UI. */
  llm_used?: boolean
  /** Backend telemetry: categories already collected this session. Not rendered. */
  satisfied_categories?: string[]
  /** True when this question refines information already partially known. */
  is_refinement?: boolean
}

export interface AnswerPayload {
  patient_id?: string
  question_id?: string | null
  raw_answer?: string | null
  normalized_answer?: Record<string, unknown> | null
  answer_type: string
  source?: string
  confidence?: number | null
  is_patient_corrected?: boolean
  /**
   * Text of the question being answered. Only needed when the question was
   * AI-generated and therefore has no question_id, so the backend can tell
   * which follow-up this answers and avoid repeating it.
   */
  asked_question_text?: string | null
}

export interface AnswerSubmissionResponse {
  answer_id: string
  saved: boolean
  next_question_available: boolean
  message: string
}
