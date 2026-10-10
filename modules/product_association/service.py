"""
产品关联管理服务

本模块提供产品与医院科室关联关系的核心业务逻辑。

主要功能：
    1. 关联记录管理
        - 创建产品与医院科室的关联记录
        - 删除关联记录
        - 获取单个关联记录详情
        
    2. 查询功能
        - 按产品查询：查询某个产品在哪些医院科室中使用
        - 按医院查询：查询某个医院使用了哪些产品
        - 按科室查询：查询某个科室使用了哪些产品
        
    3. 批量操作
        - 批量创建关联记录，支持跳过重复记录
        - 批量删除关联记录
        
    4. 筛选和搜索
        - 多条件组合筛选（产品、医院、科室、时间范围）
        - 关键词搜索（在产品、医院、科室名称中搜索）
        
    5. 数据完整性
        - 检查并标记失效的关联记录
        - 级联删除：删除产品/医院/科室时自动删除相关关联记录
        
    6. 统计分析
        - 计算产品、医院、科室的关联数量统计
        - 支持按时间范围筛选统计数据
        
    7. 数据导出
        - 导出为 CSV 格式
        - 导出为 Excel 格式
        - 支持按筛选条件导出

数据存储结构：
    - 关联记录存储在 data/associations/ 目录下
    - 每条记录一个 JSON 文件，文件名为 {association_id}.json
    - 维护四个索引文件以提高查询效率：
        * product_index.json: 产品ID → 关联记录ID列表
        * hospital_index.json: 医院ID → 关联记录ID列表
        * department_index.json: 科室ID → 关联记录ID列表
        * unique_index.json: 唯一性索引，防止重复记录

设计原则：
    - 使用索引文件加速查询操作
    - 冗余存储名称字段，减少关联查询
    - 提供清晰的错误提示和日志记录
    - 支持事务性批量操作

作者：医药信息专员系统开发团队
版本：1.0.0
"""
import os
import json
from datetime import datetime
from typing import List, Optional, Dict, Any
from pathlib import Path

from core.hospital_models import (
    ProductAssociation,
    AssociationQuery,
    AssociationStatistics,
    BatchOperationResult
)
from core.file_manager import FileManager


class ProductAssociationService:
    """
    产品关联管理服务类
    
    提供产品与医院科室关联关系的完整管理功能，包括创建、查询、删除、
    批量操作、数据完整性检查、统计分析和数据导出。
    
    属性：
        data_dir (str): 数据根目录路径
        associations_dir (str): 关联记录存储目录路径
        file_manager (FileManager): 文件管理器实例
        product_index_path (str): 产品索引文件路径
        hospital_index_path (str): 医院索引文件路径
        department_index_path (str): 科室索引文件路径
        unique_index_path (str): 唯一性索引文件路径
    
    使用示例：
        >>> service = ProductAssociationService()
        >>> 
        >>> # 创建关联记录
        >>> association = service.create_association(
        ...     product_id="prod_001",
        ...     hospital_id="hosp_001",
        ...     department_id="dept_001",
        ...     notes="该产品在心内科广泛使用"
        ... )
        >>> 
        >>> # 查询产品使用情况
        >>> result = service.query_by_product("prod_001")
        >>> for assoc in result.associations:
        ...     print(f"{assoc.hospital_name} - {assoc.department_name}")
    
    注意事项：
        - 所有ID必须在对应的实体（产品、医院、科室）中存在
        - 不允许创建重复的关联记录（相同的产品、医院、科室组合）
        - 删除操作会自动更新所有相关的索引文件
        - 批量操作遇到错误时会继续处理其他记录
    """
    
    def __init__(self, data_dir: str = "data"):
        """
        初始化产品关联管理服务
        
        创建必要的目录结构和索引文件，为关联记录管理做好准备。
        
        参数：
            data_dir (str): 数据根目录路径，默认为 "data"
                           关联记录将存储在 {data_dir}/associations/ 目录下
        
        初始化过程：
            1. 设置数据目录和关联记录目录路径
            2. 初始化文件管理器
            3. 设置四个索引文件的路径
            4. 调用 _initialize() 创建目录和索引文件
        
        注意：
            - 如果目录或索引文件已存在，不会覆盖
            - 索引文件初始化为空的 JSON 对象 {}
        """
        self.data_dir = data_dir
        self.associations_dir = os.path.join(data_dir, "associations")
        self.file_manager = FileManager()
        
        # 索引文件路径
        self.product_index_path = os.path.join(self.associations_dir, "product_index.json")
        self.hospital_index_path = os.path.join(self.associations_dir, "hospital_index.json")
        self.department_index_path = os.path.join(self.associations_dir, "department_index.json")
        self.unique_index_path = os.path.join(self.associations_dir, "unique_index.json")
        
        # 初始化目录和索引
        self._initialize()
    
    def _initialize(self):
        """
        初始化数据目录和索引文件
        
        创建关联记录存储目录和四个索引文件（如果不存在）。
        索引文件用于加速查询操作，避免遍历所有关联记录文件。
        
        创建的索引文件：
            - product_index.json: 产品ID到关联记录ID列表的映射
            - hospital_index.json: 医院ID到关联记录ID列表的映射
            - department_index.json: 科室ID到关联记录ID列表的映射
            - unique_index.json: 唯一性约束索引，格式为 "产品ID:医院ID:科室ID" → 关联记录ID
        
        注意：
            - 使用 exist_ok=True，如果目录已存在不会报错
            - 索引文件初始化为空的 JSON 对象 {}
            - 使用 UTF-8 编码确保中文字符正确存储
        """
        # 创建关联记录目录
        os.makedirs(self.associations_dir, exist_ok=True)
        
        # 初始化索引文件（如果不存在）
        for index_path in [
            self.product_index_path,
            self.hospital_index_path,
            self.department_index_path,
            self.unique_index_path
        ]:
            if not os.path.exists(index_path):
                with open(index_path, 'w', encoding='utf-8') as f:
                    json.dump({}, f, ensure_ascii=False, indent=2)
    
    def _load_index(self, index_path: str) -> Dict[str, Any]:
        """
        加载索引文件
        
        从指定路径读取索引文件内容，返回索引数据字典。
        如果文件不存在或读取失败，返回空字典。
        
        参数：
            index_path (str): 索引文件的完整路径
        
        返回：
            Dict[str, Any]: 索引数据字典，键为ID，值为关联记录ID列表或关联记录ID
        
        异常处理：
            - 如果文件不存在或读取失败，捕获异常并返回空字典 {}
            - 不会抛出异常，确保程序的健壮性
        
        注意：
            - 使用 UTF-8 编码读取文件
            - 这是一个内部方法，不应被外部直接调用
        """
        try:
            with open(index_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}
    
    def _save_index(self, index_path: str, index_data: Dict[str, Any]):
        """
        保存索引文件
        
        将索引数据字典写入指定的索引文件。
        使用格式化的 JSON 格式（缩进2个空格），便于人工查看和调试。
        
        参数：
            index_path (str): 索引文件的完整路径
            index_data (Dict[str, Any]): 要保存的索引数据字典
        
        文件格式：
            - 使用 UTF-8 编码，支持中文字符
            - ensure_ascii=False 确保中文字符不被转义
            - indent=2 使 JSON 格式化，便于阅读
        
        注意：
            - 这是一个内部方法，不应被外部直接调用
            - 写入操作会覆盖原有文件内容
            - 调用者需要确保 index_data 的格式正确
        """
        with open(index_path, 'w', encoding='utf-8') as f:
            json.dump(index_data, f, ensure_ascii=False, indent=2)
    
    def create_association(
        self,
        product_id: str,
        hospital_id: str,
        department_id: str,
        notes: str = ""
    ) -> Optional[ProductAssociation]:
        """
        创建产品关联记录

        创建一条新的产品与医院科室关联记录，记录产品在特定医院特定科室的使用情况。
        
        验证规则：
            - 产品ID、医院ID、科室ID 必须在对应的实体中存在
            - 不允许创建重复的关联记录（相同的产品、医院、科室组合）
            - 所有ID必须为非空字符串

        参数：
            product_id (str): 产品ID，必须是已存在的产品
            hospital_id (str): 医院ID，必须是已存在的医院
            department_id (str): 科室ID，必须是已存在的科室
            notes (str, optional): 备注信息，默认为空字符串

        返回：
            Optional[ProductAssociation]: 
                - 成功：返回创建的 ProductAssociation 对象
                - 失败：返回 None，并在控制台输出错误信息

        创建流程：
            1. 验证产品ID、医院ID、科室ID的有效性（调用 hospital_service）
            2. 检查唯一性约束（使用 unique_index）
            3. 生成唯一的关联记录ID（格式：assoc_YYYYMMDDHHMMSSffffff）
            4. 创建 ProductAssociation 对象，填充所有字段
            5. 保存关联记录到 JSON 文件
            6. 更新所有索引文件（product_index, hospital_index, department_index, unique_index）

        错误处理：
            - 如果产品ID不存在，输出错误信息并返回 None
            - 如果医院ID不存在，输出错误信息并返回 None
            - 如果科室ID不存在，输出错误信息并返回 None
            - 如果关联记录已存在，输出错误信息并返回 None

        使用示例：
            >>> service = ProductAssociationService()
            >>> association = service.create_association(
            ...     product_id="prod_001",
            ...     hospital_id="hosp_001",
            ...     department_id="dept_001",
            ...     notes="该产品在心内科广泛使用"
            ... )
            >>> if association:
            ...     print(f"创建成功：{association.association_id}")
            ... else:
            ...     print("创建失败")

        注意事项：
            - 创建时会自动填充产品名称、医院名称、科室名称（冗余字段）
            - 创建时间和更新时间会自动设置为当前时间
            - is_active 字段默认设置为 True
            - 索引文件会在创建成功后立即更新
        """
        # 导入 hospital_service
        from modules.hospital_manager.service import hospital_service

        # 1. 验证产品ID、医院ID、科室ID的有效性
        product = hospital_service.get_product(product_id)
        if not product:
            print(f"错误：产品ID '{product_id}' 不存在")
            return None

        hospital = hospital_service.get_hospital(hospital_id)
        if not hospital:
            print(f"错误：医院ID '{hospital_id}' 不存在")
            return None

        department = hospital_service.get_department(department_id)
        if not department:
            print(f"错误：科室ID '{department_id}' 不存在")
            return None

        # 2. 检查唯一性约束
        unique_key = f"{product_id}:{hospital_id}:{department_id}"
        unique_index = self._load_index(self.unique_index_path)

        if unique_key in unique_index:
            print(f"错误：关联记录已存在（产品：{product_id}，医院：{hospital_id}，科室：{department_id}）")
            return None

        # 3. 创建关联记录
        association_id = f"assoc_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        now = datetime.now()

        association = ProductAssociation(
            association_id=association_id,
            product_id=product_id,
            hospital_id=hospital_id,
            department_id=department_id,
            product_name=product.name,
            hospital_name=hospital.name,
            department_name=department.name,
            notes=notes,
            created_at=now,
            updated_at=now,
            is_active=True
        )

        # 4. 保存关联记录到 JSON 文件
        association_path = os.path.join(self.associations_dir, f"{association_id}.json")
        with open(association_path, 'w', encoding='utf-8') as f:
            json.dump(association.model_dump(mode='json'), f, ensure_ascii=False, indent=2, default=str)

        # 5. 更新所有索引文件
        # 更新 product_index
        product_index = self._load_index(self.product_index_path)
        if product_id not in product_index:
            product_index[product_id] = []
        product_index[product_id].append(association_id)
        self._save_index(self.product_index_path, product_index)

        # 更新 hospital_index
        hospital_index = self._load_index(self.hospital_index_path)
        if hospital_id not in hospital_index:
            hospital_index[hospital_id] = []
        hospital_index[hospital_id].append(association_id)
        self._save_index(self.hospital_index_path, hospital_index)

        # 更新 department_index
        department_index = self._load_index(self.department_index_path)
        if department_id not in department_index:
            department_index[department_id] = []
        department_index[department_id].append(association_id)
        self._save_index(self.department_index_path, department_index)

        # 更新 unique_index
        unique_index[unique_key] = association_id
        self._save_index(self.unique_index_path, unique_index)

        return association

    
    def get_association(self, association_id: str) -> Optional[ProductAssociation]:
        """
        获取单个关联记录
        
        根据关联记录ID从文件系统加载并返回关联记录对象。
        
        参数：
            association_id (str): 关联记录的唯一标识符
        
        返回：
            Optional[ProductAssociation]: 
                - 成功：返回 ProductAssociation 对象
                - 失败：返回 None（记录不存在或加载失败）
        
        加载流程：
            1. 构造关联记录文件路径：{associations_dir}/{association_id}.json
            2. 检查文件是否存在
            3. 读取 JSON 文件内容
            4. 解析为 ProductAssociation 对象
        
        错误处理：
            - 如果文件不存在，返回 None
            - 如果文件读取或解析失败，输出错误信息并返回 None
        
        使用示例：
            >>> service = ProductAssociationService()
            >>> association = service.get_association("assoc_20240115120000")
            >>> if association:
            ...     print(f"产品：{association.product_name}")
            ...     print(f"医院：{association.hospital_name}")
            ...     print(f"科室：{association.department_name}")
            ... else:
            ...     print("关联记录不存在")
        
        注意：
            - 使用 UTF-8 编码读取文件
            - 返回的对象包含所有字段，包括冗余的名称字段
        """
        association_path = os.path.join(self.associations_dir, f"{association_id}.json")
        
        if not os.path.exists(association_path):
            return None
        
        try:
            with open(association_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return ProductAssociation(**data)
        except Exception as e:
            print(f"错误：加载关联记录 {association_id} 失败：{e}")
            return None
    
    def delete_association(self, association_id: str) -> bool:
        """
        删除关联记录
        
        从文件系统删除指定的关联记录，并更新所有相关的索引文件。
        
        参数：
            association_id (str): 要删除的关联记录ID
        
        返回：
            bool: 
                - True：删除成功
                - False：记录不存在或删除失败
        
        删除流程：
            1. 检查关联记录文件是否存在
            2. 加载关联记录以获取索引信息（产品ID、医院ID、科室ID）
            3. 从文件系统删除关联记录文件
            4. 更新 product_index（移除该关联记录ID）
            5. 更新 hospital_index（移除该关联记录ID）
            6. 更新 department_index（移除该关联记录ID）
            7. 更新 unique_index（删除唯一性约束条目）
        
        错误处理：
            - 如果记录不存在，输出错误信息并返回 False
            - 如果删除过程中发生异常，输出错误信息并返回 False
        
        使用示例：
            >>> service = ProductAssociationService()
            >>> success = service.delete_association("assoc_20240115120000")
            >>> if success:
            ...     print("删除成功")
            ... else:
            ...     print("删除失败，记录可能不存在")
        
        注意事项：
            - 删除操作不可恢复，请谨慎使用
            - 如果索引中的列表为空，会自动删除该键
            - 所有索引文件会在删除成功后立即更新
            - 此方法不会检查引用完整性，如需级联删除请使用 cascade_delete_* 方法
        """
        # 1. 检查记录是否存在
        association_path = os.path.join(self.associations_dir, f"{association_id}.json")
        
        if not os.path.exists(association_path):
            print(f"错误：关联记录 '{association_id}' 不存在")
            return False
        
        try:
            # 2. 加载关联记录以获取索引信息
            with open(association_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                association = ProductAssociation(**data)
            
            # 3. 从文件系统删除关联记录文件
            os.remove(association_path)
            
            # 4. 更新所有索引文件（移除相关条目）
            # 更新 product_index
            product_index = self._load_index(self.product_index_path)
            if association.product_id in product_index:
                if association_id in product_index[association.product_id]:
                    product_index[association.product_id].remove(association_id)
                    # 如果列表为空，删除该键
                    if not product_index[association.product_id]:
                        del product_index[association.product_id]
                self._save_index(self.product_index_path, product_index)
            
            # 更新 hospital_index
            hospital_index = self._load_index(self.hospital_index_path)
            if association.hospital_id in hospital_index:
                if association_id in hospital_index[association.hospital_id]:
                    hospital_index[association.hospital_id].remove(association_id)
                    # 如果列表为空，删除该键
                    if not hospital_index[association.hospital_id]:
                        del hospital_index[association.hospital_id]
                self._save_index(self.hospital_index_path, hospital_index)
            
            # 更新 department_index
            department_index = self._load_index(self.department_index_path)
            if association.department_id in department_index:
                if association_id in department_index[association.department_id]:
                    department_index[association.department_id].remove(association_id)
                    # 如果列表为空，删除该键
                    if not department_index[association.department_id]:
                        del department_index[association.department_id]
                self._save_index(self.department_index_path, department_index)
            
            # 更新 unique_index
            unique_key = f"{association.product_id}:{association.hospital_id}:{association.department_id}"
            unique_index = self._load_index(self.unique_index_path)
            if unique_key in unique_index:
                del unique_index[unique_key]
                self._save_index(self.unique_index_path, unique_index)
            
            return True
            
        except Exception as e:
            print(f"错误：删除关联记录 {association_id} 失败：{e}")
            return False
    
    def update_association(
        self,
        association_id: str,
        product_id: str,
        hospital_id: str,
        department_id: str,
        notes: str = ""
    ) -> bool:
        """
        更新关联记录
        
        更新指定的关联记录，可以修改产品、医院、科室和备注信息。
        
        参数：
            association_id (str): 要更新的关联记录ID
            product_id (str): 新的产品ID
            hospital_id (str): 新的医院ID
            department_id (str): 新的科室ID
            notes (str, optional): 新的备注信息
        
        返回：
            bool: 
                - True：更新成功
                - False：记录不存在或更新失败
        
        更新流程：
            1. 检查关联记录是否存在
            2. 验证新的产品ID、医院ID、科室ID的有效性
            3. 检查新的组合是否与其他记录重复
            4. 从旧索引中移除记录
            5. 更新关联记录数据
            6. 保存更新后的记录
            7. 添加到新索引中
        """
        # 导入 hospital_service
        from modules.hospital_manager.service import hospital_service
        
        # 1. 检查记录是否存在
        association_path = os.path.join(self.associations_dir, f"{association_id}.json")
        
        if not os.path.exists(association_path):
            print(f"错误：关联记录 '{association_id}' 不存在")
            return False
        
        try:
            # 2. 加载现有记录
            with open(association_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                old_association = ProductAssociation(**data)
            
            # 3. 验证新的产品ID、医院ID、科室ID的有效性
            product = hospital_service.get_product(product_id)
            if not product:
                print(f"错误：产品ID '{product_id}' 不存在")
                return False
            
            hospital = hospital_service.get_hospital(hospital_id)
            if not hospital:
                print(f"错误：医院ID '{hospital_id}' 不存在")
                return False
            
            department = hospital_service.get_department(department_id)
            if not department:
                print(f"错误：科室ID '{department_id}' 不存在")
                return False
            
            # 4. 检查唯一性约束（如果组合发生变化）
            new_unique_key = f"{product_id}:{hospital_id}:{department_id}"
            old_unique_key = f"{old_association.product_id}:{old_association.hospital_id}:{old_association.department_id}"
            
            if new_unique_key != old_unique_key:
                unique_index = self._load_index(self.unique_index_path)
                if new_unique_key in unique_index:
                    print(f"错误：关联记录已存在（产品：{product_id}，医院：{hospital_id}，科室：{department_id}）")
                    return False
            
            # 5. 从旧索引中移除记录
            # 更新 product_index
            if old_association.product_id != product_id:
                product_index = self._load_index(self.product_index_path)
                if old_association.product_id in product_index:
                    if association_id in product_index[old_association.product_id]:
                        product_index[old_association.product_id].remove(association_id)
                        if not product_index[old_association.product_id]:
                            del product_index[old_association.product_id]
                    self._save_index(self.product_index_path, product_index)
            
            # 更新 hospital_index
            if old_association.hospital_id != hospital_id:
                hospital_index = self._load_index(self.hospital_index_path)
                if old_association.hospital_id in hospital_index:
                    if association_id in hospital_index[old_association.hospital_id]:
                        hospital_index[old_association.hospital_id].remove(association_id)
                        if not hospital_index[old_association.hospital_id]:
                            del hospital_index[old_association.hospital_id]
                    self._save_index(self.hospital_index_path, hospital_index)
            
            # 更新 department_index
            if old_association.department_id != department_id:
                department_index = self._load_index(self.department_index_path)
                if old_association.department_id in department_index:
                    if association_id in department_index[old_association.department_id]:
                        department_index[old_association.department_id].remove(association_id)
                        if not department_index[old_association.department_id]:
                            del department_index[old_association.department_id]
                    self._save_index(self.department_index_path, department_index)
            
            # 6. 更新关联记录数据
            updated_association = ProductAssociation(
                association_id=association_id,
                product_id=product_id,
                hospital_id=hospital_id,
                department_id=department_id,
                product_name=product.name,
                hospital_name=hospital.name,
                department_name=department.name,
                notes=notes,
                created_at=old_association.created_at,
                updated_at=datetime.now(),
                is_active=True
            )
            
            # 7. 保存更新后的记录
            with open(association_path, 'w', encoding='utf-8') as f:
                json.dump(updated_association.model_dump(mode='json'), f, ensure_ascii=False, indent=2, default=str)
            
            # 8. 添加到新索引中
            # 更新 product_index
            if old_association.product_id != product_id:
                product_index = self._load_index(self.product_index_path)
                if product_id not in product_index:
                    product_index[product_id] = []
                product_index[product_id].append(association_id)
                self._save_index(self.product_index_path, product_index)
            
            # 更新 hospital_index
            if old_association.hospital_id != hospital_id:
                hospital_index = self._load_index(self.hospital_index_path)
                if hospital_id not in hospital_index:
                    hospital_index[hospital_id] = []
                hospital_index[hospital_id].append(association_id)
                self._save_index(self.hospital_index_path, hospital_index)
            
            # 更新 department_index
            if old_association.department_id != department_id:
                department_index = self._load_index(self.department_index_path)
                if department_id not in department_index:
                    department_index[department_id] = []
                department_index[department_id].append(association_id)
                self._save_index(self.department_index_path, department_index)
            
            # 更新 unique_index
            if new_unique_key != old_unique_key:
                unique_index = self._load_index(self.unique_index_path)
                if old_unique_key in unique_index:
                    del unique_index[old_unique_key]
                unique_index[new_unique_key] = association_id
                self._save_index(self.unique_index_path, unique_index)
            
            return True
            
        except Exception as e:
            print(f"错误：更新关联记录 {association_id} 失败：{e}")
            return False
    
    def query_by_product(self, product_id: str) -> AssociationQuery:
        """
        查询产品的使用情况
        
        查询指定产品在哪些医院的哪些科室中使用，返回所有相关的关联记录。
        
        参数：
            product_id (str): 产品ID
        
        返回：
            AssociationQuery: 查询结果对象，包含：
                - associations: 关联记录列表，按医院名称和科室名称排序
                - total_count: 关联记录总数
                - query_type: 查询类型，固定为 "by_product"
        
        查询流程：
            1. 使用 product_index 快速查找该产品的所有关联记录ID
            2. 如果产品没有关联记录，返回空结果
            3. 遍历关联记录ID列表，加载每条关联记录
            4. 按医院名称和科室名称排序结果
            5. 封装为 AssociationQuery 对象返回
        
        排序规则：
            - 首先按医院名称排序（字母顺序）
            - 医院名称相同时，按科室名称排序（字母顺序）
        
        错误处理：
            - 如果产品不存在或没有关联记录，返回空列表（不报错）
            - 如果某个关联记录文件加载失败，输出警告并跳过该记录
        
        使用示例：
            >>> service = ProductAssociationService()
            >>> result = service.query_by_product("prod_001")
            >>> print(f"产品在 {result.total_count} 个科室中使用")
            >>> for assoc in result.associations:
            ...     print(f"  - {assoc.hospital_name} / {assoc.department_name}")
        
        性能优化：
            - 使用索引文件避免遍历所有关联记录
            - 只加载需要的关联记录文件
        """
        # 1. 使用 product_index 快速查找关联记录ID
        product_index = self._load_index(self.product_index_path)
        association_ids = product_index.get(product_id, [])
        
        # 2. 处理产品不存在的情况（返回空列表）
        if not association_ids:
            return AssociationQuery(
                associations=[],
                total_count=0,
                query_type="by_product"
            )
        
        # 3. 加载所有关联记录
        associations = []
        for association_id in association_ids:
            association_path = os.path.join(self.associations_dir, f"{association_id}.json")
            if os.path.exists(association_path):
                try:
                    with open(association_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        association = ProductAssociation(**data)
                        associations.append(association)
                except Exception as e:
                    print(f"警告：加载关联记录 {association_id} 失败：{e}")
        
        # 4. 按医院名称和科室名称排序结果
        associations.sort(key=lambda x: (x.hospital_name, x.department_name))
        
        return AssociationQuery(
            associations=associations,
            total_count=len(associations),
            query_type="by_product"
        )
    
    def query_by_hospital(
        self,
        hospital_id: str,
        department_id: Optional[str] = None
    ) -> AssociationQuery:
        """
        查询医院或科室的产品使用情况
        
        支持两种查询模式：
        1. 只提供医院ID：查询该医院所有科室使用的产品
        2. 同时提供医院ID和科室ID：查询特定科室使用的产品
        
        参数：
            hospital_id (str): 医院ID，必填
            department_id (Optional[str]): 科室ID，可选
                - 如果提供，则只查询该科室的产品
                - 如果不提供，则查询医院所有科室的产品
        
        返回：
            AssociationQuery: 查询结果对象，包含：
                - associations: 关联记录列表，按产品名称排序
                - total_count: 关联记录总数
                - query_type: 查询类型
                    * "by_hospital": 按医院查询
                    * "by_department": 按科室查询
        
        查询流程（按医院查询）：
            1. 使用 hospital_index 快速查找该医院的所有关联记录ID
            2. 加载所有关联记录
            3. 按产品名称排序
        
        查询流程（按科室查询）：
            1. 使用 department_index 快速查找该科室的所有关联记录ID
            2. 加载关联记录并过滤出属于指定医院的记录
            3. 按产品名称排序
        
        排序规则：
            - 按产品名称排序（字母顺序）
        
        错误处理：
            - 如果医院或科室不存在或没有关联记录，返回空列表（不报错）
            - 如果某个关联记录文件加载失败，输出警告并跳过该记录
        
        使用示例：
            >>> service = ProductAssociationService()
            >>> 
            >>> # 查询医院所有科室的产品
            >>> result = service.query_by_hospital("hosp_001")
            >>> print(f"医院使用了 {result.total_count} 个产品")
            >>> 
            >>> # 查询特定科室的产品
            >>> result = service.query_by_hospital("hosp_001", "dept_001")
            >>> print(f"科室使用了 {result.total_count} 个产品")
            >>> for assoc in result.associations:
            ...     print(f"  - {assoc.product_name}")
        
        性能优化：
            - 使用索引文件避免遍历所有关联记录
            - 按科室查询时需要额外过滤医院ID
        """
        associations = []
        
        if department_id:
            # 按医院和科室组合查询（返回特定科室的产品）
            # 使用 department_index 快速查找
            department_index = self._load_index(self.department_index_path)
            association_ids = department_index.get(department_id, [])
            
            # 加载关联记录并过滤出属于指定医院的记录
            for association_id in association_ids:
                association_path = os.path.join(self.associations_dir, f"{association_id}.json")
                if os.path.exists(association_path):
                    try:
                        with open(association_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            association = ProductAssociation(**data)
                            # 只保留属于指定医院的记录
                            if association.hospital_id == hospital_id:
                                associations.append(association)
                    except Exception as e:
                        print(f"警告：加载关联记录 {association_id} 失败：{e}")
        else:
            # 只按医院查询（返回该医院所有科室的产品）
            # 使用 hospital_index 快速查找
            hospital_index = self._load_index(self.hospital_index_path)
            association_ids = hospital_index.get(hospital_id, [])
            
            # 加载所有关联记录
            for association_id in association_ids:
                association_path = os.path.join(self.associations_dir, f"{association_id}.json")
                if os.path.exists(association_path):
                    try:
                        with open(association_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            association = ProductAssociation(**data)
                            associations.append(association)
                    except Exception as e:
                        print(f"警告：加载关联记录 {association_id} 失败：{e}")
        
        # 按产品名称排序结果
        associations.sort(key=lambda x: x.product_name)
        
        return AssociationQuery(
            associations=associations,
            total_count=len(associations),
            query_type="by_hospital" if not department_id else "by_department"
        )
    
    def batch_create(
        self,
        associations: List[Dict[str, str]]
    ) -> BatchOperationResult:
        """
        批量创建关联记录
        
        批量创建多条产品与医院科室的关联记录，支持智能错误处理。
        遇到重复记录时跳过，遇到无效ID时记录错误，但继续处理其他记录。
        
        参数：
            associations (List[Dict[str, str]]): 关联记录列表，每个元素是一个字典，包含：
                - product_id (str): 产品ID，必填
                - hospital_id (str): 医院ID，必填
                - department_id (str): 科室ID，必填
                - notes (str): 备注，可选
        
        返回：
            BatchOperationResult: 批量操作结果对象，包含：
                - success_count (int): 成功创建的记录数量
                - failed_count (int): 失败的记录数量（无效ID）
                - skipped_count (int): 跳过的记录数量（重复记录）
                - error_messages (List[str]): 详细的错误信息列表
        
        处理逻辑：
            1. 遍历输入列表，逐个创建关联记录
            2. 调用 create_association() 尝试创建
            3. 如果创建成功，success_count +1
            4. 如果创建失败：
                - 检查是否是重复记录（在 unique_index 中存在）
                - 如果是重复记录，skipped_count +1
                - 如果是无效ID，failed_count +1，并记录错误信息
            5. 如果发生异常，failed_count +1，并记录错误信息
        
        错误处理：
            - 遇到重复记录时跳过并继续处理
            - 遇到无效ID时记录错误并继续处理
            - 遇到异常时记录错误并继续处理
            - 不会因为单个记录失败而中断整个批量操作
        
        使用示例：
            >>> service = ProductAssociationService()
            >>> associations = [
            ...     {"product_id": "prod_001", "hospital_id": "hosp_001", "department_id": "dept_001"},
            ...     {"product_id": "prod_001", "hospital_id": "hosp_002", "department_id": "dept_002"},
            ...     {"product_id": "prod_002", "hospital_id": "hosp_001", "department_id": "dept_001"}
            ... ]
            >>> result = service.batch_create(associations)
            >>> print(f"成功：{result.success_count}，失败：{result.failed_count}，跳过：{result.skipped_count}")
            >>> for error in result.error_messages:
            ...     print(f"  错误：{error}")
        
        注意事项：
            - 批量操作不是原子性的，部分成功的记录会被保留
            - 建议在批量操作前先验证数据的有效性
            - 错误信息列表包含所有失败记录的详细信息
        """
        result = BatchOperationResult(
            success_count=0,
            failed_count=0,
            skipped_count=0,
            error_messages=[]
        )
        
        # 遍历输入列表，逐个创建关联记录
        for assoc_data in associations:
            try:
                product_id = assoc_data.get('product_id', '')
                hospital_id = assoc_data.get('hospital_id', '')
                department_id = assoc_data.get('department_id', '')
                notes = assoc_data.get('notes', '')
                
                # 尝试创建关联记录
                association = self.create_association(
                    product_id=product_id,
                    hospital_id=hospital_id,
                    department_id=department_id,
                    notes=notes
                )
                
                if association:
                    # 成功创建
                    result.success_count += 1
                else:
                    # 创建失败，需要判断是重复还是无效ID
                    # 检查是否是重复记录
                    unique_key = f"{product_id}:{hospital_id}:{department_id}"
                    unique_index = self._load_index(self.unique_index_path)
                    
                    if unique_key in unique_index:
                        # 重复记录，跳过
                        result.skipped_count += 1
                    else:
                        # 无效ID，记录错误
                        result.failed_count += 1
                        error_msg = f"无效的ID组合：产品={product_id}, 医院={hospital_id}, 科室={department_id}"
                        result.error_messages.append(error_msg)
                        
            except Exception as e:
                # 遇到异常，记录错误
                result.failed_count += 1
                error_msg = f"创建关联记录失败：{str(e)}"
                result.error_messages.append(error_msg)
        
        return result
    
    def batch_delete(self, association_ids: List[str]) -> BatchOperationResult:
        """
        批量删除关联记录
        
        批量删除多条关联记录，支持智能错误处理。
        遇到不存在的记录时记录错误，但继续处理其他记录。
        
        参数：
            association_ids (List[str]): 要删除的关联记录ID列表
        
        返回：
            BatchOperationResult: 批量操作结果对象，包含：
                - success_count (int): 成功删除的记录数量
                - failed_count (int): 失败的记录数量（记录不存在或删除失败）
                - skipped_count (int): 跳过的记录数量（本方法中始终为0）
                - error_messages (List[str]): 详细的错误信息列表
        
        处理逻辑：
            1. 遍历关联记录ID列表，逐个删除
            2. 调用 delete_association() 尝试删除
            3. 如果删除成功，success_count +1
            4. 如果删除失败（记录不存在），failed_count +1，并记录错误信息
            5. 如果发生异常，failed_count +1，并记录错误信息
        
        错误处理：
            - 遇到不存在的记录时记录错误并继续处理
            - 遇到异常时记录错误并继续处理
            - 不会因为单个记录失败而中断整个批量操作
        
        使用示例：
            >>> service = ProductAssociationService()
            >>> association_ids = ["assoc_001", "assoc_002", "assoc_003"]
            >>> result = service.batch_delete(association_ids)
            >>> print(f"成功删除：{result.success_count}，失败：{result.failed_count}")
            >>> for error in result.error_messages:
            ...     print(f"  错误：{error}")
        
        注意事项：
            - 批量删除操作不可恢复，请谨慎使用
            - 批量操作不是原子性的，部分成功的删除会被保留
            - 建议在批量删除前先确认要删除的记录ID是否正确
            - 所有索引文件会在每次删除成功后立即更新
        """
        result = BatchOperationResult(
            success_count=0,
            failed_count=0,
            skipped_count=0,
            error_messages=[]
        )
        
        # 遍历关联记录ID列表，逐个删除
        for association_id in association_ids:
            try:
                # 尝试删除关联记录
                if self.delete_association(association_id):
                    # 删除成功
                    result.success_count += 1
                else:
                    # 删除失败（记录不存在）
                    result.failed_count += 1
                    error_msg = f"关联记录不存在：{association_id}"
                    result.error_messages.append(error_msg)
                    
            except Exception as e:
                # 遇到异常，记录错误
                result.failed_count += 1
                error_msg = f"删除关联记录 {association_id} 失败：{str(e)}"
                result.error_messages.append(error_msg)
        
        return result
    
    def filter_associations(
        self,
        product_id: Optional[str] = None,
        hospital_id: Optional[str] = None,
        department_id: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[ProductAssociation]:
        """
        筛选关联记录
        
        支持多条件组合筛选，可以按产品、医院、科室和时间范围进行筛选。
        所有筛选条件都是可选的，可以灵活组合使用。
        
        参数：
            product_id (Optional[str]): 产品ID，可选
            hospital_id (Optional[str]): 医院ID，可选
            department_id (Optional[str]): 科室ID，可选
            start_date (Optional[str]): 开始日期，可选，格式：YYYY-MM-DD
            end_date (Optional[str]): 结束日期，可选，格式：YYYY-MM-DD
        
        返回：
            List[ProductAssociation]: 符合所有筛选条件的关联记录列表
        
        筛选逻辑：
            1. 确定候选关联记录集合：
                - 如果提供了 product_id，使用 product_index 获取候选集
                - 如果提供了 hospital_id，使用 hospital_index 获取候选集
                - 如果提供了 department_id，使用 department_index 获取候选集
                - 多个ID条件时，取交集
                - 如果没有提供任何ID条件，加载所有关联记录
            2. 加载候选记录并应用时间范围筛选：
                - 如果提供了 start_date，过滤掉创建时间早于该日期的记录
                - 如果提供了 end_date，过滤掉创建时间晚于该日期的记录
                - end_date 包含当天的所有时间（23:59:59）
        
        时间格式：
            - 输入格式：YYYY-MM-DD（例如：2024-01-15）
            - 如果格式无效，输出警告并忽略该条件
        
        错误处理：
            - 如果日期格式无效，输出警告并忽略该筛选条件
            - 如果某个关联记录文件加载失败，输出警告并跳过该记录
        
        使用示例：
            >>> service = ProductAssociationService()
            >>> 
            >>> # 按产品筛选
            >>> associations = service.filter_associations(product_id="prod_001")
            >>> 
            >>> # 按医院和时间范围筛选
            >>> associations = service.filter_associations(
            ...     hospital_id="hosp_001",
            ...     start_date="2024-01-01",
            ...     end_date="2024-12-31"
            ... )
            >>> 
            >>> # 多条件组合筛选
            >>> associations = service.filter_associations(
            ...     product_id="prod_001",
            ...     hospital_id="hosp_001",
            ...     department_id="dept_001"
            ... )
        
        性能优化：
            - 使用索引文件减少需要检查的记录数量
            - 优先使用最具选择性的索引
            - 通过取交集进一步缩小候选集
        
        注意事项：
            - 所有筛选条件都是 AND 关系（必须同时满足）
            - 如果不提供任何筛选条件，返回所有关联记录
            - 时间筛选基于关联记录的创建时间（created_at）
        """
        # 1. 确定候选关联记录集合
        # 使用最具选择性的索引来减少需要检查的记录数量
        candidate_ids = None
        
        if product_id:
            # 使用 product_index
            product_index = self._load_index(self.product_index_path)
            candidate_ids = set(product_index.get(product_id, []))
        
        if hospital_id:
            # 使用 hospital_index
            hospital_index = self._load_index(self.hospital_index_path)
            hospital_ids = set(hospital_index.get(hospital_id, []))
            
            if candidate_ids is None:
                candidate_ids = hospital_ids
            else:
                # 取交集
                candidate_ids = candidate_ids.intersection(hospital_ids)
        
        if department_id:
            # 使用 department_index
            department_index = self._load_index(self.department_index_path)
            department_ids = set(department_index.get(department_id, []))
            
            if candidate_ids is None:
                candidate_ids = department_ids
            else:
                # 取交集
                candidate_ids = candidate_ids.intersection(department_ids)
        
        # 如果没有指定任何ID筛选条件，则加载所有关联记录
        if candidate_ids is None:
            candidate_ids = set()
            # 遍历 associations 目录获取所有关联记录ID
            for filename in os.listdir(self.associations_dir):
                if filename.endswith('.json') and filename != 'product_index.json' and \
                   filename != 'hospital_index.json' and filename != 'department_index.json' and \
                   filename != 'unique_index.json':
                    association_id = filename[:-5]  # 移除 .json 后缀
                    candidate_ids.add(association_id)
        
        # 2. 加载候选记录并应用时间范围筛选
        associations = []
        
        # 解析时间范围
        start_datetime = None
        end_datetime = None
        
        if start_date:
            try:
                start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
            except ValueError:
                print(f"警告：无效的开始日期格式：{start_date}，应为 YYYY-MM-DD")
        
        if end_date:
            try:
                # 结束日期包含当天的所有时间，所以设置为当天的 23:59:59
                end_datetime = datetime.strptime(end_date, '%Y-%m-%d')
                end_datetime = end_datetime.replace(hour=23, minute=59, second=59, microsecond=999999)
            except ValueError:
                print(f"警告：无效的结束日期格式：{end_date}，应为 YYYY-MM-DD")
        
        # 加载并筛选记录
        for association_id in candidate_ids:
            association_path = os.path.join(self.associations_dir, f"{association_id}.json")
            
            if os.path.exists(association_path):
                try:
                    with open(association_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        association = ProductAssociation(**data)
                        
                        # 应用时间范围筛选
                        if start_datetime and association.created_at < start_datetime:
                            continue
                        
                        if end_datetime and association.created_at > end_datetime:
                            continue
                        
                        associations.append(association)
                        
                except Exception as e:
                    print(f"警告：加载关联记录 {association_id} 失败：{e}")
        
        return associations
    
    def search_associations(self, keyword: str) -> List[ProductAssociation]:
        """
        搜索关联记录
        
        在产品名称、医院名称、科室名称中搜索包含指定关键词的关联记录。
        使用不区分大小写的模糊匹配。
        
        参数：
            keyword (str): 搜索关键词，可以是产品、医院或科室名称的一部分
        
        返回：
            List[ProductAssociation]: 匹配的关联记录列表
        
        搜索逻辑：
            1. 将关键词转换为小写（不区分大小写）
            2. 遍历所有关联记录文件（跳过索引文件）
            3. 加载每条关联记录
            4. 检查关键词是否出现在以下字段中（不区分大小写）：
                - product_name（产品名称）
                - hospital_name（医院名称）
                - department_name（科室名称）
            5. 如果匹配，添加到结果列表
        
        匹配规则：
            - 不区分大小写（keyword.lower() in name.lower()）
            - 模糊匹配（部分匹配即可）
            - 只要在三个名称字段中的任意一个匹配即可
        
        错误处理：
            - 如果某个关联记录文件加载失败，输出警告并跳过该记录
            - 不会因为单个文件加载失败而中断搜索
        
        使用示例：
            >>> service = ProductAssociationService()
            >>> 
            >>> # 搜索包含"阿司匹林"的记录
            >>> associations = service.search_associations("阿司匹林")
            >>> 
            >>> # 搜索包含"协和"的记录（可能匹配医院名称）
            >>> associations = service.search_associations("协和")
            >>> 
            >>> # 搜索包含"心内科"的记录（可能匹配科室名称）
            >>> associations = service.search_associations("心内科")
            >>> 
            >>> for assoc in associations:
            ...     print(f"{assoc.product_name} - {assoc.hospital_name} - {assoc.department_name}")
        
        性能考虑：
            - 需要遍历所有关联记录文件，对于大量记录可能较慢
            - 建议在数据量较大时使用 filter_associations() 进行精确筛选
        
        注意事项：
            - 搜索是 OR 关系（在任意一个名称字段中匹配即可）
            - 不支持正则表达式或高级搜索语法
            - 搜索结果不排序，按文件遍历顺序返回
        """
        # 使用不区分大小写的模糊匹配
        keyword_lower = keyword.lower()
        
        # 遍历所有关联记录
        associations = []
        
        # 获取所有关联记录文件
        for filename in os.listdir(self.associations_dir):
            # 跳过索引文件
            if filename.endswith('.json') and filename not in [
                'product_index.json',
                'hospital_index.json',
                'department_index.json',
                'unique_index.json'
            ]:
                association_path = os.path.join(self.associations_dir, filename)
                
                try:
                    with open(association_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        association = ProductAssociation(**data)
                        
                        # 在产品名称、医院名称、科室名称中搜索关键词
                        if (keyword_lower in association.product_name.lower() or
                            keyword_lower in association.hospital_name.lower() or
                            keyword_lower in association.department_name.lower()):
                            associations.append(association)
                            
                except Exception as e:
                    print(f"警告：加载关联记录 {filename} 失败：{e}")
        
        return associations
    
    def check_integrity(self) -> List[ProductAssociation]:
        """
        检查数据完整性
        
        检查所有关联记录引用的产品、医院、科室是否仍然存在。
        如果引用的实体已被删除，将关联记录标记为失效（is_active = False）。
        
        返回：
            List[ProductAssociation]: 所有引用失效的关联记录列表
        
        检查流程：
            1. 遍历所有关联记录文件（跳过索引文件）
            2. 加载每条关联记录
            3. 验证产品ID是否存在（调用 hospital_service.get_product()）
            4. 验证医院ID是否存在（调用 hospital_service.get_hospital()）
            5. 验证科室ID是否存在（调用 hospital_service.get_department()）
            6. 如果任意一个实体不存在：
                - 标记关联记录为失效（is_active = False）
                - 保存更新后的关联记录
                - 添加到失效记录列表
        
        失效条件：
            - 产品ID不存在
            - 医院ID不存在
            - 科室ID不存在
            - 满足任意一个条件即标记为失效
        
        错误处理：
            - 如果某个关联记录文件加载失败，输出警告并跳过该记录
            - 不会因为单个文件加载失败而中断检查
        
        使用示例：
            >>> service = ProductAssociationService()
            >>> invalid_associations = service.check_integrity()
            >>> if invalid_associations:
            ...     print(f"发现 {len(invalid_associations)} 条失效记录：")
            ...     for assoc in invalid_associations:
            ...         print(f"  - {assoc.association_id}: {assoc.product_name} / {assoc.hospital_name} / {assoc.department_name}")
            ... else:
            ...     print("所有关联记录都有效")
        
        注意事项：
            - 此方法会修改失效记录的 is_active 字段并保存
            - 失效记录不会被自动删除，需要手动清理
            - 建议定期运行此方法以维护数据完整性
            - 失效记录仍然可以通过查询方法获取，但 is_active 为 False
        
        相关方法：
            - cascade_delete_by_product(): 删除产品时自动删除相关关联记录
            - cascade_delete_by_hospital(): 删除医院时自动删除相关关联记录
            - cascade_delete_by_department(): 删除科室时自动删除相关关联记录
        """
        # 导入 hospital_service
        from modules.hospital_manager.service import hospital_service
        
        invalid_associations = []
        
        # 1. 加载所有关联记录
        for filename in os.listdir(self.associations_dir):
            # 跳过索引文件
            if filename.endswith('.json') and filename not in [
                'product_index.json',
                'hospital_index.json',
                'department_index.json',
                'unique_index.json'
            ]:
                association_path = os.path.join(self.associations_dir, filename)
                
                try:
                    with open(association_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        association = ProductAssociation(**data)
                        
                        # 2. 验证每条记录引用的产品、医院、科室是否存在
                        is_invalid = False
                        
                        # 检查产品是否存在
                        product = hospital_service.get_product(association.product_id)
                        if not product:
                            is_invalid = True
                        
                        # 检查医院是否存在
                        hospital = hospital_service.get_hospital(association.hospital_id)
                        if not hospital:
                            is_invalid = True
                        
                        # 检查科室是否存在
                        department = hospital_service.get_department(association.department_id)
                        if not department:
                            is_invalid = True
                        
                        # 3. 如果引用失效，标记并保存
                        if is_invalid:
                            # 标记失效的关联记录（设置 is_active = False）
                            association.is_active = False
                            
                            # 保存更新后的关联记录
                            with open(association_path, 'w', encoding='utf-8') as f_write:
                                json.dump(association.model_dump(mode='json'), f_write, ensure_ascii=False, indent=2, default=str)
                            
                            # 4. 添加到失效记录列表
                            invalid_associations.append(association)
                            
                except Exception as e:
                    print(f"警告：检查关联记录 {filename} 失败：{e}")
        
        return invalid_associations
    
    def get_statistics(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> AssociationStatistics:
        """
        获取统计数据
        
        计算产品、医院、科室的关联数量统计，支持按时间范围筛选。
        
        参数：
            start_date (Optional[str]): 开始日期，可选，格式：YYYY-MM-DD
            end_date (Optional[str]): 结束日期，可选，格式：YYYY-MM-DD
        
        返回：
            AssociationStatistics: 统计数据对象，包含：
                - product_stats (Dict[str, int]): 产品统计，键为产品ID，值为关联数量
                - hospital_stats (Dict[str, int]): 医院统计，键为医院ID，值为关联数量
                - department_stats (Dict[str, int]): 科室统计，键为科室ID，值为关联数量
                - total_associations (int): 总关联数
        
        统计逻辑：
            1. 使用 filter_associations() 获取符合时间范围的关联记录
            2. 初始化三个统计字典（product_stats, hospital_stats, department_stats）
            3. 遍历关联记录，累计每个产品、医院、科室的关联数量
            4. 计算总关联数
            5. 封装为 AssociationStatistics 对象返回
        
        时间范围筛选：
            - 如果提供了 start_date 和 end_date，只统计该时间范围内创建的关联记录
            - 如果不提供时间范围，统计所有关联记录
            - 时间格式：YYYY-MM-DD
        
        使用示例：
            >>> service = ProductAssociationService()
            >>> 
            >>> # 获取所有关联记录的统计
            >>> stats = service.get_statistics()
            >>> print(f"总关联数：{stats.total_associations}")
            >>> print(f"产品数量：{len(stats.product_stats)}")
            >>> print(f"医院数量：{len(stats.hospital_stats)}")
            >>> print(f"科室数量：{len(stats.department_stats)}")
            >>> 
            >>> # 获取特定时间范围的统计
            >>> stats = service.get_statistics(
            ...     start_date="2024-01-01",
            ...     end_date="2024-12-31"
            ... )
            >>> 
            >>> # 查看产品统计（按关联数量排序）
            >>> sorted_products = sorted(
            ...     stats.product_stats.items(),
            ...     key=lambda x: x[1],
            ...     reverse=True
            ... )
            >>> for product_id, count in sorted_products[:5]:
            ...     print(f"产品 {product_id}: {count} 个关联")
        
        应用场景：
            - 生成产品市场覆盖率报告
            - 分析医院产品使用情况
            - 识别热门产品和科室
            - 按时间段分析关联趋势
        
        注意事项：
            - 统计基于关联记录的创建时间（created_at）
            - 失效的关联记录（is_active = False）也会被统计
            - 统计结果中的键是ID，不是名称
        """
        # 1. 使用 filter_associations 获取符合时间范围的关联记录
        associations = self.filter_associations(
            start_date=start_date,
            end_date=end_date
        )
        
        # 2. 初始化统计数据
        product_stats: Dict[str, int] = {}
        hospital_stats: Dict[str, int] = {}
        department_stats: Dict[str, int] = {}
        
        # 3. 遍历关联记录，计算统计数据
        for association in associations:
            # 计算每个产品的关联数量
            if association.product_id not in product_stats:
                product_stats[association.product_id] = 0
            product_stats[association.product_id] += 1
            
            # 计算每个医院的关联数量
            if association.hospital_id not in hospital_stats:
                hospital_stats[association.hospital_id] = 0
            hospital_stats[association.hospital_id] += 1
            
            # 计算每个科室的关联数量
            if association.department_id not in department_stats:
                department_stats[association.department_id] = 0
            department_stats[association.department_id] += 1
        
        # 4. 计算总关联数
        total_associations = len(associations)
        
        # 5. 返回 AssociationStatistics 对象
        return AssociationStatistics(
            product_stats=product_stats,
            hospital_stats=hospital_stats,
            department_stats=department_stats,
            total_associations=total_associations
        )
    
    def export_data(
        self,
        format: str = "csv",
        filters: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        导出关联数据
        
        将关联记录导出为 CSV 或 Excel 文件，支持按筛选条件导出。
        
        参数：
            format (str): 导出格式，可选值：
                - "csv": CSV 文件（默认）
                - "excel": Excel 文件（需要安装 openpyxl 库）
            filters (Optional[Dict[str, Any]]): 筛选条件字典，可选，包含：
                - product_id (str): 产品ID
                - hospital_id (str): 医院ID
                - department_id (str): 科室ID
                - start_date (str): 开始日期，格式：YYYY-MM-DD
                - end_date (str): 结束日期，格式：YYYY-MM-DD
        
        返回：
            str: 导出文件的完整路径
        
        导出流程：
            1. 应用筛选条件获取关联记录（如果提供了 filters）
            2. 如果没有筛选条件，导出所有关联记录
            3. 创建 outputs 目录（如果不存在）
            4. 生成带时间戳的文件名
            5. 根据格式生成 CSV 或 Excel 文件
            6. 返回文件路径
        
        CSV 格式：
            - 使用 UTF-8-BOM 编码，确保 Excel 正确显示中文
            - 包含表头：产品名称、医院名称、科室名称、创建时间
            - 时间格式：YYYY-MM-DD HH:MM:SS
        
        Excel 格式：
            - 使用 openpyxl 库生成
            - 工作表名称：产品关联记录
            - 表头加粗并居中对齐
            - 自动调整列宽
            - 包含字段：产品名称、医院名称、科室名称、创建时间
        
        错误处理：
            - 如果格式不支持，抛出 ValueError
            - 如果导出 Excel 时未安装 openpyxl，抛出 ImportError
        
        使用示例：
            >>> service = ProductAssociationService()
            >>> 
            >>> # 导出所有记录为 CSV
            >>> filepath = service.export_data(format="csv")
            >>> print(f"数据已导出到：{filepath}")
            >>> 
            >>> # 导出特定产品的记录为 Excel
            >>> filepath = service.export_data(
            ...     format="excel",
            ...     filters={"product_id": "prod_001"}
            ... )
            >>> 
            >>> # 导出特定时间范围的记录
            >>> filepath = service.export_data(
            ...     format="csv",
            ...     filters={
            ...         "start_date": "2024-01-01",
            ...         "end_date": "2024-12-31"
            ...     }
            ... )
        
        文件命名：
            - CSV: product_associations_YYYYMMdd_HHMMSS.csv
            - Excel: product_associations_YYYYMMdd_HHMMSS.xlsx
        
        注意事项：
            - 导出的文件保存在 outputs/ 目录下
            - 文件名包含时间戳，避免覆盖
            - Excel 格式需要安装 openpyxl 库：pip install openpyxl
            - 导出的数据包含冗余的名称字段，不包含ID字段
        """
        import csv
        
        # 1. 应用筛选条件获取关联记录
        if filters:
            associations = self.filter_associations(
                product_id=filters.get('product_id'),
                hospital_id=filters.get('hospital_id'),
                department_id=filters.get('department_id'),
                start_date=filters.get('start_date'),
                end_date=filters.get('end_date')
            )
        else:
            # 如果没有筛选条件，导出所有关联记录
            associations = self.filter_associations()
        
        # 2. 创建 outputs 目录（如果不存在）
        outputs_dir = "outputs"
        os.makedirs(outputs_dir, exist_ok=True)
        
        # 3. 生成文件名（包含时间戳）
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if format.lower() == "csv":
            # 4. 生成 CSV 文件
            filename = f"product_associations_{timestamp}.csv"
            filepath = os.path.join(outputs_dir, filename)
            
            # 5. 写入 CSV 文件
            with open(filepath, 'w', encoding='utf-8-sig', newline='') as f:
                writer = csv.writer(f)
                
                # 写入表头
                writer.writerow(['产品名称', '医院名称', '科室名称', '创建时间'])
                
                # 写入数据行
                for association in associations:
                    writer.writerow([
                        association.product_name,
                        association.hospital_name,
                        association.department_name,
                        association.created_at.strftime('%Y-%m-%d %H:%M:%S')
                    ])
            
            return filepath
        
        elif format.lower() == "excel":
            try:
                from openpyxl import Workbook
                from openpyxl.styles import Font, Alignment
            except ImportError:
                raise ImportError("需要安装 openpyxl 库才能导出 Excel 文件。请运行：pip install openpyxl")
            
            # 4. 生成 Excel 文件
            filename = f"product_associations_{timestamp}.xlsx"
            filepath = os.path.join(outputs_dir, filename)
            
            # 5. 创建工作簿和工作表
            wb = Workbook()
            ws = wb.active
            ws.title = "产品关联记录"
            
            # 6. 写入表头
            headers = ['产品名称', '医院名称', '科室名称', '创建时间']
            ws.append(headers)
            
            # 设置表头样式
            for cell in ws[1]:
                cell.font = Font(bold=True)
                cell.alignment = Alignment(horizontal='center', vertical='center')
            
            # 7. 写入数据行
            for association in associations:
                ws.append([
                    association.product_name,
                    association.hospital_name,
                    association.department_name,
                    association.created_at.strftime('%Y-%m-%d %H:%M:%S')
                ])
            
            # 8. 调整列宽
            ws.column_dimensions['A'].width = 20
            ws.column_dimensions['B'].width = 25
            ws.column_dimensions['C'].width = 20
            ws.column_dimensions['D'].width = 20
            
            # 9. 保存工作簿
            wb.save(filepath)
            
            return filepath
        
        else:
            raise ValueError(f"不支持的导出格式：{format}，目前支持 'csv' 和 'excel'")
    
    def cascade_delete_by_product(self, product_id: str) -> int:
        """
        级联删除：删除产品时删除所有相关关联记录
        
        当产品被删除时，自动删除所有引用该产品的关联记录，
        确保数据完整性和一致性。
        
        参数：
            product_id (str): 要删除的产品ID
        
        返回：
            int: 删除的关联记录数量
        
        删除流程：
            1. 使用 product_index 查找所有引用该产品的关联记录ID
            2. 如果没有关联记录，返回 0
            3. 遍历关联记录ID列表，逐个调用 delete_association() 删除
            4. 统计成功删除的记录数量
            5. 返回删除数量
        
        使用示例：
            >>> service = ProductAssociationService()
            >>> deleted_count = service.cascade_delete_by_product("prod_001")
            >>> print(f"删除了 {deleted_count} 条关联记录")
        
        集成建议：
            在 HospitalService 的 delete_product() 方法中调用此方法：
            
            >>> def delete_product(self, product_id: str) -> bool:
            ...     # 先删除关联记录
            ...     from modules.product_association import product_association_service
            ...     deleted_count = product_association_service.cascade_delete_by_product(product_id)
            ...     
            ...     # 再删除产品
            ...     # ... 删除产品的代码 ...
            ...     
            ...     return True
        
        注意事项：
            - 此方法会永久删除所有相关的关联记录，不可恢复
            - 删除操作会自动更新所有索引文件
            - 建议在删除产品前调用此方法
            - 使用列表副本遍历，避免在遍历时修改列表
        """
        # 1. 使用 product_index 查找所有相关的关联记录
        product_index = self._load_index(self.product_index_path)
        association_ids = product_index.get(product_id, [])
        
        if not association_ids:
            return 0
        
        # 2. 批量删除关联记录
        deleted_count = 0
        for association_id in association_ids[:]:  # 使用副本遍历
            if self.delete_association(association_id):
                deleted_count += 1
        
        return deleted_count
    
    def cascade_delete_by_hospital(self, hospital_id: str) -> int:
        """
        级联删除：删除医院时删除所有相关关联记录
        
        当医院被删除时，自动删除所有引用该医院的关联记录，
        确保数据完整性和一致性。
        
        参数：
            hospital_id (str): 要删除的医院ID
        
        返回：
            int: 删除的关联记录数量
        
        删除流程：
            1. 使用 hospital_index 查找所有引用该医院的关联记录ID
            2. 如果没有关联记录，返回 0
            3. 遍历关联记录ID列表，逐个调用 delete_association() 删除
            4. 统计成功删除的记录数量
            5. 返回删除数量
        
        使用示例：
            >>> service = ProductAssociationService()
            >>> deleted_count = service.cascade_delete_by_hospital("hosp_001")
            >>> print(f"删除了 {deleted_count} 条关联记录")
        
        集成建议：
            在 HospitalService 的 delete_hospital() 方法中调用此方法：
            
            >>> def delete_hospital(self, hospital_id: str) -> bool:
            ...     # 先删除关联记录
            ...     from modules.product_association import product_association_service
            ...     deleted_count = product_association_service.cascade_delete_by_hospital(hospital_id)
            ...     
            ...     # 再删除医院
            ...     # ... 删除医院的代码 ...
            ...     
            ...     return True
        
        注意事项：
            - 此方法会永久删除所有相关的关联记录，不可恢复
            - 删除操作会自动更新所有索引文件
            - 建议在删除医院前调用此方法
            - 使用列表副本遍历，避免在遍历时修改列表
            - 会删除该医院所有科室的产品关联记录
        """
        # 1. 使用 hospital_index 查找所有相关的关联记录
        hospital_index = self._load_index(self.hospital_index_path)
        association_ids = hospital_index.get(hospital_id, [])
        
        if not association_ids:
            return 0
        
        # 2. 批量删除关联记录
        deleted_count = 0
        for association_id in association_ids[:]:  # 使用副本遍历
            if self.delete_association(association_id):
                deleted_count += 1
        
        return deleted_count
    
    def cascade_delete_by_department(self, department_id: str) -> int:
        """
        级联删除：删除科室时删除所有相关关联记录
        
        当科室被删除时，自动删除所有引用该科室的关联记录，
        确保数据完整性和一致性。
        
        参数：
            department_id (str): 要删除的科室ID
        
        返回：
            int: 删除的关联记录数量
        
        删除流程：
            1. 使用 department_index 查找所有引用该科室的关联记录ID
            2. 如果没有关联记录，返回 0
            3. 遍历关联记录ID列表，逐个调用 delete_association() 删除
            4. 统计成功删除的记录数量
            5. 返回删除数量
        
        使用示例：
            >>> service = ProductAssociationService()
            >>> deleted_count = service.cascade_delete_by_department("dept_001")
            >>> print(f"删除了 {deleted_count} 条关联记录")
        
        集成建议：
            在 HospitalService 的 delete_department() 方法中调用此方法：
            
            >>> def delete_department(self, department_id: str) -> bool:
            ...     # 先删除关联记录
            ...     from modules.product_association import product_association_service
            ...     deleted_count = product_association_service.cascade_delete_by_department(department_id)
            ...     
            ...     # 再删除科室
            ...     # ... 删除科室的代码 ...
            ...     
            ...     return True
        
        注意事项：
            - 此方法会永久删除所有相关的关联记录，不可恢复
            - 删除操作会自动更新所有索引文件
            - 建议在删除科室前调用此方法
            - 使用列表副本遍历，避免在遍历时修改列表
            - 只删除该科室的产品关联记录，不影响其他科室
        """
        # 1. 使用 department_index 查找所有相关的关联记录
        department_index = self._load_index(self.department_index_path)
        association_ids = department_index.get(department_id, [])
        
        if not association_ids:
            return 0
        
        # 2. 批量删除关联记录
        deleted_count = 0
        for association_id in association_ids[:]:  # 使用副本遍历
            if self.delete_association(association_id):
                deleted_count += 1
        
        return deleted_count
