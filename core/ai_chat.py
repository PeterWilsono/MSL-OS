"""
AI 对话服务
支持对话记忆、上下文压缩和多会话管理
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path
import json

from .file_manager import file_manager
from .ai_integration import ai_integration
from .data_models import ChatSession, ChatMessage
from .ai_data_analyzer import ai_data_analyzer


class AIChatService:
    """AI 对话服务"""
    
    # 保留最近对话数量（完整保留）
    MAX_RECENT_MESSAGES = 10
    # 记忆摘要最大数量
    MAX_MEMORIES = 20
    
    def __init__(self):
        self.fm = file_manager
        self.ai = ai_integration
        
        # 确保会话目录存在
        self.sessions_dir = self.fm.data_dir / "chat_sessions"
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
    
    def new_session(self, title: str = "新对话") -> ChatSession:
        """创建新会话"""
        session_id = f"chat_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        session = ChatSession(
            session_id=session_id,
            title=title,
            messages=[],
            key_memories=[],
            context_summary=""
        )
        
        self._save_session(session)
        return session
    
    def get_session(self, session_id: str) -> Optional[ChatSession]:
        """获取会话"""
        session_path = self.sessions_dir / f"{session_id}.json"
        data = self.fm.read_json(session_path)
        if data:
            # 重建消息对象
            if "messages" in data:
                data["messages"] = [
                    ChatMessage(**msg) if isinstance(msg, dict) else msg
                    for msg in data["messages"]
                ]
            return ChatSession(**data)
        return None
    
    def list_sessions(self) -> List[Dict[str, Any]]:
        """列出所有会话"""
        sessions = []
        for filename in self.fm.list_files(self.sessions_dir):
            data = self.fm.read_json(self.sessions_dir / f"{filename}.json")
            if data:
                sessions.append({
                    "session_id": data.get("session_id"),
                    "title": data.get("title", "未命名"),
                    "message_count": len(data.get("messages", [])),
                    "created_at": data.get("created_at"),
                    "updated_at": data.get("updated_at")
                })
        
        return sorted(sessions, key=lambda x: x.get("updated_at", ""), reverse=True)
    
    def delete_session(self, session_id: str) -> bool:
        """删除会话"""
        return self.fm.delete_file(self.sessions_dir, session_id)
    
    async def chat(self, session_id: str, user_message: str) -> str:
        """
        发送消息并获取回复 (异步)
        """
        if not self.ai.is_enabled:
            return "❌ AI 功能未启用，请在设置中配置 API Key 并开启 AI。"
        
        session = self.get_session(session_id)
        if not session:
            return "❌ 会话不存在"
        
        # 添加用户消息
        session.messages.append(ChatMessage(
            role="user",
            content=user_message
        ))
        
        # 构建上下文
        context_messages = self._build_context(session)
        
        # 获取当前数据上下文
        data_context = self._get_data_context()
        
        # 系统提示
        system_prompt = f"""你是一位专业的医药代表职业教练，帮助用户：
1. 分析拜访策略和沟通技巧
2. 理解医生、护士、同事等不同角色的特点
3. 发现数据之间的关联和模式
4. 提供具体、可操作的指导建议
5. 追踪进步并给予鼓励

你有权访问用户的工作数据：
{data_context}

重要能力：
- 当用户询问某个医院、科室或医生时，你可以说"让我分析一下这个医院/科室/医生"，系统会自动调用AI分析功能
- 分析结果会被缓存，避免重复分析浪费token
- 你可以基于历史分析结果提供建议

重要记忆（请记住以下关键信息）：
{chr(10).join(session.key_memories) if session.key_memories else '暂无'}

之前对话的摘要：
{session.context_summary if session.context_summary else '这是新对话'}

请用简洁、专业的语言回复。回复控制在 300 字以内，除非用户要求详细分析。"""
        
        # 调用 API
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(context_messages)
        
        response = await self.ai._make_request(messages, temperature=0.7, max_tokens=1500)
        
        if not response:
            return "❌ AI 请求失败，请检查网络和 API 配置"
        
        # 添加助手回复
        session.messages.append(ChatMessage(
            role="assistant",
            content=response
        ))
        
        # 检查是否需要压缩上下文
        if len(session.messages) > self.MAX_RECENT_MESSAGES * 2:
            await self._compress_context(session)
        
        # 提取关键记忆
        if len(session.messages) % 5 == 0:  # 每5轮提取一次
            await self._extract_memories(session)
        
        # 更新会话
        session.updated_at = datetime.now()
        self._save_session(session)
        
        return response
    
    def _build_context(self, session: ChatSession) -> List[Dict[str, str]]:
        """构建对话上下文"""
        messages = []
        
        # 只取最近的消息
        recent_messages = session.messages[-self.MAX_RECENT_MESSAGES:]
        
        for msg in recent_messages:
            messages.append({
                "role": msg.role,
                "content": msg.content
            })
        
        return messages
    
    def _get_data_context(self) -> str:
        """获取当前数据上下文摘要（增强版）"""
        context_parts = []
        
        # 医院和科室统计
        hospitals_count = len(list((self.fm.data_dir / "hospitals").glob("*.json")))
        departments_count = len(list((self.fm.data_dir / "departments").glob("*.json")))
        products_count = len(list((self.fm.data_dir / "products").glob("*.json")))
        context_parts.append(f"- 医院: {hospitals_count}家, 科室: {departments_count}个, 产品: {products_count}个")
        
        # 产品列表（显示产品名称）
        if products_count > 0:
            products_dir = self.fm.data_dir / "products"
            product_names = []
            for product_file in list(products_dir.glob("*.json"))[:10]:  # 最多显示10个
                product_data = self.fm.read_json(product_file)
                if product_data:
                    product_names.append(product_data.get("name", "未命名"))
            if product_names:
                context_parts.append(f"- 产品列表: {', '.join(product_names)}")
        
        # 联系人统计
        doctors = self.fm.list_files(self.fm.doctors_dir)
        contacts_dir = self.fm.data_dir / "contacts"
        contacts = self.fm.list_files(contacts_dir) if contacts_dir.exists() else []
        context_parts.append(f"- 医生档案: {len(doctors)}人, 其他联系人: {len(contacts)}人")
        
        # 产品关联统计
        assoc_dir = self.fm.data_dir / "associations"
        if assoc_dir.exists():
            assoc_files = list(assoc_dir.glob("assoc_*.json"))
            context_parts.append(f"- 产品关联: {len(assoc_files)}条")
        
        # 最近拜访
        visits = self.fm.list_files(self.fm.visits_dir)
        context_parts.append(f"- 拜访记录: {len(visits)}条")
        
        # 待办事项
        from .analyzer import analyzer
        tasks = analyzer.get_pending_tasks()[:3]
        if tasks:
            context_parts.append(f"- 待办: {'; '.join(tasks[:3])}")
        
        # AI分析缓存状态
        cache_stats = ai_data_analyzer.get_cache_stats()
        if cache_stats.get("total_caches", 0) > 0:
            context_parts.append(f"- AI分析缓存: {cache_stats['total_caches']}个")
        
        return "\n".join(context_parts)
    
    async def _compress_context(self, session: ChatSession) -> None:
        """压缩上下文（将旧对话转为摘要）"""
        if not self.ai.is_enabled:
            return
        
        # 获取需要压缩的旧消息
        old_messages = session.messages[:-self.MAX_RECENT_MESSAGES]
        if not old_messages:
            return
        
        # 构建压缩请求
        conversation_text = "\n".join([
            f"{msg.role}: {msg.content}" for msg in old_messages
        ])
        
        prompt = f"""请将以下对话压缩为简洁的摘要（不超过200字），保留关键信息和重要决定：
{conversation_text}
摘要："""
        
        summary = await self.ai._make_request([
            {"role": "user", "content": prompt}
        ], temperature=0.3, max_tokens=300)
        
        if summary:
            # 合并新旧摘要
            if session.context_summary:
                session.context_summary = f"{session.context_summary}\n\n{summary}"
            else:
                session.context_summary = summary
            
            # 移除已压缩的消息
            session.messages = session.messages[-self.MAX_RECENT_MESSAGES:]
    
    async def _extract_memories(self, session: ChatSession) -> None:
        """提取关键记忆"""
        if not self.ai.is_enabled:
            return
        
        # 取最近的对话
        recent = session.messages[-6:]
        if len(recent) < 4:
            return
        
        conversation_text = "\n".join([
            f"{msg.role}: {msg.content}" for msg in recent
        ])
        
        prompt = f"""从以下对话中提取需要长期记住的关键信息（如用户的目标、重要决定、特定偏好等）。
If there is no info to remember, reply "None".
Each memory on a new line, max 3.

Dialogue:
{conversation_text}

Key Memories:"""
        
        memories = await self.ai._make_request([
            {"role": "user", "content": prompt}
        ], temperature=0.3, max_tokens=200)
        
        if memories and memories.strip() != "无":
            new_memories = [m.strip() for m in memories.split("\n") if m.strip() and m.strip() != "无"]
            
            # 添加新记忆，避免重复
            for mem in new_memories:
                if mem not in session.key_memories:
                    session.key_memories.append(mem)
            
            # 限制记忆数量
            if len(session.key_memories) > self.MAX_MEMORIES:
                session.key_memories = session.key_memories[-self.MAX_MEMORIES:]
    
    def _save_session(self, session: ChatSession) -> None:
        """保存会话"""
        session_path = self.sessions_dir / f"{session.session_id}.json"
        
        # 转换为可序列化格式
        data = session.model_dump()
        
        self.fm.write_json(session_path, data)
    
    def update_session_title(self, session_id: str, title: str) -> bool:
        """更新会话标题"""
        session = self.get_session(session_id)
        if session:
            session.title = title
            self._save_session(session)
            return True
        return False
    
    async def chat_with_analysis(
        self, 
        session_id: str, 
        user_message: str,
        entity_id: Optional[str] = None,
        entity_type: Optional[str] = None
    ) -> str:
        """
        带实体分析的对话（自动注入分析结果）
        
        Args:
            session_id: 会话ID
            user_message: 用户消息
            entity_id: 实体ID（医院/科室/医生）
            entity_type: 实体类型
            
        Returns:
            AI回复
        """
        if not self.ai.is_enabled:
            return "❌ AI 功能未启用，请在设置中配置 API Key 并开启 AI。"
        
        # 如果提供了实体信息，先获取分析
        analysis_context = ""
        if entity_id and entity_type:
            try:
                if entity_type == "hospital":
                    analysis = await ai_data_analyzer.analyze_hospital(entity_id)
                elif entity_type == "department":
                    analysis = await ai_data_analyzer.analyze_department(entity_id)
                elif entity_type == "doctor":
                    analysis = await ai_data_analyzer.analyze_doctor(entity_id)
                else:
                    analysis = None
                
                if analysis and "error" not in analysis:
                    cache_note = "（来自缓存）" if analysis.get("from_cache") else "（新分析）"
                    analysis_context = f"\n\n【AI分析{cache_note}】\n"
                    analysis_context += f"摘要：{analysis.get('summary', '')}\n"
                    if analysis.get('key_insights'):
                        analysis_context += f"关键洞察：\n" + "\n".join([f"- {i}" for i in analysis['key_insights'][:3]])
                    if analysis.get('recommendations'):
                        analysis_context += f"\n建议：\n" + "\n".join([f"- {r}" for r in analysis['recommendations'][:3]])
            except Exception as e:
                print(f"获取分析失败: {e}")
        
        # 将分析结果附加到用户消息
        enhanced_message = user_message
        if analysis_context:
            enhanced_message = f"{user_message}\n{analysis_context}"
        
        # 调用标准chat方法
        return await self.chat(session_id, enhanced_message)
    
    def get_session_history(self, session_id: str) -> List[Dict[str, str]]:
        """获取会话历史（用于UI显示）"""
        session = self.get_session(session_id)
        if not session:
            return []
        
        return [
            {
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat() if hasattr(msg, 'timestamp') else ""
            }
            for msg in session.messages
        ]


# 创建全局实例
ai_chat_service = AIChatService()
