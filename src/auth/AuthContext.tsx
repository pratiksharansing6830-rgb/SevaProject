import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { getCurrentUser, loginUser, registerUser, type UserProfile } from '../api/auth'

type LoginPayload = { identifier: string; password: string }
type RegisterPayload = {
  full_name: string
  email: string
  mobile_number: string
  password: string
  confirm_password: string
  role: 'CITIZEN' | 'SCHOOL' | 'HEALTHCARE' | 'NGO_WORKER'
  preferred_language: 'English' | 'Marathi' | 'Hindi'
}

type AuthContextValue = {
  user: UserProfile | null
  token: string | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (payload: LoginPayload) => Promise<void>
  register: (payload: RegisterPayload) => Promise<void>
  logout: () => void
  refreshUser: () => Promise<void>
}

const AuthContext = createContext<AuthContextValue | null>(null)
const STORAGE_KEY = 'sahaayak-auth-token'
const USER_KEY = 'sahaayak-auth-user'

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [token, setToken] = useState<string | null>(() => localStorage.getItem(STORAGE_KEY))
  const [user, setUser] = useState<UserProfile | null>(() => {
    const storedUser = localStorage.getItem(USER_KEY)
    return storedUser ? (JSON.parse(storedUser) as UserProfile) : null
  })
  const [isLoading, setIsLoading] = useState(true)
  const navigate = useNavigate()

  const persistSession = useCallback((nextToken: string, nextUser: UserProfile) => {
    localStorage.setItem(STORAGE_KEY, nextToken)
    localStorage.setItem(USER_KEY, JSON.stringify(nextUser))
    setToken(nextToken)
    setUser(nextUser)
  }, [])

  const clearSession = useCallback(() => {
    localStorage.removeItem(STORAGE_KEY)
    localStorage.removeItem(USER_KEY)
    setToken(null)
    setUser(null)
  }, [])

  const refreshUser = useCallback(async () => {
    const activeToken = token ?? localStorage.getItem(STORAGE_KEY)
    if (!activeToken) {
      clearSession()
      setIsLoading(false)
      return
    }

    try {
      const currentUser = await getCurrentUser(activeToken)
      setUser(currentUser)
      localStorage.setItem(USER_KEY, JSON.stringify(currentUser))
    } catch (error) {
      console.error('Session refresh failed', error)
      clearSession()
    } finally {
      setIsLoading(false)
    }
  }, [clearSession, token])

  useEffect(() => {
    void refreshUser()
  }, [refreshUser])

  const login = useCallback(
    async (payload: LoginPayload) => {
      setIsLoading(true)
      try {
        const response = await loginUser(payload.identifier, payload.password)
        persistSession(response.access_token, response.user)
        navigate('/dashboard')
      } finally {
        setIsLoading(false)
      }
    },
    [navigate, persistSession],
  )

  const register = useCallback(async (payload: RegisterPayload) => {
    await registerUser(payload)
  }, [])

  const logout = useCallback(() => {
    clearSession()
    navigate('/login')
  }, [clearSession, navigate])

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      token,
      isAuthenticated: Boolean(user && token),
      isLoading,
      login,
      register,
      logout,
      refreshUser,
    }),
    [login, logout, refreshUser, token, user, isLoading, register],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used inside AuthProvider')
  }
  return context
}
