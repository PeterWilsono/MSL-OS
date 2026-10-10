"""
决策引擎模块
生成每日行动建议和学习推荐
"""
from datetime import datetime
from typing import List, Dict, Any, Optional
from .file_manager import file_manager
from .analyzer import analyzer
from .ai_integration import ai_integration
from .data_models import DailyAction


class DecisionEngine:
    """决策引擎"""
    
    def __init__(self):
        self.fm = file_manager
        self.analyzer = analyzer
        self.ai = ai_integration
    
    async def generate_daily_action(self, date: Optional[str] = None) -> DailyAction:
        """
        生成每日行动单
        
        Args:
            date: 日期，默认为今天
            
        Returns:
            DailyAction 模型
        """
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        # 收集数据
        pending_tasks = self.analyzer.get_pending_tasks()
        neglected_doctors = self.analyzer.identify_neglected_doctors()
        growth_trend = self.analyzer.get_growth_trend(7)
        
        # 生成任务优先级
        top_tasks = self._prioritize_tasks(pending_tasks)
        
        # 推荐优先医生
        priority_doctor = self._suggest_priority_doctor(neglected_doctors)
        
        # 推荐学习主题
        learning_topic = self._suggest_learning_topic()
        
        # 改进重点
        improvement_focus = self._identify_improvement_focus(growth_trend)
        
        # AI 建议（如果启用）
        ai_suggestions = ""
        if self.ai.is_enabled:
            recent_visits = self.analyzer.get_recent_visits(7)
            recent_reflections = self._get_recent_reflections_safe()
            ai_suggestions = await self.ai.generate_daily_suggestions(
                recent_visits, pending_tasks, recent_reflections
            ) or ""
        
        action = DailyAction(
            date=date,
            top_tasks=top_tasks,
            priority_doctor=priority_doctor,
            recommended_learning_topic=learning_topic,
            key_improvement_focus=improvement_focus,
            ai_suggestions=ai_suggestions
        )
        
        # 保存行动单
        self.fm.save_model(
            self.fm.daily_tasks_dir,
            action,
            f"action_{date}"
        )
        
        return action
    
    def _prioritize_tasks(self, tasks: List[str]) -> List[str]:
        """任务优先级排序"""
        # 简单策略：优先处理带有"紧急"、"今日"、"明天"关键词的任务
        urgent_keywords = ["紧急", "今日", "明天", "尽快", "立即", "ASAP"]
        
        urgent = []
        normal = []
        
        for task in tasks:
            is_urgent = any(kw in task for kw in urgent_keywords)
            if is_urgent:
                urgent.append(task)
            else:
                normal.append(task)
        
        # 返回前3个任务
        return (urgent + normal)[:3]
    
    def _suggest_priority_doctor(self, neglected_doctors: List[str]) -> str:
        """推荐优先拜访医生"""
        if not neglected_doctors:
            return "无特别推荐"
        
        # 优先已建立关系但长时间未拜访的医生
        for doc_id in neglected_doctors:
            data = self.fm.read_json(self.fm.doctors_dir / f"{doc_id}.json")
            if data:
                stage = data.get("relationship_stage", "")
                if stage in ["建立中", "稳定", "深入"]:
                    return f"{data.get('name', doc_id)} ({stage})"
        
        # 否则返回第一个
        if neglected_doctors:
            data = self.fm.read_json(self.fm.doctors_dir / f"{neglected_doctors[0]}.json")
            if data:
                return data.get("name", neglected_doctors[0])
        
        return "无特别推荐"
    
    def _suggest_learning_topic(self) -> str:
        """推荐学习主题"""
        # 基于常见异议推荐
        objections = self.analyzer.analyze_common_objections()
        
        if objections:
            top_objection = list(objections.keys())[0]
            return f"针对异议：{top_objection[:30]}..."
        
        # 默认推荐
        default_topics = [
            "产品知识更新",
            "沟通技巧提升",
            "循证医学基础",
            "客户关系管理",
        ]
        
        import random
        return random.choice(default_topics)
    
    def _identify_improvement_focus(self, growth_trend: Dict[str, Any]) -> str:
        """识别改进重点"""
        if growth_trend["total_reflections"] == 0:
            return "建议：开始记录每日反思"
        
        if growth_trend["has_breakthroughs"] == 0:
            return "关注：寻找突破点和成长机会"
        
        if growth_trend["has_achievements"] < growth_trend["total_reflections"] / 2:
            return "建议：多关注和记录小成就"
        
        return "继续保持良好的反思习惯"
    
    def _get_recent_reflections_safe(self) -> List[Dict[str, Any]]:
        """获取最近反思（已移除敏感信息）"""
        from .privacy_manager import privacy_manager
        
        reflections = []
        for filename in self.fm.list_files(self.fm.reflections_dir)[-7:]:
            data = self.fm.read_json(self.fm.reflections_dir / f"{filename}.json")
            if data:
                # 过滤敏感信息
                safe_data = privacy_manager.sanitize_for_ai(data)
                reflections.append(safe_data)
        
        return reflections
    
    def get_today_action(self) -> Optional[DailyAction]:
        """获取今日行动单"""
        today = datetime.now().strftime("%Y-%m-%d")
        return self.fm.load_model(
            self.fm.daily_tasks_dir,
            f"action_{today}",
            DailyAction
        )
    
    def should_generate_new_action(self) -> bool:
        """检查是否需要生成新的行动单"""
        today_action = self.get_today_action()
        return today_action is None


# 创建全局实例
decision_engine = DecisionEngine()
