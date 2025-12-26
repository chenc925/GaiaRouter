"""
模型管理控制器（管理后台）
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from pydantic import BaseModel

from ...database.models import User
from ...models.manager import get_model_manager
from ...models.sync import sync_models_from_openrouter
from ...utils.logger import get_logger
from ..middleware.user_auth import verify_user_token

logger = get_logger(__name__)

router = APIRouter(prefix="/v1", tags=["admin-models"])


# Request/Response 模型
class ModelResponse(BaseModel):
    """模型响应"""

    id: str
    name: str
    description: Optional[str] = None
    provider: Optional[str] = None
    context_length: Optional[int] = None
    max_completion_tokens: Optional[int] = None
    pricing_prompt: Optional[float] = None
    pricing_completion: Optional[float] = None
    supports_vision: bool = False
    supports_function_calling: bool = False
    supports_streaming: bool = True
    is_enabled: bool = False
    is_free: bool = False
    synced_at: Optional[str] = None

    class Config:
        from_attributes = True


class ModelListResponse(BaseModel):
    """模型列表响应"""

    data: List[ModelResponse]
    pagination: dict


class SyncResponse(BaseModel):
    """同步响应"""

    success: bool
    stats: dict
    message: str


class BatchUpdateRequest(BaseModel):
    """批量更新请求"""

    model_ids: List[str]
    is_enabled: bool


@router.post("/admin/models/sync", response_model=SyncResponse)
async def sync_models(user: User = Depends(verify_user_token)):
    """
    同步 OpenRouter 模型到数据库

    需要 admin 权限
    """
    try:
        # 检查权限
        if user.role != "admin":
            raise HTTPException(status_code=403, detail="Insufficient permissions")

        # 执行同步
        stats = await sync_models_from_openrouter()

        return SyncResponse(
            success=True,
            stats=stats,
            message=f"同步完成: 总计 {stats['total']} 个模型, "
            f"新增 {stats['created']} 个, 更新 {stats['updated']} 个, "
            f"失败 {stats['failed']} 个",
        )

    except Exception as e:
        logger.exception("Failed to sync models", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"同步失败: {str(e)}"
        )


@router.get("/admin/models", response_model=ModelListResponse)
async def list_models(
    page: int = Query(1, ge=1, description="页码"),
    limit: int = Query(100, ge=1, le=1000, description="每页数量"),
    enabled_only: bool = Query(False, description="仅显示启用的模型"),
    provider: Optional[str] = Query(None, description="提供商筛选"),
    is_free: Optional[bool] = Query(None, description="免费模型筛选"),
    user: User = Depends(verify_user_token),
):
    """
    获取模型列表（管理后台）

    需要登录
    """
    try:
        manager = get_model_manager()
        models, total = manager.list_models(
            enabled_only=enabled_only,
            provider=provider,
            is_free=is_free,
            page=page,
            limit=limit,
        )

        # 转换为响应格式
        data = []
        for model in models:
            model_dict = {
                "id": model.id,
                "name": model.name,
                "description": model.description,
                "provider": model.provider,
                "context_length": model.context_length,
                "max_completion_tokens": model.max_completion_tokens,
                "pricing_prompt": float(model.pricing_prompt) if model.pricing_prompt else None,
                "pricing_completion": (
                    float(model.pricing_completion) if model.pricing_completion else None
                ),
                "supports_vision": model.supports_vision,
                "supports_function_calling": model.supports_function_calling,
                "supports_streaming": model.supports_streaming,
                "is_enabled": model.is_enabled,
                "is_free": model.is_free,
                "synced_at": model.synced_at.isoformat() if model.synced_at else None,
            }
            data.append(ModelResponse(**model_dict))

        pages = (total + limit - 1) // limit

        return ModelListResponse(
            data=data, pagination={"page": page, "limit": limit, "total": total, "pages": pages}
        )

    except Exception as e:
        logger.exception("Failed to list models", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="获取模型列表失败"
        )


@router.patch("/admin/models/{model_id:path}/enable")
async def enable_model(
    model_id: str = Path(..., description="模型ID"), user: User = Depends(verify_user_token)
):
    """
    启用模型

    需要 admin 权限
    """
    try:
        if user.role != "admin":
            raise HTTPException(status_code=403, detail="Insufficient permissions")

        manager = get_model_manager()
        if not manager.enable_model(model_id):
            raise HTTPException(status_code=404, detail="Model not found")

        return {"success": True, "message": "模型已启用"}

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Failed to enable model {model_id}", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="启用模型失败"
        )


@router.patch("/admin/models/{model_id:path}/disable")
async def disable_model(
    model_id: str = Path(..., description="模型ID"), user: User = Depends(verify_user_token)
):
    """
    禁用模型

    需要 admin 权限
    """
    try:
        if user.role != "admin":
            raise HTTPException(status_code=403, detail="Insufficient permissions")

        manager = get_model_manager()
        if not manager.disable_model(model_id):
            raise HTTPException(status_code=404, detail="Model not found")

        return {"success": True, "message": "模型已禁用"}

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Failed to disable model {model_id}", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="禁用模型失败"
        )


@router.post("/admin/models/batch-update")
async def batch_update_models(request: BatchUpdateRequest, user: User = Depends(verify_user_token)):
    """
    批量更新模型启用状态

    需要 admin 权限
    """
    try:
        if user.role != "admin":
            raise HTTPException(status_code=403, detail="Insufficient permissions")

        manager = get_model_manager()
        count = manager.batch_update_enabled(request.model_ids, request.is_enabled)

        action = "启用" if request.is_enabled else "禁用"
        return {"success": True, "count": count, "message": f"已{action} {count} 个模型"}

    except Exception as e:
        logger.exception("Failed to batch update models", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="批量更新失败"
        )
