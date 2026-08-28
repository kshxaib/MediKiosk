import { Container } from '../components/Container'
import { StatusBadge } from '../components/StatusBadge'
import { useSystemHealth } from '../hooks/useSystemHealth'
import { env } from '../config/env'

export function SystemStatusPage() {
  const { health, config, loading, error, refresh } = useSystemHealth()

  return (
    <Container className="py-12">
      <div className="mx-auto max-w-2xl">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-semibold tracking-tight text-slate-900">
              System status
            </h1>
            <p className="mt-1 text-sm text-slate-500">
              Developer view of backend connectivity. Not a clinical page.
            </p>
          </div>
          <button
            type="button"
            onClick={refresh}
            className="rounded-md border border-slate-300 px-3 py-1.5 text-sm font-medium text-slate-700 transition-colors hover:bg-slate-100"
          >
            Refresh
          </button>
        </div>

        {error && (
          <div className="mt-6 rounded-md border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
            Could not reach the backend at <code>{env.apiBaseUrl}</code>. {error}
          </div>
        )}

        <dl className="mt-6 divide-y divide-slate-200 rounded-lg border border-slate-200 bg-white">
          <Row label="API health">
            {loading ? (
              <span className="text-sm text-slate-400">Checking…</span>
            ) : (
              <StatusBadge ok={health?.status === 'healthy'}>
                {health?.status ?? 'unknown'}
              </StatusBadge>
            )}
          </Row>
          <Row label="Database">
            {loading ? (
              <span className="text-sm text-slate-400">Checking…</span>
            ) : (
              <StatusBadge ok={health?.checks.database === 'ok'}>
                {health?.checks.database ?? 'unknown'}
              </StatusBadge>
            )}
          </Row>
          <Row label="Service">
            <span className="text-sm text-slate-700">{config?.app_name ?? '—'}</span>
          </Row>
          <Row label="Environment">
            <span className="text-sm text-slate-700">{config?.environment ?? '—'}</span>
          </Row>
          <Row label="API version">
            <span className="text-sm text-slate-700">{config?.api_version ?? '—'}</span>
          </Row>
        </dl>
      </div>
    </Container>
  )
}

function Row({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="flex items-center justify-between px-4 py-3">
      <dt className="text-sm font-medium text-slate-600">{label}</dt>
      <dd>{children}</dd>
    </div>
  )
}
