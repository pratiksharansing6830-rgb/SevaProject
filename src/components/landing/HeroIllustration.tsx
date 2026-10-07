import { ArrowDown, CircleCheckBig, MapPin, UserRound } from 'lucide-react'

export function HeroIllustration() {
  return (
    <div className="relative mx-auto w-full max-w-xl rounded-[2rem] border border-slate-200 bg-white p-5 shadow-[0_30px_60px_-30px_rgba(15,23,42,0.35)]">
      <div className="rounded-[1.5rem] border border-slate-200 bg-slate-50 p-4">
        <div className="flex items-center justify-between border-b border-slate-200 pb-4">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Continuity overview</p>
            <h3 className="mt-2 text-lg font-bold text-slate-900">Aarav Sharma</h3>
          </div>
          <span className="rounded-full bg-emerald-100 px-2.5 py-1 text-xs font-semibold text-emerald-800">Active</span>
        </div>

        <div className="mt-4 grid gap-3 sm:grid-cols-2">
          <div className="rounded-2xl border border-slate-200 bg-white p-3">
            <div className="flex items-center gap-2 text-slate-500">
              <UserRound className="h-4 w-4" aria-hidden="true" />
              <span className="text-xs font-medium">Family status</span>
            </div>
            <p className="mt-3 text-xl font-bold text-slate-900">Moved</p>
            <p className="mt-1 text-sm text-slate-600">Nashik → Pune</p>
          </div>

          <div className="rounded-2xl border border-slate-200 bg-white p-3">
            <div className="flex items-center gap-2 text-slate-500">
              <MapPin className="h-4 w-4" aria-hidden="true" />
              <span className="text-xs font-medium">Current location</span>
            </div>
            <p className="mt-3 text-xl font-bold text-slate-900">Pune</p>
            <p className="mt-1 text-sm text-slate-600">Maharashtra</p>
          </div>
        </div>

        <div className="mt-6 rounded-2xl border border-emerald-200 bg-emerald-50 p-4">
          <div className="flex items-center justify-between">
            <p className="text-sm font-semibold text-slate-700">Service continuity</p>
            <CircleCheckBig className="h-5 w-5 text-emerald-600" aria-hidden="true" />
          </div>

          <div className="mt-4 space-y-3">
            {['Education', 'Healthcare', 'Nutrition', 'Protection'].map((label, index) => (
              <div key={label} className="flex items-center justify-between gap-3 text-sm text-slate-700">
                <span>{label}</span>
                <span className={`inline-flex h-6 w-6 items-center justify-center rounded-full ${index === 2 ? 'bg-amber-100 text-amber-700' : 'bg-emerald-100 text-emerald-700'}`}>
                  {index === 2 ? '!' : '✓'}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="mt-6 flex items-center justify-center gap-2 text-center text-sm font-medium text-slate-600">
        <span className="rounded-full bg-slate-100 px-3 py-1.5">Family Moves</span>
        <ArrowDown className="h-4 w-4 text-slate-400" aria-hidden="true" />
        <span className="rounded-full bg-slate-100 px-3 py-1.5">Continuity Check</span>
        <ArrowDown className="h-4 w-4 text-slate-400" aria-hidden="true" />
        <span className="rounded-full bg-slate-100 px-3 py-1.5">Services Connected</span>
        <ArrowDown className="h-4 w-4 text-slate-400" aria-hidden="true" />
        <span className="rounded-full bg-slate-100 px-3 py-1.5">Child Supported</span>
      </div>
    </div>
  )
}
