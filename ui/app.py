"""
医药信息专员个人职业操作系统 - 用户界面
使用 NiceGUI 构建现代化桌面应用
"""
import sys
import os
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from nicegui import ui, app
from datetime import datetime, timedelta
from typing import Optional
from pathlib import Path

# 导入服务
from core.file_manager import file_manager
from core.ai_integration import ai_integration
from core.decision_engine import decision_engine
from core.ai_chat import ai_chat_service
from modules.doctor_manager.service import doctor_service
from modules.visit_preparation.service import preparation_service
from modules.visit_summary.service import visit_summary_service
from modules.personal_growth.service import personal_growth_service
from modules.knowledge_base.service import knowledge_service
from modules.reporting.service import reporting_service
from modules.contact_manager.service import contact_service
from modules.reporting.summary_export import summary_export_service
from modules.hospital_manager.service import hospital_service
from modules.data_center.service import data_center_service

# 导入准备包服务
from core.preparation_package import preparation_package_service

# 导入样式
from ui.styles import inject_styles, NAV_STRUCTURE


class MedRepApp:
    """医药信息专员应用"""
    
    # 欢迎内容
    WELCOME_CONTENT = """
# 👋 欢迎使用医药信息专员助手！

这是一个专为医药代表设计的个人职业操作系统，帮助您：

## 🎯 核心功能

### 日常工作
- **📊 今日行动** - 智能推荐每日重点任务
- **🤖 AI 助手** - 与 AI 对话，获取精准指导和数据分析

### 拜访管理
- **📝 拜访准备** - 结构化准备，减少不确定感
- **✅ 拜访记录** - 记录拜访详情，自动生成报告
- **👥 联系人** - 管理医生、护士、同事等多类型联系人

### 数据管理
- **🏥 医院管理** - 管理医院、科室、产品、竞品信息
- **🔗 产品关联** - 管理产品与医院科室的关联关系
- **📊 数据中心** - 统一查看和管理所有数据

### 客户管理
- **📋 客户追踪** - 基于销售管理"4张表格"理念的客户管理系统
  - **客户开发表** - 记录开发全过程（渠道、首次联系、加微信等）
  - **客户追踪表** - 记录每次跟进详情（话术、回复情况、效果评分）
  - **客户分类表** - A/B/C/D类客户分类，自动建议跟进频率
  - **统计分析表** - 周报/月报，新增客户、A类客户增长等核心指标
  - **待跟进提醒** - 自动提醒需要跟进的客户
  - **Excel导出** - 一键导出所有表格数据

### 分析成长
- **💭 成长反思** - 私密记录，追踪个人成长
- **📚 知识库** - 管理病种、产品、市场知识
- **🤖 AI 数据分析** - 智能分析医院、科室、医生数据
- **📊 智能总结** - AI 分析关联，生成报告
- **✨ 智能填表** - AI 智能解析随手笔记，一键导入拜访记录

## 📝 智能填表功能

### 功能说明
有时候您可能没有时间在拜访当时详细记录，只随手记了一些关键词。**智能填表**功能可以帮您：
- 将随手记的笔记内容 AI 智能解析
- 自动提取日期、医院、医生、交流内容
- 一键导入为规范的拜访记录

### 支持的笔记格式
AI 可以理解各种随手的记录方式：

**格式示例1：**
```
周一 XX医院：张三，拿了瓶水寒暄了一下、李四加上了微信
XX科室：王五说竞品多
```

**格式示例2：**
```
3.17周二 XX医院：张三简单聊了一下，病房见了李四
XX科室：王五挺忙聊了两句，加了微信
```

**格式示例3：**
```
3.19周四 XX医院：张三李四带瓶水打个招呼
XX科室：慢病门诊拿了两瓶水
```

### 记录要点
- **日期**：写清楚哪天（可以用"周一"、"3.17"等格式）
- **医院**：说明在哪个医院（宝石花、中医院、盘山县等）
- **医生姓名**：写下拜访的医生名字
- **交流内容**：简单几个字描述（寒暄、加微信、聊产品等）
- **科室信息**（可选）：如果有就写（心内科、骨科、神内等）

### 使用步骤
1. 进入 **AI数据分析** → **智能填表**
2. 将随手记的内容粘贴到文本框
3. 点击 **AI解析**，查看解析结果
4. 如需调整，点击编辑按钮修改
5. 点击 **确认导入** 批量创建拜访记录

## 🚀 快速开始

### 基础设置
1. **配置 AI**：点击 "⚙️ 系统设置"，选择 AI 提供商（DeepSeek 或小米 MiMo），输入 API Key
2. **添加数据**：在 "数据管理" 中添加医院、科室、产品等基础信息
3. **添加联系人**：在 "联系人" 中添加医生、护士等联系人

### 使用客户追踪管理（推荐）
1. **添加开发记录**：进入 "客户管理" > "客户追踪" > "客户开发表"，记录客户开发过程
2. **记录跟进**：每次跟进后，在 "客户追踪表" 中记录详情和效果评分
3. **管理分类**：根据客户表现，在 "客户分类表" 中升降级客户
4. **查看统计**：定期查看 "统计分析表"，了解新增客户和A类客户增长情况
5. **处理提醒**：每天查看 "待跟进提醒"，确保不遗漏任何客户

### 日常工作流程
1. **开始记录**：每次拜访后记录总结
2. **日常反思**：每天花 5 分钟填写成长反思

## 💡 使用建议

### 日常工作
- 每天开始工作前，查看 "今日行动" 了解重点
- 查看 "待跟进提醒"，按优先级跟进客户（A类客户优先）
- 拜访前使用 "拜访准备" 理清思路
- 有困惑时随时打开 "AI 助手" 寻求指导

### 客户管理
- 每次跟进后立即记录，不要拖延
- 记录开口话术，积累有效的沟通模板
- 每周五回顾客户分类，及时升降级
- 每周一生成统计报告，对比上周数据
- **核心指标**：A类客户只能增长，不能减少！

### 数据分析
- 使用 "AI 数据分析" 深入了解医院和医生情况
- 每周使用 "智能总结" 回顾进展

## 🔒 隐私保护

所有数据存储在本地 `data/` 文件夹，不会上传云端。
个人反思内容标记为私密，不会出现在任何导出报告中。

## 📊 客户追踪管理核心理念

- **工具控制行为** - 通过4张表格规范销售过程
- **流程控制结果** - 按流程做就有结果
- **A类客户只能增长不能减少** - 核心考核指标

### 客户分类标准
- **A类**：有意愿有需求，保持紧密联系（建议3-5天跟进一次）
- **B类**：偶尔回复，当下需求不明确（建议7天跟进一次）
- **C类**：偶尔回祝福，不回产品信息（建议10天跟进一次）
- **D类**：不回复，像死人一样（建议15天跟进一次或考虑放弃）

---

*如有问题，请点击 "⚙️ 系统设置" > "关于" 查看联系方式*
"""
    
    def __init__(self):
        self.current_page = "home"
        self.setup_theme()
        self.first_run = self._check_first_run()
    
    def _check_first_run(self) -> bool:
        """检查是否首次运行"""
        config = file_manager.get_config()
        return not config.get('has_shown_welcome', False)
    
    def _mark_welcome_shown(self):
        """标记欢迎页已显示"""
        file_manager.update_config({'has_shown_welcome': True})
    
    def show_welcome_dialog(self):
        """显示欢迎对话框"""
        with ui.dialog() as dialog, ui.card().classes('w-full').style('max-width: 700px; max-height: 80vh; overflow-y: auto'):
            ui.markdown(self.WELCOME_CONTENT)
            with ui.row().classes('w-full justify-end q-mt-md'):
                ui.button('我知道了，开始使用', on_click=lambda: [dialog.close(), self._mark_welcome_shown()]).props('color=primary')
        dialog.open()
    
    def setup_theme(self):
        """设置主题"""
        # 注入毛玻璃样式
        inject_styles()
        
        ui.colors(
            primary='#667eea',
            secondary='#764ba2',
            accent='#4facfe',
            dark='#1a1a2e',
            positive='#38ef7d',
            negative='#f5576c',
            info='#00f2fe',
            warning='#f093fb'
        )
    
    def create_header(self):
        """创建顶部导航栏"""
        with ui.header().classes('glass-header q-pa-sm'):
            with ui.row().classes('w-full items-center'):
                # Logo 和标题
                ui.label('🧠 医药信息专员助手').classes('text-h6 text-white q-mr-lg')
                
                # 主导航标签 (动态刷新)
                self.header_tabs_row = ui.row().classes('nav-tabs')
                self.refresh_header_tabs()
                
                ui.space()
                
                # 右侧状态
                with ui.row().classes('items-center q-gutter-sm'):
                    ai_status = "🟢 AI已启用" if ai_integration.is_enabled else "⚫ AI未启用"
                    status_class = 'status-badge status-active' if ai_integration.is_enabled else 'status-badge status-inactive'
                    self.ai_status_label = ui.label(ai_status).classes(status_class)
                    ui.label(datetime.now().strftime("%Y年%m月%d日")).classes('text-white text-caption')
    
    def refresh_header_tabs(self):
        """刷新顶部导航标签状态"""
        if not hasattr(self, 'header_tabs_row'):
            return
            
        self.header_tabs_row.clear()
        with self.header_tabs_row:
            for category_key, category_data in NAV_STRUCTURE.items():
                is_active = getattr(self, 'current_category', 'daily') == category_key
                ui.button(
                    category_data['label'],
                    on_click=lambda ck=category_key: self.switch_category(ck)
                ).props('flat no-caps').classes(f'nav-tab {"active" if is_active else ""}')
    
    def create_sub_nav(self):
        """创建子导航面板"""
        category = getattr(self, 'current_category', 'daily')
        category_data = NAV_STRUCTURE.get(category, NAV_STRUCTURE['daily'])
        
        with ui.row().classes('sub-nav-panel w-full animate-in'):
            for page_key, label, color in category_data['items']:
                is_active = self.current_page == page_key
                with ui.button(on_click=lambda pk=page_key: self.navigate(pk)).props('flat no-caps').classes(f'sub-nav-item {"active" if is_active else ""}'):
                    # 兼容不同版本的 NiceGUI
                    try:
                        ui.html(f'<span class="nav-dot dot-{color}"></span>', sanitize=False)
                    except TypeError:
                        # 旧版本 NiceGUI 不支持 sanitize 参数
                        ui.html(f'<span class="nav-dot dot-{color}"></span>')
                    ui.label(label)
    
    def switch_category(self, category: str):
        """切换导航分类"""
        self.current_category = category
        # 默认导航到该分类的第一个页面
        first_page = NAV_STRUCTURE[category]['items'][0][0]
        self.navigate(first_page)
    
    def create_sidebar(self):
        """创建侧边导航 - 已弃用，保留空方法兼容"""
        pass  # 改用顶部水平导航
    
    def navigate(self, page: str):
        """页面导航"""
        self.current_page = page
        
        # 更新当前分类
        for cat_key, cat_data in NAV_STRUCTURE.items():
            for item in cat_data['items']:
                if item[0] == page:
                    self.current_category = cat_key
                    break
        
        # 刷新子导航和内容
        if hasattr(self, 'sub_nav_area'):
            self.sub_nav_area.clear()
            with self.sub_nav_area:
                self.create_sub_nav()
        
        # 刷新主导航高亮
        self.refresh_header_tabs()
        
        self.content_area.clear()
        
        with self.content_area:
            if page == "home":
                self.render_home()
            elif page == "daily_action":
                self.render_daily_action()
            elif page == "data_center":
                self.render_data_center()
            elif page == "hospitals":
                self.render_hospitals()
            elif page == "customer_tracking":
                self.render_customer_tracking()
            elif page == "ai_chat":
                self.render_ai_chat()
            elif page == "ai_analysis":
                self.render_ai_analysis()
            elif page == "preparation":
                self.render_preparation()
            elif page == "visit":
                self.render_visit()
            elif page == "contacts":
                self.render_contacts()
            elif page == "doctors":
                self.render_doctors()
            elif page == "reflection":
                self.render_reflection()
            elif page == "knowledge":
                self.render_knowledge()
            elif page == "reports":
                self.render_reports()
            elif page == "smart_export":
                self.render_smart_export()
            elif page == "settings":
                self.render_settings()
    
    # ==================== 页面渲染 ====================
    
    def render_home(self):
        """渲染首页"""
        # 欢迎横幅：日期 + 问候 + AI状态
        now = datetime.now()
        hour = now.hour
        if hour < 6:
            greeting = '夜深了'
        elif hour < 12:
            greeting = '早上好'
        elif hour < 14:
            greeting = '中午好'
        elif hour < 18:
            greeting = '下午好'
        else:
            greeting = '晚上好'
        weekday_names = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
        ai_on = ai_integration.is_enabled

        with ui.card().classes('glass-card w-full p-5 mb-4'):
            with ui.row().classes('w-full items-center justify-between'):
                with ui.column():
                    ui.label(f'{greeting}，今天也加油！').classes('text-h5 text-white font-bold').style('letter-spacing: 0.02em;')
                    ui.label(f'📅 {now.strftime("%Y年%m月%d日")} {weekday_names[now.weekday()]}').classes('text-body2 text-grey q-mt-xs')
                with ui.row().classes('items-center gap-3'):
                    ui.label('🟢 AI 已就绪' if ai_on else '⚫ AI 未启用').classes(
                        'status-badge ' + ('status-active' if ai_on else 'status-inactive'))
                    ui.button('💬 问 AI', on_click=lambda: self.navigate('ai_chat')).classes('glass-btn') if ai_on else ui.button('⚙️ 启用 AI', on_click=lambda: self.navigate('settings')).classes('glass-btn-secondary')

        # 统计卡片行 - 使用更紧凑的网格布局
        with ui.grid().classes('w-full gap-4 grid-cols-2 md:grid-cols-4'):
            doctors_count = len(doctor_service.list_doctors())
            visits_count = len(visit_summary_service.list_visits(limit=30))
            contacts_count = len(contact_service.list_contacts())
            today_reflection = personal_growth_service.has_reflected_today()

            # 医生档案卡片
            with ui.card().classes('glass-card p-4 text-center'):
                ui.label(str(doctors_count)).classes('text-3xl font-bold text-blue-4')
                ui.label('👨‍⚕️ 医生档案').classes('text-grey')

            # 本月拜访卡片
            with ui.card().classes('glass-card p-4 text-center'):
                ui.label(str(visits_count)).classes('text-3xl font-bold text-green-4')
                ui.label('📝 本月拜访').classes('text-grey')

            # 联系人卡片
            with ui.card().classes('glass-card p-4 text-center'):
                ui.label(str(contacts_count)).classes('text-3xl font-bold text-yellow-4')
                ui.label('👥 联系人').classes('text-grey')

            # 今日反思卡片
            with ui.card().classes('glass-card p-4 text-center'):
                ui.label('✓' if today_reflection else '○').classes('text-3xl font-bold ' + ('text-green-4' if today_reflection else 'text-grey'))
                ui.label('今日反思').classes('text-grey')

        # 今日状态与快捷操作合并一行
        with ui.grid().classes('w-full gap-4 mt-4 grid-cols-1 md:grid-cols-2'):
            # 今日状态卡片
            with ui.card().classes('glass-card p-4'):
                ui.label('📋 今日状态').classes('text-subtitle1 font-bold text-white mb-3')
                with ui.row().classes('gap-4'):
                    action = decision_engine.get_today_action()
                    ui.label(f'行动单: {"✅ 已生成" if action else "❌ 未生成"}').classes('text-body2 ' + ('text-green-4' if action else 'text-orange-4'))
                    ui.label(f'反思: {"✅ 已完成" if today_reflection else "⏳ 待完成"}').classes('text-body2 ' + ('text-green-4' if today_reflection else 'text-orange-4'))

            # 快捷操作卡片
            with ui.card().classes('glass-card p-4'):
                ui.label('⚡ 快捷操作').classes('text-subtitle1 font-bold text-white mb-3')
                with ui.row().classes('gap-2'):
                    ui.button('📝 拜访', on_click=lambda: self.navigate('visit')).props('flat size=sm color=primary')
                    ui.button('📖 准备', on_click=lambda: self.navigate('preparation')).props('flat size=sm color=secondary')
                    ui.button('💭 反思', on_click=lambda: self.navigate('reflection')).props('flat size=sm color=accent')

        # 待办事项
        with ui.card().classes('glass-card w-full p-4 mt-4'):
            ui.label('🎯 待办事项').classes('text-subtitle1 font-bold text-white mb-3')
            from core.analyzer import analyzer
            tasks = analyzer.get_pending_tasks()[:5]
            if tasks:
                with ui.column().classes('gap-2'):
                    for task in tasks:
                        ui.label(f'• {task[:60]}{"..." if len(task) > 60 else ""}').classes('text-body2 text-white')
            else:
                ui.label('暂无待办事项').classes('text-caption text-grey')
    
    def render_daily_action(self):
        """渲染今日行动单"""
        ui.label('📊 今日行动单').classes('page-title')

        action = decision_engine.get_today_action()
        if not action:
            with ui.card().classes('glass-card w-full q-pa-lg'):
                ui.label('今日行动单尚未生成').classes('section-title')
                ui.label('生成后 AI 将根据您的拜访记录、待办事项和反思，智能规划今日重点').classes('text-body2 text-grey q-mb-md')
                ui.button('⚡ 立即生成', on_click=self.generate_action).classes('glass-btn')
        else:
            with ui.card().classes('glass-card w-full q-pa-lg'):
                with ui.row().classes('w-full items-center justify-between q-mb-md'):
                    ui.label(f'📅 {action.date}').classes('text-h6 text-white')
                    ui.button('🔄 重新生成', on_click=self.generate_action).classes('glass-btn-secondary').props('size=sm')

                with ui.card().classes('glass-card-secondary q-pa-md q-mb-md w-full'):
                    ui.label('🎯 今日重点任务').classes('section-title')
                    with ui.column().classes('gap-2'):
                        for i, task in enumerate(action.top_tasks, 1):
                            with ui.row().classes('items-center gap-3'):
                                ui.label(f'{i}').classes('text-h6 font-bold').style('width: 28px; height: 28px; border-radius: 50%; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; display: flex; align-items: center; justify-content: center; flex-shrink: 0;')
                                ui.label(task).classes('text-body1 text-white')

                with ui.grid().classes('w-full gap-3 grid-cols-1 md:grid-cols-3'):
                    with ui.card().classes('glass-card-secondary p-3'):
                        ui.label('👨‍⚕️ 优先拜访').classes('text-caption text-grey')
                        ui.label(action.priority_doctor).classes('text-body1 text-white font-bold')
                    with ui.card().classes('glass-card-secondary p-3'):
                        ui.label('📚 推荐学习').classes('text-caption text-grey')
                        ui.label(action.recommended_learning_topic).classes('text-body1 text-white font-bold')
                    with ui.card().classes('glass-card-secondary p-3'):
                        ui.label('💪 改进重点').classes('text-caption text-grey')
                        ui.label(action.key_improvement_focus).classes('text-body1 text-white font-bold')

                if action.ai_suggestions:
                    with ui.card().classes('glass-card-secondary q-pa-md mt-4 w-full'):
                        ui.label('🤖 AI 建议').classes('section-title')
                        ui.markdown(action.ai_suggestions)
    
    def render_preparation(self):
        """渲染拜访准备页面"""
        ui.label('📝 拜访准备').classes('page-title')
        
        with ui.row().classes('w-full q-gutter-md'):
            # 左侧：准备表单
            with ui.card().classes('glass-card col-6 q-pa-lg'):
                ui.label('新建拜访准备').classes('text-h6 text-white q-mb-md')
                
                # 获取联系人选项
                doctors = doctor_service.list_doctors()
                contacts = contact_service.list_contacts()
                
                # 合并选项
                contact_options = {}
                for d in doctors:
                    contact_options[f"doctor_{d['doctor_id']}"] = f"👨‍⚕️ {d['name']}"
                for c in contacts:
                    contact_options[f"contact_{c['contact_id']}"] = f"👤 {c['name']}"
                
                self.prep_contact = ui.select(
                    label='选择拜访对象',
                    options=contact_options,
                    with_input=True
                ).classes('w-full glass-input')
                
                self.prep_date = ui.input(
                    label='计划拜访日期',
                    value=datetime.now().strftime('%Y-%m-%d')
                ).classes('w-full glass-input')
                
                self.prep_goal = ui.textarea(
                    label='🎯 拜访目标（本次想达成什么）'
                ).classes('w-full glass-input')
                
                self.prep_question = ui.textarea(
                    label='❓ 探索性问题（想了解什么）'
                ).classes('w-full glass-input')
                
                self.prep_concerns = ui.textarea(
                    label='⚠️ 可能的顾虑/风险'
                ).classes('w-full glass-input')
                
                self.prep_data = ui.textarea(
                    label='📄 准备资料要点'
                ).classes('w-full glass-input')
                
                self.prep_notes = ui.textarea(
                    label='📌 备注'
                ).classes('w-full glass-input')
                
                with ui.row().classes('q-mt-lg q-gutter-md'):
                    ui.button('保存准备', on_click=self.save_preparation).classes('glass-btn')
                    ui.button('📦 生成准备包', on_click=self.export_preparation_package).classes('glass-btn')
                    if ai_integration.is_enabled:
                        ui.button('🤖 AI建议', on_click=self.get_ai_prep_suggestion).classes('glass-btn-secondary')
            
            # 右侧：历史准备和导出包
            with ui.column().classes('col-5 q-gutter-md'):
                # 历史准备列表
                with ui.card().classes('glass-card q-pa-lg'):
                    ui.label('📋 历史准备').classes('text-h6 text-white q-mb-md')
                    self.prep_list_container = ui.column().classes('w-full')
                    self.refresh_prep_list()
                
                # 已导出的准备包
                with ui.card().classes('glass-card q-pa-lg'):
                    ui.label('📦 已导出准备包').classes('text-h6 text-white q-mb-md')
                    self.package_list_container = ui.column().classes('w-full')
                    self.refresh_package_list()
    
    async def export_preparation_package(self):
        """导出准备包"""
        if not self.prep_contact.value:
            ui.notify('请先选择拜访对象', type='warning')
            return
        
        contact_val = self.prep_contact.value
        if contact_val.startswith('doctor_'):
            contact_id = contact_val.replace('doctor_', '')
            contact_type = 'doctor'
        else:
            contact_id = contact_val.replace('contact_', '')
            contact_type = 'contact'
        
        try:
            ui.notify('正在生成准备包...', type='info')
            filepath, content = await preparation_package_service.generate_package(
                contact_id=contact_id,
                contact_type=contact_type,
                visit_date=self.prep_date.value,
                visit_goal=self.prep_goal.value,
                include_knowledge=True,
                include_history=True,
                include_ai_suggestions=ai_integration.is_enabled
            )
            
            ui.notify(f'准备包已导出: {filepath}', type='positive')
            self.refresh_package_list()
            
            # 显示预览
            with ui.dialog() as dialog, ui.card().classes('glass-card w-full').style('max-width: 800px; max-height: 80vh; overflow-y: auto'):
                ui.markdown(content)
                with ui.row().classes('w-full justify-end q-mt-md'):
                    ui.button('关闭', on_click=dialog.close).classes('glass-btn')
            dialog.open()
            
        except Exception as e:
            ui.notify(f'导出失败: {str(e)}', type='negative')
    
    def refresh_package_list(self):
        """刷新准备包列表"""
        if not hasattr(self, 'package_list_container'):
            return
        self.package_list_container.clear()
        with self.package_list_container:
            packages = preparation_package_service.list_packages()[:5]
            if packages:
                for pkg in packages:
                    with ui.element('div').classes('glass-list-item'):
                        with ui.row().classes('w-full items-center justify-between'):
                            ui.label(pkg['filename'][:30]).classes('text-white')
                            ui.button('查看', on_click=lambda p=pkg['path']: self.view_package(p)).props('flat dense size=sm color=primary')
            else:
                ui.label('暂无导出的准备包').classes('text-secondary')
    
    def view_package(self, path: str):
        """查看准备包"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            with ui.dialog() as dialog, ui.card().classes('glass-card w-full').style('max-width: 800px; max-height: 80vh; overflow-y: auto'):
                ui.markdown(content)
                with ui.row().classes('w-full justify-end q-mt-md'):
                    ui.button('关闭', on_click=dialog.close).classes('glass-btn')
            dialog.open()
        except Exception as e:
            ui.notify(f'无法打开: {str(e)}', type='negative')
    
    def render_visit(self):
        """渲染拜访记录页面"""
        ui.label('📝 拜访记录').classes('page-title')

        with ui.row().classes('w-full q-gutter-md'):
            # 左侧：双标签记录表单
            with ui.card().classes('glass-card col-7 q-pa-lg'):
                with ui.tabs().classes('w-full text-white') as tabs:
                    tab_record = ui.tab('交流记录', icon='people')
                    tab_private = ui.tab('个人总结', icon='lock')
                    tab_ai = ui.tab('AI分析', icon='smart_toy')

                with ui.tab_panels(tabs, value=tab_record).classes('w-full bg-transparent'):
                    # --- 客户交流记录 ---
                    with ui.tab_panel(tab_record):
                        ui.label('客户交流记录').classes('text-h6 text-white q-mb-md')

                        with ui.row().classes('w-full items-center q-gutter-md'):
                            ui.button('📅 选择日期查看历史', on_click=self.show_date_picker_for_visit).classes('glass-btn-secondary q-mb-md')

                        with ui.row().classes('w-full q-gutter-md'):
                            doctors = doctor_service.list_doctors()
                            contacts = contact_service.list_contacts()
                            contact_options = {}
                            for d in doctors:
                                contact_options[d['doctor_id']] = f"👨‍⚕️ {d['name']}"
                            for c in contacts:
                                contact_options[c['contact_id']] = f"👤 {c['name']}"

                            self.visit_contact = ui.select(
                                label='选择交流对象',
                                options=contact_options,
                                with_input=True
                            ).classes('w-full glass-input')

                            self.visit_date = ui.input(
                                label='交流日期',
                                value=datetime.now().strftime('%Y-%m-%d')
                            ).classes('w-full glass-input')

                        self.visit_topics = ui.textarea(
                            label='🗣️ 讨论话题'
                        ).classes('w-full glass-input')

                        self.visit_concerns = ui.textarea(
                            label='🤔 客户关注点/需求'
                        ).classes('w-full glass-input')

                        self.visit_objections = ui.textarea(
                            label='⚠️ 客户异议'
                        ).classes('w-full glass-input')

                        self.visit_responses = ui.textarea(
                            label='💬 我的回应'
                        ).classes('w-full glass-input')

                        self.visit_next_step = ui.textarea(
                            label='📅 后续跟进计划'
                        ).classes('w-full glass-input')

                        ui.label('此次交流效果 (1-5分)').classes('text-white q-mt-md')
                        self.visit_effectiveness = ui.slider(min=1, max=5, value=3).props('label-always color=yellow').classes('w-full')

                        with ui.row().classes('w-full q-gutter-md'):
                            self.visit_save_btn = ui.button('💾 保存交流记录', on_click=self.save_visit).classes('glass-btn q-mt-lg')
                            self.visit_edit_btn = ui.button('✏️ 更新记录', on_click=self.update_visit).classes('glass-btn q-mt-lg hidden')
                            self.visit_cancel_edit_btn = ui.button('❌ 取消编辑', on_click=self.cancel_edit_visit).classes('glass-btn-secondary q-mt-lg hidden')

                    # --- 个人隐私总结 ---
                    with ui.tab_panel(tab_private):
                        ui.label('个人成长总结 (隐私)').classes('text-h6 text-white q-mb-md')
                        ui.label('此部分内容仅用于您个人复盘，不用作公开报告').classes('text-caption text-secondary q-mb-lg')

                        self.summary_date = ui.input(
                            label='总结日期',
                            value=datetime.now().strftime('%Y-%m-%d')
                        ).classes('w-full glass-input')

                        self.summary_well = ui.textarea(
                            label='✅ 做得好的地方'
                        ).classes('w-full glass-input')

                        self.summary_improve = ui.textarea(
                            label='💪 需要改进的地方'
                        ).classes('w-full glass-input')

                        self.summary_learning = ui.textarea(
                            label='💡 新学到的知识/感悟'
                        ).classes('w-full glass-input')

                        self.summary_plan = ui.textarea(
                            label='🎯 下次如何做得更好'
                        ).classes('w-full glass-input')

                        ui.button('保存个人总结', on_click=self.save_personal_summary).classes('glass-btn q-mt-lg')

                    # --- AI分析 ---
                    with ui.tab_panel(tab_ai):
                        ui.label('🤖 AI 智能分析').classes('text-h6 text-white q-mb-md')
                        ui.label('按需分析：选择日期或时间范围，让AI查看并分析您的交流记录').classes('text-caption text-secondary q-mb-lg')

                        with ui.card().classes('glass-card-secondary q-pa-md q-mb-md w-full'):
                            ui.label('📅 单日分析').classes('text-subtitle1 text-white q-mb-sm')
                            ui.label('选择一个日期，AI将分析当天的交流记录').classes('text-caption q-mb-sm')

                            with ui.row().classes('w-full q-gutter-md items-end'):
                                self.ai_single_date = ui.input(
                                    label='选择日期',
                                    value=datetime.now().strftime('%Y-%m-%d')
                                ).classes('col glass-input')
                                ui.button('🔍 分析当日记录', on_click=self.request_ai_analysis_single_date).classes('glass-btn col')

                        with ui.card().classes('glass-card-secondary q-pa-md q-mb-md w-full'):
                            ui.label('📊 区间分析').classes('text-subtitle1 text-white q-mb-sm')
                            ui.label('选择一个日期范围，AI将综合分析这一时期的交流记录').classes('text-caption q-mb-sm')

                            with ui.row().classes('w-full q-gutter-md items-end'):
                                self.ai_start_date = ui.input(
                                    label='开始日期',
                                    value=(datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
                                ).classes('col glass-input')
                                self.ai_end_date = ui.input(
                                    label='结束日期',
                                    value=datetime.now().strftime('%Y-%m-%d')
                                ).classes('col glass-input')
                                ui.button('🔍 分析区间记录', on_click=self.request_ai_analysis_date_range).classes('glass-btn col')

                        self.ai_analysis_result_container = ui.column().classes('w-full q-mt-md')

            # 右侧：历史记录列表
            with ui.column().classes('col-4 q-gutter-md'):
                with ui.card().classes('glass-card q-pa-lg'):
                    ui.label('📋 历史交流记录').classes('text-h6 text-white q-mb-md')
                    ui.label('点击日期可查看/编辑历史记录').classes('text-caption text-secondary q-mb-sm')
                    self.visit_list_container = ui.column().classes('w-full')
                    self.refresh_visit_list()

                with ui.card().classes('glass-card q-pa-lg'):
                    ui.label('🔒 个人总结记录').classes('text-h6 text-white q-mb-md')
                    self.summary_list_container = ui.column().classes('w-full')
                    self.refresh_summary_list()

    def show_date_picker_for_visit(self):
        """显示日期选择器来查看历史记录"""
        with ui.dialog() as dialog, ui.card().classes('glass-card'):
            ui.label('📅 选择日期查看历史记录').classes('text-h6 text-white q-mb-md')

            all_visits = visit_summary_service.list_visits(limit=100)
            unique_dates = sorted(set(v.get('visit_date', '') for v in all_visits if v.get('visit_date')), reverse=True)

            if not unique_dates:
                ui.label('暂无历史记录').classes('text-secondary')
            else:
                ui.label('选择日期：').classes('text-white')
                for date in unique_dates[:30]:
                    date_label = date
                    visit_count = sum(1 for v in all_visits if v.get('visit_date') == date)
                    ui.button(f'📆 {date_label} ({visit_count}条记录)', on_click=lambda d=date: [self.load_visits_by_date(d), dialog.close()]).classes('q-my-xs w-full')

            ui.button('关闭', on_click=dialog.close).classes('q-mt-md')
        dialog.open()

    def load_visits_by_date(self, date: str):
        """加载指定日期的所有交流记录"""
        visits = visit_summary_service.list_visits(limit=100)
        date_visits = [v for v in visits if v.get('visit_date') == date]

        if not date_visits:
            ui.notify('该日期暂无记录', type='info')
            return

        with ui.dialog() as dialog, ui.card().classes('glass-card w-full').style('max-width: 900px; max-height: 80vh; overflow-y: auto'):
            ui.label(f'📅 {date} 交流记录').classes('text-h6 text-white q-mb-md')

            for v in date_visits:
                doctor_name = "未知医生"
                if v.get('doctor_id'):
                    doctor_data = doctor_service.get_doctor(v['doctor_id'])
                    if doctor_data:
                        doctor_name = getattr(doctor_data, 'name', '未知医生')

                with ui.card().classes('glass-card-secondary q-pa-md q-mb-sm w-full'):
                    with ui.row().classes('w-full items-center justify-between'):
                        ui.label(f"👨‍⚕️ {doctor_name}").classes('text-white text-subtitle1')
                        ui.label(f"效果: {'⭐' * v.get('response_effectiveness', 3)}").classes('text-secondary')
                    if v.get('key_topics'):
                        ui.label(f"话题: {v.get('key_topics', '')[:50]}...").classes('text-secondary text-caption')
                    if v.get('ai_summary'):
                        ui.markdown(f"**AI摘要:** {v.get('ai_summary', '')[:100]}...").classes('text-info text-caption')

                    with ui.row().classes('q-mt-sm'):
                        ui.button('✏️ 编辑', on_click=lambda e, xv=v: [self.edit_visit_by_id(xv['visit_id'], date, xv['doctor_id']), dialog.close()]).props('flat size=sm color=primary')
                        ui.button('🗑️ 删除', on_click=lambda e, xv=v: [self.delete_visit_by_id(xv['visit_id']), dialog.close()]).props('flat size=sm color=negative')

            ui.button('关闭', on_click=dialog.close).classes('q-mt-md')
        dialog.open()

    def edit_visit_by_id(self, visit_id: str, date: str, doctor_id: str):
        """根据ID编辑拜访记录"""
        visit = visit_summary_service.get_visit(visit_id)
        if not visit:
            ui.notify('记录不存在', type='warning')
            return

        if doctor_id.startswith('doctor_'):
            self.visit_contact.value = doctor_id
        else:
            self.visit_contact.value = f"doctor_{doctor_id}"

        self.visit_date.value = date
        self.visit_topics.value = visit.key_topics or ''
        self.visit_concerns.value = visit.doctor_concerns or ''
        self.visit_objections.value = visit.objections or ''
        self.visit_responses.value = visit.responses or ''
        self.visit_next_step.value = visit.follow_up_tasks or ''
        self.visit_effectiveness.value = visit.response_effectiveness or 3

        self.current_edit_visit_id = visit_id
        self.visit_save_btn.classes('hidden')
        self.visit_edit_btn.remove_class('hidden')
        self.visit_cancel_edit_btn.remove_class('hidden')

        ui.notify(f'已加载 {date} 的记录，修改后点击"更新记录"保存', type='info')
        ui.run_javascript('window.scrollTo(0, 200)')

    def update_visit(self):
        """更新拜访记录"""
        if not getattr(self, 'current_edit_visit_id', None):
            ui.notify('没有正在编辑的记录', type='warning')
            return

        visit = visit_summary_service.get_visit(self.current_edit_visit_id)
        if not visit:
            ui.notify('记录不存在', type='warning')
            return

        visit_summary_service.update_visit(
            visit_id=self.current_edit_visit_id,
            key_topics=self.visit_topics.value,
            doctor_concerns=self.visit_concerns.value,
            objections=self.visit_objections.value,
            responses=self.visit_responses.value,
            response_effectiveness=int(self.visit_effectiveness.value),
            follow_up_tasks=self.visit_next_step.value
        )

        ui.notify('记录已更新', type='positive')
        self.cancel_edit_visit()
        self.refresh_visit_list()

    def cancel_edit_visit(self):
        """取消编辑"""
        if hasattr(self, 'current_edit_visit_id'):
            delattr(self, 'current_edit_visit_id')
        self.visit_save_btn.remove_class('hidden')
        self.visit_edit_btn.add_class('hidden')
        self.visit_cancel_edit_btn.add_class('hidden')

    def delete_visit_by_id(self, visit_id: str):
        """删除拜访记录"""
        with ui.dialog() as dialog, ui.card().classes('glass-card'):
            ui.label('⚠️ 确认删除').classes('text-h6 text-white')
            ui.label('确定要删除这条交流记录吗？此操作不可恢复。').classes('text-white q-my-md')
            with ui.row().classes('w-full justify-end'):
                ui.button('取消', on_click=dialog.close).classes('glass-btn-secondary')
                ui.button('确认删除', on_click=lambda: [visit_summary_service.delete_visit(visit_id), dialog.close(), self.refresh_visit_list(), ui.notify('记录已删除', type='positive')]).classes('glass-btn')
        dialog.open()

    async def request_ai_analysis_single_date(self):
        """请求单日AI分析"""
        if not ai_integration.is_enabled:
            ui.notify('AI功能未启用，请在设置中配置', type='warning')
            return

        date = self.ai_single_date.value
        if not date:
            ui.notify('请选择日期', type='warning')
            return

        visits = visit_summary_service.get_visits_by_date_range(date, date)
        if not visits:
            ui.notify('该日期暂无交流记录', type='info')
            return

        ui.notify('AI正在分析，请稍候...', type='info')

        visits_text = ""
        for i, v in enumerate(visits, 1):
            doctor_name = "未知医生"
            if v.get('doctor_id'):
                doctor_data = doctor_service.get_doctor(v['doctor_id'])
                if doctor_data:
                    doctor_name = getattr(doctor_data, 'name', '未知医生')

            visits_text += f"""
### 第{i}条拜访记录
- **医生**: {doctor_name}
- **话题**: {v.get('key_topics', '无')}
- **顾虑**: {v.get('doctor_concerns', '无')}
- **异议**: {v.get('objections', '无')}
- **回应**: {v.get('responses', '无')}
- **效果**: {v.get('response_effectiveness', 3)}/5
"""

        prompt = f"""请分析以下日期（{date}）的拜访记录：

{visits_text}

请提供：
1. **整体评价**：这一天拜访的整体表现
2. **关键洞察**：主要发现
3. **改进建议**：可以做得更好的地方
"""

        messages = [
            {"role": "system", "content": "你是一位专业的医药代表教练，帮助分析拜访记录并提供改进建议。"},
            {"role": "user", "content": prompt}
        ]

        result = await ai_integration._make_request(messages, temperature=0.7, max_tokens=2000)

        self.ai_analysis_result_container.clear()
        with self.ai_analysis_result_container:
            if result:
                with ui.card().classes('glass-card q-pa-md w-full'):
                    ui.label(f'📊 {date} AI分析结果').classes('text-subtitle1 text-white q-mb-sm')
                    ui.markdown(result)
            else:
                ui.label('分析失败，请稍后重试').classes('text-negative')

    async def request_ai_analysis_date_range(self):
        """请求日期范围AI分析"""
        if not ai_integration.is_enabled:
            ui.notify('AI功能未启用，请在设置中配置', type='warning')
            return

        start_date = self.ai_start_date.value
        end_date = self.ai_end_date.value
        if not start_date or not end_date:
            ui.notify('请选择开始和结束日期', type='warning')
            return

        visits = visit_summary_service.get_visits_by_date_range(start_date, end_date)
        if not visits:
            ui.notify(f'{start_date} 至 {end_date} 期间暂无交流记录', type='info')
            return

        ui.notify('AI正在综合分析，请稍候...', type='info')

        result = await visit_summary_service.get_ai_analysis_for_date_range(start_date, end_date)

        self.ai_analysis_result_container.clear()
        with self.ai_analysis_result_container:
            if result:
                with ui.card().classes('glass-card q-pa-md w-full'):
                    ui.label(f'📊 {start_date} 至 {end_date} AI综合分析').classes('text-subtitle1 text-white q-mb-sm')
                    ui.markdown(result)
            else:
                ui.label('分析失败，请稍后重试').classes('text-negative')
    
    # ==================== 数据中心和医院管理页面 ====================
    
    def render_data_relationship_view(self):
        """渲染数据关联视图 - 展示医院、科室、医生、产品的关联关系"""
        with ui.row().classes('w-full items-center justify-between mb-4'):
            ui.label('📊 数据关联视图').classes('text-h6 text-white')
            ui.button('🔄 刷新', on_click=lambda: self.navigate('hospitals')).props('flat color=primary')
        
        ui.label('查看医院、科室、医生、产品之间的关联关系。修改任何名称时，所有关联数据会自动同步更新。').classes('text-caption text-grey mb-4')
        
        # 获取所有数据
        hospitals = hospital_service.list_hospitals()
        departments = hospital_service.list_departments()
        products = hospital_service.list_products()
        doctors = doctor_service.list_doctors()
        
        # 获取产品关联
        from modules.product_association.service import ProductAssociationService
        assoc_service = ProductAssociationService()
        associations = assoc_service.filter_associations()
        
        if not hospitals:
            with ui.card().classes('glass-card p-6 text-center'):
                ui.label('暂无数据').classes('text-h6 text-white mb-2')
                ui.label('请先添加医院、科室、产品等基础数据').classes('text-caption text-grey')
            return
        
        # 按医院展示关联关系
        for hospital in hospitals:
            hospital_id = hospital['hospital_id']
            hospital_name = hospital['name']
            
            # 获取该医院的科室
            hospital_depts = [d for d in departments if d.get('department_id') in hospital.get('departments', [])]
            
            # 获取该医院的医生
            hospital_doctors = [d for d in doctors if d.get('hospital_id') == hospital_id]
            
            # 获取该医院的产品关联
            hospital_assocs = [a for a in associations if a.hospital_id == hospital_id]
            
            with ui.expansion(hospital_name, icon='business').classes('glass-card w-full mb-3').props('default-opened'):
                with ui.column().classes('w-full gap-3 p-3'):
                    # 统计信息
                    with ui.row().classes('w-full gap-4 mb-3'):
                        with ui.card().classes('glass-card-secondary p-3 flex-1'):
                            ui.label(f'{len(hospital_depts)}').classes('text-2xl font-bold text-cyan-4')
                            ui.label('科室').classes('text-caption text-grey')
                        with ui.card().classes('glass-card-secondary p-3 flex-1'):
                            ui.label(f'{len(hospital_doctors)}').classes('text-2xl font-bold text-orange-4')
                            ui.label('医生').classes('text-caption text-grey')
                        with ui.card().classes('glass-card-secondary p-3 flex-1'):
                            ui.label(f'{len(hospital_assocs)}').classes('text-2xl font-bold text-green-4')
                            ui.label('产品关联').classes('text-caption text-grey')
                    
                    # 科室列表
                    if hospital_depts:
                        ui.label('📂 科室').classes('text-subtitle2 text-white mb-2')
                        with ui.grid().classes('w-full gap-2 grid-cols-1 md:grid-cols-3 mb-3'):
                            for dept in hospital_depts:
                                dept_id = dept['department_id']
                                dept_name = dept['name']
                                
                                # 该科室的医生
                                dept_doctors = [d for d in hospital_doctors if d.get('department_id') == dept_id]
                                # 该科室的产品关联
                                dept_assocs = [a for a in hospital_assocs if a.department_id == dept_id]
                                
                                with ui.card().classes('glass-card-secondary p-3'):
                                    ui.label(dept_name).classes('text-white font-bold mb-2')
                                    with ui.row().classes('gap-2 items-center'):
                                        ui.label(f'👨‍⚕️ {len(dept_doctors)}人').classes('text-caption text-orange-4')
                                        ui.label(f'💊 {len(dept_assocs)}个产品').classes('text-caption text-green-4')
                    
                    # 医生列表
                    if hospital_doctors:
                        ui.label('👨‍⚕️ 医生').classes('text-subtitle2 text-white mb-2')
                        with ui.grid().classes('w-full gap-2 grid-cols-1 md:grid-cols-4 mb-3'):
                            for doctor in hospital_doctors[:8]:  # 只显示前8个
                                with ui.card().classes('glass-card-secondary p-2'):
                                    ui.label(doctor['name']).classes('text-white text-sm')
                                    ui.label(doctor.get('department', '')).classes('text-caption text-grey')
                        if len(hospital_doctors) > 8:
                            ui.label(f'还有 {len(hospital_doctors) - 8} 位医生...').classes('text-caption text-grey')
                    
                    # 产品关联
                    if hospital_assocs:
                        ui.label('💊 产品关联').classes('text-subtitle2 text-white mb-2')
                        with ui.grid().classes('w-full gap-2 grid-cols-1 md:grid-cols-3'):
                            for assoc in hospital_assocs[:6]:  # 只显示前6个
                                with ui.card().classes('glass-card-secondary p-2'):
                                    ui.label(assoc.product_name).classes('text-white text-sm')
                                    ui.label(f"{assoc.department_name}").classes('text-caption text-grey')
                        if len(hospital_assocs) > 6:
                            ui.label(f'还有 {len(hospital_assocs) - 6} 个产品关联...').classes('text-caption text-grey')
        
        # 提示信息
        with ui.card().classes('glass-card p-4 mt-4'):
            ui.label('💡 数据同步说明').classes('text-subtitle2 text-white mb-2')
            ui.label('• 修改医院名称时，会自动同步到该医院的所有医生、科室、产品关联').classes('text-caption text-grey')
            ui.label('• 修改科室名称时，会自动同步到该科室的所有医生、产品关联').classes('text-caption text-grey')
            ui.label('• 修改产品名称时，会自动同步到所有产品关联和知识库').classes('text-caption text-grey')
            ui.label('• 修改医生名称时，会自动同步到所有拜访记录和准备计划').classes('text-caption text-grey')
            ui.label('• 添加新的产品关联后，点击右上角"🔄 刷新"按钮查看最新数据').classes('text-caption text-green-4 mt-2')
    
    def render_doctors_in_hospital(self):
        """在医院管理中渲染医生列表"""
        ui.label('👨‍⚕️ 医生档案').classes('text-h6 text-white mb-4')
        
        # 添加医生按钮
        with ui.row().classes('w-full justify-end mb-4'):
            ui.button('➕ 添加医生', on_click=self.show_add_doctor_dialog).props('color=primary')
        
        # 医生列表
        doctors = doctor_service.list_doctors()
        
        if not doctors:
            with ui.card().classes('glass-card p-6 text-center'):
                ui.label('暂无医生').classes('text-h6 text-white mb-2')
                ui.label('点击上方按钮添加医生档案').classes('text-caption text-grey')
            return
        
        # 按医院分组显示
        hospitals = hospital_service.list_hospitals()
        hospital_dict = {h['hospital_id']: h['name'] for h in hospitals}
        
        # 分组
        grouped_doctors = {}
        for doctor in doctors:
            hospital_id = doctor.get('hospital_id', '')
            hospital_name = hospital_dict.get(hospital_id, '未分配医院')
            if hospital_name not in grouped_doctors:
                grouped_doctors[hospital_name] = []
            grouped_doctors[hospital_name].append(doctor)
        
        # 显示
        for hospital_name, hospital_doctors in grouped_doctors.items():
            with ui.expansion(f'{hospital_name} ({len(hospital_doctors)}人)', icon='business').classes('glass-card w-full mb-3'):
                with ui.grid().classes('w-full gap-3 grid-cols-1 md:grid-cols-3 p-3'):
                    for doctor in hospital_doctors:
                        with ui.card().classes('glass-card-secondary p-4'):
                            ui.label(doctor['name']).classes('text-white font-bold text-lg mb-2')
                            
                            with ui.column().classes('gap-1 mb-3'):
                                if doctor.get('title'):
                                    ui.label(f"🎓 {doctor['title']}").classes('text-caption text-blue-4')
                                if doctor.get('department'):
                                    ui.label(f"🏨 {doctor['department']}").classes('text-caption text-cyan-4')
                                if doctor.get('relationship_stage'):
                                    ui.label(f"🤝 {doctor['relationship_stage']}").classes('text-caption text-green-4')
                            
                            with ui.row().classes('gap-2'):
                                ui.button('查看', on_click=lambda d=doctor: self.view_doctor(d)).props('flat dense size=sm color=primary')
                                ui.button('编辑', on_click=lambda d=doctor: self.show_edit_doctor_dialog(d)).props('flat dense size=sm color=secondary')
                                ui.button('删除', on_click=lambda d=doctor: self.delete_doctor(d['doctor_id'])).props('flat dense size=sm color=negative')
    
    def show_add_doctor_dialog(self):
        """显示添加医生对话框"""
        with ui.dialog() as dialog, ui.card().classes('w-full max-w-2xl'):
            ui.label('添加医生').classes('text-h6 mb-4')
            
            with ui.column().classes('w-full gap-3'):
                doc_name = ui.input(label='姓名*', placeholder='请输入医生姓名').classes('w-full')
                
                # 医院选择
                hospitals = hospital_service.list_hospitals()
                hospital_options = {'': '未分配'}
                hospital_options.update({h['hospital_id']: h['name'] for h in hospitals})
                
                doc_hospital_id = ui.select(
                    label='所属医院',
                    options=hospital_options,
                    value=''
                ).classes('w-full')
                
                # 科室选择
                doc_department_id = ui.select(
                    label='所属科室',
                    options={'': '未分配'},
                    value=''
                ).classes('w-full')
                
                # 当医院改变时更新科室选项
                def update_departments():
                    if doc_hospital_id.value:
                        hospital = hospital_service.get_hospital(doc_hospital_id.value)
                        if hospital:
                            dept_options = {'': '未分配'}
                            for dept_id in hospital.departments:
                                dept = hospital_service.get_department(dept_id)
                                if dept:
                                    dept_options[dept_id] = dept.name
                            doc_department_id.set_options(dept_options)
                    else:
                        doc_department_id.set_options({'': '未分配'})
                
                doc_hospital_id.on_value_change(lambda: update_departments())
                
                doc_title = ui.input(label='职称', placeholder='如：主任医师').classes('w-full')
                doc_interests = ui.input(label='兴趣领域', placeholder='用逗号分隔，如：心血管,高血压').classes('w-full')
                doc_style = ui.select(
                    label='决策风格',
                    options=['', '循证型', '经验型', '保守型', '创新型', '关系型'],
                    value=''
                ).classes('w-full')
                doc_stage = ui.select(
                    label='关系阶段',
                    options=['初识', '建立中', '稳定', '深入'],
                    value='初识'
                ).classes('w-full')
                doc_needs = ui.textarea(label='未满足需求').classes('w-full')
                doc_notes = ui.textarea(label='备注').classes('w-full')
            
            with ui.row().classes('w-full justify-end gap-2 mt-4'):
                ui.button('取消', on_click=dialog.close).props('flat')
                ui.button('保存', on_click=lambda: self.save_new_doctor(
                    dialog, doc_name, doc_hospital_id, doc_department_id,
                    doc_title, doc_interests, doc_style, doc_stage, doc_needs, doc_notes
                )).props('color=primary')
        
        dialog.open()
    
    def save_new_doctor(self, dialog, doc_name, doc_hospital_id, doc_department_id,
                        doc_title, doc_interests, doc_style, doc_stage, doc_needs, doc_notes):
        """保存新医生"""
        if not doc_name.value:
            ui.notify('请输入医生姓名', type='warning')
            return
        
        # 获取医院和科室名称
        hospital_name = ''
        department_name = ''
        
        if doc_hospital_id.value:
            hospital = hospital_service.get_hospital(doc_hospital_id.value)
            if hospital:
                hospital_name = hospital.name
        
        if doc_department_id.value:
            department = hospital_service.get_department(doc_department_id.value)
            if department:
                department_name = department.name
        
        interests = [i.strip() for i in doc_interests.value.split(',') if i.strip()]
        
        doctor_service.create_doctor(
            name=doc_name.value,
            hospital=hospital_name,
            hospital_id=doc_hospital_id.value,
            department=department_name,
            department_id=doc_department_id.value,
            title=doc_title.value,
            interests=interests,
            decision_style=doc_style.value if doc_style.value else None,
            relationship_stage=doc_stage.value,
            unmet_needs=doc_needs.value,
            notes=doc_notes.value
        )
        
        ui.notify('医生已添加', type='positive')
        dialog.close()
        self.navigate('hospitals')  # 刷新页面
    
    def show_edit_doctor_dialog(self, doctor):
        """显示编辑医生对话框"""
        with ui.dialog() as dialog, ui.card().classes('w-full max-w-2xl'):
            ui.label(f'编辑医生 - {doctor["name"]}').classes('text-h6 mb-4')
            
            with ui.column().classes('w-full gap-3'):
                doc_name = ui.input(label='姓名*', value=doctor.get('name', '')).classes('w-full')
                
                # 医院选择
                hospitals = hospital_service.list_hospitals()
                hospital_options = {'': '未分配'}
                hospital_options.update({h['hospital_id']: h['name'] for h in hospitals})
                
                current_hospital_id = doctor.get('hospital_id', '')
                doc_hospital_id = ui.select(
                    label='所属医院',
                    options=hospital_options,
                    value=current_hospital_id
                ).classes('w-full')
                
                # 科室选择
                current_department_id = doctor.get('department_id', '')
                doc_department_id = ui.select(
                    label='所属科室',
                    options={'': '未分配'},
                    value=current_department_id
                ).classes('w-full')
                
                # 初始化科室选项
                def init_departments():
                    if doc_hospital_id.value:
                        hospital = hospital_service.get_hospital(doc_hospital_id.value)
                        if hospital:
                            dept_options = {'': '未分配'}
                            for dept_id in hospital.departments:
                                dept = hospital_service.get_department(dept_id)
                                if dept:
                                    dept_options[dept_id] = dept.name
                            doc_department_id.set_options(dept_options)
                            doc_department_id.value = current_department_id
                    else:
                        doc_department_id.set_options({'': '未分配'})
                
                init_departments()
                
                # 当医院改变时更新科室选项
                def update_departments():
                    if doc_hospital_id.value:
                        hospital = hospital_service.get_hospital(doc_hospital_id.value)
                        if hospital:
                            dept_options = {'': '未分配'}
                            for dept_id in hospital.departments:
                                dept = hospital_service.get_department(dept_id)
                                if dept:
                                    dept_options[dept_id] = dept.name
                            doc_department_id.set_options(dept_options)
                            doc_department_id.value = ''
                    else:
                        doc_department_id.set_options({'': '未分配'})
                        doc_department_id.value = ''
                
                doc_hospital_id.on_value_change(lambda: update_departments())
                
                doc_title = ui.input(label='职称', value=doctor.get('title', '')).classes('w-full')
                interests_str = ', '.join(doctor.get('interests', []))
                doc_interests = ui.input(label='兴趣领域', value=interests_str).classes('w-full')
                doc_style = ui.select(
                    label='决策风格',
                    options=['', '循证型', '经验型', '保守型', '创新型', '关系型'],
                    value=doctor.get('decision_style', '')
                ).classes('w-full')
                doc_stage = ui.select(
                    label='关系阶段',
                    options=['初识', '建立中', '稳定', '深入'],
                    value=doctor.get('relationship_stage', '初识')
                ).classes('w-full')
                doc_needs = ui.textarea(label='未满足需求', value=doctor.get('unmet_needs', '')).classes('w-full')
                doc_notes = ui.textarea(label='备注', value=doctor.get('notes', '')).classes('w-full')
            
            with ui.row().classes('w-full justify-end gap-2 mt-4'):
                ui.button('取消', on_click=dialog.close).props('flat')
                ui.button('保存', on_click=lambda: self.save_edit_doctor(
                    dialog, doctor['doctor_id'], doc_name, doc_hospital_id, doc_department_id,
                    doc_title, doc_interests, doc_style, doc_stage, doc_needs, doc_notes
                )).props('color=primary')
        
        dialog.open()
    
    def save_edit_doctor(self, dialog, doctor_id, doc_name, doc_hospital_id, doc_department_id,
                         doc_title, doc_interests, doc_style, doc_stage, doc_needs, doc_notes):
        """保存编辑的医生"""
        if not doc_name.value:
            ui.notify('请输入医生姓名', type='warning')
            return
        
        # 获取医院和科室名称
        hospital_name = ''
        department_name = ''
        
        if doc_hospital_id.value:
            hospital = hospital_service.get_hospital(doc_hospital_id.value)
            if hospital:
                hospital_name = hospital.name
        
        if doc_department_id.value:
            department = hospital_service.get_department(doc_department_id.value)
            if department:
                department_name = department.name
        
        interests = [i.strip() for i in doc_interests.value.split(',') if i.strip()]
        
        updates = {
            'name': doc_name.value,
            'hospital': hospital_name,
            'hospital_id': doc_hospital_id.value,
            'department': department_name,
            'department_id': doc_department_id.value,
            'title': doc_title.value,
            'interests': interests,
            'decision_style': doc_style.value if doc_style.value else None,
            'relationship_stage': doc_stage.value,
            'unmet_needs': doc_needs.value,
            'notes': doc_notes.value
        }
        
        doctor_service.update_doctor(doctor_id, updates)
        
        ui.notify('医生信息已更新', type='positive')
        dialog.close()
        self.navigate('hospitals')  # 刷新页面
    
    def render_contacts_in_hospital(self):
        """在医院管理中渲染联系人列表"""
        ui.label('👥 联系人').classes('text-h6 text-white mb-4')
        
        # 添加联系人按钮
        with ui.row().classes('w-full justify-end mb-4'):
            ui.button('➕ 添加联系人', on_click=self.add_contact).props('color=primary')
        
        # 联系人列表
        from modules.contact_manager.service import contact_service
        contacts = contact_service.list_contacts()
        
        if not contacts:
            with ui.card().classes('glass-card p-6 text-center'):
                ui.label('暂无联系人').classes('text-h6 text-white mb-2')
                ui.label('点击上方按钮添加联系人').classes('text-caption text-grey')
            return
        
        # 按类型分组
        grouped_contacts = {}
        for contact in contacts:
            contact_type = contact.get('contact_type', '其他')
            if contact_type not in grouped_contacts:
                grouped_contacts[contact_type] = []
            grouped_contacts[contact_type].append(contact)
        
        # 显示
        for contact_type, type_contacts in grouped_contacts.items():
            type_icons = {
                '医生': '👨‍⚕️',
                '护士': '👩‍⚕️',
                '药剂师': '💊',
                '行政人员': '📋',
                '同事': '👔',
                '其他': '👤'
            }
            icon = type_icons.get(contact_type, '👤')
            
            with ui.expansion(f'{icon} {contact_type} ({len(type_contacts)}人)', icon='person').classes('glass-card w-full mb-3'):
                with ui.grid().classes('w-full gap-3 grid-cols-1 md:grid-cols-3 p-3'):
                    for contact in type_contacts:
                        with ui.card().classes('glass-card-secondary p-4'):
                            ui.label(contact['name']).classes('text-white font-bold text-lg mb-2')
                            
                            with ui.column().classes('gap-1 mb-3'):
                                if contact.get('organization'):
                                    ui.label(f"🏢 {contact['organization']}").classes('text-caption text-blue-4')
                                if contact.get('phone'):
                                    ui.label(f"📱 {contact['phone']}").classes('text-caption text-cyan-4')
                                if contact.get('email'):
                                    ui.label(f"📧 {contact['email']}").classes('text-caption text-green-4')
                            
                            with ui.row().classes('gap-2'):
                                ui.button('编辑', on_click=lambda c=contact: self.edit_contact(c)).props('flat dense size=sm color=secondary')
                                ui.button('删除', on_click=lambda c=contact: self.delete_contact(c['contact_id'])).props('flat dense size=sm color=negative')
    
    def render_data_center(self):
        """渲染数据中心页面"""
        with ui.row().classes('w-full items-center justify-between mb-4'):
            ui.label('🗄️ 数据中心').classes('page-title')
            ui.button('🔄 刷新', on_click=lambda: ui.navigate.to('/data_center')).props('flat color=primary')

        # 数据统计概览 - 卡片网格布局
        summary = data_center_service.get_all_data_summary()

        stat_labels = {
            'hospitals': ('🏥', '医院', 'blue'),
            'departments': ('🏨', '科室', 'cyan'),
            'products': ('💊', '产品', 'green'),
            'competitors': ('⚔️', '竞品', 'orange'),
            'doctors': ('👨‍⚕️', '医生', 'indigo'),
            'contacts': ('👥', '联系人', 'purple'),
            'visits': ('📝', '拜访记录', 'teal'),
            'interactions': ('💬', '交流记录', 'pink'),
            'knowledge_items': ('📚', '知识条目', 'amber'),
            'reflections': ('💭', '个人反思', 'red')
        }

        with ui.grid().classes('w-full gap-3 grid-cols-2 md:grid-cols-5'):
            for key, count in summary.items():
                icon, label, color = stat_labels.get(key, ('📊', key, 'grey'))
                with ui.card().classes(f'glass-card p-3 text-center'):
                    ui.label(str(count)).classes(f'text-2xl font-bold text-{color}-4')
                    ui.label(f'{icon} {label}').classes('text-caption text-grey')

        # 全局搜索
        # 全局搜索
        with ui.card().classes('glass-card w-full p-4 mb-4'):
            ui.label('🔍 全局搜索').classes('text-subtitle1 font-bold text-white mb-3')

            with ui.row().classes('w-full gap-3 items-end'):
                self.search_input = ui.input(
                    label='输入关键字',
                    placeholder='医生姓名、医院、产品...'
                ).classes('flex-grow glass-input')

                ui.button('搜索', on_click=self.perform_global_search).props('color=primary')

            # 搜索结果容器
            self.search_results_container = ui.column().classes('w-full mt-4')

        # 数据分类浏览
        with ui.card().classes('glass-card w-full p-4'):
            ui.label('📂 数据分类').classes('text-subtitle1 font-bold text-white mb-3')

            with ui.tabs().classes('w-full text-white glass-tabs') as tabs:
                tab_hospitals = ui.tab('🏥 医院')
                tab_products = ui.tab('💊 产品')
                tab_competitors = ui.tab('⚔️ 竞品')
                tab_doctors = ui.tab('👨‍⚕️ 医生')
                tab_contacts = ui.tab('👥 联系人')
                tab_knowledge = ui.tab('📚 知识')

            with ui.tab_panels(tabs, value=tab_hospitals).classes('w-full bg-transparent'):
                with ui.tab_panel(tab_hospitals):
                    self.render_data_table('hospitals')
                with ui.tab_panel(tab_products):
                    self.render_data_table('products')
                with ui.tab_panel(tab_competitors):
                    self.render_data_table('competitors')
                with ui.tab_panel(tab_doctors):
                    self.render_data_table('doctors')
                with ui.tab_panel(tab_contacts):
                    self.render_data_table('contacts')
                with ui.tab_panel(tab_knowledge):
                    self.render_data_table('knowledge')
    
    def perform_global_search(self):
        """执行全局搜索"""
        if not hasattr(self, 'search_input') or not self.search_input.value:
            ui.notify('请输入搜索关键字', type='warning')
            return
        
        keyword = self.search_input.value
        results = data_center_service.global_search(keyword)

        self.search_results_container.clear()
        with self.search_results_container:
            total = results.get('total_count', 0)
            ui.label(f'找到 {total} 条结果').classes('text-h6 text-white q-mb-md')

            if total == 0:
                ui.label('未找到匹配的数据').classes('text-secondary')
                return

            # 显示各类别结果
            for category, items in results.items():
                if category == 'total_count' or not items:
                    continue

                category_labels = {
                    'hospitals': '医院',
                    'products': '产品',
                    'competitors': '竞品',
                    'doctors': '医生',
                    'contacts': '联系人',
                    'knowledge': '知识库'
                }

                with ui.expansion(f'{category_labels.get(category, category)} ({len(items)})').classes('w-full glass-expansion'):
                    # 使用网格布局显示搜索结果
                    with ui.grid().classes('w-full gap-3'):
                        for item in items[:10]:  # 每类最多显示10条
                            with ui.card().classes('glass-card-secondary p-3'):
                                name = item.get('name') or item.get('title', '未命名')
                                ui.label(name).classes('text-white font-bold text-body1')

                                # 显示次要信息
                                if category == 'doctors':
                                    hospital = item.get('hospital', '')
                                    dept = item.get('department', '')
                                    if hospital or dept:
                                        ui.label(f"{hospital} {dept}").classes('text-caption text-grey')
                                    stage = item.get('relationship_stage', '')
                                    if stage:
                                        ui.label(f"关系: {stage}").classes('text-caption text-blue-4')
                                elif category == 'hospitals':
                                    level = item.get('level', '')
                                    if level:
                                        ui.label(level).classes('text-caption text-grey')
                                elif category == 'products':
                                    cat = item.get('category', '')
                                    if cat:
                                        ui.label(cat).classes('text-caption text-grey')
                                elif category == 'contacts':
                                    org = item.get('organization', '')
                                    ctype = item.get('contact_type', '')
                                    if org or ctype:
                                        ui.label(f"{ctype} | {org}").classes('text-caption text-grey')

                                ui.button('查看', on_click=lambda e, i=item, c=category: self.view_data_detail(c, i)).props('flat dense size=sm color=primary').classes('mt-2')
    
    def render_data_table(self, category: str):
        """渲染数据表格"""
        data = data_center_service.get_data_by_category(category)

        if not data:
            ui.label(f'暂无{category}数据').classes('text-secondary')
            return

        # 判断是否使用网格布局（数据多时）
        use_grid = len(data) > 6 and category in ['doctors', 'contacts']

        if use_grid:
            # 网格布局 - 卡片式显示
            cols = 3 if len(data) > 12 else 2
            with ui.grid().classes(f'w-full gap-4 grid-cols-{cols}'):
                for item in data[:50]:
                    with ui.card().classes('glass-card-secondary p-4'):
                        name = item.get('name') or item.get('title', '未命名')
                        ui.label(name).classes('text-white font-bold text-body1')

                        if category == 'doctors':
                            hospital = item.get('hospital', '')
                            dept = item.get('department', '')
                            if hospital or dept:
                                ui.label(f"{hospital} - {dept}").classes('text-caption text-grey')
                            stage = item.get('relationship_stage', '')
                            if stage:
                                ui.label(f"关系阶段: {stage}").classes('text-caption text-blue-4')
                            title = item.get('title', '')
                            if title:
                                ui.label(title).classes('text-caption')
                        elif category == 'contacts':
                            org = item.get('organization', '')
                            ctype = item.get('contact_type', '')
                            if org or ctype:
                                ui.label(f"{ctype} | {org}").classes('text-caption text-grey')
                        elif category == 'hospitals':
                            level = item.get('level', '')
                            address = item.get('address', '')
                            with ui.column().classes('gap-1'):
                                if level:
                                    ui.label(f'📋 {level}').classes('text-caption text-blue-4')
                                if address:
                                    ui.label(f'📍 {address}').classes('text-caption text-grey')
                        elif category == 'products':
                            cat = item.get('category', '未分类')
                            desc = item.get('description', '')
                            with ui.column().classes('gap-1'):
                                ui.label(f'🏷️ {cat}').classes('text-caption text-green-4')
                                if desc:
                                    desc_short = desc[:40] + '...' if len(desc) > 40 else desc
                                    ui.label(desc_short).classes('text-caption text-grey')

                        with ui.row().classes('gap-2 mt-3'):
                            ui.button('查看', on_click=lambda e, i=item, c=category: self.view_data_detail(c, i)).props('flat dense size=sm color=primary')
                            ui.button('编辑', on_click=lambda e, i=item, c=category: self.edit_data(c, i)).props('flat dense size=sm color=secondary')
                            ui.button('删除', on_click=lambda e, i=item, c=category: self.delete_data_confirm(c, i)).props('flat dense size=sm color=negative')
        else:
            # 列表布局 - 原有的垂直显示方式
            for item in data[:50]:
                with ui.element('div').classes('glass-list-item'):
                    with ui.row().classes('w-full items-center justify-between'):
                        with ui.column().classes('col-grow'):
                            name = item.get('name') or item.get('title', '未命名')
                            ui.label(name).classes('text-white font-bold')

                            if category == 'hospitals':
                                ui.label(f"{item.get('level', '')} | {item.get('address', '')}").classes('text-caption text-secondary')
                            elif category == 'products':
                                cat = item.get('category', '未分类')
                                ui.label(cat).classes('text-caption text-secondary')
                            elif category == 'competitors':
                                ui.label(f"厂家：{item.get('manufacturer', '')}").classes('text-caption text-secondary')
                            elif category == 'doctors':
                                ui.label(f"{item.get('hospital', '')} - {item.get('department', '')}").classes('text-caption text-secondary')
                            elif category == 'contacts':
                                ui.label(f"{item.get('contact_type', '')} | {item.get('organization', '')}").classes('text-caption text-secondary')
                            elif category == 'knowledge':
                                ui.label(f"{item.get('category', '')}").classes('text-caption text-secondary')

                        with ui.row().classes('q-gutter-sm'):
                            ui.button('查看', on_click=lambda i=item, c=category: self.view_data_detail(c, i)).props('flat dense size=sm color=primary')
                            ui.button('编辑', on_click=lambda i=item, c=category: self.edit_data(c, i)).props('flat dense size=sm color=secondary')
                            ui.button('删除', on_click=lambda i=item, c=category: self.delete_data_confirm(c, i)).props('flat dense size=sm color=negative')
    
    def view_data_detail(self, category: str, item: dict):
        """查看数据详情"""
        with ui.dialog() as dialog, ui.card().classes('glass-card w-full').style('max-width: 700px; max-height: 80vh; overflow-y: auto'):
            name = item.get('name') or item.get('title', '数据详情')
            ui.label(name).classes('text-h6 text-white q-mb-md')
            
            # 根据不同类型显示友好的格式
            if category == 'products':
                # 产品详情
                with ui.column().classes('w-full q-gutter-sm'):
                    if item.get('name'):
                        ui.label(f"产品名称：{item['name']}").classes('text-white')
                    if item.get('category'):
                        ui.label(f"分类：{item['category']}").classes('text-grey')
                    if item.get('description'):
                        ui.separator()
                        ui.label("产品描述：").classes('text-white font-bold')
                        ui.label(item['description']).classes('text-grey')
                    if item.get('indications'):
                        ui.separator()
                        ui.label("适应症：").classes('text-white font-bold')
                        for indication in item['indications']:
                            ui.label(f"• {indication}").classes('text-grey')
                    if item.get('key_features'):
                        ui.separator()
                        ui.label("关键特性：").classes('text-white font-bold')
                        for feature in item['key_features']:
                            ui.label(f"• {feature}").classes('text-grey')
                    if item.get('notes'):
                        ui.separator()
                        ui.label("备注：").classes('text-white font-bold')
                        ui.label(item['notes']).classes('text-grey')
                    
                    ui.separator()
                    ui.label(f"创建时间：{item.get('created_at', '')}").classes('text-caption text-grey')
                    ui.label(f"更新时间：{item.get('updated_at', '')}").classes('text-caption text-grey')
            
            elif category == 'hospitals':
                # 医院详情
                with ui.column().classes('w-full q-gutter-sm'):
                    if item.get('name'):
                        ui.label(f"医院名称：{item['name']}").classes('text-white')
                    if item.get('level'):
                        ui.label(f"医院等级：{item['level']}").classes('text-grey')
                    if item.get('address'):
                        ui.label(f"地址：{item['address']}").classes('text-grey')
                    if item.get('notes'):
                        ui.separator()
                        ui.label("备注：").classes('text-white font-bold')
                        ui.label(item['notes']).classes('text-grey')
            
            elif category == 'doctors':
                # 医生详情
                with ui.column().classes('w-full q-gutter-sm'):
                    if item.get('name'):
                        ui.label(f"姓名：{item['name']}").classes('text-white')
                    if item.get('hospital'):
                        ui.label(f"医院：{item['hospital']}").classes('text-grey')
                    if item.get('department'):
                        ui.label(f"科室：{item['department']}").classes('text-grey')
                    if item.get('title'):
                        ui.label(f"职称：{item['title']}").classes('text-grey')
                    if item.get('interests'):
                        ui.separator()
                        ui.label("学术兴趣：").classes('text-white font-bold')
                        for interest in item['interests']:
                            ui.label(f"• {interest}").classes('text-grey')
                    if item.get('notes'):
                        ui.separator()
                        ui.label("备注：").classes('text-white font-bold')
                        ui.label(item['notes']).classes('text-grey')
            
            elif category == 'competitors':
                # 竞品详情
                with ui.column().classes('w-full q-gutter-sm'):
                    if item.get('name'):
                        ui.label(f"竞品名称：{item['name']}").classes('text-white')
                    if item.get('manufacturer'):
                        ui.label(f"生产厂家：{item['manufacturer']}").classes('text-grey')
                    if item.get('description'):
                        ui.separator()
                        ui.label("产品描述：").classes('text-white font-bold')
                        ui.label(item['description']).classes('text-grey')
                    if item.get('advantages'):
                        ui.separator()
                        ui.label("优势：").classes('text-white font-bold')
                        for adv in item['advantages']:
                            ui.label(f"• {adv}").classes('text-grey')
                    if item.get('disadvantages'):
                        ui.separator()
                        ui.label("劣势：").classes('text-white font-bold')
                        for dis in item['disadvantages']:
                            ui.label(f"• {dis}").classes('text-grey')
            
            elif category == 'contacts':
                # 联系人详情
                with ui.column().classes('w-full q-gutter-sm'):
                    if item.get('name'):
                        ui.label(f"姓名：{item['name']}").classes('text-white')
                    if item.get('contact_type'):
                        ui.label(f"类型：{item['contact_type']}").classes('text-grey')
                    if item.get('organization'):
                        ui.label(f"单位：{item['organization']}").classes('text-grey')
                    if item.get('position'):
                        ui.label(f"职位：{item['position']}").classes('text-grey')
                    if item.get('phone'):
                        ui.label(f"电话：{item['phone']}").classes('text-grey')
                    if item.get('email'):
                        ui.label(f"邮箱：{item['email']}").classes('text-grey')
                    if item.get('notes'):
                        ui.separator()
                        ui.label("备注：").classes('text-white font-bold')
                        ui.label(item['notes']).classes('text-grey')
            
            elif category == 'knowledge':
                # 知识库详情
                with ui.column().classes('w-full q-gutter-sm'):
                    if item.get('title'):
                        ui.label(f"标题：{item['title']}").classes('text-white')
                    if item.get('category'):
                        ui.label(f"分类：{item['category']}").classes('text-grey')
                    if item.get('content'):
                        ui.separator()
                        ui.label("内容：").classes('text-white font-bold')
                        ui.label(item['content']).classes('text-grey')
                    if item.get('tags'):
                        ui.separator()
                        ui.label("标签：").classes('text-white font-bold')
                        ui.label(', '.join(item['tags'])).classes('text-grey')
            
            else:
                # 其他类型，显示JSON格式
                import json
                content = json.dumps(item, ensure_ascii=False, indent=2)
                ui.code(content, language='json').classes('w-full')
            
            with ui.row().classes('w-full justify-end q-mt-md'):
                ui.button('关闭', on_click=dialog.close).classes('glass-btn')
        dialog.open()
    
    def edit_data(self, category: str, item: dict):
        """编辑数据 - 跳转到对应的编辑页面"""
        if category == 'hospitals':
            self.navigate('hospitals')
        elif category == 'doctors':
            self.navigate('doctors')
        elif category == 'contacts':
            self.navigate('contacts')
        ui.notify(f'请在{category}管理页面进行编辑', type='info')
    
    def delete_data_confirm(self, category: str, item: dict):
        """确认删除数据"""
        with ui.dialog() as dialog, ui.card().classes('glass-card'):
            ui.label('确认删除').classes('text-h6 text-white q-mb-md')
            name = item.get('name') or item.get('title', '此项')
            ui.label(f'确定要删除 "{name}" 吗？').classes('text-white')
            ui.label('此操作不可恢复！').classes('text-negative q-mt-sm')
            
            with ui.row().classes('w-full justify-end q-mt-lg q-gutter-sm'):
                ui.button('取消', on_click=dialog.close).classes('glass-btn')
                ui.button('确认删除', on_click=lambda: self.delete_data_execute(category, item, dialog)).props('color=negative')
        dialog.open()
    
    def delete_data_execute(self, category: str, item: dict, dialog):
        """执行删除数据"""
        # 获取ID
        item_id = item.get('hospital_id') or item.get('doctor_id') or item.get('contact_id') or item.get('item_id')
        
        if data_center_service.delete_data(category, item_id):
            ui.notify('数据已删除', type='positive')
            dialog.close()
            # 刷新当前页面
            self.navigate('data_center')
        else:
            ui.notify('删除失败', type='negative')
    
    def render_hospitals(self):
        """渲染医院管理页面"""
        ui.label('🏥 医院管理').classes('page-title')
        
        with ui.tabs().classes('w-full text-white glass-tabs') as tabs:
            tab_overview = ui.tab('🔗 关联视图')
            tab_hospitals = ui.tab('医院')
            tab_departments = ui.tab('科室')
            tab_products = ui.tab('产品')
            tab_doctors = ui.tab('医生')
            tab_contacts = ui.tab('联系人')
            tab_competitors = ui.tab('竞品')
            tab_associations = ui.tab('产品关联')
        
        with ui.tab_panels(tabs, value=tab_overview).classes('w-full bg-transparent'):
            with ui.tab_panel(tab_overview):
                self.render_data_relationship_view()
            with ui.tab_panel(tab_hospitals):
                self.render_hospital_panel()
            with ui.tab_panel(tab_departments):
                self.render_department_panel()
            with ui.tab_panel(tab_products):
                self.render_product_panel()
            with ui.tab_panel(tab_doctors):
                self.render_doctors_in_hospital()
            with ui.tab_panel(tab_contacts):
                self.render_contacts_in_hospital()
            with ui.tab_panel(tab_competitors):
                self.render_competitor_panel()
            with ui.tab_panel(tab_associations):
                self.render_product_association_panel()
    
    def render_hospital_panel(self):
        """渲染医院管理面板"""
        current_edit_id = {'value': None}

        with ui.grid().classes('w-full gap-4 grid-cols-1 md:grid-cols-3'):
            # 左侧：添加/编辑表单
            with ui.card().classes('glass-card p-4'):
                form_label = ui.label('➕ 添加医院').classes('text-subtitle1 font-bold text-white mb-3')

                name_input = ui.input(label='医院名称').classes('w-full glass-input')
                level_input = ui.select(
                    label='医院等级',
                    options=['三甲', '三乙', '二甲', '二乙', '一甲', '一乙', '其他']
                ).classes('w-full glass-input')
                address_input = ui.input(label='地址').classes('w-full glass-input')
                phone_input = ui.input(label='联系电话').classes('w-full glass-input')
                notes_input = ui.textarea(label='备注').classes('w-full glass-input')

                def reset_form():
                    name_input.value = ''
                    level_input.value = ''
                    address_input.value = ''
                    phone_input.value = ''
                    notes_input.value = ''
                    current_edit_id['value'] = None
                    form_label.text = '➕ 添加医院'
                    save_btn.text = '💾 保存'

                def save_hospital():
                    if not name_input.value:
                        ui.notify('医院名称不能为空', type='warning')
                        return

                    hospital_service.create_hospital(
                        name=name_input.value,
                        level=level_input.value,
                        address=address_input.value,
                        contact_phone=phone_input.value,
                        notes=notes_input.value,
                        hospital_id=current_edit_id['value']
                    )

                    action = "更新" if current_edit_id['value'] else "添加"
                    ui.notify(f'医院已{action}', type='positive')
                    reset_form()
                    refresh_list()

                def load_for_edit(item):
                    name_input.value = item.get('name', '')
                    level_input.value = item.get('level', '')
                    address_input.value = item.get('address', '')
                    phone_input.value = item.get('contact_phone', '')
                    notes_input.value = item.get('notes', '')
                    current_edit_id['value'] = item['hospital_id']
                    form_label.text = '✏️ 编辑医院'
                    save_btn.text = '✏️ 更新'
                    ui.notify('已加载医院信息', type='info')

                def delete_item(item):
                    """删除医院（带确认）"""
                    with ui.dialog() as dialog, ui.card().classes('glass-card'):
                        ui.label('⚠️ 确认删除').classes('text-h6 text-white q-mb-md')
                        ui.label(f'确定要删除医院 "{item["name"]}" 吗？').classes('text-white')
                        ui.label('医院下的科室关联将失效，相关医生档案不受删除但会失去医院归属，此操作不可恢复！').classes('text-negative q-mt-sm text-caption')

                        with ui.row().classes('w-full justify-end q-mt-lg gap-3'):
                            ui.button('取消', on_click=dialog.close).classes('glass-btn-secondary')
                            ui.button('🗑️ 确认删除', on_click=lambda: [
                                hospital_service.delete_hospital(item['hospital_id']),
                                dialog.close(),
                                ui.notify('医院已删除', type='positive'),
                                reset_form() if current_edit_id['value'] == item['hospital_id'] else None,
                                refresh_list()
                            ]).props('color=negative')

                    dialog.open()

                with ui.row().classes('gap-3 mt-3'):
                    save_btn = ui.button('💾 保存', on_click=save_hospital).props('color=primary')
                    ui.button('🔄 重置', on_click=reset_form).props('color=secondary')

            # 右侧：医院列表
            with ui.card().classes('glass-card p-4 md:col-span-2'):
                ui.label('🏥 医院列表').classes('text-subtitle1 font-bold text-white mb-3')
                list_container = ui.column().classes('w-full')

                def refresh_list():
                    list_container.clear()
                    with list_container:
                        hospitals = hospital_service.list_hospitals()
                        if not hospitals:
                            ui.label('暂无医院，点击左侧表单添加').classes('text-caption text-grey')
                            return

                        cols = 3 if len(hospitals) > 6 else 2
                        with ui.grid().classes(f'w-full gap-3 grid-cols-{cols}'):
                            for hospital in hospitals:
                                with ui.card().classes('glass-card-secondary p-3'):
                                    with ui.row().classes('w-full items-center justify-between mb-2'):
                                        ui.label(hospital['name']).classes('text-white font-bold text-body1')
                                        ui.label(hospital.get('level', '')).classes('text-caption text-blue-4')
                                    with ui.row().classes('w-full mb-2'):
                                        ui.label('📍').classes('text-caption')
                                        ui.label(hospital.get('address', '未知地址')).classes('text-caption text-grey')
                                    with ui.row().classes('gap-2'):
                                        ui.button('✏️', on_click=lambda e, h=hospital: load_for_edit(h)).props('flat dense size=sm color=primary')
                                        ui.button('🗑️', on_click=lambda e, h=hospital: delete_item(h)).props('flat dense size=sm color=negative')

                refresh_list()
    
    def render_department_panel(self):
        """渲染科室管理面板"""
        hospitals = hospital_service.list_hospitals()
        hospital_options = {h['hospital_id']: h['name'] for h in hospitals}
        hospital_map = {h['hospital_id']: h['name'] for h in hospitals}

        with ui.grid().classes('w-full gap-4 grid-cols-1 md:grid-cols-3'):
            # 左侧：添加科室
            with ui.card().classes('glass-card p-4'):
                ui.label('🏥 添加科室').classes('text-subtitle1 font-bold text-white mb-3')

                hospital_select = ui.select(
                    label='所属医院',
                    options=hospital_options
                ).classes('w-full glass-input')

                name_input = ui.input(label='科室名称').classes('w-full glass-input')
                head_input = ui.input(label='科室主任').classes('w-full glass-input')
                desc_input = ui.textarea(label='科室描述').classes('w-full glass-input')
                notes_input = ui.textarea(label='备注').classes('w-full glass-input')

                def save_department():
                    if not hospital_select.value or not name_input.value:
                        ui.notify('请选择医院并输入科室名称', type='warning')
                        return

                    hospital_service.create_department(
                        name=name_input.value,
                        hospital_id=hospital_select.value,
                        description=desc_input.value,
                        head_doctor=head_input.value,
                        notes=notes_input.value
                    )

                    ui.notify('科室已添加', type='positive')
                    name_input.value = ''
                    desc_input.value = ''
                    head_input.value = ''
                    notes_input.value = ''
                    refresh_dept_list()

                ui.button('💾 保存', on_click=save_department).props('color=primary').classes('mt-3')

            # 右侧：科室列表
            with ui.card().classes('glass-card p-4 md:col-span-2'):
                ui.label('📋 科室列表').classes('text-subtitle1 font-bold text-white mb-3')
                dept_list_container = ui.column().classes('w-full')

                def edit_dept(dept_data):
                    with ui.dialog() as dialog, ui.card().classes('glass-card q-pa-lg').style('min-width: 400px'):
                        ui.label('✏️ 编辑科室').classes('text-h6 text-white q-mb-md')

                        edit_name = ui.input(label='科室名称', value=dept_data['name']).classes('w-full glass-input')
                        edit_desc = ui.textarea(label='科室描述', value=dept_data.get('description', '')).classes('w-full glass-input')
                        edit_head = ui.input(label='科室主任', value=dept_data.get('head_doctor', '')).classes('w-full glass-input')
                        edit_notes = ui.textarea(label='备注', value=dept_data.get('notes', '')).classes('w-full glass-input')

                        def save_edit():
                            if not edit_name.value:
                                ui.notify('科室名称不能为空', type='warning')
                                return

                            hospital_service.update_department(
                                dept_data['department_id'],
                                {
                                    'name': edit_name.value,
                                    'description': edit_desc.value,
                                    'head_doctor': edit_head.value,
                                    'notes': edit_notes.value
                                }
                            )
                            ui.notify('科室已更新', type='positive')
                            dialog.close()
                            refresh_dept_list()

                        with ui.row().classes('w-full justify-end q-mt-md'):
                            ui.button('取消', on_click=dialog.close).props('flat')
                            ui.button('保存', on_click=save_edit).props('color=primary')

                    dialog.open()

                def delete_dept(dept):
                    """删除科室（带确认）"""
                    with ui.dialog() as dialog, ui.card().classes('glass-card'):
                        ui.label('⚠️ 确认删除').classes('text-h6 text-white q-mb-md')
                        ui.label(f'确定要删除科室 "{dept["name"]}" 吗？').classes('text-white')
                        ui.label('此操作不可恢复！').classes('text-negative q-mt-sm text-caption')

                        with ui.row().classes('w-full justify-end q-mt-lg gap-3'):
                            ui.button('取消', on_click=dialog.close).classes('glass-btn-secondary')
                            ui.button('🗑️ 确认删除', on_click=lambda: [
                                hospital_service.delete_department(dept['department_id']),
                                dialog.close(),
                                ui.notify('科室已删除', type='positive'),
                                refresh_dept_list()
                            ]).props('color=negative')

                    dialog.open()

                def refresh_dept_list():
                    dept_list_container.clear()
                    with dept_list_container:
                        departments = hospital_service.list_departments()
                        hospitals = hospital_service.list_hospitals()

                        if not departments:
                            ui.label('暂无科室，点击左侧表单添加').classes('text-caption text-grey')
                            return

                        # 建立 department_id -> hospital_name 的反向映射
                        dept_to_hospital = {}
                        for hosp in hospitals:
                            for dept_id in hosp.get('departments', []):
                                dept_to_hospital[dept_id] = hosp.get('name', '未知医院')

                        # 按医院分组
                        dept_by_hospital = {}
                        for dept in departments:
                            hosp_name = dept_to_hospital.get(dept.get('department_id', ''), '未知医院')
                            if hosp_name not in dept_by_hospital:
                                dept_by_hospital[hosp_name] = []
                            dept_by_hospital[hosp_name].append(dept)

                        for hosp_name in sorted(dept_by_hospital.keys()):
                            with ui.expansion(f'🏥 {hosp_name}').classes('w-full glass-expansion'):
                                for dept in dept_by_hospital[hosp_name]:
                                    with ui.card().classes('glass-card-secondary p-3 mb-2'):
                                        with ui.row().classes('w-full items-center justify-between'):
                                            with ui.column().classes('col-grow'):
                                                ui.label(dept['name']).classes('text-white font-bold')
                                                if dept.get('head_doctor'):
                                                    ui.label(f'👨‍⚕️ 主任: {dept["head_doctor"]}').classes('text-caption text-blue-4')
                                            with ui.row().classes('gap-2'):
                                                ui.button('✏️', on_click=lambda e, d=dept: edit_dept(d)).props('flat dense size=sm color=primary')
                                                ui.button('🗑️', on_click=lambda e, d=dept: delete_dept(d)).props('flat dense size=sm color=negative')

                refresh_dept_list()
    
    def render_product_panel(self):
        """渲染产品管理面板"""
        with ui.grid().classes('w-full gap-4 grid-cols-1 md:grid-cols-3'):
            # 左侧：添加产品表单
            with ui.card().classes('glass-card p-4'):
                ui.label('💊 添加产品').classes('text-subtitle1 font-bold text-white mb-3')

                with ui.grid().classes('w-full gap-3 grid-cols-1 md:grid-cols-2'):
                    name_input = ui.input(label='产品名称').classes('w-full')
                    category_input = ui.input(label='产品类别').classes('w-full')
                    features_input = ui.input(label='关键特性（逗号分隔）').classes('w-full')
                    indications_input = ui.input(label='适应症（逗号分隔）').classes('w-full')

                desc_input = ui.textarea(label='产品描述').classes('w-full')
                notes_input = ui.textarea(label='备注').classes('w-full')

                def save_product():
                    if not name_input.value:
                        ui.notify('产品名称不能为空', type='warning')
                        return

                    features = [f.strip() for f in features_input.value.split(',') if f.strip()]
                    indications = [i.strip() for i in indications_input.value.split(',') if i.strip()]

                    hospital_service.create_product(
                        name=name_input.value,
                        category=category_input.value,
                        description=desc_input.value,
                        key_features=features,
                        indications=indications,
                        notes=notes_input.value
                    )

                    ui.notify('产品已添加', type='positive')
                    name_input.value = ''
                    category_input.value = ''
                    desc_input.value = ''
                    features_input.value = ''
                    indications_input.value = ''
                    notes_input.value = ''
                    refresh_product_list()

                ui.button('💾 保存', on_click=save_product).props('color=primary').classes('mt-3')

            # 右侧：产品列表
            with ui.card().classes('glass-card p-4 md:col-span-2'):
                ui.label('📋 产品列表').classes('text-subtitle1 font-bold text-white mb-3')
                product_list_container = ui.column().classes('w-full')

        def edit_product(product_data):
            """编辑产品对话框"""
            with ui.dialog() as dialog, ui.card().classes('glass-card q-pa-lg').style('min-width: 500px'):
                ui.label('编辑产品').classes('text-h6 text-white q-mb-md')

                edit_name = ui.input(label='产品名称', value=product_data['name']).classes('w-full glass-input')
                edit_category = ui.input(label='产品类别', value=product_data.get('category', '')).classes('w-full glass-input')
                edit_desc = ui.textarea(label='产品描述', value=product_data.get('description', '')).classes('w-full glass-input')

                features_str = ', '.join(product_data.get('key_features', []))
                indications_str = ', '.join(product_data.get('indications', []))

                edit_features = ui.input(label='关键特性（逗号分隔）', value=features_str).classes('w-full glass-input')
                edit_indications = ui.input(label='适应症（逗号分隔）', value=indications_str).classes('w-full glass-input')
                edit_notes = ui.textarea(label='备注', value=product_data.get('notes', '')).classes('w-full glass-input')

                def save_edit():
                    if not edit_name.value:
                        ui.notify('产品名称不能为空', type='warning')
                        return

                    features = [f.strip() for f in edit_features.value.split(',') if f.strip()]
                    indications = [i.strip() for i in edit_indications.value.split(',') if i.strip()]

                    hospital_service.update_product(
                        product_data['product_id'],
                        {
                            'name': edit_name.value,
                            'category': edit_category.value,
                            'description': edit_desc.value,
                            'key_features': features,
                            'indications': indications,
                            'notes': edit_notes.value
                        }
                    )
                    ui.notify('产品已更新', type='positive')
                    dialog.close()
                    refresh_product_list()

                with ui.row().classes('w-full justify-end q-mt-md'):
                    ui.button('取消', on_click=dialog.close).props('flat')
                    ui.button('保存', on_click=save_edit).classes('glass-btn')

            dialog.open()

        def delete_product(product_id):
            hospital_service.delete_product(product_id)
            ui.notify('产品已删除', type='positive')
            refresh_product_list()

        def refresh_product_list():
            product_list_container.clear()
            with product_list_container:
                products = hospital_service.list_products()
                if not products:
                    ui.label('暂无产品，点击上方表单添加').classes('text-caption text-grey')
                    return

                cols = 3 if len(products) > 6 else 2
                with ui.grid().classes(f'w-full gap-3 grid-cols-{cols}'):
                    for product in products:
                        with ui.card().classes('glass-card-secondary p-3'):
                            with ui.row().classes('w-full items-center justify-between mb-2'):
                                ui.label(product['name']).classes('text-white font-bold text-body1')
                                ui.label(product.get('category', '未分类')).classes('text-caption text-green-4')
                            if product.get('description'):
                                desc_short = product['description'][:50] + '...' if len(product['description']) > 50 else product['description']
                                ui.label(desc_short).classes('text-caption text-grey mb-2')
                            if product.get('key_features'):
                                features_str = ', '.join(product['key_features'][:3])
                                ui.label(f'✨ {features_str}').classes('text-caption text-amber-4')
                            with ui.row().classes('gap-2 mt-2'):
                                ui.button('✏️', on_click=lambda e, p=product: edit_product(p)).props('flat dense size=sm color=primary')
                                ui.button('🗑️', on_click=lambda e, p=product: delete_product(p['product_id'])).props('flat dense size=sm color=negative')

        refresh_product_list()

    def render_competitor_panel(self):
        """渲染竞品管理面板"""
        with ui.row().classes('w-full q-gutter-md'):
            # 左侧：添加竞品
            with ui.card().classes('glass-card col-4 q-pa-lg'):
                ui.label('添加竞品').classes('text-h6 text-white q-mb-md')
                
                name_input = ui.input(label='竞品名称').classes('w-full glass-input')
                manufacturer_input = ui.input(label='生产厂家').classes('w-full glass-input')
                advantages_input = ui.textarea(label='竞品优势').classes('w-full glass-input')
                disadvantages_input = ui.textarea(label='竞品劣势').classes('w-full glass-input')
                market_share_input = ui.input(label='市场份额').classes('w-full glass-input')
                notes_input = ui.textarea(label='备注').classes('w-full glass-input')
                
                def save_competitor():
                    if not name_input.value:
                        ui.notify('竞品名称不能为空', type='warning')
                        return
                    
                    hospital_service.create_competitor(
                        name=name_input.value,
                        manufacturer=manufacturer_input.value,
                        advantages=advantages_input.value,
                        disadvantages=disadvantages_input.value,
                        market_share=market_share_input.value,
                        notes=notes_input.value
                    )
                    
                    ui.notify('竞品已添加', type='positive')
                    name_input.value = ''
                    manufacturer_input.value = ''
                    advantages_input.value = ''
                    disadvantages_input.value = ''
                    market_share_input.value = ''
                    notes_input.value = ''
                    refresh_competitor_list()
                
                ui.button('保存', on_click=save_competitor).classes('glass-btn q-mt-md')
            
            # 右侧：竞品列表
            with ui.card().classes('glass-card col-7 q-pa-lg'):
                ui.label('竞品列表').classes('text-h6 text-white q-mb-md')
                competitor_list_container = ui.column().classes('w-full')
                
                def refresh_competitor_list():
                    competitor_list_container.clear()
                    with competitor_list_container:
                        competitors = hospital_service.list_competitors()
                        for comp in competitors:
                            with ui.expansion(comp['name']).classes('w-full glass-expansion'):
                                ui.label(f"厂家: {comp.get('manufacturer', '')}").classes('text-white')
                                ui.label(f"优势: {comp.get('advantages', '')}").classes('text-positive')
                                ui.label(f"劣势: {comp.get('disadvantages', '')}").classes('text-negative')
                                ui.label(f"市场份额: {comp.get('market_share', '')}").classes('text-secondary')
                                with ui.row().classes('q-mt-sm'):
                                    ui.button('删除', on_click=lambda c=comp: delete_competitor(c['competitor_id'])).props('flat dense size=sm color=negative')
                
                def delete_competitor(comp_id):
                    hospital_service.delete_competitor(comp_id)
                    ui.notify('竞品已删除', type='positive')
                    refresh_competitor_list()
                
                refresh_competitor_list()
    
    def render_product_association_panel(self):
        """渲染产品关联管理面板"""
        from modules.product_association.ui import render_product_association_page
        render_product_association_page()
    
    def on_hospital_change(self):
        """医院选择变化时更新科室列表"""
        if not hasattr(self, 'doc_hospital_id') or not hasattr(self, 'doc_department_id'):
            return
        
        hospital_id = self.doc_hospital_id.value
        if hospital_id:
            # 加载该医院的科室
            departments = hospital_service.list_departments(hospital_id)
            dept_options = {d['department_id']: d['name'] for d in departments}
            dept_options[''] = '未指定'
            
            # 更新科室选择框的选项
            self.doc_department_id.set_options(dept_options)
            self.doc_department_id.value = ''
            
            # 自动填充医院名称
            hospital = hospital_service.get_hospital(hospital_id)
            if hospital:
                self.doc_hospital.value = hospital.name
        else:
            self.doc_department_id.set_options({'': '未指定'})
            self.doc_department_id.value = ''
            self.doc_hospital.value = ''
    
    def on_department_change(self):
        """科室选择变化时自动填充科室名称"""
        if not hasattr(self, 'doc_department_id') or not hasattr(self, 'doc_department'):
            return
        
        department_id = self.doc_department_id.value
        if department_id:
            # 自动填充科室名称
            department = hospital_service.get_department(department_id)
            if department:
                self.doc_department.value = department.name
        else:
            self.doc_department.value = ''
    
    def render_doctors(self):
        """渲染医生管理页面"""
        ui.label('👨‍⚕️ 医生管理').classes('page-title')

        with ui.row().classes('w-full q-gutter-md'):
            # 左侧：添加医生
            with ui.card().classes('glass-card col-4 q-pa-lg'):
                ui.label('➕ 添加医生').classes('section-title')

                self.doc_name = ui.input(label='姓名 *').classes('w-full glass-input')

                # 医院选择（关联到医院管理）
                hospitals = hospital_service.list_hospitals()
                hospital_options = {h['hospital_id']: h['name'] for h in hospitals}
                hospital_options[''] = '未指定'

                self.doc_hospital_id = ui.select(
                    label='所属医院（从已有医院选择）',
                    options=hospital_options,
                    value='',
                    on_change=self.on_hospital_change
                ).classes('w-full glass-input')

                self.doc_hospital = ui.input(label='医院名称（未收录时手动输入）', ).classes('w-full glass-input')

                # 科室选择
                self.doc_department_id = ui.select(
                    label='所属科室（选择医院后可选）',
                    options={'': '未指定'},
                    value='',
                    on_change=self.on_department_change
                ).classes('w-full glass-input')

                self.doc_department = ui.input(label='科室名称（未收录时手动输入）').classes('w-full glass-input')
                self.doc_title = ui.input(label='职称').classes('w-full glass-input')
                self.doc_interests = ui.input(label='兴趣领域 (逗号分隔)').classes('w-full glass-input')

                with ui.grid().classes('w-full gap-3 grid-cols-2'):
                    self.doc_style = ui.select(
                        label='决策风格',
                        options=['循证型', '经验型', '保守型', '创新型', '关系型']
                    ).classes('w-full glass-input')
                    self.doc_stage = ui.select(
                        label='关系阶段',
                        options=['初识', '建立中', '稳定', '深入'],
                        value='初识'
                    ).classes('w-full glass-input')

                self.doc_needs = ui.textarea(label='未满足需求').classes('w-full glass-input')
                self.doc_notes = ui.textarea(label='📌 备注（要注意的事项）').classes('w-full glass-input')

                ui.button('💾 添加医生', on_click=self.add_doctor).classes('glass-btn q-mt-md')

            # 右侧：医生列表
            with ui.card().classes('glass-card col-7 q-pa-lg'):
                ui.label('📋 医生列表').classes('section-title')
                self.doctor_table_container = ui.column().classes('w-full')
                self.refresh_doctor_list()
    

    def render_reflection(self):
        """渲染成长反思页面"""
        ui.label('💭 个人成长反思').classes('page-title')
        
        # 检查今日是否已反思
        today = datetime.now().strftime('%Y-%m-%d')
        existing = personal_growth_service.get_reflection(today)
        
        with ui.row().classes('w-full q-gutter-md'):
            # 左侧：反思表单
            with ui.card().classes('glass-card col-7 q-pa-lg'):
                ui.label(f'今日反思 ({today})').classes('text-h6 text-white q-mb-md')
                
                self.ref_score = ui.slider(min=1, max=10, value=existing.today_score if existing else 5).props('label-always color=purple').classes('w-full')
                ui.label('今日自我评分 (1-10)').classes('text-white')
                
                self.ref_anxiety = ui.textarea(
                    label='😰 今日焦虑来源/压力点',
                    value=existing.anxiety_source if existing else ''
                ).classes('w-full glass-input')
                
                self.ref_achievement = ui.textarea(
                    label='🏆 今日成就/做对了什么',
                    value=existing.achievement if existing else ''
                ).classes('w-full glass-input')
                
                self.ref_weakness = ui.textarea(
                    label='😓 暴露的弱点/不足',
                    value=existing.weakness if existing else ''
                ).classes('w-full glass-input')
                
                self.ref_avoidance = ui.textarea(
                    label='🙈 在逃避什么（诚实面对）',
                    value=existing.avoidance if existing else ''
                ).classes('w-full glass-input')
                
                self.ref_breakthrough = ui.textarea(
                    label='💡 突破点/解决方案',
                    value=existing.breakthrough if existing else ''
                ).classes('w-full glass-input')
                
                self.ref_learning = ui.textarea(
                    label='📖 今日学习/感悟',
                    value=existing.learning if existing else ''
                ).classes('w-full glass-input')
                
                self.ref_improvement = ui.textarea(
                    label='🎯 明日改进目标',
                    value=existing.improvement_goal if existing else ''
                ).classes('w-full glass-input')
                
                self.ref_notes = ui.textarea(
                    label='📌 私密备注',
                    value=existing.notes if existing else ''
                ).classes('w-full glass-input')
                
                ui.button('保存今日反思', on_click=self.save_reflection).classes('glass-btn q-mt-lg')
            
            # 右侧：成长统计
            with ui.column().classes('col-4 q-gutter-md'):
                with ui.card().classes('glass-card q-pa-lg'):
                    ui.label('📈 成长统计').classes('text-h6 text-white q-mb-md')
                    summary = personal_growth_service.get_growth_summary(30)
                    
                    with ui.column().classes('q-gutter-sm'):
                        with ui.row().classes('justify-between items-center w-full'):
                            ui.label('近30天反思').classes('text-white')
                            ui.label(f"{summary['total_reflections']}篇").classes('text-accent font-bold')
                        
                        with ui.row().classes('justify-between items-center w-full'):
                            ui.label('记录成就').classes('text-white')
                            ui.label(f"{summary['days_with_achievement']}天").classes('text-positive font-bold')
                        
                        with ui.row().classes('justify-between items-center w-full'):
                            ui.label('记录学习').classes('text-white')
                            ui.label(f"{summary['days_with_learning']}天").classes('text-info font-bold')
                        
                        with ui.row().classes('justify-between items-center w-full'):
                            ui.label('坚持率').classes('text-white')
                            ui.label(f"{summary['consistency_rate']}").classes('text-warning font-bold')
    
    def render_knowledge(self):
        """渲染知识库页面"""
        ui.label('📚 知识库').classes('page-title')
        
        with ui.tabs().classes('w-full text-white glass-tabs') as tabs:
            disease_tab = ui.tab('病种知识')
            product_view_tab = ui.tab('查看产品知识库')
            product_manage_tab = ui.tab('管理产品知识库')
            market_tab = ui.tab('市场问题')
        
        with ui.tab_panels(tabs, value=disease_tab).classes('w-full bg-transparent'):
            with ui.tab_panel(disease_tab):
                self.render_knowledge_panel('disease')
            with ui.tab_panel(product_view_tab):
                self.render_product_knowledge_view()
            with ui.tab_panel(product_manage_tab):
                self.render_product_knowledge_manage()
            with ui.tab_panel(market_tab):
                self.render_knowledge_panel('market')
    
    def render_product_knowledge_view(self):
        """渲染产品知识库查看页面（只读模式）"""
        with ui.row().classes('w-full q-gutter-md'):
            # 左侧：产品列表
            with ui.card().classes('glass-card col-3 q-pa-lg'):
                ui.label('产品列表').classes('text-h6 text-white q-mb-md')
                
                products = hospital_service.list_products()
                
                if not products:
                    ui.label('暂无产品').classes('text-secondary')
                    ui.label('请先在"数据管理-医院管理-产品"中添加产品').classes('text-caption text-secondary q-mt-sm')
                    return
                
                # 产品列表容器
                self.kb_view_product_list = ui.column().classes('w-full q-gutter-sm')
                
                with self.kb_view_product_list:
                    for product in products:
                        with ui.card().classes('glass-list-item q-pa-md cursor-pointer').on('click', lambda p=product: self.show_product_detail_view(p['product_id'])):
                            ui.label(f"📦 {product['name']}").classes('text-white font-bold')
                            if product.get('category'):
                                ui.label(f"类别: {product['category']}").classes('text-caption text-secondary')
                            
                            # 显示附件数量
                            attachments = hospital_service.get_product_attachments(product['product_id'])
                            ui.label(f"📎 {len(attachments)} 个附件").classes('text-caption text-accent')
            
            # 右侧：产品详情
            with ui.card().classes('glass-card col-8 q-pa-lg'):
                ui.label('产品详情').classes('text-h6 text-white q-mb-md')
                
                self.kb_view_detail_container = ui.column().classes('w-full')
                
                with self.kb_view_detail_container:
                    ui.label('👈 请在左侧选择产品查看详情').classes('text-secondary text-h6')
    
    def show_product_detail_view(self, product_id: str):
        """显示产品详情（只读模式）"""
        product = hospital_service.get_product(product_id)
        if not product:
            return
        
        self.kb_view_detail_container.clear()
        
        with self.kb_view_detail_container:
            # 产品基本信息卡片
            with ui.card().classes('glass-card q-pa-lg q-mb-md'):
                with ui.row().classes('w-full items-center justify-between'):
                    ui.label(f'📦 {product.name}').classes('text-h5 text-white')
                    ui.button(
                        '✏️ 编辑此产品',
                        on_click=lambda: self.navigate_to_product_manage(product_id)
                    ).props('flat color=accent')
                
                ui.separator().classes('q-my-md')
                
                # 产品信息网格
                with ui.grid(columns=2).classes('w-full q-gutter-md'):
                    # 左列
                    with ui.column().classes('q-gutter-sm'):
                        if product.category:
                            with ui.row().classes('items-center'):
                                ui.label('类别:').classes('text-white font-bold')
                                ui.label(product.category).classes('text-secondary')
                        
                        if product.key_features:
                            ui.label('关键特性:').classes('text-white font-bold q-mt-md')
                            for feature in product.key_features:
                                ui.label(f'• {feature}').classes('text-secondary q-ml-md')
                    
                    # 右列
                    with ui.column().classes('q-gutter-sm'):
                        if product.indications:
                            ui.label('适应症:').classes('text-white font-bold')
                            for indication in product.indications:
                                ui.label(f'• {indication}').classes('text-secondary q-ml-md')
                
                # 产品描述
                if product.description:
                    ui.separator().classes('q-my-md')
                    ui.label('产品描述:').classes('text-white font-bold')
                    ui.label(product.description).classes('text-secondary q-mt-sm')
                
                # 备注
                if product.notes:
                    ui.separator().classes('q-my-md')
                    ui.label('备注:').classes('text-white font-bold')
                    ui.label(product.notes).classes('text-secondary q-mt-sm')
            
            # 产品附件卡片
            with ui.card().classes('glass-card q-pa-lg'):
                ui.label('📎 产品资料附件').classes('text-h6 text-white q-mb-md')
                
                attachments = hospital_service.get_product_attachments(product_id)
                
                if not attachments:
                    ui.label('暂无附件').classes('text-secondary q-pa-md')
                    ui.label('💡 如需添加附件，请切换到"管理产品知识库"标签').classes('text-caption text-accent q-mt-sm')
                else:
                    ui.label(f'共 {len(attachments)} 个附件').classes('text-white q-mb-md')
                    
                    # 附件网格显示
                    with ui.grid(columns=2).classes('w-full q-gutter-md'):
                        for idx, attachment in enumerate(attachments, 1):
                            with ui.card().classes('glass-list-item q-pa-md'):
                                file_icons = {
                                    'ppt': '📊', 'pptx': '📊',
                                    'doc': '📄', 'docx': '📄',
                                    'txt': '📝', 'pdf': '📕'
                                }
                                file_type = attachment.get('file_type', '').lower()
                                icon = file_icons.get(file_type, '📎')
                                
                                with ui.row().classes('w-full items-center justify-between'):
                                    with ui.column().classes('col-grow'):
                                        ui.label(f"{icon} {attachment.get('filename', '')}").classes('text-white font-bold')
                                        ui.label(f"类型: {file_type.upper()}").classes('text-caption text-secondary')
                                        ui.label(f"上传: {attachment.get('upload_time', '')[:10]}").classes('text-caption text-secondary')
                                    
                                    ui.button(
                                        '查看',
                                        on_click=lambda a=attachment: self.view_kb_attachment(a)
                                    ).props('flat dense color=primary')
    
    def navigate_to_product_manage(self, product_id: str):
        """导航到产品管理页面并选择指定产品"""
        # 这个函数会在管理页面渲染后被调用
        self.pending_product_id = product_id
        ui.notify('请切换到"管理产品知识库"标签进行编辑', type='info')
    
    def render_product_knowledge_manage(self):
        """渲染产品知识库管理页面（编辑模式）"""
        with ui.row().classes('w-full q-gutter-md'):
            # 左侧：产品选择和文件上传
            with ui.card().classes('glass-card col-4 q-pa-lg'):
                ui.label('产品知识库管理').classes('text-h6 text-white q-mb-md')
                
                # 选择产品
                products = hospital_service.list_products()
                product_options = {p['product_id']: p['name'] for p in products}
                
                if not product_options:
                    ui.label('暂无产品，请先在"医院管理-产品"中添加产品').classes('text-warning')
                    return
                
                self.kb_product_select = ui.select(
                    label='选择产品',
                    options=product_options,
                    on_change=self.on_kb_product_change
                ).classes('w-full glass-input')
                
                ui.label('💡 提示：选择产品后可上传资料和编辑信息').classes('text-caption text-secondary q-mt-sm')
                
                ui.separator().classes('q-my-md')
                
                # 文件上传区
                ui.label('📎 上传产品资料').classes('text-white font-bold q-mb-sm')
                ui.label('支持格式：PPT, PPTX, DOC, DOCX, TXT, PDF (最大50MB)').classes('text-caption text-secondary q-mb-md')
                ui.label('⚠️ 请先选择产品，再上传文件').classes('text-caption text-warning q-mb-md')
                
                self.kb_file_upload = ui.upload(
                    label='点击选择文件上传',
                    on_upload=self.on_kb_file_upload,
                    auto_upload=True,
                    max_file_size=50 * 1024 * 1024  # 50MB
                ).props('accept=".ppt,.pptx,.doc,.docx,.txt,.pdf"').classes('w-full')
                
                # 同步按钮（用于手动添加文件后同步）
                ui.button(
                    '🔄 同步附件目录',
                    on_click=self.sync_kb_attachments
                ).props('flat dense size=sm color=accent').classes('q-mt-sm')
                ui.label('如果手动添加了文件，点击此按钮同步').classes('text-caption text-secondary')
                
                ui.separator().classes('q-my-md')
                
                # 编辑产品信息
                ui.label('✏️ 编辑产品信息').classes('text-white font-bold q-mb-sm')
                
                self.kb_product_name = ui.input(label='产品名称').classes('w-full glass-input')
                self.kb_product_category = ui.input(label='产品类别').classes('w-full glass-input')
                self.kb_product_desc = ui.textarea(label='产品描述').classes('w-full glass-input')
                self.kb_product_features = ui.input(label='关键特性（逗号分隔）').classes('w-full glass-input')
                self.kb_product_indications = ui.input(label='适应症（逗号分隔）').classes('w-full glass-input')
                self.kb_product_notes = ui.textarea(label='备注').classes('w-full glass-input')
                
                with ui.row().classes('w-full q-gutter-sm q-mt-md'):
                    ui.button('更新产品信息', on_click=self.update_kb_product).classes('glass-btn')
                    ui.button('清空表单', on_click=self.clear_kb_product_form).classes('glass-btn-secondary')
            
            # 右侧：产品详情和附件列表
            with ui.card().classes('glass-card col-7 q-pa-lg'):
                ui.label('产品详情与附件').classes('text-h6 text-white q-mb-md')
                
                self.kb_product_detail_container = ui.column().classes('w-full')
                
                # 初始显示提示
                with self.kb_product_detail_container:
                    ui.label('👈 请在左侧选择产品').classes('text-secondary text-h6')
    
    def clear_kb_product_form(self):
        """清空产品知识库表单"""
        self.kb_product_select.value = None
        self.kb_product_name.value = ''
        self.kb_product_category.value = ''
        self.kb_product_desc.value = ''
        self.kb_product_features.value = ''
        self.kb_product_indications.value = ''
        self.kb_product_notes.value = ''
        
        # 清空右侧显示
        if hasattr(self, 'kb_product_detail_container'):
            self.kb_product_detail_container.clear()
            with self.kb_product_detail_container:
                ui.label('👈 请在左侧选择产品').classes('text-secondary text-h6')
        
        ui.notify('表单已清空', type='info')
    
    def sync_kb_attachments(self):
        """同步产品附件目录"""
        if hasattr(self, 'kb_product_select') and self.kb_product_select.value:
            # 同步当前选择的产品
            product_id = self.kb_product_select.value
            count = hospital_service.sync_product_attachments(product_id)
            
            if count > 0:
                ui.notify(f'✓ 同步成功：发现 {count} 个新文件', type='positive')
                self.refresh_kb_product_detail()
            else:
                ui.notify('未发现新文件', type='info')
        else:
            # 同步所有产品
            ui.notify('正在同步所有产品的附件...', type='info')
            results = hospital_service.sync_all_product_attachments()
            
            # 检查孤立目录
            orphans = hospital_service.list_orphan_attachment_dirs()
            
            if results:
                total = sum(results.values())
                ui.notify(f'✓ 同步完成：共发现 {total} 个新文件', type='positive')
            
            if orphans:
                # 显示孤立目录信息
                with ui.dialog() as dialog, ui.card().classes('glass-card').style('min-width: 600px;'):
                    ui.label('⚠️ 发现孤立的附件目录').classes('text-h6 text-white q-mb-md')
                    ui.label('以下目录中的文件没有对应的产品，无法同步：').classes('text-white q-mb-md')
                    
                    for orphan in orphans:
                        with ui.card().classes('glass-list-item q-pa-md q-mb-sm'):
                            ui.label(f"目录: {orphan['product_id']}").classes('text-white font-bold')
                            ui.label(f"文件数: {orphan['file_count']}").classes('text-secondary')
                            ui.label(f"路径: {orphan['path']}").classes('text-caption text-secondary')
                            
                            if orphan['files']:
                                ui.label('文件列表:').classes('text-white q-mt-sm')
                                for filename in orphan['files']:
                                    ui.label(f"  • {filename}").classes('text-caption text-secondary')
                    
                    ui.label('建议操作：').classes('text-white q-mt-md font-bold')
                    ui.label('1. 在"医院管理-产品"中创建对应的产品').classes('text-secondary')
                    ui.label('2. 或将文件移动到现有产品的目录下').classes('text-secondary')
                    
                    ui.button('关闭', on_click=dialog.close).classes('glass-btn q-mt-md')
                
                dialog.open()
            elif not results:
                ui.notify('未发现新文件', type='info')
    
    def on_kb_product_change(self):
        """产品选择变化时更新显示"""
        if not hasattr(self, 'kb_product_select') or not self.kb_product_select.value:
            return
        
        product_id = self.kb_product_select.value
        product = hospital_service.get_product(product_id)
        
        if not product:
            return
        
        # 填充产品信息到编辑表单
        self.kb_product_name.value = product.name
        self.kb_product_category.value = product.category
        self.kb_product_desc.value = product.description
        self.kb_product_features.value = ', '.join(product.key_features)
        self.kb_product_indications.value = ', '.join(product.indications)
        self.kb_product_notes.value = product.notes
        
        # 刷新产品详情和附件列表
        self.refresh_kb_product_detail()
    
    def refresh_kb_product_detail(self):
        """刷新产品详情和附件列表"""
        if not hasattr(self, 'kb_product_detail_container') or not hasattr(self, 'kb_product_select'):
            return
        
        product_id = self.kb_product_select.value
        if not product_id:
            return
        
        product = hospital_service.get_product(product_id)
        if not product:
            return
        
        self.kb_product_detail_container.clear()
        
        with self.kb_product_detail_container:
            # 产品基本信息卡片
            with ui.card().classes('glass-card q-pa-md q-mb-md'):
                with ui.row().classes('w-full items-center justify-between'):
                    ui.label(f'📦 {product.name}').classes('text-h6 text-white')
                    ui.button('🔄 刷新', on_click=self.refresh_kb_product_detail).props('flat dense size=sm color=accent')
                
                if product.category:
                    ui.label(f'类别: {product.category}').classes('text-white q-mt-sm')
                if product.description:
                    ui.label(f'描述: {product.description}').classes('text-secondary q-mt-sm')
                if product.key_features:
                    ui.label(f'特性: {", ".join(product.key_features)}').classes('text-caption q-mt-sm')
                if product.indications:
                    ui.label(f'适应症: {", ".join(product.indications)}').classes('text-caption q-mt-sm')
            
            # 附件列表卡片
            with ui.card().classes('glass-card q-pa-md'):
                ui.label('📎 产品资料附件').classes('text-h6 text-white q-mb-md')
                
                # 获取附件列表
                attachments = hospital_service.get_product_attachments(product_id)
                
                if not attachments:
                    ui.label('暂无附件，请在左侧上传产品资料').classes('text-secondary q-pa-md')
                else:
                    ui.label(f'共 {len(attachments)} 个附件').classes('text-white q-mb-md')
                    
                    for idx, attachment in enumerate(attachments, 1):
                        with ui.card().classes('glass-list-item q-pa-md q-mb-sm'):
                            with ui.row().classes('w-full items-center justify-between'):
                                with ui.column().classes('col-grow'):
                                    file_icons = {
                                        'ppt': '📊', 'pptx': '📊',
                                        'doc': '📄', 'docx': '📄',
                                        'txt': '📝', 'pdf': '📕'
                                    }
                                    file_type = attachment.get('file_type', '').lower()
                                    icon = file_icons.get(file_type, '📎')
                                    
                                    ui.label(f"{idx}. {icon} {attachment.get('filename', '')}").classes('text-white font-bold')
                                    ui.label(f"上传时间: {attachment.get('upload_time', '')[:19]}").classes('text-caption text-secondary')
                                    ui.label(f"类型: {file_type.upper()} | 路径: {attachment.get('filepath', '')}").classes('text-caption text-secondary')
                                
                                with ui.row().classes('q-gutter-sm'):
                                    ui.button(
                                        '查看',
                                        on_click=lambda a=attachment: self.view_kb_attachment(a)
                                    ).props('flat dense size=sm color=primary')
                                    ui.button(
                                        '删除',
                                        on_click=lambda a=attachment: self.delete_kb_attachment_confirm(product_id, a)
                                    ).props('flat dense size=sm color=negative')
    
    def on_kb_file_upload(self, e):
        """处理文件上传"""
        if not hasattr(self, 'kb_product_select') or not self.kb_product_select.value:
            ui.notify('请先选择产品', type='warning')
            # 清空上传组件
            if hasattr(self, 'kb_file_upload'):
                self.kb_file_upload.reset()
            return
        
        product_id = self.kb_product_select.value
        
        try:
            # 创建产品附件目录
            from pathlib import Path
            attachments_dir = Path('data/product_attachments') / product_id
            attachments_dir.mkdir(parents=True, exist_ok=True)
            
            # 保存文件
            filename = e.name
            filepath = attachments_dir / filename
            
            with open(filepath, 'wb') as f:
                f.write(e.content.read())
            
            # 获取文件类型
            file_type = filename.split('.')[-1] if '.' in filename else 'unknown'
            
            print(f"文件已保存: {filepath}")
            
            # 添加到产品附件列表
            success = hospital_service.add_product_attachment(
                product_id=product_id,
                filename=filename,
                filepath=str(filepath),
                file_type=file_type
            )
            
            if success:
                ui.notify(f'✓ 文件 {filename} 上传成功', type='positive')
                
                # 使用延迟刷新确保数据已保存
                ui.timer(0.1, lambda: self.refresh_kb_product_detail(), once=True)
                
                # 清空上传组件
                self.kb_file_upload.reset()
            else:
                ui.notify('上传失败：无法保存到数据库', type='negative')
        
        except Exception as ex:
            ui.notify(f'上传失败: {str(ex)}', type='negative')
            print(f"上传错误: {ex}")
            # 清空上传组件
            if hasattr(self, 'kb_file_upload'):
                self.kb_file_upload.reset()
    
    def update_kb_product(self):
        """更新产品信息"""
        if not hasattr(self, 'kb_product_select') or not self.kb_product_select.value:
            ui.notify('请先选择产品', type='warning')
            return
        
        product_id = self.kb_product_select.value
        
        if not self.kb_product_name.value:
            ui.notify('产品名称不能为空', type='warning')
            return
        
        features = [f.strip() for f in self.kb_product_features.value.split(',') if f.strip()]
        indications = [i.strip() for i in self.kb_product_indications.value.split(',') if i.strip()]
        
        success = hospital_service.update_product(
            product_id,
            {
                'name': self.kb_product_name.value,
                'category': self.kb_product_category.value,
                'description': self.kb_product_desc.value,
                'key_features': features,
                'indications': indications,
                'notes': self.kb_product_notes.value
            }
        )
        
        if success:
            ui.notify('产品信息已更新', type='positive')
            
            # 更新选择框显示
            products = hospital_service.list_products()
            product_options = {p['product_id']: p['name'] for p in products}
            self.kb_product_select.set_options(product_options)
            
            # 清空表单
            self.clear_kb_product_form()
        else:
            ui.notify('更新失败', type='negative')
    
    def view_kb_attachment(self, attachment: dict):
        """查看附件内容"""
        filepath = attachment.get('filepath', '')
        filename = attachment.get('filename', '')
        file_type = attachment.get('file_type', '').lower()
        
        try:
            from pathlib import Path
            import os
            
            # 读取文件内容
            if file_type == 'txt':
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                with ui.dialog() as dialog, ui.card().classes('glass-card').style('min-width: 700px; max-height: 80vh;'):
                    ui.label(f'📝 {filename}').classes('text-h6 text-white q-mb-md')
                    ui.textarea(value=content).classes('w-full').style('min-height: 400px; font-family: monospace;').props('readonly')
                    ui.button('关闭', on_click=dialog.close).classes('glass-btn q-mt-md')
                dialog.open()
            
            else:
                # PPT, DOC, PDF等文件，使用系统默认程序打开
                ui.notify(f'正在打开文件: {filename}', type='info')
                
                # Windows系统使用os.startfile
                if os.name == 'nt':
                    os.startfile(filepath)
                else:
                    # Linux/Mac使用xdg-open或open
                    import subprocess
                    if sys.platform == 'darwin':
                        subprocess.Popen(['open', filepath])
                    else:
                        subprocess.Popen(['xdg-open', filepath])
        
        except Exception as e:
            ui.notify(f'无法打开文件: {str(e)}', type='negative')
            print(f"打开文件错误: {e}")
    
    def delete_kb_attachment_confirm(self, product_id: str, attachment: dict):
        """确认删除附件"""
        with ui.dialog() as dialog, ui.card().classes('glass-card'):
            ui.label('⚠️ 确认删除').classes('text-h6 text-white q-mb-md')
            ui.label(f'确定要删除附件 "{attachment.get("filename")}" 吗？').classes('text-white')
            ui.label('此操作不可逆，请谨慎操作！').classes('text-negative q-mt-sm font-bold')
            
            with ui.row().classes('w-full justify-end q-mt-lg q-gutter-sm'):
                ui.button('取消', on_click=dialog.close).classes('glass-btn')
                ui.button(
                    '确认删除',
                    on_click=lambda: self.delete_kb_attachment_execute(product_id, attachment.get('filepath'), dialog)
                ).props('color=negative')
        
        dialog.open()
    
    def delete_kb_attachment_execute(self, product_id: str, filepath: str, dialog):
        """执行删除附件"""
        success = hospital_service.remove_product_attachment(product_id, filepath)
        
        if success:
            ui.notify('附件已删除', type='positive')
            dialog.close()
            self.refresh_kb_product_detail()
        else:
            ui.notify('删除失败', type='negative')
    
    def render_knowledge_panel(self, category: str):
        """渲染知识库面板"""
        # 添加/编辑表单
        with ui.card().classes('glass-card p-4 mb-4'):
            form_label = ui.label('📚 添加知识').classes('text-subtitle1 font-bold text-white mb-3')

            with ui.grid().classes('w-full gap-3 grid-cols-2'):
                title_input = ui.input(label='标题').classes('w-full')
                keywords_input = ui.input(label='关键词 (逗号分隔)').classes('w-full')
                source_input = ui.input(label='来源').classes('w-full')

            content_input = ui.textarea(label='内容').classes('w-full')
            notes_input = ui.textarea(label='📌 备注').classes('w-full')

            current_edit_id = {'value': None}

            def reset_form():
                title_input.value = ''
                content_input.value = ''
                keywords_input.value = ''
                source_input.value = ''
                notes_input.value = ''
                current_edit_id['value'] = None
                form_label.text = '📚 添加知识'
                save_btn.text = '💾 保存'

            def save_knowledge():
                if not title_input.value:
                    ui.notify('标题不能为空', type='warning')
                    return

                knowledge_service.create_item(
                    category=category,
                    title=title_input.value,
                    content=content_input.value,
                    keywords=[k.strip() for k in keywords_input.value.split(',') if k.strip()],
                    source=source_input.value,
                    notes=notes_input.value,
                    item_id=current_edit_id['value']
                )
                action = "更新" if current_edit_id['value'] else "添加"
                ui.notify(f'知识已{action}', type='positive')
                reset_form()
                refresh_list()

            with ui.row().classes('gap-3 mt-3'):
                save_btn = ui.button('💾 保存', on_click=save_knowledge).props('color=primary')
                ui.button('🔄 重置', on_click=reset_form).props('color=secondary')

        # 知识列表
        with ui.card().classes('glass-card p-4'):
            ui.label('📋 知识列表').classes('text-subtitle1 font-bold text-white mb-3')
            list_container = ui.column().classes('w-full')

            def load_for_edit(item):
                title_input.value = item.get('title', '')
                content_input.value = item.get('content', '')
                keywords_input.value = ', '.join(item.get('keywords', []))
                source_input.value = item.get('source', '')
                notes_input.value = item.get('notes', '')
                current_edit_id['value'] = item['item_id']
                form_label.text = '✏️ 编辑知识'
                save_btn.text = '✏️ 更新'
                ui.notify('已加载知识条目', type='info')

            def delete_item(item_id):
                knowledge_service.delete_item(item_id, category)
                ui.notify('知识条目已删除', type='positive')
                if current_edit_id['value'] == item_id:
                    reset_form()
                refresh_list()

            def refresh_list():
                list_container.clear()
                with list_container:
                    items = knowledge_service.list_items(category)
                    if not items:
                        ui.label('暂无知识条目，点击上方表单添加').classes('text-caption text-grey')
                        return

                    cols = 3 if len(items) > 6 else 2
                    with ui.grid().classes(f'w-full gap-3 grid-cols-{cols}'):
                        for item in items:
                            with ui.card().classes('glass-card-secondary p-3'):
                                with ui.row().classes('w-full items-center justify-between mb-2'):
                                    ui.label(item['title']).classes('text-white font-bold text-body1')
                                    if item.get('source'):
                                        ui.label(f'📖 {item["source"]}').classes('text-caption text-blue-4')
                                if item.get('content'):
                                    content_short = item['content'][:80] + '...' if len(item['content']) > 80 else item['content']
                                    ui.label(content_short).classes('text-caption text-grey mb-2')
                                if item.get('keywords'):
                                    keywords_str = ', '.join(item['keywords'][:3])
                                    ui.label(f'🏷️ {keywords_str}').classes('text-caption text-amber-4 mb-2')
                                with ui.row().classes('gap-2'):
                                    ui.button('✏️', on_click=lambda e, i=item: load_for_edit(i)).props('flat dense size=sm color=primary')
                                    ui.button('🗑️', on_click=lambda e, i=item['item_id']: delete_item(i)).props('flat dense size=sm color=negative')

            refresh_list()
    
    def render_reports(self):
        """渲染报告中心页面"""
        ui.label('📄 报告中心').classes('page-title')
        
        with ui.row().classes('w-full q-gutter-md q-mb-lg'):
            ui.button('📅 生成周报', on_click=self.generate_weekly_report).classes('glass-btn')
            ui.button('📊 生成月报', on_click=self.generate_monthly_report).classes('glass-btn')
            ui.button('📋 生成行动单', on_click=self.generate_action).classes('glass-btn-secondary')
        
        with ui.card().classes('glass-card w-full q-pa-lg'):
            ui.label('历史报告').classes('text-h6 text-white q-mb-md')
            
            self.reports_container = ui.column().classes('w-full')
            self.refresh_reports_list()
    
    def refresh_reports_list(self):
        """刷新报告列表"""
        if not hasattr(self, 'reports_container'):
            return
        
        self.reports_container.clear()
        with self.reports_container:
            reports = reporting_service.list_reports()
            
            if not reports:
                ui.label('暂无报告').classes('text-secondary')
                return
            
            for report in reports[:20]:
                with ui.card().classes('glass-list-item q-pa-md q-mb-sm'):
                    with ui.row().classes('w-full items-center justify-between'):
                        # 左侧：报告信息
                        with ui.column().classes('col-grow'):
                            type_icons = {
                                'weekly': '📅 周报',
                                'monthly': '📊 月报',
                                'daily': '📋 行动单',
                                'visit': '✅ 拜访',
                                'preparation': '📝 准备',
                                'doctor': '👨‍⚕️ 医生',
                            }
                            type_label = type_icons.get(report['type'], '📄 其他')
                            ui.label(f"{type_label} - {report['filename']}").classes('text-white font-bold')
                        
                        # 右侧：操作按钮
                        with ui.row().classes('q-gutter-sm'):
                            ui.button('查看', on_click=lambda r=report: self.view_report(r['path'])).props('flat dense size=sm color=primary')
                            ui.button('编辑', on_click=lambda r=report: self.edit_report(r)).props('flat dense size=sm color=secondary')
                            
                            # 周报和月报显示导出按钮
                            if report['type'] in ['weekly', 'monthly']:
                                ui.button('📱 导出HTML', on_click=lambda r=report: self.export_report_html(r)).props('flat dense size=sm color=accent')
                            
                            ui.button('删除', on_click=lambda r=report: self.delete_report_confirm(r)).props('flat dense size=sm color=negative')
    
    def edit_report(self, report: dict):
        """编辑报告"""
        content = reporting_service.get_report_content(report['path'])
        if not content:
            ui.notify('无法读取报告内容', type='negative')
            return
        
        with ui.dialog() as dialog, ui.card().classes('glass-card w-full').style('max-width: 900px; max-height: 80vh;'):
            ui.label(f'编辑报告: {report["filename"]}').classes('text-h6 text-white q-mb-md')
            
            # 编辑器
            editor = ui.textarea(
                label='报告内容（Markdown格式）',
                value=content
            ).classes('w-full').style('min-height: 400px; font-family: monospace;')
            
            # 按钮
            with ui.row().classes('w-full justify-end q-mt-md q-gutter-sm'):
                ui.button('取消', on_click=dialog.close).classes('glass-btn')
                ui.button('保存', on_click=lambda: self.save_report_edit(report['path'], editor.value, dialog)).classes('glass-btn-secondary')
        
        dialog.open()
    
    def save_report_edit(self, report_path: str, content: str, dialog):
        """保存报告编辑"""
        if reporting_service.update_report(report_path, content):
            ui.notify('报告已更新', type='positive')
            dialog.close()
            self.refresh_reports_list()
        else:
            ui.notify('保存失败', type='negative')
    
    def delete_report_confirm(self, report: dict):
        """确认删除报告"""
        with ui.dialog() as dialog, ui.card().classes('glass-card'):
            ui.label('⚠️ 确认删除').classes('text-h6 text-white q-mb-md')
            ui.label(f'确定要删除报告 "{report["filename"]}" 吗？').classes('text-white')
            ui.label('此操作不可逆，请谨慎操作！').classes('text-negative q-mt-sm font-bold')
            
            with ui.row().classes('w-full justify-end q-mt-lg q-gutter-sm'):
                ui.button('取消', on_click=dialog.close).classes('glass-btn')
                ui.button('确认删除', on_click=lambda: self.delete_report_execute(report['path'], dialog)).props('color=negative')
        
        dialog.open()
    
    def delete_report_execute(self, report_path: str, dialog):
        """执行删除报告"""
        if reporting_service.delete_report(report_path):
            ui.notify('报告已删除', type='positive')
            dialog.close()
            self.refresh_reports_list()
        else:
            ui.notify('删除失败', type='negative')
    
    def export_report_html(self, report: dict):
        """导出报告为 HTML"""
        try:
            html_path = reporting_service.export_report_to_html(report['path'])
            ui.notify(f'已导出为 HTML: {Path(html_path).name}', type='positive')
            
            # 显示导出成功对话框
            with ui.dialog() as dialog, ui.card().classes('glass-card'):
                ui.label('✅ 导出成功').classes('text-h6 text-white q-mb-md')
                ui.label(f'文件位置: {html_path}').classes('text-white')
                ui.label('您可以通过以下方式在手机上查看：').classes('text-secondary q-mt-md')
                with ui.column().classes('q-mt-sm q-ml-md'):
                    ui.label('1. 将 HTML 文件传输到手机').classes('text-white')
                    ui.label('2. 使用手机浏览器打开').classes('text-white')
                    ui.label('3. 或通过微信/QQ等发送给自己').classes('text-white')
                
                with ui.row().classes('w-full justify-end q-mt-lg'):
                    ui.button('知道了', on_click=dialog.close).classes('glass-btn')
            
            dialog.open()
            
        except Exception as e:
            ui.notify(f'导出失败: {str(e)}', type='negative')
    
    def render_ai_analysis(self):
        """渲染 AI 数据分析页面"""
        from modules.ai_analysis.ui import render_ai_analysis_page
        render_ai_analysis_page()
    
    def render_customer_tracking(self):
        """渲染客户追踪管理页面"""
        from modules.customer_tracking.ui import render_customer_tracking_page
        render_customer_tracking_page()
    
    def render_settings(self):
        """渲染设置页面"""
        ui.label('⚙️ 系统设置').classes('page-title')

        config = file_manager.get_config()

        with ui.card().classes('glass-card w-full q-pa-lg'):
            ui.label('🤖 AI 设置').classes('section-title')
            ui.label('配置 AI 服务后，可在 AI 助手、数据分析、智能填表中获得专业建议').classes('text-caption text-grey q-mb-md')

            self.ai_enabled_switch = ui.switch(
                '启用 AI 功能',
                value=config.get('ai_enabled', False),
                on_change=self.toggle_ai
            )

            # Provider Selection
            self.ai_provider = ui.select(
                label='AI 服务提供商',
                options={'deepseek': 'DeepSeek', 'xiaomi': '小米 MiMo'},
                value=config.get('ai_provider', 'deepseek')
            ).classes('w-full glass-input')

            # DeepSeek Config
            with ui.column().classes('w-full q-mt-md').bind_visibility_from(self.ai_provider, 'value', value='deepseek'):
                with ui.card().classes('glass-card-secondary q-pa-md w-full'):
                    ui.label('DeepSeek 配置').classes('text-caption text-grey q-mb-sm')
                    self.deepseek_key = ui.input(
                        label='API Key',
                        value=config.get('deepseek_api_key', ''),
                        password=True,
                        password_toggle_button=True
                    ).classes('w-full glass-input')
                    self.deepseek_model = ui.input(
                        label='模型名称',
                        value=config.get('deepseek_model', 'deepseek-chat')
                    ).classes('w-full glass-input')

            # Xiaomi Config
            with ui.column().classes('w-full q-mt-md').bind_visibility_from(self.ai_provider, 'value', value='xiaomi'):
                with ui.card().classes('glass-card-secondary q-pa-md w-full'):
                    ui.label('小米 MiMo 配置').classes('text-caption text-grey q-mb-sm')
                    self.xiaomi_key = ui.input(
                        label='API Key',
                        value=config.get('xiaomi_api_key', ''),
                        password=True,
                        password_toggle_button=True
                    ).classes('w-full glass-input')
                    self.xiaomi_model = ui.input(
                        label='模型名称',
                        value=config.get('xiaomi_model', 'mimo-v2-flash')
                    ).classes('w-full glass-input')

            ui.button('💾 保存设置', on_click=self.save_settings).classes('glass-btn q-mt-md')

        with ui.grid().classes('w-full gap-4 mt-4 grid-cols-1 md:grid-cols-2'):
            with ui.card().classes('glass-card q-pa-lg'):
                ui.label('📦 数据管理').classes('section-title')
                ui.label('将所有本地数据打包备份到指定目录').classes('text-caption text-grey q-mb-md')
                ui.button('🔄 备份数据', on_click=self.backup_data).classes('glass-btn-secondary')

            with ui.card().classes('glass-card q-pa-lg'):
                ui.label('ℹ️ 关于').classes('section-title')
                ui.label('查看系统功能介绍与使用指南').classes('text-caption text-grey q-mb-md')
                ui.button('📖 查看使用说明', on_click=self.show_about_dialog).classes('glass-btn-secondary')
    
    def render_ai_chat(self):
        """渲染 AI 对话助手页面"""
        ui.label('🤖 AI 助手').classes('page-title')
        
        if not ai_integration.is_enabled:
            with ui.card().classes('glass-card w-full q-pa-lg'):
                ui.label('⚠️ AI 功能未启用').classes('text-h6 text-white')
                ui.label('请在系统设置中配置 DeepSeek API Key 并开启 AI 功能').classes('text-secondary')
                ui.button('前往设置', on_click=lambda: self.navigate('settings')).classes('glass-btn q-mt-md')
            return
        
        # 快捷分析按钮
        with ui.row().classes('w-full q-gutter-md q-mb-lg'):
            ui.button('🔍 分析今日拜访', on_click=self.analyze_today_visits).classes('glass-btn')
            ui.button('📈 成长建议', on_click=self.get_growth_suggestions).classes('glass-btn')
            ui.button('💡 查缺补漏', on_click=self.find_gaps).classes('glass-btn-secondary')
        
        with ui.row().classes('w-full q-gutter-md'):
            # 左侧：会话列表
            with ui.card().classes('glass-card col-3 q-pa-lg'):
                ui.label('会话列表').classes('text-h6 text-white q-mb-md')
                ui.button('+ 新对话', on_click=self.new_chat_session).classes('glass-btn w-full q-mb-md')
                
                self.sessions_container = ui.column().classes('w-full')
                self.refresh_sessions_list()
            
            # 右侧：对话区域
            with ui.card().classes('glass-card col-8 q-pa-lg'):
                self.chat_container = ui.column().classes('w-full')
                self.chat_messages_container = ui.column().classes('w-full').style('height: 400px; overflow-y: auto')
                
                # 数据选择和文件上传工具栏
                with ui.expansion("📎 添加上下文数据", icon="attach_file").classes('w-full mb-2'):
                    with ui.column().classes('w-full gap-2 p-2'):
                        # 医院选择
                        hospitals = hospital_service.list_hospitals()
                        if hospitals:
                            hospital_options = {h["name"]: h["hospital_id"] for h in hospitals}
                            self.selected_hospital = ui.select(
                                options=list(hospital_options.keys()),
                                label="选择医院（可选）",
                                clearable=True
                            ).classes('w-full')
                            ui.button("添加医院数据到对话", 
                                     on_click=lambda: self.add_hospital_context(hospital_options.get(self.selected_hospital.value)),
                                     icon="add").props("flat size=sm color=primary")
                        
                        # 医生选择
                        from core.file_manager import file_manager
                        doctor_files = list(file_manager.doctors_dir.glob("*.json"))
                        if doctor_files:
                            doctors = []
                            for f in doctor_files[:50]:
                                data = file_manager.read_json(f)
                                if data:
                                    doctors.append({"id": data.get("doctor_id"), "name": data.get("name"), "hospital": data.get("hospital", "")})
                            
                            if doctors:
                                doctor_options = {f"{d['name']} ({d['hospital']})"[:50]: d["id"] for d in doctors}
                                self.selected_doctor = ui.select(
                                    options=list(doctor_options.keys()),
                                    label="选择医生（可选）",
                                    clearable=True
                                ).classes('w-full')
                                ui.button("添加医生数据到对话", 
                                         on_click=lambda: self.add_doctor_context(doctor_options.get(self.selected_doctor.value)),
                                         icon="add").props("flat size=sm color=primary")
                        
                        # 文件上传
                        ui.label("上传文件（Word/Excel/TXT）").classes('text-sm font-bold mt-2')
                        self.file_upload = ui.upload(
                            label="选择文件",
                            on_upload=self.handle_file_upload,
                            auto_upload=True
                        ).props('accept=".doc,.docx,.xls,.xlsx,.txt,.pdf"').classes('w-full')
                        ui.label("支持格式：.doc, .docx, .xls, .xlsx, .txt, .pdf").classes('text-xs text-gray-500')
                
                # Context Toolbar（保留原有的快捷按钮）
                with ui.row().classes('w-full q-px-sm items-center q-gutter-x-sm h-8 q-mb-xs'):
                    ui.label('📎 快捷引用:').classes('text-grey-4 text-caption q-mr-sm')
                    ui.button('今日数据', on_click=self.add_context_daily).props('flat dense size=sm color=accent no-caps')
                    ui.button('本周周报', on_click=self.add_context_weekly).props('flat dense size=sm color=accent no-caps')
                    ui.button('待办事项', on_click=self.add_context_tasks).props('flat dense size=sm color=accent no-caps')
                    ui.button('数据概览', on_click=self.add_context_database).props('flat dense size=sm color=accent no-caps')
                    ui.button('产品资料', on_click=self.show_product_attachment_dialog).props('flat dense size=sm color=purple no-caps')
                
                with ui.row().classes('w-full items-end'):
                    self.chat_input = ui.textarea(label='输入消息...').classes('col-10 glass-input').props('autogrow rows=1')
                    ui.button('发送', on_click=self.send_chat_message).classes('glass-btn col-2 h-10')
    
    async def analyze_today_visits(self):
        """分析今日拜访"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        # 获取今日拜访记录
        visits = visit_summary_service.list_visits(limit=10)
        today_visits = [v for v in visits if v.get('visit_date', '') == today]
        
        # 获取今日反思
        reflection = personal_growth_service.get_reflection(today)
        
        if not today_visits and not reflection:
            ui.notify('今日暂无拜访记录或个人总结', type='info')
            return
        
        # 构建分析请求
        visits_text = ""
        for v in today_visits:
            visits_text += f"""
### 拜访记录
- 话题: {v.get('key_topics', '')}
- 客户关注: {v.get('doctor_concerns', '')}
- 异议: {v.get('objections', '')}
- 我的回应: {v.get('responses', '')}
- 效果: {v.get('response_effectiveness', 3)}/5
- 新发现: {v.get('new_insights', '')}
"""
        
        reflection_text = ""
        if reflection:
            reflection_text = f"""
### 个人总结
- 焦虑来源: {reflection.anxiety_source}
- 成就: {reflection.achievement}
- 弱点: {reflection.weakness}
- 在逃避什么: {reflection.avoidance}
- 突破点: {reflection.breakthrough}
- 学习: {reflection.learning}
"""
        
        prompt = f"""请分析我今天的拜访情况，帮我发现以下内容：

{visits_text}

{reflection_text}

请帮我分析：
1. 今日做得好的地方
2. 可以改进的地方
3. 我可能遗漏了什么（没有总结到的）
4. 下次如何做得更好
5. 建议学习的方向

请给出具体、可操作的建议。"""
        
        ui.notify('正在进行 AI 分析，请稍候...', type='info')
        
        # 发送到 AI
        if hasattr(self, 'current_session_id') and self.current_session_id:
            response = await ai_chat_service.chat(self.current_session_id, prompt)
        else:
            session = ai_chat_service.new_session("今日拜访分析")
            self.current_session_id = session.session_id
            response = await ai_chat_service.chat(session.session_id, prompt)
        
        # 显示结果
        with ui.dialog() as dialog, ui.card().classes('glass-card w-full').style('max-width: 800px; max-height: 80vh; overflow-y: auto'):
            ui.label('🔍 今日拜访分析').classes('text-h5 text-white q-mb-md')
            ui.markdown(response)
            with ui.row().classes('w-full justify-end q-mt-md'):
                ui.button('关闭', on_click=dialog.close).classes('glass-btn')
        dialog.open()
        
        self.refresh_sessions_list()
    
    async def get_growth_suggestions(self):
        """获取成长建议"""
        # 获取最近反思
        reflections = personal_growth_service.list_reflections(limit=7)
        
        if not reflections:
            ui.notify('暂无反思记录，建议先记录一些个人总结', type='info')
            return
        
        # 构建分析
        reflection_summary = ""
        for r in reflections[:7]:
            reflection_summary += f"[{r.get('date', '')}] 弱点:{r.get('weakness', '')[:30]} 学习:{r.get('learning', '')[:30]}\n"
        
        prompt = f"""基于我最近一周的反思记录，分析我的成长情况并给出建议：

{reflection_summary}

请分析：
1. 我反复出现的问题/弱点
2. 进步的地方
3. 需要重点加强的技能
4. 推荐的学习资源或方法
5. 本周目标建议"""
        
        ui.notify('AI 正在分析您的成长记录...', type='info')
        
        response = await ai_integration._make_request([
            {"role": "system", "content": "你是专业的职业成长教练，提供具体可行的成长建议。"},
            {"role": "user", "content": prompt}
        ], temperature=0.6, max_tokens=800)
        
        with ui.dialog() as dialog, ui.card().classes('glass-card w-full').style('max-width: 800px; max-height: 80vh; overflow-y: auto'):
            ui.label('📈 成长建议').classes('text-h5 text-white q-mb-md')
            ui.markdown(response or "AI 分析失败，请稍后重试")
            with ui.row().classes('w-full justify-end q-mt-md'):
                ui.button('关闭', on_click=dialog.close).classes('glass-btn')
        dialog.open()

    # ==================== 快捷上下文引位方法 ====================
    
    async def add_context_daily(self):
        """引用今日数据"""
        if not hasattr(self, 'chat_input'): return
        content = await summary_export_service.export_recent_days(1, use_ai=False)
        self.chat_input.value = (self.chat_input.value or "") + f"\n\n【引用：今日数据】\n{content}\n"
        ui.notify('已引用今日数据', type='positive')

    async def add_context_weekly(self):
        """引用周报数据"""
        if not hasattr(self, 'chat_input'): return
        content = await summary_export_service.export_weekly_summary(use_ai=False)
        self.chat_input.value = (self.chat_input.value or "") + f"\n\n【引用：本周周报】\n{content}\n"
        ui.notify('已引用周报数据', type='positive')
        
    def add_context_tasks(self):
        """引用待办事项"""
        if not hasattr(self, 'chat_input'): return
        # 懒加载防循环引用
        from core.analyzer import analyzer
        tasks = analyzer.get_pending_tasks()
        if not tasks:
            ui.notify('暂无待办事项', type='info')
            return
        task_str = "\n".join([f"- {t}" for t in tasks])
        self.chat_input.value = (self.chat_input.value or "") + f"\n\n【引用：待办事项】\n{task_str}\n"
        ui.notify('已引用待办事项', type='positive')
    
    def add_context_database(self):
        """引用数据库统计"""
        if not hasattr(self, 'chat_input'): return
        doctors_count = len(file_manager.list_files(file_manager.doctors_dir))
        visits_count = len(file_manager.list_files(file_manager.visits_dir))
        contacts_dir = file_manager.data_dir / "contacts"
        contacts_count = len(file_manager.list_files(contacts_dir)) if contacts_dir.exists() else 0
        
        stats = f"""
数据概览：
- 医生档案: {doctors_count}
- 拜访记录: {visits_count}
- 其他联系人: {contacts_count}
"""
        self.chat_input.value = (self.chat_input.value or "") + f"\n\n【引用：数据库统计】\n{stats}\n"
        ui.notify('已引用数据库统计', type='positive')
    
    def show_product_attachment_dialog(self):
        """显示产品附件选择对话框"""
        products = hospital_service.list_products()
        
        if not products:
            ui.notify('暂无产品，请先添加产品', type='warning')
            return
        
        with ui.dialog() as dialog, ui.card().classes('glass-card').style('min-width: 600px; max-height: 80vh;'):
            ui.label('📎 选择产品资料').classes('text-h6 text-white q-mb-md')
            ui.label('选择要引用到对话中的产品资料（仅TXT文件内容会被AI读取）').classes('text-caption text-secondary q-mb-md')
            
            for product in products:
                product_id = product['product_id']
                attachments = hospital_service.get_product_attachments(product_id)
                
                if attachments:
                    with ui.expansion(f"📦 {product['name']} ({len(attachments)}个附件)").classes('w-full glass-expansion'):
                        for attachment in attachments:
                            filename = attachment.get('filename', '')
                            file_type = attachment.get('file_type', '').lower()
                            
                            with ui.row().classes('w-full items-center justify-between q-pa-sm'):
                                file_icons = {
                                    'txt': '📝', 'pdf': '📕',
                                    'ppt': '📊', 'pptx': '📊',
                                    'doc': '📄', 'docx': '📄'
                                }
                                icon = file_icons.get(file_type, '📎')
                                
                                ui.label(f"{icon} {filename}").classes('text-white')
                                
                                # 只有TXT文件可以引用到对话
                                if file_type == 'txt':
                                    ui.button(
                                        '引用到对话',
                                        on_click=lambda a=attachment, d=dialog: self.add_attachment_to_chat(a, d)
                                    ).props('flat dense size=sm color=primary')
                                else:
                                    ui.label('(不支持AI读取)').classes('text-caption text-secondary')
            
            ui.button('关闭', on_click=dialog.close).classes('glass-btn q-mt-md')
        
        dialog.open()
    
    def add_attachment_to_chat(self, attachment: dict, dialog):
        """将附件内容添加到对话"""
        if not hasattr(self, 'chat_input'):
            return
        
        filepath = attachment.get('filepath', '')
        filename = attachment.get('filename', '')
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 限制内容长度，避免token消耗过多
            if len(content) > 5000:
                content = content[:5000] + "\n\n...(内容过长，已截断)"
            
            self.chat_input.value = (self.chat_input.value or "") + f"\n\n【引用：{filename}】\n{content}\n"
            ui.notify(f'已引用 {filename}', type='positive')
            dialog.close()
        
        except Exception as e:
            ui.notify(f'读取文件失败: {str(e)}', type='negative')
    
    def add_hospital_context(self, hospital_id: str):
        """添加医院数据到对话"""
        if not hospital_id or not hasattr(self, 'chat_input'):
            ui.notify('请先选择医院', type='warning')
            return
        
        # 获取医院数据
        hospital_data = hospital_service.get_hospital(hospital_id)
        if not hospital_data:
            ui.notify('医院数据不存在', type='negative')
            return
        
        # 获取科室列表
        departments = hospital_service.list_departments(hospital_id)
        dept_names = [d['name'] for d in departments[:10]]
        
        # 获取产品关联
        from modules.product_association.service import product_association_service
        associations = product_association_service.query_by_hospital(hospital_id)
        product_names = list(set([a.product_name for a in associations[:10]]))
        
        context = f"""
【医院数据】
医院名称：{hospital_data.name}
医院等级：{hospital_data.level}
地址：{hospital_data.address}
科室数量：{len(departments)}
主要科室：{', '.join(dept_names[:5])}
使用产品：{', '.join(product_names[:5])}
备注：{hospital_data.notes[:100]}
"""
        self.chat_input.value = (self.chat_input.value or "") + f"\n{context}\n"
        ui.notify(f'已添加医院"{hospital_data.name}"的数据', type='positive')
    
    def add_doctor_context(self, doctor_id: str):
        """添加医生数据到对话"""
        if not doctor_id or not hasattr(self, 'chat_input'):
            ui.notify('请先选择医生', type='warning')
            return
        
        # 获取医生数据
        doctor_data = doctor_service.get_doctor(doctor_id)
        if not doctor_data:
            ui.notify('医生数据不存在', type='negative')
            return
        
        # 获取最近拜访记录
        recent_visits = []
        visits_dir = file_manager.visits_dir
        if visits_dir.exists():
            visit_files = sorted(visits_dir.glob("*.json"), reverse=True)
            for visit_file in visit_files[:20]:
                visit_data = file_manager.read_json(visit_file)
                if visit_data and visit_data.get("doctor_id") == doctor_id:
                    recent_visits.append({
                        "date": visit_data.get("visit_date"),
                        "topics": visit_data.get("key_topics", "")[:50],
                        "effectiveness": visit_data.get("response_effectiveness", 3)
                    })
                    if len(recent_visits) >= 3:
                        break
        
        visits_text = "\n".join([f"  - {v['date']}: {v['topics']} (效果{v['effectiveness']}/5)" for v in recent_visits]) if recent_visits else "  暂无拜访记录"
        
        context = f"""
【医生数据】
姓名：{doctor_data.name}
医院：{doctor_data.hospital}
科室：{doctor_data.department}
职称：{doctor_data.title}
关系阶段：{doctor_data.relationship_stage}
决策风格：{doctor_data.decision_style or '未知'}
兴趣领域：{', '.join(doctor_data.interests[:5])}
最近拜访：
{visits_text}
备注：{doctor_data.notes[:100]}
"""
        self.chat_input.value = (self.chat_input.value or "") + f"\n{context}\n"
        ui.notify(f'已添加医生"{doctor_data.name}"的数据', type='positive')
    
    def handle_file_upload(self, e):
        """处理文件上传"""
        import io
        
        try:
            file_content = e.content.read()
            file_name = e.name
            file_ext = file_name.split('.')[-1].lower()
            
            # 解析文件内容
            text_content = ""
            
            if file_ext == 'txt':
                # 文本文件
                text_content = file_content.decode('utf-8', errors='ignore')
            
            elif file_ext in ['doc', 'docx']:
                # Word文档
                try:
                    import docx
                    doc = docx.Document(io.BytesIO(file_content))
                    text_content = "\n".join([para.text for para in doc.paragraphs])
                except ImportError:
                    ui.notify('需要安装python-docx库来读取Word文档: pip install python-docx', type='warning')
                    text_content = f"[Word文档: {file_name}，无法读取内容，请安装python-docx]"
                except Exception as ex:
                    text_content = f"[Word文档: {file_name}，读取失败: {str(ex)}]"
            
            elif file_ext in ['xls', 'xlsx']:
                # Excel文件
                try:
                    import pandas as pd
                    df = pd.read_excel(io.BytesIO(file_content))
                    
                    # 构建清晰的文件内容，让AI能够理解
                    info_parts = []
                    info_parts.append(f"===== Excel文件内容: {file_name} =====")
                    info_parts.append(f"文件类型: Excel ({file_ext})")
                    info_parts.append(f"数据规模: {len(df)} 行 × {len(df.columns)} 列")
                    info_parts.append(f"列名: {', '.join(df.columns.tolist())}")
                    info_parts.append("")
                    info_parts.append("===== 数据内容 =====")
                    
                    # 使用更易读的格式显示数据（CSV格式）
                    rows_to_show = min(80, len(df))
                    info_parts.append(df.head(rows_to_show).to_csv(sep='\t', na_rep=''))
                    
                    if len(df) > 80:
                        info_parts.append("")
                        info_parts.append(f"===== 注意 =====")
                        info_parts.append(f"文件共有 {len(df)} 行，以上显示前 80 行")
                        info_parts.append(f"剩余 {len(df) - 80} 行未完整显示")
                        
                        # 添加统计信息
                        numeric_cols = df.select_dtypes(include=['number']).columns
                        if len(numeric_cols) > 0:
                            info_parts.append("")
                            info_parts.append("===== 数值列统计 =====")
                            info_parts.append(df[numeric_cols].describe().to_csv(sep='\t'))
                    
                    text_content = "\n".join(info_parts)
                    
                except ImportError:
                    ui.notify('需要安装pandas和openpyxl库: pip install pandas openpyxl', type='warning')
                    text_content = f"[Excel文档: {file_name}，无法读取内容，请安装pandas和openpyxl]"
                except Exception as ex:
                    text_content = f"[Excel文档: {file_name}，读取失败: {str(ex)}]"

            elif file_ext == 'pdf':
                try:
                    from pypdf import PdfReader
                    pdf_reader = PdfReader(io.BytesIO(file_content))
                    total_pages = len(pdf_reader.pages)

                    text_content = f"PDF文档摘要：\n"
                    text_content += f"总页数: {total_pages}\n\n"

                    pages_to_read = min(20, total_pages)
                    text_content += f"前{pages_to_read}页内容：\n\n"

                    for i, page in enumerate(pdf_reader.pages[:pages_to_read]):
                        page_text = page.extract_text()
                        text_content += f"--- 第{i+1}页 ---\n{page_text}\n\n"

                    if total_pages > 20:
                        text_content += f"\n... 还有 {total_pages - 20} 页未显示"

                except ImportError:
                    ui.notify('需要安装pypdf库: pip install pypdf', type='warning')
                    text_content = f"[PDF文档: {file_name}，无法读取内容，请安装pypdf]"
                except Exception as ex:
                    text_content = f"[PDF文档: {file_name}，读取失败: {str(ex)}]"
            
            else:
                text_content = f"[不支持的文件格式: {file_ext}]"
            
            # 限制总长度为10000字符（增加限制）
            original_length = len(text_content)
            if len(text_content) > 10000:
                text_content = text_content[:10000] + f"\n\n...(内容过长，已截断。原始长度: {original_length} 字符，显示: 10000 字符)"
            
            # 添加到输入框
            if hasattr(self, 'chat_input'):
                context = f"""
====================
【用户已上传文件】
文件名: {file_name}
文件类型: {file_ext.upper()}
文件内容如下:
====================
{text_content}
====================
【文件内容结束】
请根据上述文件内容回答用户的问题。
====================
"""
                self.chat_input.value = (self.chat_input.value or "") + f"\n{context}\n"
                
                # 显示详细的成功提示
                if original_length > 10000:
                    ui.notify(f'已添加文件"{file_name}"（{original_length}字符，显示前10000字符）', type='positive', position='top')
                else:
                    ui.notify(f'已添加文件"{file_name}"（{original_length}字符）', type='positive')
        
        except Exception as ex:
            ui.notify(f'文件上传失败: {str(ex)}', type='negative')
            import traceback
            traceback.print_exc()
    
    def find_gaps(self):
        """查缺补漏 - 发现未记录的内容"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        # 获取今日数据
        visits = [v for v in visit_summary_service.list_visits(limit=10) if v.get('visit_date', '') == today]
        reflection = personal_growth_service.get_reflection(today)
        
        gaps = []
        
        if not visits:
            gaps.append("❌ 今日无拜访记录")
        else:
            for v in visits:
                if not v.get('follow_up_tasks'):
                    gaps.append(f"⚠️ 拜访 {v.get('visit_date', '')} 未设置后续跟进")
                if not v.get('new_insights'):
                    gaps.append(f"⚠️ 拜访 {v.get('visit_date', '')} 未记录新发现")
        
        if not reflection:
            gaps.append("❌ 今日未填写个人总结")
        else:
            if not reflection.learning:
                gaps.append("⚠️ 今日反思未填写学习内容")
            if not reflection.improvement_goal:
                gaps.append("⚠️ 今日反思未设置改进目标")
        
        # 显示结果
        with ui.dialog() as dialog, ui.card().classes('glass-card w-full').style('max-width: 600px'):
            ui.label('💡 查缺补漏').classes('text-h5 text-white q-mb-md')
            if gaps:
                for gap in gaps:
                    with ui.element('div').classes('glass-list-item'):
                        ui.label(gap).classes('text-white')
            else:
                ui.label('✅ 太棒了！今日记录完整').classes('text-positive')
            with ui.row().classes('w-full justify-end q-mt-md'):
                ui.button('关闭', on_click=dialog.close).classes('glass-btn')
        dialog.open()
    
    def render_contacts(self):
        """渲染联系人管理页面"""
        ui.label('👥 联系人管理').classes('page-title')

        with ui.row().classes('w-full q-gutter-md'):
            # 左侧：添加联系人
            with ui.card().classes('glass-card col-4 q-pa-lg'):
                ui.label('➕ 添加联系人').classes('section-title')

                self.contact_name = ui.input(label='姓名 *').classes('w-full glass-input')
                self.contact_type = ui.select(
                    label='类型',
                    options=['医生', '护士', '护士长', '同事', '主管', '药剂师', '行政人员', '其他'],
                    value='其他'
                ).classes('w-full glass-input')
                self.contact_org = ui.input(label='所属机构').classes('w-full glass-input')
                self.contact_dept = ui.input(label='部门/科室').classes('w-full glass-input')
                self.contact_title = ui.input(label='职称/职位').classes('w-full glass-input')
                self.contact_tags = ui.input(label='标签 (逗号分隔)').classes('w-full glass-input')
                self.contact_notes = ui.textarea(label='备注').classes('w-full glass-input')

                self.editing_contact_id = None # Tracker for edit mode

                with ui.row().classes('q-mt-md gap-3'):
                    self.btn_save_contact = ui.button('💾 添加', on_click=self.add_contact).classes('glass-btn')
                    self.btn_cancel_contact = ui.button('取消编辑', on_click=self.reset_contact_form).classes('glass-btn-secondary')
                    self.btn_cancel_contact.visible = False

            # 右侧：联系人列表
            with ui.card().classes('glass-card col-7 q-pa-lg'):
                ui.label('📋 联系人列表').classes('section-title')

                # 类型筛选
                self.contact_filter = ui.select(
                    label='筛选类型',
                    options=['全部', '医生', '护士', '护士长', '同事', '主管', '其他'],
                    value='全部',
                    on_change=self.refresh_contacts_list
                ).classes('w-full glass-input q-mb-md')

                self.contacts_container = ui.column().classes('w-full')
                self.refresh_contacts_list()
    
    def render_smart_export(self):
        """渲染智能总结导出页面"""
        ui.label('📊 智能总结').classes('page-title')

        with ui.card().classes('glass-card w-full q-pa-lg'):
            ui.label('📤 导出时间段总结').classes('section-title')

            with ui.row().classes('q-gutter-md q-mb-md items-end'):
                self.export_start = ui.input(
                    label='开始日期 (YYYY-MM-DD)',
                    value=(datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
                ).classes('glass-input')
                self.export_end = ui.input(
                    label='结束日期 (YYYY-MM-DD)',
                    value=datetime.now().strftime('%Y-%m-%d')
                ).classes('glass-input')
                self.export_ai = ui.checkbox('包含 AI 分析', value=True)

            with ui.row().classes('q-gutter-md'):
                ui.button('📅 导出自定义时间段', on_click=self.export_custom_summary).classes('glass-btn')
                ui.button('📊 导出本周总结', on_click=self.export_weekly_summary).classes('glass-btn-secondary')
                ui.button('📆 导出最近7天', on_click=self.export_recent_summary).classes('glass-btn-secondary')

        # 导出历史
        with ui.card().classes('glass-card w-full q-pa-lg mt-4'):
            ui.label('🗂️ 历史导出').classes('section-title')
            self.exports_container = ui.column().classes('w-full')
            self.refresh_exports_list()
    
    def refresh_exports_list(self):
        """刷新导出历史列表"""
        if not hasattr(self, 'exports_container'):
            return
        
        self.exports_container.clear()
        with self.exports_container:
            exports = summary_export_service.list_exports()
            
            if not exports:
                ui.label('暂无导出记录').classes('text-secondary')
                return
            
            for exp in exports[:10]:
                with ui.row().classes('items-center q-my-sm w-full justify-between'):
                    ui.label(f"📄 {exp['filename']}").classes('col-grow')
                    with ui.row().classes('q-gutter-sm'):
                        ui.button('查看', on_click=lambda e=exp: self.view_export(e['path'])).props('flat size=sm color=primary')
                        ui.button('删除', on_click=lambda e=exp: self.delete_export_confirm(e)).props('flat size=sm color=negative')
    
    def delete_export_confirm(self, export: dict):
        """确认删除导出记录"""
        with ui.dialog() as dialog, ui.card().classes('glass-card'):
            ui.label('⚠️ 确认删除').classes('text-h6 text-white q-mb-md')
            ui.label(f'确定要删除导出记录 "{export["filename"]}" 吗？').classes('text-white')
            ui.label('此操作不可逆，请谨慎操作！').classes('text-negative q-mt-sm font-bold')
            
            with ui.row().classes('w-full justify-end q-mt-lg q-gutter-sm'):
                ui.button('取消', on_click=dialog.close).classes('glass-btn')
                ui.button('确认删除', on_click=lambda: self.delete_export_execute(export['path'], dialog)).props('color=negative')
        
        dialog.open()
    
    def delete_export_execute(self, export_path: str, dialog):
        """执行删除导出记录"""
        try:
            Path(export_path).unlink()
            ui.notify('导出记录已删除', type='positive')
            dialog.close()
            self.refresh_exports_list()
        except Exception as e:
            ui.notify(f'删除失败: {str(e)}', type='negative')
        
        # 预览区
        with ui.card().classes('w-full q-mt-md'):
            ui.label('总结预览').classes('text-h6')
            self.export_preview = ui.markdown('点击上方按钮生成总结').classes('w-full')
    
    # ==================== 操作方法 ====================
    
    async def generate_action(self):
        """生成今日行动单"""
        ui.notify('正在生成今日行动单...', type='info')
        action = await decision_engine.generate_daily_action()
        ui.notify('行动单已生成', type='positive')
        self.navigate('daily_action')
    
    def save_preparation(self):
        """保存拜访准备"""
        if not self.prep_contact.value:
            ui.notify('请选择拜访对象', type='warning')
            return
        
        # 解析联系人 ID
        contact_val = self.prep_contact.value
        if contact_val.startswith('doctor_'):
            doctor_id = contact_val.replace('doctor_', '')
        else:
            doctor_id = contact_val.replace('contact_', '')
        
        preparation_service.create_preparation(
            doctor_id=doctor_id,
            visit_date=self.prep_date.value,
            visit_goal=self.prep_goal.value,
            exploration_question=self.prep_question.value,
            concerns=self.prep_concerns.value,
            prepared_data=self.prep_data.value,
            notes=getattr(self, 'prep_notes', None) and self.prep_notes.value or ''
        )
        ui.notify('拜访准备已保存', type='positive')
        if hasattr(self, 'prep_list_container'):
            self.refresh_prep_list()
    
    async def get_ai_prep_suggestion(self):
        """获取AI准备建议"""
        if not self.prep_contact.value:
            ui.notify('请先选择拜访对象', type='warning')
            return
        
        contact_val = self.prep_contact.value
        if contact_val.startswith('doctor_'):
            doctor_id = contact_val.replace('doctor_', '')
        else:
            doctor_id = contact_val.replace('contact_', '')
        
        ui.notify('AI 正在生成建议...', type='info')
        suggestion = await preparation_service.get_ai_suggestions(doctor_id)
        if suggestion:
            ui.notify('AI建议已生成', type='positive')
            with ui.dialog() as dialog, ui.card().classes('glass-card'):
                ui.label('AI 准备建议').classes('text-h6 text-white')
                ui.markdown(suggestion)
                ui.button('关闭', on_click=dialog.close)
            dialog.open()
        else:
            ui.notify('无法获取AI建议', type='warning')
    
    def save_visit(self):
        """保存拜访记录"""
        if not self.visit_contact.value:
            ui.notify('请选择交流对象', type='warning')
            return

        contact_val = self.visit_contact.value
        if contact_val.startswith('doctor_'):
            doctor_id_for_storage = contact_val
            is_doctor = True
        else:
            doctor_id_for_storage = ""
            is_doctor = False

        visit_summary_service.create_visit_summary(
            doctor_id=doctor_id_for_storage,
            visit_date=self.visit_date.value,
            key_topics=self.visit_topics.value,
            doctor_concerns=self.visit_concerns.value,
            objections=self.visit_objections.value,
            responses=self.visit_responses.value,
            response_effectiveness=int(self.visit_effectiveness.value),
            emotional_tone="",
            new_insights="",
            follow_up_tasks=self.visit_next_step.value,
        )

        ui.notify('交流记录已保存', type='positive')

        self.visit_topics.value = ''
        self.visit_concerns.value = ''
        self.visit_objections.value = ''
        self.visit_responses.value = ''
        self.visit_next_step.value = ''
        self.visit_effectiveness.value = 3

        if hasattr(self, 'visit_list_container'):
            self.refresh_visit_list()
            
    def save_personal_summary(self):
        """保存个人成长总结"""
        personal_growth_service.create_reflection(
            date=self.summary_date.value,
            today_score=0, # 默认值
            anxiety_source="", # 默认值
            achievement=self.summary_well.value,
            weakness=self.summary_improve.value,
            avoidance="", # 默认值
            breakthrough="", # 默认值
            learning=self.summary_learning.value,
            improvement_goal=self.summary_plan.value
        )
        ui.notify('个人总结已保存', type='positive')
        if hasattr(self, 'summary_list_container'):
            self.refresh_summary_list()
    
    def refresh_summary_list(self):
        """刷新个人总结列表"""
        if not hasattr(self, 'summary_list_container'):
            return
        self.summary_list_container.clear()
        with self.summary_list_container:
            reflections = personal_growth_service.list_reflections()
            if reflections:
                for r in reflections[:10]:
                    with ui.element('div').classes('glass-list-item'):
                        ui.label(f"{r['date']} - 学习: {r.get('learning', '')[:20]}...").classes('text-white')
            else:
                ui.label('暂无总结记录').classes('text-secondary')
    
    def add_doctor(self):
        """添加医生"""
        if not self.doc_name.value:
            ui.notify('请输入医生姓名', type='warning')
            return
        
        interests = [i.strip() for i in self.doc_interests.value.split(',') if i.strip()]
        
        doctor_service.create_doctor(
            name=self.doc_name.value,
            hospital=self.doc_hospital.value,
            department=self.doc_department.value,
            title=self.doc_title.value,
            interests=interests,
            decision_style=self.doc_style.value,
            relationship_stage=self.doc_stage.value,
            unmet_needs=self.doc_needs.value,
            notes=getattr(self, 'doc_notes', None) and self.doc_notes.value or ''
        )
        ui.notify('医生已添加', type='positive')
        
        # 清空表单
        self.doc_name.value = ''
        self.doc_hospital_id.value = ''
        self.doc_hospital.value = ''
        self.doc_department_id.value = ''
        self.doc_department.value = ''
        self.doc_title.value = ''
        self.doc_interests.value = ''
        self.doc_style.value = None
        self.doc_stage.value = '初识'
        self.doc_needs.value = ''
        if hasattr(self, 'doc_notes'):
            self.doc_notes.value = ''
        
        # 重置科室选择框选项
        self.doc_department_id.set_options({'': '未指定'})
        
        self.refresh_doctor_list()
    
    def refresh_doctor_list(self):
        """刷新医生列表"""
        self.doctor_table_container.clear()
        with self.doctor_table_container:
            doctors = doctor_service.list_doctors()
            for doc in doctors:
                with ui.row().classes('items-center q-my-sm w-full'):
                    ui.label(f"👨‍⚕️ {doc['name']}").classes('col-2')
                    ui.label(f"{doc.get('hospital', '')}").classes('col-2')
                    ui.label(f"{doc.get('department', '')}").classes('col-2')
                    ui.label(f"{doc.get('relationship_stage', '')}").classes('col-2')
                    with ui.row().classes('col-4'):
                        ui.button('详情', on_click=lambda d=doc: self.view_doctor(d)).props('flat size=sm')
                        ui.button('编辑', on_click=lambda d=doc: self.edit_doctor(d)).props('flat size=sm color=primary')
                        ui.button('删除', on_click=lambda d=doc: self.delete_doctor(d['doctor_id'])).props('flat size=sm color=negative')
    
    def edit_doctor(self, doctor: dict):
        """编辑医生（加载到表单）"""
        self.doc_name.value = doctor.get('name', '')
        self.doc_hospital.value = doctor.get('hospital', '')
        self.doc_department.value = doctor.get('department', '')
        self.doc_title.value = doctor.get('title', '')
        self.doc_interests.value = ', '.join(doctor.get('interests', []))
        self.doc_style.value = doctor.get('decision_style', '')
        self.doc_stage.value = doctor.get('relationship_stage', '初识')
        self.doc_needs.value = doctor.get('unmet_needs', '')
        self.doc_notes.value = doctor.get('notes', '')
        ui.notify(f'已加载医生 {doctor.get("name")} 信息，修改后点击添加即可更新', type='info')
        # 滚动到顶部
        ui.run_javascript('window.scrollTo(0, 0)')
    
    def delete_doctor(self, doctor_id: str):
        """删除医生"""
        doctor_service.delete_doctor(doctor_id)
        ui.notify('医生已删除', type='positive')
        self.refresh_doctor_list()
    
    def view_doctor(self, doctor: dict):
        """查看医生详情"""
        report = doctor_service.generate_doctor_report(doctor['doctor_id'])
        if report:
            with ui.dialog() as dialog, ui.card().classes('w-96'):
                ui.markdown(report)
                ui.button('关闭', on_click=dialog.close)
            dialog.open()
    
    def refresh_prep_list(self):
        """刷新拜访准备列表"""
        if not hasattr(self, 'prep_list_container'):
            return
        self.prep_list_container.clear()
        with self.prep_list_container:
            preps = preparation_service.list_preparations()[:15]
            for prep in preps:
                with ui.row().classes('items-center w-full q-my-xs'):
                    ui.label(f"[{prep['visit_date']}] {prep.get('visit_goal', '')[:25]}...").classes('col-8 text-caption')
                    with ui.row().classes('col-4'):
                        ui.button('查看', on_click=lambda p=prep: self.view_prep_detail(p)).props('flat dense size=sm')
                        ui.button('编辑', on_click=lambda p=prep: self.edit_prep(p)).props('flat dense size=sm color=primary')
                        ui.button('删除', on_click=lambda p=prep: self.delete_prep(p['prep_id'])).props('flat dense size=sm color=negative')

    def edit_prep(self, prep: dict):
        """编辑准备（加载到表单）"""
        self.prep_doctor.value = prep.get('doctor_id')
        self.prep_date.value = prep.get('visit_date')
        self.prep_goal.value = prep.get('visit_goal', '')
        self.prep_question.value = prep.get('exploration_question', '')
        self.prep_concerns.value = prep.get('concerns', '')
        self.prep_data.value = prep.get('prepared_data', '')
        self.prep_notes.value = prep.get('notes', '')
        ui.notify('已加载准备记录，修改后点击保存即可更新', type='info')
        ui.run_javascript('window.scrollTo(0, 0)')
    
    def view_prep_detail(self, prep: dict):
        """查看准备详情"""
        content = f"""## 拜访准备
**日期**: {prep.get('visit_date', '')}
**目标**: {prep.get('visit_goal', '')}
**探索问题**: {prep.get('exploration_question', '')}
**顾虑**: {prep.get('concerns', '')}
**准备资料**: {prep.get('prepared_data', '')}
**备注**: {prep.get('notes', '')}
"""
        with ui.dialog() as dialog, ui.card().classes('w-full').style('max-width: 600px'):
            ui.markdown(content)
            ui.button('关闭', on_click=dialog.close)
        dialog.open()
    
    def delete_prep(self, prep_id: str):
        """删除准备记录"""
        file_manager.delete_file(file_manager.preparations_dir, prep_id)
        ui.notify('准备记录已删除', type='positive')
        self.refresh_prep_list()
    
    def refresh_visit_list(self):
        """刷新拜访记录列表"""
        if not hasattr(self, 'visit_list_container'):
            return
        self.visit_list_container.clear()
        with self.visit_list_container:
            visits = visit_summary_service.list_visits(limit=30)

            date_groups = {}
            for v in visits:
                date = v.get('visit_date', '未知')
                if date not in date_groups:
                    date_groups[date] = []
                date_groups[date].append(v)

            for date in sorted(date_groups.keys(), reverse=True):
                date_visits = date_groups[date]
                with ui.expansion(f'📅 {date} ({len(date_visits)}条记录)', icon='event').classes('w-full'):
                    for visit in date_visits:
                        doctor_name = "未知医生"
                        if visit.get('doctor_id'):
                            doctor_data = doctor_service.get_doctor(visit['doctor_id'])
                            if doctor_data:
                                doctor_name = getattr(doctor_data, 'name', '未知医生')

                        stars = "⭐" * min(visit.get('response_effectiveness', 3), 5)

                        with ui.row().classes('w-full items-center q-my-xs'):
                            ui.label(f"👨‍⚕️ {doctor_name}").classes('col-4 text-white')
                            ui.label(f"{stars}").classes('col-2 text-warning')
                            ui.label(f"{visit.get('key_topics', '')[:15]}...").classes('col-4 text-secondary')

                        with ui.row().classes('w-full q-my-xs'):
                            ui.button('👁️ 查看', on_click=lambda e, v=visit: self.load_single_visit_dialog(v['visit_id'])).props('flat dense size=sm')
                            ui.button('✏️ 编辑', on_click=lambda e, v=visit: self.edit_visit_by_id(v['visit_id'], date, v.get('doctor_id', '') or '')).props('flat dense size=sm color=primary')
                            ui.button('🗑️ 删除', on_click=lambda e, v=visit: self.delete_visit_by_id(v['visit_id'])).props('flat dense size=sm color=negative')

    def load_single_visit_dialog(self, visit_id: str):
        """加载单条拜访记录的对话框"""
        try:
            visit = visit_summary_service.get_visit(visit_id)
            if not visit:
                ui.notify('记录不存在', type='warning')
                return

            doctor_name = "未知医生"
            if visit.doctor_id:
                doctor_data = doctor_service.get_doctor(visit.doctor_id)
                if doctor_data:
                    doctor_name = getattr(doctor_data, 'name', '未知医生')

            with ui.dialog() as dialog, ui.card().classes('glass-card w-full').style('max-width: 700px; max-height: 80vh; overflow-y: auto'):
                ui.label(f'📋 {visit.visit_date} 交流记录').classes('text-h6 text-white q-mb-md')
                ui.label(f'医生: {doctor_name}').classes('text-white q-mb-sm')
                ui.label(f'效果评分: {"⭐" * int(visit.response_effectiveness)} ({visit.response_effectiveness}/5)').classes('text-warning q-mb-md')

                if visit.key_topics:
                    ui.label('讨论话题:').classes('text-secondary text-caption')
                    ui.markdown(str(visit.key_topics))

                if visit.doctor_concerns:
                    ui.label('客户关注点:').classes('text-secondary text-caption')
                    ui.markdown(str(visit.doctor_concerns))

                if visit.objections:
                    ui.label('客户异议:').classes('text-secondary text-caption')
                    ui.markdown(str(visit.objections))

                if visit.responses:
                    ui.label('我的回应:').classes('text-secondary text-caption')
                    ui.markdown(str(visit.responses))

                if visit.follow_up_tasks:
                    ui.label('后续跟进:').classes('text-secondary text-caption')
                    ui.markdown(str(visit.follow_up_tasks))

                if visit.ai_summary and not str(visit.ai_summary).startswith('<coroutine'):
                    ui.label('AI摘要:').classes('text-info text-caption')
                    ui.markdown(f"*{visit.ai_summary}*")

                with ui.row().classes('w-full justify-end q-mt-md'):
                    ui.button('关闭', on_click=dialog.close).classes('glass-btn')
            dialog.open()
        except Exception as e:
            ui.notify(f'加载记录失败: {str(e)}', type='negative')
            print(f'Error loading visit {visit_id}: {e}')

    def edit_visit(self, visit: dict):
        """编辑拜访（兼容旧方法）"""
        visit_id = visit.get('visit_id', '')
        date = visit.get('visit_date', '')
        doctor_id = visit.get('doctor_id', '')
        self.edit_visit_by_id(visit_id, date, doctor_id)

    def delete_visit(self, visit_id: str):
        """删除拜访（兼容旧方法）"""
        self.delete_visit_by_id(visit_id)

    def view_visit_detail(self, visit: dict):
        """查看拜访详情（兼容旧方法）"""
        self.edit_visit(visit)

    def save_reflection(self):
        """保存今日反思"""
        today = datetime.now().strftime('%Y-%m-%d')
        score = int(self.ref_score.value)
        
        personal_growth_service.create_reflection(
            date=today,
            today_score=score,
            anxiety_source=self.ref_anxiety.value,
            achievement=self.ref_achievement.value,
            weakness=self.ref_weakness.value,
            avoidance=self.ref_avoidance.value,
            breakthrough=self.ref_breakthrough.value,
            learning=self.ref_learning.value,
            improvement_goal=self.ref_improvement.value,
            notes=getattr(self, 'ref_notes', None) and self.ref_notes.value or ''
        )
        ui.notify('今日反思已保存', type='positive')
    
    def generate_weekly_report(self):
        """生成周报"""
        reporting_service.generate_weekly_report()
        ui.notify('周报已生成', type='positive')
        if hasattr(self, 'reports_container'):
            self.refresh_reports_list()
    
    def generate_monthly_report(self):
        """生成月报"""
        reporting_service.generate_monthly_report()
        ui.notify('月报已生成', type='positive')
        if hasattr(self, 'reports_container'):
            self.refresh_reports_list()
    
    def view_report(self, path: str):
        """查看报告"""
        content = reporting_service.get_report_content(path)
        if content:
            with ui.dialog() as dialog, ui.card().classes('glass-card w-full').style('max-width: 800px; max-height: 80vh; overflow-y: auto;'):
                ui.markdown(content)
                with ui.row().classes('w-full justify-end q-mt-md'):
                    ui.button('关闭', on_click=dialog.close).classes('glass-btn')
            dialog.open()
    
    def toggle_ai(self):
        """切换AI状态"""
        if self.ai_enabled_switch.value:
            provider = self.ai_provider.value
            has_key = False
            
            if provider == 'xiaomi':
                has_key = bool(self.xiaomi_key.value)
            else:
                has_key = bool(self.deepseek_key.value)
                
            if not has_key:
                ui.notify('请先输入选定服务商的 API Key', type='warning')
                self.ai_enabled_switch.value = False
                return
            
            # 临时保存配置以便 enable 能读取
            file_manager.update_config({
                'ai_provider': provider,
                'xiaomi_api_key': self.xiaomi_key.value,
                'deepseek_api_key': self.deepseek_key.value
            })
            ai_integration._load_config()
            
            if ai_integration.enable():
                self.ai_status_label.text = "🟢 AI已启用"
            else:
                self.ai_enabled_switch.value = False
        else:
            ai_integration.disable()
            self.ai_status_label.text = "⚫ AI未启用"
        ui.notify('AI 状态已更新', type='positive')
    
    def save_settings(self):
        """保存设置"""
        file_manager.update_config({
            'ai_enabled': self.ai_enabled_switch.value,
            'ai_provider': self.ai_provider.value,
            'deepseek_api_key': self.deepseek_key.value,
            'deepseek_model': self.deepseek_model.value,
            'xiaomi_api_key': self.xiaomi_key.value,
            'xiaomi_model': self.xiaomi_model.value
        })
        ai_integration._load_config()
        ui.notify('设置已保存', type='positive')
    
    def backup_data(self):
        """备份数据"""
        backup_path = file_manager.backup_data()
        if backup_path:
            ui.notify(f'备份完成: {backup_path}', type='positive')
        else:
            ui.notify('备份失败', type='negative')
    
    # ==================== AI 对话方法 ====================
    
    def new_chat_session(self):
        """创建新对话"""
        session = ai_chat_service.new_session()
        self.current_session_id = session.session_id
        ui.notify('新对话已创建', type='positive')
        self.refresh_sessions_list()
        self.load_chat_session(session.session_id)
    
    def refresh_sessions_list(self):
        """刷新会话列表"""
        if not hasattr(self, 'sessions_container') or self.sessions_container is None:
            return

        sessions = ai_chat_service.list_sessions()
        self.sessions_container.clear()

        if not sessions:
            with self.sessions_container:
                ui.label('暂无会话').classes('text-caption text-grey text-center w-full')
            return

        with self.sessions_container:
            for session in sessions[:20]:
                is_active = getattr(self, 'current_session_id', None) == session['session_id']
                bg_class = 'bg-primary' if is_active else 'bg-grey-8'
                text_class = 'text-white' if is_active else 'text-grey-4'

                with ui.row().classes(f'items-center w-full q-my-xs q-pa-xs rounded {bg_class}'):
                    title = session['title']
                    if len(title) > 12:
                        title = title[:12] + '...'

                    ui.button(
                        title,
                        on_click=lambda s=session: self.load_chat_session(s['session_id'])
                    ).props(f'flat dense color=white no-caps align=left').classes(f'col-grow text-left {text_class}')

                    with ui.row().classes('items-center q-gutter-x-xs'):
                        ui.button(icon='edit', on_click=lambda e, s=session: self.rename_chat_session(s)).props('flat dense round size=xs color=white')
                        ui.button(icon='delete', on_click=lambda e, s=session: self.delete_chat_session(s['session_id'])).props('flat dense round size=xs color=negative')

    def rename_chat_session(self, session: dict):
        """重命名会话"""
        def save(new_title):
            if new_title:
                ai_chat_service.update_session_title(session['session_id'], new_title)
                self.refresh_sessions_list()
                ui.notify('会话已重命名', type='positive')
                dialog.close()
                
        with ui.dialog() as dialog, ui.card().classes('w-full').style('max-width: 400px'):
            ui.label('重命名会话').classes('text-h6')
            name_input = ui.input('新标题', value=session['title']).classes('w-full').props('autofocus')
            with ui.row().classes('w-full justify-end q-mt-md'):
                ui.button('取消', on_click=dialog.close).props('flat')
                ui.button('保存', on_click=lambda: save(name_input.value)).props('color=primary')
        dialog.open()

    def delete_chat_session(self, session_id: str):
        """删除会话"""
        async def _delete():
            ai_chat_service.delete_session(session_id)
            ui.notify('会话已删除', type='positive')
            self.refresh_sessions_list()
            # Create new session if current was deleted
            if getattr(self, 'current_session_id', None) == session_id:
                self.new_chat_session()
                
        # 延迟执行以避免UI上下文错误
        ui.timer(0.01, _delete, once=True)
    
    def copy_text(self, text: str):
        """复制文本到剪贴板"""
        try:
            # 尝试使用 NiceGUI 内置方法
            ui.clipboard.write(text)
            ui.notify('已复制到剪贴板', type='positive')
        except:
            # 如果内置方法失败，使用 JavaScript 方法
            import json
            ui.run_javascript(f'navigator.clipboard.writeText({json.dumps(text)}).then(() => {{}})')
            ui.notify('已复制到剪贴板', type='positive')

    def load_chat_session(self, session_id: str):
        """加载会话"""
        self.current_session_id = session_id
        if not hasattr(self, 'chat_messages_container'):
            return
        self.chat_messages_container.clear()
        
        with self.chat_messages_container:
            history = ai_chat_service.get_session_history(session_id)
            for msg in history:
                if msg['role'] == 'user':
                    with ui.row().classes('w-full justify-end items-end group'):
                        ui.button(icon='content_copy', on_click=lambda c=msg['content']: self.copy_text(c)).props('flat dense round size=xs color=grey').classes('opacity-50 group-hover:opacity-100 transition-opacity q-mr-sm')
                        ui.label(msg['content']).classes('bg-primary text-white q-pa-sm rounded-lg')
                else:
                    with ui.row().classes('w-full items-end group'):
                        ui.markdown(msg['content']).classes('bg-grey-8 q-pa-sm rounded-lg')
                        ui.button(icon='content_copy', on_click=lambda c=msg['content']: self.copy_text(c)).props('flat dense round size=xs color=grey').classes('opacity-50 group-hover:opacity-100 transition-opacity q-ml-sm')
    
    async def send_chat_message(self):
        """发送消息"""
        if not hasattr(self, 'chat_input') or not self.chat_input.value:
            return
        
        if not hasattr(self, 'current_session_id'):
            session = ai_chat_service.new_session()
            self.current_session_id = session.session_id
        
        message = self.chat_input.value
        self.chat_input.value = ''
        
        # 立即显示用户消息
        if hasattr(self, 'chat_messages_container'):
             with self.chat_messages_container:
                 with ui.row().classes('w-full justify-end items-end group'):
                     ui.button(icon='content_copy', on_click=lambda c=message: self.copy_text(c)).props('flat dense round size=xs color=grey').classes('opacity-50 group-hover:opacity-100 transition-opacity q-mr-sm')
                     ui.label(message).classes('bg-primary text-white q-pa-sm rounded-lg')
                 
                 # 显示加载状态
                 with ui.row().classes('w-full items-center q-my-sm') as self.typing_indicator:
                     ui.spinner('dots', size='2em', color='primary')
                     ui.label('AI 正在思考...').classes('text-grey q-ml-sm text-caption')
        
        # 滚动到底部
        ui.run_javascript(f'document.querySelector(".q-scrollarea__content").scrollIntoView(false)')

        # 调用异步 AI
        response = await ai_chat_service.chat(self.current_session_id, message)
        
        if hasattr(self, 'typing_indicator'):
            self.typing_indicator.delete()
            
        self.load_chat_session(self.current_session_id)
        
        self.refresh_sessions_list()
    
    # ==================== 联系人方法 ====================
    
    def add_contact(self):
        """添加/更新联系人"""
        if not self.contact_name.value:
            ui.notify('请输入姓名', type='warning')
            return
        
        tags = [t.strip() for t in self.contact_tags.value.split(',') if t.strip()]
        
        contact_id = getattr(self, 'editing_contact_id', None)
        
        contact_service.create_contact(
            name=self.contact_name.value,
            contact_type=self.contact_type.value,
            organization=self.contact_org.value,
            department=self.contact_dept.value,
            title=self.contact_title.value,
            tags=tags,
            notes=self.contact_notes.value,
            contact_id=contact_id
        )
        
        action = "更新" if contact_id else "添加"
        ui.notify(f'联系人已{action}', type='positive')
        self.reset_contact_form()
        self.refresh_contacts_list()
    
    def reset_contact_form(self):
        """重置联系人表单"""
        self.contact_name.value = ''
        self.contact_type.value = '其他'
        self.contact_org.value = ''
        self.contact_dept.value = ''
        self.contact_title.value = ''
        self.contact_tags.value = ''
        self.contact_notes.value = ''
        self.editing_contact_id = None
        
        if hasattr(self, 'btn_save_contact'):
            self.btn_save_contact.text = '💾 添加'
        if hasattr(self, 'btn_cancel_contact'):
            self.btn_cancel_contact.visible = False
            
    def edit_contact(self, contact: dict):
        """编辑联系人"""
        self.contact_name.value = contact.get('name', '')
        self.contact_type.value = contact.get('contact_type', '其他')
        self.contact_org.value = contact.get('organization', '')
        self.contact_dept.value = contact.get('department', '')
        self.contact_title.value = contact.get('title', '')
        self.contact_tags.value = ', '.join(contact.get('tags', []))
        self.contact_notes.value = contact.get('notes', '')
        self.editing_contact_id = contact.get('contact_id')
        
        if hasattr(self, 'btn_save_contact'):
            self.btn_save_contact.text = '✏️ 更新'
        if hasattr(self, 'btn_cancel_contact'):
            self.btn_cancel_contact.visible = True
            
        ui.notify(f'已加载联系人 {contact.get("name")}', type='info')
        ui.run_javascript('window.scrollTo(0, 0)')
        
    def delete_contact(self, contact_id: str):
        """删除联系人"""
        contact_service.delete_contact(contact_id)
        ui.notify('联系人已删除', type='positive')
        if getattr(self, 'editing_contact_id', None) == contact_id:
            self.reset_contact_form()
        self.refresh_contacts_list()
    
    def refresh_contacts_list(self):
        """刷新联系人列表"""
        if not hasattr(self, 'contacts_container'):
            return
        self.contacts_container.clear()
        
        filter_type = getattr(self, 'contact_filter', None)
        type_filter = filter_type.value if filter_type and filter_type.value != '全部' else None
        
        with self.contacts_container:
            contacts = contact_service.list_contacts(contact_type=type_filter)
            for contact in contacts:
                with ui.row().classes('items-center w-full q-my-sm'):
                    type_icon = {'医生': '👨‍⚕️', '护士': '👩‍⚕️', '护士长': '👩‍⚕️', '同事': '👤', '主管': '👔'}.get(contact.get('contact_type'), '👥')
                    ui.label(f"{type_icon} {contact['name']}").classes('col-2')
                    ui.label(contact.get('contact_type', '')).classes('col-2')
                    ui.label(contact.get('organization', '')).classes('col-2')
                    
                    with ui.row().classes('col-6 justify-end items-center'):
                        tags = contact.get('tags', [])[:2]
                        ui.label(', '.join(tags) if tags else '').classes('q-mr-sm text-caption')
                        ui.button('编辑', on_click=lambda c=contact: self.edit_contact(c)).props('flat dense size=sm color=primary')
                        ui.button('删除', on_click=lambda c=contact: self.delete_contact(c['contact_id'])).props('flat dense size=sm color=negative')
    
    # ==================== 智能总结方法 ====================
    
    async def export_custom_summary(self):
        """导出自定义时间段总结"""
        ui.notify('正在生成总结...', type='info')
        content = await summary_export_service.export_period_summary(
            self.export_start.value,
            self.export_end.value,
            self.export_ai.value
        )
        self.export_preview.content = content
        ui.notify('总结已生成', type='positive')
    
    async def export_weekly_summary(self):
        """导出本周总结"""
        ui.notify('正在生成周报...', type='info')
        content = await summary_export_service.export_weekly_summary(self.export_ai.value)
        self.export_preview.content = content
        ui.notify('本周总结已生成', type='positive')
    
    async def export_recent_summary(self):
        """导出最近7天总结"""
        ui.notify('正在生成总结...', type='info')
        content = await summary_export_service.export_recent_days(7, self.export_ai.value)
        self.export_preview.content = content
        ui.notify('最近7天总结已生成', type='positive')
    
    def view_export(self, path: str):
        """查看导出报告"""
        content = file_manager.read_markdown(Path(path))
        if content:
            with ui.dialog() as dialog, ui.card().classes('w-full').style('max-width: 900px'):
                ui.markdown(content)
                ui.button('关闭', on_click=dialog.close)
            dialog.open()
    
    def show_about_dialog(self):
        """显示关于对话框"""
        about_content = """
# 关于 医药信息专员助手

## 软件说明
""" + self.WELCOME_CONTENT + """

---

## 👨‍💻 作者信息

**作者**: 王客程

## 📧 联系方式

如有任何问题、建议或反馈，我很乐于倾听！

📮 **邮箱**: 1362832924@qq.com

欢迎联系交流，感谢您的使用！

---

*版本: 1.0.0*
"""
        with ui.dialog() as dialog, ui.card().classes('w-full').style('max-width: 750px; max-height: 85vh; overflow-y: auto'):
            ui.markdown(about_content)
            with ui.row().classes('w-full justify-end q-mt-md'):
                ui.button('关闭', on_click=dialog.close).props('color=primary')
        dialog.open()
    
    def run(self):
        """运行应用"""
        # 初始化状态
        self.current_category = 'daily'
        self.current_page = 'home'
        
        self.create_header()
        self.create_sidebar()  # 保留调用但已空实现
        
        with ui.column().classes('w-full q-pa-lg animate-in'):
            # 子导航面板
            self.sub_nav_area = ui.row().classes('w-full')
            with self.sub_nav_area:
                self.create_sub_nav()
            
            # 主内容区
            self.content_area = ui.column().classes('w-full')
            with self.content_area:
                self.render_home()
        
        # 首次运行显示欢迎页面
        if self.first_run:
            self.show_welcome_dialog()


def create_app():
    """创建应用实例"""
    app_instance = MedRepApp()
    app_instance.run()


# 直接运行时启动
if __name__ in {"__main__", "__mp_main__"}:
    create_app()
    ui.run(
        title='医药信息专员助手',
        dark=True,
        native=True,  # 桌面应用模式
        window_size=(1400, 900),
        reload=False
    )
