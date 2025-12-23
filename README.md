# GaiaRouter - AI 模型路由服务

一个简单版本的 GaiaRouter，提供统一的 API 接口访问多个 AI 模型。

## 项目概述

GaiaRouter 是一个 AI 模型路由服务，支持多个 AI 模型提供商（OpenAI、Anthropic、Google、OpenRouter），提供统一的 API 接口，支持流式响应，并提供完整的后台管理功能。

## 技术栈

### 后端

- **Python 3.11+**
- **FastAPI** - 高性能异步 Web 框架
- **SQLAlchemy** - ORM 框架
- **Alembic** - 数据库迁移工具
- **httpx** - 异步 HTTP 客户端
- **structlog** - 结构化日志
- **阿里云 RDS** - 数据库（MySQL/PostgreSQL）

### 前端

- **Vue 3** - 前端框架（Composition API）
- **TypeScript** - 类型安全
- **Vite** - 构建工具
- **Arco Design Vue** - UI 组件库
- **Pinia** - 状态管理
- **Vue Router** - 路由管理
- **Axios** - HTTP 客户端
- **ECharts** - 数据可视化

## 功能特性

### 核心功能

- ✅ 多模型提供商支持（OpenAI、Anthropic、Google、OpenRouter）
- ✅ 统一的 API 接口
- ✅ 流式响应支持（Server-Sent Events）
- ✅ 请求/响应格式自动转换
- ✅ 模型路由和注册

### 管理功能

- ✅ API Key 管理（创建、查询、更新、删除）
- ✅ 组织管理（创建、查询、更新、删除）
- ✅ 使用限制管理（月度请求、Token、费用限制）
- ✅ 权限管理（read、write、admin）

### 统计功能

- ✅ 请求统计收集
- ✅ 统计数据存储
- ✅ 统计查询 API
- ✅ 数据聚合（按日期、模型、提供商）
- ✅ 统计可视化界面

### 后台管理界面

- ✅ 组织管理界面（CRUD）
- ✅ API Key 管理界面（CRUD）
- ✅ 数据统计可视化
- ✅ 用户认证

## 项目结构

```
sddDemo/
├── frontend/              # 前端项目
│   ├── src/
│   │   ├── api/          # API接口封装
│   │   ├── components/   # 公共组件
│   │   ├── views/        # 页面组件
│   │   ├── stores/       # Pinia状态管理
│   │   ├── router/       # 路由配置
│   │   └── utils/        # 工具函数
│   └── package.json
├── src/gaiarouter/        # 后端项目
│   ├── api/              # API层
│   ├── auth/             # 认证模块
│   ├── organizations/    # 组织管理模块
│   ├── stats/            # 统计模块
│   ├── providers/        # 提供商层
│   ├── adapters/         # 适配器层
│   ├── router/           # 路由层
│   ├── database/         # 数据库模块
│   └── main.py           # 应用入口
├── docs/                 # 文档
├── specs/                # 规范文档
├── designs/              # 设计文档
├── tasks/                # 任务分解
├── alembic/              # 数据库迁移
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## 快速开始

### 环境要求

- Python 3.11+
- Node.js 18+
- MySQL 8.0+ 或 PostgreSQL 13+

### 后端启动

```bash
# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp env.example .env
# 编辑 .env 文件，设置数据库和API Key
# 详细配置说明请参考 ENV_SETUP.md
# 注意：.env 文件包含敏感信息，不要提交到版本控制

# 运行数据库迁移
alembic upgrade head

# 启动服务
uvicorn src.gaiarouter.main:app --reload
```

### 前端启动

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

### Docker 启动

```bash
# 启动所有服务
docker-compose up -d

# 运行数据库迁移
docker-compose exec api alembic upgrade head
```

## API 文档

启动后端服务后，访问：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

详细 API 文档请参考：`docs/api/api-documentation.md`

## 前端访问

启动前端服务后，访问：

- 管理后台: http://localhost:3000

使用 API Key 登录后即可使用管理功能。

## 主要 API 端点

### 聊天完成

- `POST /v1/chat/completions` - 聊天完成（支持流式）

### 模型

- `GET /v1/models` - 模型列表

### API Key 管理

- `POST /v1/api-keys` - 创建 API Key
- `GET /v1/api-keys` - 查询 API Key 列表
- `GET /v1/api-keys/{key_id}` - 查询单个 API Key
- `PATCH /v1/api-keys/{key_id}` - 更新 API Key
- `DELETE /v1/api-keys/{key_id}` - 删除 API Key

### 组织管理

- `POST /v1/organizations` - 创建组织
- `GET /v1/organizations` - 查询组织列表
- `GET /v1/organizations/{org_id}` - 查询单个组织
- `PATCH /v1/organizations/{org_id}` - 更新组织
- `DELETE /v1/organizations/{org_id}` - 删除组织

### 统计

- `GET /v1/api-keys/{key_id}/stats` - API Key 统计
- `GET /v1/organizations/{org_id}/stats` - 组织统计
- `GET /v1/stats` - 全局统计

## 文档

- [API 文档](docs/api/api-documentation.md)
- [部署指南](docs/deployment/deployment-guide.md)
- [Docker 部署](docs/deployment/docker-deployment.md)
- [用户指南](docs/user-guide/user-guide.md)
- [测试计划](docs/test-plan/test-plan.md)
- [维护手册](docs/maintenance/maintenance-manual.md)
- [前端设计](designs/openrouter/frontend-design.md)

## 开发规范

本项目遵循 SDD（Spec-Driven Development）规范驱动开发：

- **规范文档**：`specs/` - 功能规范和需求
- **设计文档**：`designs/` - 架构和模块设计
- **任务分解**：`tasks/` - 开发任务分解

详细规范请参考：

- [编码规范](specs/base/coding-standards.md)
- [变更日志](specs/changes/changelog.md)

## 代码统计

- **后端文件数**: 52 个 Python 文件
- **前端文件数**: 27 个文件
- **代码行数**: 约 8000+ 行
- **完成度**: 100%

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！
