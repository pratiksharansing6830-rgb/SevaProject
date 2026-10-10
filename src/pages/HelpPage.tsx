import { CircleHelp } from 'lucide-react'
import { Link } from 'react-router-dom'
import { Button } from '../components/common/Button'
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
        description="Use the signed-in family workflow to review service needs, record provider contacts, and track follow-ups."
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
          <p className="mt-4 text-base text-slate-600">No central support contact is configured. For service availability or eligibility, confirm directly with the provider listed in the service directory.</p>
          <Button to="/login" className="mt-5">Sign in to manage family support</Button>
        </div>
        <div className="flex items-center">
          <Link to="/services" className="text-sm font-semibold text-emerald-700 hover:underline">Review available workflow services</Link>
        </div>
      </div>
    </div>
  )
}
