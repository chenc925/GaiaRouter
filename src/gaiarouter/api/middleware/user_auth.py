"""
用户认证中间件

用于管理后台的用户认证（基于JWT token）
"""

from typing import Optional
from fastapi import Header, HTTPException, status
from ...utils.errors import AuthenticationError
from ...utils.logger import get_logger
from ...auth.jwt_token import get_token_manager
from ...auth.user_manager import get_user_manager
from ...database.models import User

logger = get_logger(__name__)


async def verify_user_token(
    authorization: Optional[str] = Header(None, alias="Authorization")
) -> User:
    """
    验证用户JWT token
    
    Args:
      authorization: Authorization header值
      
    Returns:
      User: 用户对象
      
    Raises:
      AuthenticationError: 如果token无效
    """
    if not authorization:
        raise AuthenticationError("Missing authentication token")
    
    # 解析Bearer token
    if not authorization.startswith("Bearer "):
        raise AuthenticationError("Invalid authorization format")
    
    token = authorization[7:]  # 移除"Bearer "前缀
    
    if not token:
        raise AuthenticationError("Empty token")
    
    # 验证token
    token_manager = get_token_manager()
    payload = token_manager.verify_token(token)
    
    if not payload:
        raise AuthenticationError("Invalid or expired token")
    
    # 获取用户信息
    user_manager = get_user_manager()
    user = user_manager.get_user(payload.get("user_id"))
    
    if not user:
        raise AuthenticationError("User not found")
    
    if user.status != "active":
        raise AuthenticationError("User is inactive")
    
    logger.debug("User token verified", user_id=user.id, username=user.username)
    return user

