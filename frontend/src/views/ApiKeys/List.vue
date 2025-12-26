<template>
  <div class="api-keys-list">
    <a-page-header title="API Key 管理">
      <template #extra>
        <a-button type="primary" @click="$router.push('/api-keys/create')">
          <template #icon>
            <IconPlus />
          </template>
          创建 API Key
        </a-button>
      </template>
    </a-page-header>

    <a-card>
      <a-space direction="vertical" :size="16" style="width: 100%">
        <a-space>
          <a-input
            v-model="searchText"
            placeholder="搜索 API Key 名称"
            allow-clear
            style="width: 300px"
            @press-enter="handleSearch"
          />
          <a-select
            v-model="statusFilter"
            placeholder="状态筛选"
            allow-clear
            style="width: 150px"
            @change="handleSearch"
          >
            <a-option value="active"> 活跃 </a-option>
            <a-option value="inactive"> 停用 </a-option>
            <a-option value="expired"> 过期 </a-option>
          </a-select>
          <a-select
            v-model="organizationFilter"
            placeholder="组织筛选"
            allow-clear
            style="width: 200px"
            :loading="organizationStore.loading"
            @change="handleSearch"
          >
            <a-option v-for="org in organizationStore.organizations" :key="org.id" :value="org.id">
              {{ org.name }}
            </a-option>
          </a-select>
          <a-button type="primary" @click="handleSearch"> 搜索 </a-button>
        </a-space>

        <a-table
          :columns="columns"
          :data="apiKeyStore.apiKeys"
          :loading="apiKeyStore.loading"
          :pagination="paginationConfig"
          @page-change="handlePageChange"
          @page-size-change="handlePageSizeChange"
        >
          <template #key="{ record }">
            <a-space size="small">
              <span v-if="record.key" class="api-key-value">{{ maskApiKey(record.key) }}</span>
              <span v-else>-</span>
              <a-button v-if="record.key" type="text" size="mini" @click="copyKey(record.key)">
                复制
              </a-button>
            </a-space>
          </template>
          <template #status="{ record }">
            <a-tag :color="getStatusColor(record.status)">
              {{ getStatusText(record.status) }}
            </a-tag>
          </template>
          <template #operations="{ record }">
            <a-space>
              <a-button type="text" size="small" @click="handleView(record.id)"> 查看 </a-button>
              <a-popconfirm content="确定要删除这个 API Key 吗？" @ok="handleDelete(record.id)">
                <a-button type="text" size="small" status="danger"> 删除 </a-button>
              </a-popconfirm>
            </a-space>
          </template>
        </a-table>
      </a-space>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useApiKeyStore } from '@/stores/apiKeys'
import { useOrganizationStore } from '@/stores/organizations'
import { Message } from '@arco-design/web-vue'
import { IconPlus } from '@arco-design/web-vue/es/icon'

const router = useRouter()
const apiKeyStore = useApiKeyStore()
const organizationStore = useOrganizationStore()

const searchText = ref('')
const statusFilter = ref<string>()
const organizationFilter = ref<string>()

const columns = [
  { title: 'ID', dataIndex: 'id', width: 220 },
  { title: '名称', dataIndex: 'name', width: 180 },
  { title: 'API Key', slotName: 'key', width: 340 },
  { title: '描述', dataIndex: 'description', ellipsis: true },
  { title: '状态', slotName: 'status', width: 100 },
  { title: '最后使用', dataIndex: 'last_used_at', width: 180 },
  { title: '操作', slotName: 'operations', width: 150, fixed: 'right' }
]

const paginationConfig = computed(() => ({
  current: apiKeyStore.pagination.page,
  pageSize: apiKeyStore.pagination.limit,
  total: apiKeyStore.pagination.total,
  showTotal: true,
  showPageSize: true
}))

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

const handleSearch = () => {
  apiKeyStore.fetchApiKeys({
    page: 1,
    limit: apiKeyStore.pagination.limit,
    search: searchText.value || undefined,
    status: statusFilter.value,
    organization_id: organizationFilter.value
  })
}

const handlePageChange = (page: number) => {
  apiKeyStore.fetchApiKeys({
    page,
    limit: apiKeyStore.pagination.limit,
    search: searchText.value || undefined,
    status: statusFilter.value,
    organization_id: organizationFilter.value
  })
}

const handlePageSizeChange = (size: number) => {
  apiKeyStore.fetchApiKeys({
    page: 1,
    limit: size,
    search: searchText.value || undefined,
    status: statusFilter.value,
    organization_id: organizationFilter.value
  })
}

const handleView = (id: string) => {
  router.push(`/api-keys/${id}`)
}

const handleDelete = async (id: string) => {
  try {
    await apiKeyStore.deleteApiKey(id)
    Message.success('删除成功')
    handleSearch()
  } catch (error) {
    Message.error('删除失败')
  }
}

const maskApiKey = (key: string) => {
  if (!key || key.length < 8) return '****'
  // 显示前4个字符和后4个字符，中间用 * 隐藏
  return `${key.substring(0, 4)}${'*'.repeat(20)}${key.substring(key.length - 4)}`
}

const copyKey = (key: string) => {
  if (!key) return
  navigator.clipboard.writeText(key)
  Message.success('已复制 API Key')
}

onMounted(async () => {
  // 加载组织列表用于筛选
  await organizationStore.fetchOrganizations({ page: 1, limit: 1000 })
  handleSearch()
})
</script>

<style scoped>
.api-keys-list {
  padding: 0;
}

.api-key-value {
  font-family: SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace;
  font-size: 12px;
}
</style>
