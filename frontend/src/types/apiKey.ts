export interface ApiKey {
  id: string
  name: string
  description?: string
  key?: string
  permissions: string[]
  status: 'active' | 'inactive' | 'expired'
  organization_id: string
  organization_name?: string
  created_at: string
  expires_at?: string
  last_used_at?: string
  updated_at?: string
}

export interface CreateApiKeyRequest {
  organization_id: string
}

export interface UpdateApiKeyRequest {
  name?: string
  description?: string
  permissions?: string[]
  status?: 'active' | 'inactive'
  expires_at?: string
}

