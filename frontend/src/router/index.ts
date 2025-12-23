import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'Login',
      component: () => import('@/views/Login.vue'),
      meta: { requiresAuth: false }
    },
    {
      path: '/',
      component: () => import('@/components/Layout/MainLayout.vue'),
      meta: { requiresAuth: true },
      redirect: '/dashboard',
      children: [
        {
          path: 'dashboard',
          name: 'Dashboard',
          component: () => import('@/views/Dashboard/index.vue')
        },
        {
          path: 'organizations',
          name: 'Organizations',
          component: () => import('@/views/Organizations/List.vue')
        },
        {
          path: 'organizations/create',
          name: 'OrganizationCreate',
          component: () => import('@/views/Organizations/Form.vue')
        },
        {
          path: 'organizations/:id',
          name: 'OrganizationDetail',
          component: () => import('@/views/Organizations/Detail.vue')
        },
        {
          path: 'organizations/:id/edit',
          name: 'OrganizationEdit',
          component: () => import('@/views/Organizations/Form.vue')
        },
        {
          path: 'api-keys',
          name: 'ApiKeys',
          component: () => import('@/views/ApiKeys/List.vue')
        },
        {
          path: 'api-keys/create',
          name: 'ApiKeyCreate',
          component: () => import('@/views/ApiKeys/Form.vue')
        },
        {
          path: 'api-keys/:id',
          name: 'ApiKeyDetail',
          component: () => import('@/views/ApiKeys/Detail.vue')
        },
        {
          path: 'api-keys/:id/edit',
          name: 'ApiKeyEdit',
          component: () => import('@/views/ApiKeys/Form.vue')
        },
        {
          path: 'stats',
          name: 'Stats',
          component: () => import('@/views/Stats/Dashboard.vue')
        },
        {
          path: 'stats/organizations/:id',
          name: 'OrganizationStats',
          component: () => import('@/views/Stats/OrganizationStats.vue')
        },
        {
          path: 'stats/api-keys/:id',
          name: 'ApiKeyStats',
          component: () => import('@/views/Stats/ApiKeyStats.vue')
        },
        {
          path: 'chat/test',
          name: 'ChatTest',
          component: () => import('@/views/Chat/Test.vue')
        },
        {
          path: 'models',
          name: 'Models',
          component: () => import('@/views/Models/index.vue')
        },
        {
          path: 'api-usage',
          name: 'ApiUsage',
          component: () => import('@/views/Docs/ApiUsage.vue')
        }
      ]
    }
  ]
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  authStore.checkAuth()

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login')
  } else if (to.path === '/login' && authStore.isAuthenticated) {
    next('/dashboard')
  } else {
    next()
  }
})

export default router

