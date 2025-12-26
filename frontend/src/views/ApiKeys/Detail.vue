<template>
  <div class="api-key-detail">
    <a-page-header
      title="API Key 详情"
      @back="$router.push('/api-keys')"
    >
      <template #extra>
        <a-space>
          <a-button @click="$router.push(`/stats/api-keys/${apiKeyId}`)">
            查看统计
          </a-button>
        </a-space>
      </template>
    </a-page-header>

    <a-card v-if="apiKey" :loading="apiKeyStore.loading">
      <a-descriptions :column="2" bordered>
        <a-descriptions-item label="API Key ID">
          {{ apiKey.id }}
        </a-descriptions-item>
        <a-descriptions-item label="名称">
          {{ apiKey.name }}
        </a-descriptions-item>
        <a-descriptions-item label="API Key" :span="2">
          <a-space>
            <span class="api-key-value" v-if="apiKey.key">{{ maskApiKey(apiKey.key) }}</span>
            <span v-else>-</span>
            <a-button
              v-if="apiKey.key"
              type="text"
              size="small"
              @click="copyKey(apiKey.key)"
            >
              复制
            </a-button>
          </a-space>
        </a-descriptions-item>
        <a-descriptions-item label="描述" :span="2">
          {{ apiKey.description || '-' }}
        </a-descriptions-item>
        <a-descriptions-item label="权限" :span="2">
          <a-space>
            <a-tag v-for="perm in apiKey.permissions" :key="perm">
              {{ perm }}
            </a-tag>
          </a-space>
        </a-descriptions-item>
        <a-descriptions-item label="状态">
          <a-tag :color="getStatusColor(apiKey.status)">
            {{ getStatusText(apiKey.status) }}
          </a-tag>
        </a-descriptions-item>
        <a-descriptions-item label="所属组织">
          {{ apiKey.organization_id }}
        </a-descriptions-item>
        <a-descriptions-item label="最后使用时间">
          {{ apiKey.last_used_at || '从未使用' }}
        </a-descriptions-item>
        <a-descriptions-item label="创建时间">
          {{ apiKey.created_at }}
        </a-descriptions-item>
      </a-descriptions>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useApiKeyStore } from '@/stores/apiKeys'
import { Message } from '@arco-design/web-vue'

const route = useRoute()
const router = useRouter()
const apiKeyStore = useApiKeyStore()

const apiKeyId = computed(() => route.params.id as string)
const apiKey = computed(() => apiKeyStore.currentApiKey)

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
  if (apiKeyId.value) {
    await apiKeyStore.fetchApiKey(apiKeyId.value)
  }
})
</script>

<style scoped>
.api-key-detail {
  padding: 0;
}

.api-key-value {
  font-family: SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace;
  font-size: 13px;
}
</style>

