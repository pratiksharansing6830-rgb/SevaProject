import {
  ArrowRight,
  MapPinned,
  ShieldCheck,
} from 'lucide-react'
import { Link } from 'react-router-dom'
import { Badge } from '../components/common/Badge'
import { Button } from '../components/common/Button'
import { SectionHeader } from '../components/common/SectionHeader'
import { HeroIllustration } from '../components/landing/HeroIllustration'
import { featuredServices, howItWorksSteps, userGroups } from '../data/mockData'

export default function Home() {
  return (
    <div className="bg-slate-50 text-slate-900">
      <section className="mx-auto max-w-7xl px-4 pb-16 pt-12 sm:px-6 lg:px-8 lg:pb-20 lg:pt-16">
        <div className="grid items-center gap-10 lg:grid-cols-[1.1fr_0.9fr]">
          <div>
            <Badge label="Designed for families, organizations and public-service coordination" tone="info" />
            <h1 className="mt-6 max-w-xl text-4xl font-extrabold tracking-tight text-slate-900 sm:text-5xl lg:text-6xl">
              When Families Move, Children&apos;s Essential Services Shouldn&apos;t Stop.
            </h1>
            <p className="mt-6 max-w-xl text-lg leading-8 text-slate-600">
              A family-support platform for recording migration, tracking service continuity needs, and finding services
              from the available directory during intra-state migration.
            </p>
            <div className="mt-8 flex flex-col gap-3 sm:flex-row">
              <Button to="/register">Get Started</Button>
              <Button variant="outline" to="/services">
                Explore Services
              </Button>
            </div>
            <div className="mt-8 flex items-center gap-3 text-sm text-slate-600">
              <ShieldCheck className="h-5 w-5 text-emerald-600" aria-hidden="true" />
              <span>Human-centered service continuity for every child.</span>
            </div>
          </div>

          <HeroIllustration />
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-4 py-16 sm:px-6 lg:px-8">
        <SectionHeader
          eyebrow="Core services"
          title="Supporting Every Child Through Every Move"
          description="A continuity-first approach ensures that essential services stay connected even when a family relocates within the state."
          align="center"
        />

        <div className="mt-10 grid gap-5 md:grid-cols-2 xl:grid-cols-4">
          {featuredServices.map(({ title, description, icon: Icon }) => (
            <article key={title} className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm transition-shadow hover:shadow-md">
              <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-emerald-50 text-emerald-700">
                <Icon className="h-5 w-5" aria-hidden="true" />
              </div>
              <h3 className="mt-5 text-xl font-bold text-slate-900">{title}</h3>
              <p className="mt-3 text-sm leading-6 text-slate-600">{description}</p>
              <Link to="/services" className="mt-5 inline-flex items-center gap-2 text-sm font-semibold text-emerald-700 hover:text-emerald-800">
                Learn More <ArrowRight className="h-4 w-4" aria-hidden="true" />
              </Link>
            </article>
          ))}
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-4 py-16 sm:px-6 lg:px-8">
        <SectionHeader eyebrow="How it works" title="A simple continuity process" description="The platform helps families, schools, and support workers stay connected during transitions." />

        <div className="mt-10 grid gap-5 md:grid-cols-2 xl:grid-cols-4">
          {howItWorksSteps.map((step) => (
            <div key={step.number} className="relative rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
              <div className="mb-5 flex items-center justify-between">
                <span className="text-xs font-semibold uppercase tracking-[0.2em] text-emerald-700">{step.number}</span>
                <span className="flex h-9 w-9 items-center justify-center rounded-full bg-emerald-50 text-sm font-bold text-emerald-700">{step.number}</span>
              </div>
              <h3 className="text-xl font-bold text-slate-900">{step.title}</h3>
              <p className="mt-3 text-sm leading-6 text-slate-600">{step.description}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-4 py-16 sm:px-6 lg:px-8">
        <SectionHeader
          eyebrow="Working tools"
          title="Use the persisted family-support workflow"
          description="The signed-in tools load family and child records from the API. Directory matches are potential listings only; they do not confirm service availability or support."
          align="center"
        />
        <div className="mt-10 grid gap-5 md:grid-cols-3">
          <article className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <h3 className="text-xl font-bold text-slate-900">Family and child records</h3>
            <p className="mt-3 text-sm leading-6 text-slate-600">Create and manage authorized family profiles, child profiles, and service information.</p>
            <Button to="/family" className="mt-5">Open family records</Button>
          </article>
          <article className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <h3 className="text-xl font-bold text-slate-900">Migration and continuity</h3>
            <p className="mt-3 text-sm leading-6 text-slate-600">Record a move, review unresolved needs, track provider contact, and confirm outcomes with evidence.</p>
            <Button to="/family" className="mt-5">Manage a family</Button>
          </article>
          <article className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <div className="flex items-center gap-2"><MapPinned className="h-5 w-5 text-emerald-700" aria-hidden="true" /><h3 className="text-xl font-bold text-slate-900">Service directory</h3></div>
            <p className="mt-3 text-sm leading-6 text-slate-600">Search the directory for records that are actually available; verify eligibility and availability with each provider.</p>
            <Button to="/map" className="mt-5">Search directory</Button>
          </article>
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-4 py-16 sm:px-6 lg:px-8">
        <SectionHeader
          eyebrow="Users"
          title="Built for the people and organizations who support children"
          description="The platform is designed to support coordination across families, schools, NGOs, and public-service partners."
          align="center"
        />

        <div className="mt-10 grid gap-5 md:grid-cols-2 xl:grid-cols-4">
          {userGroups.map(({ title, description, icon: Icon }) => (
            <article key={title} className="rounded-2xl border border-slate-200 bg-white p-6 text-center shadow-sm">
              <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-xl bg-slate-100 text-slate-700">
                <Icon className="h-5 w-5" aria-hidden="true" />
              </div>
              <h3 className="mt-5 text-xl font-bold text-slate-900">{title}</h3>
              <p className="mt-3 text-sm leading-6 text-slate-600">{description}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="mx-auto max-w-6xl px-4 pb-20 pt-8 sm:px-6 lg:px-8">
        <div className="rounded-[2rem] bg-gradient-to-r from-emerald-700 to-sky-700 p-8 text-white shadow-lg sm:p-10">
          <div className="flex flex-col gap-5 lg:flex-row lg:items-center lg:justify-between">
            <div className="max-w-2xl">
              <p className="text-xs font-semibold uppercase tracking-[0.2em] text-emerald-100">Public service coordination</p>
              <h2 className="mt-3 text-3xl font-bold tracking-tight md:text-4xl">Ready to support continuity when families move?</h2>
            </div>
            <div className="flex flex-col gap-3 sm:flex-row">
              <Button to="/role-selection" className="bg-white text-emerald-800 hover:bg-slate-100">
                Choose a role
              </Button>
              <Button variant="outline" to="/about" className="border-white bg-transparent text-white hover:bg-white/10 hover:text-white">
                Learn more
              </Button>
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}
