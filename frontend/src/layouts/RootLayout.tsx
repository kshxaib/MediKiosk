import React from 'react'
import { NavLink, Outlet, useLocation } from 'react-router-dom'
import { useAuthStore } from '../stores'

/** Route prefixes that run in kiosk mode (patient-facing touchscreen). */
const KIOSK_PATH_PREFIX = '/patient/'

export const RootLayout: React.FC = () => {
  const { user, isAuthenticated } = useAuthStore()
  const { pathname } = useLocation()

  // Route-aware chrome: while a patient is inside the intake flow the kiosk must
  // not offer ways to wander off into staff/system pages. Staff and admin routes
  // keep the full navigation. Handled here rather than per page so every current
  // and future /patient/* route inherits it automatically.
  const isKioskRoute = pathname.startsWith(KIOSK_PATH_PREFIX)

  return (
    <div className="flex min-h-screen flex-col bg-slate-50 text-slate-900 antialiased">
      <header className="sticky top-0 z-30 border-b border-slate-200 bg-white/80 backdrop-blur-sm">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3 sm:px-6">
          <div className="flex items-center gap-6">
            {isKioskRoute ? (
              // Brand only, and deliberately not a link: tapping it mid-intake
              // would abandon the patient's session.
              <div className="flex items-center gap-2 select-none">
                <span className="h-7 w-7 rounded-lg bg-blue-600 font-black text-white flex items-center justify-center text-sm shadow-xs">
                  M
                </span>
                <span className="font-black text-lg text-slate-900 tracking-tight">MediKiosk</span>
              </div>
            ) : (
              <>
                <NavLink to="/" className="flex items-center gap-2">
                  <span className="h-7 w-7 rounded-lg bg-blue-600 font-black text-white flex items-center justify-center text-sm shadow-xs">
                    M
                  </span>
                  <span className="font-black text-lg text-slate-900 tracking-tight">MediKiosk</span>
                </NavLink>
                <nav className="flex items-center gap-1">
                  <NavLink
                    to="/"
                    className={({ isActive }) =>
                      `rounded-md px-3 py-1.5 text-sm font-medium transition ${
                        isActive ? 'bg-slate-100 text-slate-900' : 'text-slate-600 hover:text-slate-900'
                      }`
                    }
                  >
                    Home
                  </NavLink>
                  <NavLink
                    to="/patient/mobile"
                    className={({ isActive }) =>
                      `rounded-md px-3 py-1.5 text-sm font-semibold transition ${
                        isActive ? 'bg-blue-100 text-blue-800' : 'text-blue-600 hover:bg-blue-50'
                      }`
                    }
                  >
                    Patient Check-In
                  </NavLink>
                  <NavLink
                    to="/system"
                    className={({ isActive }) =>
                      `rounded-md px-3 py-1.5 text-sm font-medium transition ${
                        isActive ? 'bg-slate-100 text-slate-900' : 'text-slate-600 hover:text-slate-900'
                      }`
                    }
                  >
                    System Status
                  </NavLink>
                </nav>
              </>
            )}
          </div>

          {!isKioskRoute && (
            <div className="flex items-center gap-3">
              <NavLink
                to="/login"
                className={({ isActive }) =>
                  `rounded-lg px-3 py-1.5 text-sm font-semibold transition ${
                    isActive
                      ? 'bg-blue-50 text-blue-700'
                      : 'text-slate-700 hover:bg-slate-100'
                  }`
                }
              >
                {isAuthenticated && user ? (
                  <span className="flex items-center gap-2">
                    <span>{user.full_name}</span>
                    <span className="rounded bg-blue-100 px-1.5 py-0.5 text-xs text-blue-800">
                      {user.role.name}
                    </span>
                  </span>
                ) : (
                  'Staff Login'
                )}
              </NavLink>
            </div>
          )}
        </div>
      </header>

      <main className="flex-1">
        <Outlet />
      </main>

      <footer className="border-t border-slate-200 bg-white py-4 text-center text-xs text-slate-500">
        MediKiosk Intelligent Healthcare Intake &copy; 2026
      </footer>
    </div>
  )
}
