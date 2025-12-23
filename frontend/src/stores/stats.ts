import { defineStore } from 'pinia'
import { ref } from 'vue'
import { statsApi } from '@/api/stats'
import type { GlobalStatsResponse, KeyStatsResponse } from '@/types/stats'

export const useStatsStore = defineStore('stats', () => {
  const globalStats = ref<GlobalStatsResponse | null>(null)
  const organizationStats = ref<Record<string, KeyStatsResponse>>({})
  const apiKeyStats = ref<Record<string, KeyStatsResponse>>({})
  const loading = ref(false)

  const fetchGlobalStats = async (params?: {
    start_date?: string
    end_date?: string
    group_by?: string
  }) => {
    loading.value = true
    try {
      globalStats.value = await statsApi.getGlobalStats(params)
    } finally {
      loading.value = false
    }
  }

  const fetchOrganizationStats = async (id: string, params?: {
    start_date?: string
    end_date?: string
    group_by?: string
  }) => {
    loading.value = true
    try {
      const stats = await statsApi.getKeyStats(id, params)
      organizationStats.value[id] = stats
    } finally {
      loading.value = false
    }
  }

  const fetchApiKeyStats = async (keyId: string, params?: {
    start_date?: string
    end_date?: string
    group_by?: string
  }) => {
    loading.value = true
    try {
      const stats = await statsApi.getKeyStats(keyId, params)
      apiKeyStats.value[keyId] = stats
    } finally {
      loading.value = false
    }
  }

  return {
    globalStats,
    organizationStats,
    apiKeyStats,
    loading,
    fetchGlobalStats,
    fetchOrganizationStats,
    fetchApiKeyStats
  }
})

