"""
准备包导出服务
将医生信息、知识库、历史记录等整合为可导出的准备材料
"""
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple
from pathlib import Path

from core.file_manager import file_manager
from core.ai_integration import ai_integration


class PreparationPackageService:
    """准备包导出服务"""
    
    def __init__(self):
        self.fm = file_manager
        self.ai = ai_integration
        self.exports_dir = self.fm.output_dir / "preparation_packages"
        self.exports_dir.mkdir(parents=True, exist_ok=True)
    
    async def generate_package(
        self,
        contact_id: str,
        contact_type: str = "doctor",
        visit_date: str = None,
        visit_goal: str = "",
        include_knowledge: bool = True,
        include_history: bool = True,
        include_ai_suggestions: bool = True
    ) -> Tuple[str, str]:
        """
        生成准备包
        
        Returns:
            (文件路径, Markdown内容)
        """
        if not visit_date:
            visit_date = datetime.now().strftime("%Y-%m-%d")
        
        # 获取联系人信息
        contact_info = self._get_contact_info(contact_id, contact_type)
        
        # 获取历史拜访记录
        visit_history = []
        if include_history:
            visit_history = self._get_visit_history(contact_id, contact_type)
        
        # 获取相关知识
        related_knowledge = []
        if include_knowledge:
            related_knowledge = self._get_related_knowledge(contact_info)
        
        # AI 建议
        ai_suggestions = ""
        if include_ai_suggestions and self.ai.is_enabled:
            ai_suggestions = await self._generate_ai_suggestions(
                contact_info, visit_history, visit_goal
            )
        
        # 生成 Markdown
        content = self._build_markdown(
            contact_info=contact_info,
            visit_date=visit_date,
            visit_goal=visit_goal,
            visit_history=visit_history,
            related_knowledge=related_knowledge,
            ai_suggestions=ai_suggestions
        )
        
        # 保存文件
        contact_name = contact_info.get('name', contact_id)
        filename = f"准备包_{contact_name}_{visit_date}.md"
        filepath = self.exports_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return str(filepath), content
    
    def _get_contact_info(self, contact_id: str, contact_type: str) -> Dict[str, Any]:
        """获取联系人信息"""
        if contact_type == "doctor":
            data = self.fm.read_json(self.fm.doctors_dir / f"{contact_id}.json")
        else:
            contacts_dir = self.fm.data_dir / "contacts"
            data = self.fm.read_json(contacts_dir / f"{contact_id}.json")
        
        return data or {"name": contact_id, "contact_id": contact_id}
    
    def _get_visit_history(self, contact_id: str, contact_type: str = "doctor") -> List[Dict]:
        """获取历史拜访/交流记录"""
        history = []
        
        # 查找拜访记录
        for filename in self.fm.list_files(self.fm.visits_dir):
            if contact_id in filename:
                data = self.fm.read_json(self.fm.visits_dir / f"{filename}.json")
                if data:
                    history.append(data)
        
        # 查找交流记录
        interactions_dir = self.fm.data_dir / "interactions"
        if interactions_dir.exists():
            for filename in self.fm.list_files(interactions_dir):
                data = self.fm.read_json(interactions_dir / f"{filename}.json")
                if data and data.get("contact_id") == contact_id:
                    history.append(data)
        
        # 按日期排序
        history.sort(key=lambda x: x.get("visit_date", x.get("date", "")), reverse=True)
        return history[:10]  # 最近10次
    
    def _get_related_knowledge(self, contact_info: Dict) -> List[Dict]:
        """获取相关知识库内容"""
        knowledge = []
        
        # 根据联系人的兴趣/专业领域搜索
        interests = contact_info.get("interests", [])
        department = contact_info.get("department", "")
        
        # 搜索知识库
        for category_dir in [self.fm.diseases_dir, self.fm.products_dir, self.fm.market_dir]:
            if not category_dir.exists():
                continue
            for filename in self.fm.list_files(category_dir):
                data = self.fm.read_json(category_dir / f"{filename}.json")
                if data:
                    # 检查是否相关
                    title = data.get("title", "").lower()
                    keywords = [k.lower() for k in data.get("keywords", [])]
                    
                    is_related = False
                    for interest in interests:
                        if interest.lower() in title or interest.lower() in keywords:
                            is_related = True
                            break
                    
                    if department and department.lower() in title:
                        is_related = True
                    
                    if is_related:
                        knowledge.append(data)
        
        return knowledge[:5]  # 最多5条
    
    async def _generate_ai_suggestions(
        self, 
        contact_info: Dict, 
        visit_history: List[Dict],
        visit_goal: str
    ) -> str:
        """生成 AI 拜访建议"""
        if not self.ai.is_enabled:
            return ""
        
        # 构建上下文
        history_summary = ""
        if visit_history:
            recent = visit_history[0]
            history_summary = f"""
上次拜访日期: {recent.get('visit_date', recent.get('date', '未知'))}
上次话题: {recent.get('key_topics', '未记录')}
上次待跟进: {recent.get('follow_up_tasks', '无')}
历史拜访次数: {len(visit_history)}
"""
        
        prompt = f"""请为以下拜访提供准备建议（150字以内）：

联系人: {contact_info.get('name', '未知')}
类型: {contact_info.get('contact_type', '医生')}
科室: {contact_info.get('department', '未知')}
兴趣领域: {', '.join(contact_info.get('interests', []))}
决策风格: {contact_info.get('decision_style', '未知')}
关系阶段: {contact_info.get('relationship_stage', '初识')}

本次拜访目标: {visit_goal or '未设定'}

{history_summary}

请给出：
1. 开场建议
2. 重点话题
3. 注意事项
"""
        
        return await self.ai._make_request([
            {"role": "system", "content": "你是专业的医药代表教练，提供简洁实用的拜访建议。"},
            {"role": "user", "content": prompt}
        ], temperature=0.5, max_tokens=300) or ""
    
    def _build_markdown(
        self,
        contact_info: Dict,
        visit_date: str,
        visit_goal: str,
        visit_history: List[Dict],
        related_knowledge: List[Dict],
        ai_suggestions: str
    ) -> str:
        """构建 Markdown 内容"""
        
        name = contact_info.get('name', '未知')
        
        content = f"""# 📋 拜访准备包

## 基本信息

| 项目 | 内容 |
|------|------|
| **拜访对象** | {name} |
| **类型** | {contact_info.get('contact_type', '医生')} |
| **机构** | {contact_info.get('hospital', contact_info.get('organization', '未知'))} |
| **科室** | {contact_info.get('department', '未知')} |
| **职称** | {contact_info.get('title', '未知')} |
| **计划日期** | {visit_date} |

---

## 🎯 本次目标

{visit_goal if visit_goal else '（请在拜访前明确目标）'}

---

## 👤 联系人画像

- **兴趣领域**: {', '.join(contact_info.get('interests', ['未记录']))}
- **决策风格**: {contact_info.get('decision_style', '未知')}
- **关系阶段**: {contact_info.get('relationship_stage', '初识')}
- **未满足需求**: {contact_info.get('unmet_needs', '未记录')}

### 备注
{contact_info.get('notes', '无')}

"""
        
        # 历史记录
        if visit_history:
            content += """---

## 📅 历史拜访记录

"""
            for i, record in enumerate(visit_history[:3], 1):
                date = record.get('visit_date', record.get('date', '未知'))
                topics = record.get('key_topics', '未记录')
                followup = record.get('follow_up_tasks', '无')
                effectiveness = record.get('response_effectiveness', 3)
                
                content += f"""### 第{i}次 ({date})
- **话题**: {topics[:100]}...
- **待跟进**: {followup[:80]}...
- **有效性**: {'⭐' * effectiveness}

"""
        
        # 相关知识
        if related_knowledge:
            content += """---

## 📚 相关知识要点

"""
            for item in related_knowledge:
                content += f"""### {item.get('title', '无标题')}
{item.get('content', '')[:200]}...

"""
        
        # AI 建议
        if ai_suggestions:
            content += f"""---

## 🤖 AI 拜访建议

{ai_suggestions}

"""
        
        # 底部
        content += f"""---

*生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}*
*祝拜访顺利！知己知彼，百战不殆！*
"""
        
        return content
    
    def list_packages(self) -> List[Dict]:
        """列出所有准备包"""
        packages = []
        for filepath in self.exports_dir.glob("*.md"):
            packages.append({
                "filename": filepath.name,
                "path": str(filepath),
                "created": datetime.fromtimestamp(filepath.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
            })
        return sorted(packages, key=lambda x: x['created'], reverse=True)


# 创建全局实例
preparation_package_service = PreparationPackageService()
