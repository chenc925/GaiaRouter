"""
统计控制器

处理统计查询请求
"""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query

from ...database.models import User
from ...stats.query import StatsQuery, StatsQueryParams, get_stats_query
from ...utils.errors import InvalidRequestError
from ...utils.logger import get_logger
from ..middleware.user_auth import verify_user_token

logger = get_logger(__name__)

router = APIRouter(prefix="/v1", tags=["stats"])


@router.get("/api-keys/{key_id}/stats")
async def get_key_stats(
    key_id: str,
    start_date: Optional[str] = Query(None, description="开始日期（ISO 8601格式）"),
    end_date: Optional[str] = Query(None, description="结束日期（ISO 8601格式）"),
    group_by: str = Query("day", description="分组方式：day, week, month, model, provider"),
    user: User = Depends(verify_user_token),
) -> dict:
    """
    获取API Key使用统计

    Args:
      key_id: API Key ID
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

        # 构建查询参数
        params = StatsQueryParams(start_date=start_dt, end_date=end_dt, group_by=group_by)

        # 执行查询
        stats_query = get_stats_query()
        result = stats_query.query_key_stats(key_id, params)

        logger.info("Key stats queried", key_id=key_id, group_by=group_by)

        return result

    except InvalidRequestError:
        raise
    except Exception as e:
        logger.exception("Failed to get key stats", exc_info=e)
        raise


@router.get("/stats")
async def get_global_stats(
    start_date: Optional[str] = Query(None, description="开始日期（ISO 8601格式）"),
    end_date: Optional[str] = Query(None, description="结束日期（ISO 8601格式）"),
    group_by: str = Query("day", description="分组方式：day, week, month, provider"),
    user: User = Depends(verify_user_token),
) -> dict:
    """
    获取全局统计信息

    Args:
      start_date: 开始日期（ISO 8601格式）
      end_date: 结束日期（ISO 8601格式）
      group_by: 分组方式
      user: 当前用户（通过中间件验证）

    Returns:
      dict: 全局统计响应
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
        valid_group_by = ["day", "week", "month", "provider"]
        if group_by not in valid_group_by:
            raise InvalidRequestError(
                f"Invalid group_by: {group_by}. Must be one of {valid_group_by}"
            )

        # 构建查询参数
        params = StatsQueryParams(start_date=start_dt, end_date=end_dt, group_by=group_by)

        # 执行查询
        stats_query = get_stats_query()
        result = stats_query.query_global_stats(params)

        logger.info("Global stats queried", group_by=group_by)

        return result

    except InvalidRequestError:
        raise
    except Exception as e:
        logger.exception("Failed to get global stats", exc_info=e)
        raise
