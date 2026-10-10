"""
拜访总结服务
"""
import asyncio
from datetime import datetime
from typing import Optional, List, Dict, Any
from core.file_manager import file_manager
from core.data_models import Visit, Doctor
from core.ai_integration import ai_integration


class VisitSummaryService:
    """拜访总结服务"""

    def __init__(self):
        self.fm = file_manager
        self.ai = ai_integration

    def create_visit_summary(
        self,
        doctor_id: str,
        visit_date: str,
        key_topics: str = "",
        doctor_concerns: str = "",
        objections: str = "",
        responses: str = "",
        response_effectiveness: int = 3,
        emotional_tone: str = "",
        new_insights: str = "",
        follow_up_tasks: str = ""
    ) -> Visit:
        """创建拜访总结"""

        visit_id = f"visit_{visit_date}_{doctor_id}"

        visit = Visit(
            visit_id=visit_id,
            doctor_id=doctor_id,
            visit_date=visit_date,
            key_topics=key_topics,
            doctor_concerns=doctor_concerns,
            objections=objections,
            responses=responses,
            response_effectiveness=response_effectiveness,
            emotional_tone=emotional_tone,
            new_insights=new_insights,
            follow_up_tasks=follow_up_tasks
        )

        if self.ai.is_enabled:
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                ai_summary = loop.run_until_complete(
                    self.ai.summarize_visit(visit.model_dump())
                )
                loop.close()
                if ai_summary:
                    visit.ai_summary = ai_summary
            except Exception:
                pass

        self.fm.save_model(self.fm.visits_dir, visit, visit_id)

        self._generate_visit_report(visit)

        self._update_doctor_profile(visit)

        return visit
    
    def get_visit(self, visit_id: str) -> Optional[Visit]:
        """获取拜访记录"""
        return self.fm.load_model(
            self.fm.visits_dir,
            visit_id,
            Visit
        )

    def get_visit_by_date_and_doctor(self, visit_date: str, doctor_id: str) -> Optional[Visit]:
        """根据日期和医生ID获取拜访记录"""
        visit_id = f"visit_{visit_date}_{doctor_id}"
        return self.get_visit(visit_id)

    def update_visit(
        self,
        visit_id: str,
        key_topics: str = "",
        doctor_concerns: str = "",
        objections: str = "",
        responses: str = "",
        response_effectiveness: int = 3,
        emotional_tone: str = "",
        new_insights: str = "",
        follow_up_tasks: str = ""
    ) -> Optional[Visit]:
        """更新拜访记录"""
        visit = self.get_visit(visit_id)
        if not visit:
            return None

        visit.key_topics = key_topics
        visit.doctor_concerns = doctor_concerns
        visit.objections = objections
        visit.responses = responses
        visit.response_effectiveness = response_effectiveness
        visit.emotional_tone = emotional_tone
        visit.new_insights = new_insights
        visit.follow_up_tasks = follow_up_tasks

        self.fm.save_model(self.fm.visits_dir, visit, visit_id)

        self._generate_visit_report(visit)

        return visit

    def delete_visit(self, visit_id: str) -> bool:
        """删除拜访记录"""
        visit_path = self.fm.visits_dir / f"{visit_id}.json"
        if visit_path.exists():
            visit_path.unlink()
            return True
        return False

    def list_visits(self, doctor_id: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """列出拜访记录"""
        visits = []
        for filename in self.fm.list_files(self.fm.visits_dir):
            data = self.fm.read_json(self.fm.visits_dir / f"{filename}.json")
            if data:
                if doctor_id is None or data.get("doctor_id") == doctor_id:
                    visits.append(data)
        
        # 按日期排序
        visits.sort(key=lambda x: x.get("visit_date", ""), reverse=True)
        return visits[:limit]
    
    def _generate_visit_report(self, visit: Visit) -> None:
        """生成拜访总结报告 Markdown"""
        
        # 获取医生信息
        doctor_data = self.fm.read_json(self.fm.doctors_dir / f"{visit.doctor_id}.json")
        doctor_name = doctor_data.get("name", visit.doctor_id) if doctor_data else visit.doctor_id
        
        effectiveness_stars = "⭐" * visit.response_effectiveness
        
        content = f"""# 拜访总结报告

## 基本信息
- **医生**: {doctor_name}
- **拜访日期**: {visit.visit_date}
- **回应有效性**: {effectiveness_stars} ({visit.response_effectiveness}/5)

## 讨论话题
{visit.key_topics or "无记录"}

## 医生顾虑
{visit.doctor_concerns or "无"}

## 异议与回应
### 医生异议
{visit.objections or "无"}

### 我的回应
{visit.responses or "无"}

## 情绪氛围
{visit.emotional_tone or "未记录"}

## 新发现/洞察
{visit.new_insights or "无"}

## 后续跟进任务
{visit.follow_up_tasks or "无"}
"""
        
        if visit.ai_summary:
            content += f"""
## AI 智能摘要
{visit.ai_summary}
"""
        
        content += f"""
---
*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}*
"""
        
        # 保存
        filename = f"visit_summary_{visit.doctor_id}_{visit.visit_date}.md"
        self.fm.write_markdown(self.fm.reports_dir / filename, content)
    
    def _update_doctor_profile(self, visit: Visit) -> None:
        """根据拜访更新医生档案"""
        doctor_path = self.fm.doctors_dir / f"{visit.doctor_id}.json"
        doctor_data = self.fm.read_json(doctor_path)
        
        if doctor_data:
            # 更新最后拜访时间
            doctor_data["updated_at"] = datetime.now().isoformat()
            
            # 如果有新发现，追加到备注
            if visit.new_insights:
                notes = doctor_data.get("notes", "")
                new_note = f"\n[{visit.visit_date}] {visit.new_insights}"
                doctor_data["notes"] = notes + new_note
            
            self.fm.write_json(doctor_path, doctor_data)
    
    def get_ai_analysis(self, visit_id: str) -> Optional[str]:
        """获取AI分析"""
        if not self.ai.is_enabled:
            return None

        visit = self.get_visit(visit_id)
        if not visit:
            return None

        return self.ai.summarize_visit(visit.model_dump())

    def get_visits_by_date_range(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """获取指定日期范围内的所有拜访记录"""
        visits = []
        for filename in self.fm.list_files(self.fm.visits_dir):
            data = self.fm.read_json(self.fm.visits_dir / f"{filename}.json")
            if data:
                visit_date = data.get("visit_date", "")
                if start_date <= visit_date <= end_date:
                    visits.append(data)
        visits.sort(key=lambda x: x.get("visit_date", ""), reverse=True)
        return visits

    async def get_ai_analysis_for_date_range(
        self, start_date: str, end_date: str
    ) -> Optional[str]:
        """获取指定日期范围内所有拜访记录的AI综合分析"""
        if not self.ai.is_enabled:
            return None

        visits = self.get_visits_by_date_range(start_date, end_date)
        if not visits:
            return None

        visits_text = ""
        for i, v in enumerate(visits, 1):
            doctor_name = "未知医生"
            if v.get("doctor_id"):
                doctor_data = self.fm.read_json(self.fm.doctors_dir / f"{v['doctor_id']}.json")
                if doctor_data:
                    doctor_name = doctor_data.get("name", "未知医生")

            visits_text += f"""
---
### 第{i}条拜访记录
- **日期**: {v.get('visit_date', '未知')}
- **医生**: {doctor_name}
- **讨论话题**: {v.get('key_topics', '无')}
- **医生顾虑**: {v.get('doctor_concerns', '无')}
- **医生异议**: {v.get('objections', '无')}
- **我的回应**: {v.get('responses', '无')}
- **新发现**: {v.get('new_insights', '无')}
- **后续跟进**: {v.get('follow_up_tasks', '无')}
- **效果评分**: {v.get('response_effectiveness', 3)}/5
"""

        prompt = f"""请对以下日期范围（{start_date} 至 {end_date}）内的{len(visits)}条拜访记录进行综合分析：

{visits_text}

请提供：
1. **整体概述**：这一时期拜访的总体情况和效果
2. **关键洞察**：主要发现了什么问题和机会
3. **改进建议**：针对发现的问题提出具体改进建议
4. **重点关注**：建议后续重点跟进的医生或事项
5. **总结**：一句话总结这一时期的工作
"""

        messages = [
            {"role": "system", "content": "你是一位专业的医药代表教练，帮助分析拜访记录并提供改进建议。"},
            {"role": "user", "content": prompt}
        ]

        return await self.ai._make_request(messages, temperature=0.7, max_tokens=3000)


# 创建全局实例
visit_summary_service = VisitSummaryService()
