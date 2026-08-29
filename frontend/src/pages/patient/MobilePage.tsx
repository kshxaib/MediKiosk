import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Container } from '../../components/Container'
import { usePatientStore } from '../../stores'

export const MobilePage: React.FC = () => {
  const navigate = useNavigate()
  const {
    enteredMobile,
    setEnteredMobile,
    lookupByMobile,
    lookupStatus,
    lookupError,
    currentPatient,
    resetFlow,
  } = usePatientStore()

  const [inputVal, setInputVal] = useState(enteredMobile || '')
  const [validationError, setValidationError] = useState<string | null>(null)

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    // Only allow digits, max 10
    const digitsOnly = e.target.value.replace(/\D/g, '').slice(0, 10)
    setInputVal(digitsOnly)
    setValidationError(null)
  }

  const isValid10Digit = inputVal.length === 10
  const isLoading = lookupStatus === 'searching'

  const handleLookup = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!isValid10Digit) {
      setValidationError('Please enter a valid 10-digit mobile number.')
      return
    }

    setValidationError(null)
    setEnteredMobile(inputVal)

    try {
      await lookupByMobile(inputVal)
    } catch {
      // Store sets lookupError and lookupStatus to error
    }
  }

  const handleProceedToVerification = () => {
    navigate('/patient/face')
  }

  const handleGoToRegistration = () => {
    setEnteredMobile(inputVal)
    navigate('/patient/register')
  }

  const handleReset = () => {
    resetFlow()
    setInputVal('')
    setValidationError(null)
  }

  return (
    <Container className="py-8 max-w-xl mx-auto">
      <div className="text-center mb-6">
        <span className="inline-block rounded-full bg-blue-100 px-3 py-1 text-xs font-semibold uppercase tracking-wider text-blue-700 mb-2">
          Step 1: Identification
        </span>
        <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-slate-900">
          Patient Mobile Identification
        </h1>
        <p className="mt-1 text-sm text-slate-500">
          Enter your 10-digit mobile number to lookup your hospital record or register.
        </p>
      </div>

      <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        {(validationError || lookupError) && (
          <div className="mb-4 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700 flex items-center justify-between">
            <span>{validationError || lookupError}</span>
            <button
              onClick={() => setValidationError(null)}
              className="text-red-500 hover:text-red-700 text-xs font-bold ml-2 cursor-pointer"
            >
              ✕
            </button>
          </div>
        )}

        <form onSubmit={handleLookup} className="space-y-4">
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1">
              Mobile Number
            </label>
            <div className="flex">
              <span className="inline-flex items-center px-4 rounded-l-xl border border-r-0 border-slate-300 bg-slate-50 text-slate-600 font-mono font-bold text-base select-none">
                +91
              </span>
              <input
                type="tel"
                inputMode="numeric"
                pattern="[0-9]*"
                maxLength={10}
                disabled={isLoading}
                value={inputVal}
                onChange={handleInputChange}
                placeholder="Enter 10-digit mobile number"
                className="w-full rounded-r-xl border border-slate-300 px-4 py-3.5 text-slate-900 font-mono text-lg tracking-wider focus:border-blue-600 focus:outline-hidden disabled:bg-slate-100"
                autoFocus
              />
            </div>
            <div className="flex justify-between items-center mt-1.5 px-1">
              <span className="text-[11px] text-slate-400">Must be a valid 10-digit Indian mobile number</span>
              <span className={`text-[11px] font-mono font-bold ${inputVal.length === 10 ? 'text-emerald-600' : 'text-slate-400'}`}>
                {inputVal.length} / 10
              </span>
            </div>
          </div>

          <button
            type="submit"
            disabled={!isValid10Digit || isLoading}
            className="w-full rounded-xl bg-blue-600 py-3.5 text-base font-bold text-white shadow-sm hover:bg-blue-500 transition disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer flex items-center justify-center gap-2"
          >
            {isLoading ? (
              <>
                <span className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent inline-block" />
                <span>Searching Patient Record...</span>
              </>
            ) : (
              <span>Verify Mobile Number →</span>
            )}
          </button>
        </form>

        {/* Result: Patient Found */}
        {lookupStatus === 'found' && currentPatient && (
          <div className="mt-6 rounded-xl border border-emerald-200 bg-emerald-50 p-5">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <span className="inline-flex h-6 w-6 items-center justify-center rounded-full bg-emerald-600 text-white text-xs font-bold">
                  ✓
                </span>
                <h3 className="text-base font-bold text-emerald-900">Patient Found</h3>
              </div>
              <button
                onClick={handleReset}
                className="text-xs text-slate-500 hover:text-slate-800 underline cursor-pointer"
              >
                Change Number
              </button>
            </div>

            <div className="mt-3 space-y-1 text-sm text-slate-700 bg-white/70 p-3 rounded-lg border border-emerald-100">
              <div>Name: <span className="font-bold text-slate-900">{currentPatient.full_name}</span></div>
              <div>Patient Code: <span className="font-mono font-bold text-slate-900">{currentPatient.patient_code}</span></div>
              {currentPatient.age && (
                <div>Age: {currentPatient.age} yrs {currentPatient.gender && `• ${currentPatient.gender}`}</div>
              )}
            </div>

            <button
              onClick={handleProceedToVerification}
              className="mt-4 w-full rounded-xl bg-emerald-600 py-3.5 text-base font-bold text-white shadow-sm hover:bg-emerald-500 transition cursor-pointer"
            >
              Proceed to Webcam Face Verification →
            </button>
          </div>
        )}

        {/* Result: Patient Not Found */}
        {lookupStatus === 'not_found' && (
          <div className="mt-6 rounded-xl border border-blue-200 bg-blue-50 p-5 text-center">
            <h3 className="text-base font-bold text-blue-900">No Patient Record Found</h3>
            <p className="mt-1 text-sm text-blue-700">
              Mobile number <span className="font-mono font-bold">+91 {inputVal}</span> is not registered in our hospital system yet.
            </p>

            <button
              onClick={handleGoToRegistration}
              className="mt-4 w-full rounded-xl bg-blue-600 py-3.5 text-base font-bold text-white shadow-sm hover:bg-blue-500 transition cursor-pointer"
            >
              Register as New Patient →
            </button>
          </div>
        )}
      </div>
    </Container>
  )
}

export default MobilePage
