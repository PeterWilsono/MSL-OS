"""
知识库服务
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from core.file_manager import file_manager
from core.data_models import KnowledgeItem, KnowledgeCategory


class KnowledgeBaseService:
    """知识库服务"""
    
    def __init__(self):
        self.fm = file_manager
    
    def _get_category_dir(self, category: str):
        """获取分类目录"""
        if category == KnowledgeCategory.DISEASE:
            return self.fm.diseases_dir
        elif category == KnowledgeCategory.PRODUCT:
            return self.fm.products_dir
        elif category == KnowledgeCategory.MARKET:
            return self.fm.market_dir
        else:
            return self.fm.knowledge_dir
    
    def create_item(
        self,
        category: str,
        title: str,
        content: str = "",
        keywords: List[str] = None,
        source: str = "",
        related_doctors: List[str] = None,
        notes: str = "",
        item_id: Optional[str] = None
    ) -> KnowledgeItem:
        """创建或更新知识条目"""
        
        if not item_id:
            item_id = f"{category}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        item = KnowledgeItem(
            item_id=item_id,
            category=category,
            title=title,
            content=content,
            keywords=keywords or [],
            source=source,
            related_doctors=related_doctors or [],
            notes=notes
        )
        
        # 保存到对应分类目录
        category_dir = self._get_category_dir(category)
        self.fm.save_model(category_dir, item, item_id)
        
        return item
    
    def get_item(self, item_id: str, category: str) -> Optional[KnowledgeItem]:
        """获取知识条目"""
        category_dir = self._get_category_dir(category)
        return self.fm.load_model(category_dir, item_id, KnowledgeItem)
    
    def update_item(self, item_id: str, category: str, updates: Dict[str, Any]) -> Optional[KnowledgeItem]:
        """更新知识条目"""
        category_dir = self._get_category_dir(category)
        item_path = category_dir / f"{item_id}.json"
        data = self.fm.read_json(item_path)
        
        if not data:
            return None
        
        for key, value in updates.items():
            if key in data:
                data[key] = value
        
        data["updated_at"] = datetime.now().isoformat()
        
        self.fm.write_json(item_path, data)
        
        return KnowledgeItem(**data)
    
    def delete_item(self, item_id: str, category: str) -> bool:
        """删除知识条目"""
        category_dir = self._get_category_dir(category)
        return self.fm.delete_file(category_dir, item_id)
    
    def list_items(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """列出知识条目"""
        items = []
        
        if category:
            categories = [category]
        else:
            categories = [KnowledgeCategory.DISEASE, KnowledgeCategory.PRODUCT, KnowledgeCategory.MARKET]
        
        for cat in categories:
            cat_dir = self._get_category_dir(cat)
            for filename in self.fm.list_files(cat_dir):
                data = self.fm.read_json(cat_dir / f"{filename}.json")
                if data:
                    items.append(data)
        
        return sorted(items, key=lambda x: x.get("title", ""))
    
    def search(self, keyword: str, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """搜索知识库"""
        results = []
        
        if category:
            categories = [category]
        else:
            categories = [KnowledgeCategory.DISEASE, KnowledgeCategory.PRODUCT, KnowledgeCategory.MARKET]
        
        for cat in categories:
            cat_dir = self._get_category_dir(cat)
            matches = self.fm.search_files(cat_dir, keyword)
            results.extend([m["data"] for m in matches])
        
        return results
    
    def get_items_by_doctor(self, doctor_id: str) -> List[Dict[str, Any]]:
        """获取与医生相关的知识"""
        all_items = self.list_items()
        return [item for item in all_items if doctor_id in item.get("related_doctors", [])]
    
    def get_category_stats(self) -> Dict[str, int]:
        """获取各分类统计"""
        return {
            "disease": len(self.fm.list_files(self.fm.diseases_dir)),
            "product": len(self.fm.list_files(self.fm.products_dir)),
            "market": len(self.fm.list_files(self.fm.market_dir)),
        }


# 创建全局实例
knowledge_service = KnowledgeBaseService()
