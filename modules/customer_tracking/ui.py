"""
客户追踪管理UI界面
"""
from nicegui import ui
from datetime import datetime, timedelta
from typing import Optional
from modules.customer_tracking.service import customer_tracking_service
from modules.doctor_manager.service import doctor_service


def render_customer_tracking_page():
    """渲染客户追踪管理页面"""
    
    # 页面标题
    ui.label('📊 客户追踪管理').classes('page-title')
    
    # 功能说明
    with ui.card().classes('glass-card q-mb-md'):
        ui.markdown("""
        ### 💡 4张核心表格管理
        
        - **表1：客户开发表** - 记录客户开发全过程（渠道、首次联系、加微信等）
        - **表2：客户追踪表** - 记录每次跟进详情（话术、回复情况、效果评分）
        - **表3：客户分类表** - A/B/C/D类客户分类管理，自动建议跟进频率
        - **表4：统计分析表** - 周报/月报，新增客户、A类客户增长等核心指标
        
        **核心理念**：工具控制行为，流程控制结果。A类客户只能增长，不能减少！
        """)
    
    # 标签页
    with ui.tabs().classes('w-full text-white glass-tabs') as tabs:
        tab_development = ui.tab('客户开发表')
        tab_followup = ui.tab('客户追踪表')
        tab_classification = ui.tab('客户分类表')
        tab_statistics = ui.tab('统计分析表')
        tab_pending = ui.tab('待跟进提醒')
    
    with ui.tab_panels(tabs, value=tab_development).classes('w-full'):
        # 表1：客户开发表
        with ui.tab_panel(tab_development):
            render_development_panel()
        
        # 表2：客户追踪表
        with ui.tab_panel(tab_followup):
            render_followup_panel()
        
        # 表3：客户分类表
        with ui.tab_panel(tab_classification):
            render_classification_panel()
        
        # 表4：统计分析表
        with ui.tab_panel(tab_statistics):
            render_statistics_panel()
        
        # 待跟进提醒
        with ui.tab_panel(tab_pending):
            render_pending_panel()



def render_development_panel():
    """渲染客户开发表面板"""
    
    with ui.row().classes('w-full q-mb-md'):
        ui.button('➕ 添加开发记录', on_click=show_add_development_dialog).props('color=primary')
        ui.button('🔄 刷新', on_click=lambda: refresh_development_list()).props('color=secondary')
        ui.button('📤 导出Excel', on_click=lambda: export_development_excel()).props('color=info')
    
    # 列表容器
    development_list_container = ui.column().classes('w-full')
    
    def refresh_development_list():
        """刷新开发记录列表"""
        development_list_container.clear()
        
        records = customer_tracking_service.list_development_records()
        
        if not records:
            with development_list_container:
                ui.label('暂无开发记录').classes('text-grey')
            return
        
        with development_list_container:
            ui.label(f'共 {len(records)} 条记录').classes('text-white q-mb-sm')
            
            for record in records:
                with ui.card().classes('glass-card q-mb-sm'):
                    with ui.row().classes('w-full items-center'):
                        with ui.column().classes('col-grow'):
                            ui.label(f'👨‍⚕️ {record.doctor_name}').classes('text-h6 text-white')
                            ui.label(f'🏥 {record.hospital} - {record.department}').classes('text-grey')
                            ui.label(f'📍 渠道：{record.development_channel} {record.channel_detail}').classes('text-grey')
                            
                            # 时间节点
                            timeline = []
                            if record.first_contact_date:
                                timeline.append(f"首次联系：{record.first_contact_date.strftime('%Y-%m-%d')}")
                            if record.wechat_added_date:
                                timeline.append(f"加微信：{record.wechat_added_date.strftime('%Y-%m-%d')}")
                            if timeline:
                                ui.label(' | '.join(timeline)).classes('text-grey text-caption')
                        
                        with ui.column().classes('q-gutter-sm'):
                            ui.button('查看', on_click=lambda r=record: show_development_detail(r)).props('size=sm color=info')
                            ui.button('编辑', on_click=lambda r=record: show_edit_development_dialog(r)).props('size=sm color=secondary')
    
    refresh_development_list()


def show_add_development_dialog():
    """显示添加开发记录对话框"""
    
    # 获取医生列表
    doctors = doctor_service.list_doctors()
    doctor_options = {f"{d['name']} ({d['hospital']})": d['doctor_id'] for d in doctors}
    
    with ui.dialog() as dialog, ui.card().classes('w-full').style('max-width: 600px'):
        ui.label('➕ 添加客户开发记录').classes('text-h6')
        
        with ui.column().classes('w-full q-gutter-md'):
            # 选择医生
            doctor_select = ui.select(
                label='选择医生',
                options=list(doctor_options.keys()),
                with_input=True
            ).classes('w-full')
            
            # 开发渠道
            channel_select = ui.select(
                label='开发渠道',
                options=['学术会议', '转介绍', '陌生拜访', '线上渠道', '医院驻点', '药房推荐', '其他'],
                value='学术会议'
            ).classes('w-full')
            
            channel_detail = ui.input(label='渠道详情（如：XX学术会议）').classes('w-full')
            referrer = ui.input(label='推荐人').classes('w-full')
            
            # 联系信息
            phone = ui.input(label='电话').classes('w-full')
            wechat = ui.input(label='微信号').classes('w-full')
            
            # 时间节点
            with ui.row().classes('w-full'):
                with ui.column():
                    ui.label('首次联系时间').classes('text-grey')
                    first_contact = ui.date(value=datetime.now().strftime('%Y-%m-%d'))
                with ui.column():
                    ui.label('电话打通时间').classes('text-grey')
                    phone_connected = ui.date()
            
            with ui.row().classes('w-full'):
                with ui.column():
                    ui.label('添加微信时间').classes('text-grey')
                    wechat_added = ui.date()
                with ui.column():
                    ui.label('建群时间').classes('text-grey')
                    group_created = ui.date()
            
            # 评估
            hospital_level = ui.input(label='医院等级').classes('w-full')
            doctor_influence = ui.select(
                label='医生影响力',
                options=['高', '中', '低'],
                value='中'
            ).classes('w-full')
            prescription_volume = ui.input(label='处方量评估').classes('w-full')
            
            notes = ui.textarea(label='备注').classes('w-full')
            
            def save_development():
                if not doctor_select.value:
                    ui.notify('请选择医生', type='warning')
                    return
                
                doctor_id = doctor_options[doctor_select.value]
                doctor = doctor_service.get_doctor(doctor_id)
                
                customer_tracking_service.create_development_record(
                    doctor_id=doctor_id,
                    doctor_name=doctor.name,
                    hospital=doctor.hospital,
                    department=doctor.department,
                    development_channel=channel_select.value,
                    channel_detail=channel_detail.value,
                    referrer=referrer.value,
                    phone=phone.value,
                    wechat=wechat.value,
                    first_contact_date=datetime.strptime(first_contact.value, '%Y-%m-%d') if first_contact.value else None,
                    phone_connected_date=datetime.strptime(phone_connected.value, '%Y-%m-%d') if phone_connected.value else None,
                    wechat_added_date=datetime.strptime(wechat_added.value, '%Y-%m-%d') if wechat_added.value else None,
                    group_created_date=datetime.strptime(group_created.value, '%Y-%m-%d') if group_created.value else None,
                    hospital_level=hospital_level.value,
                    doctor_influence=doctor_influence.value,
                    prescription_volume=prescription_volume.value,
                    notes=notes.value
                )
                
                ui.notify('✅ 开发记录已添加', type='positive')
                dialog.close()
                # 刷新当前页面
                ui.navigate.reload()
            
            with ui.row().classes('w-full justify-end'):
                ui.button('取消', on_click=dialog.close).props('flat')
                ui.button('保存', on_click=save_development).props('color=primary')
    
    dialog.open()


def show_development_detail(record):
    """显示开发记录详情"""
    with ui.dialog() as dialog, ui.card().classes('w-full').style('max-width: 600px'):
        ui.label('📋 客户开发记录详情').classes('text-h6')
        
        with ui.column().classes('w-full q-gutter-sm'):
            ui.label(f'医生：{record.doctor_name}').classes('text-white')
            ui.label(f'医院：{record.hospital}').classes('text-grey')
            ui.label(f'科室：{record.department}').classes('text-grey')
            ui.label(f'开发渠道：{record.development_channel}').classes('text-grey')
            if record.channel_detail:
                ui.label(f'渠道详情：{record.channel_detail}').classes('text-grey')
            if record.referrer:
                ui.label(f'推荐人：{record.referrer}').classes('text-grey')
            
            ui.separator()
            
            if record.first_contact_date:
                ui.label(f'首次联系：{record.first_contact_date.strftime("%Y-%m-%d")}').classes('text-grey')
            if record.wechat_added_date:
                ui.label(f'添加微信：{record.wechat_added_date.strftime("%Y-%m-%d")}').classes('text-grey')
            
            if record.notes:
                ui.separator()
                ui.label('备注：').classes('text-white')
                ui.label(record.notes).classes('text-grey')
            
            ui.button('关闭', on_click=dialog.close).props('color=primary')
    
    dialog.open()


def export_development_excel():
    """导出开发记录Excel"""
    try:
        filename = customer_tracking_service.export_to_excel(export_type='development')
        ui.notify(f'✅ 已导出到：{filename}', type='positive')
    except Exception as e:
        ui.notify(f'❌ 导出失败：{str(e)}', type='negative')


def show_edit_development_dialog(record):
    """显示编辑开发记录对话框"""
    # 简化版，可以后续扩展
    ui.notify('编辑功能开发中', type='info')



def render_followup_panel():
    """渲染客户追踪表面板"""
    
    with ui.row().classes('w-full q-mb-md'):
        ui.button('➕ 添加跟进记录', on_click=show_add_followup_dialog).props('color=primary')
        ui.button('🔄 刷新', on_click=lambda: refresh_followup_list()).props('color=secondary')
        ui.button('📤 导出Excel', on_click=lambda: export_followup_excel()).props('color=info')
    
    # 筛选
    with ui.row().classes('w-full q-mb-md'):
        doctor_filter = ui.select(
            label='筛选医生',
            options=['全部'],
            value='全部'
        ).classes('w-200px')
        
        status_filter = ui.select(
            label='跟进状态',
            options=['全部', '待跟进', '跟进中', '已回复', '未回复'],
            value='全部'
        ).classes('w-200px')
        
        ui.button('筛选', on_click=lambda: refresh_followup_list()).props('color=secondary size=sm')
    
    # 列表容器
    followup_list_container = ui.column().classes('w-full')
    
    def refresh_followup_list():
        """刷新跟进记录列表"""
        followup_list_container.clear()
        
        records = customer_tracking_service.list_followup_records()
        
        if not records:
            with followup_list_container:
                ui.label('暂无跟进记录').classes('text-grey')
            return
        
        with followup_list_container:
            ui.label(f'共 {len(records)} 条记录').classes('text-white q-mb-sm')
            
            for record in records:
                with ui.card().classes('glass-card q-mb-sm'):
                    with ui.row().classes('w-full items-center'):
                        with ui.column().classes('col-grow'):
                            ui.label(f'👨‍⚕️ {record.doctor_name}').classes('text-h6 text-white')
                            ui.label(f'📅 {record.follow_date.strftime("%Y-%m-%d %H:%M")} | {record.follow_method}').classes('text-grey')
                            ui.label(f'💬 {record.content[:50]}...').classes('text-grey')
                            
                            # 回复状态
                            if record.customer_replied:
                                ui.label(f'✅ 已回复 | 效果评分：{"⭐" * record.effect_score}').classes('text-positive')
                            else:
                                ui.label(f'❌ 未回复（{record.days_no_reply}天）').classes('text-negative')
                        
                        with ui.column().classes('q-gutter-sm'):
                            ui.button('查看', on_click=lambda r=record: show_followup_detail(r)).props('size=sm color=info')
    
    refresh_followup_list()


def show_add_followup_dialog():
    """显示添加跟进记录对话框"""
    
    # 获取医生列表
    doctors = doctor_service.list_doctors()
    doctor_options = {f"{d['name']} ({d['hospital']})": d['doctor_id'] for d in doctors}
    
    with ui.dialog() as dialog, ui.card().classes('w-full').style('max-width: 600px'):
        ui.label('➕ 添加跟进记录').classes('text-h6')
        
        with ui.column().classes('w-full q-gutter-md'):
            # 选择医生
            doctor_select = ui.select(
                label='选择医生',
                options=list(doctor_options.keys()),
                with_input=True
            ).classes('w-full')
            
            # 跟进方式
            method_select = ui.select(
                label='跟进方式',
                options=['微信', '电话', '拜访', '短信', '邮件'],
                value='微信'
            ).classes('w-full')
            
            # 开口话术
            opening_script = ui.textarea(
                label='开口话术',
                placeholder='记录你的开场白...'
            ).classes('w-full')
            
            # 沟通内容
            content = ui.textarea(
                label='沟通内容',
                placeholder='记录沟通的详细内容...'
            ).classes('w-full')
            
            # 客户反馈
            replied = ui.checkbox('客户已回复')
            reply_content = ui.textarea(label='回复内容').classes('w-full')
            
            # 效果评分
            effect_score = ui.slider(
                min=1, max=5, step=1, value=3
            ).props('label-always').classes('w-full')
            ui.label('效果评分（1-5分）').classes('text-grey text-caption')
            
            notes = ui.textarea(label='备注').classes('w-full')
            
            def save_followup():
                if not doctor_select.value:
                    ui.notify('请选择医生', type='warning')
                    return
                
                if not content.value:
                    ui.notify('请填写沟通内容', type='warning')
                    return
                
                doctor_id = doctor_options[doctor_select.value]
                doctor = doctor_service.get_doctor(doctor_id)
                
                customer_tracking_service.create_followup_record(
                    doctor_id=doctor_id,
                    doctor_name=doctor.name,
                    follow_method=method_select.value,
                    opening_script=opening_script.value,
                    content=content.value,
                    customer_replied=replied.value,
                    reply_content=reply_content.value if replied.value else "",
                    reply_date=datetime.now() if replied.value else None,
                    effect_score=int(effect_score.value),
                    notes=notes.value
                )
                
                ui.notify('✅ 跟进记录已添加', type='positive')
                dialog.close()
                # 刷新当前页面
                ui.navigate.reload()
            
            with ui.row().classes('w-full justify-end'):
                ui.button('取消', on_click=dialog.close).props('flat')
                ui.button('保存', on_click=save_followup).props('color=primary')
    
    dialog.open()


def show_followup_detail(record):
    """显示跟进记录详情"""
    with ui.dialog() as dialog, ui.card().classes('w-full').style('max-width: 600px'):
        ui.label('📋 跟进记录详情').classes('text-h6')
        
        with ui.column().classes('w-full q-gutter-sm'):
            ui.label(f'医生：{record.doctor_name}').classes('text-white')
            ui.label(f'时间：{record.follow_date.strftime("%Y-%m-%d %H:%M")}').classes('text-grey')
            ui.label(f'方式：{record.follow_method}').classes('text-grey')
            
            if record.opening_script:
                ui.separator()
                ui.label('开口话术：').classes('text-white')
                ui.label(record.opening_script).classes('text-grey')
            
            ui.separator()
            ui.label('沟通内容：').classes('text-white')
            ui.label(record.content).classes('text-grey')
            
            ui.separator()
            if record.customer_replied:
                ui.label('✅ 客户已回复').classes('text-positive')
                if record.reply_content:
                    ui.label(f'回复：{record.reply_content}').classes('text-grey')
            else:
                ui.label(f'❌ 客户未回复（{record.days_no_reply}天）').classes('text-negative')
            
            ui.label(f'效果评分：{"⭐" * record.effect_score}').classes('text-grey')
            
            if record.notes:
                ui.separator()
                ui.label('备注：').classes('text-white')
                ui.label(record.notes).classes('text-grey')
            
            ui.button('关闭', on_click=dialog.close).props('color=primary')
    
    dialog.open()


def export_followup_excel():
    """导出跟进记录Excel"""
    try:
        filename = customer_tracking_service.export_to_excel(export_type='followup')
        ui.notify(f'✅ 已导出到：{filename}', type='positive')
    except Exception as e:
        ui.notify(f'❌ 导出失败：{str(e)}', type='negative')



def render_classification_panel():
    """渲染客户分类表面板"""
    
    with ui.row().classes('w-full q-mb-md'):
        ui.button('🔄 刷新', on_click=lambda: refresh_classification_list()).props('color=secondary')
        ui.button('📤 导出Excel', on_click=lambda: export_classification_excel()).props('color=info')
    
    # 分类统计卡片
    stats_container = ui.row().classes('w-full q-mb-md q-gutter-md')
    
    # 筛选
    level_filter = ui.select(
        label='筛选等级',
        options=['全部', 'A类', 'B类', 'C类', 'D类', '未分类'],
        value='全部'
    ).classes('w-200px q-mb-md')
    
    # 列表容器
    classification_list_container = ui.column().classes('w-full')
    
    def refresh_classification_list():
        """刷新客户分类列表"""
        # 清空统计卡片
        stats_container.clear()
        
        # 统计各等级客户数
        all_records = customer_tracking_service.list_customers_by_level()
        level_counts = {'A类': 0, 'B类': 0, 'C类': 0, 'D类': 0, '未分类': 0}
        for r in all_records:
            level_counts[r.customer_level] = level_counts.get(r.customer_level, 0) + 1
        
        # 显示统计卡片
        with stats_container:
            for level, count in level_counts.items():
                color = {
                    'A类': 'positive',
                    'B类': 'info',
                    'C类': 'warning',
                    'D类': 'negative',
                    '未分类': 'grey'
                }.get(level, 'grey')
                
                with ui.card().classes(f'glass-card bg-{color}'):
                    ui.label(level).classes('text-h6 text-white')
                    ui.label(f'{count} 个客户').classes('text-white')
        
        # 刷新列表
        classification_list_container.clear()
        
        level = level_filter.value if level_filter.value != '全部' else None
        records = customer_tracking_service.list_customers_by_level(level=level)
        
        if not records:
            with classification_list_container:
                ui.label('暂无客户分类记录').classes('text-grey')
            return
        
        with classification_list_container:
            ui.label(f'共 {len(records)} 条记录').classes('text-white q-mb-sm')
            
            for record in records:
                level_color = {
                    'A类': 'positive',
                    'B类': 'info',
                    'C类': 'warning',
                    'D类': 'negative',
                    '未分类': 'grey'
                }.get(record.customer_level, 'grey')
                
                with ui.card().classes('glass-card q-mb-sm'):
                    with ui.row().classes('w-full items-center'):
                        with ui.column().classes('col-grow'):
                            with ui.row().classes('items-center q-gutter-sm'):
                                ui.label(f'👨‍⚕️ {record.doctor_name}').classes('text-h6 text-white')
                                ui.badge(record.customer_level).props(f'color={level_color}')
                            
                            ui.label(f'🏥 {record.hospital} - {record.department}').classes('text-grey')
                            ui.label(f'📊 联系{record.total_contacts}次 | 回复{record.reply_count}次 | 回复率{record.reply_rate}%').classes('text-grey')
                            ui.label(f'⏰ 建议{record.suggested_follow_days}天跟进一次').classes('text-grey')
                            
                            if record.last_contact_date:
                                days_ago = (datetime.now() - datetime.fromisoformat(record.last_contact_date)).days
                                ui.label(f'🕐 最后联系：{days_ago}天前').classes('text-grey')
                        
                        with ui.column().classes('q-gutter-sm'):
                            ui.button('升级', on_click=lambda r=record: show_level_change_dialog(r, 'upgrade')).props('size=sm color=positive')
                            ui.button('降级', on_click=lambda r=record: show_level_change_dialog(r, 'downgrade')).props('size=sm color=warning')
                            ui.button('查看', on_click=lambda r=record: show_classification_detail(r)).props('size=sm color=info')
    
    level_filter.on('update:model-value', lambda: refresh_classification_list())
    refresh_classification_list()


def show_level_change_dialog(record, action):
    """显示等级变更对话框"""
    
    level_order = ['D类', 'C类', 'B类', 'A类']
    current_index = level_order.index(record.customer_level) if record.customer_level in level_order else 0
    
    if action == 'upgrade':
        if current_index >= len(level_order) - 1:
            ui.notify('已经是最高等级', type='warning')
            return
        new_level = level_order[current_index + 1]
        title = '⬆️ 升级客户等级'
    else:
        if current_index <= 0:
            ui.notify('已经是最低等级', type='warning')
            return
        new_level = level_order[current_index - 1]
        title = '⬇️ 降级客户等级'
    
    with ui.dialog() as dialog, ui.card().classes('w-full').style('max-width: 500px'):
        ui.label(title).classes('text-h6')
        
        with ui.column().classes('w-full q-gutter-md'):
            ui.label(f'客户：{record.doctor_name}').classes('text-white')
            ui.label(f'当前等级：{record.customer_level} → 新等级：{new_level}').classes('text-white')
            
            reason = ui.textarea(
                label='变更原因',
                placeholder='请说明等级变更的原因...'
            ).classes('w-full')
            
            def save_level_change():
                if not reason.value:
                    ui.notify('请填写变更原因', type='warning')
                    return
                
                customer_tracking_service.update_customer_level(
                    doctor_id=record.doctor_id,
                    new_level=new_level,
                    reason=reason.value
                )
                
                ui.notify(f'✅ 客户等级已更新为 {new_level}', type='positive')
                dialog.close()
                # 刷新当前页面
                ui.navigate.reload()
            
            with ui.row().classes('w-full justify-end'):
                ui.button('取消', on_click=dialog.close).props('flat')
                ui.button('确认', on_click=save_level_change).props('color=primary')
    
    dialog.open()


def show_classification_detail(record):
    """显示客户分类详情"""
    with ui.dialog() as dialog, ui.card().classes('w-full').style('max-width: 600px'):
        ui.label('📋 客户分类详情').classes('text-h6')
        
        with ui.column().classes('w-full q-gutter-sm'):
            ui.label(f'医生：{record.doctor_name}').classes('text-white')
            ui.label(f'医院：{record.hospital}').classes('text-grey')
            ui.label(f'科室：{record.department}').classes('text-grey')
            
            ui.separator()
            ui.label(f'客户等级：{record.customer_level}').classes('text-white')
            ui.label(f'建议跟进频率：每{record.suggested_follow_days}天').classes('text-grey')
            
            ui.separator()
            ui.label(f'总联系次数：{record.total_contacts}').classes('text-grey')
            ui.label(f'回复次数：{record.reply_count}').classes('text-grey')
            ui.label(f'回复率：{record.reply_rate}%').classes('text-grey')
            
            if record.last_contact_date:
                ui.label(f'最后联系：{record.last_contact_date}').classes('text-grey')
            
            if record.level_change_date:
                ui.separator()
                ui.label(f'上次等级：{record.last_level}').classes('text-grey')
                ui.label(f'变更时间：{record.level_change_date}').classes('text-grey')
                ui.label(f'变更原因：{record.level_change_reason}').classes('text-grey')
            
            ui.button('关闭', on_click=dialog.close).props('color=primary')
    
    dialog.open()


def export_classification_excel():
    """导出客户分类Excel"""
    try:
        filename = customer_tracking_service.export_to_excel(export_type='classification')
        ui.notify(f'✅ 已导出到：{filename}', type='positive')
    except Exception as e:
        ui.notify(f'❌ 导出失败：{str(e)}', type='negative')



def render_statistics_panel():
    """渲染统计分析表面板"""
    
    with ui.row().classes('w-full q-mb-md'):
        period_select = ui.select(
            label='统计周期',
            options=['本周', '本月', '自定义'],
            value='本周'
        ).classes('w-200px')
        
        ui.button('📊 生成统计', on_click=lambda: generate_statistics()).props('color=primary')
        ui.button('📤 导出Excel', on_click=lambda: export_statistics_excel()).props('color=info')
    
    # 统计结果容器
    statistics_container = ui.column().classes('w-full')
    
    def generate_statistics():
        """生成统计报告"""
        statistics_container.clear()
        
        # 计算日期范围
        if period_select.value == '本周':
            start_date = datetime.now() - timedelta(days=7)
            end_date = datetime.now()
            period = '周'
        elif period_select.value == '本月':
            start_date = datetime.now() - timedelta(days=30)
            end_date = datetime.now()
            period = '月'
        else:
            start_date = datetime.now() - timedelta(days=7)
            end_date = datetime.now()
            period = '周'
        
        # 生成统计
        stats = customer_tracking_service.generate_statistics(
            period=period,
            start_date=start_date,
            end_date=end_date
        )
        
        with statistics_container:
            # 标题
            ui.label(f'📊 {period}报统计').classes('text-h5 text-white q-mb-md')
            ui.label(f'{start_date.strftime("%Y-%m-%d")} 至 {end_date.strftime("%Y-%m-%d")}').classes('text-grey q-mb-md')
            
            # 核心指标卡片
            with ui.row().classes('w-full q-gutter-md q-mb-md'):
                # 新增客户
                with ui.card().classes('glass-card bg-positive'):
                    ui.label('新增客户').classes('text-white')
                    ui.label(str(stats.new_customers)).classes('text-h4 text-white')
                
                # A类客户
                with ui.card().classes('glass-card bg-info'):
                    ui.label('A类客户').classes('text-white')
                    ui.label(str(stats.a_level_count)).classes('text-h4 text-white')
                
                # 跟进次数
                with ui.card().classes('glass-card bg-warning'):
                    ui.label('跟进次数').classes('text-white')
                    ui.label(str(stats.total_follow_ups)).classes('text-h4 text-white')
                
                # 回复率
                with ui.card().classes('glass-card bg-secondary'):
                    ui.label('回复率').classes('text-white')
                    ui.label(f'{stats.reply_rate}%').classes('text-h4 text-white')
            
            # 客户分类统计
            with ui.card().classes('glass-card q-mb-md'):
                ui.label('客户分类统计').classes('text-h6 text-white q-mb-sm')
                
                with ui.row().classes('w-full q-gutter-md'):
                    with ui.column():
                        ui.label(f'A类客户：{stats.a_level_count}').classes('text-white')
                        ui.label(f'B类客户：{stats.b_level_count}').classes('text-white')
                    with ui.column():
                        ui.label(f'C类客户：{stats.c_level_count}').classes('text-white')
                        ui.label(f'D类客户：{stats.d_level_count}').classes('text-white')
            
            # 渠道统计
            if stats.channel_stats:
                with ui.card().classes('glass-card q-mb-md'):
                    ui.label('开发渠道统计').classes('text-h6 text-white q-mb-sm')
                    
                    for channel, count in stats.channel_stats.items():
                        ui.label(f'{channel}：{count} 个客户').classes('text-white')
            
            # 关键提示
            with ui.card().classes('glass-card bg-warning'):
                ui.label('⚠️ 管理提示').classes('text-h6 text-white q-mb-sm')
                ui.markdown(f"""
                - **A类客户必须增长**：当前 {stats.a_level_count} 个，目标是只增不减
                - **新增客户**：本{period}新增 {stats.new_customers} 个
                - **跟进效率**：回复率 {stats.reply_rate}%，需保持在 50% 以上
                - **重点关注**：D类客户 {stats.d_level_count} 个，考虑是否放弃或重新激活
                """).classes('text-white')
    
    generate_statistics()


def export_statistics_excel():
    """导出统计分析Excel"""
    try:
        filename = customer_tracking_service.export_to_excel(export_type='statistics')
        ui.notify(f'✅ 已导出到：{filename}', type='positive')
    except Exception as e:
        ui.notify(f'❌ 导出失败：{str(e)}', type='negative')


def render_pending_panel():
    """渲染待跟进提醒面板"""
    
    ui.label('⏰ 待跟进客户提醒').classes('text-h5 text-white q-mb-md')
    
    with ui.card().classes('glass-card q-mb-md'):
        ui.markdown("""
        ### 💡 跟进频率建议
        
        - **A类客户**：每 3-5 天跟进一次
        - **B类客户**：每 7 天跟进一次
        - **C类客户**：每 10 天跟进一次
        - **D类客户**：每 15 天跟进一次（或考虑放弃）
        
        系统会根据客户等级和最后联系时间，自动提醒你需要跟进的客户。
        """)
    
    ui.button('🔄 刷新', on_click=lambda: refresh_pending_list()).props('color=secondary q-mb-md')
    
    # 待跟进列表容器
    pending_list_container = ui.column().classes('w-full')
    
    def refresh_pending_list():
        """刷新待跟进列表"""
        pending_list_container.clear()
        
        pending = customer_tracking_service.get_pending_followups()
        
        if not pending:
            with pending_list_container:
                ui.label('✅ 太棒了！暂无需要跟进的客户').classes('text-positive')
            return
        
        with pending_list_container:
            ui.label(f'⚠️ 有 {len(pending)} 个客户需要跟进').classes('text-warning q-mb-sm')
            
            for item in pending:
                level_color = {
                    'A类': 'negative',  # A类逾期用红色强调
                    'B类': 'warning',
                    'C类': 'info',
                    'D类': 'grey'
                }.get(item['customer_level'], 'grey')
                
                with ui.card().classes(f'glass-card q-mb-sm border-l-4 border-{level_color}'):
                    with ui.row().classes('w-full items-center'):
                        with ui.column().classes('col-grow'):
                            with ui.row().classes('items-center q-gutter-sm'):
                                ui.label(f'👨‍⚕️ {item["doctor_name"]}').classes('text-h6 text-white')
                                ui.badge(item['customer_level']).props(f'color={level_color}')
                            
                            ui.label(f'📅 已 {item["days_since_last_contact"]} 天未联系').classes('text-grey')
                            ui.label(f'⏰ 建议每 {item["suggested_follow_days"]} 天跟进').classes('text-grey')
                            
                            if item['overdue_days'] > 0:
                                ui.label(f'⚠️ 逾期 {item["overdue_days"]} 天').classes('text-negative')
                        
                        with ui.column().classes('q-gutter-sm'):
                            ui.button(
                                '立即跟进',
                                on_click=lambda d_id=item['doctor_id']: quick_followup(d_id)
                            ).props('size=sm color=primary')
    
    def quick_followup(doctor_id):
        """快速跟进"""
        # 跳转到跟进记录添加
        show_add_followup_dialog()
    
    refresh_pending_list()
