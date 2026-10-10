import { AlertTriangle, CheckCircle2 } from 'lucide-react'
import { useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'
import { Button } from '../components/common/Button'
import { languages } from '../data/mockData'

const accountRoleMap = {
  'Parent / Guardian': 'CITIZEN',
  School: 'SCHOOL',
  'Healthcare Worker': 'HEALTHCARE',
  'NGO / Social Worker': 'NGO_WORKER',
} as const

export default function Register() {
  const { register } = useAuth()
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState('')
  const requestedRole = searchParams.get('role')
  const initialAccountType = requestedRole === 'SCHOOL' ? 'School'
    : requestedRole === 'HEALTHCARE' ? 'Healthcare Worker'
      : requestedRole === 'NGO_WORKER' ? 'NGO / Social Worker'
        : 'Parent / Guardian'
  const [form, setForm] = useState({
    accountType: initialAccountType,
    full_name: '',
    mobile_number: '',
    email: '',
    password: '',
    confirm_password: '',
    preferred_language: 'English',
    agree: false,
  })

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setError('')

    if (!form.agree) {
      setError('You must agree to the platform privacy principles before creating an account.')
      return
    }

    try {
      setIsSubmitting(true)
      await register({
        full_name: form.full_name,
        email: form.email,
        mobile_number: form.mobile_number,
        password: form.password,
        confirm_password: form.confirm_password,
        role: accountRoleMap[form.accountType as keyof typeof accountRoleMap],
        preferred_language: form.preferred_language as 'English' | 'Marathi' | 'Hindi',
      })
      navigate('/login')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to create the account at this time.')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="mx-auto max-w-5xl px-4 py-12 sm:px-6 lg:px-8">
      <div className="rounded-[2rem] border border-slate-200 bg-white p-6 shadow-sm lg:p-8">
        <div className="mb-8">
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-emerald-700">Create account</p>
          <h1 className="mt-3 text-3xl font-bold tracking-tight text-slate-900">Join the platform</h1>
        </div>

        <form className="space-y-6" onSubmit={handleSubmit}>
          <div>
            <label htmlFor="account-type" className="mb-2 block text-sm font-medium text-slate-700">
              Account Type
            </label>
            <select
              id="account-type"
              value={form.accountType}
              onChange={(event) => setForm((current) => ({ ...current, accountType: event.target.value }))}
              className="w-full rounded-xl border border-slate-300 bg-slate-50 px-3 py-3 text-slate-900 outline-none transition focus:border-emerald-500 focus:ring-2 focus:ring-emerald-100"
            >
              <option>Parent / Guardian</option>
              <option>School</option>
              <option>Healthcare Worker</option>
              <option>NGO / Social Worker</option>
            </select>
          </div>

          <div className="grid gap-5 md:grid-cols-2">
            <div>
              <label htmlFor="full-name" className="mb-2 block text-sm font-medium text-slate-700">Full Name</label>
              <input
                id="full-name"
                type="text"
                autoComplete="name"
                required
                minLength={2}
                maxLength={120}
                value={form.full_name}
                onChange={(event) => setForm((current) => ({ ...current, full_name: event.target.value }))}
                placeholder="Enter your full name"
                className="w-full rounded-xl border border-slate-300 bg-slate-50 px-3 py-3 text-slate-900 outline-none transition focus:border-emerald-500 focus:ring-2 focus:ring-emerald-100"
              />
            </div>
            <div>
              <label htmlFor="mobile-number" className="mb-2 block text-sm font-medium text-slate-700">Mobile Number</label>
              <input
                id="mobile-number"
                type="tel"
                autoComplete="tel"
                required
                minLength={8}
                maxLength={20}
                value={form.mobile_number}
                onChange={(event) => setForm((current) => ({ ...current, mobile_number: event.target.value }))}
                placeholder="+91 98765 43210"
                className="w-full rounded-xl border border-slate-300 bg-slate-50 px-3 py-3 text-slate-900 outline-none transition focus:border-emerald-500 focus:ring-2 focus:ring-emerald-100"
              />
            </div>
          </div>

          <div className="grid gap-5 md:grid-cols-2">
            <div>
              <label htmlFor="email" className="mb-2 block text-sm font-medium text-slate-700">Email</label>
              <input
                id="email"
                type="email"
                autoComplete="email"
                required
                maxLength={255}
                value={form.email}
                onChange={(event) => setForm((current) => ({ ...current, email: event.target.value }))}
                placeholder="name@example.com"
                className="w-full rounded-xl border border-slate-300 bg-slate-50 px-3 py-3 text-slate-900 outline-none transition focus:border-emerald-500 focus:ring-2 focus:ring-emerald-100"
              />
            </div>
            <div>
              <label htmlFor="preferred-language" className="mb-2 block text-sm font-medium text-slate-700">Preferred Language</label>
              <select
                id="preferred-language"
                value={form.preferred_language}
                onChange={(event) => setForm((current) => ({ ...current, preferred_language: event.target.value }))}
                className="w-full rounded-xl border border-slate-300 bg-slate-50 px-3 py-3 text-slate-900 outline-none transition focus:border-emerald-500 focus:ring-2 focus:ring-emerald-100"
              >
                {languages.map((language) => (
                  <option key={language}>{language}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="grid gap-5 md:grid-cols-2">
            <div>
              <label htmlFor="password" className="mb-2 block text-sm font-medium text-slate-700">Password</label>
              <input
                id="password"
                type="password"
                autoComplete="new-password"
                required
                minLength={8}
                value={form.password}
                onChange={(event) => setForm((current) => ({ ...current, password: event.target.value }))}
                placeholder="Create a password"
                className="w-full rounded-xl border border-slate-300 bg-slate-50 px-3 py-3 text-slate-900 outline-none transition focus:border-emerald-500 focus:ring-2 focus:ring-emerald-100"
              />
            </div>
            <div>
              <label htmlFor="confirm-password" className="mb-2 block text-sm font-medium text-slate-700">Confirm Password</label>
              <input
                id="confirm-password"
                type="password"
                autoComplete="new-password"
                required
                minLength={8}
                value={form.confirm_password}
                onChange={(event) => setForm((current) => ({ ...current, confirm_password: event.target.value }))}
                placeholder="Re-enter your password"
                className="w-full rounded-xl border border-slate-300 bg-slate-50 px-3 py-3 text-slate-900 outline-none transition focus:border-emerald-500 focus:ring-2 focus:ring-emerald-100"
              />
            </div>
          </div>

          <label className="flex items-start gap-3 rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-700">
            <input
              type="checkbox"
              required
              checked={form.agree}
              onChange={(event) => setForm((current) => ({ ...current, agree: event.target.checked }))}
              className="mt-1 h-4 w-4 rounded border-slate-300 text-emerald-600"
            />
            <span>I agree to the platform&apos;s privacy and data-use principles.</span>
          </label>

          {error ? (
            <div role="alert" aria-live="assertive" className="rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">{error}</div>
          ) : null}

          <div className="flex flex-col gap-3 sm:flex-row">
            <Button type="submit" className="justify-center" disabled={isSubmitting} aria-busy={isSubmitting}>
              {isSubmitting ? 'Creating account…' : 'Create Account'}
            </Button>
            <Button variant="outline" to="/login" className="justify-center">Back to Login</Button>
          </div>
        </form>

        <div className="mt-8 rounded-2xl border border-emerald-200 bg-emerald-50 p-4">
          <div className="flex items-start gap-3 text-sm text-emerald-900">
            <CheckCircle2 className="mt-0.5 h-5 w-5 shrink-0" aria-hidden="true" />
            <p>Only information necessary for providing services should be collected. Child information is sensitive and will be protected through role-based access.</p>
          </div>
        </div>

        <div className="mt-4 flex items-start gap-3 rounded-2xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-900">
          <AlertTriangle className="mt-0.5 h-5 w-5 shrink-0" aria-hidden="true" />
          <p>Government and administrator accounts are not self-registered in this prototype.</p>
        </div>
      </div>
    </div>
  )
}
