"""
通用联系人管理服务
支持医生、护士、护士长、同事、主管等多种类型
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from core.file_manager import file_manager
from core.data_models import Contact, ContactType, RelationshipStage, DecisionStyle, Interaction
from core.ai_integration import ai_integration


class ContactService:
    """联系人管理服务"""
    
    def __init__(self):
        self.fm = file_manager
        self.ai = ai_integration
        
        # 确保联系人和交流记录目录存在
        self.contacts_dir = self.fm.data_dir / "contacts"
        self.interactions_dir = self.fm.data_dir / "interactions"
        self.contacts_dir.mkdir(parents=True, exist_ok=True)
        self.interactions_dir.mkdir(parents=True, exist_ok=True)
    
    # ==================== 联系人管理 ====================
    
    def create_contact(
        self,
        name: str,
        contact_type: str = "其他",
        organization: str = "",
        department: str = "",
        title: str = "",
        interests: List[str] = None,
        decision_style: Optional[str] = None,
        relationship_stage: str = "初识",
        tags: List[str] = None,
        notes: str = "",
        contact_id: Optional[str] = None
    ) -> Contact:
        """创建或更新联系人"""
        
        if not contact_id:
            contact_id = f"contact_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        contact = Contact(
            contact_id=contact_id,
            name=name,
            contact_type=contact_type,
            organization=organization,
            department=department,
            title=title,
            interests=interests or [],
            decision_style=decision_style,
            relationship_stage=relationship_stage,
            tags=tags or [],
            notes=notes
        )
        
        self.fm.save_model(self.contacts_dir, contact, contact_id)
        return contact
    
    def get_contact(self, contact_id: str) -> Optional[Contact]:
        """获取联系人"""
        return self.fm.load_model(self.contacts_dir, contact_id, Contact)
    
    def update_contact(self, contact_id: str, updates: Dict[str, Any]) -> Optional[Contact]:
        """更新联系人"""
        contact_path = self.contacts_dir / f"{contact_id}.json"
        data = self.fm.read_json(contact_path)
        
        if not data:
            return None
        
        for key, value in updates.items():
            if key in data:
                data[key] = value
        
        data["updated_at"] = datetime.now().isoformat()
        self.fm.write_json(contact_path, data)
        
        return Contact(**data)
    
    def delete_contact(self, contact_id: str) -> bool:
        """删除联系人"""
        return self.fm.delete_file(self.contacts_dir, contact_id)
    
    def list_contacts(self, contact_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """列出联系人"""
        contacts = []
        for filename in self.fm.list_files(self.contacts_dir):
            data = self.fm.read_json(self.contacts_dir / f"{filename}.json")
            if data:
                if contact_type is None or data.get("contact_type") == contact_type:
                    contacts.append(data)
        
        return sorted(contacts, key=lambda x: x.get("name", ""))
    
    def search_contacts(self, keyword: str) -> List[Dict[str, Any]]:
        """搜索联系人"""
        results = self.fm.search_files(self.contacts_dir, keyword)
        return [r["data"] for r in results]
    
    def get_contacts_by_tag(self, tag: str) -> List[Dict[str, Any]]:
        """按标签获取联系人"""
        contacts = []
        for contact in self.list_contacts():
            if tag in contact.get("tags", []):
                contacts.append(contact)
        return contacts
    
    # ==================== 交流记录管理 ====================
    
    def create_interaction(
        self,
        contact_id: str,
        contact_type: str,
        contact_name: str,
        date: str,
        key_topics: str = "",
        their_concerns: str = "",
        objections: str = "",
        my_responses: str = "",
        response_effectiveness: int = 3,
        emotional_tone: str = "",
        insights: str = "",
        follow_up_tasks: str = "",
        related_contacts: List[str] = None,
        tags: List[str] = None,
        notes: str = ""
    ) -> Interaction:
        """创建交流记录"""
        
        interaction_id = f"interaction_{date}_{contact_id}"
        
        interaction = Interaction(
            interaction_id=interaction_id,
            contact_id=contact_id,
            contact_type=contact_type,
            contact_name=contact_name,
            date=date,
            key_topics=key_topics,
            their_concerns=their_concerns,
            objections=objections,
            my_responses=my_responses,
            response_effectiveness=response_effectiveness,
            emotional_tone=emotional_tone,
            insights=insights,
            follow_up_tasks=follow_up_tasks,
            related_contacts=related_contacts or [],
            tags=tags or [],
            notes=notes
        )
        
        # AI 生成摘要
        if self.ai.is_enabled:
            summary = self._generate_interaction_summary(interaction)
            if summary:
                interaction.ai_summary = summary
        
        self.fm.save_model(self.interactions_dir, interaction, interaction_id)
        return interaction
    
    def get_interaction(self, interaction_id: str) -> Optional[Interaction]:
        """获取交流记录"""
        return self.fm.load_model(self.interactions_dir, interaction_id, Interaction)
    
    def list_interactions(
        self, 
        contact_id: Optional[str] = None,
        contact_type: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """列出交流记录"""
        interactions = []
        for filename in self.fm.list_files(self.interactions_dir):
            data = self.fm.read_json(self.interactions_dir / f"{filename}.json")
            if data:
                if contact_id and data.get("contact_id") != contact_id:
                    continue
                if contact_type and data.get("contact_type") != contact_type:
                    continue
                interactions.append(data)
        
        interactions.sort(key=lambda x: x.get("date", ""), reverse=True)
        return interactions[:limit]
    
    def _generate_interaction_summary(self, interaction: Interaction) -> Optional[str]:
        """生成交流摘要"""
        prompt = f"""请为以下交流记录生成简洁摘要（50-100字）：

联系人类型：{interaction.contact_type}
日期：{interaction.date}
话题：{interaction.key_topics}
对方顾虑：{interaction.their_concerns}
我的回应：{interaction.my_responses}
新发现：{interaction.insights}

摘要："""
        
        return self.ai._make_request([
            {"role": "user", "content": prompt}
        ], temperature=0.3, max_tokens=150)
    
    # ==================== 关联分析 ====================
    
    def find_related_contacts(self, contact_id: str) -> List[Dict[str, Any]]:
        """查找相关联系人"""
        related = []
        
        # 获取该联系人的所有交流记录
        interactions = self.list_interactions(contact_id=contact_id)
        
        # 收集所有相关联系人ID
        related_ids = set()
        for interaction in interactions:
            related_ids.update(interaction.get("related_contacts", []))
        
        # 获取联系人详情
        for rid in related_ids:
            contact = self.get_contact(rid)
            if contact:
                related.append(contact.model_dump())
        
        return related
    
    def get_interaction_history(self, contact_id: str) -> List[Dict[str, Any]]:
        """获取与某联系人的交流历史（用于进步追踪）"""
        return self.list_interactions(contact_id=contact_id, limit=100)
    
    def analyze_progress(self, contact_id: str) -> Optional[str]:
        """分析与联系人的关系进步"""
        if not self.ai.is_enabled:
            return None
        
        contact = self.get_contact(contact_id)
        if not contact:
            return None
        
        interactions = self.get_interaction_history(contact_id)
        if not interactions:
            return "暂无交流记录，无法分析进步。"
        
        # 构建分析请求
        history_summary = "\n".join([
            f"[{i['date']}] 有效性:{i.get('response_effectiveness', 3)}/5 - {i.get('key_topics', '')[:50]}"
            for i in interactions[:10]
        ])
        
        prompt = f"""分析与以下联系人的关系发展进步：

联系人：{contact.name} ({contact.contact_type})
当前关系阶段：{contact.relationship_stage}

交流历史：
{history_summary}

请分析：
1. 关系发展趋势（进步/停滞/退步）
2. 沟通效果变化
3. 下一步建议"""
        
        return self.ai._make_request([
            {"role": "system", "content": "你是一位专业的人际关系教练。"},
            {"role": "user", "content": prompt}
        ], temperature=0.5, max_tokens=500)


# 创建全局实例
contact_service = ContactService()
