<template>
  <a-layout class="layout">
    <a-layout-header class="header">
      <div class="logo">
        <div class="logo-mark">G</div>
        <div class="logo-text">GaiaRouter</div>
      </div>
      <a-menu
        mode="horizontal"
        :selected-keys="selectedKeys"
        class="header-menu"
      >
        <a-menu-item key="dashboard" @click="$router.push('/dashboard')">
          仪表盘
        </a-menu-item>
      </a-menu>
      <div class="user-info">
        <a-button type="text" @click="handleLogout">退出</a-button>
      </div>
    </a-layout-header>
    <a-layout>
      <a-layout-sider class="sider" :width="200" collapsible breakpoint="lg">
        <a-menu
          mode="vertical"
          :selected-keys="selectedKeys"
          @menu-item-click="handleMenuClick"
        >
          <a-menu-item key="dashboard">
            <template #icon><IconDashboard /></template>
            仪表盘
          </a-menu-item>
          <a-menu-item key="organizations">
            <template #icon><IconUserGroup /></template>
            组织管理
          </a-menu-item>
          <a-menu-item key="api-keys">
            <template #icon><IconSettings /></template>
            API Key 管理
          </a-menu-item>
          <a-menu-item key="models">
            <template #icon><IconSettings /></template>
            模型管理
          </a-menu-item>
          <a-menu-item key="stats">
            <template #icon><IconBarChart /></template>
            数据统计
          </a-menu-item>
          <a-menu-item key="chat">
            <template #icon><IconDashboard /></template>
            对话测试
          </a-menu-item>
        </a-menu>
      </a-layout-sider>
      <a-layout-content class="content">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </a-layout-content>
    </a-layout>
  </a-layout>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import {
  IconDashboard,
  IconUserGroup,
  IconSettings,
  IconBarChart
} from '@arco-design/web-vue/es/icon'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const selectedKeys = computed(() => {
  const path = route.path
  if (path.startsWith('/organizations')) return ['organizations']
  if (path.startsWith('/api-keys')) return ['api-keys']
  if (path.startsWith('/models')) return ['models']
  if (path.startsWith('/stats')) return ['stats']
  if (path.startsWith('/chat')) return ['chat']
  if (path.startsWith('/dashboard')) return ['dashboard']
  return []
})

const handleMenuClick = (key: string) => {
  if (key === 'chat') {
    router.push('/chat/test')
  } else {
    router.push(`/${key}`)
  }
}

const handleLogout = () => {
  authStore.logout()
}
</script>

<style scoped>
.layout {
  height: 100vh;
  background: var(--color-bg-1);
}

.header {
  display: flex;
  align-items: center;
  padding: 0 24px;
  background: var(--color-bg-2);
  border-bottom: 1px solid var(--color-border);
}

.logo {
  display: flex;
  align-items: center;
  margin-right: 24px;
}

.logo-mark {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: linear-gradient(135deg, var(--color-primary-5), var(--color-primary-6));
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ffffff;
  font-weight: 600;
  font-size: 18px;
  margin-right: 8px;
}

.logo-text {
  font-size: 20px;
  font-weight: 600;
}

.header-menu {
  flex: 1;
}

.user-info {
  margin-left: auto;
}

.sider {
  background: var(--color-bg-1);
  border-right: 1px solid var(--color-border);
}

.sider :deep(.arco-menu-item) {
  border-radius: 4px;
}

.sider :deep(.arco-menu-item.arco-menu-selected) {
  background-color: var(--color-fill-2);
  font-weight: 500;
}

.sider :deep(.arco-menu-item:hover) {
  background-color: var(--color-fill-2);
}

.header-menu :deep(.arco-menu-item.arco-menu-selected) {
  font-weight: 500;
}

.content {
  padding: 24px;
  background: var(--color-bg-1);
  overflow-y: auto;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

@media (max-width: 768px) {
  .header {
    padding: 0 16px;
  }

  .header-menu {
    display: none;
  }

  .content {
    padding: 16px;
  }
}
</style>

