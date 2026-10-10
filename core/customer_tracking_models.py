"""
客户追踪管理数据模型
基于销售管理的4张表格理念
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class DevelopmentChannel(str, Enum):
    """开发渠道"""
    ACADEMIC_CONFERENCE = "学术会议"
    REFERRAL = "转介绍"
    COLD_CALL = "陌生拜访"
    ONLINE = "线上渠道"
    HOSPITAL_VISIT = "医院驻点"
    PHARMACY = "药房推荐"
    OTHER = "其他"


class CustomerLevel(str, Enum):
    """客户分类"""
    A = "A类"  # 有意愿有需求，保持紧密联系
    B = "B类"  # 偶尔回复，当下需求不明确
    C = "C类"  # 偶尔回祝福，不回产品信息
    D = "D类"  # 不回复，像死人一样
    UNCLASSIFIED = "未分类"


class FollowUpStatus(str, Enum):
    """跟进状态"""
    PENDING = "待跟进"
    FOLLOWING = "跟进中"
    REPLIED = "已回复"
    NO_REPLY = "未回复"
    CLOSED = "已成交"
    LOST = "已流失"


# ==================== 表1：客户开发表 ====================

class CustomerDevelopment(BaseModel):
    """客户开发记录"""
    record_id: str = Field(..., description="记录ID")
    doctor_id: str = Field(..., description="医生ID")
    doctor_name: str = Field(..., description="医生姓名")
    hospital: str = Field(default="", description="医院名称")
    department: str = Field(default="", description="科室")
    
    # 开发信息
    development_channel: DevelopmentChannel = Field(..., description="开发渠道")
    channel_detail: str = Field(default="", description="渠道详情（如：XX学术会议）")
    referrer: str = Field(default="", description="推荐人")
    
    # 联系信息
    phone: str = Field(default="", description="电话")
    wechat: str = Field(default="", description="微信号")
    
    # 时间节点
    first_contact_date: Optional[datetime] = Field(default=None, description="首次联系时间")
    phone_connected_date: Optional[datetime] = Field(default=None, description="电话打通时间")
    wechat_added_date: Optional[datetime] = Field(default=None, description="添加微信时间")
    group_created_date: Optional[datetime] = Field(default=None, description="建群时间")
    
    # 客户实力评估
    hospital_level: str = Field(default="", description="医院等级")
    doctor_influence: str = Field(default="", description="医生影响力（高/中/低）")
    prescription_volume: str = Field(default="", description="处方量评估")
    
    # 备注
    notes: str = Field(default="", description="备注")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


# ==================== 表2：客户追踪表 ====================

class FollowUpRecord(BaseModel):
    """跟进记录"""
    follow_id: str = Field(..., description="跟进记录ID")
    doctor_id: str = Field(..., description="医生ID")
    doctor_name: str = Field(..., description="医生姓名")
    
    # 跟进信息
    follow_date: datetime = Field(default_factory=datetime.now, description="跟进时间")
    follow_method: str = Field(default="微信", description="跟进方式（微信/电话/拜访）")
    opening_script: str = Field(default="", description="开口话术")
    content: str = Field(..., description="沟通内容")
    
    # 客户反馈
    customer_replied: bool = Field(default=False, description="客户是否回复")
    reply_content: str = Field(default="", description="回复内容")
    reply_date: Optional[datetime] = Field(default=None, description="回复时间")
    days_no_reply: int = Field(default=0, description="未回复天数")
    
    # 下次跟进
    next_follow_date: Optional[datetime] = Field(default=None, description="下次跟进时间")
    follow_status: FollowUpStatus = Field(default=FollowUpStatus.PENDING, description="跟进状态")
    
    # 效果评估
    effect_score: int = Field(default=3, description="效果评分（1-5分）")
    notes: str = Field(default="", description="备注")
    created_at: datetime = Field(default_factory=datetime.now)


# ==================== 表3：客户分类表 ====================

class CustomerClassification(BaseModel):
    """客户分类记录"""
    classification_id: str = Field(..., description="分类记录ID")
    doctor_id: str = Field(..., description="医生ID")
    doctor_name: str = Field(..., description="医生姓名")
    hospital: str = Field(default="", description="医院")
    department: str = Field(default="", description="科室")
    
    # 分类信息
    customer_level: CustomerLevel = Field(default=CustomerLevel.UNCLASSIFIED, description="客户等级")
    level_reason: str = Field(default="", description="分类原因")
    
    # 跟进频率（根据等级自动建议）
    suggested_follow_days: int = Field(default=15, description="建议跟进间隔（天）")
    # A类：3-5天，B类：7天，C类：10天，D类：15天
    
    # 客户特征
    has_demand: bool = Field(default=False, description="是否有需求")
    has_intention: bool = Field(default=False, description="是否有意愿")
    reply_frequency: str = Field(default="", description="回复频率（经常/偶尔/从不）")
    
    # 价值评估
    potential_value: str = Field(default="", description="潜在价值（高/中/低）")
    priority: int = Field(default=3, description="优先级（1-5，5最高）")
    
    # 升降级记录
    last_level: Optional[CustomerLevel] = Field(default=None, description="上次等级")
    level_change_date: Optional[datetime] = Field(default=None, description="等级变更时间")
    level_change_reason: str = Field(default="", description="变更原因")
    
    # 统计数据
    total_contacts: int = Field(default=0, description="总联系次数")
    reply_count: int = Field(default=0, description="回复次数")
    reply_rate: float = Field(default=0.0, description="回复率")
    last_contact_date: Optional[datetime] = Field(default=None, description="最后联系时间")
    
    notes: str = Field(default="", description="备注")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


# ==================== 表4：统计分析表 ====================

class CustomerStatistics(BaseModel):
    """客户统计数据"""
    stat_id: str = Field(..., description="统计ID")
    period: str = Field(..., description="统计周期（周/月）")
    start_date: datetime = Field(..., description="开始日期")
    end_date: datetime = Field(..., description="结束日期")
    
    # 新增客户
    new_customers: int = Field(default=0, description="新增客户数")
    new_customer_list: List[str] = Field(default_factory=list, description="新增客户ID列表")
    
    # 客户分类统计
    a_level_count: int = Field(default=0, description="A类客户数")
    b_level_count: int = Field(default=0, description="B类客户数")
    c_level_count: int = Field(default=0, description="C类客户数")
    d_level_count: int = Field(default=0, description="D类客户数")
    
    # 客户变化
    a_level_increase: int = Field(default=0, description="A类客户增长数")
    a_level_decrease: int = Field(default=0, description="A类客户减少数")
    upgraded_customers: List[str] = Field(default_factory=list, description="升级客户列表")
    downgraded_customers: List[str] = Field(default_factory=list, description="降级客户列表")
    
    # 跟进统计
    total_follow_ups: int = Field(default=0, description="总跟进次数")
    reply_count: int = Field(default=0, description="回复次数")
    reply_rate: float = Field(default=0.0, description="回复率")
    
    # 渠道统计
    channel_stats: Dict[str, int] = Field(default_factory=dict, description="渠道统计")
    
    # 目标达成
    target_new_customers: int = Field(default=0, description="目标新增客户")
    target_a_level: int = Field(default=0, description="目标A类客户")
    achievement_rate: float = Field(default=0.0, description="目标达成率")
    
    notes: str = Field(default="", description="备注")
    created_at: datetime = Field(default_factory=datetime.now)


# ==================== 导出配置 ====================

class ExportConfig(BaseModel):
    """导出配置"""
    export_type: str = Field(..., description="导出类型（development/followup/classification/statistics）")
    start_date: Optional[datetime] = Field(default=None, description="开始日期")
    end_date: Optional[datetime] = Field(default=None, description="结束日期")
    customer_levels: List[CustomerLevel] = Field(default_factory=list, description="筛选客户等级")
    include_fields: List[str] = Field(default_factory=list, description="包含字段")
    file_format: str = Field(default="excel", description="文件格式（excel/csv）")
