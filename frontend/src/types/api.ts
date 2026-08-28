// Response shapes returned by the MediKiosk backend API (Phase 1).

export interface HealthResponse {
  status: string
  service: string
  version: string
  environment: string
  timestamp: string
  checks: {
    database: string
  }
}

export interface PublicConfig {
  app_name: string
  environment: string
  api_version: string
}
