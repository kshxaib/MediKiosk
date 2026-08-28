import { apiRequest } from './apiClient'
import type { HealthResponse, PublicConfig } from '../types/api'

export function getHealth(): Promise<HealthResponse> {
  return apiRequest<HealthResponse>('/health')
}

export function getPublicConfig(): Promise<PublicConfig> {
  return apiRequest<PublicConfig>('/config/public')
}
