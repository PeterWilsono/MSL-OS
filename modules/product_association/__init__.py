"""
产品与医院科室关联管理模块

本模块提供产品与医院科室之间关联关系的完整管理功能。

主要功能：
    - 创建和删除产品与医院科室的关联记录
    - 查询产品在哪些医院科室中使用
    - 查询医院科室使用了哪些产品
    - 批量创建和删除关联记录
    - 数据完整性检查和级联删除
    - 统计分析和数据导出

模块组成：
    - service.py: 业务逻辑服务层
    - models.py: 数据模型定义（引用自 core.hospital_models）
    - ui.py: 用户界面层

使用示例：
    >>> from modules.product_association import product_association_service
    >>> 
    >>> # 创建关联记录
    >>> association = product_association_service.create_association(
    ...     product_id="prod_001",
    ...     hospital_id="hosp_001",
    ...     department_id="dept_001"
    ... )
    >>> 
    >>> # 查询产品使用情况
    >>> result = product_association_service.query_by_product("prod_001")
    >>> print(f"产品在 {result.total_count} 个科室中使用")

作者：医药信息专员系统开发团队
版本：1.0.0
"""
from .service import ProductAssociationService

# 创建全局服务实例，供整个应用使用
product_association_service = ProductAssociationService()

__all__ = ['ProductAssociationService', 'product_association_service']
