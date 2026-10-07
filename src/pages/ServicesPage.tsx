import { SectionHeader } from '../components/common/SectionHeader'
import { serviceGroups } from '../data/mockData'

export default function ServicesPage() {
  return (
    <div className="mx-auto max-w-7xl px-4 py-16 sm:px-6 lg:px-8">
      <SectionHeader
        eyebrow="Service overview"
        title="A continuity-focused service model for children and families"
        description="The platform helps maintain continuity across child welfare, public support, and coordination services as families move within a state."
      />

      <div className="mt-10 space-y-12">
        {serviceGroups.map((group) => (
          <section key={group.title}>
            <h2 className="text-2xl font-bold tracking-tight text-slate-900">{group.title}</h2>
            <div className="mt-5 grid gap-5 md:grid-cols-2 xl:grid-cols-3">
              {group.services.map(({ title, description, icon: Icon }) => (
                <article key={title} className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
                  <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-emerald-50 text-emerald-700">
                    <Icon className="h-5 w-5" aria-hidden="true" />
                  </div>
                  <h3 className="mt-5 text-xl font-bold text-slate-900">{title}</h3>
                  <p className="mt-3 text-sm leading-6 text-slate-600">{description}</p>
                </article>
              ))}
            </div>
          </section>
        ))}
      </div>
    </div>
  )
}
