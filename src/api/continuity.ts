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
  created_at: string
  updated_at: string
}

export type ServiceType = 'EDUCATION' | 'HEALTHCARE' | 'NUTRITION' | 'PROTECTION' | 'WELLBEING' | 'INCLUSION'
export type ServiceStatus = 'CONNECTED' | 'PENDING' | 'FOLLOW_UP_REQUIRED' | 'SUPPORT_NOT_REQUIRED' | 'REVIEW_REQUIRED'
export type ConfirmationMethod = 'FAMILY_REPORT' | 'SERVICE_PROVIDER' | 'DOCUMENT_REVIEW' | 'IN_PERSON' | 'OTHER'

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
  outcome_confirmed_by_user_id: string | null
  outcome_confirmed_at: string | null
  confirmation_method: ConfirmationMethod | null
  supporting_reference: string | null
}

export type ContinuitySummary = {
  child_id: string
  child_name: string
  overall_status: 'CONNECTED' | 'SUPPORT_NOT_REQUIRED' | 'FOLLOW_UP_REQUIRED' | 'REVIEW_REQUIRED'
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

export type FollowUpPayload = {
  child_id: string
  service_continuity_id: string
  title: string
  description: string
  status: 'OPEN' | 'IN_PROGRESS' | 'COMPLETED'
  due_date: string | null
}

export type GovernmentDashboard = {
  as_of: string
  privacy: {
    aggregate_only: boolean
    geographic_suppression_threshold: number
    small_geographic_groups_suppressed: boolean
  }
  profile_counts: {
    family_count: number
    child_count: number
  }
  migration_counts: Record<'PLANNED' | 'ACTIVE' | 'COMPLETED', number>
  unresolved_needs_by_service: {
    service_type: ServiceType
    pending: number
    follow_up_required: number
    review_required: number
    total: number
  }[]
  followups: {
    open_or_in_progress: number
    due_today: number
    overdue: number
  }
  destination_service_gaps: {
    district: string
    service_type: ServiceType
    unresolved_need_count: number
    affected_child_count: number
  }[]
  migration_trend: {
    month: string
    migration_count: number
    family_count: number
  }[]
}

export type ServiceRecord = Record<string, string | boolean | null> & { id?: string; child_id?: string }

export const listFamilies = (token: string) => apiRequest<Family[]>('/families', {}, token)
export const getFamily = (familyId: string, token: string) => apiRequest<Family>(`/families/${familyId}`, {}, token)
export const createFamily = (payload: object, token: string) => apiRequest<Family>('/families', { method: 'POST', body: JSON.stringify(payload) }, token)
export const updateFamily = (familyId: string, payload: object, token: string) => apiRequest<Family>(`/families/${familyId}`, { method: 'PUT', body: JSON.stringify(payload) }, token)
export const listChildren = (familyId: string, token: string) => apiRequest<Child[]>(`/families/${familyId}/children`, {}, token)
export const getChild = (childId: string, token: string) => apiRequest<Child>(`/children/${childId}`, {}, token)
export const createChild = (familyId: string, payload: object, token: string) => apiRequest<Child>(`/families/${familyId}/children`, { method: 'POST', body: JSON.stringify(payload) }, token)
export const updateChild = (childId: string, payload: object, token: string) => apiRequest<Child>(`/children/${childId}`, { method: 'PUT', body: JSON.stringify(payload) }, token)
export const listMigrations = (familyId: string, token: string) => apiRequest<Migration[]>(`/families/${familyId}/migrations`, {}, token)
export const createMigration = (familyId: string, payload: object, token: string) => apiRequest<Migration>(`/families/${familyId}/migrations`, { method: 'POST', body: JSON.stringify(payload) }, token)
export const updateMigration = (migrationId: string, payload: object, token: string) => apiRequest<Migration>(`/migrations/${migrationId}`, { method: 'PUT', body: JSON.stringify(payload) }, token)
export const getContinuity = (childId: string, token: string) => apiRequest<ContinuitySummary>(`/children/${childId}/continuity`, {}, token)
export const checkContinuity = (childId: string, token: string) => apiRequest<ServiceContinuity[]>(`/children/${childId}/continuity/check`, { method: 'POST' }, token)
export const getGovernmentDashboard = (token: string) => apiRequest<GovernmentDashboard>('/government/dashboard', {}, token)
export const updateContinuity = (recordId: string, payload: { status: 'CONNECTED' | 'SUPPORT_NOT_REQUIRED'; confirmation_method: ConfirmationMethod; supporting_reference?: string }, token: string) =>
  apiRequest<ServiceContinuity>(`/continuity/${recordId}`, { method: 'PUT', body: JSON.stringify(payload) }, token)
export const listFollowups = (familyId: string, token: string) => apiRequest<FollowUp[]>(`/families/${familyId}/followups`, {}, token)
export const createFollowup = (familyId: string, payload: FollowUpPayload, token: string) =>
  apiRequest<FollowUp>(`/families/${familyId}/followups`, { method: 'POST', body: JSON.stringify(payload) }, token)
export const updateFollowup = (followupId: string, payload: object, token: string) => apiRequest<FollowUp>(`/followups/${followupId}`, { method: 'PUT', body: JSON.stringify(payload) }, token)

export function getServiceRecord(childId: string, service: string, token: string) {
  return apiRequest<ServiceRecord | null>(`/children/${childId}/${service}`, {}, token)
}

export function saveServiceRecord(childId: string, service: string, recordId: string | undefined, payload: object, token: string) {
  const endpoint = recordId ? `/${service}/${recordId}` : `/children/${childId}/${service}`
  return apiRequest<ServiceRecord>(endpoint, { method: recordId ? 'PUT' : 'POST', body: JSON.stringify(payload) }, token)
}