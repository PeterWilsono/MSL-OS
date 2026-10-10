    # ==================== 数据中心和医院管理页面 ====================
    
    def render_data_center(self):
        """渲染数据中心页面"""
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
    
    def render_hospital_panel(self):
        """渲染医院管理面板"""
        with ui.row().classes('w-full q-gutter-md'):
            # 左侧：添加/编辑表单
            with ui.card().classes('glass-card col-4 q-pa-lg'):
                form_label = ui.label('添加医院').classes('text-h6 text-white q-mb-md')
                
                name_input = ui.input(label='医院名称').classes('w-full glass-input')
                level_input = ui.select(
                    label='医院等级',
                    options=['三甲', '三乙', '二甲', '二乙', '一甲', '一乙', '其他']
                ).classes('w-full glass-input')
                address_input = ui.input(label='地址').classes('w-full glass-input')
                phone_input = ui.input(label='联系电话').classes('w-full glass-input')
                notes_input = ui.textarea(label='备注').classes('w-full glass-input')
                
                current_edit_id = {'value': None}
                
                def reset_form():
                    name_input.value = ''
                    level_input.value = ''
                    address_input.value = ''
                    phone_input.value = ''
                    notes_input.value = ''
                    current_edit_id['value'] = None
                    form_label.text = '添加医院'
                    save_btn.text = '保存'
                
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
                
                with ui.row().classes('q-mt-md'):
                    save_btn = ui.button('保存', on_click=save_hospital).classes('glass-btn')
                    ui.button('重置', on_click=reset_form).classes('glass-btn-secondary')
            
            # 右侧：医院列表
            with ui.card().classes('glass-card col-7 q-pa-lg'):
                ui.label('医院列表').classes('text-h6 text-white q-mb-md')
                list_container = ui.column().classes('w-full')
                
                def load_for_edit(item):
                    name_input.value = item.get('name', '')
                    level_input.value = item.get('level', '')
                    address_input.value = item.get('address', '')
                    phone_input.value = item.get('contact_phone', '')
                    notes_input.value = item.get('notes', '')
                    current_edit_id['value'] = item['hospital_id']
                    form_label.text = '编辑医院'
                    save_btn.text = '更新'
                    ui.notify('已加载医院信息', type='info')
                
                def delete_item(item_id):
                    hospital_service.delete_hospital(item_id)
                    ui.notify('医院已删除', type='positive')
                    if current_edit_id['value'] == item_id:
                        reset_form()
                    refresh_list()
                
                def refresh_list():
                    list_container.clear()
                    with list_container:
                        hospitals = hospital_service.list_hospitals()
                        for hospital in hospitals:
                            with ui.element('div').classes('glass-list-item'):
                                with ui.row().classes('w-full items-center justify-between'):
                                    with ui.column():
                                        ui.label(hospital['name']).classes('text-white font-bold')
                                        ui.label(f"{hospital.get('level', '')} | {hospital.get('address', '')}").classes('text-caption text-secondary')
                                    with ui.row():
                                        ui.button('编辑', on_click=lambda h=hospital: load_for_edit(h)).props('flat dense size=sm color=primary')
                                        ui.button('删除', on_click=lambda h=hospital: delete_item(h['hospital_id'])).props('flat dense size=sm color=negative')
                
                refresh_list()
    
    def render_department_panel(self):
        """渲染科室管理面板"""
        with ui.row().classes('w-full q-gutter-md'):
            # 左侧：添加科室
            with ui.card().classes('glass-card col-4 q-pa-lg'):
                ui.label('添加科室').classes('text-h6 text-white q-mb-md')
                
                # 选择医院
                hospitals = hospital_service.list_hospitals()
                hospital_options = {h['hospital_id']: h['name'] for h in hospitals}
                
                hospital_select = ui.select(
                    label='所属医院',
                    options=hospital_options
                ).classes('w-full glass-input')
                
                name_input = ui.input(label='科室名称').classes('w-full glass-input')
                desc_input = ui.textarea(label='科室描述').classes('w-full glass-input')
                head_input = ui.input(label='科室主任').classes('w-full glass-input')
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
                
                ui.button('保存', on_click=save_department).classes('glass-btn q-mt-md')
            
            # 右侧：科室列表
            with ui.card().classes('glass-card col-7 q-pa-lg'):
                ui.label('科室列表').classes('text-h6 text-white q-mb-md')
                dept_list_container = ui.column().classes('w-full')
                
                def refresh_dept_list():
                    dept_list_container.clear()
                    with dept_list_container:
                        departments = hospital_service.list_departments()
                        for dept in departments:
                            with ui.element('div').classes('glass-list-item'):
                                with ui.row().classes('w-full items-center justify-between'):
                                    with ui.column():
                                        ui.label(dept['name']).classes('text-white font-bold')
                                        ui.label(f"主任: {dept.get('head_doctor', '未设置')}").classes('text-caption text-secondary')
                                    ui.button('删除', on_click=lambda d=dept: delete_dept(d['department_id'])).props('flat dense size=sm color=negative')
                
                def delete_dept(dept_id):
                    hospital_service.delete_department(dept_id)
                    ui.notify('科室已删除', type='positive')
                    refresh_dept_list()
                
                refresh_dept_list()
    
    def render_product_panel(self):
        """渲染产品管理面板"""
        with ui.row().classes('w-full q-gutter-md'):
            # 左侧：添加产品
            with ui.card().classes('glass-card col-4 q-pa-lg'):
                ui.label('添加产品').classes('text-h6 text-white q-mb-md')
                
                name_input = ui.input(label='产品名称').classes('w-full glass-input')
                category_input = ui.input(label='产品类别').classes('w-full glass-input')
                desc_input = ui.textarea(label='产品描述').classes('w-full glass-input')
                features_input = ui.input(label='关键特性（逗号分隔）').classes('w-full glass-input')
                indications_input = ui.input(label='适应症（逗号分隔）').classes('w-full glass-input')
                notes_input = ui.textarea(label='备注').classes('w-full glass-input')
                
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
                
                ui.button('保存', on_click=save_product).classes('glass-btn q-mt-md')
            
            # 右侧：产品列表
            with ui.card().classes('glass-card col-7 q-pa-lg'):
                ui.label('产品列表').classes('text-h6 text-white q-mb-md')
                product_list_container = ui.column().classes('w-full')
                
                def refresh_product_list():
                    product_list_container.clear()
                    with product_list_container:
                        products = hospital_service.list_products()
                        for product in products:
                            with ui.expansion(product['name']).classes('w-full glass-expansion'):
                                ui.label(f"类别: {product.get('category', '')}").classes('text-white')
                                ui.label(f"描述: {product.get('description', '')}").classes('text-secondary')
                                if product.get('key_features'):
                                    ui.label(f"特性: {', '.join(product['key_features'])}").classes('text-caption')
                                with ui.row().classes('q-mt-sm'):
                                    ui.button('删除', on_click=lambda p=product: delete_product(p['product_id'])).props('flat dense size=sm color=negative')
                
                def delete_product(product_id):
                    hospital_service.delete_product(product_id)
                    ui.notify('产品已删除', type='positive')
                    refresh_product_list()
                
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
            self.doc_department_id.options = dept_options
            
            # 自动填充医院名称
            hospital = hospital_service.get_hospital(hospital_id)
            if hospital:
                self.doc_hospital.value = hospital.name
        else:
            self.doc_department_id.options = {'': '未指定'}
            self.doc_hospital.value = ''
    
