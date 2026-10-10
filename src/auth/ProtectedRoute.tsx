import { Navigate } from 'react-router-dom'
import { useAuth } from './AuthContext'

export function ProtectedRoute({
  children,
  allowedRoles,
}: {
  children: React.ReactNode
  allowedRoles?: string[]
}) {
  const { user, isAuthenticated, isLoading } = useAuth()
  const dashboard = user?.role === 'GOVERNMENT' || user?.role === 'ADMIN'
    ? '/government/dashboard'
    : user?.role === 'SCHOOL' || user?.role === 'HEALTHCARE'
      ? '/map'
      : '/dashboard'

  if (isLoading) {
    return <div role="status" aria-live="polite" className="flex min-h-[60vh] items-center justify-center text-sm font-medium text-slate-600">Loading your session…</div>
  }

  if (!isAuthenticated || !user) {
    return <Navigate to="/login" replace />
  }

  if (allowedRoles && !allowedRoles.includes(user.role)) {
    return <Navigate to={dashboard} replace />
  }

  return <>{children}</>
}
