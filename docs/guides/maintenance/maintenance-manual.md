# GaiaRouter 维护手册

## 概述

本文档为运维人员提供 GaiaRouter 系统的维护和故障排除指导。

## 目录

1. [系统架构概述](#系统架构概述)
2. [部署指南](#部署指南)
3. [监控和日志](#监控和日志)
4. [备份与恢复](#备份与恢复)
5. [故障排除](#故障排除)
6. [性能优化](#性能优化)
7. [安全维护](#安全维护)

## 系统架构概述

### 系统组件

- **API 服务**：提供 RESTful API 接口
- **路由服务**：处理模型路由逻辑
- **适配器服务**：处理请求/响应转换
- **提供商服务**：与外部 API 通信

### 技术栈

- **语言**：Python 3.9+ 或 Node.js 18+
- **框架**：FastAPI（Python）或 Express（Node.js）
- **HTTP 客户端**：httpx/aiohttp（Python）或 axios（Node.js）

### 依赖服务

- 外部 AI 模型 API（OpenAI、Anthropic、Google 等）

## 部署指南

### 系统要求

- **CPU**：2 核心以上
- **内存**：2GB 以上
- **磁盘**：10GB 以上
- **网络**：稳定的互联网连接

### 部署步骤

1. **准备环境**

```bash
# 安装Python 3.9+
python3 --version

# 或安装Node.js 18+
node --version
```

2. **安装依赖**

```bash
# Python
pip install -r requirements.txt

# Node.js
npm install
```

3. **配置环境变量**

```bash
export OPENAI_API_KEY=your-key
export ANTHROPIC_API_KEY=your-key
export GOOGLE_API_KEY=your-key
export PORT=8000
export LOG_LEVEL=INFO
```

4. **启动服务**

```bash
# Python
python main.py

# Node.js
npm start
```

### Docker 部署

```bash
# 构建镜像
docker build -t gaiarouter .

# 运行容器
docker run -d \
  --name openrouter \
  -p 8000:8000 \
  -e OPENAI_API_KEY=your-key \
  -e ANTHROPIC_API_KEY=your-key \
  -e GOOGLE_API_KEY=your-key \
  openrouter
```

### 健康检查

```bash
# 检查服务状态
curl http://localhost:8000/health

# 或
curl http://localhost:8000/v1/models
```

## 监控和日志

### 日志位置

- **控制台输出**：标准输出
- **文件日志**：`logs/gaiarouter.log`（如果配置）

### 日志级别

- **DEBUG**：详细调试信息
- **INFO**：一般信息
- **WARNING**：警告信息
- **ERROR**：错误信息

### 日志格式

```
[2024-01-01 12:00:00] [INFO] Request received: POST /v1/chat/completions
[2024-01-01 12:00:01] [ERROR] Model not found: invalid-model
```

### 监控指标

建议监控以下指标：

1. **服务可用性**

   - HTTP 响应状态码
   - 服务响应时间

2. **性能指标**

   - API 响应时间
   - 请求处理速率
   - 错误率

3. **资源使用**
   - CPU 使用率
   - 内存使用率
   - 网络流量

### 监控工具

- **Prometheus**：指标收集
- **Grafana**：可视化
- **ELK Stack**：日志分析

## 备份与恢复

### 配置文件备份

```bash
# 备份配置文件
cp config.yaml config.yaml.backup

# 备份环境变量
env | grep -E "(API_KEY|PORT|LOG)" > env.backup
```

### 日志备份

```bash
# 定期备份日志文件
tar -czf logs-backup-$(date +%Y%m%d).tar.gz logs/
```

### 恢复步骤

1. **恢复配置文件**

```bash
cp config.yaml.backup config.yaml
```

2. **恢复环境变量**

```bash
source env.backup
```

3. **重启服务**

```bash
# 重启服务
systemctl restart openrouter
# 或
docker restart openrouter
```

## 故障排除

### 常见问题

#### 1. 服务无法启动

**症状**：服务启动失败

**可能原因**：

- 端口被占用
- 配置文件错误
- 依赖缺失

**解决方法**：

```bash
# 检查端口占用
lsof -i :8000
# 或
netstat -tulpn | grep 8000

# 检查配置文件
python -m py_compile config.yaml  # Python
node -c config.js  # Node.js

# 检查依赖
pip list  # Python
npm list  # Node.js
```

#### 2. API 请求失败

**症状**：API 返回错误

**可能原因**：

- API Key 无效
- 模型不存在
- 网络问题

**解决方法**：

```bash
# 检查API Key
echo $OPENAI_API_KEY

# 检查模型列表
curl http://localhost:8000/v1/models

# 检查网络连接
curl https://api.openai.com/v1/models
```

#### 3. 响应超时

**症状**：请求超时

**可能原因**：

- 外部 API 响应慢
- 网络延迟
- 超时设置过短

**解决方法**：

```bash
# 增加超时时间
export REQUEST_TIMEOUT=120

# 检查网络连接
ping api.openai.com
```

#### 4. 内存泄漏

**症状**：内存使用持续增长

**可能原因**：

- 连接未关闭
- 缓存未清理

**解决方法**：

```bash
# 监控内存使用
top -p $(pgrep -f openrouter)

# 重启服务
systemctl restart openrouter
```

### 日志分析

#### 查看错误日志

```bash
# 查看最近的错误
grep ERROR logs/gaiarouter.log | tail -20

# 统计错误数量
grep ERROR logs/gaiarouter.log | wc -l
```

#### 查看性能日志

```bash
# 查看响应时间
grep "response_time" logs/gaiarouter.log | awk '{print $NF}'
```

### 调试模式

启用调试模式获取更详细的日志：

```bash
export LOG_LEVEL=DEBUG
# 重启服务
```

## 性能优化

### 1. 连接池配置

```python
# Python - 使用连接池
import httpx

client = httpx.AsyncClient(
    limits=httpx.Limits(max_connections=100, max_keepalive_connections=20)
)
```

### 2. 异步处理

使用异步框架提高并发性能：

```python
# FastAPI支持异步
@app.post("/v1/chat/completions")
async def create_completion(request: ChatRequest):
    ...
```

### 3. 缓存配置

对模型列表等静态数据进行缓存：

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_models():
    ...
```

### 4. 超时优化

根据实际情况调整超时时间：

```bash
# 快速模型：30秒
# 慢速模型：120秒
export REQUEST_TIMEOUT=60
```

## 安全维护

### 1. API Key 管理

- **不要**在代码中硬编码 API Key
- **使用**环境变量或密钥管理服务
- **定期**轮换 API Key
- **限制**API Key 权限

### 2. 日志安全

- **过滤**敏感信息（API Key、用户数据）
- **限制**日志访问权限
- **定期**清理旧日志

### 3. 网络安全

- **使用**HTTPS（生产环境）
- **配置**防火墙规则
- **限制**访问 IP（如需要）

### 4. 更新维护

- **定期**更新依赖包
- **关注**安全公告
- **及时**修复安全漏洞

```bash
# 检查过时的依赖
pip list --outdated  # Python
npm outdated  # Node.js

# 更新依赖
pip install --upgrade -r requirements.txt  # Python
npm update  # Node.js
```

## 升级指南

### 版本升级步骤

1. **备份数据**

```bash
# 备份配置和日志
tar -czf backup-$(date +%Y%m%d).tar.gz config.yaml logs/
```

2. **停止服务**

```bash
systemctl stop openrouter
# 或
docker stop openrouter
```

3. **更新代码**

```bash
git pull origin main
# 或
docker pull openrouter:latest
```

4. **更新依赖**

```bash
pip install -r requirements.txt
# 或
npm install
```

5. **启动服务**

```bash
systemctl start openrouter
# 或
docker start openrouter
```

6. **验证服务**

```bash
curl http://localhost:8000/health
```

## 联系支持

如遇到无法解决的问题，请：

1. 收集错误日志
2. 记录复现步骤
3. 提交 Issue 到项目仓库

## 附录

### 常用命令

```bash
# 查看服务状态
systemctl status openrouter

# 查看日志
tail -f logs/gaiarouter.log

# 重启服务
systemctl restart openrouter

# 查看进程
ps aux | grep openrouter
```

### 配置文件示例

见 `config.yaml.example`
