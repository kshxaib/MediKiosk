import React, { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { usePatientStore } from '../../stores'
import { Container } from '../../components/Container'

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

  const videoRef = useRef<HTMLVideoElement | null>(null)
  const canvasRef = useRef<HTMLCanvasElement | null>(null)
  const [cameraStream, setCameraStream] = useState<MediaStream | null>(null)
  const [cameraError, setCameraError] = useState<string | null>(null)
  const [isCapturing, setIsCapturing] = useState(false)

  // Reset face state whenever we enter this page so a fresh capture is always required
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
            setCameraError('Camera permission was denied. Please allow camera access in your browser settings and refresh this page.')
          } else if (err.name === 'NotFoundError' || err.name === 'DevicesNotFoundError') {
            setCameraError('No webcam device found on this system. Please connect a camera and refresh.')
          } else {
            setCameraError(`Could not initialize camera: ${err.message}`)
          }
        } else {
          setCameraError('Failed to access camera. Please ensure no other application is using it.')
        }
      }
    }

    startCamera()

    return () => {
      if (stream) {
        stream.getTracks().forEach((track) => track.stop())
      }
    }
  }, [currentPatient, navigate])

  const captureFrame = (): string | null => {
    const video = videoRef.current
    const canvas = canvasRef.current
    if (!video || !canvas) return null

    // Ensure video is actually playing and has valid dimensions before capture
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
      // Store sets faceStatus to 'error' / 'failed' and faceMessage accordingly
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
          Step 3: Biometric {isEnrollmentFlow ? 'Face Enrollment' : 'Face Verification'}
        </span>
        <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-slate-900">
          {isEnrollmentFlow ? 'Enroll Your Face Biometric' : 'Verify Your Identity'}
        </h1>
        {currentPatient && (
          <p className="mt-1 text-sm text-slate-500">
            Patient: <span className="font-semibold text-slate-800">{currentPatient.full_name}</span>{' '}
            (<span className="font-mono text-slate-700">{currentPatient.patient_code}</span>)
          </p>
        )}
      </div>

      <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm text-center">

        {/* Camera error before processing */}
        {cameraError && faceStatus === 'idle' && !isProcessing && (
          <div className="rounded-xl border border-red-200 bg-red-50 p-5 mb-4 text-left">
            <div className="flex items-start gap-3">
              <span className="text-2xl">📷</span>
              <div>
                <h3 className="font-bold text-red-900">Camera Unavailable</h3>
                <p className="mt-1 text-sm text-red-700">{cameraError}</p>
              </div>
            </div>
          </div>
        )}

        {/* Camera preview - always visible while capturing */}
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

            {/* Face Oval Alignment Guide */}
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

            {/* Processing overlay */}
            {isProcessing && (
              <div className="absolute inset-0 bg-slate-900/75 backdrop-blur-xs flex flex-col items-center justify-center text-white p-4 rounded-2xl">
                <div className="h-10 w-10 animate-spin rounded-full border-4 border-blue-400 border-t-transparent mb-3" />
                <div className="font-semibold text-sm text-center">
                  {faceMessage ?? (isEnrollmentFlow ? 'Detecting face & extracting biometric embedding...' : 'Running ArcFace biometric comparison...')}
                </div>
                <div className="mt-1 text-xs text-slate-400">This may take up to 20 seconds</div>
              </div>
            )}
          </div>
        )}

        {/* Idle guide prompt */}
        {faceStatus === 'idle' && !isProcessing && !cameraError && (
          <p className="text-sm text-slate-600 mb-4">
            {isEnrollmentFlow
              ? 'Position your face within the oval guide, then click Capture.'
              : 'Position your face within the oval guide to verify your identity.'}
          </p>
        )}

        {/* === RESULT STATES === */}

        {faceStatus === 'verified' && (
          <div className="rounded-xl border-2 border-emerald-300 bg-emerald-50 p-5 mb-4 text-left">
            <div className="flex items-start gap-3">
              <span className="text-3xl">✅</span>
              <div>
                <h3 className="font-bold text-lg text-emerald-800">Identity Verified</h3>
                <p className="mt-1 text-sm text-emerald-700">
                  {faceMessage ?? 'Face matched successfully. Identity confirmed via ArcFace biometric comparison.'}
                </p>
              </div>
            </div>
          </div>
        )}

        {faceStatus === 'enrolled' && (
          <div className="rounded-xl border-2 border-emerald-300 bg-emerald-50 p-5 mb-4 text-left">
            <div className="flex items-start gap-3">
              <span className="text-3xl">✅</span>
              <div>
                <h3 className="font-bold text-lg text-emerald-800">Face Biometric Enrolled</h3>
                <p className="mt-1 text-sm text-emerald-700">
                  {faceMessage ?? 'Your face embedding has been stored. Use face verification at future check-ins.'}
                </p>
              </div>
            </div>
          </div>
        )}

        {faceStatus === 'failed' && (
          <div className="rounded-xl border-2 border-red-300 bg-red-50 p-5 mb-4 text-left">
            <div className="flex items-start gap-3">
              <span className="text-3xl">❌</span>
              <div>
                <h3 className="font-bold text-lg text-red-800">Face Not Matched — Verification Failed</h3>
                <p className="mt-1 text-sm text-red-700">
                  {faceMessage ?? 'The face does not match the registered patient. Please try again.'}
                </p>
                <p className="mt-2 text-xs text-red-600 font-medium">
                  Tip: Ensure good lighting, look directly into the camera, and keep your face within the oval guide.
                </p>
              </div>
            </div>
          </div>
        )}

        {faceStatus === 'error' && (
          <div className="rounded-xl border-2 border-amber-300 bg-amber-50 p-5 mb-4 text-left">
            <div className="flex items-start gap-3">
              <span className="text-3xl">⚠️</span>
              <div>
                <h3 className="font-bold text-lg text-amber-800">
                  {faceMessage?.includes('No face detected') ? 'No Face Detected' : 'Verification Error'}
                </h3>
                <p className="mt-1 text-sm text-amber-700">
                  {faceMessage ?? 'A technical error occurred. Please try again.'}
                </p>
                {faceMessage?.includes('No face detected') && (
                  <p className="mt-2 text-xs text-amber-800 font-semibold">
                    Please position your face clearly within the oval guide with good lighting.
                  </p>
                )}
              </div>
            </div>
          </div>
        )}

        {/* === ACTION CONTROLS === */}
        <div className="flex flex-col sm:flex-row gap-3 justify-center">

          {faceStatus === 'idle' && !isCapturing && (
            <button
              id="capture-btn"
              onClick={handleCaptureAndProcess}
              disabled={!cameraStream || isProcessing}
              className="w-full rounded-xl bg-blue-600 py-3.5 text-base font-bold text-white shadow-sm hover:bg-blue-500 transition disabled:opacity-40 disabled:cursor-not-allowed"
            >
              {isEnrollmentFlow ? '📸 Capture & Enroll Biometric Face' : '📸 Capture & Verify Identity'}
            </button>
          )}

          {(faceStatus === 'failed' || faceStatus === 'error') && (
            <button
              id="retry-btn"
              onClick={handleRetry}
              className="w-full rounded-xl bg-slate-700 py-3.5 text-base font-bold text-white hover:bg-slate-600 transition"
            >
              🔄 Retry Capture
            </button>
          )}

          {(faceStatus === 'verified' || faceStatus === 'enrolled') && (
            <button
              id="done-btn"
              onClick={() => navigate('/patient/mobile')}
              className="w-full rounded-xl bg-emerald-700 py-3.5 text-base font-bold text-white hover:bg-emerald-600 transition"
            >
              ✓ Finish & Return to Start
            </button>
          )}
        </div>
      </div>
    </Container>
  )
}
