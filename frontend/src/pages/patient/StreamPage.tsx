import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Container } from '../../components/Container'
import { usePatientStore, useSessionStore } from '../../stores'
import type { MedicalStream } from '../../types'

export const StreamPage: React.FC = () => {
  const navigate = useNavigate()
  const { currentPatient } = usePatientStore()
  const {
    currentSession,
    availableStreams,
    fetchStreams,
    setStream,
    updateSession,
    loading,
    error: sessionError,
  } = useSessionStore()

  const [submittingStreamId, setSubmittingStreamId] = useState<string | null>(null)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)

  useEffect(() => {
    if (!currentPatient) {
      navigate('/patient/mobile')
      return
    }
    fetchStreams()
  }, [currentPatient, navigate, fetchStreams])

  const handleSelectStream = async (stream: MedicalStream) => {
    if (!currentSession || submittingStreamId) return
    setErrorMessage(null)
    setSubmittingStreamId(stream.id)

    try {
      setStream(stream)
      await updateSession(currentSession.id, {
        medical_stream_id: stream.id,
      })
      navigate('/patient/department')
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to select medical stream'
      setErrorMessage(msg)
    } finally {
      setSubmittingStreamId(null)
    }
  }

  return (
    <Container className="py-8 max-w-2xl mx-auto">
      <div className="text-center mb-6">
        <span className="inline-block rounded-full bg-blue-100 px-3.5 py-1 text-xs font-bold uppercase tracking-wider text-blue-800 mb-2">
          Step 5: Medical System
        </span>
        <h1 className="text-2xl sm:text-3xl font-black tracking-tight text-slate-900">
          Select Medical Stream
        </h1>
        <p className="mt-1 text-sm text-slate-500">
          Choose whether you would like an allopathic (Modern Medicine) or traditional Ayurvedic consultation.
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

      {loading && availableStreams.length === 0 ? (
        <div className="flex flex-col items-center justify-center h-48 space-y-3">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-blue-600 border-t-transparent" />
          <div className="text-sm font-bold text-slate-500">Loading available medical streams...</div>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {availableStreams.map((stream) => {
            const isModern = stream.code === 'MODERN_MEDICINE'
            const isSelected = submittingStreamId === stream.id

            return (
              <button
                key={stream.id}
                onClick={() => handleSelectStream(stream)}
                disabled={Boolean(submittingStreamId)}
                className={`flex flex-col items-start p-6 rounded-2xl border-2 transition text-left cursor-pointer group relative ${
                  isSelected
                    ? 'border-blue-600 bg-blue-50/50 shadow-md ring-2 ring-blue-500/20'
                    : 'border-slate-200 bg-white hover:border-blue-500 hover:shadow-md'
                }`}
              >
                <div className="flex items-center justify-between w-full mb-3">
                  <span className="text-3xl">{isModern ? '🩺' : '🌿'}</span>
                  <span className="rounded-full bg-slate-100 group-hover:bg-blue-100 text-slate-700 group-hover:text-blue-700 px-3 py-1 text-xs font-bold">
                    {stream.code}
                  </span>
                </div>
                <h3 className="text-xl font-bold text-slate-900 group-hover:text-blue-600 transition">
                  {stream.name}
                </h3>
                <p className="mt-2 text-xs text-slate-500 leading-relaxed">
                  {stream.description ||
                    (isModern
                      ? 'Standard MBBS clinical history, symptoms, duration, and organ-system examination.'
                      : 'Holistic Ayurvedic assessment including Prakriti, Agni, and Dosha analysis.')}
                </p>
                <div className="mt-6 font-bold text-xs text-blue-600 flex items-center gap-1.5 group-hover:translate-x-1 transition-transform">
                  {isSelected ? (
                    <>
                      <span className="h-3.5 w-3.5 animate-spin rounded-full border-2 border-blue-600 border-t-transparent inline-block" />
                      <span>Saving selection...</span>
                    </>
                  ) : (
                    <span>Select {stream.name} →</span>
                  )}
                </div>
              </button>
            )
          })}
        </div>
      )}
    </Container>
  )
}

export default StreamPage
