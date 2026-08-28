import React from 'react'
import { NavLink, Outlet } from 'react-router-dom'
import { useAuthStore } from '../stores'

export const RootLayout: React.FC = () => {
  const { user, isAuthenticated } = useAuthStore()

  return (
    <div className="flex min-h-screen flex-col bg-slate-50 text-slate-900 antialiased">
      <header className="sticky top-0 z-30 border-b border-slate-200 bg-white/80 backdrop-blur-sm">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3 sm:px-6">
          <div className="flex items-center gap-6">
            <NavLink to="/" className="flex items-center gap-2">
              <span className="h-6 w-6 rounded-md bg-blue-600 font-bold text-white flex items-center justify-center text-xs">
                M
              </span>
              <span className="font-bold text-slate-900 tracking-tight">MediKiosk</span>
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
          </div>

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
        </div>
      </header>

      <main className="flex-1">
        <Outlet />
      </main>

      <footer className="border-t border-slate-200 bg-white py-4 text-center text-xs text-slate-500">
        MediKiosk Staff Portal &copy; 2026
      </footer>
    </div>
  )
}
