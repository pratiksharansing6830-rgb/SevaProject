import { LockKeyhole, Mail, ShieldCheck } from 'lucide-react'
import { useState } from 'react'
import { Link, Navigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'
import { Button } from '../components/common/Button'

export default function Login() {
  const { isAuthenticated, login, isLoading, user } = useAuth()
  const [identifier, setIdentifier] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  if (isAuthenticated) {
    const destination = user?.role === 'GOVERNMENT' || user?.role === 'ADMIN'
      ? '/government/dashboard'
      : user?.role === 'SCHOOL' || user?.role === 'HEALTHCARE'
        ? '/map'
        : '/dashboard'
    return <Navigate to={destination} replace />
  }

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setError('')
    setSubmitting(true)

    try {
      await login({ identifier, password })
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to sign in. Please check your credentials.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="mx-auto max-w-6xl px-4 py-12 sm:px-6 lg:px-8">
      <div className="grid gap-8 rounded-[2rem] border border-slate-200 bg-white p-6 shadow-sm lg:grid-cols-[1fr_1.05fr] lg:p-8">
        <div className="space-y-6">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-emerald-700">Secure access</p>
            <h1 className="mt-3 text-3xl font-bold tracking-tight text-slate-900">Welcome back</h1>
          </div>

          <form className="space-y-5" onSubmit={handleSubmit}>
            <div>
              <label htmlFor="login-identifier" className="mb-2 block text-sm font-medium text-slate-700">
                Email or mobile
              </label>
              <div className="relative">
                <Mail className="pointer-events-none absolute left-3 top-3.5 h-4 w-4 text-slate-400" aria-hidden="true" />
                <input
                  id="login-identifier"
                  type="text"
                  autoComplete="username"
                  required
                  minLength={3}
                  value={identifier}
                  onChange={(event) => setIdentifier(event.target.value)}
                  placeholder="username@example.com"
                  className="w-full rounded-xl border border-slate-300 bg-slate-50 py-3 pl-10 pr-3 text-slate-900 outline-none transition focus:border-emerald-500 focus:ring-2 focus:ring-emerald-100"
                />
              </div>
            </div>

            <div>
              <div className="mb-2 flex items-center justify-between">
                <label htmlFor="login-password" className="text-sm font-medium text-slate-700">
                  Password
                </label>
              </div>
              <div className="relative">
                <LockKeyhole className="pointer-events-none absolute left-3 top-3.5 h-4 w-4 text-slate-400" aria-hidden="true" />
                <input
                  id="login-password"
                  type="password"
                  autoComplete="current-password"
                  required
                  minLength={8}
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                  placeholder="Enter your password"
                  className="w-full rounded-xl border border-slate-300 bg-slate-50 py-3 pl-10 pr-3 text-slate-900 outline-none transition focus:border-emerald-500 focus:ring-2 focus:ring-emerald-100"
                />
              </div>
            </div>

            {error ? (
              <div role="alert" aria-live="assertive" className="rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">{error}</div>
            ) : null}

            <Button type="submit" className="w-full justify-center" disabled={submitting || isLoading} aria-busy={submitting || isLoading}>
              {submitting ? 'Signing in…' : 'Sign In'}
            </Button>

            <p className="text-center text-sm text-slate-600">
              Don&apos;t have an account?{' '}
              <Link to="/register" className="font-semibold text-emerald-700 hover:text-emerald-800">
                Register
              </Link>
            </p>
          </form>
        </div>

        <div className="rounded-[1.5rem] bg-slate-50 p-5">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-100 text-emerald-700">
              <ShieldCheck className="h-5 w-5" aria-hidden="true" />
            </div>
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Account access</p>
              <h2 className="text-xl font-bold text-slate-900">Access follows your account role</h2>
            </div>
          </div>
          <p className="mt-6 text-sm leading-6 text-slate-600">
            Sign in with the account you registered. The platform checks your role and permissions before loading
            family records or aggregate planning data.
          </p>
          <p className="mt-4 text-sm text-slate-600">Password recovery is not available in this proof of concept.</p>
        </div>
      </div>
    </div>
  )
}
