import { useEffect, useState, type FormEvent } from 'react'
import { Link, useNavigate, useParams, useSearchParams } from 'react-router-dom'
import { ArrowRight, MapPin, Plus, Users } from 'lucide-react'
import { useAuth } from '../auth/AuthContext'
import { Button } from '../components/common/Button'
import { Badge } from '../components/common/Badge'
import {
  createChild,
  createFamily,
  createMigration,
  checkContinuity,
  getContinuity,
  getFamily,
  listChildren,
  listFamilies,
  listFollowups,
  listMigrations,
  updateFamily,
  updateMigration,
  type Child,
  type ContinuitySummary,
  type Family,
  type FollowUp,
  type Migration,
  type ServiceStatus,
} from '../api/continuity'

function PageMessage({ children, tone = 'error' }: { children: string; tone?: 'error' | 'success' }) {
  return <p role="status" className={`rounded-lg border px-4 py-3 text-sm ${tone === 'error' ? 'border-rose-200 bg-rose-50 text-rose-800' : 'border-emerald-200 bg-emerald-50 text-emerald-800'}`}>{children}</p>
}

function PageHeading({ eyebrow, title, description }: { eyebrow: string; title: string; description: string }) {
  return <header className="mb-8 border-b border-slate-200 pb-6">
    <p className="text-sm font-semibold text-teal-700">{eyebrow}</p>
    <h1 className="mt-2 text-3xl font-bold tracking-tight text-slate-900">{title}</h1>
    <p className="mt-2 max-w-2xl text-slate-600">{description}</p>
  </header>
}

function emptyMigrationForm() {
  return { from_district: '', from_taluka: '', from_location: '', to_district: '', to_taluka: '', to_location: '', migration_date: '', migration_reason: '', status: 'PLANNED' }
}

export function FamilyDashboard() {
  const { token } = useAuth()
  const [families, setFamilies] = useState<Family[]>([])
  const [counts, setCounts] = useState<Record<string, number>>({})
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!token) return
    void listFamilies(token).then(async (results) => {
      setFamilies(results)
      const entries = await Promise.all(results.map(async (family) => [family.id, (await listChildren(family.id, token)).length] as const))
      setCounts(Object.fromEntries(entries))
    }).catch((cause: unknown) => setError(cause instanceof Error ? cause.message : 'Could not load family records.'))
      .finally(() => setLoading(false))
  }, [token])

  return <div className="mx-auto max-w-7xl px-4 py-10 sm:px-6 lg:px-8">
    <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
      <PageHeading eyebrow="Family services" title="Family dashboard" description="Keep children’s education and essential support connected as your family moves." />
      <Button to="/family/create" className="mb-8 inline-flex items-center gap-2"><Plus className="h-4 w-4" aria-hidden="true" /> Create family</Button>
    </div>
    {error && <PageMessage>{error}</PageMessage>}
    {loading ? <p className="py-12 text-center text-slate-600">Loading family records…</p> : families.length === 0 ? (
      <section className="rounded-2xl border border-slate-200 bg-white p-8 text-center">
        <Users className="mx-auto h-9 w-9 text-teal-700" aria-hidden="true" />
        <h2 className="mt-4 text-xl font-semibold text-slate-900">No family profile yet</h2>
        <p className="mt-2 text-slate-600">Create a family profile to add children and track service continuity.</p>
        <Button to="/family/create" className="mt-5">Create family profile</Button>
      </section>
    ) : <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
      {families.map((family) => <Link key={family.id} to={`/family/${family.id}`} className="group rounded-2xl border border-slate-200 bg-white p-5 transition hover:border-teal-300 hover:shadow-sm">
        <div className="flex items-start justify-between gap-3">
          <div><p className="text-xs font-semibold uppercase tracking-wider text-slate-500">{family.family_reference_id}</p><h2 className="mt-2 text-xl font-semibold text-slate-900">{family.family_name}</h2></div>
          <ArrowRight className="mt-1 h-5 w-5 text-slate-400 group-hover:text-teal-700" aria-hidden="true" />
        </div>
        <p className="mt-4 flex items-center gap-2 text-sm text-slate-600"><MapPin className="h-4 w-4" aria-hidden="true" />{family.current_village_or_city}, {family.current_district}</p>
        <div className="mt-5 flex items-center justify-between border-t border-slate-100 pt-4"><span className="text-sm text-slate-600">{counts[family.id] ?? 0} children</span><Badge label={family.preferred_language} tone="neutral" /></div>
      </Link>)}
    </div>}
  </div>
}

export function FamilyCreatePage() {
  const { token } = useAuth()
  const navigate = useNavigate()
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [form, setForm] = useState({ family_name: '', contact_mobile: '', current_district: '', current_taluka: '', current_village_or_city: '', current_address: '', preferred_language: 'Marathi' })
  const update = (key: keyof typeof form, value: string) => setForm((current) => ({ ...current, [key]: value }))

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (!token) return
    setBusy(true)
    setError('')
    try {
      const family = await createFamily(form, token)
      navigate(`/family/${family.id}`)
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : 'Could not create this family profile.')
    } finally {
      setBusy(false)
    }
  }

  const fields: [keyof typeof form, string][] = [
    ['family_name', 'Family name'], ['contact_mobile', 'Contact mobile'], ['current_district', 'Current district'],
    ['current_taluka', 'Current taluka'], ['current_village_or_city', 'Village or city'], ['current_address', 'Current address'],
  ]
  return <div className="mx-auto max-w-3xl px-4 py-10 sm:px-6">
    <PageHeading eyebrow="Family services" title="Create a family profile" description="Add only the contact and location details needed to coordinate services." />
    <form onSubmit={submit} className="space-y-5 rounded-2xl border border-slate-200 bg-white p-6">
      {error && <PageMessage>{error}</PageMessage>}
      <div className="grid gap-5 sm:grid-cols-2">
        {fields.map(([key, label]) => <label key={key} className={key === 'current_address' ? 'sm:col-span-2' : ''}>
          <span className="mb-1.5 block text-sm font-medium text-slate-800">{label}{key !== 'current_address' && <span aria-hidden="true"> *</span>}</span>
          <input required={key !== 'current_address'} maxLength={key === 'current_address' ? 300 : 120} value={form[key]} onChange={(event) => update(key, event.target.value)} className="w-full rounded-lg border border-slate-300 px-3 py-2.5 text-slate-900 outline-none focus:border-teal-600 focus:ring-2 focus:ring-teal-100" />
        </label>)}
        <label>
          <span className="mb-1.5 block text-sm font-medium text-slate-800">Preferred language</span>
          <select value={form.preferred_language} onChange={(event) => update('preferred_language', event.target.value)} className="w-full rounded-lg border border-slate-300 px-3 py-2.5">
            {['English', 'Marathi', 'Hindi'].map((language) => <option key={language}>{language}</option>)}
          </select>
        </label>
      </div>
      <div className="flex justify-end gap-3 border-t border-slate-100 pt-5">
        <Button variant="outline" to="/family">Cancel</Button>
        <button disabled={busy} className="rounded-lg bg-teal-700 px-5 py-2.5 font-semibold text-white hover:bg-teal-800 disabled:opacity-60">{busy ? 'Creating…' : 'Create family'}</button>
      </div>
    </form>
  </div>
}

export function FamilyDetailPage() {
  const { familyId = '' } = useParams()
  const { token } = useAuth()
  const [family, setFamily] = useState<Family | null>(null)
  const [children, setChildren] = useState<Child[]>([])
  const [continuity, setContinuity] = useState<Record<string, ContinuitySummary>>({})
  const [migrations, setMigrations] = useState<Migration[]>([])
  const [followups, setFollowups] = useState<FollowUp[]>([])
  const [error, setError] = useState('')
  const [editingFamily, setEditingFamily] = useState(false)
  const [savingFamily, setSavingFamily] = useState(false)
  const [familyMessage, setFamilyMessage] = useState('')
  const [familyError, setFamilyError] = useState('')
  const [familyForm, setFamilyForm] = useState({
    family_name: '',
    contact_mobile: '',
    current_address: '',
    preferred_language: 'English',
  })

  useEffect(() => {
    if (!token) return
    void Promise.all([getFamily(familyId, token), listChildren(familyId, token), listMigrations(familyId, token), listFollowups(familyId, token)])
      .then(async ([familyResult, childResults, migrationResults, followupResults]) => {
        const summaries = await Promise.all(childResults.map((child) => getContinuity(child.id, token)))
        setFamily(familyResult); setChildren(childResults); setMigrations(migrationResults); setFollowups(followupResults)
        setContinuity(Object.fromEntries(summaries.map((summary) => [summary.child_id, summary])))
      }).catch((cause: unknown) => setError(cause instanceof Error ? cause.message : 'Could not load this family.'))
  }, [familyId, token])

  function beginFamilyEdit() {
    if (!family) return
    setFamilyForm({
      family_name: family.family_name,
      contact_mobile: family.contact_mobile,
      current_address: family.current_address || '',
      preferred_language: family.preferred_language,
    })
    setFamilyError('')
    setFamilyMessage('')
    setEditingFamily(true)
  }

  async function saveFamily(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (!family || !token) return
    setSavingFamily(true)
    setFamilyError('')
    setFamilyMessage('')
    try {
      const savedFamily = await updateFamily(family.id, familyForm, token)
      setFamily(savedFamily)
      setEditingFamily(false)
      setFamilyMessage('Family profile updated.')
    } catch (cause) {
      setFamilyError(cause instanceof Error ? cause.message : 'Could not update this family profile.')
    } finally {
      setSavingFamily(false)
    }
  }

  if (error) return <div className="mx-auto max-w-5xl px-4 py-10"><PageMessage>{error}</PageMessage></div>
  if (!family) return <p className="py-16 text-center text-slate-600">Loading family profile…</p>
  const migration = migrations[0]
  return <div className="mx-auto max-w-7xl px-4 py-10 sm:px-6 lg:px-8">
    <div className="flex flex-col justify-between gap-5 border-b border-slate-200 pb-6 md:flex-row md:items-end">
      <div><p className="text-sm font-semibold text-teal-700">{family.family_reference_id}</p><h1 className="mt-2 text-3xl font-bold text-slate-900">{family.family_name}</h1><p className="mt-2 text-slate-600">{family.current_village_or_city}, {family.current_taluka}, {family.current_district} · {family.preferred_language}</p><button type="button" onClick={beginFamilyEdit} className="mt-3 text-sm font-semibold text-teal-800 hover:underline">Edit family contact details</button></div>
      <div className="flex flex-wrap gap-2"><Button variant="outline" to={`/family/${family.id}/children`}>Add child</Button><Button to={`/migration?familyId=${family.id}`}>Record migration</Button></div>
    </div>
    {familyMessage && <div className="mt-4"><PageMessage tone="success">{familyMessage}</PageMessage></div>}
    {editingFamily && <form onSubmit={saveFamily} className="mt-5 grid gap-4 rounded-2xl border border-slate-200 bg-white p-5 sm:grid-cols-2">
      {familyError && <div className="sm:col-span-2"><PageMessage>{familyError}</PageMessage></div>}
      <Field label="Family name" value={familyForm.family_name} onChange={(value) => setFamilyForm((current) => ({ ...current, family_name: value }))} required />
      <Field label="Contact mobile" value={familyForm.contact_mobile} onChange={(value) => setFamilyForm((current) => ({ ...current, contact_mobile: value }))} required />
      <Field label="Current address" value={familyForm.current_address} onChange={(value) => setFamilyForm((current) => ({ ...current, current_address: value }))} />
      <SelectField label="Preferred language" value={familyForm.preferred_language} onChange={(value) => setFamilyForm((current) => ({ ...current, preferred_language: value }))} options={['English', 'Marathi', 'Hindi']} />
      <div className="sm:col-span-2 flex justify-end gap-3">
        <button type="button" onClick={() => setEditingFamily(false)} className="rounded-lg border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-700">Cancel</button>
        <button type="submit" disabled={savingFamily} className="rounded-lg bg-teal-700 px-4 py-2 text-sm font-semibold text-white disabled:opacity-60">{savingFamily ? 'Saving…' : 'Save family'}</button>
      </div>
    </form>}
    <div className="mt-7 grid gap-4 sm:grid-cols-3">
      <Info label="Children" value={String(children.length)} />
      <Info label="Open follow-ups" value={String(followups.filter((item) => item.status === 'OPEN' || item.status === 'IN_PROGRESS').length)} />
      <Info label="Preferred language" value={family.preferred_language} />
    </div>
    <div className="mt-10 grid gap-8 lg:grid-cols-[1.35fr_0.65fr]">
      <section>
        <div className="flex items-center justify-between"><h2 className="text-xl font-semibold text-slate-900">Children</h2><Link to={`/family/${family.id}/children`} className="text-sm font-semibold text-teal-800 hover:underline">Add child</Link></div>
        {children.length ? <div className="mt-4 divide-y divide-slate-200 border-y border-slate-200 bg-white">
          {children.map((child) => <Link key={child.id} to={`/children/${child.id}`} className="flex items-center justify-between gap-4 py-4 hover:bg-slate-50">
            <div><h3 className="font-semibold text-slate-900">{child.first_name} {child.last_name}</h3><p className="mt-1 text-sm text-slate-600">Class {child.current_class || 'Not recorded'} · {child.education_status.replaceAll('_', ' ').toLowerCase()}</p><p className="mt-1 text-xs font-medium text-teal-800">Continuity: {(continuity[child.id]?.overall_status || 'PENDING').replaceAll('_', ' ').toLowerCase()}</p></div><ArrowRight className="h-5 w-5 text-slate-400" aria-hidden="true" />
          </Link>)}
        </div> : <div className="mt-4 rounded-xl border border-dashed border-slate-300 p-7 text-center text-slate-600">No child profiles yet.</div>}
      </section>
      <aside className="space-y-6">
        <section className="rounded-2xl border border-slate-200 bg-white p-5"><h2 className="font-semibold text-slate-900">Service continuity</h2>{children.length ? <div className="mt-3 space-y-1">{[
          ['Education', 'EDUCATION'], ['Healthcare', 'HEALTHCARE'], ['Nutrition', 'NUTRITION'], ['Protection', 'PROTECTION'], ['Well-being', 'WELLBEING'], ['Inclusion', 'INCLUSION'],
        ].map(([label, serviceType]) => {
          const statuses = children.map((child) => continuity[child.id]?.services.find((record) => record.service_type === serviceType)?.status).filter((value): value is ServiceStatus => Boolean(value))
          const allResolved = statuses.length > 0 && statuses.every((value) => value === 'CONNECTED' || value === 'SUPPORT_NOT_REQUIRED')
          const status = statuses.includes('REVIEW_REQUIRED') ? 'REVIEW_REQUIRED'
            : statuses.includes('FOLLOW_UP_REQUIRED') ? 'FOLLOW_UP_REQUIRED'
              : statuses.includes('PENDING') ? 'PENDING'
                : allResolved ? (statuses.includes('CONNECTED') ? 'CONNECTED' : 'SUPPORT_NOT_REQUIRED')
                  : 'PENDING'
          return <div key={serviceType} className="flex items-center justify-between border-b border-slate-100 py-2.5 last:border-0"><span className="text-sm text-slate-700">{label}</span><span className={`text-xs font-semibold ${status === 'CONNECTED' ? 'text-emerald-700' : status === 'SUPPORT_NOT_REQUIRED' ? 'text-slate-600' : status === 'REVIEW_REQUIRED' ? 'text-rose-700' : 'text-amber-700'}`}>{status.replaceAll('_', ' ').toLowerCase()}</span></div>
        })}</div> : <p className="mt-3 text-sm text-slate-600">Add a child to start the continuity checklist.</p>}</section>
        <section className="rounded-2xl border border-slate-200 bg-white p-5"><h2 className="font-semibold text-slate-900">Current migration</h2>{migration ? <><p className="mt-3 text-sm text-slate-600">{migration.from_location}, {migration.from_district} <span aria-hidden="true">→</span> {migration.to_location}, {migration.to_district}</p><p className="mt-2 text-sm text-slate-500">{migration.migration_date} · {migration.status}</p></> : <p className="mt-3 text-sm text-slate-600">No migration recorded.</p>}<Link className="mt-4 inline-block text-sm font-semibold text-teal-800 hover:underline" to={`/migration?familyId=${family.id}`}>Manage migration</Link></section>
        <section className="rounded-2xl border border-slate-200 bg-white p-5"><h2 className="font-semibold text-slate-900">Follow-up items</h2>{followups.length ? <ul className="mt-3 space-y-3">{followups.slice(0, 4).map((item) => <li key={item.id} className="border-t border-slate-100 pt-3"><p className="text-sm font-medium text-slate-800">{item.title}</p><p className="mt-1 text-xs text-slate-500">{item.status.replace('_', ' ')}{item.due_date ? ` · Due ${item.due_date}` : ''}</p></li>)}</ul> : <p className="mt-3 text-sm text-slate-600">No follow-up items recorded.</p>}</section>
      </aside>
    </div>
  </div>
}

function Info({ label, value }: { label: string; value: string }) {
  return <div className="rounded-xl border border-slate-200 bg-white p-4"><p className="text-xs font-semibold uppercase tracking-wider text-slate-500">{label}</p><p className="mt-2 text-lg font-semibold text-slate-900">{value}</p></div>
}

export function AddChildPage() {
  const { familyId = '' } = useParams()
  const { token } = useAuth()
  const navigate = useNavigate()
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [form, setForm] = useState({ first_name: '', last_name: '', date_of_birth: '', gender: 'UNDISCLOSED', education_status: 'UNKNOWN', current_class: '', preferred_language: 'Marathi', disability_or_inclusion_requirement: '' })
  const update = (key: keyof typeof form, value: string) => setForm((current) => ({ ...current, [key]: value }))
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (!token) return
    setBusy(true); setError('')
    try {
      const child = await createChild(familyId, form, token)
      navigate(`/children/${child.id}`)
    } catch (cause) { setError(cause instanceof Error ? cause.message : 'Could not create child profile.') }
    finally { setBusy(false) }
  }
  return <div className="mx-auto max-w-3xl px-4 py-10 sm:px-6">
    <PageHeading eyebrow="Family profile" title="Add a child" description="Record basic information needed to support education and service continuity." />
    <form onSubmit={submit} className="space-y-5 rounded-2xl border border-slate-200 bg-white p-6">
      {error && <PageMessage>{error}</PageMessage>}
      <div className="grid gap-5 sm:grid-cols-2">
        <Field label="First name" value={form.first_name} onChange={(value) => update('first_name', value)} required />
        <Field label="Last name" value={form.last_name} onChange={(value) => update('last_name', value)} required />
        <Field label="Date of birth" type="date" value={form.date_of_birth} onChange={(value) => update('date_of_birth', value)} required />
        <SelectField label="Gender" value={form.gender} onChange={(value) => update('gender', value)} options={['UNDISCLOSED', 'FEMALE', 'MALE', 'NON_BINARY']} />
        <SelectField label="Education status" value={form.education_status} onChange={(value) => update('education_status', value)} options={['UNKNOWN', 'ENROLLED', 'PENDING', 'NOT_ENROLLED']} />
        <Field label="Current class" value={form.current_class} onChange={(value) => update('current_class', value)} />
        <SelectField label="Preferred language" value={form.preferred_language} onChange={(value) => update('preferred_language', value)} options={['Marathi', 'Hindi', 'English']} />
        <label className="sm:col-span-2"><span className="mb-1.5 block text-sm font-medium text-slate-800">Inclusion requirement, if any</span><textarea maxLength={500} value={form.disability_or_inclusion_requirement} onChange={(event) => update('disability_or_inclusion_requirement', event.target.value)} rows={3} className="w-full rounded-lg border border-slate-300 px-3 py-2.5" /></label>
      </div>
      <div className="flex justify-end gap-3 border-t border-slate-100 pt-5"><Button variant="outline" to={`/family/${familyId}`}>Cancel</Button><button disabled={busy} className="rounded-lg bg-teal-700 px-5 py-2.5 font-semibold text-white hover:bg-teal-800 disabled:opacity-60">{busy ? 'Saving…' : 'Save child'}</button></div>
    </form>
  </div>
}

export function MigrationPage() {
  const { token } = useAuth()
  const [searchParams] = useSearchParams()
  const [families, setFamilies] = useState<Family[]>([])
  const [familyId, setFamilyId] = useState(searchParams.get('familyId') || '')
  const [migrations, setMigrations] = useState<Migration[]>([])
  const [migrationId, setMigrationId] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)
  const [children, setChildren] = useState<Child[]>([])
  const [checking, setChecking] = useState(false)
  const [form, setForm] = useState(emptyMigrationForm)
  useEffect(() => { if (token) void listFamilies(token).then(setFamilies).catch((cause: unknown) => setError(cause instanceof Error ? cause.message : 'Could not load families.')) }, [token])
  useEffect(() => {
    if (!token || !familyId) return
    let active = true
    void Promise.all([listMigrations(familyId, token), listChildren(familyId, token)])
      .then(([migrationResults, childResults]) => {
        if (!active) return
        setMigrations(migrationResults)
        setChildren(childResults)
        setMigrationId('')
      })
      .catch((cause: unknown) => {
        if (active) setError(cause instanceof Error ? cause.message : 'Could not load this family’s migration records.')
      })
    return () => { active = false }
  }, [familyId, token])
  const update = (key: keyof typeof form, value: string) => setForm((current) => ({ ...current, [key]: value }))
  function selectMigration(id: string) {
    setMigrationId(id)
    setSuccess(false)
    const selected = migrations.find((item) => item.id === id)
    setForm(selected ? {
      from_district: selected.from_district,
      from_taluka: selected.from_taluka,
      from_location: selected.from_location,
      to_district: selected.to_district,
      to_taluka: selected.to_taluka,
      to_location: selected.to_location,
      migration_date: selected.migration_date,
      migration_reason: selected.migration_reason || '',
      status: selected.status,
    } : emptyMigrationForm())
  }
  const selectedMigration = migrations.find((item) => item.id === migrationId)
  const statusOptions = selectedMigration?.status === 'PLANNED'
    ? ['PLANNED', 'ACTIVE']
    : selectedMigration?.status === 'ACTIVE'
      ? ['ACTIVE', 'COMPLETED']
      : selectedMigration?.status === 'COMPLETED'
        ? ['COMPLETED']
        : ['PLANNED', 'ACTIVE']
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); if (!token || !familyId) return
    setBusy(true); setError(''); setSuccess(false)
    try {
      const saved = migrationId
        ? await updateMigration(migrationId, form, token)
        : await createMigration(familyId, form, token)
      const [migrationResults, childResults] = await Promise.all([
        listMigrations(familyId, token),
        listChildren(familyId, token),
      ])
      setMigrations(migrationResults)
      setChildren(childResults)
      setMigrationId(saved.id)
      setSuccess(true)
    }
    catch (cause) { setError(cause instanceof Error ? cause.message : 'Could not record this migration.') }
    finally { setBusy(false) }
  }
  async function runContinuityCheck() {
    if (!token) return
    setChecking(true); setError('')
    try { await Promise.all(children.map((child) => checkContinuity(child.id, token))); setSuccess(true) }
    catch (cause) { setError(cause instanceof Error ? cause.message : 'Could not check service continuity.') }
    finally { setChecking(false) }
  }
  const fields: [keyof typeof form, string][] = [['from_district', 'From district'], ['from_taluka', 'From taluka'], ['from_location', 'From location'], ['to_district', 'To district'], ['to_taluka', 'To taluka'], ['to_location', 'To location']]
  return <div className="mx-auto max-w-3xl px-4 py-10 sm:px-6">
    <PageHeading eyebrow="Family services" title="Migration lifecycle" description="Create a planned migration, update it as the family moves, and complete it when the destination becomes current." />
    <form onSubmit={submit} className="space-y-5 rounded-2xl border border-slate-200 bg-white p-6">
      {error && <PageMessage>{error}</PageMessage>}{success && <PageMessage tone="success">{migrationId ? 'Migration updated successfully.' : 'Migration recorded successfully.'}</PageMessage>}
      <label><span className="mb-1.5 block text-sm font-medium text-slate-800">Family *</span><select required value={familyId} onChange={(event) => { setFamilyId(event.target.value); setMigrationId(''); setMigrations([]); setChildren([]); setForm(emptyMigrationForm()); setError(''); setSuccess(false) }} className="w-full rounded-lg border border-slate-300 px-3 py-2.5"><option value="">Select a family</option>{families.map((family) => <option key={family.id} value={family.id}>{family.family_name} · {family.family_reference_id}</option>)}</select></label>
      {familyId && <label><span className="mb-1.5 block text-sm font-medium text-slate-800">Migration record</span><select value={migrationId} onChange={(event) => selectMigration(event.target.value)} className="w-full rounded-lg border border-slate-300 px-3 py-2.5"><option value="">Create a new migration</option>{migrations.map((item) => <option key={item.id} value={item.id}>{item.status} · {item.from_location} → {item.to_location} · {item.migration_date}</option>)}</select></label>}
      <div className="grid gap-5 sm:grid-cols-2">{fields.map(([key, label]) => <Field key={key} label={label} value={form[key]} onChange={(value) => update(key, value)} required />)}
        <Field label="Migration date" type="date" value={form.migration_date} onChange={(value) => update('migration_date', value)} required />
        <SelectField label="Status" value={form.status} onChange={(value) => update('status', value)} options={statusOptions} />
        <label className="sm:col-span-2"><span className="mb-1.5 block text-sm font-medium text-slate-800">Reason (optional)</span><textarea maxLength={300} value={form.migration_reason} onChange={(event) => update('migration_reason', event.target.value)} rows={3} className="w-full rounded-lg border border-slate-300 px-3 py-2.5" /></label>
      </div>
      <div className="flex justify-end"><button disabled={busy || !familyId} className="rounded-lg bg-teal-700 px-5 py-2.5 font-semibold text-white hover:bg-teal-800 disabled:opacity-60">{busy ? 'Saving…' : migrationId ? 'Update migration' : 'Create migration'}</button></div>
      {success && <div className="border-t border-slate-100 pt-4"><Link to={`/family/${familyId}`} className="text-sm font-semibold text-teal-800 hover:underline">Return to family dashboard <span aria-hidden="true">→</span></Link></div>}
    </form>
    {success && <section className="mt-5 rounded-xl border border-teal-200 bg-teal-50 p-5"><h2 className="font-semibold text-slate-900">Check service continuity</h2>{children.length ? <><p className="mt-1 text-sm text-slate-600">Run the six-service checklist for every child in this family.</p><button type="button" onClick={() => void runContinuityCheck()} disabled={checking} className="mt-4 rounded-lg bg-teal-700 px-4 py-2.5 text-sm font-semibold text-white hover:bg-teal-800 disabled:opacity-60">{checking ? 'Checking…' : 'Check Service Continuity'}</button></> : <p className="mt-1 text-sm text-slate-600">Add a child profile before checking service continuity.</p>}</section>}
  </div>
}

function Field({ label, value, onChange, type = 'text', required = false }: { label: string; value: string; onChange: (value: string) => void; type?: string; required?: boolean }) {
  return <label><span className="mb-1.5 block text-sm font-medium text-slate-800">{label}{required ? ' *' : ''}</span><input type={type} required={required} value={value} onChange={(event) => onChange(event.target.value)} className="w-full rounded-lg border border-slate-300 px-3 py-2.5 outline-none focus:border-teal-600 focus:ring-2 focus:ring-teal-100" /></label>
}

function SelectField({ label, value, onChange, options }: { label: string; value: string; onChange: (value: string) => void; options: string[] }) {
  return <label><span className="mb-1.5 block text-sm font-medium text-slate-800">{label}</span><select value={value} onChange={(event) => onChange(event.target.value)} className="w-full rounded-lg border border-slate-300 px-3 py-2.5">{options.map((option) => <option key={option} value={option}>{option.replaceAll('_', ' ').toLowerCase().replace(/\b\w/g, (char) => char.toUpperCase())}</option>)}</select></label>
}