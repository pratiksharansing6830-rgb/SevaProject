import { CircleHelp, Mail, Phone } from 'lucide-react'
import { SectionHeader } from '../components/common/SectionHeader'

const helpCards = [
  {
    title: 'How do I update my family location?',
    description: 'Use the migration update flow to record your move to a new location and check continuity needs.',
  },
  {
    title: 'Who can see my information?',
    description: 'Access is designed to be role-based so families, schools and support organizations only see relevant information.',
  },
  {
    title: 'What happens if a service needs follow-up?',
    description: 'The platform can surface service follow-ups and escalation actions for human review and support coordination.',
  },
]

export default function HelpPage() {
  return (
    <div className="mx-auto max-w-7xl px-4 py-16 sm:px-6 lg:px-8">
      <SectionHeader
        eyebrow="Help and support"
        title="Support resources for families and organizations"
        description="This help center is a static frontend preview and can be expanded with real guidance and service information in future phases."
      />

      <div className="mt-10 grid gap-5 md:grid-cols-3">
        {helpCards.map(({ title, description }) => (
          <article key={title} className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-sky-50 text-sky-700">
              <CircleHelp className="h-5 w-5" aria-hidden="true" />
            </div>
            <h3 className="mt-5 text-xl font-bold text-slate-900">{title}</h3>
            <p className="mt-3 text-sm leading-6 text-slate-600">{description}</p>
          </article>
        ))}
      </div>

      <div className="mt-12 grid gap-6 rounded-[2rem] border border-slate-200 bg-white p-6 shadow-sm lg:grid-cols-2">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Contact details</p>
          <h3 className="mt-3 text-3xl font-bold text-slate-900">Still need assistance?</h3>
          <p className="mt-4 text-base text-slate-600">This contact panel is a placeholder for future service support channels and public information workflows.</p>
        </div>
        <div className="space-y-4 text-sm text-slate-700">
          <div className="flex items-center gap-3 rounded-xl border border-slate-200 bg-slate-50 p-4">
            <Mail className="h-5 w-5 text-emerald-700" aria-hidden="true" />
            <span>support@sahaayak.example</span>
          </div>
          <div className="flex items-center gap-3 rounded-xl border border-slate-200 bg-slate-50 p-4">
            <Phone className="h-5 w-5 text-emerald-700" aria-hidden="true" />
            <span>+91 98765 43210</span>
          </div>
        </div>
      </div>
    </div>
  )
}
