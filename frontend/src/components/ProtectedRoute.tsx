import React from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { useAuthStore } from '../stores'

interface ProtectedRouteProps {
  children: React.ReactNode
  allowedRoles?: string[]
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children, allowedRoles }) => {
  const { user, isAuthenticated, isLoading } = useAuthStore()
  const location = useLocation()

  if (isLoading) {
    return (
      <div className="flex min-h-[40vh] items-center justify-center">
        <div className="text-sm font-medium text-slate-500">Verifying session...</div>
      </div>
    )
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />
  }

  if (allowedRoles && user && !allowedRoles.includes(user.role.name)) {
    return (
      <div className="mx-auto max-w-md p-6 text-center">
        <div className="rounded-lg border border-red-200 bg-red-50 p-6 text-red-700">
          <h2 className="text-lg font-semibold">Access Denied</h2>
          <p className="mt-2 text-sm">
            Your role (<span className="font-mono font-bold">{user.role.name}</span>) does not have permission to view this page.
          </p>
        </div>
      </div>
    )
  }

  return <>{children}</>
}
