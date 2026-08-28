import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { usePatientStore } from '../../stores'
import { Container } from '../../components/Container'

export const MobilePage: React.FC = () => {
  const navigate = useNavigate()
  const {
    enteredMobile,
    setEnteredMobile,
    lookupByMobile,
    lookupStatus,
    lookupError,
    currentPatient,
    setIsEnrollmentFlow,
    resetFlow,
    resetFaceState,
  } = usePatientStore()

  const [inputVal, setInputVal] = useState(enteredMobile)

  const handleKeyPress = (num: string) => {
    if (inputVal.length < 10) {
      const next = inputVal + num
      setInputVal(next)
      setEnteredMobile(next)
    }
  }

  const handleBackspace = () => {
    const next = inputVal.slice(0, -1)
    setInputVal(next)
    setEnteredMobile(next)
  }

  const handleClear = () => {
    setInputVal('')
    setEnteredMobile('')
    resetFlow()
  }

  const handleLookup = async (e?: React.FormEvent) => {
    if (e) e.preventDefault()
    if (inputVal.length < 10) return

    setEnteredMobile(inputVal)
    try {
      await lookupByMobile(inputVal)
    } catch {
      // Handled in store state
    }
  }

  const handleProceedToVerification = () => {
    resetFaceState()
    setIsEnrollmentFlow(false)
    navigate('/patient/face')
  }

  const handleGoToRegistration = () => {
    setEnteredMobile(inputVal)
    setIsEnrollmentFlow(true)
    navigate('/patient/register')
  }

  return (
    <Container className="py-8 max-w-2xl mx-auto">
      <div className="text-center mb-6">
        <span className="inline-block rounded-full bg-blue-100 px-3 py-1 text-xs font-semibold uppercase tracking-wider text-blue-700 mb-2">
          Step 1: Patient Identification
        </span>
        <h1 className="text-3xl font-bold tracking-tight text-slate-900">
          Enter Your Mobile Number
        </h1>
        <p className="mt-1 text-sm text-slate-500">
          We use your mobile number to look up your existing health record or start registration.
        </p>
      </div>

      <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        {/* Mobile Input Display */}
        <form onSubmit={handleLookup} className="mb-6">
          <div className="relative">
            <div className="absolute inset-y-0 left-0 flex items-center pl-4 pointer-events-none text-slate-500 font-semibold text-lg">
              +91
            </div>
            <input
              type="tel"
              maxLength={10}
              value={inputVal}
              onChange={(e) => {
                const clean = e.target.value.replace(/\D/g, '').slice(0, 10)
                setInputVal(clean)
                setEnteredMobile(clean)
              }}
              placeholder="XXXXXXXXXX"
              className="w-full rounded-xl border-2 border-slate-300 pl-16 pr-4 py-3.5 text-2xl font-mono font-bold tracking-wider text-slate-900 focus:border-blue-600 focus:outline-hidden text-center"
            />
          </div>

          <div className="mt-4 flex gap-3">
            <button
              type="submit"
              disabled={inputVal.length < 10 || lookupStatus === 'searching'}
              className="flex-1 rounded-xl bg-blue-600 py-3 text-base font-bold text-white shadow-sm hover:bg-blue-500 transition disabled:opacity-40"
            >
              {lookupStatus === 'searching' ? 'Searching Records...' : 'Find Patient Record'}
            </button>
            {inputVal && (
              <button
                type="button"
                onClick={handleClear}
                className="rounded-xl border border-slate-300 px-4 py-3 text-sm font-semibold text-slate-600 hover:bg-slate-100 transition"
              >
                Clear
              </button>
            )}
          </div>
        </form>

        {/* Touchscreen Numeric Keypad */}
        <div className="grid grid-cols-3 gap-2.5 max-w-xs mx-auto mb-6">
          {['1', '2', '3', '4', '5', '6', '7', '8', '9'].map((n) => (
            <button
              key={n}
              type="button"
              onClick={() => handleKeyPress(n)}
              className="rounded-xl border border-slate-200 bg-slate-50 py-3.5 text-xl font-bold text-slate-800 hover:bg-slate-200 active:scale-95 transition"
            >
              {n}
            </button>
          ))}
          <button
            type="button"
            onClick={handleClear}
            className="rounded-xl border border-slate-200 bg-slate-100 py-3.5 text-xs font-bold text-slate-600 hover:bg-slate-200 transition"
          >
            RESET
          </button>
          <button
            type="button"
            onClick={() => handleKeyPress('0')}
            className="rounded-xl border border-slate-200 bg-slate-50 py-3.5 text-xl font-bold text-slate-800 hover:bg-slate-200 active:scale-95 transition"
          >
            0
          </button>
          <button
            type="button"
            onClick={handleBackspace}
            className="rounded-xl border border-slate-200 bg-slate-100 py-3.5 text-xs font-bold text-slate-600 hover:bg-slate-200 transition"
          >
            âŒ« BACK
          </button>
        </div>

        {/* Error Alert */}
        {lookupError && (
          <div className="mb-4 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
            {lookupError}
          </div>
        )}

        {/* Result: Patient Found */}
        {lookupStatus === 'found' && currentPatient && (
          <div className="rounded-xl border border-emerald-200 bg-emerald-50 p-5 text-center">
            <div className="inline-flex h-10 w-10 items-center justify-center rounded-full bg-emerald-100 text-emerald-600 font-bold mb-2">
              âœ“
            </div>
            <h3 className="text-lg font-bold text-emerald-900">Existing Patient Found</h3>
            <div className="mt-2 space-y-1 text-sm text-emerald-800">
              <div className="font-semibold text-base">{currentPatient.full_name}</div>
              <div>Patient Code: <span className="font-mono font-bold">{currentPatient.patient_code}</span></div>
              {currentPatient.age && <div>Age: {currentPatient.age} yrs {currentPatient.gender && `â€¢ ${currentPatient.gender}`}</div>}
            </div>

            <button
              onClick={handleProceedToVerification}
              className="mt-4 w-full rounded-xl bg-emerald-600 py-3 text-base font-bold text-white shadow-sm hover:bg-emerald-500 transition"
            >
              Proceed to Webcam Face Verification â†’
            </button>
          </div>
        )}

        {/* Result: Patient Not Found */}
        {lookupStatus === 'not_found' && (
          <div className="rounded-xl border border-blue-200 bg-blue-50 p-5 text-center">
            <h3 className="text-lg font-bold text-blue-900">No Patient Record Found</h3>
            <p className="mt-1 text-sm text-blue-700">
              Mobile number <span className="font-mono font-bold">+91 {inputVal}</span> is not yet registered.
            </p>

            <button
              onClick={handleGoToRegistration}
              className="mt-4 w-full rounded-xl bg-blue-600 py-3 text-base font-bold text-white shadow-sm hover:bg-blue-500 transition"
            >
              Register as New Patient â†’
            </button>
          </div>
        )}
      </div>
    </Container>
  )
}

