import { cn } from '../utils/cn'

interface ContainerProps {
  className?: string
  children: React.ReactNode
}

export function Container({ className, children }: ContainerProps) {
  return <div className={cn('mx-auto w-full max-w-5xl px-4 sm:px-6', className)}>{children}</div>
}
