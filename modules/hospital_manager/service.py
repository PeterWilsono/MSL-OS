"""
医院管理服务
包括医院、科室、产品、竞品管理
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path
from core.file_manager import file_manager
from core.hospital_models import Hospital, Department, Product, Competitor


class HospitalService:
    """医院管理服务"""
    
    def __init__(self):
        self.fm = file_manager
        
        # 创建医院相关目录
        self.hospitals_dir = self.fm.data_dir / "hospitals"
        self.departments_dir = self.fm.data_dir / "departments"
        self.products_dir = self.fm.data_dir / "products"
        self.competitors_dir = self.fm.data_dir / "competitors"
        
        self.hospitals_dir.mkdir(parents=True, exist_ok=True)
        self.departments_dir.mkdir(parents=True, exist_ok=True)
        self.products_dir.mkdir(parents=True, exist_ok=True)
        self.competitors_dir.mkdir(parents=True, exist_ok=True)
    
    # ==================== 医院管理 ====================
    
    def create_hospital(
        self,
        name: str,
        level: str = "",
        address: str = "",
        contact_phone: str = "",
        notes: str = "",
        hospital_id: Optional[str] = None
    ) -> Hospital:
        """创建医院"""
        if not hospital_id:
            hospital_id = f"hospital_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        hospital = Hospital(
            hospital_id=hospital_id,
            name=name,
            level=level,
            address=address,
            contact_phone=contact_phone,
            notes=notes
        )
        
        self.fm.save_model(self.hospitals_dir, hospital, hospital_id)
        return hospital
    
    def get_hospital(self, hospital_id: str) -> Optional[Hospital]:
        """获取医院"""
        return self.fm.load_model(self.hospitals_dir, hospital_id, Hospital)
    
    def update_hospital(self, hospital_id: str, updates: Dict[str, Any]) -> Optional[Hospital]:
        """更新医院"""
        hospital_path = self.hospitals_dir / f"{hospital_id}.json"
        data = self.fm.read_json(hospital_path)
        
        if not data:
            return None
        
        # 检查名称是否变更
        name_changed = 'name' in updates and updates['name'] != data.get('name')
        old_name = data.get('name')
        
        # 更新字段（允许添加新字段）
        for key, value in updates.items():
            data[key] = value
        
        data["updated_at"] = datetime.now().isoformat()
        self.fm.write_json(hospital_path, data)
        
        # 如果名称变更，同步到所有相关数据
        if name_changed:
            from core.data_sync_service import data_sync_service
            stats = data_sync_service.sync_hospital_name_change(hospital_id, updates['name'])
            print(f"✓ 医院名称已同步: {old_name} -> {updates['name']}")
            print(f"  更新: 医生{stats['doctors']}条, 联系人{stats['contacts']}条, "
                  f"拜访{stats['visits']}条, 关联{stats['associations']}条")
            
            # 使AI缓存失效
            data_sync_service.invalidate_ai_cache('hospital', hospital_id)
        
        return Hospital(**data)
    
    def delete_hospital(self, hospital_id: str) -> bool:
        """删除医院"""
        # 级联删除：删除所有相关的产品关联记录
        try:
            from modules.product_association.service import ProductAssociationService
            assoc_service = ProductAssociationService()
            deleted_count = assoc_service.cascade_delete_by_hospital(hospital_id)
            if deleted_count > 0:
                print(f"级联删除了 {deleted_count} 条产品关联记录")
        except Exception as e:
            print(f"警告：级联删除产品关联记录失败：{e}")
        
        return self.fm.delete_file(self.hospitals_dir, hospital_id)
    
    def list_hospitals(self) -> List[Dict[str, Any]]:
        """列出所有医院"""
        hospitals = []
        for filename in self.fm.list_files(self.hospitals_dir):
            data = self.fm.read_json(self.hospitals_dir / f"{filename}.json")
            if data:
                hospitals.append(data)
        return sorted(hospitals, key=lambda x: x.get("name", ""))
    
    def search_hospitals(self, keyword: str) -> List[Dict[str, Any]]:
        """搜索医院"""
        results = self.fm.search_files(self.hospitals_dir, keyword)
        return [r["data"] for r in results]
    
    # ==================== 科室管理 ====================
    
    def create_department(
        self,
        name: str,
        hospital_id: str,
        description: str = "",
        head_doctor: str = "",
        notes: str = "",
        department_id: Optional[str] = None
    ) -> Department:
        """创建科室"""
        if not department_id:
            department_id = f"dept_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        department = Department(
            department_id=department_id,
            name=name,
            description=description,
            head_doctor=head_doctor,
            notes=notes
        )
        
        self.fm.save_model(self.departments_dir, department, department_id)
        
        # 更新医院的科室列表
        hospital = self.get_hospital(hospital_id)
        if hospital:
            if department_id not in hospital.departments:
                hospital.departments.append(department_id)
                self.update_hospital(hospital_id, {"departments": hospital.departments})
        
        return department
    
    def get_department(self, department_id: str) -> Optional[Department]:
        """获取科室"""
        return self.fm.load_model(self.departments_dir, department_id, Department)
    
    def update_department(self, department_id: str, updates: Dict[str, Any]) -> Optional[Department]:
        """更新科室"""
        dept_path = self.departments_dir / f"{department_id}.json"
        data = self.fm.read_json(dept_path)
        
        if not data:
            return None
        
        # 检查名称是否变更
        name_changed = 'name' in updates and updates['name'] != data.get('name')
        old_name = data.get('name')
        
        # 更新字段（允许添加新字段）
        for key, value in updates.items():
            data[key] = value
        
        data["updated_at"] = datetime.now().isoformat()
        self.fm.write_json(dept_path, data)
        
        # 如果名称变更，同步到所有相关数据
        if name_changed:
            from core.data_sync_service import data_sync_service
            stats = data_sync_service.sync_department_name_change(department_id, updates['name'])
            print(f"✓ 科室名称已同步: {old_name} -> {updates['name']}")
            print(f"  更新: 医生{stats['doctors']}条, 联系人{stats['contacts']}条, "
                  f"拜访{stats['visits']}条, 关联{stats['associations']}条")
            
            # 使AI缓存失效
            data_sync_service.invalidate_ai_cache('department', department_id)
        
        return Department(**data)
    
    def delete_department(self, department_id: str) -> bool:
        """删除科室"""
        # 级联删除：删除所有相关的产品关联记录
        try:
            from modules.product_association.service import ProductAssociationService
            assoc_service = ProductAssociationService()
            deleted_count = assoc_service.cascade_delete_by_department(department_id)
            if deleted_count > 0:
                print(f"级联删除了 {deleted_count} 条产品关联记录")
        except Exception as e:
            print(f"警告：级联删除产品关联记录失败：{e}")
        
        return self.fm.delete_file(self.departments_dir, department_id)
    
    def list_departments(self, hospital_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """列出科室"""
        departments = []
        for filename in self.fm.list_files(self.departments_dir):
            data = self.fm.read_json(self.departments_dir / f"{filename}.json")
            if data:
                departments.append(data)
        
        # 如果指定医院，筛选该医院的科室
        if hospital_id:
            hospital = self.get_hospital(hospital_id)
            if hospital:
                dept_ids = set(hospital.departments)
                departments = [d for d in departments if d.get("department_id") in dept_ids]
        
        return sorted(departments, key=lambda x: x.get("name", ""))
    
    # ==================== 产品管理 ====================
    
    def create_product(
        self,
        name: str,
        category: str = "",
        description: str = "",
        key_features: List[str] = None,
        indications: List[str] = None,
        notes: str = "",
        product_id: Optional[str] = None
    ) -> Product:
        """创建产品"""
        if not product_id:
            product_id = f"product_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        product = Product(
            product_id=product_id,
            name=name,
            category=category,
            description=description,
            key_features=key_features or [],
            indications=indications or [],
            notes=notes
        )
        
        self.fm.save_model(self.products_dir, product, product_id)
        return product
    
    def get_product(self, product_id: str) -> Optional[Product]:
        """获取产品"""
        return self.fm.load_model(self.products_dir, product_id, Product)
    
    def update_product(self, product_id: str, updates: Dict[str, Any]) -> Optional[Product]:
        """更新产品"""
        product_path = self.products_dir / f"{product_id}.json"
        data = self.fm.read_json(product_path)
        
        if not data:
            return None
        
        # 检查名称是否变更
        name_changed = 'name' in updates and updates['name'] != data.get('name')
        old_name = data.get('name')
        
        # 更新字段（允许添加新字段）
        for key, value in updates.items():
            data[key] = value
        
        data["updated_at"] = datetime.now().isoformat()
        self.fm.write_json(product_path, data)
        
        # 如果名称变更，同步到所有相关数据
        if name_changed:
            from core.data_sync_service import data_sync_service
            stats = data_sync_service.sync_product_name_change(product_id, updates['name'])
            print(f"✓ 产品名称已同步: {old_name} -> {updates['name']}")
            print(f"  更新: 关联{stats['associations']}条, 知识库{stats['knowledge']}条")
        
        return Product(**data)
    
    def delete_product(self, product_id: str) -> bool:
        """删除产品"""
        # 级联删除：删除所有相关的产品关联记录
        try:
            from modules.product_association.service import ProductAssociationService
            assoc_service = ProductAssociationService()
            deleted_count = assoc_service.cascade_delete_by_product(product_id)
            if deleted_count > 0:
                print(f"级联删除了 {deleted_count} 条产品关联记录")
        except Exception as e:
            print(f"警告：级联删除产品关联记录失败：{e}")
        
        return self.fm.delete_file(self.products_dir, product_id)
    
    def list_products(self) -> List[Dict[str, Any]]:
        """列出所有产品"""
        products = []
        for filename in self.fm.list_files(self.products_dir):
            data = self.fm.read_json(self.products_dir / f"{filename}.json")
            if data:
                products.append(data)
        return sorted(products, key=lambda x: x.get("name", ""))
    
    def search_products(self, keyword: str) -> List[Dict[str, Any]]:
        """搜索产品"""
        results = self.fm.search_files(self.products_dir, keyword)
        return [r["data"] for r in results]
    
    def add_product_attachment(
        self,
        product_id: str,
        filename: str,
        filepath: str,
        file_type: str
    ) -> bool:
        """为产品添加附件"""
        product = self.get_product(product_id)
        if not product:
            print(f"错误：产品 {product_id} 不存在")
            return False
        
        attachment = {
            "filename": filename,
            "filepath": filepath,
            "upload_time": datetime.now().isoformat(),
            "file_type": file_type
        }
        
        # 获取现有附件列表
        attachments = list(product.attachments) if product.attachments else []
        attachments.append(attachment)
        
        print(f"添加附件到产品 {product_id}: {filename}, 当前附件数: {len(attachments)}")
        
        result = self.update_product(product_id, {"attachments": attachments})
        return result is not None
    
    def remove_product_attachment(
        self,
        product_id: str,
        filepath: str
    ) -> bool:
        """删除产品附件"""
        product = self.get_product(product_id)
        if not product:
            return False
        
        # 获取现有附件列表
        attachments = list(product.attachments) if product.attachments else []
        attachments = [a for a in attachments if a.get("filepath") != filepath]
        
        # 删除文件
        try:
            from pathlib import Path
            Path(filepath).unlink(missing_ok=True)
            print(f"已删除文件: {filepath}")
        except Exception as e:
            print(f"删除文件失败: {e}")
        
        result = self.update_product(product_id, {"attachments": attachments})
        return result is not None
    
    def get_product_attachments(self, product_id: str) -> List[Dict[str, str]]:
        """获取产品的所有附件"""
        product = self.get_product(product_id)
        if not product:
            return []
        
        attachments = list(product.attachments) if product.attachments else []
        print(f"获取产品 {product_id} 的附件: {len(attachments)} 个")
        return attachments
    
    def sync_product_attachments(self, product_id: str) -> int:
        """同步产品附件目录中的文件到数据库"""
        from pathlib import Path
        
        product = self.get_product(product_id)
        if not product:
            return 0
        
        # 获取附件目录
        attachments_dir = Path('data/product_attachments') / product_id
        if not attachments_dir.exists():
            return 0
        
        # 获取现有附件记录
        existing_attachments = list(product.attachments) if product.attachments else []
        existing_paths = {a.get('filepath') for a in existing_attachments}
        
        # 扫描目录中的文件
        new_count = 0
        for file_path in attachments_dir.glob('*'):
            if file_path.is_file():
                filepath_str = str(file_path)
                
                # 如果文件未记录，添加到附件列表
                if filepath_str not in existing_paths:
                    file_type = file_path.suffix[1:] if file_path.suffix else 'unknown'
                    
                    attachment = {
                        "filename": file_path.name,
                        "filepath": filepath_str,
                        "upload_time": datetime.now().isoformat(),
                        "file_type": file_type
                    }
                    
                    existing_attachments.append(attachment)
                    new_count += 1
                    print(f"发现新文件: {file_path.name}")
        
        # 更新产品数据
        if new_count > 0:
            self.update_product(product_id, {"attachments": existing_attachments})
            print(f"同步完成: 添加了 {new_count} 个附件")
        
        return new_count
    
    def sync_all_product_attachments(self) -> Dict[str, int]:
        """同步所有产品的附件"""
        from pathlib import Path
        
        results = {}
        attachments_base = Path('data/product_attachments')
        
        if not attachments_base.exists():
            return results
        
        # 遍历所有产品目录
        for product_dir in attachments_base.iterdir():
            if product_dir.is_dir():
                product_id = product_dir.name
                
                # 检查产品是否存在
                product = self.get_product(product_id)
                if not product:
                    print(f"警告：产品 {product_id} 不存在，跳过同步")
                    print(f"  附件目录: {product_dir}")
                    print(f"  建议：请先创建产品或将文件移动到现有产品目录")
                    continue
                
                count = self.sync_product_attachments(product_id)
                if count > 0:
                    results[product_id] = count
        
        return results
    
    def list_orphan_attachment_dirs(self) -> List[Dict[str, Any]]:
        """列出没有对应产品的附件目录"""
        from pathlib import Path
        
        orphans = []
        attachments_base = Path('data/product_attachments')
        
        if not attachments_base.exists():
            return orphans
        
        for product_dir in attachments_base.iterdir():
            if product_dir.is_dir():
                product_id = product_dir.name
                product = self.get_product(product_id)
                
                if not product:
                    # 统计文件数量
                    files = list(product_dir.glob('*'))
                    file_count = len([f for f in files if f.is_file()])
                    
                    orphans.append({
                        'product_id': product_id,
                        'path': str(product_dir),
                        'file_count': file_count,
                        'files': [f.name for f in files if f.is_file()]
                    })
        
        return orphans
    
    # ==================== 竞品管理 ====================
    
    def create_competitor(
        self,
        name: str,
        manufacturer: str = "",
        advantages: str = "",
        disadvantages: str = "",
        market_share: str = "",
        notes: str = "",
        competitor_id: Optional[str] = None
    ) -> Competitor:
        """创建竞品"""
        if not competitor_id:
            competitor_id = f"competitor_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        competitor = Competitor(
            competitor_id=competitor_id,
            name=name,
            manufacturer=manufacturer,
            advantages=advantages,
            disadvantages=disadvantages,
            market_share=market_share,
            notes=notes
        )
        
        self.fm.save_model(self.competitors_dir, competitor, competitor_id)
        return competitor
    
    def get_competitor(self, competitor_id: str) -> Optional[Competitor]:
        """获取竞品"""
        return self.fm.load_model(self.competitors_dir, competitor_id, Competitor)
    
    def update_competitor(self, competitor_id: str, updates: Dict[str, Any]) -> Optional[Competitor]:
        """更新竞品"""
        comp_path = self.competitors_dir / f"{competitor_id}.json"
        data = self.fm.read_json(comp_path)
        
        if not data:
            return None
        
        # 更新字段（允许添加新字段）
        for key, value in updates.items():
            data[key] = value
        
        data["updated_at"] = datetime.now().isoformat()
        self.fm.write_json(comp_path, data)
        
        return Competitor(**data)
    
    def delete_competitor(self, competitor_id: str) -> bool:
        """删除竞品"""
        return self.fm.delete_file(self.competitors_dir, competitor_id)
    
    def list_competitors(self) -> List[Dict[str, Any]]:
        """列出所有竞品"""
        competitors = []
        for filename in self.fm.list_files(self.competitors_dir):
            data = self.fm.read_json(self.competitors_dir / f"{filename}.json")
            if data:
                competitors.append(data)
        return sorted(competitors, key=lambda x: x.get("name", ""))
    
    def search_competitors(self, keyword: str) -> List[Dict[str, Any]]:
        """搜索竞品"""
        results = self.fm.search_files(self.competitors_dir, keyword)
        return [r["data"] for r in results]


# 创建全局实例
hospital_service = HospitalService()
