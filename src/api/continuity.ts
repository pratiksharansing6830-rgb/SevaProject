import { apiRequest } from './client'

export type Family = {
  id: string
  family_reference_id: string
  family_name: string
  contact_mobile: string
  current_district: string
  current_taluka: string
  current_village_or_city: string
  current_address: string | null
  preferred_language: string
}

export type Child = {
  id: string
  family_id: string
  first_name: string
  last_name: string
  date_of_birth: string
  gender: string
  education_status: string
  current_class: string | null
  preferred_language: string
  disability_or_inclusion_requirement: string | null
}

export type Migration = {
  id: string
  family_id: string
  from_district: string
  from_taluka: string
  from_location: string
  to_district: string
  to_taluka: string
  to_location: string
  migration_date: string
  migration_reason: string | null
  status: 'PLANNED' | 'ACTIVE' | 'COMPLETED'
}

export type ServiceType = 'EDUCATION' | 'HEALTHCARE' | 'NUTRITION' | 'PROTECTION' | 'WELLBEING' | 'INCLUSION'
export type ServiceStatus = 'CONNECTED' | 'PENDING' | 'FOLLOW_UP_RECOMMENDED' | 'NOT_AVAILABLE' | 'REVIEW_REQUIRED'

export type ServiceContinuity = {
  id: string
  child_id: string
  migration_id: string | null
  service_type: ServiceType
  status: ServiceStatus
  reason: string | null
  action_required: boolean
  assigned_role: string | null
  due_date: string | null
  notes: string | null
}

export type ContinuitySummary = {
  child_id: string
  child_name: string
  overall_status: 'CONNECTED' | 'FOLLOW_UP_RECOMMENDED' | 'REVIEW_REQUIRED'
  services: ServiceContinuity[]
  follow_up_count: number
}

export type FollowUp = {
  id: string
  family_id: string
  child_id: string | null
  service_continuity_id: string | null
  title: string
  description: string | null
  status: 'OPEN' | 'IN_PROGRESS' | 'COMPLETED' | 'CANCELLED'
  priority: 'LOW' | 'MEDIUM' | 'HIGH'
  due_date: string | null
  assigned_role: string | null
}

export type ServiceRecord = Record<string, string | boolean | null> & { id?: string; child_id?: string }

export const listFamilies = (token: string) => apiRequest<Family[]>('/families', {}, token)
export const getFamily = (familyId: string, token: string) => apiRequest<Family>(`/families/${familyId}`, {}, token)
export const createFamily = (payload: object, token: string) => apiRequest<Family>('/families', { method: 'POST', body: JSON.stringify(payload) }, token)
export const updateFamily = (familyId: string, payload: object, token: string) => apiRequest<Family>(`/families/${familyId}`, { method: 'PUT', body: JSON.stringify(payload) }, token)
export const listChildren = (familyId: string, token: string) => apiRequest<Child[]>(`/families/${familyId}/children`, {}, token)
export const getChild = (childId: string, token: string) => apiRequest<Child>(`/children/${childId}`, {}, token)
export const createChild = (familyId: string, payload: object, token: string) => apiRequest<Child>(`/families/${familyId}/children`, { method: 'POST', body: JSON.stringify(payload) }, token)
export const listMigrations = (familyId: string, token: string) => apiRequest<Migration[]>(`/families/${familyId}/migrations`, {}, token)
export const createMigration = (familyId: string, payload: object, token: string) => apiRequest<Migration>(`/families/${familyId}/migrations`, { method: 'POST', body: JSON.stringify(payload) }, token)
export const getContinuity = (childId: string, token: string) => apiRequest<ContinuitySummary>(`/children/${childId}/continuity`, {}, token)
export const checkContinuity = (childId: string, token: string) => apiRequest<ServiceContinuity[]>(`/children/${childId}/continuity/check`, { method: 'POST' }, token)
export const listFollowups = (familyId: string, token: string) => apiRequest<FollowUp[]>(`/families/${familyId}/followups`, {}, token)
export const updateFollowup = (followupId: string, payload: object, token: string) => apiRequest<FollowUp>(`/followups/${followupId}`, { method: 'PUT', body: JSON.stringify(payload) }, token)

export function getServiceRecord(childId: string, service: string, token: string) {
  return apiRequest<ServiceRecord | null>(`/children/${childId}/${service}`, {}, token)
}

export function saveServiceRecord(childId: string, service: string, recordId: string | undefined, payload: object, token: string) {
  const endpoint = recordId ? `/${service}/${recordId}` : `/children/${childId}/${service}`
  return apiRequest<ServiceRecord>(endpoint, { method: recordId ? 'PUT' : 'POST', body: JSON.stringify(payload) }, token)
}