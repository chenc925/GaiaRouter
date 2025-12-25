# GaiaRouter 初始化指南

本文档提供完整的项目初始化步骤，适用于首次部署和本地开发环境搭建。

## 前置要求

- Python 3.11+
- MySQL 8.0+ 或 PostgreSQL 13+
- Node.js 18+ (用于前端)
- Git

## 初始化步骤

### 1. 克隆项目并安装依赖

```bash
# 克隆项目
git clone <repository-url>
cd GaiaRouter

# 安装后端依赖
pip install -r requirements.txt

# 安装前端依赖
cd frontend
npm install
cd ..
```

### 2. 配置环境变量

```bash
# 复制环境变量模板
cp env.example .env
```

编辑 `.env` 文件，配置以下**必需**的环境变量：

```bash
# ============================================
# 数据库配置（必需）
# ============================================
DB_HOST=localhost                    # 数据库地址
DB_PORT=3306                         # 数据库端口
DB_USER=root                         # 数据库用户名
DB_PASSWORD=your_password            # 数据库密码（请修改）
DB_NAME=gaiarouter                   # 数据库名称

# ============================================
# AI 模型提供商 API Keys（可选，至少配置一个）
# ============================================
# 注意：只配置你需要使用的提供商
OPENAI_API_KEY=sk-xxx                # OpenAI API Key
ANTHROPIC_API_KEY=sk-ant-xxx         # Anthropic API Key
GOOGLE_API_KEY=xxx                   # Google API Key
OPENROUTER_API_KEY=sk-or-xxx         # OpenRouter API Key

# ============================================
# 服务器配置（可选，有默认值）
# ============================================
HOST=0.0.0.0
PORT=8000
DEBUG=false
LOG_LEVEL=INFO
```

**重要提示：**
- `.env` 文件包含敏感信息，已在 `.gitignore` 中，不会被提交到版本控制
- `DB_PASSWORD` 和 API Keys 必须使用真实值替换占位符

### 3. 准备数据库

#### 选项A：使用本地 MySQL（推荐开发环境）

```bash
# macOS 安装 MySQL
brew install mysql
brew services start mysql

# 创建数据库
mysql -u root -p -e "CREATE DATABASE gaiarouter CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# 验证
mysql -u root -p -e "SHOW DATABASES LIKE 'gaiarouter';"
```

#### 选项B：使用阿里云 RDS（生产环境）

1. 在阿里云控制台创建 RDS MySQL 实例
2. 配置白名单允许你的 IP 访问
3. 创建数据库 `gaiarouter`
4. 在 `.env` 中配置 RDS 连接信息

### 4. 运行数据库迁移

**重要：**首先清理 `alembic.ini` 中的硬编码数据库连接（安全问题）。

编辑 `alembic.ini`，将第8行改为：

```ini
# 使用环境变量，不要硬编码密码
sqlalchemy.url =
```

然后运行迁移：

```bash
# 运行所有迁移，创建数据库表
python -m alembic upgrade head
```

**迁移会创建以下表：**
- `organizations` - 组织表
- `api_keys` - API Key 管理表
- `users` - 用户表
- `request_stats` - 请求统计表
- `models` - AI 模型信息表

### 5. 创建管理员用户

```bash
# 使用默认用户名和密码（admin/admin123）
python scripts/create_admin_user.py

# 或者自定义用户名和密码
python scripts/create_admin_user.py --username myadmin --password mypassword123
```

**输出示例：**
```
初始化数据库...
创建管理员用户: admin
✓ 用户创建成功！
  用户ID: xxxx
  用户名: admin
  角色: admin
```

**默认管理员凭据：**
- 用户名：`admin`
- 密码：`admin123`

⚠️ **安全提示：** 生产环境请务必修改默认密码！

### 6. （可选）同步 OpenRouter 模型

如果你配置了 `OPENROUTER_API_KEY`，可以从 OpenRouter 同步模型列表到数据库：

```bash
# 通过 API 调用同步（需要启动后端服务后）
# 访问管理后台的模型管理页面，点击"同步模型"按钮
```

或者使用 Python 脚本：

```python
# 创建 scripts/sync_models.py
import asyncio
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.gaiarouter.models.sync import sync_models_from_openrouter

async def main():
    print("开始同步 OpenRouter 模型...")
    stats = await sync_models_from_openrouter()
    print(f"同步完成: {stats}")

if __name__ == "__main__":
    asyncio.run(main())
```

```bash
python scripts/sync_models.py
```

### 7. 启动服务

```bash
# 启动后端（开发模式）
python -m uvicorn src.gaiarouter.main:app --reload

# 在新终端启动前端
cd frontend
npm run dev
```

### 8. 验证安装

**后端服务：**
- API: http://localhost:8000
- Swagger 文档: http://localhost:8000/docs
- 健康检查: http://localhost:8000/health

**前端应用：**
- 管理后台: http://localhost:3000
- 使用创建的管理员账号登录

## 初始化完成检查清单

- [ ] 环境变量配置完成（.env）
- [ ] 数据库创建成功
- [ ] Alembic 迁移执行成功
- [ ] 管理员用户创建成功
- [ ] （可选）OpenRouter 模型同步完成
- [ ] 后端服务启动成功
- [ ] 前端服务启动成功
- [ ] 能够登录管理后台

## 故障排查

### 数据库连接失败

**错误信息：** `OperationalError: (2003, "Can't connect to MySQL server")`

**解决方案：**
1. 检查 MySQL 服务是否运行：`brew services list` (macOS)
2. 验证 `.env` 中的数据库配置
3. 测试数据库连接：`mysql -h 127.0.0.1 -u root -p`

### Alembic 迁移失败

**错误信息：** `ValidationError: Field required`

**解决方案：**
1. 确保 `.env` 文件存在且包含所有必需的数据库变量
2. 确保 `alembic.ini` 第8行为空（`sqlalchemy.url =`）
3. 检查环境变量是否加载：`python check_env.py`

### 模块找不到错误

**错误信息：** `ModuleNotFoundError: No module named 'xxx'`

**解决方案：**
```bash
pip install -r requirements.txt
```

### 管理员用户已存在

**错误信息：** `✗ 用户已存在`

**解决方案：**
- 如果是第一次初始化，请检查是否之前已创建过
- 可以使用不同的用户名：`--username newadmin`
- 或删除已有用户后重新创建

## 下一步

初始化完成后，你可以：

1. **创建组织和 API Key**
   - 登录管理后台
   - 创建组织
   - 生成 API Key 用于调用服务

2. **配置模型**
   - 在模型管理页面启用需要的模型
   - 配置模型参数和限制

3. **测试 API**
   - 使用 Swagger 文档测试 API
   - 查看请求统计和使用情况

4. **部署到生产环境**
   - 参考 `docs/deployment/deployment-guide.md`
   - 使用 Docker 部署：`docs/deployment/docker-deployment.md`

## 重置环境

如果需要完全重置环境：

```bash
# 1. 删除数据库
mysql -u root -p -e "DROP DATABASE IF EXISTS gaiarouter;"

# 2. 重新创建数据库
mysql -u root -p -e "CREATE DATABASE gaiarouter CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# 3. 重新运行迁移
python -m alembic upgrade head

# 4. 重新创建管理员用户
python scripts/create_admin_user.py
```

## 参考文档

- [快速启动指南](QUICK_START.md)
- [环境变量配置](ENV_SETUP.md)
- [Alembic 配置说明](ALEMBIC_SETUP.md)
- [API 文档](docs/api/api-documentation.md)
- [部署指南](docs/deployment/deployment-guide.md)
