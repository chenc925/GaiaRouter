# Alembic 数据库迁移配置说明

## 问题说明

运行 `alembic upgrade head` 时，如果环境变量未设置，可能会遇到以下错误：

```
pydantic_core._pydantic_core.ValidationError: 3 validation errors for DatabaseSettings
host
  Field required [type=missing, input_value={'user': 'ls'}, input_type=dict]
password
  Field required [type=missing, input_value={'user': 'ls'}, input_type=dict]
database
  Field required [type=missing, input_value={'user': 'ls'}, input_type=dict]
```

## 原因

Alembic 迁移需要数据库连接信息。配置可以通过以下方式提供：

1. **alembic.ini 文件**（推荐用于开发环境）
2. **环境变量**（推荐用于生产环境）
3. **.env 文件**（推荐用于本地开发）

## 解决方案

### 方案 1：使用 alembic.ini（最简单，适合开发）

直接编辑 `alembic.ini` 文件，修改第 8 行的数据库连接 URL：

```ini
sqlalchemy.url = mysql+pymysql://用户名:密码@主机:端口/数据库名
```

示例：

```ini
sqlalchemy.url = mysql+pymysql://root:password@localhost:3306/gaiarouter
```

### 方案 2：使用环境变量（推荐用于生产）

1. 创建 `.env` 文件：

   ```bash
   cp env.example .env
   ```

2. 编辑 `.env` 文件，填写数据库配置：

   ```bash
   DB_HOST=your-rds-host.rds.aliyuncs.com
   DB_PORT=3306
   DB_USER=your_username
   DB_PASSWORD=your_password
   DB_NAME=gaiarouter
   ```

3. 运行迁移：
   ```bash
   alembic upgrade head
   ```

### 方案 3：临时设置环境变量

```bash
export DB_HOST=localhost
export DB_USER=root
export DB_PASSWORD=password
export DB_NAME=gaiarouter
alembic upgrade head
```

## 验证配置

运行迁移前，可以检查配置是否正确：

```bash
# 检查 alembic.ini 中的 URL
grep sqlalchemy.url alembic.ini

# 或者检查环境变量
env | grep DB_
```

## 注意事项

1. **安全性**：`.env` 文件和 `alembic.ini` 中的密码不要提交到版本控制
2. **开发环境**：建议使用 `alembic.ini` 配置，方便快速开发
3. **生产环境**：建议使用环境变量，更安全且灵活

## 常见问题

### Q: 为什么 alembic.ini 中有默认 URL 还会报错？

A: 如果 `alembic.ini` 中的 URL 包含占位符（如 `user:password@localhost`），系统会尝试从环境变量读取。如果环境变量也未设置，就会报错。

### Q: 如何知道应该使用哪种配置方式？

A:

- **本地开发**：使用 `alembic.ini` 或 `.env` 文件
- **CI/CD**：使用环境变量
- **生产环境**：使用环境变量或密钥管理服务

### Q: 修改了配置后还是报错？

A: 确保：

1. `.env` 文件在项目根目录
2. 环境变量名称正确（`DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`）
3. `alembic.ini` 中的 URL 格式正确
