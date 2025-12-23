"""
统计收集器

负责收集和记录API请求的统计数据
"""

from typing import Optional
from datetime import datetime
from ..database.models import RequestStat
from ..database.connection import get_db
from ..utils.logger import get_logger

logger = get_logger(__name__)

# 全局统计收集器实例
_stats_collector: Optional["StatsCollector"] = None


class StatsCollector:
  """统计收集器"""
  
  def __init__(self):
    """初始化统计收集器"""
    self.logger = get_logger(__name__)
  
  async def record_request(
    self,
    api_key_id: str,
    organization_id: Optional[str],
    model: str,
    provider: str,
    prompt_tokens: int,
    completion_tokens: int,
    total_tokens: int,
    cost: Optional[float] = None
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
      cost: 费用（可选）
      
    Returns:
      bool: 是否成功记录
    """
    try:
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
        timestamp=datetime.utcnow()
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
          cost=cost
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
    cost: Optional[float] = None
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
      cost: 费用（可选）
      
    Returns:
      bool: 是否成功记录
    """
    try:
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
        timestamp=datetime.utcnow()
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
          cost=cost
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

