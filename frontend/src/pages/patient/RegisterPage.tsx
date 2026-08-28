import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Container } from '../../components/Container'
import { usePatientStore } from '../../stores'

export const RegisterPage: React.FC = () => {
  const navigate = useNavigate()
  const { enteredMobile, registerPatient, registrationStatus, registrationError } = usePatientStore()

  const [fullName, setFullName] = useState('')
  const [dateOfBirth, setDateOfBirth] = useState('')
  const [age, setAge] = useState<string>('')
  const [gender, setGender] = useState<string>('OTHER')
  const [email, setEmail] = useState('')
  const [validationError, setValidationError] = useState<string | null>(null)

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault()
    setValidationError(null)

    if (!fullName.trim()) {
      setValidationError('Full Name is required.')
      return
    }
    if (!enteredMobile) {
      setValidationError('Mobile number is missing. Please go back to the mobile lookup step.')
      return
    }

    try {
      await registerPatient({
        full_name: fullName.trim(),
        mobile_number: enteredMobile,
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
          <div className="mb-4 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
            {validationError || registrationError}
          </div>
        )}

        <form onSubmit={handleRegister} className="space-y-4">
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1">
              Mobile Number
            </label>
            <input
              type="text"
              disabled
              value={`+91 ${enteredMobile}`}
              className="w-full rounded-xl border border-slate-200 bg-slate-100 px-4 py-2.5 font-mono font-bold text-slate-600 text-sm cursor-not-allowed"
            />
          </div>

          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1">
              Full Name *
            </label>
            <input
              type="text"
              required
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              placeholder="e.g. Rohan Sharma"
              className="w-full rounded-xl border border-slate-300 px-4 py-2.5 text-slate-900 focus:border-blue-600 focus:outline-hidden text-sm"
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
                value={age}
                onChange={(e) => setAge(e.target.value)}
                placeholder="e.g. 35"
                className="w-full rounded-xl border border-slate-300 px-4 py-2.5 text-slate-900 focus:border-blue-600 focus:outline-hidden text-sm"
              />
            </div>

            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1">
                Date of Birth
              </label>
              <input
                type="date"
                value={dateOfBirth}
                onChange={(e) => setDateOfBirth(e.target.value)}
                className="w-full rounded-xl border border-slate-300 px-4 py-2.5 text-slate-900 focus:border-blue-600 focus:outline-hidden text-sm"
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
                  onClick={() => setGender(g)}
                  className={`rounded-xl border py-2.5 text-xs font-bold transition cursor-pointer ${
                    gender === g
                      ? 'border-blue-600 bg-blue-50 text-blue-700 ring-2 ring-blue-500/20'
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
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="patient@example.com"
              className="w-full rounded-xl border border-slate-300 px-4 py-2.5 text-slate-900 focus:border-blue-600 focus:outline-hidden text-sm"
            />
          </div>

          <div className="pt-2">
            <button
              type="submit"
              disabled={registrationStatus === 'submitting'}
              className="w-full rounded-xl bg-blue-600 py-3.5 text-base font-bold text-white shadow-sm hover:bg-blue-500 transition disabled:opacity-40 cursor-pointer"
            >
              {registrationStatus === 'submitting'
                ? 'Creating Patient Profile...'
                : 'Create Profile & Proceed to Biometrics →'}
            </button>
          </div>
        </form>
      </div>
    </Container>
  )
}
