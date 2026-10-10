import { useEffect, useState, type FormEvent } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { ArrowLeft, Check, Circle, TriangleAlert } from 'lucide-react'
import { useAuth } from '../auth/AuthContext'
import { Button } from '../components/common/Button'
import { DestinationServiceDiscovery } from '../components/DestinationServiceDiscovery'
import type { NearbyService } from '../api/services'
import {
  checkContinuity,
  createFollowup,
  getChild,
  getContinuity,
  getFamily,
  getServiceRecord,
  listFollowups,
  listMigrations,
  saveServiceRecord,
  updateFollowup,
  updateContinuity,
  updateChild,
  type Child,
  type ContinuitySummary,
  type Family,
  type FollowUp,
  type FollowUpPayload,
  type ServiceContinuity,
  type ServiceRecord,
  type ServiceType,
  type ConfirmationMethod,
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
  CONNECTED: 'Connected and confirmed', PENDING: 'Support pending', FOLLOW_UP_REQUIRED: 'Follow-up required',
  SUPPORT_NOT_REQUIRED: 'Support not required', FOLLOW_UP_RECOMMENDED: 'Follow-up recommended',
  NOT_AVAILABLE: 'Not available', REVIEW_REQUIRED: 'Review required',
}
const confirmationMethods: { value: ConfirmationMethod; label: string }[] = [
  { value: 'FAMILY_REPORT', label: 'Family report' },
  { value: 'SERVICE_PROVIDER', label: 'Service provider' },
  { value: 'DOCUMENT_REVIEW', label: 'Document review' },
  { value: 'IN_PERSON', label: 'In person' },
  { value: 'OTHER', label: 'Other' },
]

type ContactDraft = {
  record: ServiceContinuity
  followup?: FollowUp
  providerName: string
  contactInformation: string
  attempt: string
  response: string
  barrier: string
  nextSteps: string
  dueDate: string
  status: 'OPEN' | 'IN_PROGRESS' | 'COMPLETED'
}

function parseContactNotes(description: string | null) {
  const values: Record<string, string> = {}
  for (const line of description?.split('\n') || []) {
    const match = line.match(/^(Potential service|Contact details|Contact attempt \/ referral|Provider response|Barrier|Next steps):\s*(.*)$/)
    if (match) values[match[1]] = match[2]
  }
  return values
}

function contactDescription(draft: ContactDraft) {
  return [
    `Potential service: ${draft.providerName}`,
    `Contact details: ${draft.contactInformation}`,
    `Contact attempt / referral: ${draft.attempt}`,
    `Provider response: ${draft.response}`,
    `Barrier: ${draft.barrier}`,
    `Next steps: ${draft.nextSteps}`,
  ].join('\n')
}

function Message({ children, success = false }: { children: string; success?: boolean }) {
  return <p role="status" className={`rounded-lg border px-4 py-3 text-sm ${success ? 'border-emerald-200 bg-emerald-50 text-emerald-800' : 'border-rose-200 bg-rose-50 text-rose-800'}`}>{children}</p>
}

function StatusIcon({ status }: { status: string }) {
  if (status === 'CONNECTED') return <Check className="h-4 w-4 text-emerald-700" aria-hidden="true" />
  if (status === 'REVIEW_REQUIRED') return <TriangleAlert className="h-4 w-4 text-rose-700" aria-hidden="true" />
  if (status === 'FOLLOW_UP_REQUIRED' || status === 'FOLLOW_UP_RECOMMENDED' || status === 'NOT_AVAILABLE') return <TriangleAlert className="h-4 w-4 text-amber-700" aria-hidden="true" />
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
  const [editingChild, setEditingChild] = useState(false)
  const [savingChild, setSavingChild] = useState(false)
  const [childError, setChildError] = useState('')
  const [childMessage, setChildMessage] = useState('')
  const [childForm, setChildForm] = useState({
    first_name: '',
    last_name: '',
    date_of_birth: '',
    gender: 'UNDISCLOSED',
    education_status: 'UNKNOWN',
    current_class: '',
    preferred_language: 'English',
    disability_or_inclusion_requirement: '',
  })

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

  function beginChildEdit() {
    if (!child) return
    setChildForm({
      first_name: child.first_name,
      last_name: child.last_name,
      date_of_birth: child.date_of_birth,
      gender: child.gender,
      education_status: child.education_status,
      current_class: child.current_class || '',
      preferred_language: child.preferred_language,
      disability_or_inclusion_requirement: child.disability_or_inclusion_requirement || '',
    })
    setChildError('')
    setChildMessage('')
    setEditingChild(true)
  }

  async function saveChild(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (!child || !token) return
    setSavingChild(true)
    setChildError('')
    setChildMessage('')
    try {
      setChild(await updateChild(child.id, childForm, token))
      setEditingChild(false)
      setChildMessage('Child profile updated.')
    } catch (cause) {
      setChildError(cause instanceof Error ? cause.message : 'Could not update this child profile.')
    } finally {
      setSavingChild(false)
    }
  }

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
      <div className="flex flex-wrap gap-2">
        <button type="button" onClick={beginChildEdit} className="rounded-lg border border-slate-300 px-4 py-2.5 text-sm font-semibold text-slate-700">Edit child profile</button>
        <Button to={`/children/${child.id}/continuity`}>Open continuity checklist</Button>
      </div>
    </header>
    {childMessage && <div className="mt-5"><Message success>{childMessage}</Message></div>}
    {editingChild && <form onSubmit={saveChild} className="mt-5 grid gap-4 rounded-2xl border border-slate-200 bg-white p-5 sm:grid-cols-2">
      {childError && <div className="sm:col-span-2"><Message>{childError}</Message></div>}
      <ProfileEditField label="First name" value={childForm.first_name} required onChange={(value) => setChildForm((current) => ({ ...current, first_name: value }))} />
      <ProfileEditField label="Last name" value={childForm.last_name} required onChange={(value) => setChildForm((current) => ({ ...current, last_name: value }))} />
      <ProfileEditField label="Date of birth" type="date" value={childForm.date_of_birth} required onChange={(value) => setChildForm((current) => ({ ...current, date_of_birth: value }))} />
      <ProfileEditSelect label="Gender" value={childForm.gender} options={['UNDISCLOSED', 'FEMALE', 'MALE', 'NON_BINARY']} onChange={(value) => setChildForm((current) => ({ ...current, gender: value }))} />
      <ProfileEditSelect label="Education status" value={childForm.education_status} options={['UNKNOWN', 'ENROLLED', 'PENDING', 'NOT_ENROLLED']} onChange={(value) => setChildForm((current) => ({ ...current, education_status: value }))} />
      <ProfileEditField label="Current class" value={childForm.current_class} onChange={(value) => setChildForm((current) => ({ ...current, current_class: value }))} />
      <ProfileEditSelect label="Preferred language" value={childForm.preferred_language} options={['English', 'Marathi', 'Hindi']} onChange={(value) => setChildForm((current) => ({ ...current, preferred_language: value }))} />
      <label className="sm:col-span-2"><span className="mb-1 block text-sm font-medium text-slate-800">Inclusion requirement</span><textarea maxLength={500} value={childForm.disability_or_inclusion_requirement} onChange={(event) => setChildForm((current) => ({ ...current, disability_or_inclusion_requirement: event.target.value }))} rows={3} className="w-full rounded-lg border border-slate-300 px-3 py-2.5" /></label>
      <div className="sm:col-span-2 flex justify-end gap-3">
        <button type="button" onClick={() => setEditingChild(false)} className="rounded-lg border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-700">Cancel</button>
        <button type="submit" disabled={savingChild} className="rounded-lg bg-teal-700 px-4 py-2 text-sm font-semibold text-white disabled:opacity-60">{savingChild ? 'Saving…' : 'Save child'}</button>
      </div>
    </form>}
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
          <dl className="mt-4 grid grid-cols-2 gap-x-5 gap-y-4 text-sm"><ProfileValue label="School" value={str(education?.current_school_name)} /><ProfileValue label="Location" value={str(education?.current_school_location)} /><ProfileValue label="Enrollment" value={educationStatusText(education?.enrollment_status)} /><ProfileValue label="Transfer" value={educationStatusText(education?.transfer_status)} /></dl>
        </section>
        <section className="rounded-2xl border border-slate-200 bg-white p-5">
          <div className="flex items-center justify-between"><h2 className="text-lg font-semibold text-slate-900">Healthcare</h2><EditLink childId={child.id} slug="healthcare" /></div>
          <dl className="mt-4 grid grid-cols-2 gap-x-5 gap-y-4 text-sm"><ProfileValue label="Provider" value={str(healthcare?.healthcare_provider_name)} /><ProfileValue label="Location" value={str(healthcare?.healthcare_location)} /><ProfileValue label="Recorded status" value={sourceStatusText(healthcare?.continuity_status)} /><ProfileValue label="Next follow-up" value={str(healthcare?.next_followup_date)} /></dl>
        </section>
        <section className="rounded-2xl border border-slate-200 bg-white p-5">
          <div className="flex items-center justify-between"><h2 className="text-lg font-semibold text-slate-900">Nutrition</h2><EditLink childId={child.id} slug="nutrition" /></div>
          <dl className="mt-4 grid grid-cols-2 gap-x-5 gap-y-4 text-sm"><ProfileValue label="Service" value={str(nutrition?.nutrition_service_name)} /><ProfileValue label="Location" value={str(nutrition?.nutrition_service_location)} /><ProfileValue label="Recorded status" value={sourceStatusText(nutrition?.service_status)} /><ProfileValue label="Next service" value={str(nutrition?.next_service_date)} /></dl>
        </section>
        <section className="grid gap-4 sm:grid-cols-3">
          <CompactService title="Well-being" detail={sourceStatusText(wellbeing?.support_status)} edit={`/children/${child.id}/wellbeing`} />
          <CompactService title="Protection" detail={sourceStatusText(protection?.protection_status)} edit={`/children/${child.id}/protection`} />
          <CompactService title="Inclusion" detail={sourceStatusText(inclusion?.support_status)} edit={`/children/${child.id}/inclusion`} />
        </section>
      </section>
      <aside className="space-y-6">
        <section className="rounded-2xl border border-slate-200 bg-white p-5">
          <div className="flex items-start justify-between gap-4"><div><p className="text-sm text-slate-500">Service continuity</p><h2 className="mt-1 text-xl font-semibold text-slate-900">Six-service checklist</h2></div><StatusPill status={summary.overall_status} /></div>
          <div className="mt-4">{services.map((service) => <StatusLine key={service.type} label={service.label} status={summary.services.find((item) => item.service_type === service.type)?.status || 'PENDING'} />)}</div>
          <Link to={`/children/${child.id}/continuity`} className="mt-4 inline-block text-sm font-semibold text-teal-800 hover:underline">View checklist and actions</Link>
        </section>
        <FollowUpList key={token} familyId={child.family_id} token={token || ''} />
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
  const [confirmationMethod, setConfirmationMethod] = useState<ConfirmationMethod>('FAMILY_REPORT')
  const [supportingReference, setSupportingReference] = useState('')
  const [contactDraft, setContactDraft] = useState<ContactDraft | null>(null)
  const [contactError, setContactError] = useState('')
  const [savingContact, setSavingContact] = useState(false)

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

  // Destination place names (city / taluka / district) used only to pick a map search point.
  const [destination, setDestination] = useState<string[]>([])
  const [destinationDistrict, setDestinationDistrict] = useState('')
  const familyId = child?.family_id
  useEffect(() => {
    if (!token || !familyId) return
    let active = true
    void Promise.all([listMigrations(familyId, token), getFamily(familyId, token)])
      .then(([items, family]) => {
        if (!active) return
        const migrationId = summary?.services[0]?.migration_id
        const current = migrationId ? items.find((item) => item.id === migrationId) : undefined
        setDestination(current
          ? [current.to_location, current.to_taluka, current.to_district]
          : [family.current_village_or_city, family.current_taluka, family.current_district])
        setDestinationDistrict(current?.to_district || family.current_district)
      })
      .catch((cause: unknown) => {
        if (active) setError(cause instanceof Error ? cause.message : 'Could not load the destination location.')
      })
    return () => { active = false }
  }, [familyId, token, summary?.services])

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
  async function confirmOutcome(recordId: string, status: 'CONNECTED' | 'SUPPORT_NOT_REQUIRED') {
    if (!token) return
    setBusy(true); setError(''); setMessage('')
    try {
      await updateContinuity(recordId, {
        status,
        confirmation_method: confirmationMethod,
        ...(supportingReference.trim() ? { supporting_reference: supportingReference.trim() } : {}),
      }, token)
      await refreshData()
      setMessage('Service outcome confirmed and recorded.')
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : 'Could not confirm this service outcome.')
    } finally {
      setBusy(false)
    }
  }
  function beginContact(record: ServiceContinuity, service?: NearbyService) {
    setContactError('')
    const serviceLabel = record.service_type.replaceAll('_', ' ').toLowerCase().replace(/\b\w/g, (char) => char.toUpperCase())
    const defaultFollowup = followups.find((item) =>
      item.service_continuity_id === record.id &&
      item.title === `${serviceLabel} continuity follow-up` &&
      (item.status === 'OPEN' || item.status === 'IN_PROGRESS'),
    )
    setContactDraft({
      record,
      followup: defaultFollowup,
      providerName: service ? `${service.service_name} — ${service.organization_name}` : '',
      contactInformation: service?.contact_information || '',
      attempt: '',
      response: '',
      barrier: '',
      nextSteps: '',
      dueDate: defaultFollowup?.due_date || '',
      status: defaultFollowup?.status === 'IN_PROGRESS' ? 'IN_PROGRESS' : 'OPEN',
    })
  }
  function editContact(record: ServiceContinuity, followup: FollowUp) {
    setContactError('')
    const parsed = parseContactNotes(followup.description)
    setContactDraft({
      record,
      followup,
      providerName: parsed['Potential service'] || '',
      contactInformation: parsed['Contact details'] || '',
      attempt: parsed['Contact attempt / referral'] || '',
      response: parsed['Provider response'] || '',
      barrier: parsed['Barrier'] || '',
      nextSteps: parsed['Next steps'] || '',
      dueDate: followup.due_date || '',
      status: followup.status === 'CANCELLED' ? 'OPEN' : followup.status,
    })
  }
  async function saveContact(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (!token || !familyId || !child || !contactDraft) return
    const description = contactDescription(contactDraft)
    if (description.length > 2000) {
      setContactError('Combined contact/referral details exceed 2,000 characters. Shorten the details before saving.')
      return
    }
    setContactError('')
    setSavingContact(true)
    setError('')
    const payload: FollowUpPayload = {
      child_id: child.id,
      service_continuity_id: contactDraft.record.id,
      title: `${contactDraft.record.service_type.replaceAll('_', ' ')} contact / referral`,
      description,
      status: contactDraft.status,
      due_date: contactDraft.dueDate || null,
    }
    try {
      if (contactDraft.followup) {
        await updateFollowup(contactDraft.followup.id, {
          title: payload.title,
          description: payload.description,
          status: payload.status,
          due_date: payload.due_date,
        }, token)
      } else {
        await createFollowup(familyId, payload, token)
      }
      await refreshData()
      setContactDraft(null)
      setMessage('Contact/referral and next steps recorded.')
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : 'Could not save contact and follow-up details.')
    } finally {
      setSavingContact(false)
    }
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
      <div className="mt-5">
        <label className="mb-3 block max-w-sm text-sm font-medium text-slate-800">How was the outcome confirmed?
          <select value={confirmationMethod} onChange={(event) => setConfirmationMethod(event.target.value as ConfirmationMethod)} className="mt-1.5 w-full rounded-lg border border-slate-300 px-3 py-2.5">
            {confirmationMethods.map((method) => <option key={method.value} value={method.value}>{method.label}</option>)}
          </select>
        </label>
        <label className="mb-4 block max-w-sm text-sm font-medium text-slate-800">Supporting reference (optional)
          <input maxLength={200} value={supportingReference} onChange={(event) => setSupportingReference(event.target.value)} placeholder="Short, non-sensitive reference only" className="mt-1.5 w-full rounded-lg border border-slate-300 px-3 py-2.5" />
        </label>
        <p className="mb-4 text-xs text-slate-500">Do not include personal information or confidential case details in the reference.</p>
      </div>
      <div className="divide-y divide-slate-100 border-y border-slate-100">{services.map((service) => {
        const record = summary.services.find((item) => item.service_type === service.type)
        return <div key={service.type} className="flex flex-col gap-3 py-4">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div className="flex items-center gap-3"><StatusIcon status={record?.status || 'PENDING'} /><div><p className="font-medium text-slate-900">{service.label}</p>{record?.due_date && <p className="mt-0.5 text-xs text-slate-500">Follow-up due {record.due_date}</p>}</div></div>
            <div className="flex items-center gap-4"><span className="text-sm text-slate-600">{statusText[record?.status || 'PENDING']}</span><Link to={`/children/${child.id}/${service.slug}`} className="text-sm font-semibold text-teal-800 hover:underline">Update</Link></div>
          </div>
          {record?.reason && <p className="text-sm text-slate-600">{record.reason}</p>}
          {record?.outcome_confirmed_at && record.outcome_confirmed_by_user_id && <p className="text-xs text-slate-500">Confirmed {new Date(record.outcome_confirmed_at).toLocaleString()} by user {record.outcome_confirmed_by_user_id} via {record.confirmation_method?.replaceAll('_', ' ').toLowerCase()}{record.supporting_reference ? ` · Ref ${record.supporting_reference}` : ''}</p>}
          {record && <div className="flex flex-wrap gap-2">
            <button type="button" disabled={busy} onClick={() => void confirmOutcome(record.id, 'CONNECTED')} className="rounded-lg border border-emerald-700 px-3 py-2 text-sm font-semibold text-emerald-800 hover:bg-emerald-50 disabled:opacity-60">Confirm connected</button>
            <button type="button" disabled={busy} onClick={() => void confirmOutcome(record.id, 'SUPPORT_NOT_REQUIRED')} className="rounded-lg border border-slate-400 px-3 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50 disabled:opacity-60">Confirm support not required</button>
          </div>}
          {record?.action_required && token && <DestinationServiceDiscovery
            serviceType={service.type}
            placeCandidates={destination}
            district={destinationDistrict}
            token={token}
            onRecordContact={(candidate) => beginContact(record, candidate)}
          />}
          {record && <button type="button" onClick={() => beginContact(record)} className="self-start text-sm font-semibold text-teal-800 hover:underline">
            Record another contact or referral
          </button>}
          {record && <div className="space-y-2">
            {followups.filter((item) => item.service_continuity_id === record.id).map((item) => <article key={item.id} className="rounded-lg border border-slate-200 p-3">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <p className="text-sm font-semibold text-slate-800">{item.title} · {item.status.replaceAll('_', ' ').toLowerCase()}</p>
                <button type="button" onClick={() => editContact(record, item)} className="text-xs font-semibold text-teal-800 hover:underline">Update response / follow-up</button>
              </div>
              {item.due_date && <p className="mt-1 text-xs text-slate-600">Next follow-up: {item.due_date}</p>}
              {item.description && <pre className="mt-2 whitespace-pre-wrap break-words font-sans text-xs text-slate-600">{item.description}</pre>}
            </article>)}
          </div>}
        </div>
      })}</div>
      <p className="mt-4 text-sm text-slate-600">{activeFollowups.length} services require follow-up.</p>
    </section>
    {contactDraft && <section className="mt-7 rounded-2xl border border-teal-200 bg-white p-5 sm:p-7">
      <div className="flex items-start justify-between gap-4">
        <div><h2 className="text-lg font-semibold text-slate-900">{contactDraft.followup ? 'Update contact and follow-up' : 'Record contact or referral'}</h2><p className="mt-1 text-sm text-slate-600">Keep the details factual and non-sensitive. A contact or referral does not confirm that support was received.</p></div>
        <button type="button" onClick={() => setContactDraft(null)} className="text-sm font-semibold text-slate-600 hover:underline">Cancel</button>
      </div>
      <form onSubmit={(event) => void saveContact(event)} className="mt-5 grid gap-4 sm:grid-cols-2">
        <label className="sm:col-span-2"><span className="mb-1 block text-sm font-medium text-slate-800">Potential service / provider</span><input maxLength={300} value={contactDraft.providerName} onChange={(event) => { setContactDraft({ ...contactDraft, providerName: event.target.value }); setContactError('') }} className="w-full rounded-lg border border-slate-300 px-3 py-2.5" /></label>
        <label className="sm:col-span-2"><span className="mb-1 block text-sm font-medium text-slate-800">Contact details (optional)</span><input maxLength={300} value={contactDraft.contactInformation} onChange={(event) => { setContactDraft({ ...contactDraft, contactInformation: event.target.value }); setContactError('') }} className="w-full rounded-lg border border-slate-300 px-3 py-2.5" /></label>
        <EngagementField label="Contact attempt / referral" value={contactDraft.attempt} required onChange={(value) => { setContactDraft({ ...contactDraft, attempt: value }); setContactError('') }} />
        <EngagementField label="Provider response" value={contactDraft.response} onChange={(value) => { setContactDraft({ ...contactDraft, response: value }); setContactError('') }} />
        <EngagementField label="Barrier or reason still pending" value={contactDraft.barrier} onChange={(value) => { setContactDraft({ ...contactDraft, barrier: value }); setContactError('') }} />
        <EngagementField label="Next steps" value={contactDraft.nextSteps} onChange={(value) => { setContactDraft({ ...contactDraft, nextSteps: value }); setContactError('') }} />
        <label><span className="mb-1 block text-sm font-medium text-slate-800">Next follow-up date</span><input type="date" value={contactDraft.dueDate} onChange={(event) => setContactDraft({ ...contactDraft, dueDate: event.target.value })} className="w-full rounded-lg border border-slate-300 px-3 py-2.5" /></label>
        <label><span className="mb-1 block text-sm font-medium text-slate-800">Follow-up status</span><select value={contactDraft.status} onChange={(event) => setContactDraft({ ...contactDraft, status: event.target.value as ContactDraft['status'] })} className="w-full rounded-lg border border-slate-300 px-3 py-2.5"><option value="OPEN">Open</option><option value="IN_PROGRESS">In progress</option><option value="COMPLETED">Completed</option></select></label>
        <p className="sm:col-span-2 text-xs text-slate-500">Do not record child names, medical/protection case details, or other sensitive personal information in this follow-up note.</p>
        {contactError && <p className="sm:col-span-2 text-sm text-rose-700" role="alert">{contactError}</p>}
        <div className="sm:col-span-2 flex justify-end"><button type="submit" disabled={savingContact || !contactDraft.attempt.trim()} className="rounded-lg bg-teal-700 px-5 py-2.5 font-semibold text-white hover:bg-teal-800 disabled:opacity-60">{savingContact ? 'Saving…' : 'Save contact and next steps'}</button></div>
      </form>
    </section>}
    <section className="mt-7"><h2 className="text-xl font-semibold text-slate-900">Follow-up actions</h2>{activeFollowups.length ? <div className="mt-3 divide-y divide-slate-200 border-y border-slate-200 bg-white">{activeFollowups.map((item) => <div key={item.id} className="flex flex-col justify-between gap-3 py-4 sm:flex-row sm:items-center"><div><h3 className="font-medium text-slate-900">{item.title}</h3>{item.description && <p className="mt-1 text-sm text-slate-600">{item.description}</p>}<p className="mt-1 text-xs text-slate-500">{item.status.replace('_', ' ')}{item.due_date ? ` · Due ${item.due_date}` : ''}</p></div><button type="button" onClick={() => void completeFollowup(item.id)} disabled={updatingFollowup === item.id} className="inline-flex items-center justify-center gap-2 self-start rounded-lg border border-slate-300 px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50 disabled:opacity-60 sm:self-auto"><Check className="h-4 w-4" aria-hidden="true" />{updatingFollowup === item.id ? 'Updating…' : 'Mark complete'}</button></div>)}</div> : <p className="mt-3 rounded-xl border border-slate-200 bg-white p-5 text-sm text-slate-600">No open follow-up items.</p>}</section>
  </div>
}

async function fetchContinuityPageData(childId: string, token: string): Promise<{ child: Child; summary: ContinuitySummary; followups: FollowUp[] }> {
  const child = await getChild(childId, token)
  const [summary, followups] = await Promise.all([getContinuity(childId, token), listFollowups(child.family_id, token)])
  return { child, summary, followups }
}

function FollowUpList({ familyId, token }: { familyId: string; token: string }) {
  const [retry, setRetry] = useState(0)
  const [result, setResult] = useState<{ key: string; items?: FollowUp[]; failed?: boolean } | null>(null)
  const requestKey = `${familyId}:${retry}`
  useEffect(() => {
    let active = true
    void listFollowups(familyId, token)
      .then((items) => { if (active) setResult({ key: requestKey, items }) })
      .catch(() => { if (active) setResult({ key: requestKey, failed: true }) })
    return () => { active = false }
  }, [familyId, requestKey, token])
  const currentResult = result?.key === requestKey ? result : null
  const items = currentResult?.items || []
  const open = items.filter((item) => item.status === 'OPEN' || item.status === 'IN_PROGRESS')
  return <section className="rounded-2xl border border-slate-200 bg-white p-5"><h2 className="font-semibold text-slate-900">Follow-up actions</h2>
    {!currentResult ? <p role="status" className="mt-3 text-sm text-slate-600">Loading follow-up actions…</p> : currentResult.failed ? <div className="mt-3" role="alert"><p className="text-sm text-rose-700">Could not load follow-up actions.</p><button type="button" onClick={() => setRetry((value) => value + 1)} className="mt-2 text-sm font-semibold text-teal-800 hover:underline">Retry</button></div> : open.length ? <ul className="mt-3 divide-y divide-slate-100">{open.slice(0, 4).map((item) => <li key={item.id} className="py-3"><p className="text-sm font-medium text-slate-800">{item.title}</p><p className="mt-1 text-xs text-slate-500">{item.due_date ? `Due ${item.due_date}` : item.status.replace('_', ' ')}</p></li>)}</ul> : <p className="mt-3 text-sm text-slate-600">No open actions.</p>}
  </section>
}

function ProfileValue({ label, value }: { label: string; value: string }) {
  return <div><dt className="text-xs font-semibold uppercase tracking-wide text-slate-500">{label}</dt><dd className="mt-1 text-slate-800">{value}</dd></div>
}

function EngagementField({ label, value, required = false, onChange }: { label: string; value: string; required?: boolean; onChange: (value: string) => void }) {
  return <label>
    <span className="mb-1 block text-sm font-medium text-slate-800">{label}{required ? ' *' : ''}</span>
    <textarea required={required} maxLength={400} rows={3} value={value} onChange={(event) => onChange(event.target.value)} className="w-full rounded-lg border border-slate-300 px-3 py-2.5" />
  </label>
}

function ProfileEditField({ label, value, onChange, type = 'text', required = false }: { label: string; value: string; onChange: (value: string) => void; type?: string; required?: boolean }) {
  return <label>
    <span className="mb-1 block text-sm font-medium text-slate-800">{label}{required ? ' *' : ''}</span>
    <input type={type} required={required} maxLength={80} value={value} onChange={(event) => onChange(event.target.value)} className="w-full rounded-lg border border-slate-300 px-3 py-2.5" />
  </label>
}

function ProfileEditSelect({ label, value, options, onChange }: { label: string; value: string; options: string[]; onChange: (value: string) => void }) {
  return <label>
    <span className="mb-1 block text-sm font-medium text-slate-800">{label}</span>
    <select value={value} onChange={(event) => onChange(event.target.value)} className="w-full rounded-lg border border-slate-300 px-3 py-2.5">
      {options.map((option) => <option key={option} value={option}>{option.replaceAll('_', ' ')}</option>)}
    </select>
  </label>
}

function EditLink({ childId, slug }: { childId: string; slug: string }) {
  return <Link to={`/children/${childId}/${slug}`} className="text-sm font-semibold text-teal-800 hover:underline">Edit</Link>
}

function CompactService({ title, detail, edit }: { title: string; detail: string; edit: string }) {
  return <div className="rounded-xl border border-slate-200 bg-white p-4"><div className="flex items-start justify-between gap-2"><h3 className="text-sm font-semibold text-slate-900">{title}</h3><Link to={edit} className="text-xs font-semibold text-teal-800 hover:underline">Edit</Link></div><p className="mt-3 text-sm text-slate-600">{detail}</p></div>
}

function StatusPill({ status }: { status: string }) {
  const color = status === 'CONNECTED' ? 'bg-emerald-50 text-emerald-800' : status === 'SUPPORT_NOT_REQUIRED' ? 'bg-slate-100 text-slate-700' : status === 'REVIEW_REQUIRED' ? 'bg-rose-50 text-rose-800' : 'bg-amber-50 text-amber-800'
  return <span className={`inline-flex items-center rounded-full px-3 py-1 text-sm font-medium ${color}`}><StatusIcon status={status} /><span className="ml-2">{statusText[status] || status}</span></span>
}

function str(value: unknown): string {
  return typeof value === 'string' && value ? value : 'Not recorded'
}

function sourceStatusText(value: unknown): string {
  const status = str(value)
  if (status === 'CONNECTED' || status === 'SUPPORT_CONNECTED') return 'Connection reported; confirmation required'
  return statusText[status] || (status === 'Not recorded' ? status : status.replaceAll('_', ' ').toLowerCase())
}

function educationStatusText(value: unknown): string {
  const status = str(value)
  const labels: Record<string, string> = {
    ENROLLED: 'Enrollment recorded',
    PENDING: 'Enrollment pending',
    NOT_ENROLLED: 'Not enrolled',
    UNKNOWN: 'Enrollment unconfirmed',
    COMPLETED: 'Transfer completed',
    NOT_STARTED: 'Transfer not started',
    NOT_REQUIRED: 'Transfer not required',
  }
  return labels[status] || 'Not recorded'
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
    { name: 'requirement_present', label: 'Support requirement', type: 'select', options: ['UNKNOWN', 'REQUIRED', 'NOT_REQUIRED'], defaultValue: 'UNKNOWN' },
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
      setValues(Object.fromEntries(config.fields.map((field) => {
        if (service === 'inclusion' && field.name === 'requirement_present') {
          const present = recordValue?.requirement_present
          return [field.name, present === true ? 'REQUIRED' : present === false ? 'NOT_REQUIRED' : 'UNKNOWN']
        }
        return [field.name, recordValue?.[field.name] ?? field.defaultValue ?? (field.type === 'checkbox' ? false : '')]
      })) as Record<string, string | boolean>)
    }).catch((cause: unknown) => setError(cause instanceof Error ? cause.message : 'Could not load this service record.'))
  }, [childId, config, service, token])

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); if (!token) return
    setBusy(true); setError(''); setSuccess(false)
    const payload = Object.fromEntries(Object.entries(values).map(([key, value]) => {
      if (service === 'inclusion' && key === 'requirement_present') {
        return [key, value === 'REQUIRED' ? true : value === 'NOT_REQUIRED' ? false : null]
      }
      return [key, value === '' ? null : value]
    }))
    try { await saveServiceRecord(childId, service, typeof record?.id === 'string' ? record.id : undefined, payload, token); setSuccess(true); navigate(`/children/${childId}`) }
    catch (cause) { setError(cause instanceof Error ? cause.message : 'Could not save this service record.') }
    finally { setBusy(false) }
  }
  if (!config) return <div className="mx-auto max-w-3xl px-4 py-10"><Message>Service type not found.</Message></div>
  return <div className="mx-auto max-w-3xl px-4 py-10 sm:px-6">
    <Link to={`/children/${childId}`} className="inline-flex items-center gap-2 text-sm font-semibold text-teal-800 hover:underline"><ArrowLeft className="h-4 w-4" aria-hidden="true" /> Child profile</Link>
    <header className="my-6 border-b border-slate-200 pb-5"><p className="text-sm font-semibold text-teal-700">{child ? `${child.first_name} ${child.last_name}` : 'Child service'}</p><h1 className="mt-2 text-3xl font-bold text-slate-900">{config.title}</h1></header>
    {error && <div className="mb-5"><Message>{error}</Message></div>}{success && <div className="mb-5"><Message success>Service record saved.</Message></div>}
    <p className="mb-5 rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">This records service information only. It does not confirm support; use the continuity checklist to confirm an outcome.</p>
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