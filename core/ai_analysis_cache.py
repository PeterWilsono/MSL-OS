"""
AI 分析缓存系统
用于持久化AI分析结果，避免重复分析和token浪费
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from pathlib import Path
import json
from pydantic import BaseModel, Field


class AnalysisCache(BaseModel):
    """分析缓存模型"""
    entity_id: str = Field(..., description="实体ID（医院/科室/医生）")
    entity_type: str = Field(..., description="实体类型：hospital/department/doctor")
    analysis_type: str = Field(..., description="分析类型：overview/strategy/opportunity")
    
    # 分析结果
    summary: str = Field(default="", description="分析摘要")
    key_insights: List[str] = Field(default_factory=list, description="关键洞察")
    recommendations: List[str] = Field(default_factory=list, description="建议")
    data_snapshot: Dict[str, Any] = Field(default_factory=dict, description="数据快照")
    
    # 元数据
    created_at: datetime = Field(default_factory=datetime.now)
    last_updated: datetime = Field(default_factory=datetime.now)
    data_version: int = Field(default=1, description="数据版本号")
    is_stale: bool = Field(default=False, description="是否过期")


class AIAnalysisCacheService:
    """AI分析缓存服务"""
    
    # 缓存有效期（天）
    CACHE_VALIDITY_DAYS = 7
    
    def __init__(self, data_dir: Path):
        self.cache_dir = data_dir / "ai_analysis_cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_cache_path(self, entity_id: str, entity_type: str, analysis_type: str) -> Path:
        """获取缓存文件路径"""
        filename = f"{entity_type}_{entity_id}_{analysis_type}.json"
        return self.cache_dir / filename
    
    def get_cache(
        self, 
        entity_id: str, 
        entity_type: str, 
        analysis_type: str,
        max_age_days: Optional[int] = None
    ) -> Optional[AnalysisCache]:
        """
        获取缓存的分析结果
        
        Args:
            entity_id: 实体ID
            entity_type: 实体类型
            analysis_type: 分析类型
            max_age_days: 最大缓存天数，None则使用默认值
            
        Returns:
            缓存的分析结果，如果不存在或过期则返回None
        """
        cache_path = self._get_cache_path(entity_id, entity_type, analysis_type)
        
        if not cache_path.exists():
            return None
        
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            cache = AnalysisCache(**data)
            
            # 检查是否过期
            max_age = max_age_days or self.CACHE_VALIDITY_DAYS
            age = datetime.now() - cache.last_updated
            
            if age.days > max_age or cache.is_stale:
                return None
            
            return cache
            
        except Exception as e:
            print(f"读取缓存失败: {e}")
            return None
    
    def save_cache(self, cache: AnalysisCache) -> bool:
        """
        保存分析结果到缓存
        
        Args:
            cache: 分析缓存对象
            
        Returns:
            是否保存成功
        """
        try:
            cache_path = self._get_cache_path(
                cache.entity_id, 
                cache.entity_type, 
                cache.analysis_type
            )
            
            cache.last_updated = datetime.now()
            
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(cache.model_dump(), f, ensure_ascii=False, indent=2, default=str)
            
            return True
            
        except Exception as e:
            print(f"保存缓存失败: {e}")
            return False
    
    def invalidate_cache(self, entity_id: str, entity_type: str, analysis_type: Optional[str] = None) -> int:
        """
        使缓存失效
        
        Args:
            entity_id: 实体ID
            entity_type: 实体类型
            analysis_type: 分析类型，None则使所有类型失效
            
        Returns:
            失效的缓存数量
        """
        count = 0
        
        if analysis_type:
            # 失效特定类型
            cache_path = self._get_cache_path(entity_id, entity_type, analysis_type)
            if cache_path.exists():
                cache_path.unlink()
                count = 1
        else:
            # 失效所有类型
            pattern = f"{entity_type}_{entity_id}_*.json"
            for cache_file in self.cache_dir.glob(pattern):
                cache_file.unlink()
                count += 1
        
        return count
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        total_caches = len(list(self.cache_dir.glob("*.json")))
        
        # 按类型统计
        by_type = {}
        for cache_file in self.cache_dir.glob("*.json"):
            parts = cache_file.stem.split("_")
            if len(parts) >= 3:
                entity_type = parts[0]
                by_type[entity_type] = by_type.get(entity_type, 0) + 1
        
        return {
            "total_caches": total_caches,
            "by_type": by_type,
            "cache_dir": str(self.cache_dir)
        }
    
    def cleanup_old_caches(self, days: int = 30) -> int:
        """
        清理过期缓存
        
        Args:
            days: 清理多少天前的缓存
            
        Returns:
            清理的缓存数量
        """
        count = 0
        cutoff_time = datetime.now() - timedelta(days=days)
        
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                last_updated = datetime.fromisoformat(data.get('last_updated', ''))
                
                if last_updated < cutoff_time:
                    cache_file.unlink()
                    count += 1
                    
            except Exception:
                continue
        
        return count
