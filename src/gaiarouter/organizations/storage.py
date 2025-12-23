"""
组织存储模块

负责组织的数据库存储和查询
"""

from typing import List, Optional, Dict
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from ..database.models import Organization
from ..database.connection import get_db
from ..utils.logger import get_logger

logger = get_logger(__name__)

# 全局组织存储实例
_org_storage: Optional["OrganizationStorage"] = None


class OrganizationStorage:
  """组织存储"""
  
  def __init__(self):
    """初始化组织存储"""
    self.logger = get_logger(__name__)
  
  def save(self, org: Organization) -> bool:
    """
    保存组织到数据库
    
    Args:
      org: 组织对象
      
    Returns:
      bool: 是否成功保存
    """
    try:
      db = next(get_db())
      try:
        db.add(org)
        db.commit()
        db.refresh(org)
        return True
      except Exception as e:
        db.rollback()
        self.logger.error(f"Failed to save organization: {e}", exc_info=e)
        raise
      finally:
        db.close()
    except Exception as e:
      self.logger.exception("Failed to save organization", exc_info=e)
      return False
  
  def get(self, org_id: str) -> Optional[Organization]:
    """
    从数据库获取组织
    
    Args:
      org_id: 组织ID
      
    Returns:
      Optional[Organization]: 组织对象，如果不存在返回None
    """
    try:
      db = next(get_db())
      try:
        org = db.query(Organization).filter(Organization.id == org_id).first()
        return org
      finally:
        db.close()
    except Exception as e:
      self.logger.exception("Failed to get organization", exc_info=e)
      return None
  
  def list(
    self,
    filters: Optional[Dict] = None,
    page: int = 1,
    limit: int = 20
  ) -> tuple[List[Organization], int]:
    """
    查询组织列表
    
    Args:
      filters: 过滤条件
      page: 页码
      limit: 每页数量
      
    Returns:
      tuple: (组织列表, 总数)
    """
    try:
      db = next(get_db())
      try:
        query = db.query(Organization)
        
        # 应用过滤条件
        if filters:
          if "status" in filters:
            query = query.filter(Organization.status == filters["status"])
          if "search" in filters and filters["search"]:
            search_term = f"%{filters['search']}%"
            query = query.filter(
              or_(
                Organization.name.like(search_term),
                Organization.description.like(search_term)
              )
            )
        
        # 获取总数
        total = query.count()
        
        # 分页
        offset = (page - 1) * limit
        orgs = query.order_by(Organization.created_at.desc()).offset(offset).limit(limit).all()
        
        return orgs, total
      finally:
        db.close()
    except Exception as e:
      self.logger.exception("Failed to list organizations", exc_info=e)
      return [], 0
  
  def update(self, org_id: str, updates: Dict) -> bool:
    """
    更新组织
    
    Args:
      org_id: 组织ID
      updates: 更新字段字典
      
    Returns:
      bool: 是否成功更新
    """
    try:
      db = next(get_db())
      try:
        org = db.query(Organization).filter(Organization.id == org_id).first()
        if not org:
          return False
        
        # 更新字段
        for field, value in updates.items():
          if hasattr(org, field):
            setattr(org, field, value)
        
        org.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(org)
        return True
      except Exception as e:
        db.rollback()
        self.logger.error(f"Failed to update organization: {e}", exc_info=e)
        raise
      finally:
        db.close()
    except Exception as e:
      self.logger.exception("Failed to update organization", exc_info=e)
      return False
  
  def delete(self, org_id: str) -> bool:
    """
    删除组织（软删除）
    
    Args:
      org_id: 组织ID
      
    Returns:
      bool: 是否成功删除
    """
    try:
      db = next(get_db())
      try:
        org = db.query(Organization).filter(Organization.id == org_id).first()
        if not org:
          return False
        
        # 软删除：更新状态为inactive
        org.status = "inactive"
        org.updated_at = datetime.utcnow()
        db.commit()
        return True
      except Exception as e:
        db.rollback()
        self.logger.error(f"Failed to delete organization: {e}", exc_info=e)
        raise
      finally:
        db.close()
    except Exception as e:
      self.logger.exception("Failed to delete organization", exc_info=e)
      return False


def get_organization_storage() -> OrganizationStorage:
  """
  获取组织存储实例（单例模式）
  
  Returns:
    OrganizationStorage: 组织存储实例
  """
  global _org_storage
  if _org_storage is None:
    _org_storage = OrganizationStorage()
  return _org_storage

