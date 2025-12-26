<template>
  <div class="organization-detail">
    <a-page-header
      title="组织详情"
      @back="$router.push('/organizations')"
    >
      <template #extra>
        <a-space>
          <a-button @click="handleEdit">
            编辑
          </a-button>
          <a-button 
            type="primary" 
            :disabled="activeApiKeysCount > 0"
            @click="handleAssignApiKey"
          >
            <template #icon>
              <IconPlus />
            </template>
            分配 API Key
          </a-button>
          <a-button @click="$router.push(`/stats/organizations/${organizationId}`)">
            查看统计
          </a-button>
        </a-space>
      </template>
    </a-page-header>

    <a-card
      v-if="organization"
      :loading="organizationStore.loading"
    >
      <a-descriptions
        :column="2"
        bordered
      >
        <a-descriptions-item label="组织ID">
          {{ organization.id }}
        </a-descriptions-item>
        <a-descriptions-item label="名称">
          {{ organization.name }}
        </a-descriptions-item>
        <a-descriptions-item
          label="描述"
          :span="2"
        >
          {{ organization.description || '-' }}
        </a-descriptions-item>
        <a-descriptions-item label="管理员用户ID">
          {{ organization.admin_user_id || '-' }}
        </a-descriptions-item>
        <a-descriptions-item label="状态">
          <a-tag :color="organization.status === 'active' ? 'green' : 'red'">
            {{ organization.status === 'active' ? '活跃' : '停用' }}
          </a-tag>
        </a-descriptions-item>
        <a-descriptions-item label="月度请求次数限制">
          {{ organization.monthly_requests_limit || '无限制' }}
        </a-descriptions-item>
        <a-descriptions-item label="月度Token限制">
          {{ organization.monthly_tokens_limit || '无限制' }}
        </a-descriptions-item>
        <a-descriptions-item label="月度费用限制">
          {{ organization.monthly_cost_limit ? `¥${organization.monthly_cost_limit}` : '无限制' }}
        </a-descriptions-item>
        <a-descriptions-item label="创建时间">
          {{ organization.created_at }}
        </a-descriptions-item>
        <a-descriptions-item label="更新时间">
          {{ organization.updated_at }}
        </a-descriptions-item>
      </a-descriptions>
    </a-card>

    <a-card
      title="API Keys"
      style="margin-top: 16px"
    >
      <template #extra>
        <a-button 
          type="primary" 
          size="small" 
          :disabled="activeApiKeysCount > 0"
          @click="handleAssignApiKey"
        >
          <template #icon>
            <IconPlus />
          </template>
          分配 API Key
        </a-button>
      </template>
      <a-table
        :columns="apiKeyColumns"
        :data="organizationApiKeys"
        :loading="apiKeyStore.loading"
        :pagination="false"
      >
        <template #status="{ record }">
          <a-tag :color="getStatusColor(record.status)">
            {{ getStatusText(record.status) }}
          </a-tag>
        </template>
        <template #operations="{ record }">
          <a-space>
            <a-button
              type="text"
              size="small"
              @click="handleViewApiKey(record.id)"
            >
              查看
            </a-button>
            <a-popconfirm
              content="确定要删除这个 API Key 吗？"
              @ok="handleDeleteApiKey(record.id)"
            >
              <a-button
                type="text"
                size="small"
                status="danger"
              >
                删除
              </a-button>
            </a-popconfirm>
          </a-space>
        </template>
      </a-table>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useOrganizationStore } from '@/stores/organizations'
import { useApiKeyStore } from '@/stores/apiKeys'
import { Message } from '@arco-design/web-vue'
import { IconPlus } from '@arco-design/web-vue/es/icon'
import type { ApiKey } from '@/types/apiKey'

const route = useRoute()
const router = useRouter()
const organizationStore = useOrganizationStore()
const apiKeyStore = useApiKeyStore()

const organizationId = computed(() => route.params.id as string)
const organization = computed(() => organizationStore.currentOrganization)
const organizationApiKeys = ref<ApiKey[]>([])

// 计算活跃的API Key数量
const activeApiKeysCount = computed(() => {
  return organizationApiKeys.value.filter(key => key.status === 'active').length
})

const apiKeyColumns = [
  { title: 'ID', dataIndex: 'id', width: 200 },
  { title: '名称', dataIndex: 'name' },
  { title: '描述', dataIndex: 'description', ellipsis: true },
  { title: '状态', slotName: 'status', width: 100 },
  { title: '最后使用', dataIndex: 'last_used_at', width: 180 },
  { title: '操作', slotName: 'operations', width: 150, fixed: 'right' }
]

const getStatusColor = (status: string) => {
  const colors: Record<string, string> = {
    active: 'green',
    inactive: 'red',
    expired: 'orange'
  }
  return colors[status] || 'gray'
}

const getStatusText = (status: string) => {
  const texts: Record<string, string> = {
    active: '活跃',
    inactive: '停用',
    expired: '过期'
  }
  return texts[status] || status
}

const handleEdit = () => {
  router.push(`/organizations/${organizationId.value}/edit`)
}

const handleAssignApiKey = () => {
  router.push({
    path: '/api-keys/create',
    query: { organization_id: organizationId.value }
  })
}

const handleViewApiKey = (id: string) => {
  router.push(`/api-keys/${id}`)
}

const handleDeleteApiKey = async (id: string) => {
  try {
    await apiKeyStore.deleteApiKey(id)
    Message.success('删除成功')
    await loadOrganizationApiKeys()
  } catch (error) {
    Message.error('删除失败')
  }
}

const loadOrganizationApiKeys = async () => {
  try {
    const response = await apiKeyStore.fetchApiKeys({
      page: 1,
      limit: 1000,
      organization_id: organizationId.value
    })
    organizationApiKeys.value = response.data
  } catch (error) {
    console.error('Failed to load organization API keys', error)
  }
}

onMounted(async () => {
  if (organizationId.value) {
    await organizationStore.fetchOrganization(organizationId.value)
    await loadOrganizationApiKeys()
  }
})
</script>

<style scoped>
.organization-detail {
  padding: 0;
}
</style>

