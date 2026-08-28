import { Link, Outlet, useLocation } from 'react-router-dom'

import { Container } from '../components/Container'

const NAV_ITEMS = [
  { to: '/', label: 'Home' },
  { to: '/system', label: 'System' },
]

export function RootLayout() {
  const location = useLocation()

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex flex-col">
      <header className="border-b border-slate-200 bg-white">
        <Container className="flex items-center justify-between py-4">
          <Link to="/" className="text-lg font-semibold tracking-tight text-slate-900">
            Medi<span className="text-teal-600">Kiosk</span>
          </Link>
          <nav className="flex items-center gap-1">
            {NAV_ITEMS.map((item) => {
              const isActive = location.pathname === item.to
              return (
                <Link
                  key={item.to}
                  to={item.to}
                  className={
                    'rounded-md px-3 py-1.5 text-sm font-medium transition-colors ' +
                    (isActive
                      ? 'bg-teal-50 text-teal-700'
                      : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900')
                  }
                >
                  {item.label}
                </Link>
              )
            })}
          </nav>
        </Container>
      </header>

      <main className="flex-1">
        <Outlet />
      </main>

      <footer className="border-t border-slate-200 bg-white">
        <Container className="py-4">
          <p className="text-xs text-slate-400">
            MediKiosk · Phase 1 foundation · not for clinical use
          </p>
        </Container>
      </footer>
    </div>
  )
}
