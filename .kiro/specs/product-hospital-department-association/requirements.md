# 需求文档：产品与医院科室关联管理

## 引言

本文档定义了医药信息专员系统中"产品与医院科室关联管理"功能的需求。该功能旨在建立产品（Product）与医院（Hospital）、科室（Department）之间的关联关系，使医药信息专员能够追踪和管理产品在各医院科室的使用情况。

## 术语表

- **System**: 医药信息专员系统
- **Product**: 公司自有产品，包含产品ID、名称、类别、描述、关键特性、适应症等信息
- **Hospital**: 医院实体，包含医院ID、名称、等级、地址等信息
- **Department**: 医院科室，包含科室ID、名称、描述、科室主任等信息
- **Association**: 产品与医院科室之间的关联关系
- **User**: 使用系统的医药信息专员
- **Association_Record**: 关联记录，记录产品在特定医院特定科室的使用情况

## 需求

### 需求 1：建立产品与医院科室的关联关系

**用户故事：** 作为医药信息专员，我希望能够记录某个产品在哪个医院的哪个科室中使用，以便追踪产品的市场覆盖情况。

#### 验收标准

1. WHEN User 选择一个产品、一个医院和一个科室，THEN THE System SHALL 创建一条关联记录
2. WHEN User 创建关联记录时，THE System SHALL 验证产品ID、医院ID和科室ID的有效性
3. WHEN User 尝试创建重复的关联记录（相同产品、医院、科室组合），THEN THE System SHALL 拒绝创建并提示已存在
4. WHEN 关联记录被创建，THE System SHALL 记录创建时间和更新时间
5. THE System SHALL 将关联记录持久化存储到 JSON 文件中

### 需求 2：查询产品的使用情况

**用户故事：** 作为医药信息专员，我希望能够查询某个产品在哪些医院的哪些科室中使用，以便了解产品的市场分布。

#### 验收标准

1. WHEN User 选择一个产品，THEN THE System SHALL 返回该产品关联的所有医院和科室列表
2. WHEN 查询结果被展示，THE System SHALL 显示医院名称、科室名称和关联创建时间
3. WHEN 产品没有任何关联记录，THEN THE System SHALL 返回空列表并提示无关联记录
4. THE System SHALL 按医院名称和科室名称排序查询结果

### 需求 3：查询医院科室的产品使用情况

**用户故事：** 作为医药信息专员，我希望能够查询某个医院或某个科室使用了哪些产品，以便制定针对性的拜访计划。

#### 验收标准

1. WHEN User 选择一个医院，THEN THE System SHALL 返回该医院所有科室使用的产品列表
2. WHEN User 选择一个医院和一个科室，THEN THE System SHALL 返回该科室使用的产品列表
3. WHEN 查询结果被展示，THE System SHALL 显示产品名称、产品类别和关联创建时间
4. WHEN 医院或科室没有使用任何产品，THEN THE System SHALL 返回空列表并提示无产品使用记录
5. THE System SHALL 按产品名称排序查询结果

### 需求 4：删除产品与医院科室的关联关系

**用户故事：** 作为医药信息专员，我希望能够删除不再有效的产品关联记录，以便保持数据的准确性。

#### 验收标准

1. WHEN User 选择一条关联记录并执行删除操作，THEN THE System SHALL 从存储中移除该关联记录
2. WHEN 关联记录被删除，THE System SHALL 更新相关的医院和科室数据
3. WHEN User 尝试删除不存在的关联记录，THEN THE System SHALL 提示记录不存在
4. WHEN 删除操作成功，THE System SHALL 显示成功提示信息

### 需求 5：批量管理产品关联关系

**用户故事：** 作为医药信息专员，我希望能够批量添加或删除产品关联关系，以便提高数据录入效率。

#### 验收标准

1. WHEN User 选择一个产品和多个医院科室组合，THEN THE System SHALL 批量创建多条关联记录
2. WHEN 批量创建过程中遇到重复记录，THE System SHALL 跳过该记录并继续处理其他记录
3. WHEN User 选择多条关联记录并执行批量删除，THEN THE System SHALL 删除所有选中的关联记录
4. WHEN 批量操作完成，THE System SHALL 显示操作结果摘要（成功数量、失败数量、跳过数量）

### 需求 6：关联记录的数据完整性

**用户故事：** 作为系统管理员，我希望系统能够维护数据的完整性，以便确保关联记录的准确性。

#### 验收标准

1. WHEN 产品被删除，THE System SHALL 自动删除所有与该产品相关的关联记录
2. WHEN 医院被删除，THE System SHALL 自动删除所有与该医院相关的关联记录
3. WHEN 科室被删除，THE System SHALL 自动删除所有与该科室相关的关联记录
4. WHEN 关联记录引用的产品、医院或科室不存在，THE System SHALL 在查询时标记为"已失效"
5. THE System SHALL 提供数据完整性检查功能，识别并报告所有失效的关联记录

### 需求 7：用户界面展示

**用户故事：** 作为医药信息专员，我希望有一个直观的界面来管理产品关联关系，以便快速完成日常工作。

#### 验收标准

1. THE System SHALL 提供产品关联管理的专用界面模块
2. WHEN User 进入产品关联管理界面，THE System SHALL 显示所有关联记录的列表视图
3. THE System SHALL 提供筛选功能，允许按产品、医院或科室筛选关联记录
4. THE System SHALL 提供搜索功能，允许通过产品名称、医院名称或科室名称搜索关联记录
5. WHEN User 选择一条关联记录，THE System SHALL 显示该记录的详细信息
6. THE System SHALL 提供添加、编辑和删除关联记录的操作按钮

### 需求 8：数据导出功能

**用户故事：** 作为医药信息专员，我希望能够导出产品关联数据，以便进行离线分析或报告。

#### 验收标准

1. THE System SHALL 提供导出功能，支持导出所有关联记录
2. WHEN User 执行导出操作，THE System SHALL 生成包含产品名称、医院名称、科室名称、创建时间的数据文件
3. THE System SHALL 支持导出为 CSV 或 Excel 格式
4. WHEN 导出操作完成，THE System SHALL 提示用户保存文件的位置

### 需求 9：统计分析功能

**用户故事：** 作为医药信息专员，我希望能够查看产品关联的统计信息，以便了解产品的市场覆盖情况。

#### 验收标准

1. THE System SHALL 提供统计视图，显示每个产品关联的医院数量和科室数量
2. THE System SHALL 提供统计视图，显示每个医院使用的产品数量
3. THE System SHALL 提供统计视图，显示每个科室使用的产品数量
4. WHEN User 查看统计信息，THE System SHALL 以图表形式展示数据（柱状图或饼图）
5. THE System SHALL 允许按时间范围筛选统计数据

### 需求 10：数据验证和错误处理

**用户故事：** 作为系统用户，我希望系统能够验证输入数据并提供清晰的错误提示，以便避免数据错误。

#### 验收标准

1. WHEN User 输入无效的产品ID、医院ID或科室ID，THEN THE System SHALL 拒绝操作并显示错误提示
2. WHEN 数据加载失败，THE System SHALL 显示友好的错误信息并提供重试选项
3. WHEN 数据保存失败，THE System SHALL 显示错误信息并保留用户输入的数据
4. THE System SHALL 在所有用户操作后提供明确的成功或失败反馈
5. WHEN 系统检测到数据不一致，THE System SHALL 记录错误日志并通知用户
