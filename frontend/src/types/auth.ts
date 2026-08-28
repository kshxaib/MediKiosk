export interface Role {
  id: string
  name: 'ADMIN' | 'DOCTOR' | string
  description?: string | null
}

export interface User {
  id: string
  hospital_id?: string | null
  full_name: string
  email: string
  phone?: string | null
  is_active: boolean
  role: Role
  created_at: string
  last_login_at?: string | null
}

export interface LoginCredentials {
  email: string
  password: string
}

export interface AuthTokens {
  access_token: string
  refresh_token: string
  token_type: string
}

export interface AuthResponse extends AuthTokens {
  user: User
}
