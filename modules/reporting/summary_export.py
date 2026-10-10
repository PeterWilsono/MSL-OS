"""
智能总结导出服务
支持时间段总结、关联分析和进步追踪
"""
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pathlib import Path
from collections import defaultdict

from core.file_manager import file_manager
from core.ai_integration import ai_integration
from core.analyzer import analyzer


class SummaryExportService:
    """智能总结导出服务"""
    
    def __init__(self):
        self.fm = file_manager
        self.ai = ai_integration
        
        # 导出目录
        self.exports_dir = self.fm.output_dir / "exports"
        self.exports_dir.mkdir(parents=True, exist_ok=True)
    
    async def export_period_summary(
        self,
        start_date: str,
        end_date: str,
        include_ai_analysis: bool = True
    ) -> str:
        """
        导出时间段总结
        
        Args:
            start_date: 开始日期 YYYY-MM-DD
            end_date: 结束日期 YYYY-MM-DD
            include_ai_analysis: 是否包含 AI 分析
            
        Returns:
            生成的 Markdown 内容
        """
        # 收集数据
        visits = self._get_visits_in_range(start_date, end_date)
        interactions = self._get_interactions_in_range(start_date, end_date)
        reflections = self._get_reflections_in_range(start_date, end_date)
        
        # 统计数据
        stats = self._calculate_stats(visits, interactions)
        
        # 提取关键发现
        key_findings = self._extract_key_findings(visits, interactions)
        
        # 构建报告
        content = f"""# 📊 工作总结报告

## 报告周期
**{start_date}** 至 **{end_date}**

---

## 📈 数据概览

| 指标 | 数值 |
|------|------|
| 交流总次数 | {stats['total_interactions']} |
| 医生拜访 | {stats['doctor_visits']} |
| 其他交流 | {stats['other_interactions']} |
| 平均有效性 | {stats['avg_effectiveness']:.1f}/5 |
| 高效交流(4-5分) | {stats['high_effectiveness']} |
| 待跟进任务 | {stats['pending_tasks']} |

---

## 👥 联系人互动

### 按类型分布
"""
        
        for contact_type, count in stats['by_type'].items():
            content += f"- **{contact_type}**: {count} 次\n"
        
        content += """
### 活跃联系人
"""
        
        for contact, count in stats['top_contacts'][:5]:
            content += f"- {contact}: {count} 次交流\n"
        
        content += """
---

## 💡 关键发现与洞察

"""
        
        for finding in key_findings[:10]:
            content += f"- {finding}\n"
        
        if not key_findings:
            content += "- 暂无特别发现\n"
        
        content += """
---

## 📝 待跟进事项

"""
        
        tasks = self._get_pending_tasks(visits, interactions)
        for task in tasks[:15]:
            content += f"- [ ] {task}\n"
        
        if not tasks:
            content += "- 暂无待跟进事项\n"
        
        # 关联分析
        correlations = self._find_correlations(visits, interactions)
        if correlations:
            content += """
---

## 🔗 信息关联（"破案"分析）

"""
            for corr in correlations:
                content += f"### {corr['title']}\n"
                content += f"{corr['description']}\n\n"
        
        # AI 分析
        if include_ai_analysis and self.ai.is_enabled:
            ai_analysis = await self._generate_ai_analysis(visits, interactions, reflections)
            if ai_analysis:
                content += f"""
---

## 🤖 AI 智能分析

{ai_analysis}
"""
        
        # 个人成长
        if reflections:
            growth_summary = self._summarize_growth(reflections)
            content += f"""
---

## 🌱 个人成长

{growth_summary}
"""
        
        content += f"""
---

*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}*
"""
        
        # 保存报告
        filename = f"summary_{start_date}_to_{end_date}.md"
        self.fm.write_markdown(self.exports_dir / filename, content)
        
        return content
    
    async def export_weekly_summary(self, include_ai: bool = True) -> str:
        """导出本周总结"""
        today = datetime.now()
        monday = today - timedelta(days=today.weekday())
        start_date = monday.strftime("%Y-%m-%d")
        end_date = today.strftime("%Y-%m-%d")
        return await self.export_period_summary(start_date, end_date, include_ai)
    
    async def export_recent_days(self, days: int = 7, include_ai: bool = True) -> str:
        """导出最近N天总结"""
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=days-1)).strftime("%Y-%m-%d")
        return await self.export_period_summary(start_date, end_date, include_ai)
    
    def _get_visits_in_range(self, start: str, end: str) -> List[Dict]:
        """获取时间范围内的拜访"""
        visits = []
        for filename in self.fm.list_files(self.fm.visits_dir):
            data = self.fm.read_json(self.fm.visits_dir / f"{filename}.json")
            if data:
                date = data.get("visit_date", "")
                if start <= date <= end:
                    visits.append(data)
        return visits
    
    def _get_interactions_in_range(self, start: str, end: str) -> List[Dict]:
        """获取时间范围内的交流"""
        interactions = []
        interactions_dir = self.fm.data_dir / "interactions"
        if not interactions_dir.exists():
            return []
        
        for filename in self.fm.list_files(interactions_dir):
            data = self.fm.read_json(interactions_dir / f"{filename}.json")
            if data:
                date = data.get("date", "")
                if start <= date <= end:
                    interactions.append(data)
        return interactions
    
    def _get_reflections_in_range(self, start: str, end: str) -> List[Dict]:
        """获取时间范围内的反思"""
        reflections = []
        for filename in self.fm.list_files(self.fm.reflections_dir):
            data = self.fm.read_json(self.fm.reflections_dir / f"{filename}.json")
            if data:
                date = data.get("date", "")
                if start <= date <= end:
                    reflections.append(data)
        return reflections
    
    def _calculate_stats(self, visits: List, interactions: List) -> Dict:
        """计算统计数据"""
        all_records = visits + interactions
        
        # 按类型统计
        by_type = defaultdict(int)
        top_contacts = defaultdict(int)
        effectiveness_scores = []
        
        for v in visits:
            by_type["医生"] += 1
            contact_name = v.get("doctor_id", "unknown")
            top_contacts[contact_name] += 1
            effectiveness_scores.append(v.get("response_effectiveness", 3))
        
        for i in interactions:
            contact_type = i.get("contact_type", "其他")
            by_type[contact_type] += 1
            contact_name = i.get("contact_name", "unknown")
            top_contacts[contact_name] += 1
            effectiveness_scores.append(i.get("response_effectiveness", 3))
        
        # 计算待跟进任务
        pending = 0
        for r in all_records:
            if r.get("follow_up_tasks"):
                pending += len(r["follow_up_tasks"].split("\n"))
        
        avg_eff = sum(effectiveness_scores) / len(effectiveness_scores) if effectiveness_scores else 0
        high_eff = sum(1 for s in effectiveness_scores if s >= 4)
        
        return {
            "total_interactions": len(all_records),
            "doctor_visits": len(visits),
            "other_interactions": len(interactions),
            "avg_effectiveness": avg_eff,
            "high_effectiveness": high_eff,
            "pending_tasks": pending,
            "by_type": dict(by_type),
            "top_contacts": sorted(top_contacts.items(), key=lambda x: x[1], reverse=True)
        }
    
    def _extract_key_findings(self, visits: List, interactions: List) -> List[str]:
        """提取关键发现"""
        findings = []
        
        for v in visits:
            if v.get("new_insights"):
                findings.append(f"[{v.get('visit_date')}] {v['new_insights'][:100]}")
        
        for i in interactions:
            if i.get("insights"):
                findings.append(f"[{i.get('date')}] {i['insights'][:100]}")
        
        return findings
    
    def _get_pending_tasks(self, visits: List, interactions: List) -> List[str]:
        """获取待跟进任务"""
        tasks = []
        
        for v in visits:
            if v.get("follow_up_tasks"):
                for task in v["follow_up_tasks"].split("\n"):
                    task = task.strip()
                    if task:
                        tasks.append(f"[{v.get('visit_date')}] {task}")
        
        for i in interactions:
            if i.get("follow_up_tasks"):
                for task in i["follow_up_tasks"].split("\n"):
                    task = task.strip()
                    if task:
                        tasks.append(f"[{i.get('date')}] {task}")
        
        return tasks
    
    def _find_correlations(self, visits: List, interactions: List) -> List[Dict]:
        """发现信息关联"""
        correlations = []
        
        # 查找共同标签
        tag_records = defaultdict(list)
        for v in visits:
            for tag in v.get("tags", []):
                tag_records[tag].append({
                    "type": "拜访",
                    "date": v.get("visit_date"),
                    "contact": v.get("doctor_id")
                })
        
        for i in interactions:
            for tag in i.get("tags", []):
                tag_records[tag].append({
                    "type": "交流",
                    "date": i.get("date"),
                    "contact": i.get("contact_name")
                })
        
        # 找出有多条记录的标签
        for tag, records in tag_records.items():
            if len(records) > 1:
                contacts = set(r["contact"] for r in records)
                correlations.append({
                    "title": f"标签关联：{tag}",
                    "description": f"有 {len(records)} 条记录涉及此标签，关联联系人：{', '.join(contacts)}"
                })
        
        # 查找相关联系人交叉
        related_map = defaultdict(set)
        for v in visits:
            for related in v.get("related_contacts", []):
                related_map[v.get("doctor_id")].add(related)
        
        for i in interactions:
            for related in i.get("related_contacts", []):
                related_map[i.get("contact_id")].add(related)
        
        # 双向关联
        for contact, related in related_map.items():
            for r in related:
                if contact in related_map.get(r, set()):
                    correlations.append({
                        "title": f"双向关联：{contact} ↔ {r}",
                        "description": "这两位联系人在多次交流中互相提及，可能存在紧密关系"
                    })
        
        return correlations[:10]  # 最多10条
    
    async def _generate_ai_analysis(self, visits: List, interactions: List, reflections: List) -> Optional[str]:
        """生成 AI 分析"""
        if not self.ai.is_enabled:
            return None
        
        # 构建数据摘要
        data_summary = f"""
数据概览：
- 医生拜访 {len(visits)} 次
- 其他交流 {len(interactions)} 次
- 反思记录 {len(reflections)} 条

关键洞察摘要：
"""
        insights = []
        for v in visits[:5]:
            if v.get("new_insights"):
                insights.append(v["new_insights"][:50])
        for i in interactions[:5]:
            if i.get("insights"):
                insights.append(i["insights"][:50])
        
        data_summary += "\n".join(f"- {ins}" for ins in insights[:8])
        
        prompt = f"""请基于以下工作数据，提供深度分析和建议：

{data_summary}

请分析：
1. 整体工作模式和效率
2. 需要特别关注的问题或风险
3. 潜在的改进机会
4. 下周工作重点建议

请用简洁、可操作的语言回答。"""
        
        return await self.ai._make_request([
            {"role": "system", "content": "你是一位资深的医药代表教练，擅长数据分析和策略建议。"},
            {"role": "user", "content": prompt}
        ], temperature=0.5, max_tokens=800)
    
    def _summarize_growth(self, reflections: List) -> str:
        """总结个人成长"""
        achievements = []
        learnings = []
        
        for r in reflections:
            if r.get("achievement"):
                achievements.append(r["achievement"])
            if r.get("learning"):
                learnings.append(r["learning"])
        
        summary = ""
        if achievements:
            summary += f"**成就**: {len(achievements)} 项\n"
            for a in achievements[:3]:
                summary += f"- {a[:50]}...\n"
        
        if learnings:
            summary += f"\n**学习收获**: {len(learnings)} 项\n"
            for l in learnings[:3]:
                summary += f"- {l[:50]}...\n"
        
        return summary if summary else "本周期暂无成长记录"
    
    def list_exports(self) -> List[Dict]:
        """列出所有导出的报告"""
        exports = []
        for filename in self.fm.list_files(self.exports_dir, ".md"):
            exports.append({
                "filename": filename,
                "path": str(self.exports_dir / f"{filename}.md")
            })
        return sorted(exports, key=lambda x: x["filename"], reverse=True)


# 创建全局实例
summary_export_service = SummaryExportService()
