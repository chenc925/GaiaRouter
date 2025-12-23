"""
Alembic环境配置
"""

from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.gaiarouter.database.models import Base

# this is the Alembic Config object
config = context.config

# 从环境变量或配置文件获取数据库URL
# 优先使用 alembic.ini 中的配置，如果没有则尝试从环境变量读取
sqlalchemy_url = config.get_main_option("sqlalchemy.url")

# 如果 alembic.ini 中的 URL 是默认值（包含占位符），则尝试从环境变量读取
if not sqlalchemy_url or "user:password@localhost" in sqlalchemy_url:
    try:
        from src.gaiarouter.config import get_settings

        settings = get_settings()
        sqlalchemy_url = settings.database.database_url
        config.set_main_option("sqlalchemy.url", sqlalchemy_url)
    except Exception as e:
        # 如果环境变量未设置，提示用户配置
        import sys

        print(
            "\n" + "=" * 60 + "\n"
            "错误：数据库配置未设置\n"
            "=" * 60 + "\n"
            "请执行以下操作之一：\n"
            "1. 在 alembic.ini 中设置 sqlalchemy.url（推荐用于开发）\n"
            "2. 设置环境变量：DB_HOST, DB_USER, DB_PASSWORD, DB_NAME\n"
            "3. 创建 .env 文件并配置数据库连接信息\n"
            "\n示例：\n"
            "  cp env.example .env\n"
            "  # 然后编辑 .env 文件，填写数据库配置\n"
            "\n或者直接在 alembic.ini 中修改：\n"
            "  sqlalchemy.url = mysql+pymysql://user:password@host:port/database\n"
            "=" * 60 + "\n",
            file=sys.stderr,
        )
        raise RuntimeError("数据库配置未设置。请参考上面的说明进行配置。") from e

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
