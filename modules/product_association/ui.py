"""
产品关联管理用户界面

本模块提供产品与医院科室关联关系的图形化管理界面。

主要功能：
    1. 关联记录列表视图
        - 以表格形式展示所有关联记录
        - 显示产品名称、医院名称、科室名称、创建时间
        - 支持查看详情和删除操作
        
    2. 创建关联记录
        - 提供对话框界面创建新的关联记录
        - 下拉选择产品、医院、科室
        - 支持添加备注信息
        
    3. 删除关联记录
        - 单个删除：点击删除按钮删除单条记录
        - 批量删除：选择多条记录批量删除
        - 提供删除确认对话框，防止误操作
        
    4. 筛选和搜索功能
        - 按产品、医院、科室筛选
        - 关键词搜索（在产品、医院、科室名称中搜索）
        - 支持重置筛选条件
        
    5. 统计分析视图
        - 显示产品、医院、科室的关联数量统计
        - 以展开面板形式展示统计数据
        - 按关联数量排序，显示前10名
        
    6. 数据导出功能
        - 支持导出为 CSV 或 Excel 格式
        - 可按当前筛选条件导出
        - 显示导出文件路径
        
    7. 数据完整性检查
        - 检查并显示失效的关联记录
        - 提供清理失效记录的选项

界面设计：
    - 使用 NiceGUI 框架构建
    - 采用卡片式布局，清晰分区
    - 使用 glass-card 样式，提供现代化的视觉效果
    - 响应式设计，适配不同屏幕尺寸

技术特点：
    - 实时刷新：操作后自动刷新列表
    - 友好提示：所有操作都有成功或失败的提示
    - 错误处理：捕获并显示错误信息
    - 确认对话框：重要操作前需要用户确认

作者：医药信息专员系统开发团队
版本：1.0.0
"""
from nicegui import ui
from typing import Optional
from datetime import datetime

from modules.product_association.service import ProductAssociationService
from modules.hospital_manager.service import hospital_service


# 创建服务实例
product_association_service = ProductAssociationService()


def render_product_association_page():
    """
    渲染产品关联管理主界面
    
    创建并显示产品关联管理的主界面，包括标题、操作按钮区、
    筛选搜索区和关联记录列表视图。
    
    界面布局：
        1. 页面标题：🔗 产品关联管理
        2. 操作按钮区：
            - 添加关联：打开创建关联记录对话框
            - 刷新：重新加载关联记录列表
            - 统计分析：显示统计数据对话框
            - 导出数据：显示导出选项对话框
        3. 筛选和搜索区：
            - 产品下拉选择框
            - 医院下拉选择框
            - 科室下拉选择框
            - 搜索关键词输入框
            - 搜索按钮
        4. 关联记录列表视图：
            - 表格形式显示所有关联记录
            - 每行显示：产品名称、医院名称、科室名称、创建时间、操作按钮
    
    功能特点：
        - 自动加载产品、医院、科室选项
        - 筛选控件包含"全部"选项
        - 列表视图支持查看详情和删除操作
        - 使用 glass-card 样式，提供现代化视觉效果
    
    使用示例：
        >>> from modules.product_association.ui import render_product_association_page
        >>> 
        >>> # 在 NiceGUI 应用中渲染页面
        >>> @ui.page('/product-associations')
        >>> def product_association_page():
        ...     render_product_association_page()
    
    注意事项：
        - 此函数会创建全局引用，用于在其他函数中访问筛选控件和列表容器
        - 初始加载时会调用 refresh_association_list() 显示所有记录
        - 需要在 NiceGUI 应用上下文中调用
    
    相关函数：
        - refresh_association_list(): 刷新关联记录列表
        - show_create_dialog(): 显示创建关联记录对话框
        - show_statistics_dialog(): 显示统计分析对话框
        - show_export_dialog(): 显示导出数据对话框
    """
    # 页面标题
    ui.label('🔗 产品关联管理').classes('page-title')
    
    # 操作按钮区
    with ui.card().classes('glass-card w-full q-pa-lg q-mb-lg'):
        with ui.row().classes('w-full items-center justify-between'):
            ui.label('关联记录管理').classes('text-h6 text-white')
            
            with ui.row().classes('q-gutter-md'):
                ui.button('➕ 添加关联', on_click=lambda: show_create_dialog()).classes('glass-btn')
                ui.button('🔄 刷新', on_click=lambda: refresh_association_list()).classes('glass-btn')
                ui.button('📊 统计分析', on_click=lambda: show_statistics_dialog()).classes('glass-btn-secondary')
                ui.button('📤 导出数据', on_click=lambda: show_export_dialog()).classes('glass-btn-secondary')
    
    # 筛选和搜索区
    with ui.card().classes('glass-card w-full q-pa-lg q-mb-lg'):
        ui.label('🔍 筛选和搜索').classes('text-h6 text-white q-mb-md')
        
        with ui.row().classes('w-full q-gutter-md'):
            # 获取产品、医院、科室选项
            products = hospital_service.list_products()
            hospitals = hospital_service.list_hospitals()
            departments = hospital_service.list_departments()
            
            product_options = {p['product_id']: p['name'] for p in products}
            hospital_options = {h['hospital_id']: h['name'] for h in hospitals}
            department_options = {d['department_id']: d['name'] for d in departments}
            
            # 添加"全部"选项
            product_options = {'': '全部产品', **product_options}
            hospital_options = {'': '全部医院', **hospital_options}
            department_options = {'': '全部科室', **department_options}
            
            # 筛选控件
            filter_product = ui.select(
                label='产品',
                options=product_options,
                value=''
            ).classes('col-3 glass-input')
            
            filter_hospital = ui.select(
                label='医院',
                options=hospital_options,
                value=''
            ).classes('col-3 glass-input')
            
            filter_department = ui.select(
                label='科室',
                options=department_options,
                value=''
            ).classes('col-3 glass-input')
            
            # 搜索框
            search_input = ui.input(
                label='搜索关键词',
                placeholder='输入产品、医院或科室名称'
            ).classes('col-2 glass-input')
            
            ui.button('搜索', on_click=lambda: perform_search()).classes('glass-btn col-1')
        
        # 存储筛选控件的引用，以便在其他函数中访问
        render_product_association_page.filter_product = filter_product
        render_product_association_page.filter_hospital = filter_hospital
        render_product_association_page.filter_department = filter_department
        render_product_association_page.search_input = search_input
    
    # 关联记录列表视图区
    with ui.card().classes('glass-card w-full q-pa-lg'):
        ui.label('📋 关联记录列表').classes('text-h6 text-white q-mb-md')
        
        # 创建列表容器
        association_list_container = ui.column().classes('w-full')
        
        # 存储容器引用，以便刷新
        render_product_association_page.association_list_container = association_list_container
        
        # 初始加载列表
        refresh_association_list()


def refresh_association_list():
    """
    刷新关联记录列表
    
    根据当前的筛选条件重新加载并显示关联记录列表。
    
    刷新流程：
        1. 检查列表容器是否存在
        2. 清空列表容器
        3. 获取当前的筛选条件（产品ID、医院ID、科室ID）
        4. 调用 filter_associations() 获取符合条件的关联记录
        5. 如果没有记录，显示"暂无关联记录"
        6. 如果有记录：
            - 显示记录总数
            - 创建表格头部
            - 遍历记录，创建表格行
            - 每行包含：产品名称、医院名称、科室名称、创建时间、操作按钮
    
    筛选逻辑：
        - 如果筛选控件的值为空字符串，视为"全部"（不筛选）
        - 支持多条件组合筛选
        - 筛选条件保存在页面函数的属性中
    
    显示格式：
        - 表格头部：产品名称、医院名称、科室名称、创建时间、操作
        - 创建时间格式：YYYY-MM-DD HH:MM
        - 操作按钮：查看、删除
    
    使用场景：
        - 页面初始加载时
        - 点击"刷新"按钮时
        - 创建或删除关联记录后
        - 应用筛选条件后
    
    注意事项：
        - 此函数依赖于 render_product_association_page() 创建的全局引用
        - 如果列表容器不存在，函数会直接返回
        - 使用 lambda 表达式传递参数，避免闭包问题
    """
    if not hasattr(render_product_association_page, 'association_list_container'):
        return
    
    container = render_product_association_page.association_list_container
    container.clear()
    
    # 获取筛选条件
    product_id = None
    hospital_id = None
    department_id = None
    
    if hasattr(render_product_association_page, 'filter_product'):
        product_id = render_product_association_page.filter_product.value or None
    
    if hasattr(render_product_association_page, 'filter_hospital'):
        hospital_id = render_product_association_page.filter_hospital.value or None
    
    if hasattr(render_product_association_page, 'filter_department'):
        department_id = render_product_association_page.filter_department.value or None
    
    # 获取关联记录
    associations = product_association_service.filter_associations(
        product_id=product_id,
        hospital_id=hospital_id,
        department_id=department_id
    )
    
    with container:
        if not associations:
            ui.label('暂无关联记录').classes('text-secondary')
            return
        
        # 显示记录总数
        ui.label(f'共 {len(associations)} 条记录').classes('text-white q-mb-md')
        
        # 创建表格头部
        with ui.element('div').classes('w-full'):
            with ui.row().classes('w-full items-center q-pa-sm glass-list-item'):
                ui.label('产品名称').classes('col-3 text-white font-bold')
                ui.label('医院名称').classes('col-3 text-white font-bold')
                ui.label('科室名称').classes('col-3 text-white font-bold')
                ui.label('创建时间').classes('col-2 text-white font-bold')
                ui.label('操作').classes('col-1 text-white font-bold text-center')
            
            # 显示关联记录
            for association in associations:
                with ui.row().classes('w-full items-center q-pa-sm glass-list-item q-mt-sm'):
                    ui.label(association.product_name).classes('col-3 text-white')
                    ui.label(association.hospital_name).classes('col-3 text-white')
                    ui.label(association.department_name).classes('col-3 text-white')
                    ui.label(association.created_at.strftime('%Y-%m-%d %H:%M')).classes('col-2 text-white')
                    
                    # 操作按钮
                    with ui.row().classes('col-1 justify-center q-gutter-sm'):
                        ui.button(
                            '编辑',
                            on_click=lambda a=association: show_edit_dialog(a)
                        ).props('flat dense size=sm color=primary')
                        ui.button(
                            '查看',
                            on_click=lambda a=association: show_detail_dialog(a)
                        ).props('flat dense size=sm color=info')
                        ui.button(
                            '删除',
                            on_click=lambda a=association: confirm_delete(a)
                        ).props('flat dense size=sm color=negative')


def perform_search():
    """
    执行搜索操作
    
    根据搜索框中的关键词搜索关联记录，并更新列表显示。
    
    搜索流程：
        1. 检查搜索输入框是否存在
        2. 获取搜索关键词
        3. 如果关键词为空，执行普通筛选（调用 refresh_association_list()）
        4. 如果关键词不为空：
            - 调用 search_associations() 执行搜索
            - 清空列表容器
            - 如果没有搜索结果，显示"未找到包含 {keyword} 的关联记录"
            - 如果有搜索结果：
                * 显示搜索结果数量
                * 创建表格头部
                * 遍历结果，创建表格行
    
    搜索特点：
        - 不区分大小写
        - 模糊匹配（部分匹配即可）
        - 在产品名称、医院名称、科室名称中搜索
        - 搜索结果实时显示
    
    显示格式：
        - 搜索结果提示：找到 X 条包含 "关键词" 的记录
        - 表格格式与列表视图相同
        - 每行包含：产品名称、医院名称、科室名称、创建时间、操作按钮
    
    使用场景：
        - 点击"搜索"按钮时
        - 需要快速查找特定产品、医院或科室的关联记录时
    
    注意事项：
        - 搜索会忽略当前的筛选条件
        - 如果搜索框为空，会恢复到筛选模式
        - 搜索结果不排序，按文件遍历顺序显示
    """
    if not hasattr(render_product_association_page, 'search_input'):
        return
    
    keyword = render_product_association_page.search_input.value
    
    if not keyword:
        # 如果搜索框为空，执行普通筛选
        refresh_association_list()
        return
    
    # 执行搜索
    associations = product_association_service.search_associations(keyword)
    
    # 更新列表显示
    container = render_product_association_page.association_list_container
    container.clear()
    
    with container:
        if not associations:
            ui.label(f'未找到包含 "{keyword}" 的关联记录').classes('text-secondary')
            return
        
        # 显示搜索结果
        ui.label(f'找到 {len(associations)} 条包含 "{keyword}" 的记录').classes('text-white q-mb-md')
        
        # 创建表格头部
        with ui.element('div').classes('w-full'):
            with ui.row().classes('w-full items-center q-pa-sm glass-list-item'):
                ui.label('产品名称').classes('col-3 text-white font-bold')
                ui.label('医院名称').classes('col-3 text-white font-bold')
                ui.label('科室名称').classes('col-3 text-white font-bold')
                ui.label('创建时间').classes('col-2 text-white font-bold')
                ui.label('操作').classes('col-1 text-white font-bold text-center')
            
            # 显示搜索结果
            for association in associations:
                with ui.row().classes('w-full items-center q-pa-sm glass-list-item q-mt-sm'):
                    ui.label(association.product_name).classes('col-3 text-white')
                    ui.label(association.hospital_name).classes('col-3 text-white')
                    ui.label(association.department_name).classes('col-3 text-white')
                    ui.label(association.created_at.strftime('%Y-%m-%d %H:%M')).classes('col-2 text-white')
                    
                    # 操作按钮
                    with ui.row().classes('col-1 justify-center q-gutter-sm'):
                        ui.button(
                            '编辑',
                            on_click=lambda a=association: show_edit_dialog(a)
                        ).props('flat dense size=sm color=primary')
                        ui.button(
                            '查看',
                            on_click=lambda a=association: show_detail_dialog(a)
                        ).props('flat dense size=sm color=info')
                        ui.button(
                            '删除',
                            on_click=lambda a=association: confirm_delete(a)
                        ).props('flat dense size=sm color=negative')


def show_create_dialog():
    """
    显示创建关联记录对话框
    
    打开一个对话框，允许用户创建新的产品与医院科室关联记录。
    
    对话框内容：
        1. 标题：➕ 添加产品关联
        2. 产品选择下拉框：
            - 显示所有可用产品
            - 支持输入搜索
            - 显示产品名称，值为产品ID
        3. 医院选择下拉框：
            - 显示所有可用医院
            - 支持输入搜索
            - 显示医院名称，值为医院ID
        4. 科室选择下拉框：
            - 显示所有可用科室
            - 支持输入搜索
            - 显示科室名称，值为科室ID
        5. 备注输入框：
            - 多行文本输入
            - 可选字段
        6. 操作按钮：
            - 取消：关闭对话框
            - 创建：提交创建请求
    
    功能特点：
        - 自动加载产品、医院、科室选项
        - 下拉框支持输入搜索，方便快速定位
        - 使用 glass-card 样式，保持界面一致性
        - 最小宽度 500px，确保内容完整显示
    
    验证规则：
        - 产品、医院、科室必须选择（不能为空）
        - 备注为可选字段
        - 不允许创建重复的关联记录
    
    使用场景：
        - 点击"添加关联"按钮时
        - 需要记录新的产品使用情况时
    
    相关函数：
        - create_association(): 处理创建请求
    
    注意事项：
        - 对话框会自动打开
        - 创建成功后会自动关闭对话框并刷新列表
        - 创建失败会显示错误提示，但不关闭对话框
    """
    # 获取产品、医院、科室选项
    products = hospital_service.list_products()
    hospitals = hospital_service.list_hospitals()
    departments = hospital_service.list_departments()
    
    product_options = {p['product_id']: p['name'] for p in products}
    hospital_options = {h['hospital_id']: h['name'] for h in hospitals}
    department_options = {d['department_id']: d['name'] for d in departments}
    
    with ui.dialog() as dialog, ui.card().classes('glass-card').style('min-width: 500px'):
        ui.label('➕ 添加产品关联').classes('text-h6 text-white q-mb-md')
        
        # 产品选择
        product_select = ui.select(
            label='选择产品',
            options=product_options,
            with_input=True
        ).classes('w-full glass-input')
        
        # 医院选择
        hospital_select = ui.select(
            label='选择医院',
            options=hospital_options,
            with_input=True
        ).classes('w-full glass-input')
        
        # 科室选择
        department_select = ui.select(
            label='选择科室',
            options=department_options,
            with_input=True
        ).classes('w-full glass-input')
        
        # 备注
        notes_input = ui.textarea(
            label='备注（可选）'
        ).classes('w-full glass-input')
        
        # 按钮
        with ui.row().classes('w-full justify-end q-mt-md q-gutter-md'):
            ui.button('取消', on_click=dialog.close).classes('glass-btn')
            ui.button(
                '创建',
                on_click=lambda: create_association(
                    dialog,
                    product_select.value,
                    hospital_select.value,
                    department_select.value,
                    notes_input.value
                )
            ).classes('glass-btn')
    
    dialog.open()


def create_association(dialog, product_id, hospital_id, department_id, notes):
    """
    创建关联记录
    
    处理创建关联记录的请求，验证输入并调用服务层创建记录。
    
    参数：
        dialog: 对话框对象，用于在创建成功后关闭
        product_id (str): 产品ID
        hospital_id (str): 医院ID
        department_id (str): 科室ID
        notes (str): 备注信息
    
    验证规则：
        - 产品ID、医院ID、科室ID 不能为空
        - 如果验证失败，显示警告提示并返回
    
    创建流程：
        1. 验证输入（检查是否为空）
        2. 调用 product_association_service.create_association() 创建记录
        3. 如果创建成功：
            - 显示成功提示
            - 关闭对话框
            - 刷新关联记录列表
        4. 如果创建失败：
            - 显示失败提示（可能是重复记录或无效ID）
            - 不关闭对话框，允许用户修改
    
    错误处理：
        - 输入验证失败：显示警告提示
        - 创建失败：显示失败提示，说明可能的原因
    
    提示类型：
        - warning: 输入验证失败
        - positive: 创建成功
        - negative: 创建失败
    
    使用场景：
        - 在创建关联记录对话框中点击"创建"按钮时调用
    
    注意事项：
        - 备注字段可以为空，会自动转换为空字符串
        - 创建失败的原因可能是：
            * 重复的关联记录（相同的产品、医院、科室组合）
            * 无效的产品ID、医院ID或科室ID
        - 创建成功后会自动刷新列表，显示新创建的记录
    """
    # 验证输入
    if not product_id or not hospital_id or not department_id:
        ui.notify('请选择产品、医院和科室', type='warning')
        return
    
    # 创建关联记录
    association = product_association_service.create_association(
        product_id=product_id,
        hospital_id=hospital_id,
        department_id=department_id,
        notes=notes or ''
    )
    
    if association:
        ui.notify('关联记录创建成功', type='positive')
        dialog.close()
        refresh_association_list()
    else:
        ui.notify('创建失败，可能是重复记录或无效的ID', type='negative')


def show_edit_dialog(association):
    """
    显示编辑关联记录对话框
    
    打开一个对话框，允许用户编辑现有的产品与医院科室关联记录。
    
    参数：
        association (ProductAssociation): 要编辑的关联记录对象
    
    对话框内容：
        1. 标题：✏️ 编辑产品关联
        2. 产品选择下拉框（预填充当前值）
        3. 医院选择下拉框（预填充当前值）
        4. 科室选择下拉框（预填充当前值）
        5. 备注输入框（预填充当前值）
        6. 操作按钮：取消、保存
    
    功能特点：
        - 自动加载并预填充当前值
        - 支持修改产品、医院、科室和备注
        - 使用 glass-card 样式
    
    使用场景：
        - 在列表视图中点击"编辑"按钮时
        - 需要修正错误的关联记录时
    """
    # 获取产品、医院、科室选项
    products = hospital_service.list_products()
    hospitals = hospital_service.list_hospitals()
    departments = hospital_service.list_departments()
    
    product_options = {p['product_id']: p['name'] for p in products}
    hospital_options = {h['hospital_id']: h['name'] for h in hospitals}
    department_options = {d['department_id']: d['name'] for d in departments}
    
    with ui.dialog() as dialog, ui.card().classes('glass-card').style('min-width: 500px'):
        ui.label('✏️ 编辑产品关联').classes('text-h6 text-white q-mb-md')
        
        # 产品选择（预填充当前值）
        product_select = ui.select(
            label='选择产品',
            options=product_options,
            value=association.product_id,
            with_input=True
        ).classes('w-full glass-input')
        
        # 医院选择（预填充当前值）
        hospital_select = ui.select(
            label='选择医院',
            options=hospital_options,
            value=association.hospital_id,
            with_input=True
        ).classes('w-full glass-input')
        
        # 科室选择（预填充当前值）
        department_select = ui.select(
            label='选择科室',
            options=department_options,
            value=association.department_id,
            with_input=True
        ).classes('w-full glass-input')
        
        # 备注（预填充当前值）
        notes_input = ui.textarea(
            label='备注（可选）',
            value=association.notes
        ).classes('w-full glass-input')
        
        # 按钮
        with ui.row().classes('w-full justify-end q-mt-md q-gutter-md'):
            ui.button('取消', on_click=dialog.close).classes('glass-btn')
            ui.button(
                '保存',
                on_click=lambda: update_association(
                    dialog,
                    association.association_id,
                    product_select.value,
                    hospital_select.value,
                    department_select.value,
                    notes_input.value
                )
            ).classes('glass-btn')
    
    dialog.open()


def update_association(dialog, association_id, product_id, hospital_id, department_id, notes):
    """
    更新关联记录
    
    处理更新关联记录的请求，验证输入并调用服务层更新记录。
    
    参数：
        dialog: 对话框对象，用于在更新成功后关闭
        association_id (str): 关联记录ID
        product_id (str): 产品ID
        hospital_id (str): 医院ID
        department_id (str): 科室ID
        notes (str): 备注信息
    
    验证规则：
        - 产品ID、医院ID、科室ID 不能为空
    
    更新流程：
        1. 验证输入
        2. 调用服务层更新记录
        3. 显示成功或失败提示
        4. 刷新列表
    """
    # 验证输入
    if not product_id or not hospital_id or not department_id:
        ui.notify('请选择产品、医院和科室', type='warning')
        return
    
    # 更新关联记录
    success = product_association_service.update_association(
        association_id=association_id,
        product_id=product_id,
        hospital_id=hospital_id,
        department_id=department_id,
        notes=notes or ''
    )
    
    if success:
        ui.notify('关联记录已更新', type='positive')
        dialog.close()
        refresh_association_list()
    else:
        ui.notify('更新失败，请检查输入', type='negative')


def show_detail_dialog(association):
    """
    显示关联记录详情对话框
    
    打开一个对话框，显示关联记录的完整详细信息。
    
    参数：
        association (ProductAssociation): 要显示的关联记录对象
    
    显示内容：
        - 关联ID：唯一标识符
        - 产品：产品名称（产品ID）
        - 医院：医院名称（医院ID）
        - 科室：科室名称（科室ID）
        - 创建时间：YYYY-MM-DD HH:MM:SS 格式
        - 更新时间：YYYY-MM-DD HH:MM:SS 格式
        - 状态：有效 / 已失效
        - 备注：如果有备注则显示
    
    界面特点：
        - 使用 glass-card 样式
        - 最小宽度 500px
        - 信息以列表形式垂直排列
        - 包含"关闭"按钮
    
    使用场景：
        - 在列表视图中点击"查看"按钮时
        - 需要查看关联记录的完整信息时
    
    注意事项：
        - 只读显示，不支持编辑
        - 显示所有字段，包括ID和状态
        - 如果没有备注，不显示备注字段
    """
    with ui.dialog() as dialog, ui.card().classes('glass-card').style('min-width: 500px'):
        ui.label('📋 关联记录详情').classes('text-h6 text-white q-mb-md')
        
        # 显示详细信息
        with ui.column().classes('w-full q-gutter-sm'):
            ui.label(f'关联ID: {association.association_id}').classes('text-white')
            ui.label(f'产品: {association.product_name} ({association.product_id})').classes('text-white')
            ui.label(f'医院: {association.hospital_name} ({association.hospital_id})').classes('text-white')
            ui.label(f'科室: {association.department_name} ({association.department_id})').classes('text-white')
            ui.label(f'创建时间: {association.created_at.strftime("%Y-%m-%d %H:%M:%S")}').classes('text-white')
            ui.label(f'更新时间: {association.updated_at.strftime("%Y-%m-%d %H:%M:%S")}').classes('text-white')
            ui.label(f'状态: {"有效" if association.is_active else "已失效"}').classes('text-white')
            
            if association.notes:
                ui.label(f'备注: {association.notes}').classes('text-white')
        
        # 关闭按钮
        with ui.row().classes('w-full justify-end q-mt-md'):
            ui.button('关闭', on_click=dialog.close).classes('glass-btn')
    
    dialog.open()


def confirm_delete(association):
    """
    确认删除关联记录
    
    显示删除确认对话框，防止用户误删除关联记录。
    
    参数：
        association (ProductAssociation): 要删除的关联记录对象
    
    对话框内容：
        - 标题：⚠️ 确认删除
        - 提示信息：确定要删除以下关联记录吗？
        - 记录详情：
            * 产品：产品名称
            * 医院：医院名称
            * 科室：科室名称
        - 警告：此操作不可恢复！（红色文字）
        - 操作按钮：
            * 取消：关闭对话框，不执行删除
            * 确认删除：执行删除操作（红色按钮）
    
    安全措施：
        - 显示要删除的记录详情，让用户确认
        - 使用红色警告文字提醒操作不可恢复
        - 删除按钮使用 negative 颜色（红色），引起注意
    
    使用场景：
        - 在列表视图中点击"删除"按钮时
        - 需要删除不再有效的关联记录时
    
    相关函数：
        - delete_association(): 执行实际的删除操作
    
    注意事项：
        - 这是一个确认对话框，不会直接删除记录
        - 只有点击"确认删除"按钮才会执行删除
        - 删除操作不可恢复，请谨慎使用
    """
    with ui.dialog() as dialog, ui.card().classes('glass-card'):
        ui.label('⚠️ 确认删除').classes('text-h6 text-white q-mb-md')
        ui.label(f'确定要删除以下关联记录吗？').classes('text-white')
        ui.label(f'产品: {association.product_name}').classes('text-white q-mt-sm')
        ui.label(f'医院: {association.hospital_name}').classes('text-white')
        ui.label(f'科室: {association.department_name}').classes('text-white')
        ui.label('此操作不可恢复！').classes('text-negative q-mt-md')
        
        # 按钮
        with ui.row().classes('w-full justify-end q-mt-md q-gutter-md'):
            ui.button('取消', on_click=dialog.close).classes('glass-btn')
            ui.button(
                '确认删除',
                on_click=lambda: delete_association(dialog, association.association_id)
            ).props('color=negative')
    
    dialog.open()


def delete_association(dialog, association_id):
    """
    删除关联记录
    
    执行实际的删除操作，调用服务层删除关联记录。
    
    参数：
        dialog: 确认对话框对象，用于在删除后关闭
        association_id (str): 要删除的关联记录ID
    
    删除流程：
        1. 调用 product_association_service.delete_association() 删除记录
        2. 如果删除成功：
            - 显示成功提示
            - 关闭确认对话框
            - 刷新关联记录列表
        3. 如果删除失败：
            - 显示失败提示
            - 不关闭对话框
    
    提示类型：
        - positive: 删除成功
        - negative: 删除失败
    
    使用场景：
        - 在删除确认对话框中点击"确认删除"按钮时调用
    
    注意事项：
        - 删除操作不可恢复
        - 删除成功后会自动更新所有索引文件
        - 删除失败可能是因为记录不存在
        - 删除成功后列表会自动刷新，不再显示已删除的记录
    """
    success = product_association_service.delete_association(association_id)
    
    if success:
        ui.notify('关联记录已删除', type='positive')
        dialog.close()
        refresh_association_list()
    else:
        ui.notify('删除失败', type='negative')


def show_statistics_dialog():
    """
    显示统计分析对话框
    
    打开一个对话框，显示产品、医院、科室的关联数量统计信息。
    
    对话框内容：
        1. 标题：📊 统计分析
        2. 总体统计卡片：
            - 显示总关联数
        3. 产品统计展开面板：
            - 显示每个产品的关联数量
            - 按关联数量降序排序
            - 只显示前10个产品
            - 格式：产品名称 - X 个关联
        4. 医院统计展开面板：
            - 显示每个医院的关联数量
            - 按关联数量降序排序
            - 只显示前10个医院
            - 格式：医院名称 - X 个关联
        5. 科室统计展开面板：
            - 显示每个科室的关联数量
            - 按关联数量降序排序
            - 只显示前10个科室
            - 格式：科室名称 - X 个关联
        6. 关闭按钮
    
    统计特点：
        - 实时计算统计数据
        - 使用展开面板，节省空间
        - 按关联数量排序，突出热门项
        - 自动获取实体名称，便于阅读
    
    界面特点：
        - 使用 glass-card 样式
        - 最小宽度 600px
        - 最大高度 80vh，超出部分可滚动
        - 使用图标增强视觉效果
    
    使用场景：
        - 点击"统计分析"按钮时
        - 需要了解产品市场覆盖情况时
        - 需要分析医院或科室的产品使用情况时
    
    注意事项：
        - 统计数据基于所有关联记录（不受筛选条件影响）
        - 如果某个实体已被删除，显示其ID而不是名称
        - 只显示前10名，避免列表过长
        - 如果没有数据，显示"暂无数据"
    """
    # 获取统计数据
    stats = product_association_service.get_statistics()
    
    with ui.dialog() as dialog, ui.card().classes('glass-card').style('min-width: 600px; max-height: 80vh; overflow-y: auto'):
        ui.label('📊 统计分析').classes('text-h6 text-white q-mb-md')
        
        # 总体统计
        with ui.card().classes('glass-card w-full q-pa-md q-mb-md'):
            ui.label(f'总关联数: {stats.total_associations}').classes('text-h6 text-white')
        
        # 产品统计
        with ui.expansion('产品统计', icon='inventory').classes('w-full glass-expansion'):
            if stats.product_stats:
                # 按关联数量排序
                sorted_products = sorted(
                    stats.product_stats.items(),
                    key=lambda x: x[1],
                    reverse=True
                )
                
                for product_id, count in sorted_products[:10]:  # 显示前10个
                    # 获取产品名称
                    product = hospital_service.get_product(product_id)
                    product_name = product.name if product else product_id
                    
                    with ui.row().classes('w-full items-center justify-between q-pa-sm'):
                        ui.label(product_name).classes('text-white')
                        ui.label(f'{count} 个关联').classes('text-secondary')
            else:
                ui.label('暂无数据').classes('text-secondary')
        
        # 医院统计
        with ui.expansion('医院统计', icon='local_hospital').classes('w-full glass-expansion'):
            if stats.hospital_stats:
                # 按关联数量排序
                sorted_hospitals = sorted(
                    stats.hospital_stats.items(),
                    key=lambda x: x[1],
                    reverse=True
                )
                
                for hospital_id, count in sorted_hospitals[:10]:  # 显示前10个
                    # 获取医院名称
                    hospital = hospital_service.get_hospital(hospital_id)
                    hospital_name = hospital.name if hospital else hospital_id
                    
                    with ui.row().classes('w-full items-center justify-between q-pa-sm'):
                        ui.label(hospital_name).classes('text-white')
                        ui.label(f'{count} 个关联').classes('text-secondary')
            else:
                ui.label('暂无数据').classes('text-secondary')
        
        # 科室统计
        with ui.expansion('科室统计', icon='meeting_room').classes('w-full glass-expansion'):
            if stats.department_stats:
                # 按关联数量排序
                sorted_departments = sorted(
                    stats.department_stats.items(),
                    key=lambda x: x[1],
                    reverse=True
                )
                
                for department_id, count in sorted_departments[:10]:  # 显示前10个
                    # 获取科室名称
                    department = hospital_service.get_department(department_id)
                    department_name = department.name if department else department_id
                    
                    with ui.row().classes('w-full items-center justify-between q-pa-sm'):
                        ui.label(department_name).classes('text-white')
                        ui.label(f'{count} 个关联').classes('text-secondary')
            else:
                ui.label('暂无数据').classes('text-secondary')
        
        # 关闭按钮
        with ui.row().classes('w-full justify-end q-mt-md'):
            ui.button('关闭', on_click=dialog.close).classes('glass-btn')
    
    dialog.open()


def show_export_dialog():
    """
    显示导出数据对话框
    
    打开一个对话框，允许用户选择导出格式并导出关联数据。
    
    对话框内容：
        1. 标题：📤 导出数据
        2. 导出格式选择下拉框：
            - CSV 文件（默认）
            - Excel 文件
        3. 操作按钮：
            - 取消：关闭对话框
            - 导出：执行导出操作
    
    导出特点：
        - 支持两种格式：CSV 和 Excel
        - 导出当前筛选条件下的记录
        - 如果没有筛选条件，导出所有记录
        - 文件名包含时间戳，避免覆盖
    
    界面特点：
        - 使用 glass-card 样式
        - 最小宽度 400px
        - 简洁的界面，只包含必要的选项
    
    使用场景：
        - 点击"导出数据"按钮时
        - 需要离线分析关联数据时
        - 需要生成报告或备份数据时
    
    相关函数：
        - export_data(): 执行实际的导出操作
    
    注意事项：
        - 导出的数据基于当前的筛选条件
        - 导出文件保存在 outputs/ 目录下
        - Excel 格式需要安装 openpyxl 库
        - 导出成功后会显示文件路径
    """
    with ui.dialog() as dialog, ui.card().classes('glass-card').style('min-width: 400px'):
        ui.label('📤 导出数据').classes('text-h6 text-white q-mb-md')
        
        # 导出格式选择
        format_select = ui.select(
            label='导出格式',
            options={'csv': 'CSV 文件', 'excel': 'Excel 文件'},
            value='csv'
        ).classes('w-full glass-input')
        
        # 按钮
        with ui.row().classes('w-full justify-end q-mt-md q-gutter-md'):
            ui.button('取消', on_click=dialog.close).classes('glass-btn')
            ui.button(
                '导出',
                on_click=lambda: export_data(dialog, format_select.value)
            ).classes('glass-btn')
    
    dialog.open()


def export_data(dialog, format_type):
    """
    导出数据
    
    执行实际的数据导出操作，根据选择的格式和当前筛选条件导出关联数据。
    
    参数：
        dialog: 导出对话框对象，用于在导出成功后关闭
        format_type (str): 导出格式，"csv" 或 "excel"
    
    导出流程：
        1. 获取当前的筛选条件（产品ID、医院ID、科室ID）
        2. 构建筛选条件字典
        3. 调用 product_association_service.export_data() 执行导出
        4. 如果导出成功：
            - 显示成功提示，包含文件路径
            - 关闭导出对话框
        5. 如果导出失败：
            - 显示失败提示，包含错误信息
            - 不关闭对话框
    
    筛选条件：
        - 如果筛选控件有值，添加到筛选条件中
        - 如果筛选控件为空，不添加该条件
        - 如果没有任何筛选条件，导出所有记录
    
    错误处理：
        - 捕获所有异常并显示错误提示
        - 常见错误：
            * Excel 格式需要 openpyxl 库
            * 磁盘空间不足
            * 权限不足
    
    提示类型：
        - positive: 导出成功
        - negative: 导出失败
    
    使用场景：
        - 在导出数据对话框中点击"导出"按钮时调用
    
    注意事项：
        - 导出的数据基于当前的筛选条件
        - 导出文件保存在 outputs/ 目录下
        - 文件名包含时间戳，格式：product_associations_YYYYMMdd_HHMMSS.csv/xlsx
        - 导出的数据包含：产品名称、医院名称、科室名称、创建时间
    """
    try:
        # 获取当前筛选条件
        filters = {}
        
        if hasattr(render_product_association_page, 'filter_product'):
            product_id = render_product_association_page.filter_product.value
            if product_id:
                filters['product_id'] = product_id
        
        if hasattr(render_product_association_page, 'filter_hospital'):
            hospital_id = render_product_association_page.filter_hospital.value
            if hospital_id:
                filters['hospital_id'] = hospital_id
        
        if hasattr(render_product_association_page, 'filter_department'):
            department_id = render_product_association_page.filter_department.value
            if department_id:
                filters['department_id'] = department_id
        
        # 导出数据
        filepath = product_association_service.export_data(
            format=format_type,
            filters=filters if filters else None
        )
        
        ui.notify(f'数据已导出到: {filepath}', type='positive')
        dialog.close()
        
    except Exception as e:
        ui.notify(f'导出失败: {str(e)}', type='negative')
