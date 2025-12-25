# GaiaRouter 用户手册

## 简介

GaiaRouter 是一个 AI 模型路由服务，提供统一的 API 接口，允许您通过单一端点访问多个 AI 模型（如 OpenAI、Anthropic、Google 等）。本手册将指导您如何安装、配置和使用 GaiaRouter。

## 目录

1. [快速开始](#快速开始)
2. [安装部署](#安装部署)
3. [配置说明](#配置说明)
4. [API 使用](#api使用)
5. [常见问题](#常见问题)

## 快速开始

### 前提条件

- Python 3.9+ 或 Node.js 18+
- 各模型提供商的 API Key（OpenAI、Anthropic、Google 等）

### 快速启动

1. **克隆项目**

```bash
git clone <repository-url>
cd openrouter
```

2. **安装依赖**

```bash
# Python
pip install -r requirements.txt

# Node.js
npm install
```

3. **配置 API Key**

```bash
export OPENAI_API_KEY=your-openai-key
export ANTHROPIC_API_KEY=your-anthropic-key
export GOOGLE_API_KEY=your-google-key
```

4. **启动服务**

```bash
# Python
python main.py

# Node.js
npm start
```

服务将在 `http://localhost:8000` 启动。

## 安装部署

### Docker 部署

1. **构建镜像**

```bash
docker build -t gaiarouter .
```

2. **运行容器**

```bash
docker run -d \
  -p 8000:8000 \
  -e OPENAI_API_KEY=your-key \
  -e ANTHROPIC_API_KEY=your-key \
  -e GOOGLE_API_KEY=your-key \
  gaiarouter
```

### 直接部署

1. **安装依赖**

```bash
pip install -r requirements.txt
```

2. **配置环境变量**

```bash
export OPENAI_API_KEY=your-key
export ANTHROPIC_API_KEY=your-key
export GOOGLE_API_KEY=your-key
```

3. **启动服务**

```bash
python main.py
```

### 使用 systemd（Linux）

创建服务文件 `/etc/systemd/system/gaiarouter.service`：

```ini
[Unit]
Description=GaiaRouter Service
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/gaiarouter
Environment="OPENAI_API_KEY=your-key"
Environment="ANTHROPIC_API_KEY=your-key"
Environment="GOOGLE_API_KEY=your-key"
ExecStart=/usr/bin/python3 main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
sudo systemctl enable gaiarouter
sudo systemctl start gaiarouter
```

## 配置说明

### 环境变量配置

| 变量名              | 说明               | 必需                   |
| ------------------- | ------------------ | ---------------------- |
| `OPENAI_API_KEY`    | OpenAI API Key     | 是（如使用 OpenAI）    |
| `ANTHROPIC_API_KEY` | Anthropic API Key  | 是（如使用 Anthropic） |
| `GOOGLE_API_KEY`    | Google API Key     | 是（如使用 Google）    |
| `PORT`              | 服务端口           | 否（默认 8000）        |
| `LOG_LEVEL`         | 日志级别           | 否（默认 INFO）        |
| `REQUEST_TIMEOUT`   | 请求超时时间（秒） | 否（默认 60）          |

### 配置文件

创建 `config.yaml`：

```yaml
models:
  - id: openai/gpt-4
    provider: openai
    api_key: ${OPENAI_API_KEY}
  - id: openai/gpt-3.5-turbo
    provider: openai
    api_key: ${OPENAI_API_KEY}
  - id: anthropic/claude-3-opus
    provider: anthropic
    api_key: ${ANTHROPIC_API_KEY}
  - id: google/gemini-pro
    provider: google
    api_key: ${GOOGLE_API_KEY}

server:
  port: 8000
  host: 0.0.0.0

logging:
  level: INFO
  file: logs/gaiarouter.log
```

## API 使用

### 基础 URL

```
http://localhost:8000/v1
```

### 认证

目前 GaiaRouter 不需要认证，但建议在生产环境中添加 API Key 认证。

### 聊天完成接口

**端点**：`POST /v1/chat/completions`

**请求示例**：

```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "openai/gpt-4",
    "messages": [
      {
        "role": "user",
        "content": "Hello, world!"
      }
    ],
    "temperature": 0.7,
    "max_tokens": 1000
  }'
```

**Python 示例**：

```python
import requests

url = "http://localhost:8000/v1/chat/completions"
headers = {"Content-Type": "application/json"}
data = {
    "model": "openai/gpt-4",
    "messages": [
        {"role": "user", "content": "Hello, world!"}
    ],
    "temperature": 0.7,
    "max_tokens": 1000
}

response = requests.post(url, json=data, headers=headers)
print(response.json())
```

**Node.js 示例**：

```javascript
const axios = require("axios");

const response = await axios.post("http://localhost:8000/v1/chat/completions", {
  model: "openai/gpt-4",
  messages: [{ role: "user", content: "Hello, world!" }],
  temperature: 0.7,
  max_tokens: 1000,
});

console.log(response.data);
```

**响应示例**：

```json
{
  "id": "chatcmpl-123",
  "object": "chat.completion",
  "created": 1677652288,
  "model": "openai/gpt-4",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Hello! How can I help you?"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 20,
    "total_tokens": 30
  }
}
```

### 模型列表接口

**端点**：`GET /v1/models`

**请求示例**：

```bash
curl http://localhost:8000/v1/models
```

**响应示例**：

```json
{
  "data": [
    {
      "id": "openai/gpt-4",
      "object": "model",
      "created": 1677610602,
      "owned_by": "openai",
      "provider": "openai"
    },
    {
      "id": "anthropic/claude-3-opus",
      "object": "model",
      "created": 1677610602,
      "owned_by": "anthropic",
      "provider": "anthropic"
    }
  ]
}
```

### 支持的模型

- **OpenAI**: `openai/gpt-4`, `openai/gpt-3.5-turbo`
- **Anthropic**: `anthropic/claude-3-opus`, `anthropic/claude-3-sonnet`
- **Google**: `google/gemini-pro`

### 请求参数

| 参数                | 类型   | 必需 | 说明                                        |
| ------------------- | ------ | ---- | ------------------------------------------- |
| `model`             | string | 是   | 模型标识符，格式：`{provider}/{model-name}` |
| `messages`          | array  | 是   | 消息数组                                    |
| `temperature`       | number | 否   | 温度参数（0-2），默认 0.7                   |
| `max_tokens`        | number | 否   | 最大 token 数                               |
| `top_p`             | number | 否   | Top-p 采样参数                              |
| `frequency_penalty` | number | 否   | 频率惩罚                                    |
| `presence_penalty`  | number | 否   | 存在惩罚                                    |

### 错误处理

**错误响应格式**：

```json
{
  "error": {
    "message": "Model not found",
    "type": "invalid_request_error",
    "code": "model_not_found"
  }
}
```

**常见错误码**：

- `model_not_found`: 模型不存在
- `invalid_request`: 请求格式错误
- `authentication_error`: API Key 无效
- `rate_limit_error`: 请求频率超限
- `server_error`: 服务器内部错误
- `timeout_error`: 请求超时

## 常见问题

### Q1: 如何切换不同的模型？

A: 在请求中修改 `model` 参数即可，例如：

- `openai/gpt-4` → OpenAI GPT-4
- `anthropic/claude-3-opus` → Anthropic Claude 3 Opus
- `google/gemini-pro` → Google Gemini Pro

### Q2: API Key 在哪里配置？

A: 可以通过环境变量或配置文件配置。推荐使用环境变量，更安全。

### Q3: 如何查看日志？

A: 日志默认输出到控制台和文件（如果配置了日志文件）。可以通过 `LOG_LEVEL` 环境变量控制日志级别。

### Q4: 支持哪些模型提供商？

A: 目前支持 OpenAI、Anthropic 和 Google。未来会支持更多提供商。

### Q5: 如何处理请求超时？

A: 可以通过 `REQUEST_TIMEOUT` 环境变量设置超时时间（秒），默认 60 秒。

### Q6: 如何添加新的模型提供商？

A: 需要实现 Provider 接口和相应的 Adapter。参考开发文档。

### Q7: 服务无法启动怎么办？

A: 检查：

1. 端口是否被占用
2. API Key 是否正确配置
3. 依赖是否安装完整
4. 查看错误日志

### Q8: 如何提高性能？

A:

1. 使用异步框架（FastAPI）
2. 配置 HTTP 连接池
3. 合理设置超时时间
4. 使用缓存（如果支持）

## 技术支持

如有问题，请：

1. 查看日志文件
2. 检查配置是否正确
3. 参考 API 文档
4. 提交 Issue 到项目仓库

## 更新日志

查看 `CHANGELOG.md` 了解版本更新信息。
