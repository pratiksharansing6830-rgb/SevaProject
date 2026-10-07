import { Activity, ArrowRight, Bell, BriefcaseBusiness, FileText, MapPinned, ShieldCheck, Users } from 'lucide-react'
import { Button } from '../components/common/Button'
import { Badge } from '../components/common/Badge'
import { familyRecord } from '../data/mockData'

const quickActions = [
  { label: 'Update Migration', icon: MapPinned, to: '/help' },
  { label: 'View Child', icon: Users, to: '/dashboard' },
  { label: 'Find Services', icon: BriefcaseBusiness, to: '/services' },
  { label: 'Submit Help Request', icon: FileText, to: '/help' },
  { label: 'Ask AI Assistant', icon: Activity, to: '/help' },
]

export default function CitizenDashboard() {
  return (
    <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
      <header className="rounded-[2rem] border border-slate-200 bg-white p-6 shadow-sm">
        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div>
            <p className="text-sm font-medium text-slate-500">Dashboard overview</p>
            <h1 className="mt-2 text-3xl font-bold tracking-tight text-slate-900">Welcome, Parent</h1>
          </div>
          <div className="flex items-center gap-3">
            <div className="rounded-full bg-slate-100 p-2 text-slate-700">
              <Bell className="h-5 w-5" aria-hidden="true" />
            </div>
            <Badge label="3 follow-ups" tone="info" />
          </div>
        </div>

        <div className="mt-8 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">Family location</p>
            <p className="mt-3 text-xl font-bold text-slate-900">Pune, Maharashtra</p>
          </div>
          <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">Children</p>
            <p className="mt-3 text-xl font-bold text-slate-900">2</p>
          </div>
          <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">Active Service Requests</p>
            <p className="mt-3 text-xl font-bold text-slate-900">2</p>
          </div>
          <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">Follow-ups</p>
            <p className="mt-3 text-xl font-bold text-slate-900">3</p>
          </div>
        </div>
      </header>

      <div className="mt-8 grid gap-8 xl:grid-cols-[1.1fr_0.9fr]">
        <section className="rounded-[2rem] border border-slate-200 bg-white p-6 shadow-sm">
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-bold text-slate-900">Continuity Overview</h2>
            <Badge label="Child profile" tone="neutral" />
          </div>

          <div className="mt-6 space-y-3">
            {[
              ['Education', 'Connected'],
              ['Healthcare', 'Connected'],
              ['Nutrition', 'Review Needed'],
              ['Protection', 'Supported'],
              ['Well-being', 'Available'],
            ].map(([label, status]) => (
              <div key={label} className="flex items-center justify-between rounded-xl border border-slate-200 bg-slate-50 px-4 py-3">
                <span className="font-medium text-slate-700">{label}</span>
                <span className="text-sm text-slate-600">{status}</span>
              </div>
            ))}
          </div>
        </section>

        <aside className="rounded-[2rem] border border-slate-200 bg-slate-900 p-6 text-white shadow-sm">
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">Current child</p>
          <h2 className="mt-3 text-3xl font-bold">{familyRecord.childName}</h2>
          <div className="mt-6 space-y-4 text-sm text-slate-300">
            <div className="flex items-center justify-between rounded-xl border border-slate-700 bg-slate-800 px-4 py-3">
              <span>Age</span>
              <span>{familyRecord.age}</span>
            </div>
            <div className="flex items-center justify-between rounded-xl border border-slate-700 bg-slate-800 px-4 py-3">
              <span>Class</span>
              <span>{familyRecord.className}</span>
            </div>
            <div className="flex items-center justify-between rounded-xl border border-slate-700 bg-slate-800 px-4 py-3">
              <span>Location</span>
              <span>{familyRecord.currentLocation}</span>
            </div>
          </div>
        </aside>
      </div>

      <section className="mt-10 rounded-[2rem] border border-slate-200 bg-white p-6 shadow-sm">
        <div className="flex items-center justify-between gap-3">
          <h2 className="text-2xl font-bold text-slate-900">Quick actions</h2>
          <div className="flex items-center gap-2 text-slate-500">
            <ShieldCheck className="h-5 w-5 text-emerald-600" aria-hidden="true" />
            <span className="text-sm font-medium">Support coordination</span>
          </div>
        </div>

        <div className="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-5">
          {quickActions.map(({ label, icon: Icon, to }) => (
            <Button key={label} variant="outline" to={to} className="flex h-full flex-col items-start justify-between rounded-2xl border border-slate-200 bg-slate-50 px-4 py-4 text-left text-slate-800 hover:bg-white">
              <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-white text-slate-700">
                <Icon className="h-5 w-5" aria-hidden="true" />
              </span>
              <span className="mt-5 flex w-full items-center justify-between text-sm font-semibold">
                {label}
                <ArrowRight className="h-4 w-4" aria-hidden="true" />
              </span>
            </Button>
          ))}
        </div>
      </section>
    </div>
  )
}
