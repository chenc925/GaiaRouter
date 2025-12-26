import { defineStore } from 'pinia'
import { ref } from 'vue'
import { apiKeysApi } from '@/api/apiKeys'
import type { ApiKey, CreateApiKeyRequest, UpdateApiKeyRequest } from '@/types/apiKey'
import type { Pagination } from '@/types/api'

export const useApiKeyStore = defineStore('apiKeys', () => {
  const apiKeys = ref<ApiKey[]>([])
  const currentApiKey = ref<ApiKey | null>(null)
  const loading = ref(false)
  const pagination = ref<Pagination>({
    page: 1,
    limit: 20,
    total: 0,
    pages: 0
  })

  const fetchApiKeys = async (params?: {
    page?: number
    limit?: number
    status?: string
    search?: string
    organization_id?: string
  }) => {
    loading.value = true
    try {
      const response = await apiKeysApi.getList(params)
      apiKeys.value = response.data
      pagination.value = response.pagination
      return response
    } finally {
      loading.value = false
    }
  }

  const fetchApiKey = async (id: string) => {
    loading.value = true
    try {
      currentApiKey.value = await apiKeysApi.getDetail(id)
    } finally {
      loading.value = false
    }
  }

  const createApiKey = async (data: CreateApiKeyRequest) => {
    loading.value = true
    try {
      console.log('[Store] Creating API key with data:', data)
      const key = await apiKeysApi.create(data)
      console.log('[Store] Received from API:', key)
      console.log('[Store] Key field type:', typeof key.key)
      console.log('[Store] Key field value:', key.key)
      console.log('[Store] Full response:', JSON.stringify(key, null, 2))
      apiKeys.value.unshift(key)
      return key
    } finally {
      loading.value = false
    }
  }

  const updateApiKey = async (id: string, data: UpdateApiKeyRequest) => {
    loading.value = true
    try {
      const key = await apiKeysApi.update(id, data)
      const index = apiKeys.value.findIndex(k => k.id === id)
      if (index !== -1) {
        apiKeys.value[index] = key
      }
      if (currentApiKey.value?.id === id) {
        currentApiKey.value = key
      }
      return key
    } finally {
      loading.value = false
    }
  }

  const deleteApiKey = async (id: string) => {
    loading.value = true
    try {
      await apiKeysApi.delete(id)
      apiKeys.value = apiKeys.value.filter(k => k.id !== id)
      if (currentApiKey.value?.id === id) {
        currentApiKey.value = null
      }
    } finally {
      loading.value = false
    }
  }

  return {
    apiKeys,
    currentApiKey,
    loading,
    pagination,
    fetchApiKeys,
    fetchApiKey,
    createApiKey,
    updateApiKey,
    deleteApiKey
  }
})
