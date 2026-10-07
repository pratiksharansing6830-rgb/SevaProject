import { MapPin } from 'lucide-react'
import { mapPoints } from '../../data/mockData'

export function MapPreview() {
  return (
    <div className="rounded-[2rem] border border-slate-200 bg-slate-100 p-4 shadow-sm">
      <div className="relative h-[360px] overflow-hidden rounded-[1.5rem] border border-slate-200 bg-[radial-gradient(circle_at_center,_rgba(148,163,184,0.22),_rgba(15,23,42,0.04)_40%,_rgba(255,255,255,0.2)_100%)]">
        <div className="absolute inset-0 opacity-50 [background-image:linear-gradient(rgba(148,163,184,0.18)_1px,transparent_1px),linear-gradient(90deg,rgba(148,163,184,0.18)_1px,transparent_1px)] [background-size:26px_26px]" />

        {mapPoints.map((point) => (
          <div key={point.title} className={`absolute ${point.position}`}>
            <div className="relative">
              <span className="flex h-4 w-4 items-center justify-center rounded-full bg-emerald-600 shadow-[0_0_0_6px_rgba(16,185,129,0.14)]">
                <MapPin className="h-2.5 w-2.5 fill-white text-white" aria-hidden="true" />
              </span>
              <span className="absolute left-5 top-1 whitespace-nowrap rounded-full border border-slate-200 bg-white px-2.5 py-1 text-[10px] font-semibold text-slate-700 shadow-sm">
                {point.title}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
