export interface Role {
  id: number
  name: string
  description?: string
}

export interface User {
  id: number
  email: string
  username: string
  full_name: string
  phone?: string
  is_active: boolean
  is_verified: boolean
  role: Role
  created_at: string
  last_login?: string
}

export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
}

export interface LoginRequest {
  username: string
  password: string
}

export interface RegisterRequest {
  email: string
  username: string
  password: string
  full_name: string
  phone?: string
  role_name?: string
}
