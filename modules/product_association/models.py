"""
产品关联管理数据模型

本模块定义了产品与医院科室关联管理所需的数据模型。

数据模型说明：
    主要的数据模型已在 core/hospital_models.py 中定义，本模块进行引用和导出。
    
    - ProductAssociation: 产品关联记录模型
        记录产品在特定医院特定科室的使用情况，包含产品ID、医院ID、科室ID
        以及冗余的名称字段（用于快速查询和展示）。
        
    - AssociationQuery: 查询结果模型
        封装关联记录查询的结果，包含关联记录列表、总数量和查询类型。
        
    - AssociationStatistics: 统计数据模型
        提供产品、医院、科室的关联统计信息，用于数据分析和报表生成。
        
    - BatchOperationResult: 批量操作结果模型
        记录批量创建或删除操作的执行结果，包括成功、失败、跳过的数量
        以及详细的错误信息列表。

设计原则：
    - 使用 Pydantic 进行数据验证，确保数据类型和格式的正确性
    - 冗余存储常用字段（如名称），减少查询时的关联查询次数
    - 提供清晰的结果封装，便于上层调用和错误处理

本文件保留用于未来可能的模块特定模型扩展。

作者：医药信息专员系统开发团队
版本：1.0.0
"""
from core.hospital_models import (
    ProductAssociation,
    AssociationQuery,
    AssociationStatistics,
    BatchOperationResult
)

__all__ = [
    'ProductAssociation',
    'AssociationQuery',
    'AssociationStatistics',
    'BatchOperationResult'
]
