"""
拜访准备服务
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from core.file_manager import file_manager
from core.data_models import Preparation, Doctor
from core.ai_integration import ai_integration


class PreparationService:
    """拜访准备服务"""
    
    def __init__(self):
        self.fm = file_manager
        self.ai = ai_integration
    
    def create_preparation(
        self,
        doctor_id: str,
        visit_date: str,
        visit_goal: str = "",
        exploration_question: str = "",
        concerns: str = "",
        prepared_data: str = "",
        key_messages: List[str] = None
    ) -> Preparation:
        """创建拜访准备"""
        
        # 获取上次拜访摘要
        last_visit_summary = self._get_last_visit_summary(doctor_id)
        
        prep_id = f"prep_{visit_date}_{doctor_id}"
        
        prep = Preparation(
            prep_id=prep_id,
            doctor_id=doctor_id,
            visit_date=visit_date,
            last_visit_summary=last_visit_summary,
            visit_goal=visit_goal,
            exploration_question=exploration_question,
            concerns=concerns,
            prepared_data=prepared_data,
            key_messages=key_messages or []
        )
        
        # 保存
        self.fm.save_model(self.fm.preparations_dir, prep, prep_id)
        
        # 生成准备简报
        self._generate_prep_brief(prep)
        
        return prep
    
    def get_preparation(self, prep_id: str) -> Optional[Preparation]:
        """获取拜访准备"""
        return self.fm.load_model(
            self.fm.preparations_dir,
            prep_id,
            Preparation
        )
    
    def list_preparations(self, doctor_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """列出拜访准备"""
        preps = []
        for filename in self.fm.list_files(self.fm.preparations_dir):
            data = self.fm.read_json(self.fm.preparations_dir / f"{filename}.json")
            if data:
                if doctor_id is None or data.get("doctor_id") == doctor_id:
                    preps.append(data)
        
        return sorted(preps, key=lambda x: x.get("visit_date", ""), reverse=True)
    
    def _get_last_visit_summary(self, doctor_id: str) -> str:
        """获取上次拜访摘要"""
        visits = []
        for filename in self.fm.list_files(self.fm.visits_dir):
            if doctor_id in filename:
                data = self.fm.read_json(self.fm.visits_dir / f"{filename}.json")
                if data:
                    visits.append(data)
        
        if not visits:
            return "无历史拜访记录"
        
        # 按日期排序，取最近一次
        visits.sort(key=lambda x: x.get("visit_date", ""), reverse=True)
        last_visit = visits[0]
        
        summary = f"""日期：{last_visit.get('visit_date', '')}
话题：{last_visit.get('key_topics', '')}
待跟进：{last_visit.get('follow_up_tasks', '')}"""
        
        return summary
    
    async def get_ai_suggestions(self, doctor_id: str) -> Optional[str]:
        """获取AI准备建议"""
        if not self.ai.is_enabled:
            return None
        
        # 加载医生数据
        doctor_data = self.fm.read_json(self.fm.doctors_dir / f"{doctor_id}.json")
        if not doctor_data:
            return None
        
        # 获取上次拜访
        last_visit = None
        visits = self.list_preparations(doctor_id)
        if visits:
            last_visit = visits[0]
        
        return await self.ai.suggest_preparation(doctor_data, last_visit)
    
    def _generate_prep_brief(self, prep: Preparation) -> None:
        """生成准备简报 Markdown"""
        
        # 获取医生信息
        doctor_data = self.fm.read_json(self.fm.doctors_dir / f"{prep.doctor_id}.json")
        doctor_name = doctor_data.get("name", prep.doctor_id) if doctor_data else prep.doctor_id
        
        content = f"""# 拜访准备简报

## 基本信息
- **医生**: {doctor_name}
- **计划日期**: {prep.visit_date}
- **创建时间**: {prep.created_at}

## 上次拜访摘要
{prep.last_visit_summary}

## 本次拜访目标
{prep.visit_goal or "待填写"}

## 探索性问题
{prep.exploration_question or "待填写"}

## 顾虑/担心
{prep.concerns or "无"}

## 准备资料
{prep.prepared_data or "无"}

## 关键信息点
"""
        
        for msg in prep.key_messages:
            content += f"- {msg}\n"
        
        if not prep.key_messages:
            content += "- 暂无\n"
        
        # 保存
        filename = f"prep_brief_{prep.doctor_id}_{prep.visit_date}.md"
        self.fm.write_markdown(self.fm.reports_dir / filename, content)


# 创建全局实例
preparation_service = PreparationService()
