"""
数据库连接管理

使用SQLAlchemy管理数据库连接（阿里云RDS）
"""

from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import QueuePool

from ..config import get_settings

# 全局数据库引擎和会话工厂
_engine = None
_SessionLocal = None


def init_db() -> None:
    """
    初始化数据库连接

    创建数据库引擎和会话工厂，并创建所有表
    """
    global _engine, _SessionLocal

    settings = get_settings()

    # 创建数据库引擎
    _engine = create_engine(
        settings.database.database_url,
        poolclass=QueuePool,
        pool_size=settings.database.pool_size,
        max_overflow=settings.database.max_overflow,
        pool_pre_ping=True,  # 连接前检查连接是否有效
        echo=settings.server.debug,  # 调试模式下打印SQL
    )

    # 创建所有表
    from .models import Base

    Base.metadata.create_all(bind=_engine)

    # 创建会话工厂
    _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)


def get_db() -> Generator[Session, None, None]:
    """
    获取数据库会话（依赖注入）

    Yields:
      Session: 数据库会话
    """
    if _SessionLocal is None:
        init_db()

    db = _SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_engine():
    """获取数据库引擎"""
    if _engine is None:
        init_db()
    return _engine
