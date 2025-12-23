"""
组织管理控制器

处理组织的CRUD操作
"""

from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, Query, HTTPException, status
from ..middleware.user_auth import verify_user_token
from ..schemas.organization import (
    CreateOrganizationRequest,
    UpdateOrganizationRequest,
    OrganizationResponse,
    OrganizationListResponse,
)
from ..schemas.api_key import CreateAPIKeyRequest, APIKeyResponse
from ...organizations.manager import get_organization_manager
from ...database.models import User
from ...utils.logger import get_logger
from ...utils.errors import InvalidRequestError, AuthenticationError

logger = get_logger(__name__)

router = APIRouter(prefix="/v1", tags=["organizations"])


def _organization_to_dict(org) -> dict:
    """将组织对象转换为字典"""
    return {
        "id": org.id,
        "name": org.name,
        "description": org.description,
        "admin_user_id": org.admin_user_id,
        "status": org.status,
        "monthly_requests_limit": org.monthly_requests_limit,
        "monthly_tokens_limit": org.monthly_tokens_limit,
        "monthly_cost_limit": float(org.monthly_cost_limit) if org.monthly_cost_limit else None,
        "created_at": org.created_at.isoformat() + "Z" if org.created_at else None,
        "updated_at": org.updated_at.isoformat() + "Z" if org.updated_at else None,
    }


@router.post(
    "/organizations", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED
)
async def create_organization(
    request: CreateOrganizationRequest, user: User = Depends(verify_user_token)
) -> OrganizationResponse:
    """
    创建组织

    Args:
      data: 创建组织请求数据
      user: 当前用户（通过中间件验证）

    Returns:
      dict: 组织响应
    """
    try:
        # 检查权限（只有admin用户可以创建组织）
        if user.role != "admin":
            raise AuthenticationError("Insufficient permissions")

        # 创建组织
        org_manager = get_organization_manager()
        org = org_manager.create_organization(
            name=request.name,
            description=request.description,
            admin_user_id=None,  # 创建组织时不需要管理员ID
            monthly_requests_limit=request.monthly_requests_limit,
            monthly_tokens_limit=request.monthly_tokens_limit,
            monthly_cost_limit=request.monthly_cost_limit,
        )

        logger.info(f"Organization created: {org.id}")
        return OrganizationResponse(**_organization_to_dict(org))

    except (InvalidRequestError, AuthenticationError):
        raise
    except Exception as e:
        logger.exception("Failed to create organization", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create organization",
        )


@router.get("/organizations", response_model=OrganizationListResponse)
async def list_organizations(
    page: int = Query(1, ge=1, description="页码"),
    limit: int = Query(20, ge=1, le=1000, description="每页数量"),
    status: Optional[str] = Query(None, description="状态筛选"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    user: User = Depends(verify_user_token),
) -> dict:
    """
    查询组织列表

    Args:
      page: 页码
      limit: 每页数量
      status: 状态筛选
      search: 搜索关键词
      user: 当前用户（通过中间件验证）

    Returns:
      OrganizationListResponse: 组织列表响应
    """
    try:
        # 查询组织列表（登录用户都可以查看）
        org_manager = get_organization_manager()
        orgs, total = org_manager.list_organizations(
            page=page, limit=limit, status=status, search=search
        )

        # 转换为响应格式
        data = [_organization_to_dict(org) for org in orgs]

        # 计算总页数
        pages = (total + limit - 1) // limit

        return OrganizationListResponse(
            data=[OrganizationResponse(**item) for item in data],
            pagination={"page": page, "limit": limit, "total": total, "pages": pages},
        )

    except AuthenticationError:
        raise
    except Exception as e:
        logger.exception("Failed to list organizations", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to list organizations"
        )


@router.get("/organizations/{org_id}", response_model=OrganizationResponse)
async def get_organization(
    org_id: str, user: User = Depends(verify_user_token)
) -> OrganizationResponse:
    """
    查询单个组织

    Args:
      org_id: 组织ID
      user: 当前用户（通过中间件验证）

    Returns:
      dict: 组织响应
    """
    try:
        # 查询组织（登录用户都可以查看）
        org_manager = get_organization_manager()
        org = org_manager.get_organization(org_id)

        if not org:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found"
            )

        return OrganizationResponse(**_organization_to_dict(org))

    except (AuthenticationError, HTTPException):
        raise
    except Exception as e:
        logger.exception("Failed to get organization", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get organization"
        )


@router.patch("/organizations/{org_id}", response_model=OrganizationResponse)
async def update_organization(
    org_id: str, request: UpdateOrganizationRequest, user: User = Depends(verify_user_token)
) -> OrganizationResponse:
    """
    更新组织

    Args:
      org_id: 组织ID
      data: 更新组织请求数据
      user: 当前用户（通过中间件验证）

    Returns:
      OrganizationResponse: 更新后的组织响应
    """
    try:
        # 检查权限（只有admin用户可以更新组织）
        if user.role != "admin":
            raise AuthenticationError("Insufficient permissions")

        # 查询组织
        org_manager = get_organization_manager()
        org = org_manager.get_organization(org_id)

        if not org:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found"
            )

        # 更新组织
        updated_org = org_manager.update_organization(
            org_id=org_id,
            name=request.name,
            description=request.description,
            admin_user_id=request.admin_user_id,
            status=request.status,
            monthly_requests_limit=request.monthly_requests_limit,
            monthly_tokens_limit=request.monthly_tokens_limit,
            monthly_cost_limit=request.monthly_cost_limit,
        )

        if not updated_org:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update organization",
            )

        logger.info(f"Organization updated: {org_id}")
        return OrganizationResponse(**_organization_to_dict(updated_org))

    except (InvalidRequestError, AuthenticationError, HTTPException):
        raise
    except Exception as e:
        logger.exception("Failed to update organization", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update organization",
        )


@router.delete("/organizations/{org_id}", status_code=status.HTTP_200_OK)
async def delete_organization(org_id: str, user: User = Depends(verify_user_token)) -> dict:
    """
    删除组织

    Args:
      org_id: 组织ID
      user: 当前用户（通过中间件验证）

    Returns:
      dict: 删除成功消息
    """
    try:
        # 检查权限（只有admin用户可以删除组织）
        if user.role != "admin":
            raise AuthenticationError("Insufficient permissions")

        # 查询组织
        org_manager = get_organization_manager()
        org = org_manager.get_organization(org_id)

        if not org:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found"
            )

        # 删除组织
        success = org_manager.delete_organization(org_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete organization",
            )

        logger.info(f"Organization deleted: {org_id}")
        return {"message": "Organization deleted successfully"}

    except (AuthenticationError, HTTPException):
        raise
    except Exception as e:
        logger.exception("Failed to delete organization", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete organization",
        )


@router.get("/organizations/{org_id}/stats")
async def get_organization_stats(
    org_id: str,
    start_date: Optional[str] = Query(None, description="开始日期（ISO 8601格式）"),
    end_date: Optional[str] = Query(None, description="结束日期（ISO 8601格式）"),
    group_by: str = Query("day", description="分组方式：day, week, month, model, provider"),
    user: User = Depends(verify_user_token),
) -> dict:
    """
    获取组织使用统计

    Args:
      org_id: 组织ID
      start_date: 开始日期（ISO 8601格式）
      end_date: 结束日期（ISO 8601格式）
      group_by: 分组方式
      user: 当前用户（通过中间件验证）

    Returns:
      dict: 统计响应
    """
    try:
        # 解析日期参数
        start_dt = None
        end_dt = None

        if start_date:
            try:
                start_dt = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
            except ValueError:
                raise InvalidRequestError(f"Invalid start_date format: {start_date}")

        if end_date:
            try:
                end_dt = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
            except ValueError:
                raise InvalidRequestError(f"Invalid end_date format: {end_date}")

        # 验证分组方式
        valid_group_by = ["day", "week", "month", "model", "provider"]
        if group_by not in valid_group_by:
            raise InvalidRequestError(
                f"Invalid group_by: {group_by}. Must be one of {valid_group_by}"
            )

        # 使用统计查询（通过组织ID查询该组织下所有API Key的统计）
        from ...stats.query import StatsQuery, StatsQueryParams, get_stats_query

        params = StatsQueryParams(start_date=start_dt, end_date=end_dt, group_by=group_by)

        # 查询该组织下所有API Key的统计
        from ...auth.key_storage import get_key_storage

        key_storage = get_key_storage()
        keys, _ = key_storage.list(filters={"organization_id": org_id}, page=1, limit=1000)

        # 聚合所有API Key的统计
        from ...stats.storage import get_stats_storage

        stats_storage = get_stats_storage()

        all_stats = []
        for key in keys:
            key_stats = stats_storage.get_key_stats(
                key_id=key.id, start_date=start_dt, end_date=end_dt, group_by=group_by
            )
            all_stats.extend(key_stats)

        # 获取摘要
        summary = stats_storage.get_summary(all_stats)

        # 构建响应
        response = {
            "organization_id": org_id,
            "period": {
                "start": (start_dt or datetime.utcnow()).isoformat() + "Z",
                "end": (end_dt or datetime.utcnow()).isoformat() + "Z",
            },
            "summary": summary,
        }

        # 根据分组方式聚合数据
        if params.group_by == "day":
            by_date = stats_storage.aggregate_by_date(all_stats)
            response["by_date"] = list(by_date.values())
        elif params.group_by == "model":
            by_model = stats_storage.aggregate_by_model(all_stats)
            response["by_model"] = list(by_model.values())
        elif params.group_by == "provider":
            by_provider = stats_storage.aggregate_by_provider(all_stats)
            response["by_provider"] = list(by_provider.values())

        logger.info(f"Organization stats queried: {org_id}")
        return response

    except (InvalidRequestError, AuthenticationError):
        raise
    except Exception as e:
        logger.exception("Failed to get organization stats", exc_info=e)
        raise
