import { useState } from 'react'
import { Link } from 'react-router-dom'
import { discoveryPath, getNearbyServices, discoveryServiceType, formatLabel, verificationLabel, type NearbyService } from '../api/services'
import { findPlaceCentre } from '../data/placeCentres'

type Props = {
  serviceType: string
  placeCandidates: string[]
  district?: string
  token: string
  onRecordContact: (service: NearbyService) => void
}

export function DestinationServiceDiscovery({ serviceType, placeCandidates, district, token, onRecordContact }: Props) {
  const [services, setServices] = useState<NearbyService[] | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const target = discoveryServiceType(serviceType)
  const matchedDestination = placeCandidates
    .map((place) => ({ place, centre: findPlaceCentre(place) }))
    .find((match) => match.centre !== null)
  const centre = matchedDestination?.centre

  async function search() {
    if (!target || !centre) return
    setLoading(true)
    setError('')
    try {
      setServices(await getNearbyServices({
        latitude: centre.latitude,
        longitude: centre.longitude,
        radius: 50,
        service_type: target,
        district,
      }, token))
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : 'Could not search destination services.')
    } finally {
      setLoading(false)
    }
  }

  if (!target) return null
  return <div className="rounded-xl border border-slate-200 bg-slate-50 p-3">
    <div className="flex flex-wrap items-center justify-between gap-3">
      <div>
        <p className="text-sm font-semibold text-slate-800">Potential {formatLabel(target)} services</p>
        <p className="text-xs text-slate-600">These are potential matches only. A verified directory listing does not confirm eligibility, capacity, or current availability.</p>
      </div>
      <button type="button" disabled={!centre || loading} onClick={() => void search()} className="rounded-lg border border-teal-700 px-3 py-2 text-sm font-semibold text-teal-800 hover:bg-teal-50 disabled:opacity-50">
        {loading ? 'Searching…' : services ? 'Search again' : 'Find at destination'}
      </button>
    </div>
    {centre && <p className="mt-2 text-xs text-slate-600">
      Approximate search point: {centre.name} town centre
      {matchedDestination?.place ? `, matched from destination area ${matchedDestination.place}` : ''}. Distances are measured from this point.
      The authenticated lookup sends the approximate location and service filters; child and family identifiers or case details are not included.
    </p>}
    {!centre && <p className="mt-2 text-xs text-amber-800">
      No supported destination town is available for a nearby search. No other city will be substituted. Check the migration destination or choose a search location on the service map.
      Child and family identifiers or case details are not sent to the directory.{' '}
      <Link to={discoveryPath(serviceType)} className="font-semibold underline">Open service map</Link>
    </p>}
    {error && <p role="alert" className="mt-2 text-sm text-rose-700">{error}</p>}
    {services && (services.length ? <ul className="mt-3 space-y-3">
      {services.map((service) => <li key={service.service_id} className="rounded-lg border border-slate-200 bg-white p-3">
        <div className="flex flex-col justify-between gap-2 sm:flex-row">
          <div>
            <p className="font-semibold text-slate-900">{service.service_name}</p>
            <p className="text-sm text-slate-700">{service.organization_name}</p>
            <p className="text-xs text-slate-600">{formatLabel(service.service_type)} · {service.distance_km} km from approximate search point</p>
            <p className="text-xs text-slate-600">{[service.address, service.city_or_village, service.taluka, service.district].filter(Boolean).join(', ') || 'Address not listed'}</p>
            <p className={`text-xs font-semibold ${service.is_verified ? 'text-emerald-700' : 'text-amber-800'}`}>{verificationLabel(service)}</p>
            {service.eligibility && <p className="mt-1 text-xs text-slate-600">Eligibility: {service.eligibility}</p>}
            {service.contact_information && <p className="mt-1 text-xs text-slate-600">Contact: {service.contact_information}</p>}
          </div>
          <button type="button" onClick={() => onRecordContact(service)} className="self-start rounded-lg bg-teal-700 px-3 py-2 text-sm font-semibold text-white hover:bg-teal-800">Record contact / referral</button>
        </div>
      </li>)}
    </ul> : <p className="mt-3 text-sm text-slate-600">No matching directory listings found within 50 km. The need remains open; try a wider area or record another referral.</p>)}
  </div>
}
