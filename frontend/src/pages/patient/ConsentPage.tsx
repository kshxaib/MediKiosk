import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Container } from '../../components/Container'
import { usePatientStore, useSessionStore } from '../../stores'
import { useTranslation } from '../../utils/i18n'

export const ConsentPage: React.FC = () => {
  const navigate = useNavigate()
  const { currentPatient } = usePatientStore()
  const {
    currentSession,
    selectedLanguage,
    createSession,
    submitConsent,
    loading,
    error: sessionError,
  } = useSessionStore()

  const t = useTranslation(selectedLanguage)

  const [hasDeclined, setHasDeclined] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)

  useEffect(() => {
    if (!currentPatient) {
      navigate('/patient/mobile')
    }
  }, [currentPatient, navigate])

  const handleGrantConsent = async () => {
    if (!currentPatient || submitting) return
    setErrorMessage(null)
    setSubmitting(true)

    try {
      let session = currentSession
      if (!session) {
        session = await createSession({
          patient_id: currentPatient.id,
          language: selectedLanguage || 'en',
        })
      }

      await submitConsent(session.id, {
        patient_id: currentPatient.id,
        consent_type: 'CLINICAL_INTAKE',
        consent_text: t.consentStatement,
        language: selectedLanguage || 'en',
        is_granted: true,
      })

      navigate('/patient/stream')
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to record consent'
      setErrorMessage(msg)
    } finally {
      setSubmitting(false)
    }
  }

  const handleDeclineConsent = async () => {
    if (!currentPatient || submitting) return
    setErrorMessage(null)
    setSubmitting(true)

    try {
      let session = currentSession
      if (!session) {
        session = await createSession({
          patient_id: currentPatient.id,
          language: selectedLanguage || 'en',
        })
      }

      await submitConsent(session.id, {
        patient_id: currentPatient.id,
        consent_type: 'CLINICAL_INTAKE',
        consent_text: 'Declined clinical intake consent.',
        language: selectedLanguage || 'en',
        is_granted: false,
      })

      setHasDeclined(true)
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to process consent decline'
      setErrorMessage(msg)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <Container className="py-8 max-w-2xl mx-auto">
      <div className="text-center mb-6">
        <span className="inline-block rounded-full bg-blue-100 px-3.5 py-1 text-xs font-bold uppercase tracking-wider text-blue-800 mb-2">
          {t.stepConsent}
        </span>
        <h1 className="text-2xl sm:text-3xl font-black tracking-tight text-slate-900">
          {t.consentTitle}
        </h1>
        {currentPatient && (
          <p className="mt-1 text-sm text-slate-500">
            {t.patient}: <span className="font-semibold text-slate-800">{currentPatient.full_name}</span>{' '}
            (<span className="font-mono text-slate-700">{currentPatient.patient_code}</span>)
          </p>
        )}
      </div>

      {(errorMessage || sessionError) && (
        <div className="mb-4 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          {errorMessage || sessionError}
        </div>
      )}

      {hasDeclined ? (
        <div className="rounded-2xl border border-amber-200 bg-amber-50 p-8 text-center shadow-xs">
          <div className="text-4xl mb-3">⚠️</div>
          <h2 className="text-xl font-bold text-amber-900">{t.consentDeclinedTitle}</h2>
          <p className="mt-2 text-sm text-amber-800 leading-relaxed">
            {t.consentDeclinedDesc}
          </p>
          <button
            onClick={() => navigate('/')}
            className="mt-6 rounded-xl bg-slate-900 px-6 py-3 text-sm font-bold text-white shadow-sm hover:bg-slate-800 transition cursor-pointer"
          >
            {t.returnHomeBtn}
          </button>
        </div>
      ) : (
        <div className="rounded-2xl border border-slate-200 bg-white p-6 sm:p-8 shadow-sm">
          <p className="text-sm sm:text-base text-slate-700 leading-relaxed font-medium">
            {t.consentSummary}
          </p>

          <div className="mt-5 space-y-3 rounded-xl bg-slate-50 p-4 sm:p-5 border border-slate-100">
            <div className="flex items-start gap-2.5 text-xs sm:text-sm text-slate-600">
              <span className="text-blue-600 font-bold text-base leading-none">✓</span>
              <span>{t.consentPt1}</span>
            </div>
            <div className="flex items-start gap-2.5 text-xs sm:text-sm text-slate-600">
              <span className="text-blue-600 font-bold text-base leading-none">✓</span>
              <span>{t.consentPt2}</span>
            </div>
            <div className="flex items-start gap-2.5 text-xs sm:text-sm text-slate-600">
              <span className="text-blue-600 font-bold text-base leading-none">✓</span>
              <span>{t.consentPt3}</span>
            </div>
            <div className="flex items-start gap-2.5 text-xs sm:text-sm text-slate-600">
              <span className="text-blue-600 font-bold text-base leading-none">✓</span>
              <span>{t.consentPt4}</span>
            </div>
          </div>

          <div className="mt-6 rounded-xl border border-blue-200 bg-blue-50/60 p-4 text-xs sm:text-sm text-blue-900 font-medium">
            🛡️ <span className="font-semibold">{t.consentStatement}</span>
          </div>

          <div className="mt-8 flex flex-col sm:flex-row gap-3">
            <button
              id="accept-consent-btn"
              onClick={handleGrantConsent}
              disabled={submitting || loading}
              className="flex-1 rounded-xl bg-blue-600 py-4 text-base font-bold text-white shadow-md hover:bg-blue-500 active:scale-98 transition disabled:opacity-50 cursor-pointer"
            >
              {submitting ? '...' : t.consentAgreeBtn}
            </button>
            <button
              id="decline-consent-btn"
              onClick={handleDeclineConsent}
              disabled={submitting || loading}
              className="sm:w-36 rounded-xl border border-slate-300 bg-white py-4 text-base font-semibold text-slate-700 hover:bg-slate-50 active:scale-98 transition disabled:opacity-50 cursor-pointer"
            >
              {t.consentDeclineBtn}
            </button>
          </div>
        </div>
      )}
    </Container>
  )
}