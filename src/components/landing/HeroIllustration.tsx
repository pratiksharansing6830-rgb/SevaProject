import { ArrowDown, ClipboardList, MapPin, UserRound } from 'lucide-react'

export function HeroIllustration() {
  return (
    <div className="relative mx-auto w-full max-w-xl rounded-[2rem] border border-slate-200 bg-white p-5 shadow-[0_30px_60px_-30px_rgba(15,23,42,0.35)]">
      <div className="rounded-[1.5rem] border border-slate-200 bg-slate-50 p-4">
        <div className="flex items-center justify-between border-b border-slate-200 pb-4">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Workflow overview</p>
            <h3 className="mt-2 text-lg font-bold text-slate-900">Family support</h3>
          </div>
          <ClipboardList className="h-5 w-5 text-slate-500" aria-hidden="true" />
        </div>

        <div className="mt-4 grid gap-3 sm:grid-cols-2">
          <div className="rounded-2xl border border-slate-200 bg-white p-3">
            <div className="flex items-center gap-2 text-slate-500">
              <UserRound className="h-4 w-4" aria-hidden="true" />
              <span className="text-xs font-medium">Family records</span>
            </div>
            <p className="mt-3 text-xl font-bold text-slate-900">Families and children</p>
            <p className="mt-1 text-sm text-slate-600">Managed by authorized users</p>
          </div>

          <div className="rounded-2xl border border-slate-200 bg-white p-3">
            <div className="flex items-center gap-2 text-slate-500">
              <MapPin className="h-4 w-4" aria-hidden="true" />
              <span className="text-xs font-medium">Migration records</span>
            </div>
            <p className="mt-3 text-xl font-bold text-slate-900">Plan and track</p>
            <p className="mt-1 text-sm text-slate-600">Review continuity at each step</p>
          </div>
        </div>

        <div className="mt-6 rounded-2xl border border-slate-200 bg-white p-4">
          <div className="flex items-center justify-between">
            <p className="text-sm font-semibold text-slate-700">Needs to review</p>
            <ClipboardList className="h-5 w-5 text-slate-500" aria-hidden="true" />
          </div>

          <div className="mt-4 grid grid-cols-2 gap-3">
            {['Education', 'Healthcare', 'Nutrition', 'Wellbeing', 'Protection', 'Inclusion'].map((label) => (
              <div key={label} className="flex items-center gap-2 text-sm text-slate-700">
                <span>{label}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="mt-6 flex items-center justify-center gap-2 text-center text-sm font-medium text-slate-600">
        <span className="rounded-full bg-slate-100 px-3 py-1.5">Record needs</span>
        <ArrowDown className="h-4 w-4 text-slate-400" aria-hidden="true" />
        <span className="rounded-full bg-slate-100 px-3 py-1.5">Plan support</span>
        <ArrowDown className="h-4 w-4 text-slate-400" aria-hidden="true" />
        <span className="rounded-full bg-slate-100 px-3 py-1.5">Track follow-up</span>
        <ArrowDown className="h-4 w-4 text-slate-400" aria-hidden="true" />
        <span className="rounded-full bg-slate-100 px-3 py-1.5">Confirm outcomes</span>
      </div>
    </div>
  )
}
