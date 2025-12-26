<template>
  <div class="chat-test">
    <a-page-header title="对话测试" subtitle="使用组织API Key进行AI模型对话测试" />

    <a-card class="config-card" title="配置" :bordered="false">
      <template #extra>
        <a-button type="text" size="small" @click="$router.push('/api-usage')">
          查看终端 API 使用说明
        </a-button>
      </template>
      <a-form :model="config" layout="vertical">
        <a-row :gutter="16">
          <a-col :span="8">
            <a-form-item label="API Key" required>
              <a-select
                v-model="config.apiKeyId"
                placeholder="选择API Key"
                :loading="apiKeysLoading"
                @change="handleApiKeyChange"
              >
                <a-option v-for="key in apiKeys" :key="key.id" :value="key.id">
                  {{ key.key || key.name }}
                </a-option>
              </a-select>
            </a-form-item>
          </a-col>

          <a-col :span="8">
            <a-form-item label="模型" required>
              <a-select
                v-model="config.model"
                placeholder="选择模型"
                :loading="modelsLoading"
                :disabled="!selectedApiKey"
                allow-search
              >
                <a-option v-for="model in models" :key="model.id" :value="model.id">
                  {{ model.id }}
                </a-option>
              </a-select>
            </a-form-item>
          </a-col>

          <a-col :span="4">
            <a-form-item label="Temperature">
              <a-input-number
                v-model="config.temperature"
                :min="0"
                :max="2"
                :step="0.1"
                style="width: 100%"
              />
            </a-form-item>
          </a-col>

          <a-col :span="4">
            <a-form-item label="Max Tokens">
              <a-input-number v-model="config.maxTokens" :min="1" :max="4096" style="width: 100%" />
            </a-form-item>
          </a-col>
        </a-row>

        <a-row :gutter="16">
          <a-col :span="4">
            <a-form-item label="流式输出">
              <a-switch v-model="config.stream" />
            </a-form-item>
          </a-col>
        </a-row>
      </a-form>
    </a-card>

    <a-card class="chat-card" :bordered="false">
      <div class="chat-container">
        <div ref="messagesContainer" class="messages-container">
          <div
            v-for="(message, index) in messages"
            :key="index"
            :class="['message-item', `message-${message.role}`]"
          >
            <div class="message-role">
              {{
                message.role === 'user' ? '用户' : message.role === 'assistant' ? '助手' : '系统'
              }}
            </div>
            <div class="message-content">
              <template v-if="typeof message.content === 'string'">
                {{ message.content }}
                <span
                  v-if="
                    isStreaming && message.role === 'assistant' && index === messages.length - 1
                  "
                  class="streaming-caret"
                />
              </template>
              <template v-else>
                <div v-for="(part, idx) in message.content" :key="idx" class="content-part">
                  <div v-if="part.type === 'text'">
                    {{ part.text }}
                  </div>
                  <img
                    v-else-if="part.type === 'image_url'"
                    :src="part.image_url?.url"
                    class="message-image"
                  />
                </div>
              </template>
            </div>
          </div>

          <div v-if="loading && !isStreaming" class="message-item message-assistant">
            <div class="message-role">助手</div>
            <div class="message-content"><a-spin size="small" /> 思考中...</div>
          </div>
        </div>

        <div class="input-container">
          <a-upload
            :file-list="imageFiles"
            list-type="picture-card"
            :auto-upload="false"
            accept="image/*"
            :limit="5"
            @change="handleUploadChange"
            @preview="handlePreview"
          >
            <template #upload-button>
              <div class="upload-btn">
                <icon-plus />
                <div style="margin-top: 8px">添加图片</div>
              </div>
            </template>
          </a-upload>

          <a-textarea
            v-model="userInput"
            placeholder="输入消息... (支持多模态输入，Ctrl+Enter发送)"
            :auto-size="{ minRows: 3, maxRows: 6 }"
            @keydown.enter="handleKeyDown"
          />

          <div class="input-actions">
            <a-button @click="handleClear"> 清空对话 </a-button>
            <a-button type="primary" :loading="loading" :disabled="!canSend" @click="handleSend">
              发送
            </a-button>
          </div>
        </div>
      </div>
    </a-card>

    <!-- 图片预览 -->
    <a-modal :visible="previewVisible" :footer="null" @cancel="previewVisible = false">
      <img :src="previewImage" style="width: 100%" />
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import { Message } from '@arco-design/web-vue'
import { IconPlus } from '@arco-design/web-vue/es/icon'
import { useApiKeyStore } from '@/stores/apiKeys'
import {
  getModels,
  sendChatMessage,
  sendChatMessageStream,
  type ChatMessage,
  type ContentPart
} from '@/api/chat'
import type { FileItem } from '@arco-design/web-vue'

const apiKeyStore = useApiKeyStore()

// 配置
const config = ref({
  apiKeyId: undefined as string | undefined,
  model: undefined as string | undefined,
  temperature: 0.7,
  maxTokens: 2000,
  stream: false
})

// API Keys
const apiKeys = ref<any[]>([])
const apiKeysLoading = ref(false)
const selectedApiKey = ref<any>(null)

// 模型列表
const models = ref<any[]>([])
const modelsLoading = ref(false)

// 对话消息
const messages = ref<ChatMessage[]>([])
const userInput = ref('')
const loading = ref(false)
const isStreaming = ref(false)
const messagesContainer = ref<HTMLElement>()

// 图片上传
const imageFiles = ref<FileItem[]>([])
const previewVisible = ref(false)
const previewImage = ref('')

// 是否可以发送
const canSend = computed(() => {
  return (
    !loading.value &&
    !isStreaming.value &&
    config.value.apiKeyId &&
    config.value.model &&
    (userInput.value.trim() || imageFiles.value.length > 0)
  )
})

// 加载API Keys
const loadApiKeys = async () => {
  apiKeysLoading.value = true
  try {
    await apiKeyStore.fetchApiKeys({ page: 1, limit: 100 })
    apiKeys.value = apiKeyStore.apiKeys
  } catch (error) {
    console.error('Failed to load API keys:', error)
    Message.error('加载API Key失败')
  } finally {
    apiKeysLoading.value = false
  }
}

// 加载模型列表
const loadModels = async () => {
  if (!selectedApiKey.value) return

  modelsLoading.value = true
  try {
    // 使用选中的 API Key
    const response = await getModels(selectedApiKey.value.key)
    models.value = response.data || []
  } catch (error) {
    console.error('Failed to load models:', error)
    Message.error('加载模型列表失败')
  } finally {
    modelsLoading.value = false
  }
}

// API Key变更
const handleApiKeyChange = (value: string) => {
  selectedApiKey.value = apiKeys.value.find(k => k.id === value)
  config.value.model = undefined
  models.value = []
  loadModels()
}

// 图片上传变化处理
const handleUploadChange = (fileList: FileItem[], currentFile: FileItem) => {
  // 验证文件类型
  if (currentFile.file && !currentFile.file.type.startsWith('image/')) {
    Message.error('只能上传图片文件！')
    return
  }

  // 验证文件大小
  if (currentFile.file && currentFile.file.size / 1024 / 1024 > 5) {
    Message.error('图片大小不能超过5MB！')
    return
  }

  // 转换为base64
  if (currentFile.file && currentFile.status === 'init') {
    const reader = new FileReader()
    reader.readAsDataURL(currentFile.file)
    reader.onload = () => {
      currentFile.url = reader.result as string
      imageFiles.value = fileList
    }
  } else {
    imageFiles.value = fileList
  }
}

// 预览图片
const handlePreview = (file: FileItem) => {
  previewImage.value = file.url || ''
  previewVisible.value = true
}

// 键盘事件处理
const handleKeyDown = (e: KeyboardEvent) => {
  if (e.ctrlKey && e.key === 'Enter') {
    e.preventDefault()
    handleSend()
  }
}

// 发送消息
const handleSend = async () => {
  if (!canSend.value) return

  loading.value = true
  isStreaming.value = !!config.value.stream

  try {
    // 构建消息内容
    let content: string | ContentPart[]

    if (imageFiles.value.length > 0) {
      // 多模态消息
      content = []

      // 添加文本
      if (userInput.value.trim()) {
        content.push({
          type: 'text',
          text: userInput.value.trim()
        })
      }

      // 添加图片
      for (const file of imageFiles.value) {
        content.push({
          type: 'image_url',
          image_url: {
            url: file.url
          }
        })
      }
    } else {
      // 纯文本消息
      content = userInput.value.trim()
    }

    // 添加用户消息
    const userMessage: ChatMessage = {
      role: 'user',
      content
    }
    messages.value.push(userMessage)

    // 清空输入
    userInput.value = ''
    imageFiles.value = []

    // 滚动到底部
    await nextTick()
    scrollToBottom()

    if (config.value.stream) {
      // 流式模式：先插入一个空的助手消息占位
      const assistantMessage: ChatMessage = {
        role: 'assistant',
        content: ''
      }
      messages.value.push(assistantMessage)
      await nextTick()
      scrollToBottom()

      await sendChatMessageStream(
        {
          model: config.value.model!,
          messages: messages.value.slice(0, messages.value.length - 1),
          temperature: config.value.temperature,
          max_tokens: config.value.maxTokens
        },
        selectedApiKey.value.key,
        delta => {
          if (typeof assistantMessage.content === 'string') {
            assistantMessage.content += delta
            messages.value[messages.value.length - 1] = { ...assistantMessage }
            nextTick().then(() => {
              scrollToBottom()
            })
          }
        }
      )

      await nextTick()
      scrollToBottom()
    } else {
      // 非流式：一次性返回完整回复
      const response = await sendChatMessage(
        {
          model: config.value.model!,
          messages: messages.value,
          temperature: config.value.temperature,
          max_tokens: config.value.maxTokens
        },
        selectedApiKey.value.key
      )

      // 添加助手回复
      if (response.choices && response.choices.length > 0) {
        const assistantMessage: ChatMessage = {
          role: 'assistant',
          content: response.choices[0].message.content
        }
        messages.value.push(assistantMessage)

        // 滚动到底部
        await nextTick()
        scrollToBottom()
      }
    }
  } catch (error: any) {
    console.error('Failed to send message:', error)
    Message.error(error?.response?.data?.error?.message || error?.message || '发送消息失败')
    // 移除最后一条用户消息
    messages.value.pop()
  } finally {
    loading.value = false
    isStreaming.value = false
  }
}

// 清空对话
const handleClear = () => {
  messages.value = []
  userInput.value = ''
  imageFiles.value = []
}

// 滚动到底部
const scrollToBottom = () => {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

// 初始化
onMounted(() => {
  loadApiKeys()
})
</script>

<style scoped>
.chat-test {
  padding: 0;
}

.config-card {
  margin-bottom: 16px;
}

.chat-card {
  margin-top: 16px;
}

.chat-container {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 400px);
  min-height: 500px;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  background: #f5f5f5;
  border-radius: 4px;
  margin-bottom: 16px;
}

.message-item {
  margin-bottom: 16px;
  display: flex;
  flex-direction: column;
}

.message-role {
  font-size: 12px;
  color: #999;
  margin-bottom: 4px;
}

.message-content {
  padding: 12px;
  border-radius: 8px;
  max-width: 70%;
  word-wrap: break-word;
  white-space: pre-wrap;
}

.message-user .message-content {
  background: #1890ff;
  color: white;
  align-self: flex-end;
  margin-left: auto;
}

.message-assistant .message-content {
  background: white;
  color: #333;
  align-self: flex-start;
}

.message-system .message-content {
  background: #f0f0f0;
  color: #666;
  align-self: center;
}

.content-part {
  margin-bottom: 8px;
}

.content-part:last-child {
  margin-bottom: 0;
}

.message-image {
  max-width: 300px;
  max-height: 300px;
  border-radius: 4px;
  margin-top: 8px;
}

.input-container {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.input-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.streaming-caret {
  display: inline-block;
  width: 6px;
  height: 1em;
  margin-left: 2px;
  background: rgba(0, 0, 0, 0.4);
  animation: blink 1s step-end infinite;
}

@keyframes blink {
  50% {
    opacity: 0;
  }
}
</style>
