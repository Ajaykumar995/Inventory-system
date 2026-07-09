import api from './api'
import type { User } from '../types/auth'

export interface PagedUsers {
  items: User[]
  total: number
  page: number
  page_size: number
}

export interface RoleOption {
  name: string
  description: string
}

export const authService = {
  login: (data: { username: string; password: string }) => api.post('/auth/login', data),
  register: (data: import('../types/auth').RegisterRequest) => api.post<User>('/auth/register', data),
  me: () => api.get<User>('/auth/me'),
  updateMe: (data: { email?: string; full_name?: string; phone?: string }) =>
    api.put<User>('/auth/me', data),
  listUsers: (params?: { page?: number; page_size?: number }) =>
    api.get<PagedUsers>('/auth/users', { params }),
  listRoles: () => api.get<RoleOption[]>('/auth/roles'),
  createUser: (data: {
    email: string
    username: string
    password: string
    full_name: string
    phone?: string
    role_name: string
  }) => api.post<User>('/auth/users', data),
  updateUser: (id: number, data: {
    email?: string
    full_name?: string
    phone?: string
    is_active?: boolean
    role_name?: string
  }) => api.put<User>(`/auth/users/${id}`, data),
  logout: () => { localStorage.clear() },
}
