import { Link } from 'react-router-dom'

import { Container } from '../components/Container'

export function HomePage() {
  return (
    <Container className="py-16">
      <div className="mx-auto max-w-2xl text-center">
        <p className="text-sm font-medium uppercase tracking-wide text-teal-600">
          Phase 1 · Foundation
        </p>
        <h1 className="mt-3 text-4xl font-semibold tracking-tight text-slate-900">
          MediKiosk
        </h1>
        <p className="mt-4 text-base leading-relaxed text-slate-600">
          The platform foundation is in place. This build establishes the backend
          service, database, and frontend scaffolding. Clinical intake features
          arrive in later phases.
        </p>
        <div className="mt-8">
          <Link
            to="/system"
            className="inline-flex items-center rounded-md bg-teal-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-teal-700"
          >
            View system status
          </Link>
        </div>
      </div>
    </Container>
  )
}
