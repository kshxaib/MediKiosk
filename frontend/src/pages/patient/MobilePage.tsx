import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Container } from '../../components/Container'
import { NumericKeypad } from '../../components/NumericKeypad'
import { usePatientStore } from '../../stores'
import { cn } from '../../utils/cn'

const MOBILE_LENGTH = 10

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

  const isValid10Digit = inputVal.length === MOBILE_LENGTH
  const isLoading = lookupStatus === 'searching'

  // Functional updates so several rapid taps can never read a stale value and
  // silently drop digits.
  const appendDigit = (digit: string) => {
    setInputVal((prev) =>
      prev.length >= MOBILE_LENGTH ? prev : (prev + digit).replace(/\D/g, ''),
    )
    setValidationError(null)
  }

  const backspace = () => {
    setInputVal((prev) => prev.slice(0, -1))
    setValidationError(null)
  }

  const clearAll = () => {
    setInputVal('')
    setValidationError(null)
  }

  const handleLookup = async () => {
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

  // Ten fixed slots so the number stays readable while it is being entered and
  // the display never reflows as digits are added.
  const slots = Array.from({ length: MOBILE_LENGTH }, (_, i) => inputVal[i] ?? null)

  return (
    <Container className="py-8 max-w-xl mx-auto">
      <div className="text-center mb-6">
        <span className="inline-block rounded-full bg-blue-100 px-3 py-1 text-xs font-semibold uppercase tracking-wider text-blue-700 mb-2">
          Step 1: Identification
        </span>
        <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-slate-900">
          Patient Mobile Identification
        </h1>
        <p className="mt-1 text-base text-slate-500">
          Tap your 10-digit mobile number on the keypad below.
        </p>
      </div>

      <div className="rounded-2xl border border-slate-200 bg-white p-5 sm:p-6 shadow-sm">
        {(validationError || lookupError) && (
          <div className="mb-5 rounded-xl border-2 border-red-200 bg-red-50 p-4 text-base font-semibold text-red-700 flex items-center justify-between gap-3">
            <span>{validationError || lookupError}</span>
            <button
              onClick={() => setValidationError(null)}
              aria-label="Dismiss message"
              className="shrink-0 rounded-lg px-3 py-1 text-lg font-bold text-red-500 active:bg-red-100 cursor-pointer touch-manipulation"
            >
              ✕
            </button>
          </div>
        )}

        {/* Number display */}
        <div className="mb-5">
          <div className="flex items-center justify-between px-1 mb-2">
            <label className="text-xs font-bold uppercase tracking-wider text-slate-600">
              Mobile Number
            </label>
            <span
              className={cn(
                'font-mono text-sm font-bold',
                isValid10Digit ? 'text-emerald-600' : 'text-slate-400',
              )}
            >
              {inputVal.length} / {MOBILE_LENGTH}
            </span>
          </div>

          <div className="flex items-center gap-2 rounded-2xl border-2 border-slate-200 bg-slate-50 px-3 py-4 sm:px-4">
            <span className="select-none font-mono text-2xl font-bold text-slate-500">
              +91
            </span>
            <div className="flex flex-1 items-end justify-between gap-0.5">
              {slots.map((digit, i) => (
                <span
                  key={i}
                  className={cn(
                    'flex-1 text-center font-mono text-3xl font-black tabular-nums',
                    digit ? 'text-slate-900' : 'text-slate-300',
                  )}
                >
                  {digit ?? '·'}
                </span>
              ))}
            </div>
          </div>
          <p className="mt-2 px-1 text-sm text-slate-400">
            Must be a valid 10-digit Indian mobile number
          </p>
        </div>

        {/* On-screen keypad — the kiosk has no physical keyboard */}
        <NumericKeypad
          value={inputVal}
          onAppend={appendDigit}
          onBackspace={backspace}
          onClear={clearAll}
          maxLength={MOBILE_LENGTH}
          disabled={isLoading}
          className="mb-5"
        />

        <button
          type="button"
          onClick={handleLookup}
          disabled={!isValid10Digit || isLoading}
          className={cn(
            'flex w-full touch-manipulation items-center justify-center gap-3 rounded-2xl',
            'bg-blue-600 py-6 text-xl font-bold text-white shadow-md transition',
            'active:scale-[0.99] disabled:cursor-not-allowed disabled:opacity-40 cursor-pointer',
          )}
        >
          {isLoading ? (
            <>
              <span className="inline-block h-6 w-6 animate-spin rounded-full border-3 border-white border-t-transparent" />
              <span>Searching Patient Record...</span>
            </>
          ) : (
            <span>Continue →</span>
          )}
        </button>

        {/* Result: Patient Found */}
        {lookupStatus === 'found' && currentPatient && (
          <div className="mt-6 rounded-2xl border-2 border-emerald-200 bg-emerald-50 p-5">
            <div className="flex items-center justify-between gap-3">
              <div className="flex items-center space-x-2">
                <span className="inline-flex h-7 w-7 items-center justify-center rounded-full bg-emerald-600 text-white text-sm font-bold">
                  ✓
                </span>
                <h3 className="text-lg font-bold text-emerald-900">Patient Found</h3>
              </div>
              <button
                onClick={handleReset}
                className="shrink-0 rounded-xl border-2 border-slate-300 px-4 py-2 text-sm font-bold text-slate-600 active:bg-slate-100 cursor-pointer touch-manipulation"
              >
                Change Number
              </button>
            </div>

            <div className="mt-3 space-y-1 text-base text-slate-700 bg-white/70 p-4 rounded-xl border border-emerald-100">
              <div>Name: <span className="font-bold text-slate-900">{currentPatient.full_name}</span></div>
              <div>Patient Code: <span className="font-mono font-bold text-slate-900">{currentPatient.patient_code}</span></div>
              {currentPatient.age && (
                <div>Age: {currentPatient.age} yrs {currentPatient.gender && `• ${currentPatient.gender}`}</div>
              )}
            </div>

            <button
              onClick={handleProceedToVerification}
              className="mt-4 w-full touch-manipulation rounded-2xl bg-emerald-600 py-5 text-lg font-bold text-white shadow-md transition active:scale-[0.99] cursor-pointer"
            >
              Proceed to Face Verification →
            </button>
          </div>
        )}

        {/* Result: Patient Not Found */}
        {lookupStatus === 'not_found' && (
          <div className="mt-6 rounded-2xl border-2 border-blue-200 bg-blue-50 p-5 text-center">
            <h3 className="text-lg font-bold text-blue-900">No Patient Record Found</h3>
            <p className="mt-1 text-base text-blue-700">
              Mobile number <span className="font-mono font-bold">+91 {inputVal}</span> is not
              registered in our hospital system yet.
            </p>

            <button
              onClick={handleGoToRegistration}
              className="mt-4 w-full touch-manipulation rounded-2xl bg-blue-600 py-5 text-lg font-bold text-white shadow-md transition active:scale-[0.99] cursor-pointer"
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
