"""
API Key管理器

提供API Key的完整生命周期管理
"""

import secrets
import hashlib
from typing import List, Optional
from datetime import datetime, timedelta
from ..database.models import APIKey
from .key_storage import KeyStorage, get_key_storage
from .permission import Permission
from ..utils.logger import get_logger
from ..utils.errors import InvalidRequestError, AuthenticationError

logger = get_logger(__name__)

# 全局API Key管理器实例
_api_key_manager: Optional["APIKeyManager"] = None


class APIKeyManager:
    """API Key管理器"""

    def __init__(self):
        """初始化API Key管理器"""
        self.logger = get_logger(__name__)
        self.storage = get_key_storage()

    def _generate_key_id(self) -> str:
        """
        生成唯一的API Key ID

        Returns:
          str: API Key ID（格式：ak_xxxxxxxx）
        """
        random_bytes = secrets.token_bytes(16)
        key_id = "ak_" + random_bytes.hex()
        return key_id

    def _generate_api_key(self) -> str:
        """
        生成API Key值

        Returns:
          str: API Key值（格式：sk-or-v1-xxxxxxxx）
        """
        random_bytes = secrets.token_bytes(32)
        api_key = "sk-or-v1-" + random_bytes.hex()
        return api_key

    def _hash_key(self, api_key: str) -> str:
        """
        对API Key进行哈希

        Args:
          api_key: API Key值

        Returns:
          str: 哈希值
        """
        return hashlib.sha256(api_key.encode()).hexdigest()

    def create_key(
        self,
        organization_id: str,
        name: str,
        description: Optional[str] = None,
        permissions: Optional[List[str]] = None,
        expires_at: Optional[datetime] = None,
    ) -> tuple[APIKey, str]:
        """
        创建API Key

        Args:
          organization_id: 组织ID
          name: API Key名称
          description: 描述
          permissions: 权限列表
          expires_at: 过期时间

        Returns:
          tuple: (APIKey对象, API Key值)
        """
        try:
            # 生成API Key
            key_id = self._generate_key_id()
            api_key_value = self._generate_api_key()

            # 设置默认权限
            if permissions is None:
                permissions = [Permission.READ, Permission.WRITE]

            # 创建API Key对象（直接存储原始key）
            api_key = APIKey(
                id=key_id,
                organization_id=organization_id,
                name=name,
                description=description,
                key=api_key_value,  # 直接存储原始key
                permissions=permissions,
                status="active",
                expires_at=expires_at,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )

            # 保存到数据库
            if self.storage.save(api_key):
                self.logger.info(f"API Key created: {key_id}")
                return api_key, api_key_value
            else:
                raise InvalidRequestError("Failed to create API Key")

        except Exception as e:
            self.logger.exception("Failed to create API Key", exc_info=e)
            raise

    def get_key(self, key_id: str) -> Optional[APIKey]:
        """
        获取API Key

        Args:
          key_id: API Key ID

        Returns:
          Optional[APIKey]: API Key对象
        """
        return self.storage.get(key_id)

    def list_keys(
        self,
        organization_id: Optional[str] = None,
        page: int = 1,
        limit: int = 20,
        status: Optional[str] = None,
        search: Optional[str] = None,
    ) -> tuple[List[APIKey], int]:
        """
        查询API Key列表

        Args:
          organization_id: 组织ID（可选）
          page: 页码
          limit: 每页数量
          status: 状态筛选
          search: 搜索关键词

        Returns:
          tuple: (API Key列表, 总数)
        """
        filters = {}
        if organization_id:
            filters["organization_id"] = organization_id
        if status:
            filters["status"] = status
        if search:
            filters["search"] = search

        return self.storage.list(filters=filters, page=page, limit=limit)

    def update_key(
        self,
        key_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        permissions: Optional[List[str]] = None,
        status: Optional[str] = None,
        expires_at: Optional[datetime] = None,
    ) -> Optional[APIKey]:
        """
        更新API Key

        Args:
          key_id: API Key ID
          name: 名称
          description: 描述
          permissions: 权限列表
          status: 状态
          expires_at: 过期时间

        Returns:
          Optional[APIKey]: 更新后的API Key对象
        """
        try:
            updates = {}
            if name is not None:
                updates["name"] = name
            if description is not None:
                updates["description"] = description
            if permissions is not None:
                updates["permissions"] = permissions
            if status is not None:
                updates["status"] = status
            if expires_at is not None:
                updates["expires_at"] = expires_at

            if updates:
                updates["updated_at"] = datetime.utcnow()
                if self.storage.update(key_id, updates):
                    return self.get_key(key_id)

            return None
        except Exception as e:
            self.logger.exception("Failed to update API Key", exc_info=e)
            raise

    def delete_key(self, key_id: str) -> bool:
        """
        删除API Key（软删除）

        Args:
          key_id: API Key ID

        Returns:
          bool: 是否成功删除
        """
        return self.storage.delete(key_id)

    def verify_key(self, api_key: str) -> APIKey:
        """
        验证API Key有效性

        Args:
          api_key: API Key值

        Returns:
          APIKey: API Key对象

        Raises:
          AuthenticationError: 如果API Key无效
        """
        try:
            # 直接查询数据库（使用原始key）
            db_key = self.storage.get_by_key(api_key)

            if not db_key:
                raise AuthenticationError("Invalid API Key")

            # 检查状态
            if db_key.status != "active":
                raise AuthenticationError(f"API Key is {db_key.status}")

            # 检查过期时间
            if db_key.expires_at and db_key.expires_at < datetime.utcnow():
                # 更新状态为过期
                self.update_key(db_key.id, status="expired")
                raise AuthenticationError("API Key has expired")

            # 更新最后使用时间
            self.storage.update_last_used(db_key.id)

            return db_key

        except AuthenticationError:
            raise
        except Exception as e:
            self.logger.exception("Failed to verify API Key", exc_info=e)
            raise AuthenticationError("Failed to verify API Key")


def get_api_key_manager() -> APIKeyManager:
    """
    获取API Key管理器实例（单例模式）

    Returns:
      APIKeyManager: API Key管理器实例
    """
    global _api_key_manager
    if _api_key_manager is None:
        _api_key_manager = APIKeyManager()
    return _api_key_manager
