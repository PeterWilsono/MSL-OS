"""
AI 数据分析器
提供医院、科室、医生的智能分析功能，支持缓存和增量更新
"""
from datetime import datetime
from typing import Optional, Dict, Any, List
from pathlib import Path

from .file_manager import file_manager
from .ai_integration import ai_integration
from .ai_analysis_cache import AIAnalysisCacheService, AnalysisCache


class AIDataAnalyzer:
    """AI数据分析器"""
    
    def __init__(self):
        self.fm = file_manager
        self.ai = ai_integration
        self.cache_service = AIAnalysisCacheService(self.fm.data_dir)
    
    # ==================== 数据获取辅助方法 ====================
    
    def _get_hospital_data_summary(self, hospital_id: str) -> Optional[Dict[str, Any]]:
        """获取医院数据摘要（优化token使用）"""
        hospital_path = self.fm.data_dir / "hospitals" / f"{hospital_id}.json"
        hospital_data = self.fm.read_json(hospital_path)
        
        if not hospital_data:
            return None
        
        # 获取关联的科室
        departments = []
        dept_dir = self.fm.data_dir / "departments"
        if dept_dir.exists():
            for dept_file in dept_dir.glob("*.json"):
                dept_data = self.fm.read_json(dept_file)
                if dept_data and dept_data.get("hospital_id") == hospital_id:
                    departments.append({
                        "id": dept_data.get("department_id"),
                        "name": dept_data.get("name"),
                        "head_doctor": dept_data.get("head_doctor", "")
                    })
        
        # 获取产品关联统计
        assoc_dir = self.fm.data_dir / "associations"
        hospital_index_path = assoc_dir / "hospital_index.json"
        product_associations = []
        
        if hospital_index_path.exists():
            hospital_index = self.fm.read_json(hospital_index_path)
            if hospital_index and hospital_id in hospital_index:
                assoc_ids = hospital_index[hospital_id]
                for assoc_id in assoc_ids[:10]:  # 限制数量
                    assoc_path = assoc_dir / f"{assoc_id}.json"
                    assoc_data = self.fm.read_json(assoc_path)
                    if assoc_data and assoc_data.get("is_active", True):
                        product_associations.append({
                            "product_name": assoc_data.get("product_name"),
                            "department_name": assoc_data.get("department_name")
                        })
        
        return {
            "hospital_id": hospital_id,
            "name": hospital_data.get("name"),
            "level": hospital_data.get("level", ""),
            "address": hospital_data.get("address", ""),
            "departments_count": len(departments),
            "departments": departments[:5],  # 只取前5个
            "product_associations_count": len(product_associations),
            "product_associations": product_associations[:10],  # 只取前10个
            "notes": hospital_data.get("notes", "")[:200]  # 限制长度
        }
    
    def _get_department_data_summary(self, department_id: str) -> Optional[Dict[str, Any]]:
        """获取科室数据摘要"""
        dept_path = self.fm.data_dir / "departments" / f"{department_id}.json"
        dept_data = self.fm.read_json(dept_path)
        
        if not dept_data:
            return None
        
        # 获取所属医院信息
        hospital_id = dept_data.get("hospital_id", "")
        hospital_name = ""
        if hospital_id:
            hospital_path = self.fm.data_dir / "hospitals" / f"{hospital_id}.json"
            hospital_data = self.fm.read_json(hospital_path)
            if hospital_data:
                hospital_name = hospital_data.get("name", "")
        
        # 获取产品关联
        assoc_dir = self.fm.data_dir / "associations"
        dept_index_path = assoc_dir / "department_index.json"
        product_associations = []
        
        if dept_index_path.exists():
            dept_index = self.fm.read_json(dept_index_path)
            if dept_index and department_id in dept_index:
                assoc_ids = dept_index[department_id]
                for assoc_id in assoc_ids[:10]:
                    assoc_path = assoc_dir / f"{assoc_id}.json"
                    assoc_data = self.fm.read_json(assoc_path)
                    if assoc_data and assoc_data.get("is_active", True):
                        product_associations.append({
                            "product_name": assoc_data.get("product_name")
                        })
        
        return {
            "department_id": department_id,
            "name": dept_data.get("name"),
            "hospital_name": hospital_name,
            "head_doctor": dept_data.get("head_doctor", ""),
            "description": dept_data.get("description", "")[:200],
            "product_associations_count": len(product_associations),
            "products": [p["product_name"] for p in product_associations],
            "notes": dept_data.get("notes", "")[:200]
        }
    
    def _get_doctor_data_summary(self, doctor_id: str) -> Optional[Dict[str, Any]]:
        """获取医生数据摘要"""
        doctor_path = self.fm.doctors_dir / f"{doctor_id}.json"
        doctor_data = self.fm.read_json(doctor_path)
        
        if not doctor_data:
            return None
        
        # 获取最近拜访记录（最多5条）
        recent_visits = []
        visits_dir = self.fm.visits_dir
        if visits_dir.exists():
            visit_files = sorted(visits_dir.glob("*.json"), reverse=True)
            for visit_file in visit_files[:20]:  # 检查最近20个文件
                visit_data = self.fm.read_json(visit_file)
                if visit_data and visit_data.get("doctor_id") == doctor_id:
                    recent_visits.append({
                        "date": visit_data.get("visit_date"),
                        "topics": visit_data.get("key_topics", "")[:100],
                        "effectiveness": visit_data.get("response_effectiveness", 3)
                    })
                    if len(recent_visits) >= 5:
                        break
        
        return {
            "doctor_id": doctor_id,
            "name": doctor_data.get("name"),
            "hospital": doctor_data.get("hospital", ""),
            "department": doctor_data.get("department", ""),
            "title": doctor_data.get("title", ""),
            "relationship_stage": doctor_data.get("relationship_stage", ""),
            "interests": doctor_data.get("interests", []),
            "decision_style": doctor_data.get("decision_style", ""),
            "recent_visits_count": len(recent_visits),
            "recent_visits": recent_visits,
            "notes": doctor_data.get("notes", "")[:200]
        }
    
    # ==================== 医院分析 ====================
    
    async def analyze_hospital(
        self, 
        hospital_id: str, 
        force_refresh: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        分析医院
        
        Args:
            hospital_id: 医院ID
            force_refresh: 是否强制刷新（忽略缓存）
            
        Returns:
            分析结果
        """
        if not self.ai.is_enabled:
            return {"error": "AI功能未启用"}
        
        # 检查缓存
        if not force_refresh:
            cached = self.cache_service.get_cache(hospital_id, "hospital", "overview")
            if cached:
                return {
                    "from_cache": True,
                    "cached_at": cached.last_updated.isoformat(),
                    "summary": cached.summary,
                    "key_insights": cached.key_insights,
                    "recommendations": cached.recommendations
                }
        
        # 获取数据摘要
        data_summary = self._get_hospital_data_summary(hospital_id)
        if not data_summary:
            return {"error": "医院不存在"}
        
        # 构建分析提示
        prompt = f"""请分析以下医院的情况，提供简洁的战略建议（控制在300字以内）：

医院信息：
- 名称：{data_summary['name']}
- 等级：{data_summary['level']}
- 科室数量：{data_summary['departments_count']}
- 产品覆盖：{data_summary['product_associations_count']}个产品关联

主要科室：
{chr(10).join([f"- {d['name']} (主任: {d['head_doctor']})" for d in data_summary['departments'][:5]])}

产品使用情况：
{chr(10).join([f"- {p['product_name']} ({p['department_name']})" for p in data_summary['product_associations'][:8]])}

请提供：
1. 医院概况分析（1-2句话）
2. 3个关键洞察
3. 3个具体建议
"""
        
        messages = [
            {"role": "system", "content": "你是医药行业战略分析专家，擅长医院市场分析和客户开发策略。"},
            {"role": "user", "content": prompt}
        ]
        
        response = await self.ai._make_request(messages, temperature=0.6, max_tokens=800)
        
        if not response or response.startswith("❌"):
            return {"error": response or "AI分析失败"}
        
        # 解析响应（简单分段）
        lines = [line.strip() for line in response.split("\n") if line.strip()]
        summary = lines[0] if lines else response[:200]
        
        # 提取洞察和建议
        insights = []
        recommendations = []
        current_section = None
        
        for line in lines[1:]:
            if "洞察" in line or "发现" in line or "观察" in line:
                current_section = "insights"
            elif "建议" in line or "推荐" in line or "策略" in line:
                current_section = "recommendations"
            elif line.startswith(("-", "•", "*", "1", "2", "3")):
                cleaned = line.lstrip("-•*123456789. ")
                if current_section == "insights" and len(insights) < 5:
                    insights.append(cleaned)
                elif current_section == "recommendations" and len(recommendations) < 5:
                    recommendations.append(cleaned)
        
        # 保存到缓存
        cache = AnalysisCache(
            entity_id=hospital_id,
            entity_type="hospital",
            analysis_type="overview",
            summary=summary,
            key_insights=insights,
            recommendations=recommendations,
            data_snapshot=data_summary
        )
        self.cache_service.save_cache(cache)
        
        return {
            "from_cache": False,
            "summary": summary,
            "key_insights": insights,
            "recommendations": recommendations,
            "full_response": response
        }

    
    # ==================== 科室分析 ====================
    
    async def analyze_department(
        self, 
        department_id: str, 
        force_refresh: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        分析科室
        
        Args:
            department_id: 科室ID
            force_refresh: 是否强制刷新
            
        Returns:
            分析结果
        """
        if not self.ai.is_enabled:
            return {"error": "AI功能未启用"}
        
        # 检查缓存
        if not force_refresh:
            cached = self.cache_service.get_cache(department_id, "department", "overview")
            if cached:
                return {
                    "from_cache": True,
                    "cached_at": cached.last_updated.isoformat(),
                    "summary": cached.summary,
                    "key_insights": cached.key_insights,
                    "recommendations": cached.recommendations
                }
        
        # 获取数据摘要
        data_summary = self._get_department_data_summary(department_id)
        if not data_summary:
            return {"error": "科室不存在"}
        
        prompt = f"""请分析以下科室的情况（控制在250字以内）：

科室信息：
- 名称：{data_summary['name']}
- 所属医院：{data_summary['hospital_name']}
- 科室主任：{data_summary['head_doctor']}
- 产品覆盖：{data_summary['product_associations_count']}个产品

使用的产品：
{', '.join(data_summary['products'][:8])}

请提供：
1. 科室特点分析（1句话）
2. 2-3个关键洞察
3. 2-3个开发建议
"""
        
        messages = [
            {"role": "system", "content": "你是医药行业科室开发专家。"},
            {"role": "user", "content": prompt}
        ]
        
        response = await self.ai._make_request(messages, temperature=0.6, max_tokens=600)
        
        if not response or response.startswith("❌"):
            return {"error": response or "AI分析失败"}
        
        # 解析响应
        lines = [line.strip() for line in response.split("\n") if line.strip()]
        summary = lines[0] if lines else response[:200]
        
        insights = []
        recommendations = []
        current_section = None
        
        for line in lines[1:]:
            if "洞察" in line or "发现" in line or "特点" in line:
                current_section = "insights"
            elif "建议" in line or "推荐" in line or "策略" in line:
                current_section = "recommendations"
            elif line.startswith(("-", "•", "*", "1", "2", "3")):
                cleaned = line.lstrip("-•*123456789. ")
                if current_section == "insights" and len(insights) < 5:
                    insights.append(cleaned)
                elif current_section == "recommendations" and len(recommendations) < 5:
                    recommendations.append(cleaned)
        
        # 保存缓存
        cache = AnalysisCache(
            entity_id=department_id,
            entity_type="department",
            analysis_type="overview",
            summary=summary,
            key_insights=insights,
            recommendations=recommendations,
            data_snapshot=data_summary
        )
        self.cache_service.save_cache(cache)
        
        return {
            "from_cache": False,
            "summary": summary,
            "key_insights": insights,
            "recommendations": recommendations,
            "full_response": response
        }
    
    # ==================== 医生分析 ====================
    
    async def analyze_doctor(
        self, 
        doctor_id: str, 
        force_refresh: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        分析医生关系和拜访策略
        
        Args:
            doctor_id: 医生ID
            force_refresh: 是否强制刷新
            
        Returns:
            分析结果
        """
        if not self.ai.is_enabled:
            return {"error": "AI功能未启用"}
        
        # 检查缓存
        if not force_refresh:
            cached = self.cache_service.get_cache(doctor_id, "doctor", "strategy")
            if cached:
                return {
                    "from_cache": True,
                    "cached_at": cached.last_updated.isoformat(),
                    "summary": cached.summary,
                    "key_insights": cached.key_insights,
                    "recommendations": cached.recommendations
                }
        
        # 获取数据摘要
        data_summary = self._get_doctor_data_summary(doctor_id)
        if not data_summary:
            return {"error": "医生不存在"}
        
        # 构建拜访历史摘要
        visits_text = ""
        if data_summary['recent_visits']:
            visits_text = "\n".join([
                f"- {v['date']}: {v['topics'][:80]} (有效性: {v['effectiveness']}/5)"
                for v in data_summary['recent_visits']
            ])
        else:
            visits_text = "暂无拜访记录"
        
        prompt = f"""请分析以下医生的情况并提供拜访策略（控制在300字以内）：

医生信息：
- 姓名：{data_summary['name']}
- 医院：{data_summary['hospital']}
- 科室：{data_summary['department']}
- 职称：{data_summary['title']}
- 关系阶段：{data_summary['relationship_stage']}
- 决策风格：{data_summary['decision_style']}
- 兴趣领域：{', '.join(data_summary['interests'][:5])}

最近拜访记录（{data_summary['recent_visits_count']}次）：
{visits_text}

请提供：
1. 关系状态评估（1-2句话）
2. 3个关键洞察
3. 3个具体的拜访建议
"""
        
        messages = [
            {"role": "system", "content": "你是资深医药代表培训师，擅长客户关系分析和拜访策略制定。"},
            {"role": "user", "content": prompt}
        ]
        
        response = await self.ai._make_request(messages, temperature=0.7, max_tokens=800)
        
        if not response or response.startswith("❌"):
            return {"error": response or "AI分析失败"}
        
        # 解析响应
        lines = [line.strip() for line in response.split("\n") if line.strip()]
        summary = lines[0] if lines else response[:200]
        
        insights = []
        recommendations = []
        current_section = None
        
        for line in lines[1:]:
            if "洞察" in line or "发现" in line or "评估" in line or "分析" in line:
                current_section = "insights"
            elif "建议" in line or "推荐" in line or "策略" in line:
                current_section = "recommendations"
            elif line.startswith(("-", "•", "*", "1", "2", "3")):
                cleaned = line.lstrip("-•*123456789. ")
                if current_section == "insights" and len(insights) < 5:
                    insights.append(cleaned)
                elif current_section == "recommendations" and len(recommendations) < 5:
                    recommendations.append(cleaned)
        
        # 保存缓存
        cache = AnalysisCache(
            entity_id=doctor_id,
            entity_type="doctor",
            analysis_type="strategy",
            summary=summary,
            key_insights=insights,
            recommendations=recommendations,
            data_snapshot=data_summary
        )
        self.cache_service.save_cache(cache)
        
        return {
            "from_cache": False,
            "summary": summary,
            "key_insights": insights,
            "recommendations": recommendations,
            "full_response": response
        }
    
    # ==================== 综合分析 ====================
    
    async def analyze_overall_strategy(self) -> Optional[Dict[str, Any]]:
        """
        分析整体业务策略
        
        Returns:
            综合分析结果
        """
        if not self.ai.is_enabled:
            return {"error": "AI功能未启用"}
        
        # 收集整体数据统计
        hospitals_count = len(list((self.fm.data_dir / "hospitals").glob("*.json")))
        departments_count = len(list((self.fm.data_dir / "departments").glob("*.json")))
        products_count = len(list((self.fm.data_dir / "products").glob("*.json")))
        doctors_count = len(list(self.fm.doctors_dir.glob("*.json")))
        
        # 获取产品关联统计
        assoc_dir = self.fm.data_dir / "associations"
        product_index_path = assoc_dir / "product_index.json"
        product_coverage = {}
        
        if product_index_path.exists():
            product_index = self.fm.read_json(product_index_path)
            if product_index:
                for product_id, assoc_ids in list(product_index.items())[:10]:
                    # 获取产品名称
                    product_path = self.fm.data_dir / "products" / f"{product_id}.json"
                    product_data = self.fm.read_json(product_path)
                    if product_data:
                        product_coverage[product_data.get("name", product_id)] = len(assoc_ids)
        
        prompt = f"""请分析当前业务整体情况并提供战略建议（控制在400字以内）：

业务数据：
- 覆盖医院：{hospitals_count}家
- 覆盖科室：{departments_count}个
- 管理产品：{products_count}个
- 医生档案：{doctors_count}位

产品覆盖情况（前10）：
{chr(10).join([f"- {name}: {count}个关联" for name, count in list(product_coverage.items())[:10]])}

请提供：
1. 业务现状评估（2-3句话）
2. 4个关键发现
3. 4个战略建议
"""
        
        messages = [
            {"role": "system", "content": "你是医药行业战略顾问，擅长市场分析和业务规划。"},
            {"role": "user", "content": prompt}
        ]
        
        response = await self.ai._make_request(messages, temperature=0.6, max_tokens=1000)
        
        if not response or response.startswith("❌"):
            return {"error": response or "AI分析失败"}
        
        # 解析响应
        lines = [line.strip() for line in response.split("\n") if line.strip()]
        summary = " ".join(lines[:2]) if len(lines) >= 2 else (lines[0] if lines else response[:300])
        
        insights = []
        recommendations = []
        current_section = None
        
        for line in lines[2:]:
            if "发现" in line or "洞察" in line or "观察" in line:
                current_section = "insights"
            elif "建议" in line or "推荐" in line or "策略" in line:
                current_section = "recommendations"
            elif line.startswith(("-", "•", "*", "1", "2", "3", "4")):
                cleaned = line.lstrip("-•*123456789. ")
                if current_section == "insights" and len(insights) < 6:
                    insights.append(cleaned)
                elif current_section == "recommendations" and len(recommendations) < 6:
                    recommendations.append(cleaned)
        
        return {
            "summary": summary,
            "key_insights": insights,
            "recommendations": recommendations,
            "full_response": response,
            "data_stats": {
                "hospitals": hospitals_count,
                "departments": departments_count,
                "products": products_count,
                "doctors": doctors_count
            }
        }
    
    # ==================== 缓存管理 ====================
    
    def invalidate_entity_cache(self, entity_id: str, entity_type: str) -> int:
        """
        使实体的所有缓存失效（当数据更新时调用）
        
        Args:
            entity_id: 实体ID
            entity_type: 实体类型
            
        Returns:
            失效的缓存数量
        """
        return self.cache_service.invalidate_cache(entity_id, entity_type)
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """获取缓存统计"""
        return self.cache_service.get_cache_stats()
    
    def cleanup_old_caches(self, days: int = 30) -> int:
        """清理旧缓存"""
        return self.cache_service.cleanup_old_caches(days)

    # ==================== 智能填表 ====================

    async def parse_visit_notes(self, raw_notes: str) -> Dict[str, Any]:
        """
        解析随手笔记，提取拜访记录

        Args:
            raw_notes: 用户粘贴的随手笔记原始文本

        Returns:
            解析后的结构化数据
        """
        if not self.ai.is_enabled:
            return {"error": "AI功能未启用", "parsed_visits": []}

        # 收集系统中已有的医生和医院信息用于匹配
        doctors = []
        doctor_files = list(self.fm.doctors_dir.glob("*.json"))
        for f in doctor_files[:100]:
            data = self.fm.read_json(f)
            if data:
                doctors.append({
                    "id": data.get("doctor_id"),
                    "name": data.get("name"),
                    "hospital": data.get("hospital", ""),
                    "department": data.get("department", "")
                })

        hospitals = []
        hosp_dir = self.fm.data_dir / "hospitals"
        if hosp_dir.exists():
            for f in hosp_dir.glob("*.json"):
                data = self.fm.read_json(f)
                if data:
                    hospitals.append({
                        "id": data.get("hospital_id"),
                        "name": data.get("name")
                    })

        # 构造提示词
        prompt = f"""你是一个医药代表的拜访记录解析助手。用户的笔记是随手的、格式自由的，你需要理解并提取信息。

【你的任务】
分析用户的随手笔记，提取出拜访记录。用户的笔记可能：
- 日期格式混乱（如"周一"、"3.17周二"、"3.20"）
- 医院名可能只说一次，后面跟多个医生（如"XX医院：张三、李四"）
- 科室可能写在医生前面（如"心内科门诊王医生"）
- 医生姓名可能不完整或只有称呼（如"刘哥"、"张主任"）
- 交流内容可能很简短（如"寒暄"、"加了微信"）

【系统中的医院】（用于匹配）：
{chr(10).join([f"- {h['name']}" for h in hospitals[:20]]) if hospitals else "(暂无医院数据)"}

【系统中的医生】（用于匹配）：
{chr(10).join([f"- {d['name']} | {d.get('hospital', '')} | {d.get('department', '')} | ID:{d['id']}" for d in doctors[:50]]) if doctors else "(暂无医生数据)"}

【用户的随手笔记】：
{raw_notes}

【通用理解指南】
- 日期理解："周一"等表示一周中的第几天，AI需根据上下文推断具体日期
- 医院匹配：用户可能只写简称（如"市医院"可能匹配"XX市人民医院"），需尝试匹配最相似的
- 医生匹配：用户可能只写名字中的两个字或称呼，需在系统医生中模糊匹配
- 交流简语：
  * "加了微信"、"加的微信" = 加了微信好友
  * "寒暄了一下"、"聊了几句" = 简单交流
  * "聊了聊"、"谈了谈" = 进行了交谈
  * "带了东西"、"拿了瓶水" = 带了小礼品
  * "打了声招呼"、"问候了一下" = 简单问候
  * "竞品多"、"有竞品" = 提到竞品问题
  * "效果好"、"产品不错" = 对产品评价正面
- 科室理解："心内科"、"骨科"、"神内"、"消化内"等是常见科室简称
- 格式理解：通常是"医院名：医生1、医生2（备注），医生3（备注）"

【输出格式 - 必须是有效的JSON数组】
返回JSON数组格式，每个元素是一天的拜访记录：
[
  {{
    "date": "周一 3.17",
    "parsed_date": "2026-03-17",
    "hospitals": [
      {{
        "name": "匹配的医院名",
        "doctors": [
          {{
            "name": "医生姓名",
            "department": "科室（如有）",
            "content": "交流内容描述",
            "matched": true/false,
            "matched_doctor_id": "系统中的doctor_id（如匹配到）",
            "insights": "从内容中提取的关键洞察"
          }}
        ]
      }}
    ]
  }}
]

【关键要求】
1. 只要笔记中出现了日期，就要解析为一条记录
2. 优先尝试将用户写的医院简称与系统医院列表模糊匹配
3. 优先尝试将用户写的医生姓名与系统医生列表模糊匹配
4. matched=true时matched_doctor_id必须是系统中存在的完整doctor_id
5. 如果医生匹配不上，matched=false，matched_doctor_id为空，但仍然要保留这条记录
6. content要尽量完整描述交流内容
7. insights可以从交流内容中提取关键信息（如"提到竞品"、"对产品感兴趣"等）"""

        try:
            response = await self.ai.chat(prompt, system="你是一个专业的拜访记录解析助手，只返回JSON格式的结果。")

            import json
            import re

            json_match = re.search(r'\[[\s\S]*\]', response)
            if not json_match:
                json_match = re.search(r'\{[\s\S]*\}', response)

            if json_match:
                result = json.loads(json_match.group())
                if isinstance(result, list):
                    return {"parsed_visits": result}
                return result
            else:
                return {"error": "AI返回格式错误", "parsed_visits": []}

        except Exception as e:
            return {"error": str(e), "parsed_visits": []}


# 创建全局实例
ai_data_analyzer = AIDataAnalyzer()
