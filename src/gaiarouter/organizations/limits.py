"""
使用限制检查模块

检查组织是否超出使用限制
"""

from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import and_, func

from ..database.connection import get_db
from ..database.models import Organization, RequestStat
from ..utils.errors import OrganizationLimitError
from ..utils.logger import get_logger

logger = get_logger(__name__)

# 全局限制检查器实例
_limit_checker: Optional["LimitChecker"] = None


class LimitChecker:
    """使用限制检查器"""

    def __init__(self):
        """初始化限制检查器"""
        self.logger = get_logger(__name__)

    def _get_month_start(self) -> datetime:
        """
        获取当前月份的开始时间

        Returns:
          datetime: 月份开始时间
        """
        now = datetime.utcnow()
        return datetime(now.year, now.month, 1, 0, 0, 0)

    def _get_month_end(self) -> datetime:
        """
        获取当前月份的结束时间

        Returns:
          datetime: 月份结束时间
        """
        now = datetime.utcnow()
        if now.month == 12:
            return datetime(now.year + 1, 1, 1, 0, 0, 0) - timedelta(seconds=1)
        else:
            return datetime(now.year, now.month + 1, 1, 0, 0, 0) - timedelta(seconds=1)

    def _get_monthly_stats(self, organization_id: str) -> dict:
        """
        获取组织本月统计数据

        Args:
          organization_id: 组织ID

        Returns:
          dict: 统计数据（requests, tokens, cost）
        """
        try:
            db = next(get_db())
            try:
                month_start = self._get_month_start()
                month_end = self._get_month_end()

                # 查询本月统计数据
                stats = (
                    db.query(
                        func.count(RequestStat.id).label("requests"),
                        func.sum(RequestStat.total_tokens).label("tokens"),
                        func.sum(RequestStat.cost).label("cost"),
                    )
                    .filter(
                        and_(
                            RequestStat.organization_id == organization_id,
                            RequestStat.timestamp >= month_start,
                            RequestStat.timestamp <= month_end,
                        )
                    )
                    .first()
                )

                return {
                    "requests": int(stats.requests or 0),
                    "tokens": int(stats.tokens or 0),
                    "cost": float(stats.cost or 0.0),
                }
            finally:
                db.close()
        except Exception as e:
            self.logger.exception("Failed to get monthly stats", exc_info=e)
            return {"requests": 0, "tokens": 0, "cost": 0.0}

    def check_limits(
        self,
        organization: Organization,
        additional_requests: int = 0,
        additional_tokens: int = 0,
        additional_cost: float = 0.0,
    ) -> bool:
        """
        检查组织是否超出使用限制

        Args:
          organization: 组织对象
          additional_requests: 额外请求数（用于预检查）
          additional_tokens: 额外Token数（用于预检查）
          additional_cost: 额外费用（用于预检查）

        Returns:
          bool: 是否超出限制

        Raises:
          OrganizationLimitError: 如果超出限制
        """
        try:
            # 获取本月统计数据
            stats = self._get_monthly_stats(organization.id)

            # 检查请求次数限制
            if organization.monthly_requests_limit:
                total_requests = stats["requests"] + additional_requests
                if total_requests >= organization.monthly_requests_limit:
                    raise OrganizationLimitError(
                        f"Monthly requests limit exceeded: {total_requests}/{organization.monthly_requests_limit}"
                    )

            # 检查Token限制
            if organization.monthly_tokens_limit:
                total_tokens = stats["tokens"] + additional_tokens
                if total_tokens >= organization.monthly_tokens_limit:
                    raise OrganizationLimitError(
                        f"Monthly tokens limit exceeded: {total_tokens}/{organization.monthly_tokens_limit}"
                    )

            # 检查费用限制
            if organization.monthly_cost_limit:
                total_cost = stats["cost"] + additional_cost
                if total_cost >= float(organization.monthly_cost_limit):
                    raise OrganizationLimitError(
                        f"Monthly cost limit exceeded: {total_cost:.2f}/{organization.monthly_cost_limit}"
                    )

            return True

        except OrganizationLimitError:
            raise
        except Exception as e:
            self.logger.exception("Failed to check limits", exc_info=e)
            # 如果检查失败，允许请求继续（避免因系统问题导致服务不可用）
            return True


def get_limit_checker() -> LimitChecker:
    """
    获取限制检查器实例（单例模式）

    Returns:
      LimitChecker: 限制检查器实例
    """
    global _limit_checker
    if _limit_checker is None:
        _limit_checker = LimitChecker()
    return _limit_checker
