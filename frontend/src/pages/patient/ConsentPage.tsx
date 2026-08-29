import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Container } from '../../components/Container'
import { usePatientStore, useSessionStore } from '../../stores'

export const ConsentPage: React.FC = () => {
  const navigate = useNavigate()
  const { currentPatient } = usePatientStore()
  const {
    currentSession,
    createSession,
    submitConsent,
    selectedLanguage,
    loading,
    error: sessionError,
  } = useSessionStore()

  const [clinicalConsent, setClinicalConsent] = useState(false)
  const [dataConsent, setDataConsent] = useState(false)
  const [aiConsent, setAiConsent] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)

  useEffect(() => {
    if (!currentPatient) {
      navigate('/patient/mobile')
      return
    }

    if (!currentSession) {
      createSession({
        patient_id: currentPatient.id,
        language: selectedLanguage || 'en',
      }).catch((err: unknown) => {
        const msg = err instanceof Error ? err.message : 'Failed to create session'
        setErrorMessage(msg)
      })
    }
  }, [currentPatient, currentSession, selectedLanguage, createSession, navigate])

  const allConsentsGranted = clinicalConsent && dataConsent && aiConsent

  const handleGrantAll = () => {
    setClinicalConsent(true)
    setDataConsent(true)
    setAiConsent(true)
    setErrorMessage(null)
  }

  const handleSubmitConsent = async () => {
    if (!allConsentsGranted) {
      setErrorMessage('Please grant all required consents to proceed.')
      return
    }
    if (!currentSession || !currentPatient) return

    setErrorMessage(null)
    setSubmitting(true)

    try {
      await submitConsent(currentSession.id, {
        patient_id: currentPatient.id,
        consent_type: 'CLINICAL_INTAKE',
        consent_text:
          'I consent to automated clinical pre-assessment, data processing for triage, and AI-assisted history taking.',
        language: selectedLanguage || 'en',
        is_granted: true,
      })

      navigate('/patient/stream')
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to submit consent'
      setErrorMessage(msg)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <Container className="py-8 max-w-2xl mx-auto">
      <div className="text-center mb-6">
        <span className="inline-block rounded-full bg-blue-100 px-3.5 py-1 text-xs font-bold uppercase tracking-wider text-blue-800 mb-2">
          Step 4: Patient Consent
        </span>
        <h1 className="text-2xl sm:text-3xl font-black tracking-tight text-slate-900">
          Informed Patient Consent
        </h1>
        <p className="mt-1 text-sm text-slate-500">
          Please review and accept hospital policies before your AI clinical interview.
        </p>
      </div>

      {(errorMessage || sessionError) && (
        <div className="mb-4 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700 flex items-center justify-between">
          <span>{errorMessage || sessionError}</span>
          <button
            onClick={() => setErrorMessage(null)}
            className="text-red-500 hover:text-red-700 text-xs font-bold ml-2 cursor-pointer"
          >
            ✕
          </button>
        </div>
      )}

      <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm space-y-4">
        {/* Consent 1 */}
        <label className="flex items-start gap-3.5 p-4 rounded-xl border border-slate-200 hover:bg-slate-50 transition cursor-pointer">
          <input
            type="checkbox"
            checked={clinicalConsent}
            onChange={(e) => {
              setClinicalConsent(e.target.checked)
              setErrorMessage(null)
            }}
            className="mt-1 h-5 w-5 rounded-sm border-slate-300 text-blue-600 focus:ring-blue-500 cursor-pointer"
          />
          <div>
            <div className="text-sm font-bold text-slate-900">Clinical Intake & Pre-Assessment</div>
            <div className="text-xs text-slate-500 mt-0.5 leading-relaxed">
              I consent to answering health questions on this kiosk to assist hospital staff in preparing my medical chart.
            </div>
          </div>
        </label>

        {/* Consent 2 */}
        <label className="flex items-start gap-3.5 p-4 rounded-xl border border-slate-200 hover:bg-slate-50 transition cursor-pointer">
          <input
            type="checkbox"
            checked={dataConsent}
            onChange={(e) => {
              setDataConsent(e.target.checked)
              setErrorMessage(null)
            }}
            className="mt-1 h-5 w-5 rounded-sm border-slate-300 text-blue-600 focus:ring-blue-500 cursor-pointer"
          />
          <div>
            <div className="text-sm font-bold text-slate-900">Hospital Data Storage & Privacy</div>
            <div className="text-xs text-slate-500 mt-0.5 leading-relaxed">
              I consent to my medical history being securely recorded in the hospital database for my attending physician's review.
            </div>
          </div>
        </label>

        {/* Consent 3 */}
        <label className="flex items-start gap-3.5 p-4 rounded-xl border border-slate-200 hover:bg-slate-50 transition cursor-pointer">
          <input
            type="checkbox"
            checked={aiConsent}
            onChange={(e) => {
              setAiConsent(e.target.checked)
              setErrorMessage(null)
            }}
            className="mt-1 h-5 w-5 rounded-sm border-slate-300 text-blue-600 focus:ring-blue-500 cursor-pointer"
          />
          <div>
            <div className="text-sm font-bold text-slate-900">AI-Assisted Questioning Notice</div>
            <div className="text-xs text-slate-500 mt-0.5 leading-relaxed">
              I understand that the AI assistant collects clinical information only and does not provide final diagnosis or prescription.
            </div>
          </div>
        </label>

        <div className="pt-2 flex flex-col sm:flex-row items-center gap-3">
          <button
            type="button"
            onClick={handleGrantAll}
            className="w-full sm:w-auto px-4 py-2.5 rounded-xl border border-slate-300 bg-slate-50 hover:bg-slate-100 text-xs font-bold text-slate-700 transition cursor-pointer"
          >
            ✓ Select All Consents
          </button>
        </div>

        <div className="pt-4 border-t border-slate-100">
          <button
            onClick={handleSubmitConsent}
            disabled={!allConsentsGranted || submitting || loading}
            className="w-full rounded-xl bg-blue-600 py-3.5 text-base font-bold text-white shadow-md hover:bg-blue-500 transition disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer flex items-center justify-center gap-2"
          >
            {submitting ? (
              <>
                <span className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent inline-block" />
                <span>Recording Consent...</span>
              </>
            ) : (
              <span>Confirm Consent & Proceed →</span>
            )}
          </button>
        </div>
      </div>
    </Container>
  )
}

export default ConsentPage
