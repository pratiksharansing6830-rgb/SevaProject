import {
  ArrowRight,
  CheckCircle2,
  CircleAlert,
  MapPinned,
  ShieldCheck,
  Sparkles,
} from 'lucide-react'
import { Link } from 'react-router-dom'
import { Badge } from '../components/common/Badge'
import { Button } from '../components/common/Button'
import { SectionHeader } from '../components/common/SectionHeader'
import { HeroIllustration } from '../components/landing/HeroIllustration'
import { MapPreview } from '../components/landing/MapPreview'
import { aiCards, continuityItems, featuredServices, familyRecord, howItWorksSteps, userGroups } from '../data/mockData'

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
              An AI-assisted, GIS-enabled platform helping migrant-worker families maintain continuity of education,
              healthcare, nutrition, protection and social support during intra-state migration.
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
          eyebrow="Continuity preview"
          title="One Place to Check Child Service Continuity"
          description="The continuity overview gives a structured snapshot of the child’s active service profile and follow-up needs."
        />

        <div className="mt-10 grid gap-8 lg:grid-cols-[1.1fr_0.9fr]">
          <div className="rounded-[2rem] border border-slate-200 bg-white p-6 shadow-sm">
            <div className="flex flex-col gap-3 border-b border-slate-200 pb-5 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Child</p>
                <h3 className="mt-1 text-2xl font-bold text-slate-900">{familyRecord.childName}</h3>
              </div>
              <Badge label="Active support plan" tone="success" />
            </div>

            <div className="mt-6 grid gap-4 sm:grid-cols-2">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">Location</p>
                <p className="mt-2 text-lg font-semibold text-slate-800">{familyRecord.currentLocation}</p>
              </div>
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">Previous location</p>
                <p className="mt-2 text-lg font-semibold text-slate-800">{familyRecord.previousLocation}</p>
              </div>
            </div>

            <div className="mt-7 space-y-3">
              {continuityItems.map(({ label, status }) => (
                <div key={label} className="flex items-center justify-between rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm font-medium text-slate-700">
                  <span>{label}</span>
                  {status === 'connected' ? (
                    <Badge label="Connected" tone="success" />
                  ) : status === 'review' ? (
                    <Badge label="Review Needed" tone="warning" />
                  ) : status === 'supported' ? (
                    <Badge label="Supported" tone="info" />
                  ) : (
                    <Badge label="Available" tone="neutral" />
                  )}
                </div>
              ))}
            </div>
          </div>

          <div className="rounded-[2rem] border border-slate-200 bg-slate-900 p-6 text-white shadow-sm">
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">Quick snapshot</p>
            <h3 className="mt-3 text-3xl font-bold">{familyRecord.childName}</h3>
            <div className="mt-6 space-y-4 text-sm text-slate-300">
              <div className="flex items-center justify-between rounded-xl border border-slate-700 bg-slate-800 px-4 py-3">
                <span>Education</span>
                <CheckCircle2 className="h-4 w-4 text-emerald-400" aria-hidden="true" />
              </div>
              <div className="flex items-center justify-between rounded-xl border border-slate-700 bg-slate-800 px-4 py-3">
                <span>Healthcare</span>
                <CheckCircle2 className="h-4 w-4 text-emerald-400" aria-hidden="true" />
              </div>
              <div className="flex items-center justify-between rounded-xl border border-slate-700 bg-slate-800 px-4 py-3">
                <span>Nutrition</span>
                <CircleAlert className="h-4 w-4 text-amber-400" aria-hidden="true" />
              </div>
              <div className="flex items-center justify-between rounded-xl border border-slate-700 bg-slate-800 px-4 py-3">
                <span>Protection</span>
                <CheckCircle2 className="h-4 w-4 text-emerald-400" aria-hidden="true" />
              </div>
            </div>
            <div className="mt-8">
              <Button to="/dashboard" className="w-full justify-center">View Continuity Details</Button>
            </div>
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-4 py-16 sm:px-6 lg:px-8">
        <SectionHeader
          eyebrow="AI support"
          title="Intelligent Support, With Humans in Control"
          description="Future AI capabilities will help guide service coordination, but qualified professionals remain in charge of decisions and actions."
          align="center"
        />

        <div className="mt-10 grid gap-5 md:grid-cols-3">
          {aiCards.map(({ title, description, icon: Icon }) => (
            <article key={title} className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
              <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-sky-50 text-sky-700">
                <Icon className="h-5 w-5" aria-hidden="true" />
              </div>
              <h3 className="mt-5 text-xl font-bold text-slate-900">{title}</h3>
              <p className="mt-3 text-sm leading-6 text-slate-600">{description}</p>
            </article>
          ))}
        </div>

        <div className="mt-6 flex items-start gap-3 rounded-2xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-900">
          <Sparkles className="mt-0.5 h-4 w-4 shrink-0" aria-hidden="true" />
          <p>AI recommendations are intended to support human decision-making, not replace qualified professionals.</p>
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-4 py-16 sm:px-6 lg:px-8">
        <SectionHeader
          eyebrow="GIS preview"
          title="Find Essential Services Near You"
          description="This preview illustrates how geographic insight can help families find nearby schools, clinics, support centres and public services."
        />

        <div className="mt-10 grid gap-8 lg:grid-cols-[1.1fr_0.9fr]">
          <MapPreview />
          <div className="rounded-[2rem] border border-slate-200 bg-white p-6 shadow-sm">
            <div className="flex items-center gap-3">
              <MapPinned className="h-6 w-6 text-emerald-600" aria-hidden="true" />
              <h3 className="text-2xl font-bold text-slate-900">Nearby service discovery</h3>
            </div>
            <div className="mt-6 space-y-4">
              {['School', 'Healthcare', 'Nutrition', 'NGO', 'Government Service'].map((service) => (
                <div key={service} className="flex items-center justify-between rounded-xl border border-slate-200 bg-slate-50 px-4 py-3">
                  <span className="font-medium text-slate-700">{service}</span>
                  <span className="text-sm text-slate-500">Within 2–5 km</span>
                </div>
              ))}
            </div>
            <p className="mt-6 text-sm leading-6 text-slate-600">
              GIS-based service discovery will be connected in a later development phase.
            </p>
          </div>
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
