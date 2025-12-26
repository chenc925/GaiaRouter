import apiClient from '@/utils/request'
import type { ApiKey, CreateApiKeyRequest, UpdateApiKeyRequest } from '@/types/apiKey'
import type { ListResponse } from '@/types/api'
import type { KeyStatsResponse } from '@/types/stats'

export const apiKeysApi = {
  getList: (params?: {
    page?: number
    limit?: number
    status?: string
    search?: string
    organization_id?: string
  }) => {
    return apiClient.get<ListResponse<ApiKey>>('/v1/api-keys', { params })
  },

  getDetail: (id: string) => {
    return apiClient.get<ApiKey>(`/v1/api-keys/${id}`)
  },

  create: (data: CreateApiKeyRequest) => {
    return apiClient.post<ApiKey>('/v1/api-keys', data)
  },

  update: (id: string, data: UpdateApiKeyRequest) => {
    return apiClient.patch<ApiKey>(`/v1/api-keys/${id}`, data)
  },

  delete: (id: string) => {
    return apiClient.delete(`/v1/api-keys/${id}`)
  },

  getStats: (
    id: string,
    params?: {
      start_date?: string
      end_date?: string
      group_by?: string
    }
  ) => {
    return apiClient.get<KeyStatsResponse>(`/v1/api-keys/${id}/stats`, { params })
  }
}
