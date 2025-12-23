"""
用户管理模块

处理用户认证和用户管理
"""

import secrets
import hashlib
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from bcrypt import hashpw, gensalt, checkpw
from ..database.connection import get_db
from ..database.models import User
from ..utils.logger import get_logger

logger = get_logger(__name__)


class UserManager:
  """用户管理器"""
  
  def __init__(self):
    self.logger = get_logger(__name__)
  
  def _hash_password(self, password: str) -> str:
    """哈希密码"""
    return hashpw(password.encode('utf-8'), gensalt()).decode('utf-8')
  
  def _verify_password(self, password: str, password_hash: str) -> bool:
    """验证密码"""
    try:
      return checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    except Exception as e:
      self.logger.error(f"Password verification failed: {e}")
      return False
  
  def _generate_user_id(self) -> str:
    """生成用户ID"""
    return f"user_{secrets.token_hex(16)}"
  
  def create_user(
    self,
    username: str,
    password: str,
    email: Optional[str] = None,
    full_name: Optional[str] = None,
    role: str = "admin"
  ) -> User:
    """
    创建用户
    
    Args:
      username: 用户名
      password: 密码
      email: 邮箱
      full_name: 全名
      role: 角色
      
    Returns:
      User: 用户对象
    """
    db = next(get_db())
    try:
      # 检查用户名是否已存在
      existing_user = db.query(User).filter(User.username == username).first()
      if existing_user:
        raise ValueError(f"Username {username} already exists")
      
      # 创建用户
      user = User(
        id=self._generate_user_id(),
        username=username,
        password_hash=self._hash_password(password),
        email=email,
        full_name=full_name,
        role=role,
        status="active"
      )
      
      db.add(user)
      db.commit()
      db.refresh(user)
      
      # 在关闭会话前，先访问所有需要的属性，确保它们被加载
      # 这样即使会话关闭后，这些属性仍然可以访问
      _ = user.id
      _ = user.username
      _ = user.role
      _ = user.status
      
      # 将对象从会话中分离，使其可以在会话外使用
      db.expunge(user)
      
      self.logger.info(f"User created: {user.id}")
      return user
      
    except Exception as e:
      db.rollback()
      self.logger.exception("Failed to create user", exc_info=e)
      raise
    finally:
      db.close()
  
  def verify_user(self, username: str, password: str) -> Optional[User]:
    """
    验证用户登录
    
    Args:
      username: 用户名
      password: 密码
      
    Returns:
      User: 用户对象，如果验证失败返回None
    """
    db = next(get_db())
    try:
      user = db.query(User).filter(User.username == username).first()
      
      if not user:
        return None
      
      if user.status != "active":
        return None
      
      if not self._verify_password(password, user.password_hash):
        return None
      
      # 更新最后登录时间
      user.last_login_at = datetime.utcnow()
      db.commit()
      
      # 在关闭会话前，先访问所有需要的属性，确保它们被加载
      # 这样即使会话关闭后，这些属性仍然可以访问
      _ = user.id
      _ = user.username
      _ = user.role
      _ = user.status
      
      # 将对象从会话中分离，使其可以在会话外使用
      db.expunge(user)
      
      return user
      
    except Exception as e:
      self.logger.exception("Failed to verify user", exc_info=e)
      return None
    finally:
      db.close()
  
  def get_user(self, user_id: str) -> Optional[User]:
    """获取用户"""
    db = next(get_db())
    try:
      user = db.query(User).filter(User.id == user_id).first()
      if user:
        # 在关闭会话前，先访问所有需要的属性，确保它们被加载
        _ = user.id
        _ = user.username
        _ = user.role
        _ = user.status
        # 将对象从会话中分离，使其可以在会话外使用
        db.expunge(user)
      return user
    finally:
      db.close()
  
  def get_user_by_username(self, username: str) -> Optional[User]:
    """根据用户名获取用户"""
    db = next(get_db())
    try:
      user = db.query(User).filter(User.username == username).first()
      if user:
        # 在关闭会话前，先访问所有需要的属性，确保它们被加载
        _ = user.id
        _ = user.username
        _ = user.role
        _ = user.status
        # 将对象从会话中分离，使其可以在会话外使用
        db.expunge(user)
      return user
    finally:
      db.close()


# 全局实例
_user_manager: Optional[UserManager] = None


def get_user_manager() -> UserManager:
  """获取用户管理器实例（单例模式）"""
  global _user_manager
  if _user_manager is None:
    _user_manager = UserManager()
  return _user_manager

