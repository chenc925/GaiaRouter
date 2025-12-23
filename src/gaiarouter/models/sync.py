"""
模型同步服务

从 OpenRouter API 同步模型列表到数据库
"""

import httpx
from datetime import datetime
from typing import List, Dict, Any, Optional
from ..database.models import Model
from ..database.connection import get_db
from ..config import get_settings
from ..utils.logger import get_logger

logger = get_logger(__name__)

# 全局同步器实例
_syncer: Optional["ModelSyncer"] = None


class ModelSyncer:
    """模型同步器"""

    def __init__(self):
        self.settings = get_settings()
        self.logger = get_logger(__name__)
        self.openrouter_api_key = self.settings.providers.openrouter_api_key

    async def fetch_openrouter_models(self) -> List[Dict[str, Any]]:
        """
        从 OpenRouter 获取模型列表

        Returns:
            模型列表
        """
        url = "https://openrouter.ai/api/v1/models"
        headers = {}

        if self.openrouter_api_key:
            headers["Authorization"] = f"Bearer {self.openrouter_api_key}"

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                data = response.json()
                return data.get("data", [])
        except Exception as e:
            self.logger.error(f"Failed to fetch OpenRouter models: {e}")
            raise

    def sync_model_to_db(self, model_data: Dict[str, Any]) -> Model:
        """
        将单个模型同步到数据库

        Args:
            model_data: OpenRouter 模型数据

        Returns:
            Model 对象
        """
        db = next(get_db())
        try:
            # 从 OpenRouter 获取的原始 ID
            original_model_id = model_data.get("id")
            # 添加 openrouter/ 前缀
            model_id = f"openrouter/{original_model_id}"

            # 检查模型是否已存在
            existing_model = db.query(Model).filter(Model.id == model_id).first()

            # 提取定价信息
            pricing = model_data.get("pricing", {})

            # 判断是否免费（定价为0或没有定价）
            is_free = (
                pricing.get("prompt") == "0"
                or pricing.get("completion") == "0"
                or ":free" in original_model_id.lower()
            )

            model_dict = {
                "name": model_data.get("name", original_model_id),
                "description": model_data.get("description"),
                "provider": "openrouter",
                "context_length": model_data.get("context_length"),
                "max_completion_tokens": model_data.get("top_provider", {}).get(
                    "max_completion_tokens"
                ),
                "pricing_prompt": (
                    float(pricing.get("prompt", 0)) if pricing.get("prompt") else None
                ),
                "pricing_completion": (
                    float(pricing.get("completion", 0)) if pricing.get("completion") else None
                ),
                "supports_vision": "vision"
                in model_data.get("architecture", {}).get("modality", "").lower(),
                "supports_function_calling": model_data.get("architecture", {}).get("tokenizer")
                == "GPT",
                "supports_streaming": True,  # OpenRouter 大部分模型支持流式
                "is_free": is_free,
                "openrouter_id": original_model_id,  # 保留原始 ID
                "synced_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }

            if existing_model:
                # 更新现有模型（保留 is_enabled 状态）
                for key, value in model_dict.items():
                    if key != "is_enabled":  # 不自动修改启用状态
                        setattr(existing_model, key, value)
                db.commit()
                db.refresh(existing_model)
                self.logger.info(f"Updated model: {model_id}")
                return existing_model
            else:
                # 创建新模型（默认禁用）
                model_dict["id"] = model_id  # 使用带前缀的 ID
                model_dict["is_enabled"] = False  # 新模型默认禁用
                model_dict["created_at"] = datetime.utcnow()

                new_model = Model(**model_dict)
                db.add(new_model)
                db.commit()
                db.refresh(new_model)
                self.logger.info(f"Created model: {model_id}")
                return new_model

        except Exception as e:
            db.rollback()
            self.logger.error(f"Failed to sync model {model_data.get('id')}: {e}")
            raise
        finally:
            db.close()

    async def sync_all_models(self) -> Dict[str, int]:
        """
        同步所有 OpenRouter 模型

        Returns:
            同步统计信息 {"total": 总数, "created": 新建数, "updated": 更新数, "failed": 失败数}
        """
        try:
            self.logger.info("Starting to sync OpenRouter models...")

            # 获取 OpenRouter 模型列表
            models_data = await self.fetch_openrouter_models()

            stats = {
                "total": len(models_data),
                "created": 0,
                "updated": 0,
                "failed": 0,
            }

            # 同步每个模型
            for model_data in models_data:
                try:
                    db = next(get_db())
                    original_model_id = model_data.get("id")
                    # 使用带前缀的 ID 检查
                    model_id = f"openrouter/{original_model_id}"
                    existing = db.query(Model).filter(Model.id == model_id).first()
                    db.close()

                    self.sync_model_to_db(model_data)

                    if existing:
                        stats["updated"] += 1
                    else:
                        stats["created"] += 1

                except Exception as e:
                    stats["failed"] += 1
                    self.logger.error(f"Failed to sync model: {model_data.get('id')}, error: {e}")

            self.logger.info(f"Sync completed: {stats}")
            return stats

        except Exception as e:
            self.logger.exception("Failed to sync models", exc_info=e)
            raise


def get_model_syncer() -> ModelSyncer:
    """获取模型同步器实例（单例）"""
    global _syncer
    if _syncer is None:
        _syncer = ModelSyncer()
    return _syncer


async def sync_models_from_openrouter() -> Dict[str, int]:
    """
    同步 OpenRouter 模型（快捷函数）

    Returns:
        同步统计信息
    """
    syncer = get_model_syncer()
    return await syncer.sync_all_models()
