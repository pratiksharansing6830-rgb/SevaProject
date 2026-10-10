import { ArrowRight, GraduationCap, HandHelping, UserRound, HeartPulse } from 'lucide-react'
import { Button } from '../components/common/Button'
import { SectionHeader } from '../components/common/SectionHeader'

const roles = [
  { role: 'CITIZEN', title: 'Parent / Guardian', description: 'Manage family profiles and child continuity.', icon: UserRound },
  { role: 'SCHOOL', title: 'School', description: 'Create an account for school coordination access.', icon: GraduationCap },
  { role: 'HEALTHCARE', title: 'Healthcare Worker', description: 'Create an account for healthcare coordination access.', icon: HeartPulse },
  { role: 'NGO_WORKER', title: 'NGO / Social Worker', description: 'Coordinate authorized family support and follow-ups.', icon: HandHelping },
] as const

export default function RoleSelection() {
  return (
    <div className="mx-auto max-w-6xl px-4 py-16 sm:px-6 lg:px-8">
      <SectionHeader
        eyebrow="Choose your role"
        title="Select the profile that best matches your work"
        description="Choose the role you will use to register. Access to family and planning records remains controlled by backend permissions."
        align="center"
      />

      <div className="mt-10 grid gap-5 md:grid-cols-2 xl:grid-cols-3">
        {roles.map(({ role, title, description, icon: Icon }) => (
          <article key={title} className="rounded-[1.75rem] border border-slate-200 bg-white p-6 shadow-sm transition hover:-translate-y-0.5 hover:shadow-md">
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-emerald-50 text-emerald-700">
              <Icon className="h-5 w-5" aria-hidden="true" />
            </div>
            <h3 className="mt-5 text-xl font-bold text-slate-900">{title}</h3>
            <p className="mt-3 text-sm leading-6 text-slate-600">{description}</p>
            <Button variant="outline" className="mt-6 w-full justify-center" to={`/register?role=${role}`}>
              Register with this role <ArrowRight className="ml-2 h-4 w-4" aria-hidden="true" />
            </Button>
          </article>
        ))}
      </div>
    </div>
  )
}
