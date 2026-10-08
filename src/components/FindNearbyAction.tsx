import { Link } from 'react-router-dom'
import { MapPin } from 'lucide-react'
import { discoveryPath, discoveryServiceType, formatLabel, needsDiscoveryAction } from '../api/services'
import { firstResolvablePlace } from '../data/placeCentres'

type Props = {
  /** Part 3 continuity service type, e.g. EDUCATION or PROTECTION */
  serviceType: string
  /** Part 3 continuity status */
  status: string
  /** Part 3 action_required flag */
  actionRequired?: boolean | null
  /** Place names for the current destination, most specific first. Only a city/district name is used. */
  placeCandidates?: Array<string | null | undefined>
}

export function FindNearbyAction({ serviceType, status, actionRequired, placeCandidates = [] }: Props) {
  if (!needsDiscoveryAction(status, actionRequired)) return null
  const target = discoveryServiceType(serviceType)
  if (!target) return null

  const place = firstResolvablePlace(placeCandidates)
  return (
    <Link
      to={discoveryPath(serviceType, place)}
      className="mt-3 inline-flex items-center gap-2 rounded-lg bg-emerald-700 px-3 py-2 text-sm font-semibold text-white hover:bg-emerald-800"
    >
      <MapPin className="h-4 w-4" aria-hidden="true" />
      Find Nearby {formatLabel(target)}
    </Link>
  )
}