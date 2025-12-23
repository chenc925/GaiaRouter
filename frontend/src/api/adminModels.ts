/**
 * 模型管理 API
 */

import request from '@/utils/request'

export interface Model {
  id: string
  name: string
  description?: string
  provider?: string
  context_length?: number
  max_completion_tokens?: number
  pricing_prompt?: number
  pricing_completion?: number
  supports_vision: boolean
  supports_function_calling: boolean
  supports_streaming: boolean
  is_enabled: boolean
  is_free: boolean
  synced_at?: string
}

export interface ModelListParams {
  page?: number
  limit?: number
  enabled_only?: boolean
  provider?: string
  is_free?: boolean
}

/**
 * 同步 OpenRouter 模型
 */
export function syncModels() {
  return request.post('/v1/admin/models/sync')
}

/**
 * 获取模型列表
 */
export function getAdminModels(params: ModelListParams) {
  return request.get('/v1/admin/models', { params })
}

/**
 * 启用模型
 */
export function enableModel(modelId: string) {
  return request.patch(`/v1/admin/models/${encodeURIComponent(modelId)}/enable`)
}

/**
 * 禁用模型
 */
export function disableModel(modelId: string) {
  return request.patch(`/v1/admin/models/${encodeURIComponent(modelId)}/disable`)
}

/**
 * 批量更新模型状态
 */
export function batchUpdateModels(model_ids: string[], is_enabled: boolean) {
  return request.post('/v1/admin/models/batch-update', {
    model_ids,
    is_enabled
  })
}
