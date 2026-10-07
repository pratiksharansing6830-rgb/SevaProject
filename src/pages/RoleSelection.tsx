import { ArrowRight } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { Button } from '../components/common/Button'
import { SectionHeader } from '../components/common/SectionHeader'
import { roleOptions } from '../data/mockData'

export default function RoleSelection() {
  const navigate = useNavigate()

  return (
    <div className="mx-auto max-w-6xl px-4 py-16 sm:px-6 lg:px-8">
      <SectionHeader
        eyebrow="Choose your role"
        title="Select the profile that best matches your work"
        description="This preview page is designed for static role-based navigation. The selected profile can be used to open a dashboard preview."
        align="center"
      />

      <div className="mt-10 grid gap-5 md:grid-cols-2 xl:grid-cols-3">
        {roleOptions.map(({ title, description, icon: Icon }) => (
          <article key={title} className="rounded-[1.75rem] border border-slate-200 bg-white p-6 shadow-sm transition hover:-translate-y-0.5 hover:shadow-md">
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-emerald-50 text-emerald-700">
              <Icon className="h-5 w-5" aria-hidden="true" />
            </div>
            <h3 className="mt-5 text-xl font-bold text-slate-900">{title}</h3>
            <p className="mt-3 text-sm leading-6 text-slate-600">{description}</p>
            <Button variant="outline" className="mt-6 w-full justify-center" onClick={() => navigate('/dashboard')}>
              Continue <ArrowRight className="ml-2 h-4 w-4" aria-hidden="true" />
            </Button>
          </article>
        ))}
      </div>
    </div>
  )
}
