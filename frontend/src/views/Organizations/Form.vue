<template>
  <div class="organization-form">
    <a-page-header :title="isEdit ? '编辑组织' : '创建组织'" @back="$router.back()" />

    <a-card>
      <a-form ref="formRef" :model="form" :rules="rules" layout="vertical" @submit="handleSubmit">
        <a-form-item field="name" label="组织名称">
          <a-input v-model="form.name" placeholder="请输入组织名称" />
        </a-form-item>
        <a-form-item field="description" label="描述">
          <a-textarea
            v-model="form.description"
            placeholder="请输入组织描述"
            :auto-size="{ minRows: 3, maxRows: 5 }"
          />
        </a-form-item>
        <a-form-item field="monthly_requests_limit" label="月度请求次数限制">
          <a-input-number
            v-model="form.monthly_requests_limit"
            placeholder="请输入月度请求次数限制"
            :min="0"
            style="width: 100%"
          />
        </a-form-item>
        <a-form-item field="monthly_tokens_limit" label="月度Token限制">
          <a-input-number
            v-model="form.monthly_tokens_limit"
            placeholder="请输入月度Token限制"
            :min="0"
            style="width: 100%"
          />
        </a-form-item>
        <a-form-item field="monthly_cost_limit" label="月度费用限制">
          <a-input-number
            v-model="form.monthly_cost_limit"
            placeholder="请输入月度费用限制"
            :min="0"
            :precision="2"
            style="width: 100%"
          />
        </a-form-item>
        <a-form-item>
          <a-space>
            <a-button type="primary" html-type="submit" :loading="loading">
              {{ isEdit ? '更新' : '创建' }}
            </a-button>
            <a-button @click="$router.back()"> 取消 </a-button>
          </a-space>
        </a-form-item>
      </a-form>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useOrganizationStore } from '@/stores/organizations'
import { Message } from '@arco-design/web-vue'
import type { FormInstance } from '@arco-design/web-vue'

const route = useRoute()
const router = useRouter()
const organizationStore = useOrganizationStore()

const formRef = ref<FormInstance>()
const loading = ref(false)

const isEdit = computed(() => route.name === 'OrganizationEdit')
const organizationId = computed(() => route.params.id as string)

const form = ref({
  name: '',
  description: '',
  monthly_requests_limit: undefined as number | undefined,
  monthly_tokens_limit: undefined as number | undefined,
  monthly_cost_limit: undefined as number | undefined
})

const rules = {
  name: [{ required: true, message: '请输入组织名称' }]
}

const handleSubmit = async () => {
  // 验证表单
  try {
    await formRef.value?.validate()
  } catch (error) {
    // 验证失败，不继续执行
    console.log('Form validation failed:', error)
    return
  }

  loading.value = true
  try {
    console.log('Submitting form:', form.value)
    if (isEdit.value) {
      await organizationStore.updateOrganization(organizationId.value, form.value)
      Message.success('更新成功')
    } else {
      await organizationStore.createOrganization(form.value)
      Message.success('创建成功')
    }
    router.push('/organizations')
  } catch (error: any) {
    // 错误已经在响应拦截器中处理，这里只记录日志
    console.error('Organization operation failed:', error)
    // 如果响应拦截器没有处理（比如网络错误），则显示错误
    if (!error?.response) {
      Message.error(isEdit.value ? '更新失败，请检查网络连接' : '创建失败，请检查网络连接')
    }
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  if (isEdit.value && organizationId.value) {
    await organizationStore.fetchOrganization(organizationId.value)
    if (organizationStore.currentOrganization) {
      const org = organizationStore.currentOrganization
      form.value = {
        name: org.name,
        description: org.description || '',
        monthly_requests_limit: org.monthly_requests_limit || undefined,
        monthly_tokens_limit: org.monthly_tokens_limit || undefined,
        monthly_cost_limit: org.monthly_cost_limit ? Number(org.monthly_cost_limit) : undefined
      }
    }
  }
})
</script>

<style scoped>
.organization-form {
  padding: 0;
}
</style>
