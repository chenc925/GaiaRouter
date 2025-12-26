"""
API Key管理控制器

处理API Key的CRUD操作
"""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from ...auth.api_key_manager import get_api_key_manager
from ...database.models import User
from ...utils.errors import AuthenticationError, InvalidRequestError
from ...utils.logger import get_logger
from ..middleware.user_auth import verify_user_token
from ..schemas.api_key import (
    APIKeyListResponse,
    APIKeyResponse,
    CreateAPIKeyRequest,
    UpdateAPIKeyRequest,
)

logger = get_logger(__name__)

router = APIRouter(prefix="/v1", tags=["api-keys"])


def _api_key_to_response(
    api_key, include_key: bool = True, organization_name: str = None
) -> APIKeyResponse:
    """将API Key对象转换为响应模型"""
    return APIKeyResponse(
        id=api_key.id,
        organization_id=api_key.organization_id,
        organization_name=organization_name,
        name=api_key.name,
        description=api_key.description,
        key=api_key.key if include_key and hasattr(api_key, "key") else None,
        permissions=api_key.permissions or [],
        status=api_key.status,
        created_at=api_key.created_at.isoformat() + "Z" if api_key.created_at else None,
        expires_at=api_key.expires_at.isoformat() + "Z" if api_key.expires_at else None,
        last_used_at=api_key.last_used_at.isoformat() + "Z" if api_key.last_used_at else None,
        updated_at=api_key.updated_at.isoformat() + "Z" if api_key.updated_at else None,
    )


@router.post("/api-keys", response_model=APIKeyResponse, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    request: CreateAPIKeyRequest, user: User = Depends(verify_user_token)
) -> APIKeyResponse:
    """
    创建API Key

    Args:
      request: 创建API Key请求
      user: 当前用户（通过中间件验证）

    Returns:
      APIKeyResponse: API Key响应（包含key字段）
    """
    try:
        # 检查权限（只有admin用户可以创建API Key）
        if user.role != "admin":
            raise AuthenticationError("Insufficient permissions")

        # 验证组织是否存在
        from ...organizations.manager import get_organization_manager

        org_manager = get_organization_manager()
        org = org_manager.get_organization(request.organization_id)
        if not org:
            raise InvalidRequestError(f"Organization not found: {request.organization_id}")

        # 检查该组织是否已经有活跃的API Key（一个组织只能有一个活跃的API Key）
        api_key_manager = get_api_key_manager()
        existing_keys, total = api_key_manager.list_keys(
            organization_id=request.organization_id, page=1, limit=1, status="active"
        )

        if total > 0:
            raise InvalidRequestError(
                f"Organization already has an API Key. Each organization can only have one API Key."
            )

        # 自动生成API Key名称和描述
        key_name = f"{org.name} API Key"
        key_description = f"Auto-generated API Key for {org.name}"

        # 设置默认权限：读取和写入
        permissions = ["read", "write"]

        # 创建API Key（不设置过期时间）
        new_key, key_value = api_key_manager.create_key(
            organization_id=request.organization_id,
            name=key_name,
            description=key_description,
            permissions=permissions,
            expires_at=None,
        )

        # 创建响应（包含key值）- 直接构建响应对象而不是修改
        response = APIKeyResponse(
            id=new_key.id,
            organization_id=new_key.organization_id,
            organization_name=org.name,
            name=new_key.name,
            description=new_key.description,
            key=key_value,  # 仅在创建时返回明文key
            permissions=new_key.permissions or [],
            status=new_key.status,
            created_at=new_key.created_at.isoformat() + "Z" if new_key.created_at else None,
            expires_at=new_key.expires_at.isoformat() + "Z" if new_key.expires_at else None,
            last_used_at=new_key.last_used_at.isoformat() + "Z" if new_key.last_used_at else None,
            updated_at=new_key.updated_at.isoformat() + "Z" if new_key.updated_at else None,
        )

        logger.info(f"API Key created: {new_key.id}, key_value: {key_value[:20]}...")
        logger.info(f"Response key field: {response.key[:20] if response.key else 'None'}...")

        return response

    except (InvalidRequestError, AuthenticationError):
        raise
    except Exception as e:
        logger.exception("Failed to create API Key", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create API Key"
        )


@router.get("/api-keys", response_model=APIKeyListResponse)
async def list_api_keys(
    page: int = Query(1, ge=1, description="页码"),
    limit: int = Query(20, ge=1, le=1000, description="每页数量"),
    status: Optional[str] = Query(None, description="状态筛选"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    organization_id: Optional[str] = Query(None, description="组织ID筛选"),
    user: User = Depends(verify_user_token),
) -> APIKeyListResponse:
    """
    查询API Key列表

    Args:
      page: 页码
      limit: 每页数量
      status: 状态筛选
      search: 搜索关键词
      organization_id: 组织ID筛选（可选）
      user: 当前用户（通过中间件验证）

    Returns:
      APIKeyListResponse: API Key列表响应
    """
    try:
        # 查询API Key列表（登录用户都可以查看）
        api_key_manager = get_api_key_manager()
        # 如果指定了组织ID，只查询该组织的；否则查询所有（admin用户）或根据用户权限查询
        keys, total = api_key_manager.list_keys(
            organization_id=organization_id, page=page, limit=limit, status=status, search=search
        )

        # 获取组织管理器，用于查询组织名称
        from ...organizations.manager import get_organization_manager

        org_manager = get_organization_manager()

        # 构建组织ID到名称的映射
        org_ids = list(set(k.organization_id for k in keys))
        org_map = {}
        for org_id in org_ids:
            org = org_manager.get_organization(org_id)
            if org:
                org_map[org_id] = org.name

        # 转换为响应模型
        data = [
            _api_key_to_response(k, organization_name=org_map.get(k.organization_id)) for k in keys
        ]

        # 计算总页数
        pages = (total + limit - 1) // limit

        return APIKeyListResponse(
            data=data, pagination={"page": page, "limit": limit, "total": total, "pages": pages}
        )

    except AuthenticationError:
        raise
    except Exception as e:
        logger.exception("Failed to list API Keys", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to list API Keys"
        )


@router.get("/api-keys/{key_id}", response_model=APIKeyResponse)
async def get_api_key(key_id: str, user: User = Depends(verify_user_token)) -> APIKeyResponse:
    """
    查询单个API Key

    Args:
      key_id: API Key ID
      user: 当前用户（通过中间件验证）

    Returns:
      APIKeyResponse: API Key响应
    """
    try:
        # 查询API Key
        api_key_manager = get_api_key_manager()
        key = api_key_manager.get_key(key_id)

        if not key:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="API Key not found")

        # 非admin用户只能查看自己组织的API Key（如果需要的话，可以进一步限制）
        # 这里简化处理，登录用户都可以查看

        return _api_key_to_response(key)

    except (AuthenticationError, HTTPException):
        raise
    except Exception as e:
        logger.exception("Failed to get API Key", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get API Key"
        )


@router.patch("/api-keys/{key_id}", response_model=APIKeyResponse)
async def update_api_key(
    key_id: str, request: UpdateAPIKeyRequest, user: User = Depends(verify_user_token)
) -> APIKeyResponse:
    """
    更新API Key

    Args:
      key_id: API Key ID
      request: 更新API Key请求
      user: 当前用户（通过中间件验证）

    Returns:
      APIKeyResponse: 更新后的API Key响应
    """
    try:
        # 检查权限（只有admin用户可以更新API Key）
        if user.role != "admin":
            raise AuthenticationError("Insufficient permissions")

        # 查询API Key
        api_key_manager = get_api_key_manager()
        key = api_key_manager.get_key(key_id)

        if not key:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="API Key not found")

        # 解析过期时间
        expires_at = None
        if request.expires_at:
            try:
                expires_at = datetime.fromisoformat(request.expires_at.replace("Z", "+00:00"))
            except ValueError:
                raise InvalidRequestError(f"Invalid expires_at format: {request.expires_at}")

        # 更新API Key
        updated_key = api_key_manager.update_key(
            key_id=key_id,
            name=request.name,
            description=request.description,
            permissions=request.permissions,
            status=request.status,
            expires_at=expires_at,
        )

        if not updated_key:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update API Key"
            )

        logger.info(f"API Key updated: {key_id}")
        return _api_key_to_response(updated_key)

    except (InvalidRequestError, AuthenticationError, HTTPException):
        raise
    except Exception as e:
        logger.exception("Failed to update API Key", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update API Key"
        )


@router.delete("/api-keys/{key_id}", status_code=status.HTTP_200_OK)
async def delete_api_key(key_id: str, user: User = Depends(verify_user_token)) -> dict:
    """
    删除API Key

    Args:
      key_id: API Key ID
      user: 当前用户（通过中间件验证）

    Returns:
      dict: 删除成功消息
    """
    try:
        # 检查权限（只有admin用户可以删除API Key）
        if user.role != "admin":
            raise AuthenticationError("Insufficient permissions")

        # 查询API Key
        api_key_manager = get_api_key_manager()
        key = api_key_manager.get_key(key_id)

        if not key:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="API Key not found")

        # 删除API Key
        success = api_key_manager.delete_key(key_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete API Key"
            )

        logger.info(f"API Key deleted: {key_id}")
        return {"message": "API Key deleted successfully"}

    except (AuthenticationError, HTTPException):
        raise
    except Exception as e:
        logger.exception("Failed to delete API Key", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete API Key"
        )
