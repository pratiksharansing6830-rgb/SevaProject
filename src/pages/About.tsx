import { ArrowRight, BrainCircuit, ShieldCheck, Sparkles, Users } from 'lucide-react'
import { SectionHeader } from '../components/common/SectionHeader'

const pillars = [
  {
    title: 'Mission',
    description: 'Ensure that migration does not interrupt a child’s essential services.',
    icon: Users,
  },
  {
    title: 'Problem',
    description: 'Children of migrant-worker families may experience interruptions in education, healthcare, nutrition and support when families move.',
    icon: ShieldCheck,
  },
  {
    title: 'Our Approach',
    description: 'The platform uses a continuity-based model to keep service planning connected across migration events and local service networks.',
    icon: ArrowRight,
  },
  {
    title: 'Technology Vision',
    description: 'AI, GIS, secure digital services, role-based access and analytics can work together to support coordinated, human-led decisions.',
    icon: BrainCircuit,
  },
]

export default function About() {
  return (
    <div className="mx-auto max-w-7xl px-4 py-16 sm:px-6 lg:px-8">
      <SectionHeader
        eyebrow="About Sahaayak"
        title="A continuity-first platform for children and families on the move"
        description="The platform is designed to reduce service disruption for children whose families move within a state and need support across education, health, nutrition, protection and welfare services."
      />

      <div className="mt-10 grid gap-5 md:grid-cols-2 xl:grid-cols-4">
        {pillars.map(({ title, description, icon: Icon }) => (
          <article key={title} className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-emerald-50 text-emerald-700">
              <Icon className="h-5 w-5" aria-hidden="true" />
            </div>
            <h3 className="mt-5 text-xl font-bold text-slate-900">{title}</h3>
            <p className="mt-3 text-sm leading-6 text-slate-600">{description}</p>
          </article>
        ))}
      </div>

      <div className="mt-14 rounded-[2rem] border border-slate-200 bg-white p-8 shadow-sm md:p-10">
        <div className="grid gap-8 lg:grid-cols-2">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-emerald-700">Problem statement</p>
            <h3 className="mt-3 text-3xl font-bold text-slate-900">Children shouldn&apos;t lose access to essential support during migration.</h3>
            <p className="mt-4 text-base leading-7 text-slate-600">
              When families move between areas within the same state, children may face breaks in school enrollment,
              health follow-ups, nutrition support, child protection oversight, and social service coordination. The result can be unstable service access and compounding welfare risk.
            </p>
          </div>

          <div className="rounded-2xl bg-slate-50 p-6">
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Technology vision</p>
            <ul className="mt-5 space-y-4 text-sm text-slate-700">
              <li className="flex items-center gap-3"><Sparkles className="h-4 w-4 text-sky-600" aria-hidden="true" /> AI-driven recommendations and follow-up assistance</li>
              <li className="flex items-center gap-3"><ArrowRight className="h-4 w-4 text-sky-600" aria-hidden="true" /> GIS-based service discovery and geographic insight</li>
              <li className="flex items-center gap-3"><ShieldCheck className="h-4 w-4 text-sky-600" aria-hidden="true" /> Secure digital services with role-based access</li>
              <li className="flex items-center gap-3"><Users className="h-4 w-4 text-sky-600" aria-hidden="true" /> Analytics to support decision-making and planning</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}
