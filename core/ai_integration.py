"""
DeepSeek AI 集成模块
"""
import httpx
import time
import random
import asyncio
from typing import Optional, List, Dict, Any
from .file_manager import file_manager


class AIIntegration:
    """DeepSeek AI 集成"""
    
    def __init__(self):
        self._enabled = False
        self._api_key = ""
        self._base_url = "https://api.deepseek.com"
        self._model = "deepseek-chat"
        self._load_config()
    
    def _load_config(self) -> None:
        """从配置文件加载 AI 设置"""
        config = file_manager.get_config()
        self._enabled = config.get("ai_enabled", False)
        self._deepseek_api_key = config.get("deepseek_api_key", "")
        self._deepseek_base_url = config.get("deepseek_base_url", "https://api.deepseek.com")
        self._deepseek_model = config.get("deepseek_model", "deepseek-chat")
        
        self._xiaomi_api_key = config.get("xiaomi_api_key", "")
        self._xiaomi_base_url = config.get("xiaomi_base_url", "https://api.xiaomimimo.com/v1")
        self._xiaomi_model = config.get("xiaomi_model", "mimo-v2-flash")
        
        # Provider selection: 'deepseek' or 'xiaomi'
        self._active_provider = config.get("ai_provider", "deepseek")
        
        if self._active_provider == "xiaomi":
            self._api_key = self._xiaomi_api_key
            self._base_url = self._xiaomi_base_url
            self._model = self._xiaomi_model
        else:
            self._api_key = self._deepseek_api_key
            self._base_url = self._deepseek_base_url
            self._model = self._deepseek_model
    
    @property
    def is_enabled(self) -> bool:
        """检查 AI 是否启用"""
        return self._enabled and bool(self._api_key)
    
    def enable(self) -> bool:
        """启用 AI 分析"""
        if not self._api_key:
            print("错误：未配置 DeepSeek API Key")
            return False
        self._enabled = True
        file_manager.update_config({"ai_enabled": True})
        return True
    
    def disable(self) -> None:
        """禁用 AI 分析"""
        self._enabled = False
        file_manager.update_config({"ai_enabled": False})
    
    def set_api_key(self, api_key: str) -> None:
        """设置 API Key"""
        self._api_key = api_key
        file_manager.update_config({"deepseek_api_key": api_key})
    
    def _make_request(
        self, 
        messages: List[Dict[str, str]], 
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> Optional[str]:
        """
        发送请求到 DeepSeek API
        
        Args:
            messages: 对话消息列表
            temperature: 温度参数
            max_tokens: 最大token数
            
        Returns:
            AI 回复内容
        """
    async def _make_request(
        self, 
        messages: List[Dict[str, str]], 
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> Optional[str]:
        """
        发送请求到 DeepSeek API (带重试机制 - 异步)
        """
        if not self.is_enabled:
            return None
        
        try:
            # 构建正确的 API URL
            base_url = self._base_url.rstrip("/")
            if base_url.endswith("/v1"):
                api_url = f"{base_url}/chat/completions"
            else:
                api_url = f"{base_url}/v1/chat/completions"
            
            payload = {
                "model": self._model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            
            # Xiaomi MiMo 特有参数
            if self._active_provider == "xiaomi":
                payload["thinking"] = {"type": "disabled"}
                payload["frequency_penalty"] = 0
            
            # 重试逻辑
            max_retries = 3
            last_error = None
            
            for attempt in range(max_retries):
                try:
                    async with httpx.AsyncClient(timeout=60.0) as client:
                        response = await client.post(
                            api_url,
                            headers={
                                "Authorization": f"Bearer {self._api_key}",
                                "Content-Type": "application/json",
                                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                            },
                            json=payload
                        )
                        
                        if response.status_code == 429:
                            if attempt < max_retries - 1:
                                delay = (2 ** attempt) + random.uniform(0.5, 1.5)
                                print(f"⚠️ API 限流 (429). {delay:.1f}秒后重试...")
                                await asyncio.sleep(delay)
                                continue
                        
                        response.raise_for_status()
                        result = response.json()
                        return result["choices"][0]["message"]["content"]
                        
                except httpx.HTTPStatusError as e:
                    if e.response.status_code == 429 and attempt < max_retries - 1:
                        delay = (2 ** attempt) + random.uniform(0.5, 1.5)
                        print(f"⚠️ API 限流 (429). {delay:.1f}秒后重试...")
                        await asyncio.sleep(delay)
                        continue
                    last_error = f"❌ API 请求失败 ({e.response.status_code}): {e.response.text[:100]}"
                    print(f"API 请求失败: {e.response.status_code} - {e.response.text}")
                    
                except Exception as e:
                    last_error = f"❌ AI 连接错误: {str(e)[:100]}"
                    print(f"AI 请求错误: {str(e)}")
            
            return last_error
            
        except Exception as e:
            print(f"系统错误: {e}")
            return f"❌ 系统错误: {str(e)}"

    
    # ==================== AI 功能 ====================
    
    async def summarize_visit(self, visit_data: Dict[str, Any]) -> Optional[str]:
        """
        生成拜访总结
        
        Args:
            visit_data: 拜访数据
            
        Returns:
            AI 生成的总结
        """
        prompt = f"""请根据以下拜访记录，生成一份简洁的总结（100-200字）：

拜访日期：{visit_data.get('visit_date', '')}
讨论话题：{visit_data.get('key_topics', '')}
医生顾虑：{visit_data.get('doctor_concerns', '')}
医生异议：{visit_data.get('objections', '')}
我的回应：{visit_data.get('responses', '')}
新发现：{visit_data.get('new_insights', '')}

请提供：
1. 核心要点（1-2句话）
2. 关键洞察
3. 下一步建议
"""
        
        messages = [
            {"role": "system", "content": "你是一位专业的医药代表教练，帮助分析拜访记录并提供改进建议。"},
            {"role": "user", "content": prompt}
        ]

        return await self._make_request(messages)

    async def chat(self, prompt: str, system: str = "你是一个有帮助的AI助手。") -> Optional[str]:
        """
        通用对话接口

        Args:
            prompt: 用户输入
            system: 系统提示

        Returns:
            AI 回复内容
        """
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt}
        ]

        return await self._make_request(messages, max_tokens=4000)

    async def suggest_preparation(
        self, 
        doctor_data: Dict[str, Any], 
        last_visit: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        生成拜访准备建议
        
        Args:
            doctor_data: 医生数据
            last_visit: 上次拜访数据
            
        Returns:
            AI 生成的准备建议
        """
        last_visit_info = ""
        if last_visit:
            last_visit_info = f"""
上次拜访信息：
- 日期：{last_visit.get('visit_date', '')}
- 话题：{last_visit.get('key_topics', '')}
- 待跟进：{last_visit.get('follow_up_tasks', '')}
"""
        
        prompt = f"""请为以下医生拜访提供准备建议：

医生信息：
- 科室：{doctor_data.get('department', '')}
- 职称：{doctor_data.get('title', '')}
- 兴趣领域：{', '.join(doctor_data.get('interests', []))}
- 决策风格：{doctor_data.get('decision_style', '')}
- 未满足需求：{doctor_data.get('unmet_needs', '')}
- 当前关系阶段：{doctor_data.get('relationship_stage', '')}
{last_visit_info}

请提供：
1. 本次拜访的建议目标
2. 可探索的问题
3. 推荐准备的资料
4. 沟通策略建议
"""
        
        messages = [
            {"role": "system", "content": "你是一位资深医药代表培训师，擅长制定拜访策略。"},
            {"role": "user", "content": prompt}
        ]
        
        return await self._make_request(messages)
    
    async def generate_daily_suggestions(
        self,
        recent_visits: List[Dict[str, Any]],
        pending_tasks: List[str],
        recent_reflections: List[Dict[str, Any]]
    ) -> Optional[str]:
        """
        生成每日行动建议
        
        Args:
            recent_visits: 最近的拜访记录
            pending_tasks: 待办任务
            recent_reflections: 最近的反思（已过滤敏感信息）
            
        Returns:
            AI 生成的每日建议
        """
        visits_summary = "\n".join([
            f"- {v.get('visit_date')}: {v.get('key_topics', '')[:50]}..."
            for v in recent_visits[:5]
        ])
        
        tasks_summary = "\n".join([f"- {t}" for t in pending_tasks[:10]])
        
        prompt = f"""请根据以下信息，生成今日行动建议：

最近拜访：
{visits_summary}

待办任务：
{tasks_summary}

请提供：
1. 今日三个最重要的任务
2. 建议优先拜访的医生类型
3. 今日学习/改进重点
"""
        
        messages = [
            {"role": "system", "content": "你是一位效率教练，帮助医药代表制定每日行动计划。"},
            {"role": "user", "content": prompt}
        ]
        
        return await self._make_request(messages)
    
    async def analyze_doctor_relationship(self, doctor_data: Dict[str, Any], visits: List[Dict[str, Any]]) -> Optional[str]:
        """
        分析医生关系状态
        
        Args:
            doctor_data: 医生数据
            visits: 与该医生的拜访记录
            
        Returns:
            关系分析报告
        """
        visits_summary = "\n".join([
            f"- {v.get('visit_date')}: 有效性{v.get('response_effectiveness', 3)}/5, 氛围: {v.get('emotional_tone', '')}"
            for v in visits[:10]
        ])
        
        prompt = f"""请分析与以下医生的关系发展状况：

医生信息：
- 科室：{doctor_data.get('department', '')}
- 职称：{doctor_data.get('title', '')}
- 当前关系阶段：{doctor_data.get('relationship_stage', '')}
- 兴趣领域：{', '.join(doctor_data.get('interests', []))}

拜访历史：
{visits_summary}

请分析：
1. 关系发展趋势
2. 沟通障碍识别
3. 关系提升建议
"""
        
        messages = [
            {"role": "system", "content": "你是一位医药行业客户关系专家。"},
            {"role": "user", "content": prompt}
        ]
        
        return await self._make_request(messages)


# 创建全局实例
ai_integration = AIIntegration()
