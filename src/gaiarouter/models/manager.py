"""
模型管理器

管理模型的增删改查和启用/禁用
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from ..database.models import Model
from ..database.connection import get_db
from ..utils.logger import get_logger

logger = get_logger(__name__)

# 全局管理器实例
_manager: Optional["ModelManager"] = None


class ModelManager:
    """模型管理器"""

    def __init__(self):
        self.logger = get_logger(__name__)

    def list_models(
        self,
        enabled_only: bool = False,
        provider: Optional[str] = None,
        is_free: Optional[bool] = None,
        page: int = 1,
        limit: int = 100,
    ) -> tuple[List[Model], int]:
        """
        查询模型列表

        Args:
            enabled_only: 仅返回启用的模型
            provider: 按提供商筛选
            is_free: 按免费/付费筛选
            page: 页码
            limit: 每页数量

        Returns:
            (模型列表, 总数)
        """
        db = next(get_db())
        try:
            query = db.query(Model)

            if enabled_only:
                query = query.filter(Model.is_enabled == True)

            if provider:
                query = query.filter(Model.provider == provider)

            if is_free is not None:
                query = query.filter(Model.is_free == is_free)

            total = query.count()

            offset = (page - 1) * limit
            models = query.order_by(Model.name).offset(offset).limit(limit).all()

            return models, total

        finally:
            db.close()

    def get_model(self, model_id: str) -> Optional[Model]:
        """
        获取单个模型

        Args:
            model_id: 模型ID

        Returns:
            模型对象
        """
        db = next(get_db())
        try:
            return db.query(Model).filter(Model.id == model_id).first()
        finally:
            db.close()

    def update_model(self, model_id: str, updates: Dict[str, Any]) -> Optional[Model]:
        """
        更新模型

        Args:
            model_id: 模型ID
            updates: 更新字段

        Returns:
            更新后的模型对象
        """
        db = next(get_db())
        try:
            model = db.query(Model).filter(Model.id == model_id).first()
            if not model:
                return None

            for key, value in updates.items():
                if hasattr(model, key):
                    setattr(model, key, value)

            model.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(model)

            self.logger.info(f"Updated model {model_id}: {updates}")
            return model

        except Exception as e:
            db.rollback()
            self.logger.error(f"Failed to update model {model_id}: {e}")
            raise
        finally:
            db.close()

    def enable_model(self, model_id: str) -> bool:
        """
        启用模型

        Args:
            model_id: 模型ID

        Returns:
            是否成功
        """
        result = self.update_model(model_id, {"is_enabled": True})
        return result is not None

    def disable_model(self, model_id: str) -> bool:
        """
        禁用模型

        Args:
            model_id: 模型ID

        Returns:
            是否成功
        """
        result = self.update_model(model_id, {"is_enabled": False})
        return result is not None

    def batch_update_enabled(self, model_ids: List[str], enabled: bool) -> int:
        """
        批量更新模型启用状态

        Args:
            model_ids: 模型ID列表
            enabled: 启用状态

        Returns:
            更新的数量
        """
        count = 0
        for model_id in model_ids:
            if self.update_model(model_id, {"is_enabled": enabled}):
                count += 1
        return count


def get_model_manager() -> ModelManager:
    """获取模型管理器实例（单例）"""
    global _manager
    if _manager is None:
        _manager = ModelManager()
    return _manager
