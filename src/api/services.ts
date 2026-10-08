import { apiRequest } from './client'

export const DISCOVERY_SERVICE_TYPES = [
  'EDUCATION',
  'HEALTHCARE',
  'NUTRITION',
  'PROTECTION',
  'CHILD_SUPPORT',
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

// ---- Continuity -> discovery mapping -------------------------------------------------------
// Mirror of backend/app/services/discovery_mapping.py (the backend copy is the tested one).
// This only chooses WHICH kind of public service to look for. Part 3 decides status and
// action_required; nothing about continuity is calculated here.
const CONTINUITY_TO_DISCOVERY: Record<string, DiscoveryServiceType> = {
  EDUCATION: 'EDUCATION',
  HEALTHCARE: 'HEALTHCARE',
  NUTRITION: 'NUTRITION',
  PROTECTION: 'CHILD_SUPPORT',
  WELLBEING: 'WELLBEING',
  INCLUSION: 'INCLUSION',
  GOVERNMENT_SCHEME: 'GOVERNMENT_SCHEME',
  SOCIAL_SUPPORT: 'SOCIAL_SUPPORT',
  DOCUMENTATION: 'DOCUMENTATION',
  HOUSING_SUPPORT: 'HOUSING_SUPPORT',
}

const DISCOVERY_ACTION_STATUSES = ['PENDING', 'FOLLOW_UP_RECOMMENDED', 'REVIEW_REQUIRED', 'NOT_AVAILABLE']

export function discoveryServiceType(continuityServiceType: string): DiscoveryServiceType | null {
  return CONTINUITY_TO_DISCOVERY[(continuityServiceType || '').toUpperCase()] ?? null
}

export function needsDiscoveryAction(status: string, actionRequired?: boolean | null) {
  return Boolean(actionRequired) || DISCOVERY_ACTION_STATUSES.includes((status || '').toUpperCase())
}

/** Map URL carrying only a service type and an optional place name. No child or family data. */
export function discoveryPath(continuityServiceType: string, place?: string | null) {
  const target = discoveryServiceType(continuityServiceType)
  if (!target) return '/map'
  const params = new URLSearchParams({ service_type: target })
  if (place) params.set('place', place)
  return `/map?${params.toString()}`
}

// ---- DEMO labelling -----------------------------------------------------------------------
export function isDemoOrganization(service: Pick<NearbyService, 'organization_name'>) {
  return /\bDEMO\b/.test(service.organization_name)
}

export function verificationLabel(service: Pick<NearbyService, 'organization_name' | 'is_verified'>) {
  const status = service.is_verified ? 'Verified' : 'Not verified'
  return isDemoOrganization(service) ? `DEMO — ${status}` : status
}