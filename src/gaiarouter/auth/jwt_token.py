"""
JWT Token管理模块

处理JWT token的生成和验证
"""

import jwt
import time
from datetime import datetime, timedelta
from typing import Optional, Dict
from ..config import get_settings
from ..utils.logger import get_logger

logger = get_logger(__name__)


class JWTTokenManager:
  """JWT Token管理器"""
  
  def __init__(self):
    self.logger = get_logger(__name__)
    # 使用配置中的密钥，如果没有则使用默认值
    self.secret_key = getattr(get_settings(), 'jwt_secret_key', 'your-secret-key-change-in-production')
    self.algorithm = "HS256"
    self.token_expire_hours = 24  # token过期时间（小时）
  
  def generate_token(self, user_id: str, username: str, role: str = "admin") -> str:
    """
    生成JWT token
    
    Args:
      user_id: 用户ID
      username: 用户名
      role: 用户角色
      
    Returns:
      str: JWT token
    """
    now = datetime.utcnow()
    exp = now + timedelta(hours=self.token_expire_hours)
    
    payload = {
      "user_id": user_id,
      "username": username,
      "role": role,
      "exp": int(exp.timestamp()),
      "iat": int(now.timestamp())
    }
    
    token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    return token
  
  def verify_token(self, token: str) -> Optional[Dict]:
    """
    验证JWT token
    
    Args:
      token: JWT token
      
    Returns:
      Dict: token payload，如果验证失败返回None
    """
    try:
      payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
      return payload
    except jwt.ExpiredSignatureError:
      self.logger.warning("Token expired")
      return None
    except jwt.InvalidTokenError as e:
      self.logger.warning(f"Invalid token: {e}")
      return None
    except Exception as e:
      self.logger.exception("Failed to verify token", exc_info=e)
      return None


# 全局实例
_token_manager: Optional[JWTTokenManager] = None


def get_token_manager() -> JWTTokenManager:
  """获取JWT Token管理器实例（单例模式）"""
  global _token_manager
  if _token_manager is None:
    _token_manager = JWTTokenManager()
  return _token_manager

