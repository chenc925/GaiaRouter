"""
API Key存储模块

负责API Key的数据库存储和查询
"""

from typing import List, Optional, Dict
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from ..database.models import APIKey
from ..database.connection import get_db
from ..utils.logger import get_logger

logger = get_logger(__name__)

# 全局Key存储实例
_key_storage: Optional["KeyStorage"] = None


class KeyStorage:
    """API Key存储"""

    def __init__(self):
        """初始化Key存储"""
        self.logger = get_logger(__name__)

    def save(self, key: APIKey) -> bool:
        """
        保存API Key到数据库

        Args:
          key: API Key对象

        Returns:
          bool: 是否成功保存
        """
        try:
            db = next(get_db())
            try:
                db.add(key)
                db.commit()
                db.refresh(key)
                return True
            except Exception as e:
                db.rollback()
                self.logger.error(f"Failed to save API Key: {e}", exc_info=e)
                raise
            finally:
                db.close()
        except Exception as e:
            self.logger.exception("Failed to save API Key", exc_info=e)
            return False

    def get(self, key_id: str) -> Optional[APIKey]:
        """
        从数据库获取API Key

        Args:
          key_id: API Key ID

        Returns:
          Optional[APIKey]: API Key对象，如果不存在返回None
        """
        try:
            db = next(get_db())
            try:
                key = db.query(APIKey).filter(APIKey.id == key_id).first()
                return key
            finally:
                db.close()
        except Exception as e:
            self.logger.exception("Failed to get API Key", exc_info=e)
            return None

    def get_by_key(self, key_value: str) -> Optional[APIKey]:
        """
        通过API Key原始值查询

        Args:
          key_value: API Key原始值

        Returns:
          Optional[APIKey]: API Key对象，如果不存在返回None
        """
        try:
            db = next(get_db())
            try:
                key = db.query(APIKey).filter(APIKey.key == key_value).first()
                return key
            finally:
                db.close()
        except Exception as e:
            self.logger.exception("Failed to get API Key by value", exc_info=e)
            return None

    def get_by_key_hash(self, key_hash: str) -> Optional[APIKey]:
        """
        通过API Key哈希值查询

        Args:
          key_hash: API Key哈希值

        Returns:
          Optional[APIKey]: API Key对象，如果不存在返回None
        """
        try:
            db = next(get_db())
            try:
                key = db.query(APIKey).filter(APIKey.key_hash == key_hash).first()
                return key
            finally:
                db.close()
        except Exception as e:
            self.logger.exception("Failed to get API Key by hash", exc_info=e)
            return None

    def list(
        self, filters: Optional[Dict] = None, page: int = 1, limit: int = 20
    ) -> tuple[List[APIKey], int]:
        """
        查询API Key列表

        Args:
          filters: 过滤条件
          page: 页码
          limit: 每页数量

        Returns:
          tuple: (API Key列表, 总数)
        """
        try:
            db = next(get_db())
            try:
                query = db.query(APIKey)

                # 应用过滤条件
                if filters:
                    if "organization_id" in filters:
                        query = query.filter(APIKey.organization_id == filters["organization_id"])
                    if "status" in filters:
                        query = query.filter(APIKey.status == filters["status"])
                    if "search" in filters and filters["search"]:
                        search_term = f"%{filters['search']}%"
                        query = query.filter(
                            or_(APIKey.name.like(search_term), APIKey.description.like(search_term))
                        )

                # 获取总数
                total = query.count()

                # 分页
                offset = (page - 1) * limit
                keys = query.order_by(APIKey.created_at.desc()).offset(offset).limit(limit).all()

                return keys, total
            finally:
                db.close()
        except Exception as e:
            self.logger.exception("Failed to list API Keys", exc_info=e)
            return [], 0

    def update(self, key_id: str, updates: Dict) -> bool:
        """
        更新API Key

        Args:
          key_id: API Key ID
          updates: 更新字段字典

        Returns:
          bool: 是否成功更新
        """
        try:
            db = next(get_db())
            try:
                key = db.query(APIKey).filter(APIKey.id == key_id).first()
                if not key:
                    return False

                # 更新字段
                for field, value in updates.items():
                    if hasattr(key, field):
                        setattr(key, field, value)

                key.updated_at = datetime.utcnow()
                db.commit()
                db.refresh(key)
                return True
            except Exception as e:
                db.rollback()
                self.logger.error(f"Failed to update API Key: {e}", exc_info=e)
                raise
            finally:
                db.close()
        except Exception as e:
            self.logger.exception("Failed to update API Key", exc_info=e)
            return False

    def delete(self, key_id: str) -> bool:
        """
        删除API Key（软删除，将状态设置为inactive）

        注意：软删除后，组织可以重新创建新的API Key

        Args:
          key_id: API Key ID

        Returns:
          bool: 是否成功删除
        """
        try:
            db = next(get_db())
            try:
                key = db.query(APIKey).filter(APIKey.id == key_id).first()
                if not key:
                    return False

                # 软删除：更新状态为inactive
                key.status = "inactive"
                key.updated_at = datetime.utcnow()
                db.commit()
                return True
            except Exception as e:
                db.rollback()
                self.logger.error(f"Failed to delete API Key: {e}", exc_info=e)
                raise
            finally:
                db.close()
        except Exception as e:
            self.logger.exception("Failed to delete API Key", exc_info=e)
            return False

    def update_last_used(self, key_id: str) -> bool:
        """
        更新API Key最后使用时间

        Args:
          key_id: API Key ID

        Returns:
          bool: 是否成功更新
        """
        try:
            db = next(get_db())
            try:
                key = db.query(APIKey).filter(APIKey.id == key_id).first()
                if not key:
                    return False

                key.last_used_at = datetime.utcnow()
                db.commit()
                return True
            except Exception as e:
                db.rollback()
                self.logger.error(f"Failed to update last used: {e}", exc_info=e)
                return False
            finally:
                db.close()
        except Exception as e:
            self.logger.exception("Failed to update last used", exc_info=e)
            return False


def get_key_storage() -> KeyStorage:
    """
    获取Key存储实例（单例模式）

    Returns:
      KeyStorage: Key存储实例
    """
    global _key_storage
    if _key_storage is None:
        _key_storage = KeyStorage()
    return _key_storage
