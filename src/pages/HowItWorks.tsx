import { CheckCircle2 } from 'lucide-react'
import { SectionHeader } from '../components/common/SectionHeader'
import { howItWorksSteps } from '../data/mockData'

export default function HowItWorks() {
  return (
    <div className="mx-auto max-w-7xl px-4 py-16 sm:px-6 lg:px-8">
      <SectionHeader
        eyebrow="How it works"
        title="A simple process to maintain service continuity"
        description="Families and support teams can update, coordinate and track essential support needs as a child moves between locations."
      />

      <div className="mt-12 space-y-6">
        {howItWorksSteps.map((step, index) => (
          <div key={step.number} className="grid gap-6 rounded-[2rem] border border-slate-200 bg-white p-6 shadow-sm md:grid-cols-[80px_1fr_auto] md:items-center">
            <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-emerald-50 text-lg font-bold text-emerald-700">{step.number}</div>
            <div>
              <h3 className="text-2xl font-bold text-slate-900">{step.title}</h3>
              <p className="mt-2 text-base text-slate-600">{step.description}</p>
            </div>
            <div className="flex items-center gap-2 text-sm font-medium text-slate-500">
              <CheckCircle2 className="h-5 w-5 text-emerald-600" aria-hidden="true" />
              Step {index + 1}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
