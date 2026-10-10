"""
报告生成服务
"""
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pathlib import Path
from core.file_manager import file_manager
from core.analyzer import analyzer
from core.privacy_manager import privacy_manager


class ReportingService:
    """报告生成服务"""
    
    def __init__(self):
        self.fm = file_manager
        self.analyzer = analyzer
    
    def generate_weekly_report(self) -> str:
        """生成周报"""
        summary = self.analyzer.generate_weekly_summary()
        effectiveness = summary['effectiveness']
        
        content = f"""# 周工作报告

## 报告周期
{summary['week_start']} 至 {summary['week_end']}

## 工作概览
- **总拜访次数**: {summary['total_visits']}
- **拜访医生数**: {summary['unique_doctors']}
- **平均回应有效性**: {effectiveness.get('average_effectiveness', 0):.1f}/5

## 效果分析
- 高效拜访（4-5分）: {effectiveness.get('high_effectiveness_count', 0)}次
- 低效拜访（1-2分）: {effectiveness.get('low_effectiveness_count', 0)}次

## 待跟进事项
"""
        
        for task in summary['pending_tasks']:
            content += f"- {task}\n"
        
        if not summary['pending_tasks']:
            content += "- 暂无待跟进事项\n"
        
        content += f"""
---
*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}*
"""
        
        # 保存报告
        filename = f"weekly_report_{summary['week_end']}.md"
        self.fm.write_markdown(self.fm.reports_dir / filename, content)
        
        return content
    
    def generate_monthly_report(self) -> str:
        """生成月报"""
        # 获取最近30天数据
        visits = self.analyzer.get_recent_visits(30)
        relationship_dist = self.analyzer.get_relationship_distribution()
        objections = self.analyzer.analyze_common_objections()
        growth = self.analyzer.get_growth_trend(30)
        
        month_name = datetime.now().strftime("%Y年%m月")
        
        content = f"""# {month_name} 月度报告

## 拜访统计
- **总拜访次数**: {len(visits)}
- **平均每周拜访**: {len(visits) / 4:.1f}次

## 医生关系分布
"""
        
        for stage, count in relationship_dist.items():
            content += f"- {stage}: {count}人\n"
        
        content += """
## 常见异议 TOP5
"""
        
        for i, (objection, count) in enumerate(list(objections.items())[:5], 1):
            content += f"{i}. {objection[:50]}... ({count}次)\n"
        
        if not objections:
            content += "- 暂无记录\n"
        
        content += f"""
## 个人成长
- 反思记录: {growth['total_reflections']}篇
- 记录成就: {growth['has_achievements']}天
- 记录学习: {growth['has_learnings']}天
- 记录突破: {growth['has_breakthroughs']}天

---
*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}*
"""
        
        # 保存报告
        filename = f"monthly_report_{datetime.now().strftime('%Y%m')}.md"
        self.fm.write_markdown(self.fm.reports_dir / filename, content)
        
        return content
    
    def generate_daily_action_report(self) -> str:
        """生成每日行动单报告"""
        from core.decision_engine import decision_engine
        
        action = decision_engine.get_today_action()
        if not action:
            action = decision_engine.generate_daily_action()
        
        today = datetime.now().strftime("%Y年%m月%d日")
        
        content = f"""# 今日行动单

**日期**: {today}

## 🎯 今日重点任务
"""
        
        for i, task in enumerate(action.top_tasks, 1):
            content += f"{i}. {task}\n"
        
        if not action.top_tasks:
            content += "- 暂无特别任务\n"
        
        content += f"""
## 👨‍⚕️ 优先拜访
{action.priority_doctor}

## 📚 推荐学习主题
{action.recommended_learning_topic}

## 💪 今日改进重点
{action.key_improvement_focus}
"""
        
        if action.ai_suggestions:
            content += f"""
## 🤖 AI 智能建议
{action.ai_suggestions}
"""
        
        content += f"""
---
*生成时间: {datetime.now().strftime('%H:%M')}*
"""
        
        # 保存
        filename = f"daily_action_{datetime.now().strftime('%Y-%m-%d')}.md"
        self.fm.write_markdown(self.fm.daily_tasks_dir / filename, content)
        
        return content
    
    def list_reports(self) -> List[Dict[str, Any]]:
        """列出所有报告"""
        reports = []
        
        for filename in self.fm.list_files(self.fm.reports_dir, ".md"):
            file_path = self.fm.reports_dir / f"{filename}.md"
            reports.append({
                "filename": filename,
                "path": str(file_path),
                "type": self._get_report_type(filename)
            })
        
        return sorted(reports, key=lambda x: x["filename"], reverse=True)
    
    def _get_report_type(self, filename: str) -> str:
        """识别报告类型"""
        if filename.startswith("weekly"):
            return "weekly"
        elif filename.startswith("monthly"):
            return "monthly"
        elif filename.startswith("daily"):
            return "daily"
        elif filename.startswith("visit_summary"):
            return "visit"
        elif filename.startswith("prep_brief"):
            return "preparation"
        elif filename.startswith("doctor_profile"):
            return "doctor"
        else:
            return "other"
    
    def get_report_content(self, report_path: str) -> Optional[str]:
        """获取报告内容"""
        return self.fm.read_markdown(Path(report_path))
    
    def update_report(self, report_path: str, content: str) -> bool:
        """更新报告内容"""
        try:
            self.fm.write_markdown(Path(report_path), content)
            return True
        except Exception as e:
            print(f"更新报告失败: {e}")
            return False
    
    def delete_report(self, report_path: str) -> bool:
        """删除报告"""
        try:
            Path(report_path).unlink()
            return True
        except Exception as e:
            print(f"删除报告失败: {e}")
            return False
    
    def export_report_to_html(self, report_path: str, output_path: Optional[str] = None) -> str:
        """导出报告为 HTML（适合手机查看）"""
        import markdown
        
        content = self.get_report_content(report_path)
        if not content:
            return ""
        
        # 转换 Markdown 到 HTML
        html_content = markdown.markdown(content, extensions=['tables', 'fenced_code'])
        
        # 添加移动端友好的样式
        full_html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>报告</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
            padding: 10px;
        }}
        .container {{
            max-width: 800px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #667eea;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
            margin-bottom: 20px;
            font-size: 1.8em;
        }}
        h2 {{
            color: #764ba2;
            margin-top: 25px;
            margin-bottom: 15px;
            font-size: 1.4em;
        }}
        h3 {{
            color: #555;
            margin-top: 20px;
            margin-bottom: 10px;
            font-size: 1.2em;
        }}
        ul, ol {{
            margin-left: 20px;
            margin-bottom: 15px;
        }}
        li {{
            margin-bottom: 8px;
        }}
        p {{
            margin-bottom: 15px;
        }}
        strong {{
            color: #667eea;
        }}
        hr {{
            border: none;
            border-top: 1px solid #ddd;
            margin: 20px 0;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 10px;
            text-align: left;
        }}
        th {{
            background: #667eea;
            color: white;
        }}
        @media (max-width: 600px) {{
            body {{
                padding: 5px;
            }}
            .container {{
                padding: 15px;
            }}
            h1 {{
                font-size: 1.5em;
            }}
            h2 {{
                font-size: 1.2em;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        {html_content}
    </div>
</body>
</html>"""
        
        # 保存 HTML 文件
        if output_path is None:
            report_name = Path(report_path).stem
            output_path = str(self.fm.reports_dir / f"{report_name}.html")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(full_html)
        
        return output_path
    
    def export_reports(self, report_type: Optional[str] = None) -> List[str]:
        """导出报告（返回文件路径列表）"""
        reports = self.list_reports()
        
        if report_type:
            reports = [r for r in reports if r["type"] == report_type]
        
        # 过滤私有内容
        exported = []
        for report in reports:
            content = self.get_report_content(report["path"])
            if content:
                # 这里可以添加隐私过滤逻辑
                exported.append(report["path"])
        
        return exported


# 创建全局实例
reporting_service = ReportingService()
