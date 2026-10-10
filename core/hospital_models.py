"""
医院、科室、产品相关数据模型
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class Product(BaseModel):
    """产品模型"""
    product_id: str = Field(..., description="产品ID")
    name: str = Field(..., description="产品名称")
    category: str = Field(default="", description="产品类别")
    description: str = Field(default="", description="产品描述")
    key_features: List[str] = Field(default_factory=list, description="关键特性")
    indications: List[str] = Field(default_factory=list, description="适应症")
    notes: str = Field(default="", description="备注")
    attachments: List[Dict[str, str]] = Field(default_factory=list, description="附件列表：[{filename, filepath, upload_time, file_type}]")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class Competitor(BaseModel):
    """竞品模型"""
    competitor_id: str = Field(..., description="竞品ID")
    name: str = Field(..., description="竞品名称")
    manufacturer: str = Field(default="", description="生产厂家")
    advantages: str = Field(default="", description="竞品优势")
    disadvantages: str = Field(default="", description="竞品劣势")
    market_share: str = Field(default="", description="市场份额")
    notes: str = Field(default="", description="备注")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class Department(BaseModel):
    """科室模型"""
    department_id: str = Field(..., description="科室ID")
    name: str = Field(..., description="科室名称")
    description: str = Field(default="", description="科室描述")
    head_doctor: str = Field(default="", description="科室主任")
    products_used: List[str] = Field(default_factory=list, description="使用的产品ID列表")
    competitors_used: List[str] = Field(default_factory=list, description="使用的竞品ID列表")
    notes: str = Field(default="", description="备注")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class Hospital(BaseModel):
    """医院模型"""
    hospital_id: str = Field(..., description="医院ID")
    name: str = Field(..., description="医院名称")
    level: str = Field(default="", description="医院等级（三甲、二甲等）")
    address: str = Field(default="", description="地址")
    contact_phone: str = Field(default="", description="联系电话")
    departments: List[str] = Field(default_factory=list, description="科室ID列表")
    key_products: List[str] = Field(default_factory=list, description="重点产品ID列表")
    competitors: List[str] = Field(default_factory=list, description="竞品ID列表")
    notes: str = Field(default="", description="备注")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


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


class AssociationQuery(BaseModel):
    """关联查询结果"""
    associations: List[ProductAssociation] = Field(default_factory=list)
    total_count: int = Field(default=0, description="总数量")
    query_type: str = Field(..., description="查询类型：by_product/by_hospital/by_department")


class AssociationStatistics(BaseModel):
    """关联统计数据"""
    product_stats: Dict[str, int] = Field(default_factory=dict, description="产品统计：{product_id: count}")
    hospital_stats: Dict[str, int] = Field(default_factory=dict, description="医院统计：{hospital_id: count}")
    department_stats: Dict[str, int] = Field(default_factory=dict, description="科室统计：{department_id: count}")
    total_associations: int = Field(default=0, description="总关联数")


class BatchOperationResult(BaseModel):
    """批量操作结果"""
    success_count: int = Field(default=0, description="成功数量")
    failed_count: int = Field(default=0, description="失败数量")
    skipped_count: int = Field(default=0, description="跳过数量")
    error_messages: List[str] = Field(default_factory=list, description="错误信息列表")
