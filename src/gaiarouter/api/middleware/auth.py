"""
认证中间件

API Key验证
"""

from typing import Optional

from fastapi import Header, HTTPException, status

from ...auth.api_key_manager import get_api_key_manager
from ...database.models import APIKey
from ...utils.errors import AuthenticationError
from ...utils.logger import get_logger

logger = get_logger(__name__)


async def verify_api_key(
    authorization: Optional[str] = Header(None, alias="Authorization")
) -> APIKey:
    """
    验证API Key

    Args:
      authorization: Authorization header值

    Returns:
      APIKey: API Key对象

    Raises:
      AuthenticationError: 如果API Key无效
    """
    if not authorization:
        raise AuthenticationError("Missing API Key")

    # 解析Bearer token
    if not authorization.startswith("Bearer "):
        raise AuthenticationError("Invalid authorization format")

    api_key_value = authorization[7:]  # 移除"Bearer "前缀

    if not api_key_value:
        raise AuthenticationError("Empty API Key")

    # 从数据库验证API Key
    api_key_manager = get_api_key_manager()
    api_key = api_key_manager.verify_key(api_key_value)

    logger.debug("API Key verified", api_key_id=api_key.id)
    return api_key


def get_current_api_key(authorization: Optional[str] = None) -> Optional[str]:
    """
    获取当前请求的API Key（用于内部调用）

    Args:
      authorization: Authorization header值

    Returns:
      API Key值，如果不存在返回None
    """
    if not authorization:
        return None

    if not authorization.startswith("Bearer "):
        return None

    return authorization[7:]
