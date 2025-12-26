"""
统计存储模块

负责统计数据的存储和查询
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional

from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from ..database.connection import get_db
from ..database.models import APIKey, RequestStat
from ..utils.logger import get_logger

logger = get_logger(__name__)

# 全局统计存储实例
_stats_storage: Optional["StatsStorage"] = None


class StatsStorage:
    """统计存储"""

    def __init__(self):
        """初始化统计存储"""
        self.logger = get_logger(__name__)

    def save(self, stat: RequestStat) -> bool:
        """
        保存统计数据

        Args:
          stat: 统计记录

        Returns:
          bool: 是否成功保存
        """
        try:
            db = next(get_db())
            try:
                db.add(stat)
                db.commit()
                db.refresh(stat)
                return True
            except Exception as e:
                db.rollback()
                self.logger.error(f"Failed to save stat: {e}", exc_info=e)
                raise
            finally:
                db.close()
        except Exception as e:
            self.logger.exception("Failed to save stat", exc_info=e)
            return False

    def get_key_stats(
        self,
        key_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        group_by: str = "day",
    ) -> List[RequestStat]:
        """
        查询API Key统计

        Args:
          key_id: API Key ID
          start_date: 开始日期
          end_date: 结束日期
          group_by: 分组方式（day/week/month）

        Returns:
          List[RequestStat]: 统计记录列表
        """
        try:
            db = next(get_db())
            try:
                query = db.query(RequestStat).filter(RequestStat.api_key_id == key_id)

                # 时间范围过滤
                if start_date:
                    query = query.filter(RequestStat.timestamp >= start_date)
                if end_date:
                    query = query.filter(RequestStat.timestamp <= end_date)

                # 排序
                query = query.order_by(RequestStat.timestamp.asc())

                stats = query.all()
                return stats
            finally:
                db.close()
        except Exception as e:
            self.logger.exception("Failed to get key stats", exc_info=e)
            return []

    def get_global_stats(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        group_by: str = "day",
    ) -> List[RequestStat]:
        """
        查询全局统计

        Args:
          start_date: 开始日期
          end_date: 结束日期
          group_by: 分组方式（day/week/month）

        Returns:
          List[RequestStat]: 统计记录列表
        """
        try:
            db = next(get_db())
            try:
                query = db.query(RequestStat)

                # 时间范围过滤
                if start_date:
                    query = query.filter(RequestStat.timestamp >= start_date)
                if end_date:
                    query = query.filter(RequestStat.timestamp <= end_date)

                # 排序
                query = query.order_by(RequestStat.timestamp.asc())

                stats = query.all()
                return stats
            finally:
                db.close()
        except Exception as e:
            self.logger.exception("Failed to get global stats", exc_info=e)
            return []

    def aggregate_by_date(self, stats: List[RequestStat]) -> Dict[str, Dict]:
        """
        按日期聚合统计数据

        Args:
          stats: 统计记录列表

        Returns:
          Dict[str, Dict]: 按日期聚合的统计数据
        """
        aggregated = {}

        for stat in stats:
            # 获取日期（YYYY-MM-DD格式）
            date_str = stat.timestamp.strftime("%Y-%m-%d")

            if date_str not in aggregated:
                aggregated[date_str] = {
                    "date": date_str,
                    "requests": 0,
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "total_tokens": 0,
                    "cost": 0.0,
                }

            aggregated[date_str]["requests"] += 1
            aggregated[date_str]["prompt_tokens"] += stat.prompt_tokens
            aggregated[date_str]["completion_tokens"] += stat.completion_tokens
            aggregated[date_str]["total_tokens"] += stat.total_tokens
            if stat.cost:
                aggregated[date_str]["cost"] += float(stat.cost)

        return aggregated

    def aggregate_by_model(self, stats: List[RequestStat]) -> Dict[str, Dict]:
        """
        按模型聚合统计数据

        Args:
          stats: 统计记录列表

        Returns:
          Dict[str, Dict]: 按模型聚合的统计数据
        """
        aggregated = {}

        for stat in stats:
            model = stat.model

            if model not in aggregated:
                aggregated[model] = {
                    "model": model,
                    "requests": 0,
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "total_tokens": 0,
                    "cost": 0.0,
                }

            aggregated[model]["requests"] += 1
            aggregated[model]["prompt_tokens"] += stat.prompt_tokens
            aggregated[model]["completion_tokens"] += stat.completion_tokens
            aggregated[model]["total_tokens"] += stat.total_tokens
            if stat.cost:
                aggregated[model]["cost"] += float(stat.cost)

        return aggregated

    def aggregate_by_provider(self, stats: List[RequestStat]) -> Dict[str, Dict]:
        """
        按提供商聚合统计数据

        Args:
          stats: 统计记录列表

        Returns:
          Dict[str, Dict]: 按提供商聚合的统计数据
        """
        aggregated = {}

        for stat in stats:
            provider = stat.provider

            if provider not in aggregated:
                aggregated[provider] = {
                    "provider": provider,
                    "requests": 0,
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "total_tokens": 0,
                    "cost": 0.0,
                }

            aggregated[provider]["requests"] += 1
            aggregated[provider]["prompt_tokens"] += stat.prompt_tokens
            aggregated[provider]["completion_tokens"] += stat.completion_tokens
            aggregated[provider]["total_tokens"] += stat.total_tokens
            if stat.cost:
                aggregated[provider]["cost"] += float(stat.cost)

        return aggregated

    def get_summary(self, stats: List[RequestStat]) -> Dict:
        """
        获取统计摘要

        Args:
          stats: 统计记录列表

        Returns:
          Dict: 统计摘要
        """
        summary = {
            "total_requests": len(stats),
            "total_prompt_tokens": 0,
            "total_completion_tokens": 0,
            "total_tokens": 0,
            "total_cost": 0.0,
        }

        for stat in stats:
            summary["total_prompt_tokens"] += stat.prompt_tokens
            summary["total_completion_tokens"] += stat.completion_tokens
            summary["total_tokens"] += stat.total_tokens
            if stat.cost:
                summary["total_cost"] += float(stat.cost)

        return summary


def get_stats_storage() -> StatsStorage:
    """
    获取统计存储实例（单例模式）

    Returns:
      StatsStorage: 统计存储实例
    """
    global _stats_storage
    if _stats_storage is None:
        _stats_storage = StatsStorage()
    return _stats_storage
