import React from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuthStore } from '../stores'

export const Navbar: React.FC = () => {
  const navigate = useNavigate()
  const { user, isAuthenticated, logout } = useAuthStore()

  const handleLogout = () => {
    logout()
    navigate('/')
  }

  return (
    <header className="sticky top-0 z-40 border-b border-slate-200 bg-white/95 backdrop-blur-xs">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3 sm:px-6">
        <Link to="/" className="flex items-center gap-2.5">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-blue-600 text-white font-black text-lg shadow-xs">
            M
          </div>
          <div className="flex flex-col">
            <span className="text-lg font-black tracking-tight text-slate-900 leading-tight">
              Medi<span className="text-blue-600">Kiosk</span>
            </span>
            <span className="text-[10px] font-semibold uppercase tracking-wider text-slate-600">
              Clinical Intake System
            </span>
          </div>
        </Link>

        <nav className="flex items-center gap-3">
          <Link
            to="/patient/language"
            className="rounded-lg bg-blue-50 px-3.5 py-1.5 text-xs font-bold text-blue-700 hover:bg-blue-100 transition"
          >
            Patient Kiosk
          </Link>
          <Link
            to="/system"
            className="hidden sm:inline-block rounded-lg px-3 py-1.5 text-xs font-semibold text-slate-600 hover:bg-slate-100 transition"
          >
            System Status
          </Link>

          {isAuthenticated && user ? (
            <div className="flex items-center gap-2 pl-2 border-l border-slate-200">
              <span className="text-xs font-medium text-slate-700">
                {user.full_name} ({user.role?.name || 'Staff'})
              </span>
              <button
                onClick={handleLogout}
                className="rounded-lg border border-slate-300 px-2.5 py-1 text-xs font-semibold text-slate-600 hover:bg-slate-50 transition cursor-pointer"
              >
                Logout
              </button>
            </div>
          ) : (
            <Link
              to="/login"
              className="rounded-lg border border-slate-300 px-3 py-1.5 text-xs font-semibold text-slate-700 hover:bg-slate-50 transition"
            >
              Staff Login
            </Link>
          )}
        </nav>
      </div>
    </header>
  )
}

export default Navbar
