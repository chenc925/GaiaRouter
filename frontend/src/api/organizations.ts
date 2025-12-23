import apiClient from '@/utils/request'
import type { Organization, CreateOrganizationRequest, UpdateOrganizationRequest } from '@/types/organization'
import type { ListResponse } from '@/types/api'
import type { KeyStatsResponse } from '@/types/stats'

export const organizationsApi = {
  getList: (params?: {
    page?: number
    limit?: number
    status?: string
    search?: string
  }) => {
    return apiClient.get<ListResponse<Organization>>('/v1/organizations', { params })
  },

  getDetail: (id: string) => {
    return apiClient.get<Organization>(`/v1/organizations/${id}`)
  },

  create: (data: CreateOrganizationRequest) => {
    return apiClient.post<Organization>('/v1/organizations', data)
  },

  update: (id: string, data: UpdateOrganizationRequest) => {
    return apiClient.patch<Organization>(`/v1/organizations/${id}`, data)
  },

  delete: (id: string) => {
    return apiClient.delete(`/v1/organizations/${id}`)
  },

  getStats: (id: string, params?: {
    start_date?: string
    end_date?: string
    group_by?: string
  }) => {
    return apiClient.get<KeyStatsResponse>(`/v1/organizations/${id}/stats`, { params })
  }
}

