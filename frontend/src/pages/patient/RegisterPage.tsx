import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Container } from '../../components/Container'
import { NumericKeypad } from '../../components/NumericKeypad'
import { usePatientStore } from '../../stores'
import { cn } from '../../utils/cn'

const MOBILE_LENGTH = 10

export const RegisterPage: React.FC = () => {
  const navigate = useNavigate()
  const {
    enteredMobile,
    setEnteredMobile,
    registerPatient,
    registrationStatus,
    registrationError,
  } = usePatientStore()

  const [fullName, setFullName] = useState('')
  const [dateOfBirth, setDateOfBirth] = useState('')
  const [age, setAge] = useState<string>('')
  const [gender, setGender] = useState<string>('OTHER')
  const [email, setEmail] = useState('')
  const [validationError, setValidationError] = useState<string | null>(null)
  // Seeded from the lookup step, but editable here on the touchscreen so a
  // mistyped number can be corrected without going back.
  const [mobile, setMobile] = useState(enteredMobile || '')

  const isSubmitting = registrationStatus === 'submitting'
  const isMobileComplete = mobile.length === MOBILE_LENGTH

  // Functional updates so rapid taps can never read a stale value.
  const appendDigit = (digit: string) => {
    setMobile((prev) =>
      prev.length >= MOBILE_LENGTH ? prev : (prev + digit).replace(/\D/g, ''),
    )
    setValidationError(null)
  }

  const backspace = () => {
    setMobile((prev) => prev.slice(0, -1))
    setValidationError(null)
  }

  const clearAll = () => {
    setMobile('')
    setValidationError(null)
  }

  const handleDobChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const dob = e.target.value
    setDateOfBirth(dob)
    if (dob) {
      const birthYear = new Date(dob).getFullYear()
      const currentYear = new Date().getFullYear()
      const calculatedAge = currentYear - birthYear
      if (calculatedAge >= 0 && calculatedAge <= 130) {
        setAge(calculatedAge.toString())
      }
    }
  }

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault()
    setValidationError(null)

    if (!fullName.trim()) {
      setValidationError('Full Name is required.')
      return
    }
    if (!mobile) {
      setValidationError('Mobile number is missing. Please enter it on the keypad below.')
      return
    }
    if (!isMobileComplete) {
      setValidationError('Please enter a valid 10-digit mobile number.')
      return
    }

    // Keep the shared flow state in step with what was entered here.
    setEnteredMobile(mobile)

    try {
      await registerPatient({
        full_name: fullName.trim(),
        mobile_number: mobile,
        date_of_birth: dateOfBirth || null,
        age: age ? parseInt(age, 10) : null,
        gender: gender || 'OTHER',
        email: email.trim() || null,
        primary_language: 'en',
      })

      navigate('/patient/face')
    } catch {
      // Store sets registrationError
    }
  }

  // Ten fixed slots so the number stays readable and never reflows.
  const slots = Array.from({ length: MOBILE_LENGTH }, (_, i) => mobile[i] ?? null)

  return (
    <Container className="py-8 max-w-xl mx-auto">
      <div className="text-center mb-6">
        <span className="inline-block rounded-full bg-blue-100 px-3 py-1 text-xs font-semibold uppercase tracking-wider text-blue-700 mb-2">
          Step 2: Patient Registration
        </span>
        <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-slate-900">
          New Patient Registration
        </h1>
        <p className="mt-1 text-sm text-slate-500">
          Please fill in your basic details for your hospital profile.
        </p>
      </div>

      <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        {(validationError || registrationError) && (
          <div className="mb-4 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700 flex items-center justify-between">
            <span>{validationError || registrationError}</span>
            <button
              onClick={() => setValidationError(null)}
              className="text-red-500 hover:text-red-700 text-xs font-bold ml-2 cursor-pointer"
            >
              ✕
            </button>
          </div>
        )}

        <form onSubmit={handleRegister} className="space-y-4">
          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="text-xs font-bold uppercase tracking-wider text-slate-600">
                Mobile Number *
              </label>
              <span
                className={cn(
                  'font-mono text-sm font-bold',
                  isMobileComplete ? 'text-emerald-600' : 'text-slate-400',
                )}
              >
                {mobile.length} / {MOBILE_LENGTH}
              </span>
            </div>

            <div className="flex items-center gap-2 rounded-2xl border-2 border-slate-200 bg-slate-50 px-3 py-4 sm:px-4">
              <span className="select-none font-mono text-2xl font-bold text-slate-500">+91</span>
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

            {/* Same on-screen keypad component as the lookup step */}
            <NumericKeypad
              value={mobile}
              onAppend={appendDigit}
              onBackspace={backspace}
              onClear={clearAll}
              maxLength={MOBILE_LENGTH}
              disabled={isSubmitting}
              className="mt-3"
            />
          </div>

          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1">
              Full Name *
            </label>
            <input
              type="text"
              required
              disabled={isSubmitting}
              value={fullName}
              onChange={(e) => {
                setFullName(e.target.value)
                setValidationError(null)
              }}
              placeholder="e.g. Rohan Sharma"
              className="w-full rounded-xl border border-slate-300 px-4 py-2.5 text-slate-900 focus:border-blue-600 focus:outline-hidden text-sm disabled:bg-slate-100"
            />
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1">
                Age (Years)
              </label>
              <input
                type="number"
                min={0}
                max={130}
                disabled={isSubmitting}
                value={age}
                onChange={(e) => setAge(e.target.value)}
                placeholder="e.g. 35"
                className="w-full rounded-xl border border-slate-300 px-4 py-2.5 text-slate-900 focus:border-blue-600 focus:outline-hidden text-sm disabled:bg-slate-100"
              />
            </div>

            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1">
                Date of Birth
              </label>
              <input
                type="date"
                disabled={isSubmitting}
                value={dateOfBirth}
                onChange={handleDobChange}
                className="w-full rounded-xl border border-slate-300 px-4 py-2.5 text-slate-900 focus:border-blue-600 focus:outline-hidden text-sm disabled:bg-slate-100"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1">
              Gender
            </label>
            <div className="grid grid-cols-3 gap-2">
              {['MALE', 'FEMALE', 'OTHER'].map((g) => (
                <button
                  type="button"
                  key={g}
                  disabled={isSubmitting}
                  onClick={() => setGender(g)}
                  className={`rounded-xl border py-2.5 text-xs font-bold transition cursor-pointer disabled:opacity-50 ${
                    gender === g
                      ? 'border-blue-600 bg-blue-50 text-blue-700 ring-2 ring-blue-500/20 shadow-xs'
                      : 'border-slate-200 bg-white text-slate-700 hover:bg-slate-50'
                  }`}
                >
                  {g}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1">
              Email (Optional)
            </label>
            <input
              type="email"
              disabled={isSubmitting}
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="patient@example.com"
              className="w-full rounded-xl border border-slate-300 px-4 py-2.5 text-slate-900 focus:border-blue-600 focus:outline-hidden text-sm disabled:bg-slate-100"
            />
          </div>

          <div className="pt-2">
            <button
              type="submit"
              disabled={isSubmitting || !fullName.trim() || !isMobileComplete}
              className="w-full rounded-xl bg-blue-600 py-3.5 text-base font-bold text-white shadow-sm hover:bg-blue-500 transition disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer flex items-center justify-center gap-2"
            >
              {isSubmitting ? (
                <>
                  <span className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent inline-block" />
                  <span>Creating Patient Profile...</span>
                </>
              ) : (
                <span>Create Profile & Proceed to Biometrics →</span>
              )}
            </button>
          </div>
        </form>
      </div>
    </Container>
  )
}

export default RegisterPage
