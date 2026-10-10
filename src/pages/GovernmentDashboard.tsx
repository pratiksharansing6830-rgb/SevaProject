import { useEffect, useState } from 'react'
import { getGovernmentDashboard, type GovernmentDashboard as GovernmentDashboardData, type ServiceType } from '../api/continuity'
import { useAuth } from '../auth/AuthContext'

const SERVICE_LABELS: Record<ServiceType, string> = {
  EDUCATION: 'Education',
  HEALTHCARE: 'Healthcare',
  NUTRITION: 'Nutrition',
  PROTECTION: 'Protection',
  WELLBEING: 'Well-being',
  INCLUSION: 'Inclusion',
}

function Metric({ label, value, note }: { label: string; value: number; note?: string }) {
  return (
    <article className="rounded-xl border border-slate-200 bg-white p-5">
      <p className="text-sm font-medium text-slate-600">{label}</p>
      <p className="mt-2 text-3xl font-bold text-slate-900">{value.toLocaleString()}</p>
      {note && <p className="mt-1 text-xs text-slate-500">{note}</p>}
    </article>
  )
}

export default function GovernmentDashboard() {
  const { token } = useAuth()
  const [data, setData] = useState<GovernmentDashboardData | null>(null)
  const [error, setError] = useState('')
  const [retry, setRetry] = useState(0)

  useEffect(() => {
    if (!token) return
    let active = true
    void getGovernmentDashboard(token)
      .then((result) => {
        if (active) setData(result)
      })
      .catch((cause: unknown) => {
        if (active) setError(cause instanceof Error ? cause.message : 'Could not load aggregate dashboard data.')
      })
    return () => {
      active = false
    }
  }, [retry, token])

  if (error) {
    return <div className="mx-auto max-w-7xl px-4 py-10"><p role="alert" className="rounded-lg border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-800">{error}</p><button type="button" onClick={() => { setError(''); setRetry((value) => value + 1) }} className="mt-3 text-sm font-semibold text-teal-800 hover:underline">Retry loading dashboard</button></div>
  }
  if (!data) return <p className="py-16 text-center text-slate-600">Loading aggregate planning data…</p>

  const maxNeeds = Math.max(1, ...data.unresolved_needs_by_service.map((item) => item.total))
  const maxMigrationCount = Math.max(1, ...data.migration_trend.map((item) => item.migration_count))

  return (
    <div className="mx-auto max-w-7xl px-4 py-10 sm:px-6 lg:px-8">
      <header className="mb-8">
        <p className="text-sm font-semibold uppercase tracking-wide text-emerald-700">Authorized planning</p>
        <h1 className="mt-1 text-3xl font-bold tracking-tight text-slate-900">Government service-gap dashboard</h1>
        <p className="mt-2 text-sm text-slate-600">Aggregate operational counts only · Updated {data.as_of}</p>
      </header>

      <section aria-label="Profile counts" className="grid gap-4 sm:grid-cols-2">
        <Metric label="Family profiles" value={data.profile_counts.family_count} note="Registered in the platform; not a count of confirmed service outcomes." />
        <Metric label="Child profiles" value={data.profile_counts.child_count} note="Aggregate profile count; individual records are not available on this dashboard." />
      </section>

      <section aria-labelledby="migration-heading" className="mt-8">
        <h2 id="migration-heading" className="mb-3 text-xl font-bold text-slate-900">Migration lifecycle</h2>
        <div className="grid gap-4 sm:grid-cols-3">
          {(['PLANNED', 'ACTIVE', 'COMPLETED'] as const).map((status) => (
            <Metric key={status} label={`${status[0]}${status.slice(1).toLowerCase()} migrations`} value={data.migration_counts[status]} />
          ))}
        </div>
      </section>

      <section aria-labelledby="followup-heading" className="mt-8">
        <h2 id="followup-heading" className="mb-3 text-xl font-bold text-slate-900">Follow-up workload</h2>
        <div className="grid gap-4 sm:grid-cols-3">
          <Metric label="Open or in progress" value={data.followups.open_or_in_progress} />
          <Metric label="Due today" value={data.followups.due_today} />
          <Metric label="Overdue" value={data.followups.overdue} />
        </div>
      </section>

      <section aria-labelledby="needs-heading" className="mt-8 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
        <h2 id="needs-heading" className="text-xl font-bold text-slate-900">Unresolved needs by service category</h2>
        <p className="mt-1 text-sm text-slate-600">Counts use each child&apos;s effective migration and include pending, follow-up, and review-required statuses.</p>
        <ul className="mt-5 space-y-4">
          {data.unresolved_needs_by_service.map((item) => (
            <li key={item.service_type}>
              <div className="flex items-center justify-between gap-3 text-sm">
                <span className="font-medium text-slate-800">{SERVICE_LABELS[item.service_type]}</span>
                <span className="font-semibold text-slate-900">{item.total.toLocaleString()}</span>
              </div>
              <div className="mt-2 h-2 overflow-hidden rounded-full bg-slate-100" aria-hidden="true">
                <div className="h-full rounded-full bg-amber-500" style={{ width: `${(item.total / maxNeeds) * 100}%` }} />
              </div>
              <p className="mt-1 text-xs text-slate-500">
                {item.pending} pending · {item.follow_up_required} follow-up · {item.review_required} review
              </p>
            </li>
          ))}
        </ul>
      </section>

      <div className="mt-8 grid gap-8 lg:grid-cols-2">
        <section aria-labelledby="geography-heading" className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
          <h2 id="geography-heading" className="text-xl font-bold text-slate-900">Destination service gaps</h2>
          <p className="mt-1 text-sm text-slate-600">District/category rows are shown only when at least {data.privacy.geographic_suppression_threshold} families contribute to that group.</p>
          {data.destination_service_gaps.length ? (
            <div className="mt-4 overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead><tr className="border-b border-slate-200 text-xs uppercase text-slate-500"><th className="py-2 pr-3">District</th><th className="py-2 pr-3">Category</th><th className="py-2 pr-3">Unresolved</th><th className="py-2">Children*</th></tr></thead>
                <tbody>
                  {data.destination_service_gaps.map((gap) => (
                    <tr key={`${gap.district}-${gap.service_type}`} className="border-b border-slate-100 last:border-0">
                      <td className="py-3 pr-3 font-medium text-slate-800">{gap.district}</td>
                      <td className="py-3 pr-3 text-slate-700">{SERVICE_LABELS[gap.service_type]}</td>
                      <td className="py-3 pr-3 text-slate-700">{gap.unresolved_need_count}</td>
                      <td className="py-3 text-slate-700">{gap.affected_child_count}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
              <p className="mt-3 text-xs text-slate-500">Small district/category groups are suppressed; this table does not identify children or families.</p>
            </div>
          ) : (
            <p className="mt-4 rounded-lg bg-slate-50 p-4 text-sm text-slate-600">No destination groups meet the privacy threshold, or reliable district data is not available.</p>
          )}
        </section>

        <section aria-labelledby="trend-heading" className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
          <h2 id="trend-heading" className="text-xl font-bold text-slate-900">Recent migration trend</h2>
          <p className="mt-1 text-sm text-slate-600">Monthly totals over the latest six months; months with fewer than {data.privacy.geographic_suppression_threshold} contributing families are omitted.</p>
          {data.migration_trend.length ? (
            <ul className="mt-5 space-y-4">
              {data.migration_trend.map((item) => (
                <li key={item.month}>
                  <div className="flex justify-between gap-3 text-sm"><span className="font-medium text-slate-800">{item.month}</span><span className="text-slate-700">{item.migration_count} migrations · {item.family_count} families</span></div>
                  <div className="mt-2 h-2 overflow-hidden rounded-full bg-slate-100" aria-hidden="true">
                    <div className="h-full rounded-full bg-sky-600" style={{ width: `${(item.migration_count / maxMigrationCount) * 100}%` }} />
                  </div>
                </li>
              ))}
            </ul>
          ) : (
            <p className="mt-4 rounded-lg bg-slate-50 p-4 text-sm text-slate-600">No monthly trend meets the privacy threshold in this period.</p>
          )}
        </section>
      </div>

      <p className="mt-8 rounded-xl border border-slate-200 bg-slate-100 p-4 text-xs leading-5 text-slate-600">
        Aggregate counts describe records currently held in the platform and are not evidence that support was received. Seeded demo family records are excluded using their DEMO- reference. Do not use suppressed or missing geographic rows to infer individual cases.
      </p>
    </div>
  )
}
