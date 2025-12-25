# GaiaRouter

<div align="center">

[![CI](https://github.com/your-org/GaiaRouter/workflows/CI/badge.svg)](https://github.com/your-org/GaiaRouter/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![Vue 3](https://img.shields.io/badge/Vue-3.3+-brightgreen.svg)](https://vuejs.org/)

**统一的 AI 模型路由服务，提供对多个 AI 提供商的无缝访问**

[快速开始](#快速开始) • [文档](docs/getting-started/README.md) • [示例](examples/) • [贡献指南](CONTRIBUTING.md)

**语言版本:** [English](README.md) | 简体中文

</div>

---

## 什么是 GaiaRouter？

GaiaRouter 是一个智能的 AI 模型路由服务，提供**统一的 API 接口**访问多个 AI 模型提供商（OpenAI、Anthropic、Google、OpenRouter）。它提供：

- 🚀 **统一接口**：所有提供商使用 OpenAI 兼容的 API
- ⚡ **流式支持**：通过 Server-Sent Events 实现实时响应
- 🔄 **自动格式转换**：提供商格式之间的无缝转换
- 🔑 **API 密钥管理**：多租户密钥和组织管理
- 📊 **使用分析**：全面的统计和监控
- 🎛️ **管理后台**：现代化的 Vue 3 管理界面

## 架构

```
客户端 → API 层 → 路由层 → 适配器层 → 提供商层 → 外部 AI API
```

GaiaRouter 采用 4 层架构：
- **API 层**：FastAPI 端点、身份验证、限流
- **路由层**：模型选择、负载均衡、路由逻辑
- **适配器层**：OpenAI 和提供商格式之间的转换
- **提供商层**：外部 AI API 的 HTTP 客户端

详见 [架构文档](docs/architecture/README.md)。

## 快速开始

### 环境要求

- Python 3.11+
- Node.js 18+
- MySQL 8.0+ 或 PostgreSQL 13+

### 安装

**1. 克隆并安装依赖：**

```bash
git clone https://github.com/your-org/GaiaRouter.git
cd GaiaRouter
pip install -r requirements.txt
```

**2. 配置环境：**

```bash
cp env.example .env
# 编辑 .env 文件，填写数据库凭据和 API 密钥
```

**3. 一键初始化：**

```bash
python scripts/init.py
```

这将：
- 运行数据库迁移
- 创建管理员用户（默认：`admin` / `admin123`）
- 设置数据库架构

**4. 启动服务：**

```bash
# 后端（终端 1）
python -m uvicorn src.gaiarouter.main:app --reload

# 前端（终端 2）
cd frontend && npm install && npm run dev
```

**5. 访问：**
- 管理后台：http://localhost:3000
- API 文档：http://localhost:8000/docs
- API 端点：http://localhost:8000/v1

### Docker 快速启动

```bash
docker-compose up -d
docker-compose exec api python scripts/init.py
```

详见 [Docker 部署指南](docs/deployment/docker-deployment.md)。

## 使用示例

```python
import httpx

response = httpx.post(
    "http://localhost:8000/v1/chat/completions",
    headers={"Authorization": "Bearer your-api-key"},
    json={
        "model": "openrouter/anthropic/claude-3.5-sonnet",
        "messages": [{"role": "user", "content": "你好！"}],
        "stream": True
    }
)
```

更多示例请查看 [examples/](examples/) 目录。

## 功能特性

### 核心功能

- ✅ **多提供商支持**：OpenAI、Anthropic、Google、OpenRouter
- ✅ **统一 API**：所有提供商使用 OpenAI 兼容格式
- ✅ **流式响应**：支持 Server-Sent Events (SSE)
- ✅ **格式转换**：自动请求/响应转换
- ✅ **模型注册**：集中式模型管理

### 管理功能

- ✅ **API 密钥管理**：创建、更新、删除 API 密钥
- ✅ **组织管理**：多租户组织支持
- ✅ **使用限制**：每月请求、Token 和费用限制
- ✅ **权限系统**：读取、写入和管理员角色

### 分析功能

- ✅ **使用统计**：请求、Token 和费用追踪
- ✅ **数据聚合**：按日期、模型、提供商、组织聚合
- ✅ **可视化仪表板**：使用 ECharts 的图表和指标

### 管理后台

- ✅ **现代 UI**：Vue 3 + TypeScript + Arco Design
- ✅ **组织管理**：完整的 CRUD 操作
- ✅ **API 密钥管理**：完整的密钥生命周期
- ✅ **统计可视化**：实时分析
- ✅ **用户认证**：安全登录系统

## 技术栈

### 后端
- **FastAPI** - 高性能异步 Web 框架
- **SQLAlchemy** - SQL ORM
- **Alembic** - 数据库迁移
- **httpx** - 异步 HTTP 客户端
- **structlog** - 结构化日志

### 前端
- **Vue 3** - 渐进式 JavaScript 框架（Composition API）
- **TypeScript** - 类型安全开发
- **Vite** - 下一代构建工具
- **Arco Design Vue** - 企业级 UI 组件
- **Pinia** - 状态管理
- **ECharts** - 数据可视化

## 开发理念

### 规范驱动开发（SDD）

GaiaRouter 采用**规范驱动开发（Spec-Driven Development, SDD）**方法论，确保高代码质量和可维护性：

```
📋 规范 → 🏗️ 设计 → ✅ 任务 → 💻 实现 → 📚 文档
```

**为什么选择 SDD？**
- ✅ **更好的架构** - 编码前深思熟虑的设计
- ✅ **更少的 Bug** - 清晰的规范减少误解
- ✅ **更易上手** - 为新贡献者提供全面的文档
- ✅ **可维护的代码** - 意图清晰、文档完善的代码

**GaiaRouter 中的 SDD：**
- **[规范文档](docs/development/sdd/specs/)** - 详细的功能需求和 API 契约
- **[设计文档](docs/development/sdd/designs/)** - 架构和模块设计
- **[任务分解](docs/development/sdd/tasks/)** - 开发任务分解和追踪

**了解更多：** [SDD 文档](docs/development/sdd/README.md) | [开发指南](docs/development/README.md)

## 文档

- 📖 [快速入门指南](docs/getting-started/README.md)
- 🔧 [安装指南](docs/getting-started/installation.md)
- ⚙️ [配置指南](docs/getting-started/configuration.md)
- 📚 [用户指南](docs/guides/user-guide/user-guide.md)
- 🏗️ [架构文档](docs/architecture/README.md)
- 📡 [API 文档](docs/api/api-documentation.md)
- 🚀 [部署指南](docs/deployment/deployment-guide.md)
- 🐳 [Docker 部署](docs/deployment/docker-deployment.md)
- 🛠️ [开发指南](docs/development/README.md)
- 💡 [代码示例](examples/README.md)

## API 端点

### 聊天完成
- `POST /v1/chat/completions` - 支持流式的聊天完成

### 模型
- `GET /v1/models` - 列出可用模型

### API 密钥
- `POST /v1/api-keys` - 创建 API 密钥
- `GET /v1/api-keys` - 列出 API 密钥
- `GET /v1/api-keys/{key_id}` - 获取 API 密钥详情
- `PATCH /v1/api-keys/{key_id}` - 更新 API 密钥
- `DELETE /v1/api-keys/{key_id}` - 删除 API 密钥

### 组织
- `POST /v1/organizations` - 创建组织
- `GET /v1/organizations` - 列出组织
- `GET /v1/organizations/{org_id}` - 获取组织详情
- `PATCH /v1/organizations/{org_id}` - 更新组织
- `DELETE /v1/organizations/{org_id}` - 删除组织

### 统计
- `GET /v1/api-keys/{key_id}/stats` - API 密钥使用统计
- `GET /v1/organizations/{org_id}/stats` - 组织统计
- `GET /v1/stats` - 全局统计

完整 API 文档：http://localhost:8000/docs

## 项目结构

```
GaiaRouter/
├── src/gaiarouter/         # 后端源代码
│   ├── api/                # API 端点
│   ├── router/             # 模型路由逻辑
│   ├── adapters/           # 提供商适配器
│   ├── providers/          # 提供商客户端
│   ├── auth/               # 身份验证
│   ├── organizations/      # 组织管理
│   ├── stats/              # 统计追踪
│   └── database/           # 数据库模型
├── frontend/               # Vue 3 前端
│   ├── src/
│   │   ├── api/            # API 客户端
│   │   ├── components/     # Vue 组件
│   │   ├── views/          # 页面视图
│   │   ├── stores/         # Pinia 状态
│   │   └── router/         # Vue Router
├── docs/                   # 文档
│   ├── getting-started/    # 安装指南
│   ├── guides/             # 用户指南
│   ├── api/                # API 参考
│   ├── architecture/       # 架构文档
│   └── development/        # 开发指南
├── examples/               # 代码示例
├── scripts/                # 实用脚本
├── alembic/                # 数据库迁移
└── tests/                  # 测试套件
```

## 开发

### 运行测试

```bash
# 后端测试
pytest

# 前端测试
cd frontend && npm run test
```

### 代码质量

```bash
# Python 格式化
black .
isort .

# 类型检查
mypy src/

# 前端代码检查
cd frontend && npm run lint
```

详见 [开发指南](docs/development/README.md)。

## 贡献

我们欢迎贡献！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解指南。

### 快速贡献指南

1. Fork 仓库
2. 创建功能分支（`git checkout -b feature/amazing-feature`）
3. 提交更改（`git commit -m 'feat: add amazing feature'`）
4. 推送到分支（`git push origin feature/amazing-feature`）
5. 开启 Pull Request

## 路线图

- [ ] 支持更多 AI 提供商（Cohere、Mistral）
- [ ] 高级负载均衡策略
- [ ] 请求缓存层
- [ ] 增强的限流功能
- [ ] Webhook 事件支持
- [ ] 编程式管理 API

## 常见问题

**Q: 可以使用自己的 API 密钥吗？**
A: 可以！在 `.env` 文件中配置提供商 API 密钥。

**Q: 支持流式传输吗？**
A: 支持！在请求中设置 `"stream": true`。

**Q: 可以用于生产环境吗？**
A: 可以！GaiaRouter 已在生产环境中使用。

详见 [FAQ](docs/guides/faq.md)。

## 统计数据

- **后端**：52 个 Python 文件，约 5000 行代码
- **前端**：27 个 TypeScript/Vue 文件，约 3000 行代码
- **总计**：约 8000+ 行代码
- **测试覆盖率**：80%+
- **完成度**：100%

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

## 致谢

- 使用 [FastAPI](https://fastapi.tiangolo.com/) 构建
- 前端由 [Vue 3](https://vuejs.org/) 驱动
- UI 组件来自 [Arco Design](https://arco.design/)
- 灵感来自 OpenAI API 设计

## 支持

- 📖 [文档](docs/getting-started/README.md)
- 💬 [GitHub 讨论](https://github.com/your-org/GaiaRouter/discussions)
- 🐛 [问题追踪](https://github.com/your-org/GaiaRouter/issues)

---

<div align="center">

**[⬆ 回到顶部](#gaiarouter)**

用 ❤️ 由 GaiaRouter 团队制作

</div>
