import { cn } from '../utils/cn'

interface StatusBadgeProps {
  ok: boolean
  children: React.ReactNode
}

export function StatusBadge({ ok, children }: StatusBadgeProps) {
  return (
    <span
      className={cn(
        'inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-medium',
        ok ? 'bg-teal-50 text-teal-700' : 'bg-red-50 text-red-700',
      )}
    >
      <span className={cn('h-1.5 w-1.5 rounded-full', ok ? 'bg-teal-500' : 'bg-red-500')} />
      {children}
    </span>
  )
}
