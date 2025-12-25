# 归档文件说明

本目录存放项目的历史文件，这些文件已不再使用，但保留作为参考。

## 📁 目录结构

### migrations/
**一次性数据迁移脚本**（已完成，不再需要）

- `migrate_key.py` - SQLite 迁移脚本（项目现用 MySQL）
- `migrate_model_prefix.py` - 为模型 ID 添加 openrouter/ 前缀
- `migrate_mysql_key.py` - 将 key_hash 字段改为 key 字段

**说明**：这些迁移脚本用于旧版本数据库升级，现在已通过 Alembic 管理数据库迁移。

---

### config/
**过时的配置文件**（已废弃）

- `config.yaml.example` - YAML 格式配置示例（已改用 .env）
- `setup.py` - Python 打包配置（项目不作为包发布）
- `pyproject.toml` - 项目元数据（不需要）

**说明**：项目现在使用 `.env` 文件进行配置，更简单直接。

---

### docs/
**开发阶段的文档**（已完成的项目文档）

- `COMPLETE_DEVELOPMENT.md` - 开发完成文档
- `IMPLEMENTATION_STATUS.md` - 实现状态文档
- `PROJECT_SUMMARY.md` - 项目总结
- `SDD_COMPLIANCE_CHECK.md` - SDD 规范合规检查

**说明**：这些是开发阶段的文档，项目完成后作为历史记录保存。

---

## ⚠️ 重要提示

**这些文件已不再使用，请勿修改或依赖这些文件！**

如需了解当前项目配置和使用方式，请查看：
- 项目说明: `../README.md`
- 初始化指南: `../INITIALIZATION_GUIDE.md`
- 环境配置: `../env.example` 和 `../ENV_SETUP.md`
- 数据库迁移: 使用 Alembic (`alembic upgrade head`)

---

**归档日期**: 2025-12-25
**归档原因**: 项目清理，移除冗余和过时文件
