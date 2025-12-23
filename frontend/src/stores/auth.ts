import { defineStore } from 'pinia'
import { ref } from 'vue'
import router from '@/router'
import { authApi } from '@/api/auth'

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem('token'))
  const user = ref<{ id: string; username: string; role: string } | null>(
    localStorage.getItem('user') ? JSON.parse(localStorage.getItem('user')!) : null
  )
  const isAuthenticated = ref(!!token.value)

  const login = async (username: string, password: string) => {
    const response = await authApi.login({ username, password })
    token.value = response.token
    user.value = {
      id: response.user_id,
      username: response.username,
      role: response.role
    }
    localStorage.setItem('token', response.token)
    localStorage.setItem('user', JSON.stringify(user.value))
    isAuthenticated.value = true
  }

  const logout = () => {
    token.value = null
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    isAuthenticated.value = false
    router.push('/login')
  }

  const checkAuth = () => {
    const storedToken = localStorage.getItem('token')
    const storedUser = localStorage.getItem('user')
    if (storedToken && storedUser) {
      token.value = storedToken
      user.value = JSON.parse(storedUser)
      isAuthenticated.value = true
    } else {
      isAuthenticated.value = false
    }
  }

  return {
    token,
    user,
    isAuthenticated,
    login,
    logout,
    checkAuth
  }
})

