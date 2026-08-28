import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../stores'
import { Container } from '../components/Container'

export const LoginPage: React.FC = () => {
  const { login, isAuthenticated, user, logout, isLoading } = useAuthStore()
  const navigate = useNavigate()

  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setIsSubmitting(true)

    try {
      await login({ email, password })
      navigate('/system')
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message)
      } else {
        setError('Login failed. Please check your credentials.')
      }
    } finally {
      setIsSubmitting(false)
    }
  }

  if (isLoading) {
    return (
      <Container className="py-12 text-center text-slate-500">
        Checking authentication state...
      </Container>
    )
  }

  if (isAuthenticated && user) {
    return (
      <Container className="py-12">
        <div className="mx-auto max-w-md rounded-xl border border-slate-200 bg-white p-8 shadow-xs">
          <h1 className="text-xl font-bold text-slate-900">Authenticated Staff Session</h1>
          <div className="mt-4 space-y-2 rounded-lg bg-slate-50 p-4 text-sm text-slate-700">
            <div><span className="font-medium text-slate-500">Name:</span> {user.full_name}</div>
            <div><span className="font-medium text-slate-500">Email:</span> {user.email}</div>
            <div>
              <span className="font-medium text-slate-500">Role:</span>{' '}
              <span className="inline-flex rounded-full bg-blue-100 px-2.5 py-0.5 text-xs font-semibold text-blue-800">
                {user.role.name}
              </span>
            </div>
          </div>
          <button
            onClick={() => logout()}
            className="mt-6 w-full rounded-lg bg-slate-800 px-4 py-2.5 text-sm font-semibold text-white hover:bg-slate-700 transition"
          >
            Sign Out
          </button>
        </div>
      </Container>
    )
  }

  return (
    <Container className="py-12">
      <div className="mx-auto max-w-md rounded-xl border border-slate-200 bg-white p-8 shadow-xs">
        <div className="mb-6 text-center">
          <h1 className="text-2xl font-bold text-slate-900">Staff Portal Login</h1>
          <p className="mt-1 text-sm text-slate-500">
            Secure authentication for hospital administrators and attending doctors.
          </p>
        </div>

        {error && (
          <div className="mb-4 rounded-lg bg-red-50 p-3 text-sm text-red-700 border border-red-200">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-700">Email or Username</label>
            <input
              type="text"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="e.g. admin@medikiosk.local"
              className="mt-1 w-full rounded-lg border border-slate-300 px-3.5 py-2 text-sm text-slate-900 focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700">Password</label>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••••••"
              className="mt-1 w-full rounded-lg border border-slate-300 px-3.5 py-2 text-sm text-slate-900 focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
            />
          </div>

          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full rounded-lg bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white shadow-xs hover:bg-blue-500 transition disabled:opacity-50"
          >
            {isSubmitting ? 'Authenticating...' : 'Sign In'}
          </button>
        </form>

        <div className="mt-6 rounded-lg bg-slate-50 p-3 text-xs text-slate-500 space-y-1">
          <div className="font-semibold text-slate-700">Development Seed Credentials:</div>
          <div>Admin: <span className="font-mono text-slate-800">admin@medikiosk.local / AdminPassword123!</span></div>
          <div>Doctor: <span className="font-mono text-slate-800">doctor@medikiosk.local / DoctorPassword123!</span></div>
        </div>
      </div>
    </Container>
  )
}
