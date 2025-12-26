<template>
  <div class="api-usage">
    <a-page-header
      title="终端 API 使用说明"
      subtitle="面向终端应用的 Chat 与模型调用示例"
    />

    <a-card
      class="section-card"
      title="1. 基本信息"
      :bordered="false"
    >
      <a-typography>
        <a-typography-paragraph>
          <strong>Base URL：</strong>
          <code>{{ baseUrl }}</code>
        </a-typography-paragraph>
        <a-typography-paragraph>
          <strong>认证方式：</strong> 在请求头中携带 API Key：
        </a-typography-paragraph>
        <a-typography-paragraph>
          <pre><code>Authorization: Bearer &lt;YOUR_API_KEY&gt;</code></pre>
        </a-typography-paragraph>
      </a-typography>
    </a-card>

    <a-card
      class="section-card"
      title="2. 获取可用模型列表 (GET /v1/models)"
      :bordered="false"
    >
      <a-typography>
        <a-typography-paragraph>
          终端应用在发起聊天前，应先调用 <code>/v1/models</code> 获取可用模型列表，只能调用已启用的模型。
        </a-typography-paragraph>
        <a-typography-title :heading="5">
          请求示例（curl）
        </a-typography-title>
        <a-typography-paragraph>
          <pre><code>curl -X GET {{ baseUrl }}/models \
  -H "Authorization: Bearer &lt;YOUR_API_KEY&gt;"</code></pre>
        </a-typography-paragraph>
        <a-typography-title :heading="5">
          响应示例
        </a-typography-title>
        <a-typography-paragraph>
          <pre><code>{
  "data": [
    {
      "id": "openai/gpt-4",
      "object": "model",
      "created": 1677610602,
      "owned_by": "openai",
      "provider": "openai"
    }
  ]
}</code></pre>
        </a-typography-paragraph>
      </a-typography>
    </a-card>

    <a-card
      class="section-card"
      title="3. 发起聊天补全 (POST /v1/chat/completions)"
      :bordered="false"
    >
      <a-typography>
        <a-typography-paragraph>
          Chat 接口兼容 OpenAI 风格，支持普通模式与流式模式。
        </a-typography-paragraph>
        <a-typography-title :heading="5">
          请求示例（普通模式）
        </a-typography-title>
        <a-typography-paragraph>
          <pre><code>curl -X POST {{ baseUrl }}/chat/completions \
  -H "Authorization: Bearer &lt;YOUR_API_KEY&gt;" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "openai/gpt-4",
    "messages": [
      {"role": "user", "content": "Hello!"}
    ],
    "temperature": 0.7,
    "max_tokens": 1000
  }'</code></pre>
        </a-typography-paragraph>
        <a-typography-title :heading="5">
          请求示例（流式模式）
        </a-typography-title>
        <a-typography-paragraph>
          <pre><code>curl -N -X POST {{ baseUrl }}/chat/completions \
  -H "Authorization: Bearer &lt;YOUR_API_KEY&gt;" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "openai/gpt-4",
    "messages": [
      {"role": "user", "content": "Hello!"}
    ],
    "stream": true
  }'</code></pre>
        </a-typography-paragraph>
        <a-typography-title :heading="5">
          关键参数说明
        </a-typography-title>
        <a-typography-paragraph>
          <ul>
            <li><strong>model</strong>：模型标识符，例如 <code>openai/gpt-4</code> 或 <code>openrouter/xxx</code>。</li>
            <li><strong>messages</strong>：对话消息数组，角色支持 <code>system</code> / <code>user</code> / <code>assistant</code>。</li>
            <li><strong>temperature</strong>：采样温度，范围 0-2。</li>
            <li><strong>max_tokens</strong>：本次回复最大片段的 token 数。</li>
            <li><strong>stream</strong>：是否开启流式输出，终端可按行解析 <code>data:</code> 前缀。</li>
          </ul>
        </a-typography-paragraph>
      </a-typography>
    </a-card>

    <a-card
      class="section-card"
      title="4. 集成建议"
      :bordered="false"
    >
      <a-typography>
        <a-typography-paragraph>
          - 首次集成建议先在「对话测试」页面验证 API Key 与模型是否可用，再接入终端应用；
          - 推荐为不同环境（测试 / 生产）创建独立 API Key，便于统计与隔离；
          - 对于长对话或高并发场景，优先使用流式输出以降低延迟体验。
        </a-typography-paragraph>
      </a-typography>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const baseUrl = computed(() => {
  const apiBase = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
  return `${apiBase.replace(/\/$/, '')}/v1`
})
</script>

<style scoped>
.api-usage {
  padding: 0;
}

.section-card {
  margin-top: 16px;
}

pre {
  margin: 8px 0;
  padding: 8px 12px;
  background: var(--color-fill-1);
  border-radius: 6px;
  font-size: 12px;
  overflow: auto;
}

code {
  font-family: SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
}
</style>
