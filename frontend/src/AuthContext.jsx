import { createContext, useContext, useEffect, useState, useCallback } from 'react'
import { api, getToken, setToken, getStoredUser, setStoredUser } from './api.js'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => getStoredUser())
  const [ready, setReady] = useState(false)

  useEffect(() => {
    let cancelled = false
    async function init() {
      if (!getToken()) {
        setReady(true)
        return
      }
      try {
        const me = await api.authGet('/api/auth/me')
        if (!cancelled) {
          setUser(me)
          setStoredUser(me)
        }
      } catch {
        if (!cancelled) {
          setUser(null)
          setToken('')
          setStoredUser(null)
        }
      } finally {
        if (!cancelled) setReady(true)
      }
    }
    init()
    return () => {
      cancelled = true
    }
  }, [])

  const login = useCallback(async (username, password) => {
    const data = await api.post('/api/auth/login', { username, password })
    setToken(data.access_token)
    setUser(data.user)
    setStoredUser(data.user)
    return data.user
  }, [])

  const register = useCallback(async (username, password, nickname) => {
    const body = { username, password }
    if (nickname) body.nickname = nickname
    const data = await api.post('/api/auth/register', body)
    setToken(data.access_token)
    setUser(data.user)
    setStoredUser(data.user)
    return data.user
  }, [])

  const logout = useCallback(() => {
    setToken('')
    setStoredUser(null)
    setUser(null)
  }, [])

  return (
    <AuthContext.Provider value={{ user, ready, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  return useContext(AuthContext)
}
