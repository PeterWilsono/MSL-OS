# 设计文档：产品与医院科室关联管理

## 概述

本设计文档描述了医药信息专员系统中"产品与医院科室关联管理"功能的技术实现方案。该功能通过建立产品（Product）与医院（Hospital）、科室（Department）之间的多对多关联关系，使医药信息专员能够追踪和管理产品在各医院科室的使用情况。

### 设计目标

- 建立灵活的产品-医院-科室关联数据模型
- 提供高效的关联关系查询和管理功能
- 确保数据完整性和一致性
- 支持批量操作以提高工作效率
- 提供统计分析功能以支持决策

### 技术栈

- **编程语言**：Python 3.x
- **数据验证**：Pydantic
- **UI 框架**：NiceGUI
- **数据存储**：JSON 文件
- **测试框架**：pytest + Hypothesis（属性测试）

## 架构设计

### 系统架构

```
┌─────────────────────────────────────────────────────────┐
│                    UI Layer (NiceGUI)                    │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Product Association Management Interface        │  │
│  │  - List View  - Filter  - Search  - Statistics   │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                            │
                            ↓
┌─────────────────────────────────────────────────────────┐
│                   Service Layer                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │  ProductAssociationService                       │  │
│  │  - create_association()                          │  │
│  │  - delete_association()                          │  │
│  │  - query_by_product()                            │  │
│  │  - query_by_hospital()                           │  │
│  │  - query_by_department()                         │  │
│  │  - batch_create()                                │  │
│  │  - batch_delete()                                │  │
│  │  - check_integrity()                             │  │
│  │  - get_statistics()                              │  │
│  │  - export_data()                                 │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                            │
                            ↓
┌─────────────────────────────────────────────────────────┐
│                   Data Layer                             │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Data Models (Pydantic)                          │  │
│  │  - ProductAssociation                            │  │
│  │  - AssociationQuery                              │  │
│  │  - AssociationStatistics                         │  │
│  └──────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────┐  │
│  │  File Manager                                    │  │
│  │  - save_json()  - load_json()  - search()       │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                            │
                            ↓
┌─────────────────────────────────────────────────────────┐
│              Storage (JSON Files)                        │
│  data/associations/                                      │
│    - association_<id>.json                               │
│  data/products/                                          │
│  data/hospitals/                                         │
│  data/departments/                                       │
└─────────────────────────────────────────────────────────┘
```

### 模块结构

```
modules/
└── product_association/
    ├── __init__.py
    ├── models.py          # 数据模型定义
    ├── service.py         # 业务逻辑服务
    └── ui.py              # 用户界面
```

## 组件和接口

### 数据模型

#### ProductAssociation（产品关联记录）

```python
class ProductAssociation(BaseModel):
    """产品与医院科室关联记录"""
    association_id: str = Field(..., description="关联记录唯一标识")
    product_id: str = Field(..., description="产品ID")
    hospital_id: str = Field(..., description="医院ID")
    department_id: str = Field(..., description="科室ID")
    
    # 冗余字段（用于快速查询和展示）
    product_name: str = Field(default="", description="产品名称")
    hospital_name: str = Field(default="", description="医院名称")
    department_name: str = Field(default="", description="科室名称")
    
    # 元数据
    notes: str = Field(default="", description="备注")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")
    is_active: bool = Field(default=True, description="是否有效")
```

#### AssociationQuery（查询结果）

```python
class AssociationQuery(BaseModel):
    """关联查询结果"""
    associations: List[ProductAssociation] = Field(default_factory=list)
    total_count: int = Field(default=0, description="总数量")
    query_type: str = Field(..., description="查询类型：by_product/by_hospital/by_department")
```

#### AssociationStatistics（统计数据）

```python
class AssociationStatistics(BaseModel):
    """关联统计数据"""
    product_stats: Dict[str, int] = Field(default_factory=dict, description="产品统计：{product_id: count}")
    hospital_stats: Dict[str, int] = Field(default_factory=dict, description="医院统计：{hospital_id: count}")
    department_stats: Dict[str, int] = Field(default_factory=dict, description="科室统计：{department_id: count}")
    total_associations: int = Field(default=0, description="总关联数")
```

#### BatchOperationResult（批量操作结果）

```python
class BatchOperationResult(BaseModel):
    """批量操作结果"""
    success_count: int = Field(default=0, description="成功数量")
    failed_count: int = Field(default=0, description="失败数量")
    skipped_count: int = Field(default=0, description="跳过数量")
    error_messages: List[str] = Field(default_factory=list, description="错误信息列表")
```

### 服务接口

#### ProductAssociationService

```python
class ProductAssociationService:
    """产品关联管理服务"""
    
    def create_association(
        self,
        product_id: str,
        hospital_id: str,
        department_id: str,
        notes: str = ""
    ) -> Optional[ProductAssociation]:
        """
        创建产品关联记录
        
        验证：
        - 产品ID、医院ID、科室ID 必须存在
        - 不允许创建重复的关联记录
        
        返回：
        - 成功：ProductAssociation 对象
        - 失败：None（并记录错误）
        """
        pass
    
    def delete_association(self, association_id: str) -> bool:
        """
        删除关联记录
        
        返回：
        - True：删除成功
        - False：记录不存在或删除失败
        """
        pass
    
    def query_by_product(self, product_id: str) -> AssociationQuery:
        """
        查询产品的使用情况
        
        返回：该产品关联的所有医院和科室
        """
        pass
    
    def query_by_hospital(
        self,
        hospital_id: str,
        department_id: Optional[str] = None
    ) -> AssociationQuery:
        """
        查询医院或科室的产品使用情况
        
        参数：
        - hospital_id：医院ID
        - department_id：科室ID（可选，如果提供则只查询该科室）
        
        返回：医院或科室使用的所有产品
        """
        pass
    
    def batch_create(
        self,
        associations: List[Dict[str, str]]
    ) -> BatchOperationResult:
        """
        批量创建关联记录
        
        参数：
        - associations：关联记录列表，每个元素包含 product_id, hospital_id, department_id
        
        处理逻辑：
        - 遇到重复记录时跳过并继续处理
        - 遇到无效ID时记录错误并继续处理
        
        返回：批量操作结果
        """
        pass
    
    def batch_delete(self, association_ids: List[str]) -> BatchOperationResult:
        """
        批量删除关联记录
        
        返回：批量操作结果
        """
        pass
    
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
        
        支持多条件组合筛选
        """
        pass
    
    def search_associations(self, keyword: str) -> List[ProductAssociation]:
        """
        搜索关联记录
        
        在产品名称、医院名称、科室名称中搜索关键词
        """
        pass
    
    def check_integrity(self) -> List[ProductAssociation]:
        """
        检查数据完整性
        
        返回：所有引用失效的关联记录
        """
        pass
    
    def get_statistics(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> AssociationStatistics:
        """
        获取统计数据
        
        支持按时间范围筛选
        """
        pass
    
    def export_data(
        self,
        format: str = "csv",
        filters: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        导出关联数据
        
        参数：
        - format：导出格式（csv 或 excel）
        - filters：筛选条件（可选）
        
        返回：导出文件路径
        """
        pass
    
    def cascade_delete_by_product(self, product_id: str) -> int:
        """
        级联删除：删除产品时删除所有相关关联记录
        
        返回：删除的记录数量
        """
        pass
    
    def cascade_delete_by_hospital(self, hospital_id: str) -> int:
        """
        级联删除：删除医院时删除所有相关关联记录
        
        返回：删除的记录数量
        """
        pass
    
    def cascade_delete_by_department(self, department_id: str) -> int:
        """
        级联删除：删除科室时删除所有相关关联记录
        
        返回：删除的记录数量
        """
        pass
```

## 数据模型详细设计

### 存储结构

关联记录存储在 `data/associations/` 目录下，每条记录一个 JSON 文件：

```json
{
  "association_id": "assoc_20240115120000",
  "product_id": "product_001",
  "hospital_id": "hospital_001",
  "department_id": "dept_001",
  "product_name": "阿司匹林",
  "hospital_name": "北京协和医院",
  "department_name": "心内科",
  "notes": "",
  "created_at": "2024-01-15T12:00:00",
  "updated_at": "2024-01-15T12:00:00",
  "is_active": true
}
```

### 索引策略

为了提高查询效率，维护以下索引文件：

1. **product_index.json**：产品ID → 关联记录ID列表
2. **hospital_index.json**：医院ID → 关联记录ID列表
3. **department_index.json**：科室ID → 关联记录ID列表

索引文件示例：

```json
{
  "product_001": ["assoc_001", "assoc_002", "assoc_003"],
  "product_002": ["assoc_004", "assoc_005"]
}
```

### 唯一性约束

关联记录的唯一性由 `(product_id, hospital_id, department_id)` 三元组保证。

维护一个唯一性索引文件 `unique_index.json`：

```json
{
  "product_001:hospital_001:dept_001": "assoc_001",
  "product_001:hospital_002:dept_003": "assoc_002"
}
```

## 正确性属性

*属性是一种特征或行为，应该在系统的所有有效执行中保持为真——本质上是关于系统应该做什么的形式化陈述。属性作为人类可读规范和机器可验证正确性保证之间的桥梁。*

### 属性 1：关联记录创建和持久化往返

*对于任何*有效的产品ID、医院ID和科室ID组合，创建关联记录后保存到存储，然后重新加载，应该得到等价的关联记录对象。

**验证需求：1.1, 1.4, 1.5**

### 属性 2：ID 有效性验证

*对于任何*包含无效产品ID、医院ID或科室ID的输入，创建关联记录的操作应该被拒绝并返回错误。

**验证需求：1.2, 10.1**

### 属性 3：唯一性约束

*对于任何*已存在的关联记录（相同的产品、医院、科室组合），尝试创建重复记录应该被拒绝。

**验证需求：1.3**

### 属性 4：产品查询完整性

*对于任何*产品ID，查询该产品的关联记录应该返回所有包含该产品ID的关联记录，且结果按医院名称和科室名称排序。

**验证需求：2.1, 2.4**

### 属性 5：查询结果包含必需字段

*对于任何*查询结果中的关联记录，应该包含产品名称、医院名称、科室名称和创建时间字段。

**验证需求：2.2, 3.3**

### 属性 6：医院查询完整性

*对于任何*医院ID，查询该医院的关联记录应该返回所有包含该医院ID的关联记录。

**验证需求：3.1**

### 属性 7：科室查询完整性

*对于任何*医院ID和科室ID组合，查询该科室的关联记录应该返回所有匹配的关联记录，且结果按产品名称排序。

**验证需求：3.2, 3.5**

### 属性 8：删除操作的有效性

*对于任何*存在的关联记录，删除操作后，该记录应该不再存在于存储中，且查询不应返回该记录。

**验证需求：4.1**

### 属性 9：删除不存在记录的错误处理

*对于任何*不存在的关联记录ID，删除操作应该返回失败状态。

**验证需求：4.3**

### 属性 10：批量创建操作

*对于任何*有效的关联记录列表，批量创建操作应该成功创建所有记录，且返回的成功数量等于输入列表的长度。

**验证需求：5.1**

### 属性 11：批量创建跳过重复记录

*对于任何*包含重复记录的批量输入，批量创建操作应该跳过重复记录并继续处理其他记录，且返回的跳过数量等于重复记录的数量。

**验证需求：5.2**

### 属性 12：批量删除操作

*对于任何*存在的关联记录ID列表，批量删除操作应该删除所有记录，且返回的成功数量等于输入列表的长度。

**验证需求：5.3**

### 属性 13：批量操作结果摘要准确性

*对于任何*批量操作，返回的结果摘要中的成功数量、失败数量和跳过数量之和应该等于输入的总数量。

**验证需求：5.4**

### 属性 14：级联删除完整性

*对于任何*产品、医院或科室，当其被删除时，所有引用该实体的关联记录也应该被自动删除。

**验证需求：6.1, 6.2, 6.3**

### 属性 15：失效记录识别

*对于任何*引用不存在的产品、医院或科室的关联记录，数据完整性检查应该识别并返回该记录。

**验证需求：6.4, 6.5**

### 属性 16：筛选功能正确性

*对于任何*筛选条件（产品、医院、科室），筛选结果应该只包含满足所有指定条件的关联记录。

**验证需求：7.3**

### 属性 17：搜索功能完整性

*对于任何*搜索关键词，搜索结果应该包含所有在产品名称、医院名称或科室名称中包含该关键词的关联记录。

**验证需求：7.4**

### 属性 18：导出数据完整性

*对于任何*关联记录集合，导出操作生成的文件应该包含所有记录的产品名称、医院名称、科室名称和创建时间。

**验证需求：8.1, 8.2**

### 属性 19：统计数据准确性

*对于任何*关联记录集合，统计功能计算的产品数量、医院数量和科室数量应该与实际的关联记录数量一致。

**验证需求：9.1, 9.2, 9.3**

### 属性 20：时间范围筛选正确性

*对于任何*时间范围（开始日期和结束日期），筛选后的统计数据应该只包含创建时间在该范围内的关联记录。

**验证需求：9.5**

## 错误处理

### 错误类型

1. **验证错误**：
   - 无效的产品ID、医院ID或科室ID
   - 重复的关联记录
   - 缺少必需字段

2. **数据完整性错误**：
   - 引用的实体不存在
   - 数据文件损坏
   - 索引不一致

3. **文件系统错误**：
   - 文件读写失败
   - 磁盘空间不足
   - 权限不足

### 错误处理策略

```python
class AssociationError(Exception):
    """关联管理基础异常"""
    pass

class ValidationError(AssociationError):
    """验证错误"""
    pass

class DuplicateError(AssociationError):
    """重复记录错误"""
    pass

class NotFoundError(AssociationError):
    """记录不存在错误"""
    pass

class IntegrityError(AssociationError):
    """数据完整性错误"""
    pass
```

### 错误处理原则

1. **早期验证**：在创建或更新操作前验证所有输入
2. **明确的错误信息**：提供清晰的错误描述和建议
3. **事务性操作**：批量操作失败时不影响已成功的部分
4. **日志记录**：记录所有错误和异常情况
5. **用户友好**：向用户展示易于理解的错误提示

## 测试策略

### 双重测试方法

本功能采用单元测试和属性测试相结合的方法：

- **单元测试**：验证特定示例、边界情况和错误条件
- **属性测试**：验证跨所有输入的通用属性

两者互补，共同确保全面覆盖（单元测试捕获具体错误，属性测试验证一般正确性）。

### 属性测试配置

- **测试库**：Hypothesis（Python 的属性测试库）
- **迭代次数**：每个属性测试最少 100 次迭代
- **标签格式**：`# Feature: product-hospital-department-association, Property {number}: {property_text}`

### 测试用例设计

#### 单元测试

1. **创建关联记录**：
   - 测试有效输入创建成功
   - 测试无效ID被拒绝
   - 测试重复记录被拒绝
   - 测试时间戳字段被正确设置

2. **查询功能**：
   - 测试按产品查询返回正确结果
   - 测试按医院查询返回正确结果
   - 测试按科室查询返回正确结果
   - 测试空结果情况

3. **删除功能**：
   - 测试删除存在的记录成功
   - 测试删除不存在的记录返回错误
   - 测试级联删除正确执行

4. **批量操作**：
   - 测试批量创建成功
   - 测试批量创建跳过重复记录
   - 测试批量删除成功
   - 测试批量操作结果摘要准确

5. **数据完整性**：
   - 测试完整性检查识别失效记录
   - 测试级联删除清理相关记录

6. **筛选和搜索**：
   - 测试单条件筛选
   - 测试多条件组合筛选
   - 测试关键词搜索

7. **统计和导出**：
   - 测试统计数据计算准确
   - 测试导出文件格式正确
   - 测试时间范围筛选

#### 属性测试

每个正确性属性都应该实现为一个属性测试，使用 Hypothesis 生成随机测试数据：

```python
from hypothesis import given, strategies as st
import pytest

# Feature: product-hospital-department-association, Property 1: 关联记录创建和持久化往返
@given(
    product_id=st.text(min_size=1, max_size=50),
    hospital_id=st.text(min_size=1, max_size=50),
    department_id=st.text(min_size=1, max_size=50)
)
def test_association_round_trip(product_id, hospital_id, department_id):
    """对于任何有效的ID组合，创建、保存、加载应该得到等价的对象"""
    # 创建关联记录
    association = service.create_association(product_id, hospital_id, department_id)
    
    # 重新加载
    loaded = service.get_association(association.association_id)
    
    # 验证等价性
    assert loaded.product_id == product_id
    assert loaded.hospital_id == hospital_id
    assert loaded.department_id == department_id
```

### 测试数据生成策略

使用 Hypothesis 的策略生成测试数据：

```python
# 生成有效的ID
valid_id = st.text(
    alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')),
    min_size=1,
    max_size=50
)

# 生成关联记录
association_strategy = st.builds(
    ProductAssociation,
    product_id=valid_id,
    hospital_id=valid_id,
    department_id=valid_id
)

# 生成关联记录列表
associations_list = st.lists(association_strategy, min_size=0, max_size=20)
```

### 边界情况测试

属性测试的生成器应该包含以下边界情况：

- 空字符串ID
- 非常长的ID
- 特殊字符ID
- 空列表（批量操作）
- 单元素列表
- 大量元素列表
- 全部重复的列表
- 部分重复的列表
- 不存在的ID
- 已删除的实体ID

## 实现注意事项

### 性能优化

1. **索引维护**：
   - 在创建和删除操作时同步更新索引
   - 使用索引加速查询操作

2. **批量操作优化**：
   - 批量操作时一次性更新索引
   - 使用事务性写入减少I/O操作

3. **缓存策略**：
   - 缓存常用的查询结果
   - 缓存实体名称映射（ID → 名称）

### 数据迁移

如果需要从现有系统迁移数据：

1. 扫描现有的 Hospital 和 Department 模型中的 `products_used` 字段
2. 为每个产品使用记录创建对应的 ProductAssociation
3. 验证迁移后的数据完整性
4. 更新索引文件

### 与现有系统集成

1. **HospitalService 集成**：
   - 在 HospitalService 的删除方法中调用级联删除
   - 在产品、医院、科室创建时验证ID的唯一性

2. **UI 集成**：
   - 在医院管理界面添加"产品关联"标签页
   - 在产品管理界面添加"使用情况"视图
   - 在科室管理界面添加"产品列表"视图

3. **报告集成**：
   - 在报告模块中添加产品覆盖率统计
   - 支持按医院、科室生成产品使用报告

## 未来扩展

1. **关联属性扩展**：
   - 添加使用开始日期和结束日期
   - 添加使用量或采购量信息
   - 添加负责人信息

2. **高级查询**：
   - 支持复杂的组合查询
   - 支持聚合查询（如：某个区域的产品覆盖率）

3. **数据分析**：
   - 产品市场渗透率分析
   - 竞品对比分析
   - 趋势分析和预测

4. **权限管理**：
   - 不同用户角色的访问控制
   - 数据修改审计日志

5. **数据同步**：
   - 支持多设备数据同步
   - 支持云端备份和恢复
