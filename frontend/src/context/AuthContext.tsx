import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
  ReactNode,
} from 'react'
import { api } from '../api/client'

type User = {
  username: string
}

type AuthContextValue = {
  user: User | null
  token: string | null
  login: (token: string) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(
    () => localStorage.getItem('token'),
  )
  const [user, setUser] = useState<User | null>(null)

  const fetchCurrentUser = useCallback(async (overrideToken?: string) => {
    const effectiveToken = overrideToken ?? localStorage.getItem('token')

    // #region agent log
    fetch('http://127.0.0.1:7242/ingest/6306f29d-08bd-41b8-b534-9c6611085768', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        id: `log_${Date.now()}_fetch_enter`,
        runId: 'auth_debug',
        hypothesisId: 'H1',
        location: 'AuthContext.tsx:fetchCurrentUser',
        message: 'fetchCurrentUser called',
        data: {
          hasOverrideToken: !!overrideToken,
          hasEffectiveToken: !!effectiveToken,
        },
        timestamp: Date.now(),
      }),
    }).catch(() => {})
    // #endregion agent log

    if (!effectiveToken) {
      // #region agent log
      fetch('http://127.0.0.1:7242/ingest/6306f29d-08bd-41b8-b534-9c6611085768', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          id: `log_${Date.now()}_fetch_skip`,
          runId: 'auth_debug',
          hypothesisId: 'H1',
          location: 'AuthContext.tsx:fetchCurrentUser',
          message: 'fetchCurrentUser early return due to missing token',
          data: {},
          timestamp: Date.now(),
        }),
      }).catch(() => {})
      // #endregion agent log
      return
    }
    try {
      const res = await api.get<{ username: string }>('/users/me')
      // #region agent log
      fetch('http://127.0.0.1:7242/ingest/6306f29d-08bd-41b8-b534-9c6611085768', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          id: `log_${Date.now()}_fetch_success`,
          runId: 'auth_debug',
          hypothesisId: 'H1',
          location: 'AuthContext.tsx:fetchCurrentUser',
          message: 'fetchCurrentUser succeeded',
          data: { username: res.data.username },
          timestamp: Date.now(),
        }),
      }).catch(() => {})
      // #endregion agent log
      setUser({ username: res.data.username })
    } catch {
      setToken(null)
      setUser(null)
      localStorage.removeItem('token')
    }
  }, [])

  useEffect(() => {
    void fetchCurrentUser()
  }, [fetchCurrentUser])

  const login = useCallback(async (newToken: string) => {
    // #region agent log
    fetch('http://127.0.0.1:7242/ingest/6306f29d-08bd-41b8-b534-9c6611085768', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        id: `log_${Date.now()}_login_start`,
        runId: 'auth_debug',
        hypothesisId: 'H1',
        location: 'AuthContext.tsx:login',
        message: 'login called',
        data: {
          hasExistingStateToken: !!token,
          hasExistingStorageToken: !!localStorage.getItem('token'),
          hasNewToken: !!newToken,
        },
        timestamp: Date.now(),
      }),
    }).catch(() => {})
    // #endregion agent log

    localStorage.setItem('token', newToken)
    setToken(newToken)
    await fetchCurrentUser(newToken)
  }, [fetchCurrentUser])

  const logout = useCallback(() => {
    localStorage.removeItem('token')
    setToken(null)
    setUser(null)
  }, [])

  return (
    <AuthContext.Provider value={{ user, token, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return ctx
}

