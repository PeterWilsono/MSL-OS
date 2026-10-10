"""
数据中心和医院管理页面渲染方法
这些方法将被添加到 MedRepApp 类中
"""

# 这些方法需要添加到 ui/app.py 的 MedRepApp 类中

def render_data_center(self):
    """渲染数据中心页面"""
    from nicegui import ui
    from modules.data_center.service import data_center_service
    
    ui.label('🗄️ 数据中心').classes('page-title')
    
    # 数据统计概览
    with ui.card().classes('glass-card w-full q-pa-lg q-mb-lg'):
        ui.label('数据统计').classes('text-h6 text-white q-mb-md')
        
        summary = data_center_service.get_all_data_summary()
        
        with ui.grid(columns=5).classes('w-full q-gutter-md'):
            for key, count in summary.items():
                with ui.element('div').classes('stat-card'):
                    ui.label(str(count)).classes('stat-number')
                    labels = {
                        'hospitals': '医院',
                        'departments': '科室',
                        'products': '产品',
                        'competitors': '竞品',
                        'doctors': '医生',
                        'contacts': '联系人',
                        'visits': '拜访记录',
                        'interactions': '交流记录',
                        'knowledge_items': '知识条目',
                        'reflections': '个人反思'
                    }
                    ui.label(labels.get(key, key)).classes('stat-label')
    
    # 全局搜索
    with ui.card().classes('glass-card w-full q-pa-lg q-mb-lg'):
        ui.label('🔍 全局搜索').classes('text-h6 text-white q-mb-md')
        
        with ui.row().classes('w-full items-end q-gutter-md'):
            self.search_input = ui.input(
                label='输入关键字搜索所有数据',
                placeholder='例如：医生姓名、医院名称、产品名称等'
            ).classes('col-10 glass-input')
            
            ui.button('搜索', on_click=self.perform_global_search).classes('glass-btn col-2')
        
        # 搜索结果容器
        self.search_results_container = ui.column().classes('w-full q-mt-md')
    
    # 数据分类浏览
    with ui.card().classes('glass-card w-full q-pa-lg'):
        ui.label('📂 数据分类浏览').classes('text-h6 text-white q-mb-md')
        
        with ui.tabs().classes('w-full text-white glass-tabs') as tabs:
            tab_hospitals = ui.tab('医院')
            tab_products = ui.tab('产品')
            tab_competitors = ui.tab('竞品')
            tab_doctors = ui.tab('医生')
            tab_contacts = ui.tab('联系人')
            tab_knowledge = ui.tab('知识库')
        
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
    from nicegui import ui
    from modules.data_center.service import data_center_service
    
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
                for item in items[:10]:  # 每类最多显示10条
                    with ui.element('div').classes('glass-list-item'):
                        # 显示关键信息
                        name = item.get('name') or item.get('title', '未命名')
                        ui.label(name).classes('text-white font-bold')
                        
                        # 显示详细信息按钮
                        with ui.row().classes('q-mt-sm'):
                            ui.button('查看详情', on_click=lambda i=item, c=category: self.view_data_detail(c, i)).props('flat dense size=sm color=primary')


def render_data_table(self, category: str):
    """渲染数据表格"""
    from nicegui import ui
    from modules.data_center.service import data_center_service
    
    data = data_center_service.get_data_by_category(category)
    
    if not data:
        ui.label(f'暂无{category}数据').classes('text-secondary')
        return
    
    for item in data[:50]:  # 限制显示数量
        with ui.element('div').classes('glass-list-item'):
            with ui.row().classes('w-full items-center justify-between'):
                # 左侧：主要信息
                with ui.column().classes('col-grow'):
                    name = item.get('name') or item.get('title', '未命名')
                    ui.label(name).classes('text-white font-bold')
                    
                    # 显示次要信息
                    if category == 'hospitals':
                        ui.label(f"{item.get('level', '')} | {item.get('address', '')}").classes('text-caption text-secondary')
                    elif category == 'doctors':
                        ui.label(f"{item.get('hospital', '')} - {item.get('department', '')}").classes('text-caption text-secondary')
                    elif category == 'contacts':
                        ui.label(f"{item.get('contact_type', '')} | {item.get('organization', '')}").classes('text-caption text-secondary')
                
                # 右侧：操作按钮
                with ui.row().classes('q-gutter-sm'):
                    ui.button('查看', on_click=lambda i=item, c=category: self.view_data_detail(c, i)).props('flat dense size=sm color=primary')
                    ui.button('编辑', on_click=lambda i=item, c=category: self.edit_data(c, i)).props('flat dense size=sm color=secondary')
                    ui.button('删除', on_click=lambda i=item, c=category: self.delete_data_confirm(c, i)).props('flat dense size=sm color=negative')


def view_data_detail(self, category: str, item: dict):
    """查看数据详情"""
    from nicegui import ui
    import json
    
    content = json.dumps(item, ensure_ascii=False, indent=2)
    
    with ui.dialog() as dialog, ui.card().classes('glass-card w-full').style('max-width: 700px; max-height: 80vh; overflow-y: auto'):
        name = item.get('name') or item.get('title', '数据详情')
        ui.label(name).classes('text-h6 text-white q-mb-md')
        ui.code(content, language='json').classes('w-full')
        with ui.row().classes('w-full justify-end q-mt-md'):
            ui.button('关闭', on_click=dialog.close).classes('glass-btn')
    dialog.open()


def edit_data(self, category: str, item: dict):
    """编辑数据 - 跳转到对应的编辑页面"""
    from nicegui import ui
    
    if category == 'hospitals':
        self.navigate('hospitals')
    elif category == 'doctors':
        self.navigate('doctors')
    elif category == 'contacts':
        self.navigate('contacts')
    ui.notify(f'请在{category}管理页面进行编辑', type='info')


def delete_data_confirm(self, category: str, item: dict):
    """确认删除数据"""
    from nicegui import ui
    
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
    from nicegui import ui
    from modules.data_center.service import data_center_service
    
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
    from nicegui import ui
    
    ui.label('🏥 医院管理').classes('page-title')
    
    with ui.tabs().classes('w-full text-white glass-tabs') as tabs:
        tab_hospitals = ui.tab('医院')
        tab_departments = ui.tab('科室')
        tab_products = ui.tab('产品')
        tab_competitors = ui.tab('竞品')
    
    with ui.tab_panels(tabs, value=tab_hospitals).classes('w-full bg-transparent'):
        with ui.tab_panel(tab_hospitals):
            self.render_hospital_panel()
        with ui.tab_panel(tab_departments):
            self.render_department_panel()
        with ui.tab_panel(tab_products):
            self.render_product_panel()
        with ui.tab_panel(tab_competitors):
            self.render_competitor_panel()
