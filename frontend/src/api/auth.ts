import apiClient from '@/utils/request'

export interface LoginRequest {
  username: string
  password: string
}

export interface LoginResponse {
  token: string
  user_id: string
  username: string
  role: string
}

export const authApi = {
  login: (data: LoginRequest) => {
    return apiClient.post<LoginResponse>('/v1/admin/login', data)
  }
}

