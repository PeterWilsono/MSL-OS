"""
分析器模块
用于数据分析和趋势跟踪
"""
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from collections import Counter
from .file_manager import file_manager
from .data_models import Visit, Doctor, Reflection, RelationshipStage


class Analyzer:
    """数据分析器"""
    
    def __init__(self):
        self.fm = file_manager
    
    def get_recent_visits(self, days: int = 30) -> List[Dict[str, Any]]:
        """获取最近N天的拜访记录"""
        cutoff_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        
        visits = []
        for filename in self.fm.list_files(self.fm.visits_dir):
            data = self.fm.read_json(self.fm.visits_dir / f"{filename}.json")
            if data and data.get("visit_date", "") >= cutoff_date:
                visits.append(data)
        
        return sorted(visits, key=lambda x: x.get("visit_date", ""), reverse=True)
    
    def get_pending_tasks(self) -> List[str]:
        """从拜访记录中提取待办任务"""
        tasks = []
        recent_visits = self.get_recent_visits(14)  # 最近两周
        
        for visit in recent_visits:
            follow_up = visit.get("follow_up_tasks", "")
            if follow_up:
                # 按行分割任务
                for task in follow_up.split("\n"):
                    task = task.strip()
                    if task and task not in tasks:
                        tasks.append(task)
        
        return tasks[:20]  # 限制数量
    
    def analyze_visit_effectiveness(self, doctor_id: Optional[str] = None) -> Dict[str, Any]:
        """分析拜访有效性"""
        visits = self.get_recent_visits(90)
        
        if doctor_id:
            visits = [v for v in visits if v.get("doctor_id") == doctor_id]
        
        if not visits:
            return {"average_effectiveness": 0, "total_visits": 0}
        
        effectiveness_scores = [v.get("response_effectiveness", 3) for v in visits]
        
        return {
            "average_effectiveness": sum(effectiveness_scores) / len(effectiveness_scores),
            "total_visits": len(visits),
            "high_effectiveness_count": sum(1 for s in effectiveness_scores if s >= 4),
            "low_effectiveness_count": sum(1 for s in effectiveness_scores if s <= 2),
        }
    
    def get_doctor_visit_frequency(self) -> Dict[str, int]:
        """统计医生拜访频率"""
        visits = self.get_recent_visits(90)
        doctor_counts = Counter(v.get("doctor_id", "") for v in visits)
        return dict(doctor_counts.most_common())
    
    def identify_neglected_doctors(self, days_threshold: int = 14) -> List[str]:
        """识别长时间未拜访的医生"""
        cutoff_date = (datetime.now() - timedelta(days=days_threshold)).strftime("%Y-%m-%d")
        
        # 获取所有医生
        all_doctors = set(self.fm.list_files(self.fm.doctors_dir))
        
        # 获取最近拜访过的医生
        recent_visits = self.get_recent_visits(days_threshold)
        recently_visited = set(v.get("doctor_id", "") for v in recent_visits)
        
        # 返回未拜访的医生
        return list(all_doctors - recently_visited)
    
    def analyze_common_objections(self) -> Dict[str, int]:
        """分析常见异议"""
        visits = self.get_recent_visits(90)
        
        objections = []
        for visit in visits:
            obj = visit.get("objections", "")
            if obj:
                # 简单分词
                objections.extend(obj.split("；"))
                objections.extend(obj.split(";"))
        
        # 清理和统计
        cleaned = [o.strip() for o in objections if o.strip()]
        return dict(Counter(cleaned).most_common(10))
    
    def get_relationship_distribution(self) -> Dict[str, int]:
        """统计医生关系阶段分布"""
        distribution = Counter()
        
        for filename in self.fm.list_files(self.fm.doctors_dir):
            data = self.fm.read_json(self.fm.doctors_dir / f"{filename}.json")
            if data:
                stage = data.get("relationship_stage", RelationshipStage.FIRST_CONTACT)
                distribution[stage] += 1
        
        return dict(distribution)
    
    def get_growth_trend(self, days: int = 30) -> Dict[str, Any]:
        """分析个人成长趋势"""
        cutoff_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        
        reflections = []
        for filename in self.fm.list_files(self.fm.reflections_dir):
            data = self.fm.read_json(self.fm.reflections_dir / f"{filename}.json")
            if data and data.get("date", "") >= cutoff_date:
                reflections.append(data)
        
        return {
            "total_reflections": len(reflections),
            "has_achievements": sum(1 for r in reflections if r.get("achievement")),
            "has_learnings": sum(1 for r in reflections if r.get("learning")),
            "has_breakthroughs": sum(1 for r in reflections if r.get("breakthrough")),
        }
    
    def generate_weekly_summary(self) -> Dict[str, Any]:
        """生成周报数据"""
        visits = self.get_recent_visits(7)
        
        # 按医生分组
        doctor_visits = {}
        for visit in visits:
            doc_id = visit.get("doctor_id", "unknown")
            if doc_id not in doctor_visits:
                doctor_visits[doc_id] = []
            doctor_visits[doc_id].append(visit)
        
        return {
            "week_start": (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"),
            "week_end": datetime.now().strftime("%Y-%m-%d"),
            "total_visits": len(visits),
            "unique_doctors": len(doctor_visits),
            "effectiveness": self.analyze_visit_effectiveness(),
            "pending_tasks": self.get_pending_tasks()[:5],
        }


# 创建全局实例
analyzer = Analyzer()
