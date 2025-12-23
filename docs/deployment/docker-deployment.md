# Docker 部署指南

## 概述

本文档提供使用 Docker 和 Docker Compose 部署 GaiaRouter 系统的详细步骤。

## 前置要求

- Docker 20.10+
- Docker Compose 2.0+

## 快速开始

### 1. 克隆项目

```bash
git clone <repository-url>
cd sddDemo
```

### 2. 配置环境变量

创建`.env`文件：

```bash
cp .env.example .env
```

编辑`.env`文件，设置必要的环境变量：

```env
# 数据库配置
DB_HOST=db
DB_PORT=3306
DB_USER=openrouter
DB_PASSWORD=your_password
DB_NAME=gaiarouter

# API Keys
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
GOOGLE_API_KEY=your_google_key
OPENROUTER_API_KEY=your_openrouter_key

# 服务器配置
DEBUG=false
LOG_LEVEL=INFO
HOST=0.0.0.0
PORT=8000
```

### 3. 启动服务

```bash
# 使用Docker Compose启动
docker-compose up -d

# 查看日志
docker-compose logs -f api

# 查看服务状态
docker-compose ps
```

### 4. 验证部署

```bash
# 健康检查
curl http://localhost:8000/health

# 测试API
curl http://localhost:8000/
```

## 数据库迁移

首次部署需要运行数据库迁移：

```bash
# 进入容器
docker-compose exec api bash

# 运行迁移
alembic upgrade head
```

## 常用命令

### 启动服务

```bash
docker-compose up -d
```

### 停止服务

```bash
docker-compose down
```

### 重启服务

```bash
docker-compose restart
```

### 查看日志

```bash
# 查看所有服务日志
docker-compose logs -f

# 查看API服务日志
docker-compose logs -f api

# 查看数据库日志
docker-compose logs -f db
```

### 进入容器

```bash
# 进入API容器
docker-compose exec api bash

# 进入数据库容器
docker-compose exec db bash
```

### 备份数据库

```bash
# 备份
docker-compose exec db mysqldump -u openrouter -popenrouter123 openrouter > backup.sql

# 恢复
docker-compose exec -T db mysql -u openrouter -popenrouter123 openrouter < backup.sql
```

## 生产环境配置

### 1. 使用外部数据库

修改`docker-compose.yml`：

```yaml
services:
  api:
    environment:
      - DB_HOST=your-db-host
      - DB_PORT=3306
      - DB_USER=your-db-user
      - DB_PASSWORD=your-db-password
      - DB_NAME=your-db-name
    # 移除depends_on
    # depends_on:
    #   - db

  # 移除db服务
  # db:
```

### 2. 使用环境变量文件

创建`.env.production`：

```env
DB_HOST=your-production-db-host
DB_PORT=3306
DB_USER=your-db-user
DB_PASSWORD=your-secure-password
DB_NAME=gaiarouter
DEBUG=false
LOG_LEVEL=INFO
```

启动时指定环境文件：

```bash
docker-compose --env-file .env.production up -d
```

### 3. 配置资源限制

在`docker-compose.yml`中添加资源限制：

```yaml
services:
  api:
    deploy:
      resources:
        limits:
          cpus: "2"
          memory: 2G
        reservations:
          cpus: "1"
          memory: 1G
```

### 4. 配置日志

```yaml
services:
  api:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

## 故障排查

### 容器无法启动

```bash
# 查看容器日志
docker-compose logs api

# 检查容器状态
docker-compose ps

# 检查端口占用
netstat -tuln | grep 8000
```

### 数据库连接失败

```bash
# 检查数据库容器状态
docker-compose ps db

# 查看数据库日志
docker-compose logs db

# 测试数据库连接
docker-compose exec api python -c "from src.gaiarouter.database.connection import get_db; print('OK')"
```

### API 无法访问

```bash
# 检查API容器状态
docker-compose ps api

# 查看API日志
docker-compose logs api

# 检查端口
curl http://localhost:8000/health
```

## 更新部署

```bash
# 拉取最新代码
git pull

# 重新构建镜像
docker-compose build

# 重启服务
docker-compose up -d

# 运行数据库迁移
docker-compose exec api alembic upgrade head
```

## 清理

```bash
# 停止并删除容器
docker-compose down

# 删除容器和卷
docker-compose down -v

# 删除镜像
docker-compose down --rmi all
```
