"""
组织管理器

提供组织的完整生命周期管理
"""

import secrets
from datetime import datetime
from typing import List, Optional

from ..database.models import Organization
from ..utils.errors import InvalidRequestError
from ..utils.logger import get_logger
from .storage import OrganizationStorage, get_organization_storage

logger = get_logger(__name__)

# 全局组织管理器实例
_org_manager: Optional["OrganizationManager"] = None


class OrganizationManager:
    """组织管理器"""

    def __init__(self):
        """初始化组织管理器"""
        self.logger = get_logger(__name__)
        self.storage = get_organization_storage()

    def _generate_org_id(self) -> str:
        """
        生成唯一的组织ID

        Returns:
          str: 组织ID（格式：org_xxxxxxxx）
        """
        random_bytes = secrets.token_bytes(16)
        org_id = "org_" + random_bytes.hex()
        return org_id

    def create_organization(
        self,
        name: str,
        description: Optional[str] = None,
        admin_user_id: Optional[str] = None,
        monthly_requests_limit: Optional[int] = None,
        monthly_tokens_limit: Optional[int] = None,
        monthly_cost_limit: Optional[float] = None,
    ) -> Organization:
        """
        创建组织

        Args:
          name: 组织名称
          description: 描述
          admin_user_id: 管理员用户ID
          monthly_requests_limit: 月度请求次数限制
          monthly_tokens_limit: 月度Token限制
          monthly_cost_limit: 月度费用限制

        Returns:
          Organization: 组织对象
        """
        try:
            # 生成组织ID
            org_id = self._generate_org_id()

            # 创建组织对象
            org = Organization(
                id=org_id,
                name=name,
                description=description,
                admin_user_id=admin_user_id,
                status="active",
                monthly_requests_limit=monthly_requests_limit,
                monthly_tokens_limit=monthly_tokens_limit,
                monthly_cost_limit=monthly_cost_limit,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )

            # 保存到数据库
            if self.storage.save(org):
                self.logger.info(f"Organization created: {org_id}")
                return org
            else:
                raise InvalidRequestError("Failed to create organization")

        except Exception as e:
            self.logger.exception("Failed to create organization", exc_info=e)
            raise

    def get_organization(self, org_id: str) -> Optional[Organization]:
        """
        获取组织

        Args:
          org_id: 组织ID

        Returns:
          Optional[Organization]: 组织对象
        """
        return self.storage.get(org_id)

    def list_organizations(
        self,
        page: int = 1,
        limit: int = 20,
        status: Optional[str] = None,
        search: Optional[str] = None,
    ) -> tuple[List[Organization], int]:
        """
        查询组织列表

        Args:
          page: 页码
          limit: 每页数量
          status: 状态筛选
          search: 搜索关键词

        Returns:
          tuple: (组织列表, 总数)
        """
        filters = {}
        if status:
            filters["status"] = status
        if search:
            filters["search"] = search

        return self.storage.list(filters=filters, page=page, limit=limit)

    def update_organization(
        self,
        org_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        admin_user_id: Optional[str] = None,
        status: Optional[str] = None,
        monthly_requests_limit: Optional[int] = None,
        monthly_tokens_limit: Optional[int] = None,
        monthly_cost_limit: Optional[float] = None,
    ) -> Optional[Organization]:
        """
        更新组织

        Args:
          org_id: 组织ID
          name: 名称
          description: 描述
          admin_user_id: 管理员用户ID
          status: 状态
          monthly_requests_limit: 月度请求次数限制
          monthly_tokens_limit: 月度Token限制
          monthly_cost_limit: 月度费用限制

        Returns:
          Optional[Organization]: 更新后的组织对象
        """
        try:
            updates = {}
            if name is not None:
                updates["name"] = name
            if description is not None:
                updates["description"] = description
            if admin_user_id is not None:
                updates["admin_user_id"] = admin_user_id
            if status is not None:
                updates["status"] = status
            if monthly_requests_limit is not None:
                updates["monthly_requests_limit"] = monthly_requests_limit
            if monthly_tokens_limit is not None:
                updates["monthly_tokens_limit"] = monthly_tokens_limit
            if monthly_cost_limit is not None:
                updates["monthly_cost_limit"] = monthly_cost_limit

            if updates:
                updates["updated_at"] = datetime.utcnow()
                if self.storage.update(org_id, updates):
                    return self.get_organization(org_id)

            return None
        except Exception as e:
            self.logger.exception("Failed to update organization", exc_info=e)
            raise

    def delete_organization(self, org_id: str) -> bool:
        """
        删除组织（软删除）

        Args:
          org_id: 组织ID

        Returns:
          bool: 是否成功删除
        """
        return self.storage.delete(org_id)


def get_organization_manager() -> OrganizationManager:
    """
    获取组织管理器实例（单例模式）

    Returns:
      OrganizationManager: 组织管理器实例
    """
    global _org_manager
    if _org_manager is None:
        _org_manager = OrganizationManager()
    return _org_manager
