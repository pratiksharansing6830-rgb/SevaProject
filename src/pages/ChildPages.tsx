import { useEffect, useState, type FormEvent } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { ArrowLeft, Check, Circle, TriangleAlert } from 'lucide-react'
import { useAuth } from '../auth/AuthContext'
import { Button } from '../components/common/Button'
import {
  checkContinuity,
  getChild,
  getContinuity,
  getFamily,
  getServiceRecord,
  listFollowups,
  saveServiceRecord,
  updateFollowup,
  type Child,
  type ContinuitySummary,
  type Family,
  type FollowUp,
  type ServiceRecord,
  type ServiceType,
} from '../api/continuity'

const services: { type: ServiceType; slug: string; label: string }[] = [
  { type: 'EDUCATION', slug: 'education', label: 'Education' },
  { type: 'HEALTHCARE', slug: 'healthcare', label: 'Healthcare' },
  { type: 'NUTRITION', slug: 'nutrition', label: 'Nutrition' },
  { type: 'PROTECTION', slug: 'protection', label: 'Protection' },
  { type: 'WELLBEING', slug: 'wellbeing', label: 'Well-being' },
  { type: 'INCLUSION', slug: 'inclusion', label: 'Inclusion' },
]

const statusText: Record<string, string> = {
  CONNECTED: 'Connected', PENDING: 'Pending', FOLLOW_UP_RECOMMENDED: 'Follow-up recommended',
  NOT_AVAILABLE: 'Not available', REVIEW_REQUIRED: 'Review required',
}

function Message({ children, success = false }: { children: string; success?: boolean }) {
  return <p role="status" className={`rounded-lg border px-4 py-3 text-sm ${success ? 'border-emerald-200 bg-emerald-50 text-emerald-800' : 'border-rose-200 bg-rose-50 text-rose-800'}`}>{children}</p>
}

function StatusIcon({ status }: { status: string }) {
  if (status === 'CONNECTED') return <Check className="h-4 w-4 text-emerald-700" aria-hidden="true" />
  if (status === 'REVIEW_REQUIRED') return <TriangleAlert className="h-4 w-4 text-rose-700" aria-hidden="true" />
  if (status === 'FOLLOW_UP_RECOMMENDED' || status === 'NOT_AVAILABLE') return <TriangleAlert className="h-4 w-4 text-amber-700" aria-hidden="true" />
  return <Circle className="h-4 w-4 text-slate-400" aria-hidden="true" />
}

function StatusLine({ label, status }: { label: string; status: string }) {
  return <div className="flex items-center justify-between gap-4 border-b border-slate-100 py-3 last:border-0">
    <span className="text-sm font-medium text-slate-800">{label}</span>
    <span className="flex items-center gap-2 text-sm text-slate-600"><StatusIcon status={status} />{statusText[status] || status.replaceAll('_', ' ')}</span>
  </div>
}

export function ChildProfilePage() {
  const { childId = '' } = useParams()
  const { token } = useAuth()
  const [child, setChild] = useState<Child | null>(null)
  const [family, setFamily] = useState<Family | null>(null)
  const [summary, setSummary] = useState<ContinuitySummary | null>(null)
  const [records, setRecords] = useState<Record<string, ServiceRecord | null>>({})
  const [error, setError] = useState('')

  useEffect(() => {
    if (!token) return
    void Promise.all([
      getChild(childId, token), getContinuity(childId, token),
      ...services.map((service) => getServiceRecord(childId, service.slug, token)),
    ]).then(async ([childResult, continuityResult, ...serviceResults]) => {
      const childValue = childResult as Child
      setChild(childValue)
      setSummary(continuityResult as ContinuitySummary)
      setRecords(Object.fromEntries(services.map((service, index) => [service.slug, serviceResults[index] as ServiceRecord | null])))
      setFamily(await getFamily(childValue.family_id, token))
    }).catch((cause: unknown) => setError(cause instanceof Error ? cause.message : 'Could not load this child profile.'))
  }, [childId, token])

  if (error) return <div className="mx-auto max-w-5xl px-4 py-10"><Message>{error}</Message></div>
  if (!child || !summary) return <p className="py-16 text-center text-slate-600">Loading child profile…</p>
  const education = records.education
  const healthcare = records.healthcare
  const nutrition = records.nutrition
  const wellbeing = records.wellbeing
  const protection = records.protection
  const inclusion = records.inclusion
  return <div className="mx-auto max-w-7xl px-4 py-10 sm:px-6 lg:px-8">
    <Link to={family ? `/family/${family.id}` : '/family'} className="inline-flex items-center gap-2 text-sm font-semibold text-teal-800 hover:underline"><ArrowLeft className="h-4 w-4" aria-hidden="true" /> Family dashboard</Link>
    <header className="mt-5 flex flex-col justify-between gap-4 border-b border-slate-200 pb-6 md:flex-row md:items-end">
      <div><p className="text-sm font-semibold text-teal-700">Child profile</p><h1 className="mt-2 text-3xl font-bold text-slate-900">{child.first_name} {child.last_name}</h1><p className="mt-2 text-slate-600">Class {child.current_class || 'Not recorded'} · {child.preferred_language}</p></div>
      <Button to={`/children/${child.id}/continuity`}>Open continuity checklist</Button>
    </header>
    <div className="mt-8 grid gap-8 lg:grid-cols-[0.9fr_1.1fr]">
      <section className="space-y-6">
        <div className="rounded-2xl border border-slate-200 bg-white p-5">
          <h2 className="text-lg font-semibold text-slate-900">Basic information</h2>
          <dl className="mt-4 grid grid-cols-2 gap-x-5 gap-y-4 text-sm">
            <ProfileValue label="Date of birth" value={child.date_of_birth} />
            <ProfileValue label="Gender" value={child.gender.replaceAll('_', ' ')} />
            <ProfileValue label="Current class" value={child.current_class || 'Not recorded'} />
            <ProfileValue label="Language" value={child.preferred_language} />
            <div className="col-span-2"><ProfileValue label="Inclusion requirement" value={child.disability_or_inclusion_requirement || 'None recorded'} /></div>
          </dl>
        </div>
        <section className="rounded-2xl border border-slate-200 bg-white p-5">
          <div className="flex items-center justify-between"><h2 className="text-lg font-semibold text-slate-900">Education</h2><EditLink childId={child.id} slug="education" /></div>
          <dl className="mt-4 grid grid-cols-2 gap-x-5 gap-y-4 text-sm"><ProfileValue label="School" value={str(education?.current_school_name)} /><ProfileValue label="Location" value={str(education?.current_school_location)} /><ProfileValue label="Enrollment" value={statusText[str(education?.enrollment_status)] || 'Not recorded'} /><ProfileValue label="Transfer" value={statusText[str(education?.transfer_status)] || 'Not recorded'} /></dl>
        </section>
        <section className="rounded-2xl border border-slate-200 bg-white p-5">
          <div className="flex items-center justify-between"><h2 className="text-lg font-semibold text-slate-900">Healthcare</h2><EditLink childId={child.id} slug="healthcare" /></div>
          <dl className="mt-4 grid grid-cols-2 gap-x-5 gap-y-4 text-sm"><ProfileValue label="Provider" value={str(healthcare?.healthcare_provider_name)} /><ProfileValue label="Location" value={str(healthcare?.healthcare_location)} /><ProfileValue label="Continuity" value={statusText[str(healthcare?.continuity_status)] || 'Not recorded'} /><ProfileValue label="Next follow-up" value={str(healthcare?.next_followup_date)} /></dl>
        </section>
        <section className="rounded-2xl border border-slate-200 bg-white p-5">
          <div className="flex items-center justify-between"><h2 className="text-lg font-semibold text-slate-900">Nutrition</h2><EditLink childId={child.id} slug="nutrition" /></div>
          <dl className="mt-4 grid grid-cols-2 gap-x-5 gap-y-4 text-sm"><ProfileValue label="Service" value={str(nutrition?.nutrition_service_name)} /><ProfileValue label="Location" value={str(nutrition?.nutrition_service_location)} /><ProfileValue label="Status" value={statusText[str(nutrition?.service_status)] || 'Not recorded'} /><ProfileValue label="Next service" value={str(nutrition?.next_service_date)} /></dl>
        </section>
        <section className="grid gap-4 sm:grid-cols-3">
          <CompactService title="Well-being" detail={statusText[str(wellbeing?.support_status)] || 'Not recorded'} edit={`/children/${child.id}/wellbeing`} />
          <CompactService title="Protection" detail={statusText[str(protection?.protection_status)] || 'Not recorded'} edit={`/children/${child.id}/protection`} />
          <CompactService title="Inclusion" detail={statusText[str(inclusion?.support_status)] || 'Not recorded'} edit={`/children/${child.id}/inclusion`} />
        </section>
      </section>
      <aside className="space-y-6">
        <section className="rounded-2xl border border-slate-200 bg-white p-5">
          <div className="flex items-start justify-between gap-4"><div><p className="text-sm text-slate-500">Service continuity</p><h2 className="mt-1 text-xl font-semibold text-slate-900">Six-service checklist</h2></div><StatusPill status={summary.overall_status} /></div>
          <div className="mt-4">{services.map((service) => <StatusLine key={service.type} label={service.label} status={summary.services.find((item) => item.service_type === service.type)?.status || 'PENDING'} />)}</div>
          <Link to={`/children/${child.id}/continuity`} className="mt-4 inline-block text-sm font-semibold text-teal-800 hover:underline">View checklist and actions</Link>
        </section>
        <FollowUpList familyId={child.family_id} token={token || ''} />
        {family && <section className="rounded-xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-600"><span className="font-medium text-slate-800">Family:</span> {family.family_name} · {family.current_village_or_city}, {family.current_district}</section>}
      </aside>
    </div>
  </div>
}

export function ContinuityPage() {
  const { childId = '' } = useParams()
  const { token } = useAuth()
  const [child, setChild] = useState<Child | null>(null)
  const [summary, setSummary] = useState<ContinuitySummary | null>(null)
  const [followups, setFollowups] = useState<FollowUp[]>([])
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  const [updatingFollowup, setUpdatingFollowup] = useState<string | null>(null)
  const [message, setMessage] = useState('')

  useEffect(() => {
    if (!token) return
    let active = true
    void fetchContinuityPageData(childId, token).then((data) => {
      if (!active) return
      setChild(data.child); setSummary(data.summary); setFollowups(data.followups)
    }).catch((cause: unknown) => {
      if (active) setError(cause instanceof Error ? cause.message : 'Could not load continuity.')
    })
    return () => { active = false }
  }, [childId, token])

  async function refreshData() {
    if (!token) return
    const data = await fetchContinuityPageData(childId, token)
    setChild(data.child); setSummary(data.summary); setFollowups(data.followups)
  }

  async function runCheck() {
    if (!token) return
    setBusy(true); setError(''); setMessage('')
    try { await checkContinuity(childId, token); await refreshData(); setMessage('Service continuity checklist updated.') }
    catch (cause) { setError(cause instanceof Error ? cause.message : 'Could not check service continuity.') }
    finally { setBusy(false) }
  }
  async function completeFollowup(followupId: string) {
    if (!token) return
    setUpdatingFollowup(followupId); setError('')
    try { await updateFollowup(followupId, { status: 'COMPLETED' }, token); await refreshData() }
    catch (cause) { setError(cause instanceof Error ? cause.message : 'Could not update this follow-up.') }
    finally { setUpdatingFollowup(null) }
  }
  if (error) return <div className="mx-auto max-w-5xl px-4 py-10"><Message>{error}</Message></div>
  if (!child || !summary) return <p className="py-16 text-center text-slate-600">Loading continuity checklist…</p>
  const activeFollowups = followups.filter((item) => item.status === 'OPEN' || item.status === 'IN_PROGRESS')
  return <div className="mx-auto max-w-5xl px-4 py-10 sm:px-6">
    <Link to={`/children/${child.id}`} className="inline-flex items-center gap-2 text-sm font-semibold text-teal-800 hover:underline"><ArrowLeft className="h-4 w-4" aria-hidden="true" /> Child profile</Link>
    <header className="mt-5 flex flex-col justify-between gap-4 border-b border-slate-200 pb-6 sm:flex-row sm:items-end"><div><p className="text-sm font-semibold text-teal-700">Service continuity</p><h1 className="mt-2 text-3xl font-bold text-slate-900">{child.first_name} {child.last_name}</h1><p className="mt-2 text-slate-600">Review connections and record follow-up with a human reviewer.</p></div><button onClick={() => void runCheck()} disabled={busy} className="rounded-lg bg-teal-700 px-4 py-2.5 font-semibold text-white hover:bg-teal-800 disabled:opacity-60">{busy ? 'Checking…' : 'Check service continuity'}</button></header>
    {message && <div className="mt-5"><Message success>{message}</Message></div>}
    <section className="mt-7 rounded-2xl border border-slate-200 bg-white p-5 sm:p-7">
      <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center"><div><p className="text-sm text-slate-500">Overall status</p><h2 className="mt-1 text-2xl font-semibold text-slate-900">{statusText[summary.overall_status]}</h2></div><StatusPill status={summary.overall_status} /></div>
      <div className="mt-5 divide-y divide-slate-100 border-y border-slate-100">{services.map((service) => {
        const record = summary.services.find((item) => item.service_type === service.type)
        return <div key={service.type} className="flex flex-col gap-3 py-4">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div className="flex items-center gap-3"><StatusIcon status={record?.status || 'PENDING'} /><div><p className="font-medium text-slate-900">{service.label}</p>{record?.due_date && <p className="mt-0.5 text-xs text-slate-500">Follow-up due {record.due_date}</p>}</div></div>
            <div className="flex items-center gap-4"><span className="text-sm text-slate-600">{statusText[record?.status || 'PENDING']}</span><Link to={`/children/${child.id}/${service.slug}`} className="text-sm font-semibold text-teal-800 hover:underline">Update</Link></div>
          </div>
          {record?.reason && <p className="text-sm text-slate-600">{record.reason}</p>}
        </div>
      })}</div>
      <p className="mt-4 text-sm text-slate-600">{activeFollowups.length} services require follow-up.</p>
    </section>
    <section className="mt-7"><h2 className="text-xl font-semibold text-slate-900">Follow-up actions</h2>{activeFollowups.length ? <div className="mt-3 divide-y divide-slate-200 border-y border-slate-200 bg-white">{activeFollowups.map((item) => <div key={item.id} className="flex flex-col justify-between gap-3 py-4 sm:flex-row sm:items-center"><div><h3 className="font-medium text-slate-900">{item.title}</h3>{item.description && <p className="mt-1 text-sm text-slate-600">{item.description}</p>}<p className="mt-1 text-xs text-slate-500">{item.status.replace('_', ' ')}{item.due_date ? ` · Due ${item.due_date}` : ''}</p></div><button type="button" onClick={() => void completeFollowup(item.id)} disabled={updatingFollowup === item.id} className="inline-flex items-center justify-center gap-2 self-start rounded-lg border border-slate-300 px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50 disabled:opacity-60 sm:self-auto"><Check className="h-4 w-4" aria-hidden="true" />{updatingFollowup === item.id ? 'Updating…' : 'Mark complete'}</button></div>)}</div> : <p className="mt-3 rounded-xl border border-slate-200 bg-white p-5 text-sm text-slate-600">No open follow-up items.</p>}</section>
  </div>
}

async function fetchContinuityPageData(childId: string, token: string): Promise<{ child: Child; summary: ContinuitySummary; followups: FollowUp[] }> {
  const child = await getChild(childId, token)
  const [summary, followups] = await Promise.all([getContinuity(childId, token), listFollowups(child.family_id, token)])
  return { child, summary, followups }
}

function FollowUpList({ familyId, token }: { familyId: string; token: string }) {
  const [items, setItems] = useState<FollowUp[]>([])
  useEffect(() => { void listFollowups(familyId, token).then(setItems).catch(() => setItems([])) }, [familyId, token])
  const open = items.filter((item) => item.status === 'OPEN' || item.status === 'IN_PROGRESS')
  return <section className="rounded-2xl border border-slate-200 bg-white p-5"><h2 className="font-semibold text-slate-900">Follow-up actions</h2>{open.length ? <ul className="mt-3 divide-y divide-slate-100">{open.slice(0, 4).map((item) => <li key={item.id} className="py-3"><p className="text-sm font-medium text-slate-800">{item.title}</p><p className="mt-1 text-xs text-slate-500">{item.due_date ? `Due ${item.due_date}` : item.status.replace('_', ' ')}</p></li>)}</ul> : <p className="mt-3 text-sm text-slate-600">No open actions.</p>}</section>
}

function ProfileValue({ label, value }: { label: string; value: string }) {
  return <div><dt className="text-xs font-semibold uppercase tracking-wide text-slate-500">{label}</dt><dd className="mt-1 text-slate-800">{value}</dd></div>
}

function EditLink({ childId, slug }: { childId: string; slug: string }) {
  return <Link to={`/children/${childId}/${slug}`} className="text-sm font-semibold text-teal-800 hover:underline">Edit</Link>
}

function CompactService({ title, detail, edit }: { title: string; detail: string; edit: string }) {
  return <div className="rounded-xl border border-slate-200 bg-white p-4"><div className="flex items-start justify-between gap-2"><h3 className="text-sm font-semibold text-slate-900">{title}</h3><Link to={edit} className="text-xs font-semibold text-teal-800 hover:underline">Edit</Link></div><p className="mt-3 text-sm text-slate-600">{detail}</p></div>
}

function StatusPill({ status }: { status: string }) {
  const color = status === 'CONNECTED' ? 'bg-emerald-50 text-emerald-800' : status === 'REVIEW_REQUIRED' ? 'bg-rose-50 text-rose-800' : 'bg-amber-50 text-amber-800'
  return <span className={`inline-flex items-center rounded-full px-3 py-1 text-sm font-medium ${color}`}><StatusIcon status={status} /><span className="ml-2">{statusText[status] || status}</span></span>
}

function str(value: unknown): string {
  return typeof value === 'string' && value ? value : 'Not recorded'
}

type InputField = { name: string; label: string; type: 'text' | 'date' | 'textarea' | 'select' | 'checkbox'; options?: string[]; defaultValue?: string | boolean }
type ServiceConfig = { title: string; fields: InputField[] }
const serviceConfigs: Record<string, ServiceConfig> = {
  education: { title: 'Education continuity', fields: [
    { name: 'previous_school_name', label: 'Previous school', type: 'text' }, { name: 'previous_school_location', label: 'Previous school location', type: 'text' },
    { name: 'current_school_name', label: 'Current school', type: 'text' }, { name: 'current_school_location', label: 'Current school location', type: 'text' },
    { name: 'current_class', label: 'Current class', type: 'text' }, { name: 'enrollment_status', label: 'Enrollment status', type: 'select', options: ['ENROLLED', 'PENDING', 'NOT_ENROLLED', 'UNKNOWN'], defaultValue: 'UNKNOWN' },
    { name: 'transfer_status', label: 'Transfer status', type: 'select', options: ['COMPLETED', 'PENDING', 'NOT_STARTED', 'NOT_REQUIRED'], defaultValue: 'NOT_STARTED' }, { name: 'last_attendance_date', label: 'Last attendance date', type: 'date' }, { name: 'notes', label: 'Notes', type: 'textarea' },
  ] },
  healthcare: { title: 'Healthcare continuity', fields: [
    { name: 'healthcare_provider_name', label: 'Provider', type: 'text' }, { name: 'healthcare_location', label: 'Location', type: 'text' },
    { name: 'continuity_status', label: 'Continuity status', type: 'select', options: ['CONNECTED', 'PENDING', 'FOLLOW_UP_RECOMMENDED', 'NOT_AVAILABLE'], defaultValue: 'PENDING' },
    { name: 'last_followup_date', label: 'Last follow-up', type: 'date' }, { name: 'next_followup_date', label: 'Next follow-up', type: 'date' }, { name: 'notes', label: 'Notes', type: 'textarea' },
  ] },
  nutrition: { title: 'Nutrition continuity', fields: [
    { name: 'nutrition_service_name', label: 'Nutrition service', type: 'text' }, { name: 'nutrition_service_location', label: 'Location', type: 'text' },
    { name: 'service_status', label: 'Service status', type: 'select', options: ['CONNECTED', 'PENDING', 'FOLLOW_UP_RECOMMENDED', 'NOT_AVAILABLE'], defaultValue: 'PENDING' },
    { name: 'last_service_date', label: 'Last service date', type: 'date' }, { name: 'next_service_date', label: 'Next service date', type: 'date' }, { name: 'notes', label: 'Notes', type: 'textarea' },
  ] },
  wellbeing: { title: 'Well-being support', fields: [
    { name: 'support_status', label: 'Support status', type: 'select', options: ['CONNECTED', 'PENDING', 'FOLLOW_UP_RECOMMENDED', 'NOT_AVAILABLE'], defaultValue: 'PENDING' }, { name: 'support_provider', label: 'Support provider', type: 'text' },
    { name: 'last_followup_date', label: 'Last follow-up', type: 'date' }, { name: 'next_followup_date', label: 'Next follow-up', type: 'date' }, { name: 'notes', label: 'Notes', type: 'textarea' },
  ] },
  protection: { title: 'Protection support review', fields: [
    { name: 'protection_status', label: 'Review status', type: 'select', options: ['NO_ACTION_RECORDED', 'FOLLOW_UP_RECOMMENDED', 'SUPPORT_CONNECTED', 'REVIEW_REQUIRED'], defaultValue: 'NO_ACTION_RECORDED' },
    { name: 'support_contact_available', label: 'Support contact available', type: 'checkbox', defaultValue: false }, { name: 'last_review_date', label: 'Last review date', type: 'date' },
    { name: 'followup_required', label: 'Follow-up required', type: 'checkbox', defaultValue: false }, { name: 'notes', label: 'Notes', type: 'textarea' },
  ] },
  inclusion: { title: 'Inclusion support', fields: [
    { name: 'requirement_present', label: 'Support requirement present', type: 'checkbox', defaultValue: false },
    { name: 'support_type', label: 'Support type', type: 'select', options: ['ACCESSIBILITY', 'LEARNING_SUPPORT', 'MOBILITY_SUPPORT', 'COMMUNICATION_SUPPORT', 'OTHER'], defaultValue: 'OTHER' },
    { name: 'support_status', label: 'Support status', type: 'select', options: ['CONNECTED', 'PENDING', 'FOLLOW_UP_RECOMMENDED', 'NOT_AVAILABLE'], defaultValue: 'PENDING' }, { name: 'notes', label: 'Notes', type: 'textarea' },
  ] },
}

export function ChildServicePage() {
  const { childId = '', service = '' } = useParams()
  const { token } = useAuth()
  const navigate = useNavigate()
  const config = serviceConfigs[service]
  const [child, setChild] = useState<Child | null>(null)
  const [record, setRecord] = useState<ServiceRecord | null>(null)
  const [values, setValues] = useState<Record<string, string | boolean>>({})
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)

  useEffect(() => {
    if (!token || !config) return
    void Promise.all([getChild(childId, token), getServiceRecord(childId, service, token)]).then(([childValue, recordValue]) => {
      setChild(childValue); setRecord(recordValue)
      setValues(Object.fromEntries(config.fields.map((field) => [field.name, recordValue?.[field.name] ?? field.defaultValue ?? (field.type === 'checkbox' ? false : '')])) as Record<string, string | boolean>)
    }).catch((cause: unknown) => setError(cause instanceof Error ? cause.message : 'Could not load this service record.'))
  }, [childId, config, service, token])

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); if (!token) return
    setBusy(true); setError(''); setSuccess(false)
    const payload = Object.fromEntries(Object.entries(values).map(([key, value]) => [key, value === '' ? null : value]))
    try { await saveServiceRecord(childId, service, typeof record?.id === 'string' ? record.id : undefined, payload, token); setSuccess(true); navigate(`/children/${childId}`) }
    catch (cause) { setError(cause instanceof Error ? cause.message : 'Could not save this service record.') }
    finally { setBusy(false) }
  }
  if (!config) return <div className="mx-auto max-w-3xl px-4 py-10"><Message>Service type not found.</Message></div>
  return <div className="mx-auto max-w-3xl px-4 py-10 sm:px-6">
    <Link to={`/children/${childId}`} className="inline-flex items-center gap-2 text-sm font-semibold text-teal-800 hover:underline"><ArrowLeft className="h-4 w-4" aria-hidden="true" /> Child profile</Link>
    <header className="my-6 border-b border-slate-200 pb-5"><p className="text-sm font-semibold text-teal-700">{child ? `${child.first_name} ${child.last_name}` : 'Child service'}</p><h1 className="mt-2 text-3xl font-bold text-slate-900">{config.title}</h1></header>
    {error && <div className="mb-5"><Message>{error}</Message></div>}{success && <div className="mb-5"><Message success>Service record saved.</Message></div>}
    {!child ? <p className="py-8 text-center text-slate-600">Loading service record…</p> : <form onSubmit={submit} className="space-y-5 rounded-2xl border border-slate-200 bg-white p-6">
      <div className="grid gap-5 sm:grid-cols-2">{config.fields.map((field) => <label key={field.name} className={`${field.type === 'textarea' ? 'sm:col-span-2' : ''} ${field.type === 'checkbox' ? 'flex items-center gap-3 rounded-lg border border-slate-200 px-3 py-3' : ''}`}>
        {field.type === 'checkbox' ? <><input type="checkbox" checked={Boolean(values[field.name])} onChange={(event) => setValues((current) => ({ ...current, [field.name]: event.target.checked }))} className="h-4 w-4 rounded border-slate-300 text-teal-700 focus:ring-teal-600" /><span className="text-sm font-medium text-slate-800">{field.label}</span></> : <>
          <span className="mb-1.5 block text-sm font-medium text-slate-800">{field.label}</span>
          {field.type === 'select' ? <select value={String(values[field.name] ?? '')} onChange={(event) => setValues((current) => ({ ...current, [field.name]: event.target.value }))} className="w-full rounded-lg border border-slate-300 px-3 py-2.5">{field.options?.map((option) => <option key={option} value={option}>{option.replaceAll('_', ' ').toLowerCase().replace(/\b\w/g, (char) => char.toUpperCase())}</option>)}</select> : field.type === 'textarea' ? <textarea maxLength={2000} rows={4} value={String(values[field.name] ?? '')} onChange={(event) => setValues((current) => ({ ...current, [field.name]: event.target.value }))} className="w-full rounded-lg border border-slate-300 px-3 py-2.5" /> : <input type={field.type} maxLength={160} value={String(values[field.name] ?? '')} onChange={(event) => setValues((current) => ({ ...current, [field.name]: event.target.value }))} className="w-full rounded-lg border border-slate-300 px-3 py-2.5" />}
        </>}
      </label>)}</div>
      <div className="flex justify-end gap-3 border-t border-slate-100 pt-5"><Button variant="outline" to={`/children/${childId}`}>Cancel</Button><button disabled={busy} className="rounded-lg bg-teal-700 px-5 py-2.5 font-semibold text-white hover:bg-teal-800 disabled:opacity-60">{busy ? 'Saving…' : 'Save service record'}</button></div>
    </form>}
  </div>
}