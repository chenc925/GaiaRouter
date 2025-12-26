import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios'
import { Message } from '@arco-design/web-vue'
import router from '@/router'

const apiBaseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

class ApiClient {
  private axiosInstance: AxiosInstance

  constructor() {
    this.axiosInstance = axios.create({
      baseURL: apiBaseURL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json'
      }
    })

    // 请求拦截器
    this.axiosInstance.interceptors.request.use(
      config => {
        // 如果请求头中没有 Authorization，则添加用户 token
        // 这样可以让测试页面传入的 API Key 不被覆盖
        if (!config.headers.Authorization) {
          const token = localStorage.getItem('token')
          if (token) {
            config.headers.Authorization = `Bearer ${token}`
          }
        }
        return config
      },
      error => {
        return Promise.reject(error)
      }
    )

    // 响应拦截器
    this.axiosInstance.interceptors.response.use(
      (response: AxiosResponse) => {
        return response.data
      },
      error => {
        // 统一错误处理
        if (error.response) {
          const { status, data } = error.response

          if (status === 401) {
            // 如果是 API Key 认证失败，不要跳转登录页
            // 只有用户 token 认证失败才跳转
            const isApiKeyAuth = error.config?.headers?.Authorization?.startsWith('Bearer sk-or-')

            if (!isApiKeyAuth) {
              // 未授权，清除token并跳转到登录页
              localStorage.removeItem('token')
              router.push('/login')
              Message.error('登录已过期，请重新登录')
            } else {
              // API Key 认证失败
              Message.error(data?.error?.message || 'API Key 无效或已过期')
            }
          } else if (status === 403) {
            Message.error('权限不足')
          } else if (status === 404) {
            Message.error('资源不存在')
          } else if (status >= 500) {
            Message.error('服务器错误，请稍后重试')
          } else {
            // 尝试多种错误消息格式
            const errorMessage = data?.error?.message || data?.detail || data?.message || '请求失败'
            Message.error(errorMessage)
          }
        } else {
          Message.error('网络错误，请检查网络连接')
        }

        return Promise.reject(error)
      }
    )
  }

  get<T = any>(url: string, config?: AxiosRequestConfig): Promise<T> {
    return this.axiosInstance.get(url, config)
  }

  post<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    return this.axiosInstance.post(url, data, config)
  }

  put<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    return this.axiosInstance.put(url, data, config)
  }

  patch<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    return this.axiosInstance.patch(url, data, config)
  }

  delete<T = any>(url: string, config?: AxiosRequestConfig): Promise<T> {
    return this.axiosInstance.delete(url, config)
  }
}

export default new ApiClient()
