"""
数据同步服务
负责在数据更新时自动同步相关的所有数据，保持数据一致性
"""
from typing import Dict, Any, List
from pathlib import Path
from datetime import datetime


class DataSyncService:
    """数据同步服务"""
    
    def __init__(self, file_manager):
        self.fm = file_manager
    
    # ==================== 医院数据同步 ====================
    
    def sync_hospital_name_change(self, hospital_id: str, new_name: str) -> Dict[str, int]:
        """
        同步医院名称变更到所有相关数据
        
        Returns:
            更新统计 {'doctors': 更新数量, 'associations': 更新数量, ...}
        """
        stats = {
            'doctors': 0,
            'contacts': 0,
            'visits': 0,
            'preparations': 0,
            'associations': 0,
            'customer_tracking': 0
        }
        
        # 1. 更新医生档案中的医院名称
        doctors_dir = self.fm.data_dir / "doctors"
        if doctors_dir.exists():
            for doctor_file in doctors_dir.glob("*.json"):
                data = self.fm.read_json(doctor_file)
                if data and data.get('hospital_id') == hospital_id:
                    data['hospital'] = new_name
                    data['updated_at'] = datetime.now().isoformat()
                    self.fm.write_json(doctor_file, data)
                    stats['doctors'] += 1
        
        # 2. 更新联系人中的医院名称
        contacts_dir = self.fm.data_dir / "contacts"
        if contacts_dir.exists():
            for contact_file in contacts_dir.glob("*.json"):
                data = self.fm.read_json(contact_file)
                if data and data.get('hospital_id') == hospital_id:
                    data['hospital'] = new_name
                    data['updated_at'] = datetime.now().isoformat()
                    self.fm.write_json(contact_file, data)
                    stats['contacts'] += 1
        
        # 3. 更新拜访记录中的医院名称
        visits_dir = self.fm.data_dir / "visits"
        if visits_dir.exists():
            for visit_file in visits_dir.glob("*.json"):
                data = self.fm.read_json(visit_file)
                if data and data.get('hospital_id') == hospital_id:
                    data['hospital'] = new_name
                    data['updated_at'] = datetime.now().isoformat()
                    self.fm.write_json(visit_file, data)
                    stats['visits'] += 1
        
        # 4. 更新拜访准备中的医院名称
        preparations_dir = self.fm.data_dir / "preparations"
        if preparations_dir.exists():
            for prep_file in preparations_dir.glob("*.json"):
                data = self.fm.read_json(prep_file)
                if data and data.get('hospital_id') == hospital_id:
                    data['hospital'] = new_name
                    data['updated_at'] = datetime.now().isoformat()
                    self.fm.write_json(prep_file, data)
                    stats['preparations'] += 1
        
        # 5. 更新产品关联中的医院名称
        associations_dir = self.fm.data_dir / "associations"
        if associations_dir.exists():
            for assoc_file in associations_dir.glob("*.json"):
                data = self.fm.read_json(assoc_file)
                if data and data.get('hospital_id') == hospital_id:
                    data['hospital_name'] = new_name
                    data['updated_at'] = datetime.now().isoformat()
                    self.fm.write_json(assoc_file, data)
                    stats['associations'] += 1
        
        # 6. 更新客户追踪中的医院名称（暂时跳过，因为客户追踪数据结构不同）
        # 客户追踪数据存储在statistics.json中，是统计数据而非单个记录
        # 如果需要同步，需要单独处理
        
        return stats
    
    # ==================== 科室数据同步 ====================
    
    def sync_department_name_change(self, department_id: str, new_name: str) -> Dict[str, int]:
        """同步科室名称变更到所有相关数据"""
        stats = {
            'doctors': 0,
            'contacts': 0,
            'visits': 0,
            'preparations': 0,
            'associations': 0,
            'customer_tracking': 0
        }
        
        # 1. 更新医生档案
        doctors_dir = self.fm.data_dir / "doctors"
        if doctors_dir.exists():
            for doctor_file in doctors_dir.glob("*.json"):
                data = self.fm.read_json(doctor_file)
                if data and data.get('department_id') == department_id:
                    data['department'] = new_name
                    data['updated_at'] = datetime.now().isoformat()
                    self.fm.write_json(doctor_file, data)
                    stats['doctors'] += 1
        
        # 2. 更新联系人
        contacts_dir = self.fm.data_dir / "contacts"
        if contacts_dir.exists():
            for contact_file in contacts_dir.glob("*.json"):
                data = self.fm.read_json(contact_file)
                if data and data.get('department_id') == department_id:
                    data['department'] = new_name
                    data['updated_at'] = datetime.now().isoformat()
                    self.fm.write_json(contact_file, data)
                    stats['contacts'] += 1
        
        # 3. 更新拜访记录
        visits_dir = self.fm.data_dir / "visits"
        if visits_dir.exists():
            for visit_file in visits_dir.glob("*.json"):
                data = self.fm.read_json(visit_file)
                if data and data.get('department_id') == department_id:
                    data['department'] = new_name
                    data['updated_at'] = datetime.now().isoformat()
                    self.fm.write_json(visit_file, data)
                    stats['visits'] += 1
        
        # 4. 更新产品关联
        associations_dir = self.fm.data_dir / "associations"
        if associations_dir.exists():
            for assoc_file in associations_dir.glob("*.json"):
                data = self.fm.read_json(assoc_file)
                if data and data.get('department_id') == department_id:
                    data['department_name'] = new_name
                    data['updated_at'] = datetime.now().isoformat()
                    self.fm.write_json(assoc_file, data)
                    stats['associations'] += 1
        
        # 5. 更新客户追踪（暂时跳过，因为客户追踪数据结构不同）
        # 客户追踪数据存储在statistics.json中，是统计数据而非单个记录
        
        return stats
    
    # ==================== 产品数据同步 ====================
    
    def sync_product_name_change(self, product_id: str, new_name: str) -> Dict[str, int]:
        """同步产品名称变更到所有相关数据"""
        stats = {
            'associations': 0,
            'knowledge': 0
        }
        
        # 1. 更新产品关联
        associations_dir = self.fm.data_dir / "associations"
        if associations_dir.exists():
            for assoc_file in associations_dir.glob("*.json"):
                data = self.fm.read_json(assoc_file)
                if data and data.get('product_id') == product_id:
                    data['product_name'] = new_name
                    data['updated_at'] = datetime.now().isoformat()
                    self.fm.write_json(assoc_file, data)
                    stats['associations'] += 1
        
        # 2. 更新知识库产品
        knowledge_products_dir = self.fm.data_dir / "knowledge" / "products"
        if knowledge_products_dir.exists():
            for kb_file in knowledge_products_dir.glob("*.json"):
                data = self.fm.read_json(kb_file)
                if data and data.get('product_id') == product_id:
                    data['product_name'] = new_name
                    data['updated_at'] = datetime.now().isoformat()
                    self.fm.write_json(kb_file, data)
                    stats['knowledge'] += 1
        
        return stats
    
    # ==================== 医生数据同步 ====================
    
    def sync_doctor_name_change(self, doctor_id: str, new_name: str) -> Dict[str, int]:
        """同步医生名称变更到所有相关数据"""
        stats = {
            'visits': 0,
            'preparations': 0,
            'contacts': 0,
            'customer_tracking': 0
        }
        
        # 1. 更新拜访记录
        visits_dir = self.fm.data_dir / "visits"
        if visits_dir.exists():
            for visit_file in visits_dir.glob("*.json"):
                data = self.fm.read_json(visit_file)
                if data and data.get('doctor_id') == doctor_id:
                    data['doctor_name'] = new_name
                    data['updated_at'] = datetime.now().isoformat()
                    self.fm.write_json(visit_file, data)
                    stats['visits'] += 1
        
        # 2. 更新拜访准备
        preparations_dir = self.fm.data_dir / "preparations"
        if preparations_dir.exists():
            for prep_file in preparations_dir.glob("*.json"):
                data = self.fm.read_json(prep_file)
                if data and data.get('doctor_id') == doctor_id:
                    data['doctor_name'] = new_name
                    data['updated_at'] = datetime.now().isoformat()
                    self.fm.write_json(prep_file, data)
                    stats['preparations'] += 1
        
        # 3. 更新联系人（如果医生也是联系人）
        contacts_dir = self.fm.data_dir / "contacts"
        if contacts_dir.exists():
            for contact_file in contacts_dir.glob("*.json"):
                data = self.fm.read_json(contact_file)
                if data and data.get('related_doctor_id') == doctor_id:
                    data['name'] = new_name
                    data['updated_at'] = datetime.now().isoformat()
                    self.fm.write_json(contact_file, data)
                    stats['contacts'] += 1
        
        # 4. 更新客户追踪（暂时跳过，因为客户追踪数据结构不同）
        # 客户追踪数据存储在statistics.json中，是统计数据而非单个记录
        
        return stats
    
    # ==================== 批量同步 ====================
    
    def sync_all_data(self) -> Dict[str, Any]:
        """
        全量同步所有数据，确保数据一致性
        用于数据修复或初始化
        """
        results = {
            'hospitals_synced': 0,
            'departments_synced': 0,
            'products_synced': 0,
            'doctors_synced': 0,
            'total_updates': 0
        }
        
        # 1. 同步所有医院
        hospitals_dir = self.fm.data_dir / "hospitals"
        if hospitals_dir.exists():
            for hospital_file in hospitals_dir.glob("*.json"):
                data = self.fm.read_json(hospital_file)
                if data:
                    hospital_id = data.get('hospital_id')
                    hospital_name = data.get('name')
                    stats = self.sync_hospital_name_change(hospital_id, hospital_name)
                    results['hospitals_synced'] += 1
                    results['total_updates'] += sum(stats.values())
        
        # 2. 同步所有科室
        departments_dir = self.fm.data_dir / "departments"
        if departments_dir.exists():
            for dept_file in departments_dir.glob("*.json"):
                data = self.fm.read_json(dept_file)
                if data:
                    dept_id = data.get('department_id')
                    dept_name = data.get('name')
                    stats = self.sync_department_name_change(dept_id, dept_name)
                    results['departments_synced'] += 1
                    results['total_updates'] += sum(stats.values())
        
        # 3. 同步所有产品
        products_dir = self.fm.data_dir / "products"
        if products_dir.exists():
            for product_file in products_dir.glob("*.json"):
                data = self.fm.read_json(product_file)
                if data:
                    product_id = data.get('product_id')
                    product_name = data.get('name')
                    stats = self.sync_product_name_change(product_id, product_name)
                    results['products_synced'] += 1
                    results['total_updates'] += sum(stats.values())
        
        # 4. 同步所有医生
        doctors_dir = self.fm.data_dir / "doctors"
        if doctors_dir.exists():
            for doctor_file in doctors_dir.glob("*.json"):
                data = self.fm.read_json(doctor_file)
                if data:
                    doctor_id = data.get('doctor_id')
                    doctor_name = data.get('name')
                    stats = self.sync_doctor_name_change(doctor_id, doctor_name)
                    results['doctors_synced'] += 1
                    results['total_updates'] += sum(stats.values())
        
        return results
    
    # ==================== AI缓存失效 ====================
    
    def invalidate_ai_cache(self, entity_type: str, entity_id: str):
        """
        使AI分析缓存失效
        当数据更新时，相关的AI分析缓存应该失效
        """
        cache_dir = self.fm.data_dir / "ai_analysis_cache"
        if not cache_dir.exists():
            return
        
        # 删除相关的缓存文件
        pattern = f"{entity_type}_{entity_id}_*.json"
        for cache_file in cache_dir.glob(pattern):
            try:
                cache_file.unlink()
                print(f"已失效AI缓存: {cache_file.name}")
            except Exception as e:
                print(f"失效AI缓存失败: {e}")


# 创建全局实例
from core.file_manager import file_manager
data_sync_service = DataSyncService(file_manager)
