"""
数据模型定义
使用 Pydantic 进行数据验证和序列化
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum


class VisibilityLevel(str, Enum):
    """可见性级别"""
    PUBLIC = "public"
    PRIVATE = "private"


class RelationshipStage(str, Enum):
    """关系阶段"""
    UNKNOWN = "未知"
    FIRST_CONTACT = "初识"
    BUILDING = "建立中"
    STABLE = "稳定"
    DEEP = "深入"


class DecisionStyle(str, Enum):
    """决策风格"""
    EVIDENCE_BASED = "循证型"
    EXPERIENCE_BASED = "经验型"
    CONSERVATIVE = "保守型"
    INNOVATIVE = "创新型"
    RELATIONSHIP = "关系型"


class ContactType(str, Enum):
    """联系人类型"""
    DOCTOR = "医生"
    NURSE = "护士"
    HEAD_NURSE = "护士长"
    COLLEAGUE = "同事"
    SUPERVISOR = "主管"
    PHARMACIST = "药剂师"
    ADMIN = "行政人员"
    OTHER = "其他"


# ==================== 联系人（通用） ====================

class Contact(BaseModel):
    """通用联系人模型"""
    contact_id: str = Field(..., description="联系人唯一标识")
    name: str = Field(..., description="姓名")
    contact_type: ContactType = Field(default=ContactType.OTHER, description="联系人类型")
    organization: str = Field(default="", description="所属机构")
    department: str = Field(default="", description="部门/科室")
    title: str = Field(default="", description="职称/职位")
    interests: List[str] = Field(default_factory=list, description="兴趣/关注点")
    decision_style: Optional[DecisionStyle] = Field(default=None, description="决策风格")
    relationship_stage: RelationshipStage = Field(
        default=RelationshipStage.FIRST_CONTACT, 
        description="关系阶段"
    )
    tags: List[str] = Field(default_factory=list, description="标签（用于关联分析）")
    notes: str = Field(default="", description="备注")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        use_enum_values = True


# ==================== 医生（兼容旧模型） ====================

class Doctor(BaseModel):
    """医生信息模型"""
    doctor_id: str = Field(..., description="医生唯一标识")
    name: str = Field(..., description="医生姓名")
    hospital: str = Field(default="", description="医院名称")
    hospital_id: str = Field(default="", description="医院ID（关联）")
    department: str = Field(default="", description="科室")
    department_id: str = Field(default="", description="科室ID（关联）")
    title: str = Field(default="", description="职称")
    interests: List[str] = Field(default_factory=list, description="学术兴趣")
    decision_style: Optional[DecisionStyle] = Field(default=None, description="决策风格")
    prescription_pattern: str = Field(default="", description="处方习惯")
    unmet_needs: str = Field(default="", description="未满足需求")
    relationship_stage: RelationshipStage = Field(
        default=RelationshipStage.FIRST_CONTACT, 
        description="关系阶段"
    )
    tags: List[str] = Field(default_factory=list, description="标签")
    notes: str = Field(default="", description="备注")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        use_enum_values = True


# ==================== 交流记录（通用） ====================

class Interaction(BaseModel):
    """交流记录模型（通用，支持所有联系人类型）"""
    interaction_id: str = Field(..., description="交流记录ID")
    contact_id: str = Field(..., description="联系人ID")
    contact_type: ContactType = Field(default=ContactType.DOCTOR, description="联系人类型")
    contact_name: str = Field(default="", description="联系人姓名（冗余存储）")
    date: str = Field(..., description="交流日期 YYYY-MM-DD")
    key_topics: str = Field(default="", description="讨论的关键话题")
    their_concerns: str = Field(default="", description="对方的顾虑")
    objections: str = Field(default="", description="反对意见/异议")
    my_responses: str = Field(default="", description="我的回应")
    response_effectiveness: int = Field(default=3, ge=1, le=5, description="回应有效性1-5")
    emotional_tone: str = Field(default="", description="情绪氛围")
    insights: str = Field(default="", description="新发现/洞察/启发")
    follow_up_tasks: str = Field(default="", description="后续跟进任务")
    related_contacts: List[str] = Field(default_factory=list, description="相关联系人ID")
    tags: List[str] = Field(default_factory=list, description="标签（用于关联分析）")
    notes: str = Field(default="", description="备注")
    ai_summary: str = Field(default="", description="AI摘要")
    created_at: datetime = Field(default_factory=datetime.now)

    class Config:
        use_enum_values = True


# ==================== 拜访相关（兼容旧模型） ====================

class Preparation(BaseModel):
    """拜访前准备模型"""
    prep_id: str = Field(..., description="准备记录ID")
    doctor_id: str = Field(..., description="医生ID")
    contact_type: ContactType = Field(default=ContactType.DOCTOR, description="联系人类型")
    visit_date: str = Field(..., description="计划拜访日期 YYYY-MM-DD")
    last_visit_summary: str = Field(default="", description="上次拜访摘要")
    visit_goal: str = Field(default="", description="本次拜访目标")
    exploration_question: str = Field(default="", description="探索性问题")
    concerns: str = Field(default="", description="顾虑/担心")
    prepared_data: str = Field(default="", description="准备的资料/数据")
    key_messages: List[str] = Field(default_factory=list, description="关键信息点")
    notes: str = Field(default="", description="备注")
    created_at: datetime = Field(default_factory=datetime.now)

    class Config:
        use_enum_values = True


class Visit(BaseModel):
    """拜访记录模型"""
    visit_id: str = Field(..., description="拜访记录ID")
    doctor_id: str = Field(..., description="医生ID")
    contact_type: ContactType = Field(default=ContactType.DOCTOR, description="联系人类型")
    visit_date: str = Field(..., description="拜访日期 YYYY-MM-DD")
    key_topics: str = Field(default="", description="讨论的关键话题")
    doctor_concerns: str = Field(default="", description="医生的顾虑")
    objections: str = Field(default="", description="医生的反对意见")
    responses: str = Field(default="", description="我的回应")
    response_effectiveness: int = Field(
        default=3, 
        ge=1, le=5, 
        description="回应有效性 1-5分"
    )
    emotional_tone: str = Field(default="", description="情绪氛围")
    new_insights: str = Field(default="", description="新发现/洞察")
    follow_up_tasks: str = Field(default="", description="后续跟进任务")
    related_contacts: List[str] = Field(default_factory=list, description="相关联系人")
    tags: List[str] = Field(default_factory=list, description="标签")
    notes: str = Field(default="", description="备注")
    ai_summary: str = Field(default="", description="AI生成的摘要")
    created_at: datetime = Field(default_factory=datetime.now)

    class Config:
        use_enum_values = True


# ==================== 个人成长 ====================

class Reflection(BaseModel):
    """个人成长反思模型"""
    reflection_id: str = Field(..., description="反思记录ID")
    date: str = Field(..., description="日期 YYYY-MM-DD")
    today_score: int = Field(default=5, ge=1, le=10, description="今日自我评分")
    anxiety_source: str = Field(default="", description="焦虑来源")
    achievement: str = Field(default="", description="今日成就")
    weakness: str = Field(default="", description="暴露的弱点")
    avoidance: str = Field(default="", description="在逃避什么")
    breakthrough: str = Field(default="", description="突破点")
    learning: str = Field(default="", description="今日学习")
    improvement_goal: str = Field(default="", description="改进目标")
    notes: str = Field(default="", description="备注")
    visibility: VisibilityLevel = Field(
        default=VisibilityLevel.PRIVATE, 
        description="可见性(私有)"
    )
    created_at: datetime = Field(default_factory=datetime.now)

    class Config:
        use_enum_values = True


# ==================== AI 对话 ====================

class ChatMessage(BaseModel):
    """对话消息"""
    role: str = Field(..., description="角色: user/assistant")
    content: str = Field(..., description="消息内容")
    timestamp: datetime = Field(default_factory=datetime.now)


class ChatSession(BaseModel):
    """AI 对话会话"""
    session_id: str = Field(..., description="会话ID")
    title: str = Field(default="新对话", description="会话标题")
    messages: List[ChatMessage] = Field(default_factory=list, description="消息历史")
    key_memories: List[str] = Field(default_factory=list, description="关键记忆摘要")
    context_summary: str = Field(default="", description="上下文压缩摘要")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        use_enum_values = True


# ==================== 知识库 ====================

class KnowledgeCategory(str, Enum):
    """知识分类"""
    DISEASE = "disease"      # 病种
    PRODUCT = "product"      # 产品
    MARKET = "market"        # 市场问题


class KnowledgeItem(BaseModel):
    """知识条目模型"""
    item_id: str = Field(..., description="知识条目ID")
    category: KnowledgeCategory = Field(..., description="分类")
    title: str = Field(..., description="标题")
    content: str = Field(default="", description="内容")
    keywords: List[str] = Field(default_factory=list, description="关键词")
    source: str = Field(default="", description="来源")
    related_doctors: List[str] = Field(default_factory=list, description="相关医生ID")
    related_contacts: List[str] = Field(default_factory=list, description="相关联系人ID")
    tags: List[str] = Field(default_factory=list, description="标签")
    notes: str = Field(default="", description="备注")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        use_enum_values = True


# ==================== 每日行动 ====================

class DailyAction(BaseModel):
    """每日行动单模型"""
    date: str = Field(..., description="日期 YYYY-MM-DD")
    top_tasks: List[str] = Field(default_factory=list, description="今日重点任务")
    priority_doctor: str = Field(default="", description="优先拜访医生")
    recommended_learning_topic: str = Field(default="", description="推荐学习主题")
    key_improvement_focus: str = Field(default="", description="关键改进重点")
    ai_suggestions: str = Field(default="", description="AI建议")
    created_at: datetime = Field(default_factory=datetime.now)

    class Config:
        use_enum_values = True


# ==================== 系统配置 ====================

class SystemConfig(BaseModel):
    """系统配置模型"""
    ai_enabled: bool = Field(default=False, description="是否启用AI分析")
    deepseek_api_key: str = Field(default="", description="DeepSeek API Key")
    deepseek_base_url: str = Field(
        default="https://api.deepseek.com", 
        description="DeepSeek API地址"
    )
    deepseek_model: str = Field(
        default="deepseek-chat", 
        description="DeepSeek模型名称"
    )
    theme: str = Field(default="dark", description="界面主题")
    language: str = Field(default="zh-CN", description="语言")

    class Config:
        use_enum_values = True

