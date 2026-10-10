"""
隐私管理模块
控制敏感数据的输出和访问
"""
from typing import Dict, List, Any, Optional
from .data_models import VisibilityLevel


class PrivacyManager:
    """隐私管理器"""
    
    # 需要过滤的私有字段
    PRIVATE_FIELDS = [
        "anxiety_source",
        "weakness",
        "avoidance",
        "breakthrough",
    ]
    
    # 始终隐藏的字段（不对外暴露）
    HIDDEN_FIELDS = [
        "deepseek_api_key",
    ]
    
    @classmethod
    def filter_private_content(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        过滤私有内容
        
        Args:
            data: 原始数据
            
        Returns:
            过滤后的数据
        """
        if not isinstance(data, dict):
            return data
        
        # 如果整条记录标记为私有，返回空
        if data.get("visibility") == VisibilityLevel.PRIVATE:
            return {}
        
        filtered = {}
        for key, value in data.items():
            # 跳过私有字段
            if key in cls.PRIVATE_FIELDS:
                continue
            # 跳过隐藏字段
            if key in cls.HIDDEN_FIELDS:
                continue
            
            # 递归处理嵌套数据
            if isinstance(value, dict):
                filtered[key] = cls.filter_private_content(value)
            elif isinstance(value, list):
                filtered[key] = [
                    cls.filter_private_content(item) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                filtered[key] = value
        
        return filtered
    
    @classmethod
    def filter_for_export(cls, data_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        为导出过滤数据列表
        
        Args:
            data_list: 数据列表
            
        Returns:
            过滤后的数据列表
        """
        result = []
        for item in data_list:
            filtered = cls.filter_private_content(item)
            if filtered:  # 只添加非空结果
                result.append(filtered)
        return result
    
    @classmethod
    def is_private_record(cls, data: Dict[str, Any]) -> bool:
        """检查记录是否为私有"""
        return data.get("visibility") == VisibilityLevel.PRIVATE
    
    @classmethod
    def sanitize_for_ai(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        清理数据以用于 AI 分析（移除敏感信息）
        
        Args:
            data: 原始数据
            
        Returns:
            清理后的数据
        """
        sanitized = cls.filter_private_content(data)
        
        # 额外移除可能泄露身份的信息
        identity_fields = ["hospital", "name"]
        for field in identity_fields:
            if field in sanitized:
                sanitized[field] = "[已隐藏]"
        
        return sanitized
    
    @classmethod
    def get_exportable_fields(cls, model_name: str) -> List[str]:
        """
        获取模型可导出的字段列表
        
        Args:
            model_name: 模型名称
            
        Returns:
            可导出字段列表
        """
        # 定义各模型的可导出字段
        exportable = {
            "Doctor": [
                "doctor_id", "name", "hospital", "department", "title",
                "interests", "decision_style", "relationship_stage"
            ],
            "Visit": [
                "visit_id", "doctor_id", "visit_date", "key_topics",
                "doctor_concerns", "responses", "follow_up_tasks"
            ],
            "Preparation": [
                "prep_id", "doctor_id", "visit_date", "visit_goal",
                "prepared_data", "key_messages"
            ],
            "Reflection": [],  # 个人反思不导出
            "KnowledgeItem": [
                "item_id", "category", "title", "content", "keywords"
            ],
        }
        
        return exportable.get(model_name, [])


# 创建全局实例
privacy_manager = PrivacyManager()
