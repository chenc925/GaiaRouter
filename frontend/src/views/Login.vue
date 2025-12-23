<template>
  <div class="login-page">
    <div class="login-container">
      <div class="login-left">
        <div class="brand">
          <div class="logo-mark">G</div>
          <div class="brand-text">
            <div class="brand-title">GaiaRouter 管理后台</div>
            <div class="brand-subtitle">统一管理 API Key、组织与模型路由</div>
          </div>
        </div>
        <div class="brand-desc">
          <p>· 多提供商模型统一接入</p>
          <p>· 精细化限额与统计看板</p>
          <p>· 安全可控的密钥管理</p>
        </div>
      </div>
      <div class="login-right">
        <a-card class="login-card" :bordered="false">
          <div class="login-card-header">
            <div class="login-card-title">欢迎登录</div>
            <div class="login-card-subtitle">使用管理员账号访问 GaiaRouter 控制台</div>
          </div>
          <a-form
            :model="form"
            layout="vertical"
            @submit="handleSubmit"
          >
            <a-form-item
              field="username"
              label="用户名"
              :rules="[{ required: true, message: '请输入用户名' }]"
            >
              <a-input
                v-model="form.username"
                placeholder="请输入用户名"
                :disabled="loading"
              />
            </a-form-item>
            <a-form-item
              field="password"
              label="密码"
              :rules="[{ required: true, message: '请输入密码' }]"
            >
              <a-input-password
                v-model="form.password"
                placeholder="请输入密码"
                :disabled="loading"
              />
            </a-form-item>
            <a-form-item>
              <a-button
                type="primary"
                html-type="submit"
                long
                :loading="loading"
              >
                登录
              </a-button>
            </a-form-item>
          </a-form>
        </a-card>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { Message } from '@arco-design/web-vue'

const router = useRouter()
const authStore = useAuthStore()

const form = ref({
  username: '',
  password: ''
})

const loading = ref(false)

const handleSubmit = async () => {
  if (!form.value.username || !form.value.password) {
    Message.error('请输入用户名和密码')
    return
  }

  loading.value = true
  try {
    await authStore.login(form.value.username, form.value.password)
    Message.success('登录成功')
    router.push('/dashboard')
  } catch (error: any) {
    const errorMessage = error?.response?.data?.error?.message || error?.message || '登录失败，请检查用户名和密码'
    Message.error(errorMessage)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: radial-gradient(circle at top left, var(--color-primary-4) 0, var(--color-primary-8) 55%, #0b1020 100%);
}

.login-container {
  width: 960px;
  max-width: 100%;
  padding: 24px;
  display: flex;
  gap: 32px;
}

.login-left {
  flex: 1.1;
  color: #ffffff;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.brand {
  display: flex;
  align-items: center;
  margin-bottom: 24px;
}

.logo-mark {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  background: linear-gradient(135deg, var(--color-primary-5), var(--color-primary-6));
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ffffff;
  font-weight: 600;
  font-size: 22px;
  margin-right: 12px;
}

.brand-title {
  font-size: 24px;
  font-weight: 600;
}

.brand-subtitle {
  margin-top: 4px;
  font-size: 13px;
  opacity: 0.9;
}

.brand-desc p {
  margin: 0 0 4px;
  font-size: 13px;
  opacity: 0.9;
}

.login-right {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.login-card {
  width: 360px;
  max-width: 100%;
  box-shadow: 0 18px 45px rgba(15, 23, 42, 0.35);
  border-radius: 16px;
}

.login-card-header {
  margin-bottom: 24px;
}

.login-card-title {
  font-size: 20px;
  font-weight: 600;
}

.login-card-subtitle {
  margin-top: 4px;
  font-size: 13px;
  color: var(--color-text-2);
}

:deep(.arco-form-item-label-col) {
  font-size: 13px;
}

@media (max-width: 768px) {
  .login-container {
    padding: 16px;
    flex-direction: column;
    align-items: stretch;
  }

  .login-left {
    align-items: flex-start;
  }

  .login-card {
    width: 100%;
  }
}
</style>

