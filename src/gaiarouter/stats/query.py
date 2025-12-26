"""
统计查询模块

负责构建和执行统计查询，格式化响应
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional

from pydantic import BaseModel

from ..utils.logger import get_logger
from .storage import StatsStorage, get_stats_storage

logger = get_logger(__name__)

# 全局统计查询实例
_stats_query: Optional["StatsQuery"] = None


class StatsQueryParams(BaseModel):
    """统计查询参数"""

    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    group_by: str = "day"  # day, week, month, model, provider


class StatsQuery:
    """统计查询"""

    def __init__(self):
        """初始化统计查询"""
        self.logger = get_logger(__name__)
        self.storage = get_stats_storage()

    def query_key_stats(self, key_id: str, params: StatsQueryParams) -> Dict:
        """
        查询API Key统计

        Args:
          key_id: API Key ID
          params: 查询参数

        Returns:
          Dict: 统计响应
        """
        try:
            # 设置默认时间范围（最近30天）
            if not params.start_date:
                params.start_date = datetime.utcnow() - timedelta(days=30)
            if not params.end_date:
                params.end_date = datetime.utcnow()

            # 查询统计数据
            stats = self.storage.get_key_stats(
                key_id=key_id,
                start_date=params.start_date,
                end_date=params.end_date,
                group_by=params.group_by,
            )

            # 获取摘要
            summary = self.storage.get_summary(stats)

            # 构建响应
            response = {
                "key_id": key_id,
                "period": {
                    "start": params.start_date.isoformat() + "Z",
                    "end": params.end_date.isoformat() + "Z",
                },
                "summary": summary,
            }

            # 根据分组方式聚合数据
            if params.group_by == "day":
                by_date = self.storage.aggregate_by_date(stats)
                response["by_date"] = list(by_date.values())
            elif params.group_by == "model":
                by_model = self.storage.aggregate_by_model(stats)
                response["by_model"] = list(by_model.values())
            elif params.group_by == "provider":
                by_provider = self.storage.aggregate_by_provider(stats)
                response["by_provider"] = list(by_provider.values())
            else:
                # 默认按日期分组
                by_date = self.storage.aggregate_by_date(stats)
                response["by_date"] = list(by_date.values())

            # 如果没有指定分组，提供所有聚合数据
            if params.group_by == "day":
                by_model = self.storage.aggregate_by_model(stats)
                by_provider = self.storage.aggregate_by_provider(stats)
                response["by_model"] = list(by_model.values())
                response["by_provider"] = list(by_provider.values())

            return response

        except Exception as e:
            self.logger.exception("Failed to query key stats", exc_info=e)
            raise

    def query_global_stats(self, params: StatsQueryParams) -> Dict:
        """
        查询全局统计

        Args:
          params: 查询参数

        Returns:
          Dict: 全局统计响应
        """
        try:
            # 设置默认时间范围（最近30天）
            if not params.start_date:
                params.start_date = datetime.utcnow() - timedelta(days=30)
            if not params.end_date:
                params.end_date = datetime.utcnow()

            # 查询统计数据
            stats = self.storage.get_global_stats(
                start_date=params.start_date, end_date=params.end_date, group_by=params.group_by
            )

            # 获取摘要
            summary = self.storage.get_summary(stats)

            # 构建响应
            response = {
                "period": {
                    "start": params.start_date.isoformat() + "Z",
                    "end": params.end_date.isoformat() + "Z",
                },
                "summary": {
                    "total_keys": 0,  # TODO: 从数据库查询
                    "active_keys": 0,  # TODO: 从数据库查询
                    "total_requests": summary["total_requests"],
                    "total_tokens": summary["total_tokens"],
                    "total_cost": summary["total_cost"],
                },
            }

            # 按提供商聚合
            by_provider = self.storage.aggregate_by_provider(stats)
            response["by_provider"] = list(by_provider.values())

            return response

        except Exception as e:
            self.logger.exception("Failed to query global stats", exc_info=e)
            raise


def get_stats_query() -> StatsQuery:
    """
    获取统计查询实例（单例模式）

    Returns:
      StatsQuery: 统计查询实例
    """
    global _stats_query
    if _stats_query is None:
        _stats_query = StatsQuery()
    return _stats_query
