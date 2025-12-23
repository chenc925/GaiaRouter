# GaiaRouter 部署指南

## 概述

本文档提供 GaiaRouter 系统的详细部署指南，包括不同环境的部署方式。

## 目录

1. [部署前准备](#部署前准备)
2. [开发环境部署](#开发环境部署)
3. [生产环境部署](#生产环境部署)
4. [Docker 部署](#docker部署)
5. [Kubernetes 部署](#kubernetes部署)
6. [配置说明](#配置说明)
7. [健康检查](#健康检查)
8. [故障排查](#故障排查)

## 部署前准备

### 系统要求

- **操作系统**：Linux、macOS、Windows
- **Python**：3.9+ 或 **Node.js**：18+
- **内存**：至少 2GB
- **磁盘**：至少 10GB 可用空间
- **网络**：稳定的互联网连接

### 获取 API Key

1. **OpenAI API Key**

   - 访问 https://platform.openai.com/api-keys
   - 创建新的 API Key

2. **Anthropic API Key**

   - 访问 https://console.anthropic.com/
   - 创建新的 API Key

3. **Google API Key**
   - 访问 https://console.cloud.google.com/
   - 创建新的 API Key

## 开发环境部署

### 1. 克隆项目

```bash
git clone <repository-url>
cd openrouter
```

### 2. 创建虚拟环境（Python）

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate  # Windows
```

### 3. 安装依赖

```bash
# Python
pip install -r requirements.txt

# Node.js
npm install
```

### 4. 配置环境变量

创建 `.env` 文件：

```bash
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key
GOOGLE_API_KEY=your-google-key
PORT=8000
LOG_LEVEL=DEBUG
```

### 5. 启动服务

```bash
# Python
python main.py

# Node.js
npm start
```

服务将在 `http://localhost:8000` 启动。

### 6. 验证部署

```bash
# 检查健康状态
curl http://localhost:8000/health

# 检查模型列表
curl http://localhost:8000/v1/models
```

## 生产环境部署

### 方式 1：直接部署

#### 1. 准备服务器

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装Python
sudo apt install python3 python3-pip python3-venv -y

# 或安装Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs
```

#### 2. 部署应用

```bash
# 创建应用目录
sudo mkdir -p /opt/openrouter
sudo chown $USER:$USER /opt/openrouter

# 复制代码
cp -r . /opt/openrouter/
cd /opt/openrouter
```

#### 3. 安装依赖

```bash
# Python
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Node.js
npm install --production
```

#### 4. 配置环境变量

创建 `/etc/openrouter/env`：

```bash
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key
GOOGLE_API_KEY=your-google-key
PORT=8000
LOG_LEVEL=INFO
REQUEST_TIMEOUT=60
```

#### 5. 创建 systemd 服务

创建 `/etc/systemd/system/gaiarouter.service`：

```ini
[Unit]
Description=GaiaRouter Service
After=network.target

[Service]
Type=simple
User=openrouter
WorkingDirectory=/opt/openrouter
EnvironmentFile=/etc/openrouter/env
ExecStart=/opt/openrouter/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### 6. 启动服务

```bash
# 创建用户
sudo useradd -r -s /bin/false openrouter
sudo chown -R openrouter:openrouter /opt/openrouter

# 启动服务
sudo systemctl daemon-reload
sudo systemctl enable gaiarouter
sudo systemctl start openrouter

# 查看状态
sudo systemctl status openrouter
```

### 方式 2：使用 Nginx 反向代理

#### 1. 安装 Nginx

```bash
sudo apt install nginx -y
```

#### 2. 配置 Nginx

创建 `/etc/nginx/sites-available/openrouter`：

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### 3. 启用配置

```bash
sudo ln -s /etc/nginx/sites-available/openrouter /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

#### 4. 配置 HTTPS（可选）

使用 Let's Encrypt：

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com
```

## Docker 部署

### 1. 构建镜像

```bash
docker build -t gaiarouter:latest .
```

### 2. 运行容器

```bash
docker run -d \
  --name openrouter \
  -p 8000:8000 \
  -e OPENAI_API_KEY=your-key \
  -e ANTHROPIC_API_KEY=your-key \
  -e GOOGLE_API_KEY=your-key \
  -e PORT=8000 \
  -e LOG_LEVEL=INFO \
  openrouter:latest
```

### 3. 使用 Docker Compose

创建 `docker-compose.yml`：

```yaml
version: "3.8"

services:
  openrouter:
    build: .
    container_name: openrouter
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
      - PORT=8000
      - LOG_LEVEL=INFO
    restart: unless-stopped
    volumes:
      - ./logs:/app/logs
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

启动服务：

```bash
docker-compose up -d
```

## Kubernetes 部署

### 1. 创建 ConfigMap

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: openrouter-config
data:
  PORT: "8000"
  LOG_LEVEL: "INFO"
  REQUEST_TIMEOUT: "60"
```

### 2. 创建 Secret

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: openrouter-secrets
type: Opaque
stringData:
  OPENAI_API_KEY: your-openai-key
  ANTHROPIC_API_KEY: your-anthropic-key
  GOOGLE_API_KEY: your-google-key
```

### 3. 创建 Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: openrouter
spec:
  replicas: 3
  selector:
    matchLabels:
      app: openrouter
  template:
    metadata:
      labels:
        app: openrouter
    spec:
      containers:
        - name: openrouter
          image: openrouter:latest
          ports:
            - containerPort: 8000
          envFrom:
            - configMapRef:
                name: openrouter-config
            - secretRef:
                name: openrouter-secrets
          resources:
            requests:
              memory: "512Mi"
              cpu: "250m"
            limits:
              memory: "1Gi"
              cpu: "500m"
          livenessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 30
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 5
            periodSeconds: 5
```

### 4. 创建 Service

```yaml
apiVersion: v1
kind: Service
metadata:
  name: gaiarouter-service
spec:
  selector:
    app: openrouter
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8000
  type: LoadBalancer
```

### 5. 部署

```bash
kubectl apply -f configmap.yaml
kubectl apply -f secret.yaml
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
```

## 配置说明

### 环境变量

| 变量名              | 说明              | 默认值  | 必需         |
| ------------------- | ----------------- | ------- | ------------ |
| `OPENAI_API_KEY`    | OpenAI API Key    | -       | 是（如使用） |
| `ANTHROPIC_API_KEY` | Anthropic API Key | -       | 是（如使用） |
| `GOOGLE_API_KEY`    | Google API Key    | -       | 是（如使用） |
| `PORT`              | 服务端口          | 8000    | 否           |
| `HOST`              | 服务主机          | 0.0.0.0 | 否           |
| `LOG_LEVEL`         | 日志级别          | INFO    | 否           |
| `REQUEST_TIMEOUT`   | 请求超时（秒）    | 60      | 否           |
| `MAX_RETRIES`       | 最大重试次数      | 3       | 否           |

### 配置文件

创建 `config.yaml`：

```yaml
models:
  - id: openai/gpt-4
    provider: openai
    api_key: ${OPENAI_API_KEY}
  - id: anthropic/claude-3-opus
    provider: anthropic
    api_key: ${ANTHROPIC_API_KEY}

server:
  port: 8000
  host: 0.0.0.0

logging:
  level: INFO
  file: logs/gaiarouter.log

timeouts:
  request: 60
  connect: 10
```

## 验证部署

### 1. 健康检查

```bash
curl http://localhost:8000/health
```

预期响应：

```json
{ "status": "healthy" }
```

### 2. 模型列表

```bash
curl http://localhost:8000/v1/models
```

### 3. 测试聊天接口

```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "openai/gpt-4",
    "messages": [{"role": "user", "content": "Hello"}]
  }'
```

## 故障排除

### 服务无法启动

1. 检查端口是否被占用
2. 检查环境变量是否正确
3. 查看日志文件

### API 请求失败

1. 检查 API Key 是否有效
2. 检查网络连接
3. 查看错误日志

### 性能问题

1. 检查资源使用情况
2. 调整超时设置
3. 优化配置

## 监控建议

- 使用 Prometheus 收集指标
- 使用 Grafana 可视化
- 配置告警规则
- 定期检查日志

## 安全建议

1. 使用 HTTPS（生产环境）
2. 限制 API 访问
3. 定期更新依赖
4. 使用密钥管理服务
5. 配置防火墙规则
