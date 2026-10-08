import { apiRequest } from './client'

export const DISCOVERY_SERVICE_TYPES = [
  'EDUCATION',
  'HEALTHCARE',
  'NUTRITION',
  'PROTECTION',
  'WELLBEING',
  'INCLUSION',
  'GOVERNMENT_SCHEME',
  'SOCIAL_SUPPORT',
  'DOCUMENTATION',
  'HOUSING_SUPPORT',
  'OTHER',
] as const

export type DiscoveryServiceType = (typeof DISCOVERY_SERVICE_TYPES)[number]

/** Public service-discovery result. Contains no child, family or user data. */
export type NearbyService = {
  organization_id: string
  organization_name: string
  organization_type: string
  description: string | null
  address: string | null
  district: string | null
  taluka: string | null
  city_or_village: string | null
  latitude: number | null
  longitude: number | null
  service_id: string
  service_name: string
  service_type: DiscoveryServiceType
  service_description: string | null
  eligibility: string | null
  contact_information: string | null
  distance_km: number
  is_verified: boolean
}

export type NearbyQuery = {
  latitude: number
  longitude: number
  radius?: number
  service_type?: DiscoveryServiceType | ''
  district?: string
  taluka?: string
}

/** The backend does all filtering and sorting. The search point is sent only in this request. */
export function getNearbyServices(query: NearbyQuery, token: string) {
  const params = new URLSearchParams({
    latitude: String(query.latitude),
    longitude: String(query.longitude),
  })
  if (query.radius !== undefined) params.set('radius', String(query.radius))
  if (query.service_type) params.set('service_type', query.service_type)
  const district = query.district?.trim()
  if (district) params.set('district', district)
  const taluka = query.taluka?.trim()
  if (taluka) params.set('taluka', taluka)

  return apiRequest<NearbyService[]>(`/services/nearby?${params.toString()}`, {}, token)
}

/** "GOVERNMENT_SCHEME" -> "Government Scheme" */
export function formatLabel(value: string) {
  return value
    .replace(/_/g, ' ')
    .toLowerCase()
    .replace(/(^|\s)\w/g, (char) => char.toUpperCase())
}