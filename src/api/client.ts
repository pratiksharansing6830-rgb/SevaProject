export const API_BASE_URL = import.meta.env.VITE_API_URL || '/api/v1'

export type ApiError = {
  detail?: string
  message?: string
}

async function handleResponse<T>(response: Response): Promise<T> {
  const contentType = response.headers.get('content-type') || ''
  const isJson = contentType.includes('application/json')
  const payload = isJson ? await response.json() : await response.text()

  if (!response.ok) {
    const detail = typeof payload === 'object' && payload && 'detail' in payload ? payload.detail : null
    const validationMessage = Array.isArray(detail)
      ? detail.map((item) => typeof item === 'object' && item && 'msg' in item ? String(item.msg) : '').filter(Boolean).join(' ')
      : typeof detail === 'string' ? detail : ''
    const statusMessage: Record<number, string> = {
      401: 'Your session has expired. Please sign in again.',
      403: 'You do not have permission to access this information.',
      404: 'The requested record could not be found.',
      422: validationMessage || 'Please check the information and try again.',
      500: 'Something went wrong. Please try again later.',
    }
    throw new Error(statusMessage[response.status] || validationMessage || 'Request failed. Please try again.')
  }

  return payload as T
}

export async function apiRequest<T>(endpoint: string, options: RequestInit = {}, token?: string): Promise<T> {
  const headers = new Headers(options.headers || {})
  headers.set('Content-Type', 'application/json')

  if (token) {
    headers.set('Authorization', `Bearer ${token}`)
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  })

  return handleResponse<T>(response)
}
