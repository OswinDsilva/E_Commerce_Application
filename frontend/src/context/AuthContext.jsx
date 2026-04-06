import React, { createContext, useContext, useEffect, useState } from 'react'
import { getCurrentUser, isBackendUnavailableError, loginUser, logoutUser, registerUser } from '../services/api'

const AuthContext = createContext(null)

const USER_STORAGE_KEY = 'atelier_user'
const AUTH_MODE_STORAGE_KEY = 'atelier_auth_mode'

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    const stored = localStorage.getItem('atelier_user')
    return stored ? JSON.parse(stored) : null
  })
  const [authMode, setAuthMode] = useState(() => localStorage.getItem(AUTH_MODE_STORAGE_KEY) || 'mock')

  useEffect(() => {
    let active = true

    const hydrateUser = async () => {
      try {
        const currentUser = await getCurrentUser()
        if (!active) return

        setUser(currentUser)
        setAuthMode('backend')
        localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(currentUser))
        localStorage.setItem(AUTH_MODE_STORAGE_KEY, 'backend')
      } catch (error) {
        if (!active) return

        const storedUser = localStorage.getItem(USER_STORAGE_KEY)
        const storedMode = localStorage.getItem(AUTH_MODE_STORAGE_KEY)

        if (storedUser && storedMode === 'mock') {
          setUser(JSON.parse(storedUser))
          setAuthMode('mock')
          return
        }

        if (!isBackendUnavailableError(error)) {
          setUser(null)
          setAuthMode('mock')
          localStorage.removeItem(USER_STORAGE_KEY)
          localStorage.removeItem(AUTH_MODE_STORAGE_KEY)
        }
      }
    }

    hydrateUser()

    return () => {
      active = false
    }
  }, [])

  const persistUser = (userData, mode) => {
    setUser(userData)
    setAuthMode(mode)
    localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(userData))
    localStorage.setItem(AUTH_MODE_STORAGE_KEY, mode)
  }

  const login = async (credentials) => {
    try {
      const currentUser = await loginUser(credentials)
      persistUser(currentUser, 'backend')
      return currentUser
    } catch (error) {
      if (!isBackendUnavailableError(error)) {
        throw error
      }

      const fallbackUser = {
        u_id: 1,
        username: credentials.username,
        email: `${credentials.username}@example.com`,
        role: credentials.username.toLowerCase() === 'admin' ? 'ADMIN' : 'USER',
      }
      persistUser(fallbackUser, 'mock')
      return fallbackUser
    }
  }

  const register = async (payload) => {
    try {
      const currentUser = await registerUser(payload)
      persistUser(currentUser, 'backend')
      return currentUser
    } catch (error) {
      if (!isBackendUnavailableError(error)) {
        throw error
      }

      const fallbackUser = {
        u_id: Date.now(),
        username: payload.username,
        email: payload.email,
        phone: payload.phone,
        role: 'USER',
      }
      persistUser(fallbackUser, 'mock')
      return fallbackUser
    }
  }

  const logout = async () => {
    if (authMode === 'backend') {
      try {
        await logoutUser()
      } catch {
        // Ignore backend logout errors and clear the local session either way.
      }
    }

    setUser(null)
    setAuthMode('mock')
    localStorage.removeItem(USER_STORAGE_KEY)
    localStorage.removeItem(AUTH_MODE_STORAGE_KEY)
  }

  const isAdmin = user?.role === 'ADMIN'

  return (
    <AuthContext.Provider value={{ user, authMode, login, register, logout, isAdmin }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)
