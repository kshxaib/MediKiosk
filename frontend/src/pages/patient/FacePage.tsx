import React, { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Container } from '../../components/Container'
import { usePatientStore, useSessionStore } from '../../stores'
import { useTranslation } from '../../utils/i18n'

export const FacePage: React.FC = () => {
  const navigate = useNavigate()
  const {
    currentPatient,
    isEnrollmentFlow,
    enrollFace,
    verifyFace,
    faceStatus,
    faceMessage,
    resetFaceState,
  } = usePatientStore()

  const { selectedLanguage } = useSessionStore()
  const t = useTranslation(selectedLanguage)

  const videoRef = useRef<HTMLVideoElement | null>(null)
  const canvasRef = useRef<HTMLCanvasElement | null>(null)
  const [cameraStream, setCameraStream] = useState<MediaStream | null>(null)
  const [cameraError, setCameraError] = useState<string | null>(null)
  const [isCapturing, setIsCapturing] = useState(false)

  useEffect(() => {
    resetFaceState()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  useEffect(() => {
    if (!currentPatient) {
      navigate('/patient/mobile')
      return
    }

    let stream: MediaStream | null = null

    async function startCamera() {
      setCameraError(null)
      try {
        stream = await navigator.mediaDevices.getUserMedia({
          video: { width: { ideal: 640 }, height: { ideal: 480 }, facingMode: 'user' },
          audio: false,
        })
        setCameraStream(stream)
        if (videoRef.current) {
          videoRef.current.srcObject = stream
        }
      } catch (err: unknown) {
        if (err instanceof Error) {
          if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
            setCameraError(t.cameraUnavailable)
          } else if (err.name === 'NotFoundError' || err.name === 'DevicesNotFoundError') {
            setCameraError('No webcam device found on this system.')
          } else {
            setCameraError(`Could not initialize camera: ${err.message}`)
          }
        } else {
          setCameraError('Failed to access camera.')
        }
      }
    }

    startCamera()

    return () => {
      if (stream) {
        stream.getTracks().forEach((track) => track.stop())
      }
    }
  }, [currentPatient, navigate, t.cameraUnavailable])

  const captureFrame = (): string | null => {
    const video = videoRef.current
    const canvas = canvasRef.current
    if (!video || !canvas) return null

    if (video.readyState < 2 || video.videoWidth === 0 || video.videoHeight === 0) {
      setCameraError('Camera is not ready yet. Please wait a moment and try again.')
      return null
    }

    canvas.width = video.videoWidth
    canvas.height = video.videoHeight
    const ctx = canvas.getContext('2d')
    if (!ctx) return null
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height)
    return canvas.toDataURL('image/jpeg', 0.9)
  }

  const handleCaptureAndProcess = async () => {
    if (isCapturing || faceStatus === 'processing') return
    setCameraError(null)

    const frameB64 = captureFrame()
    if (!frameB64) return

    setIsCapturing(true)
    try {
      if (isEnrollmentFlow) {
        await enrollFace(frameB64)
      } else {
        await verifyFace(frameB64)
      }
    } catch {
      // Handled in store
    } finally {
      setIsCapturing(false)
    }
  }

  const handleRetry = () => {
    resetFaceState()
    setCameraError(null)
  }

  const isProcessing = faceStatus === 'processing' || isCapturing

  return (
    <Container className="py-8 max-w-xl mx-auto">
      <div className="text-center mb-4">
        <span className="inline-block rounded-full bg-blue-100 px-3 py-1 text-xs font-semibold uppercase tracking-wider text-blue-700 mb-2">
          {t.stepFace}
        </span>
        <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-slate-900">
          {isEnrollmentFlow ? t.faceEnrollTitle : t.faceVerifyTitle}
        </h1>
        {currentPatient && (
          <p className="mt-1 text-sm text-slate-500">
            {t.patient}: <span className="font-semibold text-slate-800">{currentPatient.full_name}</span>{' '}
            (<span className="font-mono text-slate-700">{currentPatient.patient_code}</span>)
          </p>
        )}
      </div>

      <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm text-center">
        {cameraError && faceStatus === 'idle' && !isProcessing && (
          <div className="rounded-xl border border-red-200 bg-red-50 p-5 mb-4 text-left">
            <div className="flex items-start gap-3">
              <span className="text-2xl">📷</span>
              <div>
                <h3 className="font-bold text-red-900">Camera Error</h3>
                <p className="mt-1 text-sm text-red-700">{cameraError}</p>
              </div>
            </div>
          </div>
        )}

        {!cameraError && (
          <div className="relative mx-auto max-w-sm rounded-2xl overflow-hidden border-4 border-slate-800 bg-slate-900 shadow-inner mb-4">
            <video
              ref={videoRef}
              autoPlay
              playsInline
              muted
              className="w-full h-64 sm:h-72 object-cover"
              style={{ transform: 'scaleX(-1)' }}
            />
            <canvas ref={canvasRef} className="hidden" />

            <div className="absolute inset-0 pointer-events-none flex items-center justify-center">
              <div
                className={`w-44 h-56 rounded-[50%] border-2 border-dashed transition-all duration-300 ${
                  faceStatus === 'verified' || faceStatus === 'enrolled'
                    ? 'border-emerald-400 bg-emerald-500/10'
                    : faceStatus === 'failed' || faceStatus === 'error'
                    ? 'border-red-400 bg-red-500/10'
                    : isProcessing
                    ? 'border-yellow-400 bg-yellow-500/10'
                    : 'border-blue-400 bg-blue-500/5'
                }`}
              />
            </div>

            {isProcessing && (
              <div className="absolute inset-0 bg-slate-900/75 backdrop-blur-xs flex flex-col items-center justify-center text-white p-4 rounded-2xl">
                <div className="h-10 w-10 animate-spin rounded-full border-4 border-blue-400 border-t-transparent mb-3" />
                <div className="font-semibold text-sm text-center">
                  {faceMessage ?? (isEnrollmentFlow ? t.faceProcessingEnroll : t.faceProcessingVerify)}
                </div>
                <div className="mt-1 text-xs text-slate-400">This may take up to 20 seconds</div>
              </div>
            )}
          </div>
        )}

        {faceStatus === 'idle' && !isProcessing && !cameraError && (
          <p className="text-sm text-slate-600 mb-4">
            {t.faceOvalPrompt}
          </p>
        )}

        {/* VERIFIED */}
        {faceStatus === 'verified' && (
          <div className="rounded-xl border-2 border-emerald-300 bg-emerald-50 p-5 mb-4 text-left">
            <div className="flex items-start gap-3">
              <span className="text-3xl">✅</span>
              <div>
                <h3 className="font-bold text-lg text-emerald-800">{t.faceVerifiedTitle}</h3>
                <p className="mt-1 text-sm text-emerald-700">
                  {faceMessage ?? t.faceVerifiedDesc}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* ENROLLED */}
        {faceStatus === 'enrolled' && (
          <div className="rounded-xl border-2 border-emerald-300 bg-emerald-50 p-5 mb-4 text-left">
            <div className="flex items-start gap-3">
              <span className="text-3xl">✅</span>
              <div>
                <h3 className="font-bold text-lg text-emerald-800">{t.faceEnrolledTitle}</h3>
                <p className="mt-1 text-sm text-emerald-700">
                  {faceMessage ?? t.faceEnrolledDesc}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* FAILED */}
        {faceStatus === 'failed' && (
          <div className="rounded-xl border-2 border-red-300 bg-red-50 p-5 mb-4 text-left">
            <div className="flex items-start gap-3">
              <span className="text-3xl">❌</span>
              <div>
                <h3 className="font-bold text-lg text-red-800">{t.faceFailedTitle}</h3>
                <p className="mt-1 text-sm text-red-700">
                  {faceMessage ?? t.faceFailedDesc}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* ERROR */}
        {faceStatus === 'error' && (
          <div className="rounded-xl border-2 border-amber-300 bg-amber-50 p-5 mb-4 text-left">
            <div className="flex items-start gap-3">
              <span className="text-3xl">⚠️</span>
              <div>
                <h3 className="font-bold text-lg text-amber-800">{t.faceErrorTitle}</h3>
                <p className="mt-1 text-sm text-amber-700">
                  {faceMessage ?? 'A technical error occurred.'}
                </p>
                {faceMessage?.includes('No face detected') && (
                  <p className="mt-2 text-xs text-amber-800 font-semibold">
                    {t.faceNoFaceDetected}
                  </p>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Action Controls */}
        <div className="flex flex-col sm:flex-row gap-3 justify-center">
          {faceStatus === 'idle' && !isCapturing && (
            <button
              id="capture-btn"
              onClick={handleCaptureAndProcess}
              disabled={!cameraStream || isProcessing}
              className="w-full rounded-xl bg-blue-600 py-3.5 text-base font-bold text-white shadow-sm hover:bg-blue-500 transition disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer"
            >
              {isEnrollmentFlow ? t.faceCaptureEnrollBtn : t.faceCaptureVerifyBtn}
            </button>
          )}

          {(faceStatus === 'failed' || faceStatus === 'error') && (
            <button
              id="retry-btn"
              onClick={handleRetry}
              className="w-full rounded-xl bg-slate-700 py-3.5 text-base font-bold text-white hover:bg-slate-600 transition cursor-pointer"
            >
              🔄 {t.retry}
            </button>
          )}

          {(faceStatus === 'verified' || faceStatus === 'enrolled') && (
            <button
              id="proceed-consent-btn"
              onClick={() => navigate('/patient/consent')}
              className="w-full rounded-xl bg-blue-600 py-3.5 text-base font-bold text-white shadow-md hover:bg-blue-500 transition active:scale-98 cursor-pointer"
            >
              {t.proceedToConsentBtn}
            </button>
          )}
        </div>
      </div>
    </Container>
  )
}