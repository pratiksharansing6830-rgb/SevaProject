import { useCallback, useEffect, useRef, useState, type FormEvent } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { LocateFixed, Search } from 'lucide-react'
import { useAuth } from '../auth/AuthContext'
import {
  DISCOVERY_SERVICE_TYPES,
  formatLabel,
  getNearbyServices,
  isDemoOrganization,
  verificationLabel,
  type DiscoveryServiceType,
  type NearbyQuery,
  type NearbyService,
} from '../api/services'
import { ServiceMap } from '../components/ServiceMap'
import { findPlaceCentre } from '../data/placeCentres'

type AppliedQuery = NearbyQuery & { radius: number }

type FormState = {
  latitude: string
  longitude: string
  radius: string
  service_type: DiscoveryServiceType | ''
  district: string
  taluka: string
}

type Status = 'idle' | 'loading' | 'ready' | 'error'

const RADIUS_OPTIONS = [2, 5, 10, 25, 50, 100]

const INITIAL_FORM: FormState = {
  latitude: '',
  longitude: '',
  radius: '10',
  service_type: '',
  district: '',
  taluka: '',
}

const inputClass =
  'mt-1 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 focus:border-emerald-600 focus:outline-none focus:ring-1 focus:ring-emerald-600'
const labelClass = 'block text-sm font-medium text-slate-700'

function buildQuery(form: FormState): { query?: AppliedQuery; error?: string } {
  const latitude = Number(form.latitude)
  const longitude = Number(form.longitude)
  const radius = Number(form.radius)

  if (form.latitude.trim() === '' || !Number.isFinite(latitude) || latitude < -90 || latitude > 90) {
    return { error: 'Latitude must be a number between -90 and 90.' }
  }
  if (form.longitude.trim() === '' || !Number.isFinite(longitude) || longitude < -180 || longitude > 180) {
    return { error: 'Longitude must be a number between -180 and 180.' }
  }
  if (!Number.isFinite(radius) || radius <= 0) {
    return { error: 'Radius must be greater than 0.' }
  }
  return {
    query: {
      latitude,
      longitude,
      radius,
      service_type: form.service_type,
      district: form.district,
      taluka: form.taluka,
    },
  }
}

/** Reads a coarse destination and service type; no family or child identifiers belong in this URL. */
function initialFromParams(params: URLSearchParams): { form: FormState; notice: string; query: AppliedQuery | null } {
  const form: FormState = { ...INITIAL_FORM }
  let notice = ''
  let query: AppliedQuery | null = null

  const typeParam = params.get('service_type')
  if (typeParam && (DISCOVERY_SERVICE_TYPES as readonly string[]).includes(typeParam)) {
    form.service_type = typeParam as DiscoveryServiceType
  }

  const placeParam = params.get('place')
  if (placeParam) {
    const centre = findPlaceCentre(placeParam)
    if (centre) {
      form.latitude = String(centre.latitude)
      form.longitude = String(centre.longitude)
      notice = `Approximate search around the town centre of ${centre.name}, based on destination area "${placeParam}". Distances are measured from this point; adjust the coordinates to refine the search.`
      query = buildQuery(form).query ?? null
    } else {
      notice = `No supported approximate search point was found for destination "${placeParam}". No other city will be substituted. Enter coordinates or use your location.`
    }
  } else if (typeParam) {
    notice = 'No supported destination search point was provided. Enter destination coordinates or use your location to search; no default city will be used.'
  }
  return { form, notice, query }
}

function locationLine(service: NearbyService) {
  return [service.city_or_village, service.taluka, service.district].filter(Boolean).join(', ') || 'Location not listed'
}

function Detail({ label, value }: { label: string; value: string | null | undefined }) {
  return (
    <div>
      <dt className="text-xs font-semibold uppercase tracking-wide text-slate-500">{label}</dt>
      <dd className="mt-1 text-slate-800">{value && value.trim() ? value : 'Not listed'}</dd>
    </div>
  )
}

export default function MapPage() {
  const { token } = useAuth()
  const [searchParams] = useSearchParams()
  const [initial] = useState(() => initialFromParams(searchParams))
  const [form, setForm] = useState<FormState>(initial.form)
  const [applied, setApplied] = useState<AppliedQuery | null>(initial.query)
  const [services, setServices] = useState<NearbyService[]>([])
  const [status, setStatus] = useState<Status>(initial.query ? 'loading' : 'idle')
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [formError, setFormError] = useState('')
  const [locationMessage, setLocationMessage] = useState('')
  const latestRequest = useRef(0)

  const runSearch = useCallback(
    async (query: AppliedQuery) => {
      if (!token) return
      const requestId = ++latestRequest.current
      setStatus('loading')
      setSelectedId(null)
      try {
        const results = await getNearbyServices(query, token)
        if (requestId !== latestRequest.current) return
        setServices(results)
        setStatus('ready')
      } catch {
        if (requestId !== latestRequest.current) return
        setServices([])
        setStatus('error')
      }
    },
    [token],
  )

  useEffect(() => {
    if (applied) void runSearch(applied)
  }, [applied, runSearch])

  function updateField<K extends keyof FormState>(field: K, value: FormState[K]) {
    setForm((current) => ({ ...current, [field]: value }))
  }

  function handleSubmit(event: FormEvent) {
    event.preventDefault()
    const { query, error } = buildQuery(form)
    if (!query) {
      setFormError(error ?? 'Please check the search details.')
      return
    }
    setFormError('')
    setLocationMessage('')
    setApplied(query)
  }

  function handleUseMyLocation() {
    if (!('geolocation' in navigator)) {
      setLocationMessage('Your browser does not support location. Please enter latitude and longitude instead.')
      return
    }
    setLocationMessage('Asking your browser for your location...')
    // One-time request only. No watchPosition and nothing is stored.
    navigator.geolocation.getCurrentPosition(
      (position) => {
        const next = {
          ...form,
          latitude: position.coords.latitude.toFixed(5),
          longitude: position.coords.longitude.toFixed(5),
        }
        const { query, error } = buildQuery(next)
        setForm(next)
        if (!query) {
          setFormError(error ?? 'Please check the search details.')
          return
        }
        setFormError('')
        setLocationMessage('Using your current location for this search only. It is not saved.')
        setApplied(query)
      },
      () => {
        setLocationMessage('Location permission was not granted. Please enter latitude and longitude instead.')
      },
      { timeout: 10000, maximumAge: 0 },
    )
  }

  const selectedService = services.find((service) => service.service_id === selectedId) ?? null

  return (
    <div className="mx-auto max-w-7xl px-4 py-10 sm:px-6 lg:px-8">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <p className="text-sm font-semibold uppercase tracking-wide text-emerald-700">Service discovery</p>
          <h1 className="mt-1 text-3xl font-bold tracking-tight text-slate-900">Find services near you</h1>
          <p className="mt-2 max-w-2xl text-sm text-slate-600">
            This map shows public service locations only. Search coordinates and filters are sent to the authenticated
            directory for this request and are not saved. No child name, family identifier, or private case details are sent
            or shown here. OpenStreetMap supplies map tiles and receives standard tile requests from your browser.
            Directory verification does not confirm suitability or current availability.
          </p>
        </div>
        <Link to="/services" className="text-sm font-semibold text-emerald-700 hover:underline">
          Back to services overview
        </Link>
      </div>

      {initial.notice ? (
        <p className="mt-4 rounded-lg border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-900">
          {initial.notice}
        </p>
      ) : null}

      <form onSubmit={handleSubmit} className="mt-6 rounded-2xl border border-slate-200 bg-white p-4 shadow-sm sm:p-5">
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <label className={labelClass}>
            Latitude
            <input
              className={inputClass}
              inputMode="decimal"
              value={form.latitude}
              onChange={(event) => updateField('latitude', event.target.value)}
            />
          </label>
          <label className={labelClass}>
            Longitude
            <input
              className={inputClass}
              inputMode="decimal"
              value={form.longitude}
              onChange={(event) => updateField('longitude', event.target.value)}
            />
          </label>
          <label className={labelClass}>
            Radius
            <select className={inputClass} value={form.radius} onChange={(event) => updateField('radius', event.target.value)}>
              {RADIUS_OPTIONS.map((km) => (
                <option key={km} value={km}>
                  {km} km
                </option>
              ))}
            </select>
          </label>
          <label className={labelClass}>
            Service type
            <select
              className={inputClass}
              value={form.service_type}
              onChange={(event) => updateField('service_type', event.target.value as DiscoveryServiceType | '')}
            >
              <option value="">All service types</option>
              {DISCOVERY_SERVICE_TYPES.map((type) => (
                <option key={type} value={type}>
                  {formatLabel(type)}
                </option>
              ))}
            </select>
          </label>
          <label className={labelClass}>
            District
            <input className={inputClass} value={form.district} onChange={(event) => updateField('district', event.target.value)} />
          </label>
          <label className={labelClass}>
            Taluka
            <input className={inputClass} value={form.taluka} onChange={(event) => updateField('taluka', event.target.value)} />
          </label>
        </div>

        <div className="mt-4 flex flex-wrap items-center gap-3">
          <button
            type="submit"
            className="inline-flex items-center gap-2 rounded-lg bg-emerald-700 px-4 py-2 text-sm font-semibold text-white hover:bg-emerald-800"
          >
            <Search className="h-4 w-4" aria-hidden="true" />
            Search
          </button>
          <button
            type="button"
            onClick={handleUseMyLocation}
            className="inline-flex items-center gap-2 rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50"
          >
            <LocateFixed className="h-4 w-4" aria-hidden="true" />
            Use my location
          </button>
          {locationMessage ? <p className="text-sm text-slate-600">{locationMessage}</p> : null}
        </div>
        {formError ? (
          <p role="alert" className="mt-3 text-sm font-medium text-red-700">
            {formError}
          </p>
        ) : null}
      </form>
      {status === 'idle' ? (
        <p className="mt-6 rounded-xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-900">
          Choose a destination location or enter coordinates and search. No city is assumed when the destination is unknown.
        </p>
      ) : null}

      <div className="mt-6 grid gap-6 lg:grid-cols-[minmax(0,380px)_minmax(0,1fr)]">
        <section aria-label="Service results" className="order-2 lg:order-1">
          {status === 'loading' ? <p className="text-sm text-slate-600">Finding nearby services...</p> : null}
          {status === 'idle' ? <p className="text-sm text-slate-600">Service results will appear here after a location is selected.</p> : null}

          {status === 'error' ? (
            <div role="alert" className="rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-800">
              <p>Unable to load nearby services. Please try again.</p>
              <button type="button" onClick={() => applied && void runSearch(applied)} className="mt-2 font-semibold underline">
                Try again
              </button>
            </div>
          ) : null}

          {status === 'ready' && services.length === 0 ? (
            <p className="rounded-xl border border-slate-200 bg-white p-4 text-sm text-slate-600">
              No directory listings matched this search. This does not prove that no service exists or resolve any child&apos;s need; verify locally or record another referral.
            </p>
          ) : null}

          {applied && services.length > 0 ? (
            <>
              <p className="mb-2 text-sm text-slate-600">
                {services.length} {services.length === 1 ? 'service' : 'services'} within {applied.radius} km, nearest first
              </p>
              <ul className="max-h-[600px] space-y-3 overflow-y-auto pr-1">
                {services.map((service) => {
                  const isSelected = service.service_id === selectedId
                  return (
                    <li key={service.service_id}>
                      <button
                        type="button"
                        onClick={() => setSelectedId(service.service_id)}
                        aria-pressed={isSelected}
                        className={`w-full rounded-xl border p-4 text-left shadow-sm transition ${
                          isSelected ? 'border-amber-500 bg-amber-50' : 'border-slate-200 bg-white hover:border-emerald-600'
                        }`}
                      >
                        <p className="text-sm font-semibold text-slate-900">{service.organization_name}</p>
                        <p className="mt-1 text-sm text-slate-800">{service.service_name}</p>
                        <p className="mt-1 text-xs text-slate-600">
                          {formatLabel(service.service_type)} · {service.distance_km} km from search point
                        </p>
                        <p className="mt-1 text-xs text-slate-600">{service.address || 'Address not listed'}</p>
                        <p className="mt-1 text-xs text-slate-600">{locationLine(service)}</p>
                        <p
                          className={`mt-1 text-xs font-semibold ${
                            service.is_verified ? 'text-emerald-700' : isDemoOrganization(service) ? 'text-amber-700' : 'text-slate-500'
                          }`}
                        >
                          {verificationLabel(service)}
                        </p>
                      </button>
                    </li>
                  )
                })}
              </ul>
            </>
          ) : null}
        </section>

        <section aria-label="Service map" className="order-1 lg:order-2">
          {applied ? (
            <ServiceMap
              center={{ latitude: applied.latitude, longitude: applied.longitude }}
              radiusKm={applied.radius}
              services={services}
              selectedId={selectedId}
              onSelect={setSelectedId}
              className="h-[360px] w-full lg:h-[600px]"
            />
          ) : (
            <div className="flex h-[360px] items-center justify-center rounded-2xl border border-dashed border-slate-300 bg-slate-50 text-sm text-slate-600 lg:h-[600px]">
              A map will appear after you choose a search location.
            </div>
          )}
        </section>
      </div>

      {selectedService ? (
        <section aria-label="Service details" className="mt-6 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
          <div className="flex flex-wrap items-start justify-between gap-3">
            <div>
              <h2 className="text-xl font-bold text-slate-900">{selectedService.service_name}</h2>
              <p className="mt-1 text-sm text-slate-600">{selectedService.organization_name}</p>
            </div>
            <span
              className={`rounded-full px-3 py-1 text-xs font-semibold ${
                selectedService.is_verified ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-800'
              }`}
            >
              {verificationLabel(selectedService)}
            </span>
          </div>

          {isDemoOrganization(selectedService) ? (
            <p className="mt-3 rounded-lg bg-amber-50 px-3 py-2 text-sm text-amber-900">
              This is a fictional DEMO record used to demonstrate the platform. It is not a real institution.
            </p>
          ) : null}

          <dl className="mt-4 grid gap-4 text-sm sm:grid-cols-2 lg:grid-cols-3">
            <Detail label="Service type" value={formatLabel(selectedService.service_type)} />
            <Detail label="Distance" value={`${selectedService.distance_km} km`} />
            <Detail label="Organization type" value={formatLabel(selectedService.organization_type)} />
            <Detail label="Service description" value={selectedService.service_description} />
            <Detail label="Eligibility" value={selectedService.eligibility} />
            <Detail label="About the organization" value={selectedService.description} />
            <Detail label="Address" value={selectedService.address} />
            <Detail label="District / Taluka" value={[selectedService.district, selectedService.taluka].filter(Boolean).join(' / ')} />
            <Detail label="City or village" value={selectedService.city_or_village} />
            <Detail label="Contact" value={selectedService.contact_information} />
          </dl>
        </section>
      ) : null}
    </div>
  )
}