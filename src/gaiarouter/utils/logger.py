"""
日志模块

使用structlog进行结构化日志记录
"""

import logging
import sys
from typing import Optional

import structlog

from ..config import get_settings


def setup_logger(log_level: Optional[str] = None) -> None:
    """
    设置日志配置

    Args:
      log_level: 日志级别，默认从配置读取
    """
    settings = get_settings()
    level = log_level or settings.server.log_level

    # 配置标准库logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, level.upper()),
    )

    # 配置structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def get_logger(name: str = __name__):
    """
    获取日志记录器

    Args:
      name: 日志记录器名称

    Returns:
      日志记录器实例
    """
    return structlog.get_logger(name)
