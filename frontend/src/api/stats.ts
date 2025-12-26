import apiClient from '@/utils/request'
import type { GlobalStatsResponse, KeyStatsResponse } from '@/types/stats'

export const statsApi = {
  getGlobalStats: (params?: { start_date?: string; end_date?: string; group_by?: string }) => {
    return apiClient.get<GlobalStatsResponse>('/v1/stats', { params })
  },

  getKeyStats: (
    keyId: string,
    params?: {
      start_date?: string
      end_date?: string
      group_by?: string
    }
  ) => {
    return apiClient.get<KeyStatsResponse>(`/v1/api-keys/${keyId}/stats`, { params })
  }
}
