"""
数据中心服务 - 统一数据管理和搜索
"""
from typing import List, Dict, Any, Optional
from core.file_manager import file_manager
from modules.doctor_manager.service import doctor_service
from modules.contact_manager.service import contact_service
from modules.knowledge_base.service import knowledge_service
from modules.hospital_manager.service import hospital_service
from modules.visit_summary.service import visit_summary_service
from modules.personal_growth.service import personal_growth_service


class DataCenterService:
    """数据中心服务"""
    
    def __init__(self):
        self.fm = file_manager
    
    def get_all_data_summary(self) -> Dict[str, int]:
        """获取所有数据的统计摘要"""
        return {
            "hospitals": len(hospital_service.list_hospitals()),
            "departments": len(hospital_service.list_departments()),
            "products": len(hospital_service.list_products()),
            "competitors": len(hospital_service.list_competitors()),
            "doctors": len(doctor_service.list_doctors()),
            "contacts": len(contact_service.list_contacts()),
            "visits": len(visit_summary_service.list_visits(limit=1000)),
            "interactions": len(contact_service.list_interactions(limit=1000)),
            "knowledge_items": len(knowledge_service.list_items()),
            "reflections": len(personal_growth_service.list_reflections(limit=1000)),
        }
    
    def global_search(self, keyword: str) -> Dict[str, List[Dict[str, Any]]]:
        """全局搜索所有数据"""
        results = {
            "hospitals": self._extract_search_results(hospital_service.search_hospitals(keyword)),
            "products": self._extract_search_results(hospital_service.search_products(keyword)),
            "competitors": self._extract_search_results(hospital_service.search_competitors(keyword)),
            "doctors": self._extract_search_results(doctor_service.search_doctors(keyword)),
            "contacts": self._extract_search_results(contact_service.search_contacts(keyword)),
            "knowledge": self._extract_search_results(knowledge_service.search(keyword)),
        }

        # 添加结果计数
        results["total_count"] = sum(len(v) for v in results.values() if isinstance(v, list))

        return results

    def _extract_search_results(self, search_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """从搜索结果中提取数据，兼容不同格式"""
        if not search_results:
            return []

        # 如果是 {"filename": ..., "data": ...} 格式，提取 data
        if isinstance(search_results[0], dict) and "data" in search_results[0]:
            return [item["data"] for item in search_results]

        # 如果已经是扁平格式，直接返回
        return search_results
    
    def get_data_by_category(self, category: str, limit: int = 100) -> List[Dict[str, Any]]:
        """按分类获取数据"""
        if category == "hospitals":
            return hospital_service.list_hospitals()
        elif category == "departments":
            return hospital_service.list_departments()
        elif category == "products":
            return hospital_service.list_products()
        elif category == "competitors":
            return hospital_service.list_competitors()
        elif category == "doctors":
            return doctor_service.list_doctors()
        elif category == "contacts":
            return contact_service.list_contacts()
        elif category == "visits":
            return visit_summary_service.list_visits(limit=limit)
        elif category == "interactions":
            return contact_service.list_interactions(limit=limit)
        elif category == "knowledge":
            return knowledge_service.list_items()
        elif category == "reflections":
            return personal_growth_service.list_reflections(limit=limit)
        else:
            return []
    
    def delete_data(self, category: str, item_id: str) -> bool:
        """删除数据"""
        if category == "hospitals":
            return hospital_service.delete_hospital(item_id)
        elif category == "departments":
            return hospital_service.delete_department(item_id)
        elif category == "products":
            return hospital_service.delete_product(item_id)
        elif category == "competitors":
            return hospital_service.delete_competitor(item_id)
        elif category == "doctors":
            return doctor_service.delete_doctor(item_id)
        elif category == "contacts":
            return contact_service.delete_contact(item_id)
        elif category == "knowledge":
            # 需要知道知识的具体分类
            for cat in ["disease", "product", "market"]:
                if knowledge_service.delete_item(item_id, cat):
                    return True
            return False
        else:
            return False
    
    def export_all_data(self) -> str:
        """导出所有数据为JSON格式"""
        import json
        
        all_data = {
            "hospitals": hospital_service.list_hospitals(),
            "departments": hospital_service.list_departments(),
            "products": hospital_service.list_products(),
            "competitors": hospital_service.list_competitors(),
            "doctors": doctor_service.list_doctors(),
            "contacts": contact_service.list_contacts(),
            "knowledge": knowledge_service.list_items(),
        }
        
        return json.dumps(all_data, ensure_ascii=False, indent=2, default=str)


# 创建全局实例
data_center_service = DataCenterService()
