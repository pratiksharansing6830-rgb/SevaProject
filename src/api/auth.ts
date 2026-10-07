import { apiRequest } from './client'

export type UserRole =
  | 'CITIZEN'
  | 'SCHOOL'
  | 'HEALTHCARE'
  | 'NGO_WORKER'
  | 'GOVERNMENT'
  | 'ADMIN'

export type UserProfile = {
  id: string
  full_name: string
  email: string
  mobile_number: string
  role: UserRole
  preferred_language: string
  is_active: boolean
  is_verified: boolean
}

export type AuthResponse = {
  access_token: string
  token_type: string
  user: UserProfile
}

export async function registerUser(data: {
  full_name: string
  email: string
  mobile_number: string
  password: string
  confirm_password: string
  role: 'CITIZEN' | 'SCHOOL' | 'HEALTHCARE' | 'NGO_WORKER'
  preferred_language: 'English' | 'Marathi' | 'Hindi'
}) {
  return apiRequest<UserProfile>('/auth/register', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export async function loginUser(identifier: string, password: string) {
  return apiRequest<AuthResponse>('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ identifier, password }),
  })
}

export async function getCurrentUser(token: string) {
  return apiRequest<UserProfile>('/auth/me', {}, token)
}
