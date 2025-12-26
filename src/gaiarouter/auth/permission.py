"""
权限管理模块

提供API Key权限检查功能
"""

from typing import List

from ..database.models import APIKey
from ..utils.logger import get_logger

logger = get_logger(__name__)


class Permission:
    """权限常量"""

    READ = "read"
    WRITE = "write"
    ADMIN = "admin"

    @staticmethod
    def check(api_key: APIKey, required_permission: str) -> bool:
        """
        检查API Key权限

        Args:
          api_key: API Key对象
          required_permission: 所需权限

        Returns:
          bool: 是否有权限
        """
        if not api_key:
            return False

        if not api_key.permissions:
            return False

        # ADMIN权限拥有所有权限
        if Permission.ADMIN in api_key.permissions:
            return True

        # 检查所需权限
        return required_permission in api_key.permissions

    @staticmethod
    def has_read(api_key: APIKey) -> bool:
        """检查是否有读权限"""
        return Permission.check(api_key, Permission.READ)

    @staticmethod
    def has_write(api_key: APIKey) -> bool:
        """检查是否有写权限"""
        return Permission.check(api_key, Permission.WRITE)

    @staticmethod
    def has_admin(api_key: APIKey) -> bool:
        """检查是否有管理员权限"""
        return Permission.check(api_key, Permission.ADMIN)
