import { defineStore } from 'pinia'
import { ref } from 'vue'
import { organizationsApi } from '@/api/organizations'
import type { Organization, CreateOrganizationRequest, UpdateOrganizationRequest } from '@/types/organization'
import type { Pagination } from '@/types/api'

export const useOrganizationStore = defineStore('organizations', () => {
  const organizations = ref<Organization[]>([])
  const currentOrganization = ref<Organization | null>(null)
  const loading = ref(false)
  const pagination = ref<Pagination>({
    page: 1,
    limit: 20,
    total: 0,
    pages: 0
  })

  const fetchOrganizations = async (params?: {
    page?: number
    limit?: number
    status?: string
    search?: string
  }) => {
    loading.value = true
    try {
      const response = await organizationsApi.getList(params)
      organizations.value = response.data
      pagination.value = response.pagination
    } finally {
      loading.value = false
    }
  }

  const fetchOrganization = async (id: string) => {
    loading.value = true
    try {
      currentOrganization.value = await organizationsApi.getDetail(id)
    } finally {
      loading.value = false
    }
  }

  const createOrganization = async (data: CreateOrganizationRequest) => {
    loading.value = true
    try {
      const org = await organizationsApi.create(data)
      organizations.value.unshift(org)
      return org
    } finally {
      loading.value = false
    }
  }

  const updateOrganization = async (id: string, data: UpdateOrganizationRequest) => {
    loading.value = true
    try {
      const org = await organizationsApi.update(id, data)
      const index = organizations.value.findIndex(o => o.id === id)
      if (index !== -1) {
        organizations.value[index] = org
      }
      if (currentOrganization.value?.id === id) {
        currentOrganization.value = org
      }
      return org
    } finally {
      loading.value = false
    }
  }

  const deleteOrganization = async (id: string) => {
    loading.value = true
    try {
      await organizationsApi.delete(id)
      organizations.value = organizations.value.filter(o => o.id !== id)
      if (currentOrganization.value?.id === id) {
        currentOrganization.value = null
      }
    } finally {
      loading.value = false
    }
  }

  return {
    organizations,
    currentOrganization,
    loading,
    pagination,
    fetchOrganizations,
    fetchOrganization,
    createOrganization,
    updateOrganization,
    deleteOrganization
  }
})

