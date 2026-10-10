"""
个人成长反思服务
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from core.file_manager import file_manager
from core.data_models import Reflection, VisibilityLevel


class PersonalGrowthService:
    """个人成长反思服务"""
    
    def __init__(self):
        self.fm = file_manager
    
    def create_reflection(
        self,
        date: Optional[str] = None,
        today_score: int = 5,
        anxiety_source: str = "",
        achievement: str = "",
        weakness: str = "",
        avoidance: str = "",
        breakthrough: str = "",
        learning: str = "",
        improvement_goal: str = "",
        notes: str = ""
    ) -> Reflection:
        """创建反思记录"""
        
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        reflection_id = f"reflection_{date}"
        
        reflection = Reflection(
            reflection_id=reflection_id,
            date=date,
            today_score=today_score,
            anxiety_source=anxiety_source,
            achievement=achievement,
            weakness=weakness,
            avoidance=avoidance,
            breakthrough=breakthrough,
            learning=learning,
            improvement_goal=improvement_goal,
            notes=notes,
            visibility=VisibilityLevel.PRIVATE  # 始终私有
        )
        
        # 保存
        self.fm.save_model(self.fm.reflections_dir, reflection, reflection_id)
        
        return reflection
    
    def get_reflection(self, date: str) -> Optional[Reflection]:
        """获取指定日期的反思"""
        reflection_id = f"reflection_{date}"
        return self.fm.load_model(
            self.fm.reflections_dir,
            reflection_id,
            Reflection
        )
    
    def get_today_reflection(self) -> Optional[Reflection]:
        """获取今日反思"""
        today = datetime.now().strftime("%Y-%m-%d")
        return self.get_reflection(today)
    
    def list_reflections(self, limit: int = 30) -> List[Dict[str, Any]]:
        """列出反思记录"""
        reflections = []
        for filename in self.fm.list_files(self.fm.reflections_dir):
            data = self.fm.read_json(self.fm.reflections_dir / f"{filename}.json")
            if data:
                reflections.append(data)
        
        # 按日期排序
        reflections.sort(key=lambda x: x.get("date", ""), reverse=True)
        return reflections[:limit]
    
    def update_reflection(self, date: str, updates: Dict[str, Any]) -> Optional[Reflection]:
        """更新反思记录"""
        reflection_id = f"reflection_{date}"
        reflection_path = self.fm.reflections_dir / f"{reflection_id}.json"
        data = self.fm.read_json(reflection_path)
        
        if not data:
            return None
        
        # 更新字段
        for key, value in updates.items():
            if key in data and key != "visibility":  # 不允许更改可见性
                data[key] = value
        
        self.fm.write_json(reflection_path, data)
        
        return Reflection(**data)
    
    def get_growth_summary(self, days: int = 30) -> Dict[str, Any]:
        """获取成长总结"""
        reflections = self.list_reflections(days)
        
        total = len(reflections)
        achievements = sum(1 for r in reflections if r.get("achievement"))
        learnings = sum(1 for r in reflections if r.get("learning"))
        breakthroughs = sum(1 for r in reflections if r.get("breakthrough"))
        
        # 提取所有改进目标
        goals = []
        for r in reflections:
            goal = r.get("improvement_goal", "")
            if goal and goal not in goals:
                goals.append(goal)
        
        return {
            "period_days": days,
            "total_reflections": total,
            "days_with_achievement": achievements,
            "days_with_learning": learnings,
            "days_with_breakthrough": breakthroughs,
            "recent_goals": goals[:5],
            "consistency_rate": f"{(total / days * 100):.1f}%" if days > 0 else "0%"
        }
    
    def get_improvement_trends(self) -> Dict[str, List[str]]:
        """获取改进趋势"""
        reflections = self.list_reflections(30)
        
        trends = {
            "weaknesses": [],
            "avoidances": [],
            "breakthroughs": [],
            "learnings": []
        }
        
        for r in reflections:
            if r.get("weakness"):
                trends["weaknesses"].append(r["weakness"])
            if r.get("avoidance"):
                trends["avoidances"].append(r["avoidance"])
            if r.get("breakthrough"):
                trends["breakthroughs"].append(r["breakthrough"])
            if r.get("learning"):
                trends["learnings"].append(r["learning"])
        
        return trends
    
    def has_reflected_today(self) -> bool:
        """检查今天是否已反思"""
        return self.get_today_reflection() is not None


# 创建全局实例
personal_growth_service = PersonalGrowthService()
