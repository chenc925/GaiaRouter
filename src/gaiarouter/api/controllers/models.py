"""
模型列表控制器

处理模型列表查询请求
"""

import time

from fastapi import APIRouter, Depends

from ...models.manager import get_model_manager
from ...utils.logger import get_logger
from ..middleware.auth import verify_api_key
from ..schemas.response import ModelInfo, ModelsResponse

logger = get_logger(__name__)

router = APIRouter(prefix="/v1", tags=["models"])


@router.get("/models")
async def list_models(api_key=Depends(verify_api_key)) -> ModelsResponse:
    """
    获取可用模型列表（仅返回启用的模型）

    Args:
      api_key: API Key（通过中间件验证）

    Returns:
      模型列表响应
    """
    # 从数据库获取启用的模型
    manager = get_model_manager()
    models, _ = manager.list_models(enabled_only=True, limit=1000)

    model_list = []
    current_time = int(time.time())

    for model in models:
        model_list.append(
            ModelInfo(
                id=model.id,
                object="model",
                created=current_time,
                owned_by=model.provider or "openrouter",
                provider=model.provider or "openrouter",
            )
        )

    logger.info(f"Listed {len(model_list)} enabled models")

    return ModelsResponse(data=model_list)
