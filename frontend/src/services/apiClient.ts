import axios, { AxiosError } from 'axios'
import { env } from '../config/env'

export const TOKEN_KEY = 'medikiosk_access_token'

// Normalize baseURL so it always targets /api/v1 regardless of env.apiBaseUrl formatting
const normalizedBaseUrl = env.apiBaseUrl.endsWith('/api/v1')
  ? env.apiBaseUrl
  : `${env.apiBaseUrl.replace(/\/+$/, '')}/api/v1`

/**
 * Global Axios instance configured with base URL, standard headers,
 * and automatic JWT Bearer token attachment.
 */
export const apiClient = axios.create({
  baseURL: normalizedBaseUrl,
  headers: {
    'Content-Type': 'application/json',
    Accept: 'application/json',
  },
  timeout: 60000, // AI/LLM calls can take up to 15s + face verification 25s
})

// Request Interceptor: Attach JWT Token from storage
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem(TOKEN_KEY)
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error),
)

// Response Interceptor: Normalize error messages from FastAPI
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError<{ detail?: string | Array<{ msg: string }> }>) => {
    let message = 'An unexpected error occurred'
    if (error.response?.data) {
      const data = error.response.data
      if (typeof data.detail === 'string') {
        message = data.detail
      } else if (Array.isArray(data.detail) && data.detail.length > 0) {
        message = data.detail.map((d) => d.msg).join(', ')
      }
    } else if (error.message) {
      message = error.message
    }
    return Promise.reject(new Error(message))
  },
)

export default apiClient

