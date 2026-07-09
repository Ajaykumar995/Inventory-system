import { createContext, useContext, useEffect, useState, type ReactNode } from 'react'
import { authService } from '../services/authService'
import type { User } from '../types/auth'

interface AuthContextType {
  user: User | null
  loading: boolean
  login: (username: string, password: string) => Promise<void>
  register: (data: { email: string; username: string; password: string; full_name: string }) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthContextType | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('access_token')
    if (token) {
      authService.me().then((r) => setUser(r.data)).catch(() => localStorage.clear()).finally(() => setLoading(false))
    } else setLoading(false)
  }, [])

  const login = async (username: string, password: string) => {
    const { data } = await authService.login({ username, password })
    localStorage.setItem('access_token', data.access_token)
    localStorage.setItem('refresh_token', data.refresh_token)
    const me = await authService.me()
    setUser(me.data)
  }

  const register = async (data: { email: string; username: string; password: string; full_name: string }) => {
    await authService.register(data)
    await login(data.username, data.password)
  }

  const logout = () => { authService.logout(); setUser(null) }

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
