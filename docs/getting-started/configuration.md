# 环境变量配置说明

## 创建 .env 文件

项目使用环境变量进行配置。请按照以下步骤设置：

1. 复制环境变量示例文件：

   ```bash
   cp env.example .env
   ```

2. 编辑 `.env` 文件，填写实际的配置值。

## 必需的环境变量

### 数据库配置（必需）

```bash
DB_HOST=your-rds-host.rds.aliyuncs.com
DB_PORT=3306
DB_USER=your_username
DB_PASSWORD=your_password
DB_NAME=gaiarouter
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20
```

### AI 模型提供商 API Key（至少配置一个）

```bash
# OpenAI（如果使用OpenAI模型）
OPENAI_API_KEY=sk-your-openai-api-key

# Anthropic（如果使用Anthropic模型）
ANTHROPIC_API_KEY=sk-ant-your-anthropic-api-key

# Google（如果使用Google模型）
GOOGLE_API_KEY=your-google-api-key

# OpenRouter（如果使用OpenRouter模型）
OPENROUTER_API_KEY=sk-or-your-openrouter-api-key
```

### 服务器配置（可选，有默认值）

```bash
HOST=0.0.0.0
PORT=8000
DEBUG=false
LOG_LEVEL=INFO
```

### 请求配置（可选，有默认值）

```bash
REQUEST_TIMEOUT=60
MAX_RETRIES=3
```

## 完整示例

请参考 `env.example` 文件获取完整的配置示例。

## 注意事项

1. **安全**: `.env` 文件包含敏感信息，不要提交到版本控制系统
2. **格式**: 环境变量值不需要引号，除非值中包含空格
3. **注释**: 使用 `#` 开头添加注释
4. **布尔值**: 使用 `true` 或 `false`（小写）

## 验证配置

启动应用后，检查日志确认配置是否正确加载。如果配置有误，应用会显示相应的错误信息。
