"""
统计收集器

负责收集和记录API请求的统计数据
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from ..database.connection import get_db
from ..database.models import Model, RequestStat
from ..utils.logger import get_logger

logger = get_logger(__name__)

# 全局统计收集器实例
_stats_collector: Optional["StatsCollector"] = None


class StatsCollector:
    """统计收集器"""

    def __init__(self):
        """初始化统计收集器"""
        self.logger = get_logger(__name__)

    def calculate_cost(
        self, model_id: str, prompt_tokens: int, completion_tokens: int
    ) -> Optional[float]:
        """
        计算请求费用

        根据模型定价和 token 使用量自动计算费用

        Args:
            model_id: 模型ID（如 openai/gpt-4）
            prompt_tokens: 输入 Token 数
            completion_tokens: 输出 Token 数

        Returns:
            float: 计算的费用（美元），如果无法计算则返回 None
        """
        try:
            # 查询模型定价信息
            db = next(get_db())
            try:
                model = db.query(Model).filter(Model.id == model_id).first()

                if not model:
                    self.logger.warning(f"Model not found for cost calculation: {model_id}")
                    return None

                # 检查是否有定价信息
                if model.pricing_prompt is None or model.pricing_completion is None:
                    self.logger.debug(
                        f"Model {model_id} has no pricing info, cost calculation skipped"
                    )
                    return None

                # 计算费用（定价单位为每1K tokens）
                prompt_cost = (float(prompt_tokens) / 1000.0) * float(model.pricing_prompt)
                completion_cost = (float(completion_tokens) / 1000.0) * float(
                    model.pricing_completion
                )
                total_cost = prompt_cost + completion_cost

                self.logger.debug(
                    "Cost calculated",
                    model=model_id,
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    prompt_cost=prompt_cost,
                    completion_cost=completion_cost,
                    total_cost=total_cost,
                )

                return round(total_cost, 6)  # 保留6位小数

            finally:
                db.close()

        except Exception as e:
            self.logger.error(f"Failed to calculate cost: {e}", exc_info=True)
            return None

    async def record_request(
        self,
        api_key_id: str,
        organization_id: Optional[str],
        model: str,
        provider: str,
        prompt_tokens: int,
        completion_tokens: int,
        total_tokens: int,
        cost: Optional[float] = None,
    ) -> bool:
        """
        记录请求统计

        Args:
          api_key_id: API Key ID
          organization_id: 组织ID（可选）
          model: 模型标识
          provider: 提供商
          prompt_tokens: 输入Token数
          completion_tokens: 输出Token数
          total_tokens: 总Token数
          cost: 费用（可选，如果不提供则自动计算）

        Returns:
          bool: 是否成功记录
        """
        try:
            # 如果没有提供费用，则自动计算
            if cost is None:
                cost = self.calculate_cost(model, prompt_tokens, completion_tokens)

            # 创建统计记录
            stat = RequestStat(
                api_key_id=api_key_id,
                organization_id=organization_id,
                model=model,
                provider=provider,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                cost=cost,
                timestamp=datetime.utcnow(),
            )

            # 保存到数据库
            db = next(get_db())
            try:
                db.add(stat)
                db.commit()
                db.refresh(stat)

                self.logger.debug(
                    "Request stat recorded",
                    api_key_id=api_key_id,
                    model=model,
                    tokens=total_tokens,
                    cost=cost,
                )

                return True
            except Exception as e:
                db.rollback()
                self.logger.error(f"Failed to save stat: {e}", exc_info=e)
                raise
            finally:
                db.close()

        except Exception as e:
            self.logger.exception("Failed to record request stat", exc_info=e)
            return False

    def record_request_sync(
        self,
        api_key_id: str,
        organization_id: Optional[str],
        model: str,
        provider: str,
        prompt_tokens: int,
        completion_tokens: int,
        total_tokens: int,
        cost: Optional[float] = None,
    ) -> bool:
        """
        同步记录请求统计（用于非异步环境）

        Args:
          api_key_id: API Key ID
          organization_id: 组织ID（可选）
          model: 模型标识
          provider: 提供商
          prompt_tokens: 输入Token数
          completion_tokens: 输出Token数
          total_tokens: 总Token数
          cost: 费用（可选，如果不提供则自动计算）

        Returns:
          bool: 是否成功记录
        """
        try:
            # 如果没有提供费用，则自动计算
            if cost is None:
                cost = self.calculate_cost(model, prompt_tokens, completion_tokens)

            # 创建统计记录
            stat = RequestStat(
                api_key_id=api_key_id,
                organization_id=organization_id,
                model=model,
                provider=provider,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                cost=cost,
                timestamp=datetime.utcnow(),
            )

            # 保存到数据库
            db = next(get_db())
            try:
                db.add(stat)
                db.commit()
                db.refresh(stat)

                self.logger.debug(
                    "Request stat recorded (sync)",
                    api_key_id=api_key_id,
                    model=model,
                    tokens=total_tokens,
                    cost=cost,
                )

                return True
            except Exception as e:
                db.rollback()
                self.logger.error(f"Failed to save stat: {e}", exc_info=e)
                raise
            finally:
                db.close()

        except Exception as e:
            self.logger.exception("Failed to record request stat (sync)", exc_info=e)
            return False


def get_stats_collector() -> StatsCollector:
    """
    获取统计收集器实例（单例模式）

    Returns:
      StatsCollector: 统计收集器实例
    """
    global _stats_collector
    if _stats_collector is None:
        _stats_collector = StatsCollector()
    return _stats_collector
