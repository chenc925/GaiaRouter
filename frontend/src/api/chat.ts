/**
 * 聊天测试API
 */

import request from '@/utils/request'

const apiBaseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

/**
 * 获取模型列表
 * @param apiKey - API Key（可选，用于测试）
 */
export function getModels(apiKey?: string) {
  const config: any = {}
  
  // 如果提供了 API Key，添加到请求头
  if (apiKey) {
    config.headers = {
      'Authorization': `Bearer ${apiKey}`
    }
  }
  
  return request.get('/v1/models', config)
}

/**
 * 发送聊天消息
 */
export interface ChatMessage {
  role: 'system' | 'user' | 'assistant'
  content: string | ContentPart[]
}

export interface ContentPart {
  type: 'text' | 'image_url'
  text?: string
  image_url?: {
    url: string
    detail?: string
  }
}

export interface ChatRequest {
  model: string
  messages: ChatMessage[]
  temperature?: number
  max_tokens?: number
  stream?: boolean
}

export interface ChatResponse {
  id: string
  object: string
  created: number
  model: string
  choices: {
    index: number
    message: {
      role: string
      content: string
    }
    finish_reason: string
  }[]
  usage?: {
    prompt_tokens: number
    completion_tokens: number
    total_tokens: number
  }
}

export async function sendChatMessage(data: ChatRequest, apiKey?: string) {
  const config: any = {}

  if (apiKey) {
    config.headers = {
      Authorization: `Bearer ${apiKey}`
    }
  }

  return request.post<ChatResponse>('/v1/chat/completions', data, config)
}

export async function sendChatMessageStream(
  data: ChatRequest,
  apiKey: string | undefined,
  onDelta: (text: string) => void
) {
  const url = `${apiBaseURL.replace(/\/$/, '')}/v1/chat/completions`

  const resp = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(apiKey ? { Authorization: `Bearer ${apiKey}` } : {})
    },
    body: JSON.stringify({ ...data, stream: true })
  })

  if (!resp.ok || !resp.body) {
    const text = await resp.text().catch(() => '')
    throw new Error(text || `请求失败，状态码 ${resp.status}`)
  }

  const reader = resp.body.getReader()
  const decoder = new TextDecoder('utf-8')
  let buffer = ''

  // 简单解析 SSE 数据流
  while (true) {
    const { value, done } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })

    const parts = buffer.split('\n\n')
    buffer = parts.pop() || ''

    for (const part of parts) {
      const line = part.trim()
      if (!line.startsWith('data:')) continue
      const dataStr = line.replace(/^data:\s*/, '')
      if (dataStr === '[DONE]') {
        return
      }
      try {
        const chunk = JSON.parse(dataStr)
        const delta = chunk.choices?.[0]?.delta?.content
        if (typeof delta === 'string' && delta) {
          onDelta(delta)
        }
      } catch {
        // 忽略单个块的解析错误
      }
    }
  }
}
