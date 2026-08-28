import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Container } from '../../components/Container'
import { usePatientStore, useSessionStore } from '../../stores'
import { useTranslation } from '../../utils/i18n'

export const InterviewReadyPage: React.FC = () => {
  const navigate = useNavigate()
  const { currentPatient, resetFlow } = usePatientStore()
  const {
    currentSession,
    selectedStream,
    selectedDepartment,
    selectedLanguage,
    startSession,
    resetSession,
  } = useSessionStore()

  const t = useTranslation(selectedLanguage)

  const [isStarting, setIsStarting] = useState(false)
  const [started, setStarted] = useState(false)

  useEffect(() => {
    if (!currentPatient || !currentSession) {
      navigate('/patient/mobile')
    }
  }, [currentPatient, currentSession, navigate])

  const handleStartInterview = async () => {
    if (!currentSession) return
    setIsStarting(true)
    try {
      await startSession(currentSession.id)
      setStarted(true)
      navigate('/patient/interview')
    } catch {
      // Handled in store
    } finally {
      setIsStarting(false)
    }
  }

  const handleFinish = () => {
    resetSession()
    resetFlow()
    navigate('/')
  }

  return (
    <Container className="py-10 max-w-xl mx-auto">
      <div className="text-center mb-6">
        <span className="inline-block rounded-full bg-emerald-100 px-3.5 py-1 text-xs font-bold uppercase tracking-wider text-emerald-800 mb-2">
          {t.stepReady}
        </span>
        <h1 className="text-3xl font-black tracking-tight text-slate-900">
          {t.readyTitle}
        </h1>
        <p className="mt-1 text-sm text-slate-500">
          {t.readySubtitle}
        </p>
      </div>

      <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm space-y-4">
        <div className="flex items-center justify-between border-b border-slate-100 pb-3">
          <span className="text-sm text-slate-500">{t.patient}</span>
          <span className="font-bold text-slate-900">
            {currentPatient?.full_name} ({currentPatient?.patient_code})
          </span>
        </div>

        <div className="flex items-center justify-between border-b border-slate-100 pb-3">
          <span className="text-sm text-slate-500">भाषा / Language</span>
          <span className="font-semibold text-slate-800 uppercase">
            {selectedLanguage === 'hi' ? 'हिन्दी (Hindi)' : 'English (en)'}
          </span>
        </div>

        <div className="flex items-center justify-between border-b border-slate-100 pb-3">
          <span className="text-sm text-slate-500">{t.selectedStreamLabel}</span>
          <span className="font-semibold text-slate-800">
            {selectedStream?.name || currentSession?.medical_stream?.name || 'Modern Medicine'}
          </span>
        </div>

        <div className="flex items-center justify-between border-b border-slate-100 pb-3">
          <span className="text-sm text-slate-500">विभाग / Department</span>
          <span className="font-semibold text-slate-800">
            {selectedDepartment?.name || currentSession?.department?.name || 'General Medicine'}
          </span>
        </div>

        <div className="flex items-center justify-between border-b border-slate-100 pb-3">
          <span className="text-sm text-slate-500">{t.sessionStatus}</span>
          <span className="inline-flex items-center rounded-full bg-emerald-100 px-3 py-0.5 text-xs font-bold text-emerald-800">
            {currentSession?.status}
          </span>
        </div>

        <div className="mt-6 rounded-xl bg-blue-50 border border-blue-200 p-4 text-xs text-blue-900 leading-relaxed">
          <div className="font-bold mb-1">ℹ️ Next: Phase 5 AI Clinical Interview</div>
          {t.nextPhaseNotice}
        </div>

        <div className="mt-6 space-y-3">
          {!started ? (
            <button
              onClick={handleStartInterview}
              disabled={isStarting}
              className="w-full rounded-xl bg-blue-600 py-3.5 text-base font-bold text-white shadow-md hover:bg-blue-500 transition active:scale-98 disabled:opacity-50 cursor-pointer"
            >
              {isStarting ? t.loading : t.startInterviewBtn}
            </button>
          ) : (
            <div className="rounded-xl border border-emerald-300 bg-emerald-50 p-4 text-center text-emerald-900 font-bold text-sm">
              {t.sessionActiveStatus}
            </div>
          )}

          <button
            onClick={handleFinish}
            className="w-full rounded-xl border border-slate-300 bg-white py-3 text-sm font-semibold text-slate-700 hover:bg-slate-50 transition cursor-pointer"
          >
            {t.finish}
          </button>
        </div>
      </div>
    </Container>
  )
}