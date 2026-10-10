"""
AI 数据分析 UI - 美化版本
"""
from nicegui import ui
from typing import Optional
import asyncio

from core.ai_data_analyzer import ai_data_analyzer
from modules.hospital_manager.service import hospital_service


def render_ai_analysis_page():
    """渲染AI数据分析页面"""

    ui.label("🤖 AI 数据分析").classes("page-title")

    if not ai_data_analyzer.ai.is_enabled:
        with ui.card().classes("glass-card w-full p-4"):
            ui.label("⚠️ AI功能未启用").classes("text-h6 text-orange-4")
            ui.label("请在设置中配置API Key并启用AI功能").classes("text-secondary")
        return

    with ui.tabs().classes('w-full text-white glass-tabs') as tabs:
        tab_new = ui.tab('✨ 新建分析')
        tab_smart = ui.tab('📝 智能填表')
        tab_history = ui.tab('📋 历史记录')

    with ui.tab_panels(tabs, value=tab_new).classes('w-full bg-transparent'):
        with ui.tab_panel(tab_new):
            render_new_analysis_panel()

        with ui.tab_panel(tab_smart):
            render_smart_import_panel()

        with ui.tab_panel(tab_history):
            render_history_panel()


def render_new_analysis_panel():
    """渲染新建分析面板"""

    with ui.card().classes("glass-card w-full p-4 mb-4"):
        with ui.row().classes('items-center gap-3 mb-3'):
            ui.icon("tips_and_updates", color='blue-4').classes('text-2xl')
            ui.label("功能说明").classes("text-subtitle1 font-bold text-white")

        with ui.column().classes("gap-2 ml-2"):
            ui.label("AI数据分析可以帮助你：").classes("text-body2 text-grey")
            ui.label("• 分析医院的规模、科室分布、产品覆盖情况").classes("text-caption text-grey-4")
            ui.label("• 分析科室的特点、产品使用，开发策略").classes("text-caption text-grey-4")
            ui.label("• 分析医生的关系阶段、拜访历史、个性化建议").classes("text-caption text-grey-4")
            ui.label("• 分析整体业务战略和市场机会").classes("text-caption text-grey-4")

        ui.separator().classes('my-2')

        with ui.row().classes('gap-2 items-center'):
            ui.label("💡").classes('text-amber-4')
            ui.label("分析结果会缓存7天，节约token消耗").classes("text-caption text-grey")

    with ui.grid().classes('w-full gap-4 grid-cols-1 md:grid-cols-4 mb-4'):
        analysis_type = ui.select(
            ["医院分析", "科室分析", "医生分析", "整体战略"],
            label="分析类型",
            value="医院分析"
        ).classes('w-full glass-input')

    entity_select_container = ui.column().classes("w-full")
    result_container = ui.column().classes("w-full mt-4")
    cache_stats_container = ui.row().classes("w-full")

    def update_entity_selector():
        entity_select_container.clear()

        with entity_select_container:
            if analysis_type.value == "医院分析":
                hospitals = hospital_service.list_hospitals()
                if hospitals:
                    hospital_options = {h["name"]: h["hospital_id"] for h in hospitals}
                    with ui.grid().classes('w-full gap-4 grid-cols-1 md:grid-cols-2'):
                        selected_hospital = ui.select(
                            options=list(hospital_options.keys()),
                            label="选择医院",
                            value=list(hospital_options.keys())[0] if hospital_options else None
                        ).classes('w-full glass-input')

                        with ui.row().classes('items-end gap-2'):
                            ui.button("🚀 开始分析", on_click=lambda: analyze_entity(
                                hospital_options[selected_hospital.value], "hospital"
                            )).props("color=primary")
                            ui.button("🔄 强制刷新", on_click=lambda: analyze_entity(
                                hospital_options[selected_hospital.value], "hospital", force=True
                            )).props("color=secondary flat")
                else:
                    with ui.card().classes('glass-card-secondary w-full p-4'):
                        with ui.row().classes('items-center gap-2'):
                            ui.icon("info").classes('text-yellow-4')
                            ui.label("暂无医院数据").classes('text-white font-bold')
                        ui.label("请先在'数据管理 > 医院管理'中添加医院信息").classes('text-caption text-grey mt-2')

            elif analysis_type.value == "科室分析":
                departments = hospital_service.list_departments()
                if departments:
                    dept_options = {f"{d['name']}"[:50]: d["department_id"]
                                   for d in departments}
                    with ui.grid().classes('w-full gap-4 grid-cols-1 md:grid-cols-2'):
                        selected_dept = ui.select(
                            options=list(dept_options.keys()),
                            label="选择科室",
                            value=list(dept_options.keys())[0] if dept_options else None
                        ).classes('w-full glass-input')

                        with ui.row().classes('items-end gap-2'):
                            ui.button("🚀 开始分析", on_click=lambda: analyze_entity(
                                dept_options[selected_dept.value], "department"
                            )).props("color=primary")
                            ui.button("🔄 强制刷新", on_click=lambda: analyze_entity(
                                dept_options[selected_dept.value], "department", force=True
                            )).props("color=secondary flat")
                else:
                    with ui.card().classes('glass-card-secondary w-full p-4'):
                        with ui.row().classes('items-center gap-2'):
                            ui.icon("info").classes('text-yellow-4')
                            ui.label("暂无科室数据").classes('text-white font-bold')

            elif analysis_type.value == "医生分析":
                from core.file_manager import file_manager
                doctor_files = list(file_manager.doctors_dir.glob("*.json"))
                if doctor_files:
                    doctors = []
                    for f in doctor_files[:50]:
                        data = file_manager.read_json(f)
                        if data:
                            doctors.append({
                                "id": data.get("doctor_id"),
                                "name": data.get("name"),
                                "hospital": data.get("hospital", "")
                            })

                    if doctors:
                        doctor_options = {f"{d['name']} ({d['hospital']})"[:50]: d["id"] for d in doctors}
                        with ui.grid().classes('w-full gap-4 grid-cols-1 md:grid-cols-2'):
                            selected_doctor = ui.select(
                                options=list(doctor_options.keys()),
                                label="选择医生",
                                value=list(doctor_options.keys())[0] if doctor_options else None
                            ).classes('w-full glass-input')

                            with ui.row().classes('items-end gap-2'):
                                ui.button("🚀 开始分析", on_click=lambda: analyze_entity(
                                    doctor_options[selected_doctor.value], "doctor"
                                )).props("color=primary")
                                ui.button("🔄 强制刷新", on_click=lambda: analyze_entity(
                                    doctor_options[selected_doctor.value], "doctor", force=True
                                )).props("color=secondary flat")
                    else:
                        with ui.card().classes('glass-card-secondary w-full p-4'):
                            ui.label("暂无医生数据").classes('text-white font-bold')
                else:
                    with ui.card().classes('glass-card-secondary w-full p-4'):
                        ui.label("暂无医生数据").classes('text-white font-bold')

            elif analysis_type.value == "整体战略":
                with ui.card().classes('glass-card-secondary w-full p-4'):
                    ui.label("点击开始整体战略分析，将分析所有医院、科室、医生的整体情况").classes('text-caption text-grey mb-3')
                    ui.button("🚀 开始整体分析", on_click=analyze_overall).props("color=primary")

    async def analyze_entity(entity_id: str, entity_type: str, force: bool = False):
        result_container.clear()

        with result_container:
            with ui.card().classes('glass-card w-full p-6'):
                with ui.row().classes('items-center gap-3'):
                    ui.spinner(size="lg", color='primary')
                    ui.label("分析中...").classes("text-white text-lg")

        try:
            if entity_type == "hospital":
                result = await ai_data_analyzer.analyze_hospital(entity_id, force_refresh=force)
            elif entity_type == "department":
                result = await ai_data_analyzer.analyze_department(entity_id, force_refresh=force)
            elif entity_type == "doctor":
                result = await ai_data_analyzer.analyze_doctor(entity_id, force_refresh=force)
            else:
                result = {"error": "未知实体类型"}

            result_container.clear()
            with result_container:
                if "error" in result:
                    with ui.card().classes('glass-card-secondary w-full p-4'):
                        ui.label(f"❌ {result['error']}").classes("text-red-4")
                else:
                    cache_badge = f"📦 来自缓存 ({result.get('cached_at', '')[:16]})" if result.get("from_cache") else "✨ 新分析"

                    with ui.card().classes('glass-card w-full p-4'):
                        ui.label(cache_badge).classes("text-caption text-grey mb-3")

                        ui.label("📊 分析摘要").classes("text-subtitle1 font-bold text-white mb-2")
                        ui.label(result.get("summary", "")).classes("text-body2 text-grey leading-relaxed")

                        if result.get("key_insights"):
                            ui.separator().classes('my-3')
                            ui.label("💡 关键洞察").classes("text-subtitle1 font-bold text-blue-4 mb-2")
                            for insight in result["key_insights"]:
                                with ui.row().classes('gap-2 mb-2'):
                                    ui.label("•").classes("text-blue-4 text-lg")
                                    ui.label(insight).classes("text-body2 text-grey leading-relaxed")

                        if result.get("recommendations"):
                            ui.separator().classes('my-3')
                            ui.label("🎯 建议").classes("text-subtitle1 font-bold text-green-4 mb-2")
                            for rec in result["recommendations"]:
                                with ui.row().classes('gap-2 mb-2'):
                                    ui.label("→").classes("text-green-4 text-lg")
                                    ui.label(rec).classes("text-body2 text-grey leading-relaxed")

                        if result.get("full_response"):
                            with ui.expansion("查看完整分析", icon="description").classes('mt-4 glass-expansion'):
                                ui.label(result["full_response"]).classes("text-caption text-grey whitespace-pre-wrap leading-relaxed")

            update_cache_stats()

        except Exception as e:
            result_container.clear()
            with result_container:
                with ui.card().classes('glass-card-secondary w-full p-4'):
                    ui.label(f"❌ 分析失败: {str(e)}").classes("text-red-4")

    async def analyze_overall():
        result_container.clear()

        with result_container:
            with ui.card().classes('glass-card w-full p-6'):
                with ui.row().classes('items-center gap-3'):
                    ui.spinner(size="lg", color='primary')
                    ui.label("整体分析中...").classes("text-white text-lg")

        try:
            result = await ai_data_analyzer.analyze_overall_strategy()

            result_container.clear()
            with result_container:
                if "error" in result:
                    with ui.card().classes('glass-card-secondary w-full p-4'):
                        ui.label(f"❌ {result['error']}").classes("text-red-4")
                else:
                    with ui.card().classes('glass-card w-full p-4'):
                        if result.get("data_stats"):
                            stats = result["data_stats"]
                            with ui.grid().classes('w-full gap-3 grid-cols-2 md:grid-cols-4 mb-4'):
                                with ui.card().classes('glass-card-secondary p-3 text-center'):
                                    ui.label(f"{stats['hospitals']}").classes('text-2xl font-bold text-blue-4')
                                    ui.label("🏥 医院").classes('text-caption text-grey')
                                with ui.card().classes('glass-card-secondary p-3 text-center'):
                                    ui.label(f"{stats['departments']}").classes('text-2xl font-bold text-cyan-4')
                                    ui.label("🏢 科室").classes('text-caption text-grey')
                                with ui.card().classes('glass-card-secondary p-3 text-center'):
                                    ui.label(f"{stats['products']}").classes('text-2xl font-bold text-green-4')
                                    ui.label("💊 产品").classes('text-caption text-grey')
                                with ui.card().classes('glass-card-secondary p-3 text-center'):
                                    ui.label(f"{stats['doctors']}").classes('text-2xl font-bold text-indigo-4')
                                    ui.label("👨‍⚕️ 医生").classes('text-caption text-grey')

                        ui.separator().classes('my-3')

                        ui.label("📊 业务现状").classes("text-subtitle1 font-bold text-white mb-2")
                        ui.label(result.get("summary", "")).classes("text-body2 text-grey leading-relaxed")

                        if result.get("key_insights"):
                            ui.separator().classes('my-3')
                            ui.label("💡 关键发现").classes("text-subtitle1 font-bold text-blue-4 mb-2")
                            for insight in result["key_insights"]:
                                with ui.row().classes('gap-2 mb-2'):
                                    ui.label("•").classes("text-blue-4 text-lg")
                                    ui.label(insight).classes("text-body2 text-grey leading-relaxed")

                        if result.get("recommendations"):
                            ui.separator().classes('my-3')
                            ui.label("🎯 战略建议").classes("text-subtitle1 font-bold text-green-4 mb-2")
                            for rec in result["recommendations"]:
                                with ui.row().classes('gap-2 mb-2'):
                                    ui.label("→").classes("text-green-4 text-lg")
                                    ui.label(rec).classes("text-body2 text-grey leading-relaxed")

                        if result.get("full_response"):
                            with ui.expansion("查看完整分析", icon="description").classes('mt-4 glass-expansion'):
                                ui.label(result["full_response"]).classes("text-caption text-grey whitespace-pre-wrap leading-relaxed")

        except Exception as e:
            result_container.clear()
            with result_container:
                with ui.card().classes('glass-card-secondary w-full p-4'):
                    ui.label(f"❌ 分析失败: {str(e)}").classes("text-red-4")

    def update_cache_stats():
        cache_stats_container.clear()

        with cache_stats_container:
            stats = ai_data_analyzer.get_cache_stats()

            with ui.card().classes('glass-card p-3'):
                with ui.row().classes('items-center gap-4'):
                    ui.label("📦 缓存统计").classes('font-bold text-white')
                    ui.label(f"共 {stats['total_caches']} 个").classes('text-caption text-grey')

                    if stats.get("by_type"):
                        type_names = {"hospital": "医院", "department": "科室", "doctor": "医生"}
                        for entity_type, count in stats["by_type"].items():
                            ui.label(f"{type_names.get(entity_type, entity_type)}: {count}").classes("text-caption text-grey")

                    ui.button("🗑️ 清理旧缓存", on_click=cleanup_caches).props("flat dense size=sm color=warning")

    def cleanup_caches():
        count = ai_data_analyzer.cleanup_old_caches(30)
        ui.notify(f"已清理 {count} 个旧缓存", type="positive")
        update_cache_stats()

    analysis_type.on_value_change(lambda: update_entity_selector())

    update_entity_selector()
    update_cache_stats()


def render_history_panel():
    """渲染历史记录面板"""

    with ui.card().classes('glass-card w-full p-4 mb-4'):
        with ui.row().classes('items-center gap-3 mb-2'):
            ui.icon("history", color='primary').classes('text-xl')
            ui.label("📋 历史分析记录").classes("text-subtitle1 font-bold text-white")

    from core.file_manager import file_manager
    cache_dir = file_manager.data_dir / "ai_analysis_cache"

    if not cache_dir.exists() or not list(cache_dir.glob("*.json")):
        with ui.card().classes('glass-card w-full p-6'):
            with ui.column().classes('items-center gap-2'):
                ui.icon("folder_open", size="xl", color='grey').classes('')
                ui.label("暂无历史记录").classes('text-h6 text-grey')
                ui.label("进行AI分析后，记录会自动保存在这里").classes('text-caption text-grey-4')
        return

    cache_files = []
    for cache_file in cache_dir.glob("*.json"):
        try:
            data = file_manager.read_json(cache_file)
            if data:
                data['_filename'] = cache_file.name
                cache_files.append(data)
        except Exception as e:
            print(f"读取缓存文件失败: {e}")
            continue

    cache_files.sort(key=lambda x: x.get('last_updated', ''), reverse=True)

    with ui.grid().classes('w-full gap-4 grid-cols-1 md:grid-cols-4 mb-4'):
        filter_type = ui.select(
            ["全部", "医院", "科室", "医生"],
            label="类型筛选",
            value="全部"
        ).classes('w-full glass-input')

        search_input = ui.input(
            label="搜索",
            placeholder="输入关键词搜索..."
        ).classes('w-full glass-input')

    records_container = ui.column().classes("w-full gap-4")

    def update_records_display():
        records_container.clear()

        filtered_records = cache_files.copy()

        if filter_type.value != "全部":
            type_map = {"医院": "hospital", "科室": "department", "医生": "doctor"}
            target_type = type_map.get(filter_type.value)
            filtered_records = [r for r in filtered_records if r.get('entity_type') == target_type]

        if search_input.value:
            keyword = search_input.value.lower()
            filtered_records = [
                r for r in filtered_records
                if keyword in r.get('summary', '').lower()
                or keyword in str(r.get('key_insights', [])).lower()
                or keyword in str(r.get('recommendations', [])).lower()
            ]

        with records_container:
            if not filtered_records:
                with ui.card().classes('glass-card w-full p-4'):
                    ui.label("🔍 未找到匹配的记录").classes('text-grey')
                return

            for idx, record in enumerate(filtered_records, 1):
                render_analysis_record(record, idx)

    def render_analysis_record(record: dict, index: int):
        entity_type = record.get('entity_type', 'unknown')
        entity_id = record.get('entity_id', '')
        last_updated = record.get('last_updated', '')[:19]

        entity_name = get_entity_name(entity_id, entity_type)

        type_icons = {"hospital": "🏥", "department": "🏢", "doctor": "👨‍⚕️"}
        type_names = {"hospital": "医院", "department": "科室", "doctor": "医生"}
        type_colors = {"hospital": "blue", "department": "cyan", "doctor": "indigo"}

        icon = type_icons.get(entity_type, "📄")
        type_name = type_names.get(entity_type, entity_type)
        color = type_colors.get(entity_type, "grey")

        with ui.card().classes('glass-card w-full p-4'):
            with ui.row().classes('w-full items-center justify-between mb-3'):
                with ui.row().classes('items-center gap-3'):
                    ui.label(f"{index}").classes('text-grey text-lg w-6')
                    ui.label(icon).classes('text-2xl')
                    ui.label(entity_name).classes('text-white font-bold text-body1')
                    ui.badge(type_name).props(f"color={color}")

                with ui.row().classes('gap-2'):
                    ui.button("👁️", on_click=lambda r=record: show_record_detail(r)).props('flat dense size=sm color=primary')
                    ui.button("🗑️", on_click=lambda r=record: delete_record_confirm(r)).props('flat dense size=sm color=negative')

            ui.label(f"📅 {last_updated}").classes('text-caption text-grey mb-2')

            summary = record.get('summary', '')
            if summary:
                preview = summary[:120] + "..." if len(summary) > 120 else summary
                ui.label(preview).classes('text-body2 text-grey leading-relaxed')

            insights_count = len(record.get('key_insights', []))
            recs_count = len(record.get('recommendations', []))

            with ui.row().classes('gap-4 mt-2'):
                if insights_count > 0:
                    ui.label(f"💡 {insights_count} 个洞察").classes('text-caption text-blue-4')
                if recs_count > 0:
                    ui.label(f"🎯 {recs_count} 条建议").classes('text-caption text-green-4')

    def get_entity_name(entity_id: str, entity_type: str) -> str:
        try:
            if entity_type == "hospital":
                hospital = hospital_service.get_hospital(entity_id)
                return hospital.name if hospital else entity_id
            elif entity_type == "department":
                dept = hospital_service.get_department(entity_id)
                return dept.name if dept else entity_id
            elif entity_type == "doctor":
                from modules.doctor_manager.service import doctor_service
                doctor = doctor_service.get_doctor(entity_id)
                return doctor.name if doctor else entity_id
        except:
            pass
        return entity_id

    def show_record_detail(record: dict):
        with ui.dialog() as dialog, ui.card().classes('glass-card w-full').style('max-width: 800px; max-height: 80vh; overflow-y: auto'):
            entity_name = get_entity_name(record.get('entity_id'), record.get('entity_type'))
            type_names = {"hospital": "医院", "department": "科室", "doctor": "医生"}
            type_name = type_names.get(record.get('entity_type'), '')

            with ui.row().classes('w-full items-center justify-between mb-4'):
                ui.label(f"📊 {entity_name}").classes('text-h6 text-white')
                ui.badge(type_name).props('color=primary')

            ui.label(f"分析时间: {record.get('last_updated', '')[:19]}").classes('text-caption text-grey mb-4')

            if record.get('summary'):
                ui.label("📊 分析摘要").classes('text-subtitle1 font-bold text-white mb-2')
                ui.label(record['summary']).classes('text-body2 text-grey leading-relaxed')

            if record.get('key_insights'):
                ui.separator().classes('my-3')
                ui.label("💡 关键洞察").classes('text-subtitle1 font-bold text-blue-4 mb-2')
                for insight in record['key_insights']:
                    with ui.row().classes('gap-2 mb-2'):
                        ui.label("•").classes('text-blue-4 text-lg')
                        ui.label(insight).classes('text-body2 text-grey leading-relaxed')

            if record.get('recommendations'):
                ui.separator().classes('my-3')
                ui.label("🎯 建议").classes('text-subtitle1 font-bold text-green-4 mb-2')
                for rec in record['recommendations']:
                    with ui.row().classes('gap-2 mb-2'):
                        ui.label("→").classes('text-green-4 text-lg')
                        ui.label(rec).classes('text-body2 text-grey leading-relaxed')

            if record.get('data_snapshot'):
                with ui.expansion("查看数据快照", icon="data_object").classes('mt-4 glass-expansion'):
                    ui.json_editor({'content': {'json': record['data_snapshot']}}).classes("w-full")

            with ui.row().classes('w-full justify-end mt-4'):
                ui.button("关闭", on_click=dialog.close).props("flat color=primary")

        dialog.open()

    def delete_record_confirm(record: dict):
        entity_name = get_entity_name(record.get('entity_id'), record.get('entity_type'))

        with ui.dialog() as dialog, ui.card().classes('glass-card'):
            ui.label("⚠️ 确认删除").classes('text-h6 text-white mb-2')
            ui.label(f"确定要删除 {entity_name} 的分析记录吗？").classes('text-body2 text-grey mb-2')
            ui.label("此操作不可逆！").classes('text-red-4 font-bold mb-4')

            with ui.row().classes('gap-2'):
                ui.button("取消", on_click=dialog.close).props('flat')
                ui.button("确认删除", on_click=lambda: delete_record_execute(record, dialog)).props("color=negative")

        dialog.open()

    def delete_record_execute(record: dict, dialog):
        try:
            cache_file = cache_dir / record.get('_filename')
            if cache_file.exists():
                cache_file.unlink()
                ui.notify("记录已删除", type="positive")
                dialog.close()
                ui.timer(0.1, lambda: update_records_display(), once=True)
            else:
                ui.notify("记录不存在", type="warning")
        except Exception as e:
            ui.notify(f"删除失败: {str(e)}", type="negative")

    filter_type.on_value_change(lambda: update_records_display())
    search_input.on_value_change(lambda: update_records_display())

    update_records_display()


def render_smart_import_panel():
    """渲染智能填表面板 - 从随手笔记导入"""

    with ui.card().classes("glass-card w-full p-4 mb-4"):
        with ui.row().classes('items-center gap-3 mb-3'):
            ui.icon("auto_awesome", color='amber-4').classes('text-2xl')
            ui.label("智能填表").classes("text-subtitle1 font-bold text-white")
            ui.badge("AI辅助").props("color=amber")

        with ui.column().classes("gap-2 ml-2"):
            ui.label("将您的随手笔记粘贴到下方，AI会自动解析并填入拜访记录").classes("text-body2 text-grey")
            ui.label("• 支持识别日期、医院、医生、交流内容").classes("text-caption text-grey-4")
            ui.label("• 自动匹配系统中的医生信息").classes("text-caption text-grey-4")
            ui.label("• 只新增不覆盖，确认后再写入").classes("text-caption text-grey-4")

    notes_input = ui.textarea(
        label="粘贴随手笔记",
        placeholder="例如：\n周一 宝石花：赵瑜，拿了瓶水寒暄\n中医院：耿慧说竞品多\n3.17周二 盘山县：心内科刘志勇聊了很多..."
    ).classes('w-full glass-input').props('rows=8')

    with ui.row().classes('gap-3 mt-3'):
        ui.button("🔄 AI解析", on_click=lambda: parse_notes(notes_input.value)).props("color=primary")
        ui.button("🗑️ 清空", on_click=lambda: [notes_input.set_value(''), clear_preview()]).props("flat color=grey")

    preview_container = ui.column().classes('w-full mt-4')

    parsed_data = {'visits': [], 'raw': ''}

    def clear_preview():
        nonlocal parsed_data
        parsed_data = {'visits': [], 'raw': ''}
        preview_container.clear()

    async def parse_notes(raw_text: str):
        if not raw_text or not raw_text.strip():
            ui.notify('请先粘贴笔记内容', type='warning')
            return

        preview_container.clear()
        parsed_data['raw'] = raw_text

        with preview_container:
            with ui.card().classes('glass-card w-full p-4'):
                with ui.row().classes('items-center gap-3'):
                    ui.spinner(size='lg', color='primary')
                    ui.label("AI正在解析笔记...").classes('text-white text-lg')

        try:
            result = await ai_data_analyzer.parse_visit_notes(raw_text)
            parsed_data['visits'] = result.get('parsed_visits', [])

            render_preview(parsed_data['visits'])

        except Exception as e:
            preview_container.clear()
            with preview_container:
                with ui.card().classes('glass-card-secondary w-full p-4'):
                    ui.label(f"❌ 解析失败: {str(e)}").classes('text-red-4')

    def render_preview(visits: list):
        preview_container.clear()

        if not visits:
            with preview_container:
                with ui.card().classes('glass-card w-full p-4'):
                    ui.label("🔍 未解析到拜访记录，请检查笔记格式").classes('text-grey')
            return

        editable_visits = []
        edit_states = {}

        def toggle_edit(visit_idx, hosp_idx, doc_idx):
            key = f"{visit_idx}_{hosp_idx}_{doc_idx}"
            edit_states[key] = not edit_states.get(key, False)
            refresh_preview()

        def render_visit_card(visit_idx: int, hosp_idx: int, doc_idx: int):
            visit = editable_visits[visit_idx]
            hosp = visit['hospitals'][hosp_idx]
            doc = hosp['doctors'][doc_idx]

            key = f"{visit_idx}_{hosp_idx}_{doc_idx}"
            is_editing = edit_states.get(key, False)

            with ui.card().classes('bg-grey-9 w-full p-3 mb-2'):
                if is_editing:
                    with ui.column().classes('gap-2'):
                        doc['name'] = doc.get('edit_name', doc.get('name', ''))
                        doc_input = ui.input(
                            value=doc['name'],
                            placeholder='医生姓名'
                        ).classes('w-full').props('dense')
                        doc_input.on_value_change(lambda v, d=doc: d.update({'edit_name': v, 'name': v}))

                        hosp['name'] = hosp.get('edit_name', hosp.get('name', ''))
                        hosp_input = ui.input(
                            value=hosp['name'],
                            placeholder='医院名称'
                        ).classes('w-full').props('dense')
                        hosp_input.on_value_change(lambda v, h=hosp: h.update({'edit_name': v, 'name': v}))

                        doc['content'] = doc.get('edit_content', doc.get('content', ''))
                        content_input = ui.textarea(
                            value=doc['content'],
                            placeholder='交流内容...'
                        ).classes('w-full').props('rows=2 dense')
                        content_input.on_value_change(lambda v, d=doc: d.update({'edit_content': v, 'content': v}))

                        with ui.row().classes('gap-2'):
                            ui.button("✅ 完成", on_click=lambda *a: toggle_edit(visit_idx, hosp_idx, doc_idx)).props('color=positive size=sm')
                            ui.button("🗑️ 删除此医生", on_click=lambda *a: delete_doctor(visit_idx, hosp_idx, doc_idx)).props('color=negative size=sm flat')
                else:
                    doc_name = doc.get('name', '未知')
                    content = doc.get('content', '')
                    department = doc.get('department', '')
                    status = doc.get('status', 'new')
                    matched = doc.get('matched', False)
                    matched_id = doc.get('matched_doctor_id', '')

                    status_icon = '✅' if status == 'exists' else '🆕'
                    if matched and matched_id:
                        match_icon = '🎯'
                        match_color = 'text-green-4'
                    elif matched and not matched_id:
                        match_icon = '⚠️'
                        match_color = 'text-yellow-4'
                    else:
                        match_icon = '❌'
                        match_color = 'text-red-4'

                    with ui.column().classes('w-full ml-6'):
                        with ui.row().classes('items-center gap-2 mb-1'):
                            ui.label(status_icon).classes('text-lg')
                            ui.label(f"{match_icon} {doc_name}").classes(f'text-body2 text-white font-bold {match_color}')
                            if department:
                                ui.label(f"({department})").classes('text-caption text-grey')
                            ui.button(icon='edit', on_click=lambda *a: toggle_edit(visit_idx, hosp_idx, doc_idx)).props('flat dense round size=sm color=primary')
                            if doc.get('deletable', True):
                                ui.button(icon='delete', on_click=lambda *a: delete_doctor(visit_idx, hosp_idx, doc_idx)).props('flat dense round size=sm color=negative')

                        if content:
                            content_short = content[:80] + '...' if len(content) > 80 else content
                            ui.label(content_short).classes('text-caption text-grey leading-relaxed ml-6')

                        if not matched or not matched_id:
                            ui.label('⚠️ 未匹配到系统医生，导入后将创建临时记录').classes('text-caption text-yellow-4 ml-6')

        def delete_doctor(visit_idx, hosp_idx, doc_idx):
            hosp = editable_visits[visit_idx]['hospitals'][hosp_idx]
            hosp['doctors'].pop(doc_idx)
            if not hosp['doctors']:
                editable_visits[visit_idx]['hospitals'].pop(hosp_idx)
            if not editable_visits[visit_idx]['hospitals']:
                editable_visits.pop(visit_idx)
            refresh_preview()

        def delete_visit(visit_idx):
            editable_visits.pop(visit_idx)
            refresh_preview()

        def refresh_preview():
            preview_container.clear()
            with preview_container:
                if not editable_visits:
                    with ui.card().classes('glass-card w-full p-4'):
                        ui.label("已删除所有记录").classes('text-grey')
                    return

                with ui.card().classes('glass-card w-full p-4 mb-4'):
                    with ui.row().classes('items-center justify-between mb-3'):
                        ui.label("📋 解析预览（可编辑）").classes('text-subtitle1 font-bold text-white')
                        ui.label(f"共 {len(editable_visits)} 天记录").classes('text-caption text-grey')

                for idx, visit in enumerate(editable_visits):
                    date = visit.get('date', '未知日期')
                    day_color = 'blue' if '周二' in date or '周四' in date else 'indigo' if '周三' in date or '周五' in date else 'grey'

                    with ui.card().classes('glass-card w-full p-4 mb-4'):
                        with ui.row().classes('items-center justify-between mb-3'):
                            with ui.row().classes('items-center gap-3'):
                                ui.label(f"{idx + 1}").classes(f'text-lg font-bold text-{day_color}-4')
                                ui.label(f"📅 {date}").classes('text-white font-bold')
                                doctor_count = sum(len(h.get('doctors', [])) for h in visit.get('hospitals', []))
                                ui.label(f"👨‍⚕️ {doctor_count} 位医生").classes('text-caption text-grey')
                            ui.button(icon='delete', on_click=lambda *a: delete_visit(idx)).props('flat dense round size=sm color=negative')

                        for hosp_idx, hosp in enumerate(visit.get('hospitals', [])):
                            hosp_name = hosp.get('name', '未知医院')

                            with ui.card().classes('bg-grey-9 w-full p-3 mb-2'):
                                with ui.row().classes('items-center gap-2 mb-2'):
                                    ui.label("🏥").classes('text-lg')
                                    ui.label(hosp_name).classes('text-body2 text-white font-bold')

                                for doc_idx, doc in enumerate(hosp.get('doctors', [])):
                                    render_visit_card(idx, hosp_idx, doc_idx)

                with ui.card().classes('glass-card w-full p-4'):
                    with ui.row().classes('gap-3 justify-end'):
                        ui.button("🔄 重新解析", on_click=lambda: clear_preview()).props('flat color=grey')
                        ui.button("❌ 取消", on_click=lambda: clear_preview()).props('flat')
                        ui.button("✅ 确认导入", on_click=lambda: confirm_import(editable_visits)).props("color=positive")

        editable_visits.clear()
        editable_visits.extend([v.copy() for v in visits])
        for v in editable_visits:
            v['hospitals'] = [h.copy() for h in v.get('hospitals', [])]
            for h in v['hospitals']:
                h['doctors'] = [d.copy() for d in h.get('doctors', [])]

        refresh_preview()

    async def confirm_import(visits: list):
        if not visits:
            ui.notify('没有可导入的记录', type='warning')
            return

        progress_card = ui.card().classes('glass-card w-full p-6')
        with progress_card:
            with ui.column().classes('items-center gap-3'):
                ui.spinner(size='lg', color='positive')
                ui.label("正在导入...").classes('text-white text-lg')

        loop = asyncio.get_event_loop()

        def do_import():
            success_count = 0
            fail_count = 0
            skip_count = 0
            errors = []

            for visit in visits:
                try:
                    for hosp in visit.get('hospitals', []):
                        for doc in hosp.get('doctors', []):
                            if doc.get('status') == 'exists':
                                continue

                            doctor_id = doc.get('matched_doctor_id', '')
                            if not doctor_id:
                                doctor_id = doc.get('doctor_id', '')

                            if not doctor_id or not doctor_id.strip():
                                skip_count += 1
                                continue

                            if not doctor_id.startswith('doctor_'):
                                doctor_id = f'doctor_{doctor_id}'

                            from modules.visit_summary.service import visit_summary_service

                            visit_summary_service.create_visit_summary(
                                doctor_id=doctor_id,
                                visit_date=visit.get('parsed_date', ''),
                                key_topics=doc.get('content', ''),
                                doctor_concerns='',
                                objections='',
                                responses='',
                                response_effectiveness=3,
                                emotional_tone='',
                                new_insights='',
                                follow_up_tasks=doc.get('insights', '')
                            )
                            success_count += 1
                except Exception as e:
                    fail_count += 1
                    errors.append(str(e))
                    print(f"导入失败: {e}")

            return success_count, fail_count, skip_count, errors

        try:
            result = await loop.run_in_executor(None, do_import)
            success_count, fail_count, skip_count, errors = result

            progress_card.clear()
            with progress_card:
                if fail_count == 0 and skip_count == 0:
                    with ui.column().classes('items-center gap-3'):
                        ui.icon("check_circle", size="xl", color='positive').classes('')
                        ui.label("✅ 导入成功！").classes('text-h6 text-white')
                        ui.label(f"共导入 {success_count} 条拜访记录").classes('text-body2 text-grey')
                elif fail_count == 0:
                    with ui.column().classes('items-center gap-3'):
                        ui.icon("check_circle", size="xl", color='positive').classes('')
                        ui.label("✅ 导入完成！").classes('text-h6 text-white')
                        ui.label(f"导入 {success_count} 条，跳过 {skip_count} 条（无医生ID）").classes('text-body2 text-grey')
                else:
                    with ui.column().classes('items-center gap-3'):
                        ui.icon("warning", size="xl", color='yellow').classes('')
                        ui.label(f"⚠️ 导入成功: {success_count} 条，跳过: {skip_count} 条，失败: {fail_count} 条").classes('text-yellow-4')
                        if errors:
                            ui.label(f"错误: {errors[:3]}").classes('text-caption text-red-4')
        except Exception as e:
            progress_card.clear()
            with progress_card:
                with ui.column().classes('items-center gap-3'):
                    ui.icon("error", size="xl", color='negative').classes('')
                    ui.label(f"❌ 导入失败: {str(e)}").classes('text-red-4')