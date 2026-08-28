import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { usePatientStore } from '../../stores'
import { Container } from '../../components/Container'

export const RegisterPage: React.FC = () => {
  const navigate = useNavigate()
  const { enteredMobile, registerPatient, registrationStatus, registrationError } = usePatientStore()

  const [fullName, setFullName] = useState('')
  const [mobile, setMobile] = useState(enteredMobile)
  const [age, setAge] = useState<string>('')
  const [dob, setDob] = useState<string>('')
  const [gender, setGender] = useState<string>('OTHER')
  const [language, setLanguage] = useState<string>('en')
  const [email, setEmail] = useState<string>('')
  const [localError, setLocalError] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLocalError(null)

    if (fullName.trim().length < 2) {
      setLocalError('Please enter a valid full name (at least 2 characters).')
      return
    }

    if (mobile.replace(/\D/g, '').length < 10) {
      setLocalError('Please enter a valid 10-digit mobile number.')
      return
    }

    try {
      await registerPatient({
        full_name: fullName.trim(),
        mobile_number: mobile.replace(/\D/g, ''),
        age: age ? parseInt(age, 10) : undefined,
        date_of_birth: dob || undefined,
        gender: gender || undefined,
        primary_language: language,
        email: email.trim() || undefined,
      })
      navigate('/patient/face')
    } catch {
      // Handled in store
    }
  }

  return (
    <Container className="py-8 max-w-xl mx-auto">
      <div className="text-center mb-6">
        <span className="inline-block rounded-full bg-blue-100 px-3 py-1 text-xs font-semibold uppercase tracking-wider text-blue-700 mb-2">
          Step 2: New Patient Registration
        </span>
        <h1 className="text-3xl font-bold tracking-tight text-slate-900">
          Patient Registration
        </h1>
        <p className="mt-1 text-sm text-slate-500">
          Please enter basic details to create your digital hospital record.
        </p>
      </div>

      <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        {(localError || registrationError) && (
          <div className="mb-4 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
            {localError || registrationError}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-semibold text-slate-700">
              Full Name <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              required
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              placeholder="e.g. Ramesh Kumar"
              className="mt-1 w-full rounded-xl border border-slate-300 px-4 py-2.5 text-base text-slate-900 focus:border-blue-600 focus:outline-hidden"
            />
          </div>

          <div>
            <label className="block text-sm font-semibold text-slate-700">
              Mobile Number <span className="text-red-500">*</span>
            </label>
            <input
              type="tel"
              required
              maxLength={10}
              value={mobile}
              onChange={(e) => setMobile(e.target.value.replace(/\D/g, ''))}
              placeholder="10-digit mobile"
              className="mt-1 w-full rounded-xl border border-slate-300 px-4 py-2.5 text-base font-mono text-slate-900 focus:border-blue-600 focus:outline-hidden"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-sm font-semibold text-slate-700">Age (Years)</label>
              <input
                type="number"
                min={0}
                max={125}
                value={age}
                onChange={(e) => setAge(e.target.value)}
                placeholder="e.g. 35"
                className="mt-1 w-full rounded-xl border border-slate-300 px-4 py-2.5 text-base text-slate-900 focus:border-blue-600 focus:outline-hidden"
              />
            </div>
            <div>
              <label className="block text-sm font-semibold text-slate-700">Date of Birth</label>
              <input
                type="date"
                value={dob}
                onChange={(e) => setDob(e.target.value)}
                className="mt-1 w-full rounded-xl border border-slate-300 px-4 py-2.5 text-base text-slate-900 focus:border-blue-600 focus:outline-hidden"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-sm font-semibold text-slate-700">Gender</label>
              <select
                value={gender}
                onChange={(e) => setGender(e.target.value)}
                className="mt-1 w-full rounded-xl border border-slate-300 px-4 py-2.5 text-base text-slate-900 focus:border-blue-600 focus:outline-hidden bg-white"
              >
                <option value="MALE">Male</option>
                <option value="FEMALE">Female</option>
                <option value="OTHER">Other</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-semibold text-slate-700">Primary Language</label>
              <select
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                className="mt-1 w-full rounded-xl border border-slate-300 px-4 py-2.5 text-base text-slate-900 focus:border-blue-600 focus:outline-hidden bg-white"
              >
                <option value="en">English</option>
                <option value="hi">Hindi (हिंदी)</option>
                <option value="bn">Bengali (বাংলা)</option>
                <option value="ta">Tamil (தமிழ்)</option>
                <option value="te">Telugu (తెలుగు)</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-semibold text-slate-700">Email Address (Optional)</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="e.g. ramesh@example.com"
              className="mt-1 w-full rounded-xl border border-slate-300 px-4 py-2.5 text-base text-slate-900 focus:border-blue-600 focus:outline-hidden"
            />
          </div>

          <button
            type="submit"
            disabled={registrationStatus === 'submitting'}
            className="w-full mt-4 rounded-xl bg-blue-600 py-3.5 text-base font-bold text-white shadow-sm hover:bg-blue-500 transition disabled:opacity-50"
          >
            {registrationStatus === 'submitting'
              ? 'Creating Record...'
              : 'Save & Continue to Face Enrollment →'}
          </button>
        </form>
      </div>
    </Container>
  )
}
