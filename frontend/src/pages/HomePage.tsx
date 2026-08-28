import React from 'react'
import { Link } from 'react-router-dom'
import { Container } from '../components/Container'

export const HomePage: React.FC = () => {
  return (
    <Container className="py-12 sm:py-16">
      <div className="mx-auto max-w-3xl text-center">
        <span className="inline-block rounded-full bg-blue-100 px-3.5 py-1 text-xs font-bold uppercase tracking-wider text-blue-800 mb-4">
          Self-Service Intelligent Clinical Intake
        </span>
        <h1 className="text-4xl sm:text-5xl font-black tracking-tight text-slate-900 leading-tight">
          Welcome to <span className="text-blue-600">MediKiosk</span>
        </h1>
        <p className="mt-4 text-lg text-slate-600 leading-relaxed">
          Fast, accessible hospital check-in with contactless biometric facial verification,
          adaptive clinical assessment, and seamless doctor coordination.
        </p>

        <div className="mt-8 flex flex-col sm:flex-row items-center justify-center gap-4">
          <Link
            to="/patient/language"
            className="w-full sm:w-auto rounded-xl bg-blue-600 px-8 py-4 text-lg font-bold text-white shadow-md hover:bg-blue-500 transition active:scale-98"
          >
            Start Patient Check-In / Register â†’
          </Link>
          <Link
            to="/system"
            className="w-full sm:w-auto rounded-xl border border-slate-300 bg-white px-6 py-4 text-base font-semibold text-slate-700 hover:bg-slate-50 transition"
          >
            System Health & Diagnostics
          </Link>
        </div>

        <div className="mt-12 grid grid-cols-1 sm:grid-cols-3 gap-6 text-left">
          <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-xs">
            <div className="text-2xl mb-2">ðŸ“±</div>
            <h3 className="font-bold text-slate-900">Mobile Identifier</h3>
            <p className="mt-1 text-xs text-slate-500">
              Instant patient lookup with 10-digit mobile number or easy on-kiosk registration.
            </p>
          </div>
          <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-xs">
            <div className="text-2xl mb-2">ðŸ‘¤</div>
            <h3 className="font-bold text-slate-900">ArcFace Biometrics</h3>
            <p className="mt-1 text-xs text-slate-500">
              Deep learning facial recognition via InsightFace with real-time live webcam verification.
            </p>
          </div>
          <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-xs">
            <div className="text-2xl mb-2">ðŸ”’</div>
            <h3 className="font-bold text-slate-900">Hospital Grade Security</h3>
            <p className="mt-1 text-xs text-slate-500">
              Strict RBAC separation, token authentication, and privacy-preserving biometric storage.
            </p>
          </div>
        </div>
      </div>
    </Container>
  )
}

