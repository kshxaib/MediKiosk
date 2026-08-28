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
            Start Patient Check-In / Register &rarr;
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
            <div className="h-10 w-10 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center font-bold text-xl mb-3">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z" />
              </svg>
            </div>
            <h3 className="font-bold text-slate-900">Mobile Identifier</h3>
            <p className="mt-1 text-xs text-slate-500 leading-relaxed">
              Instant patient lookup with 10-digit mobile number or easy on-kiosk registration.
            </p>
          </div>

          <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-xs">
            <div className="h-10 w-10 rounded-lg bg-emerald-50 text-emerald-600 flex items-center justify-center font-bold text-xl mb-3">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5.121 17.804A13.937 13.937 0 0112 16c2.5 0 4.847.655 6.879 1.804M15 10a3 3 0 11-6 0 3 3 0 016 0zm6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h3 className="font-bold text-slate-900">ArcFace Biometrics</h3>
            <p className="mt-1 text-xs text-slate-500 leading-relaxed">
              Deep learning facial recognition via InsightFace with real-time live webcam verification.
            </p>
          </div>

          <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-xs">
            <div className="h-10 w-10 rounded-lg bg-purple-50 text-purple-600 flex items-center justify-center font-bold text-xl mb-3">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
            </div>
            <h3 className="font-bold text-slate-900">Hospital Grade Security</h3>
            <p className="mt-1 text-xs text-slate-500 leading-relaxed">
              Strict RBAC separation, token authentication, and privacy-preserving biometric storage.
            </p>
          </div>
        </div>
      </div>
    </Container>
  )
}

export default HomePage
