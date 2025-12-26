<template>
  <div class="api-key-form">
    <a-page-header
      :title="isEdit ? '编辑 API Key' : '创建 API Key'"
      @back="$router.back()"
    />

    <a-card>
      <a-form
        :model="form"
        :rules="rules"
        ref="formRef"
        layout="vertical"
      >
        <a-form-item v-if="!isEdit && !createdKey" field="organization_id" label="组织">
          <a-select
            v-model="form.organization_id"
            placeholder="请选择组织"
            :loading="organizationStore.loading"
            :disabled="!!organizationIdFromQuery"
          >
            <a-option
              v-for="org in organizationStore.organizations"
              :key="org.id"
              :value="org.id"
            >
              {{ org.name }}
            </a-option>
          </a-select>
        </a-form-item>
        <a-form-item v-if="createdKey" field="key" label="API Key（请妥善保存，仅显示一次）">
          <a-textarea
            :model-value="createdKey.key"
            readonly
            :auto-size="{ minRows: 2, maxRows: 4 }"
            style="font-family: 'SFMono-Regular', 'Menlo', 'Monaco', 'Consolas', monospace; font-size: 13px;"
          />
          <template #extra>
            <a-space style="margin-top: 12px;">
              <a-button type="primary" size="small" @click="copyKey">
                <template #icon>
                  <icon-copy />
                </template>
                复制 API Key
              </a-button>
              <a-button size="small" @click="$router.push('/api-keys')">
                返回列表
              </a-button>
            </a-space>
          </template>
        </a-form-item>
        <a-form-item v-if="!createdKey">
          <a-space>
            <a-button type="primary" :loading="loading" @click="handleSubmit">
              {{ isEdit ? '更新' : '生成 API Key' }}
            </a-button>
            <a-button @click="$router.back()">取消</a-button>
          </a-space>
        </a-form-item>
      </a-form>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useApiKeyStore } from '@/stores/apiKeys'
import { useOrganizationStore } from '@/stores/organizations'
import { Message } from '@arco-design/web-vue'
import { IconCopy } from '@arco-design/web-vue/es/icon'
import type { FormInstance } from '@arco-design/web-vue'

const route = useRoute()
const router = useRouter()
const apiKeyStore = useApiKeyStore()
const organizationStore = useOrganizationStore()

const formRef = ref<FormInstance>()
const loading = ref(false)
const createdKey = ref<{ key: string } | null>(null)

const isEdit = computed(() => route.name === 'ApiKeyEdit')
const apiKeyId = computed(() => route.params.id as string)
// 从路由查询参数获取organization_id（如果是从组织详情页面跳转过来的）
const organizationIdFromQuery = computed(() => route.query.organization_id as string | undefined)

const form = ref({
  organization_id: ''
})

const rules = {
  organization_id: [{ required: true, message: '请选择组织' }]
}

const handleSubmit = async () => {
  try {
    // 表单验证
    const errors = await formRef.value?.validate()
    if (errors) {
      Message.warning('请选择组织')
      return
    }

    loading.value = true
    
    const submitData = {
      organization_id: form.value.organization_id
    }

    if (isEdit.value) {
      await apiKeyStore.updateApiKey(apiKeyId.value, submitData)
      Message.success('更新成功')
      router.push('/api-keys')
    } else {
      const key = await apiKeyStore.createApiKey(submitData)
      console.log('[Form] Received API key from backend:', key)
      console.log('[Form] Key value:', key.key)
      console.log('[Form] Key type:', typeof key.key)
      console.log('[Form] Full key object:', JSON.stringify(key, null, 2))

      if (!key.key) {
        console.error('[Form] ERROR: key.key is empty or undefined!')
        Message.error('API Key 创建成功，但未返回 key 值，请刷新页面查看')
        return
      }

      createdKey.value = { key: key.key }
      console.log('[Form] createdKey.value:', createdKey.value)
      console.log('[Form] createdKey.value.key:', createdKey.value.key)
      Message.success('创建成功，请保存 API Key')
    }
  } catch (error: any) {
    console.error('Error in handleSubmit:', error)
    // 检查是否是组织已有API Key的错误
    if (error?.response?.data?.detail?.includes('already has an API Key')) {
      Message.error('该组织已经有API Key，每个组织只能有一个API Key')
    } else {
      const errorMsg = error?.response?.data?.detail || error?.message || '创建失败'
      Message.error(errorMsg)
    }
  } finally {
    loading.value = false
  }
}

const copyKey = () => {
  if (createdKey.value?.key) {
    navigator.clipboard.writeText(createdKey.value.key)
    Message.success('已复制到剪贴板')
  }
}

onMounted(async () => {
  // 如果是创建模式，加载组织列表
  if (!isEdit.value) {
    await organizationStore.fetchOrganizations({ page: 1, limit: 1000 })
    // 如果从查询参数中获取到organization_id，自动填充
    if (organizationIdFromQuery.value) {
      form.value.organization_id = organizationIdFromQuery.value
    }
  }
  
  // 编辑模式不再支持，因为一个组织只能有一个API Key
  if (isEdit.value) {
    Message.warning('不支持编辑API Key，请删除后重新创建')
    router.push('/api-keys')
  }
})
</script>

<style scoped>
.api-key-form {
  padding: 0;
}
</style>

