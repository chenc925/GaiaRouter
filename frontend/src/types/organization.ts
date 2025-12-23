export interface Organization {
  id: string
  name: string
  description?: string
  admin_user_id?: string
  status: 'active' | 'inactive'
  monthly_requests_limit?: number
  monthly_tokens_limit?: number
  monthly_cost_limit?: number
  created_at: string
  updated_at: string
}

export interface CreateOrganizationRequest {
  name: string
  description?: string
  monthly_requests_limit?: number
  monthly_tokens_limit?: number
  monthly_cost_limit?: number
}

export interface UpdateOrganizationRequest {
  name?: string
  description?: string
  admin_user_id?: string
  status?: 'active' | 'inactive'
  monthly_requests_limit?: number
  monthly_tokens_limit?: number
  monthly_cost_limit?: number
}

