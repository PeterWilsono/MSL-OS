# 医药信息专员个人职业操作系统

<div align="center">

**一个专为医药信息专员设计的本地化职业管理系统**

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-Personal%20Use-green.svg)](LICENSE)

[功能特性](#功能特性) • [快速开始](#快速开始) • [使用指南](#使用指南) • [项目结构](#项目结构)

</div>

---

## 简介

本系统是一个基于 Python 的本地个人职业操作系统,专为医药信息沟通专员设计,帮助您系统化管理工作内容,提升职业发展效率。

### 核心价值

- **本地化存储** - 所有数据保存在本地,无需联网,隐私安全有保障
- **结构化管理** - 通过系统化的方法管理医院、医生、拜访记录等信息
- **智能辅助** - 集成 AI 助手,提供数据分析和决策支持
- **个人成长** - 记录反思,追踪进步,持续提升专业能力

---

## 功能特性

### 日常工作管理
- **今日行动** - 智能推荐每日重点任务,帮助规划工作优先级
- **AI 助手** - 支持 DeepSeek/小米 MiMo 双模型,可上传文档分析,引用系统数据
- **待办管理** - 创建和管理待办事项,支持优先级和截止日期

### 拜访管理
- **拜访准备** - 结构化准备拜访内容,减少不确定感
- **拜访记录** - 记录拜访详情,自动生成拜访报告
- **联系人管理** - 管理医生、护士、同事等多类型联系人信息

### 数据管理
- **医院管理** - 管理医院、科室信息,建立完整的医院档案
- **产品管理** - 管理产品信息,关联医院科室
- **知识库** - 管理病种、产品、市场知识
- **数据中心** - 统一查看和管理所有数据

### 分析成长
- **AI 数据分析** - 智能分析医院、科室、医生数据,提供多维度洞察
- **成长反思** - 私密记录个人成长,标记为 private 的内容不会对外公开
- **智能总结** - 自动生成周报、月报,可视化进步轨迹

### 客户追踪管理

基于销售管理的"4张表格"理念,帮助系统化管理客户关系:

- **客户开发表** - 记录客户从开发到建立联系的全过程
- **客户追踪表** - 记录每次跟进的详细情况,包括沟通内容、效果评分
- **客户分类表** - A/B/C/D 四级分类管理,系统自动统计关键指标
- **统计分析表** - 周报/月报核心指标,支持导出 Excel

---

## 快速开始

### 环境要求

- Python 3.8 或更高版本
- Windows / macOS / Linux

### 安装步骤

1. **克隆仓库**
```bash
git clone https://github.com/your-username/medicine-info-assistant.git
cd medicine-info-assistant
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **启动程序**
```bash
python main.py
```

程序将在浏览器中自动打开,默认地址: `http://localhost:8080`

### 配置 AI 助手(推荐)

程序启动后:
1. 点击顶部导航栏 **"系统"** → **"系统设置"**
2. 开启 **"启用 AI 分析"** 开关
3. 选择 AI 提供商(DeepSeek 或 小米 MiMo)
4. 输入对应的 API Key 并保存

---

## 使用指南

### 基本流程

1. **添加医院和科室** - 在"医院管理"中添加目标医院和科室信息
2. **添加产品** - 在"产品管理"中添加负责的产品信息
3. **建立关联** - 在"产品关联"中将产品与医院科室关联
4. **拜访准备** - 在"拜访准备"中为即将进行的拜访做准备
5. **记录拜访** - 拜访后在"拜访记录"中记录详情
6. **定期复盘** - 使用"AI 数据分析"和"成长反思"进行定期总结

### 客户追踪使用流程

1. **新增客户** - 在"客户开发表"中记录新开发的客户
2. **跟进记录** - 每次跟进后在"客户追踪表"中记录详情
3. **分类管理** - 根据客户反馈及时调整客户等级(A/B/C/D)
4. **查看提醒** - 每天查看"待跟进提醒",按优先级跟进
5. **统计分析** - 定期查看"统计分析表",了解工作效果

---

## 项目结构

```
medicine-info-assistant/
├── main.py                 # 程序入口
├── requirements.txt        # 依赖列表
├── core/                   # 核心业务逻辑
│   ├── ai_integration.py   # AI 集成
│   ├── data_models.py      # 数据模型
│   ├── file_manager.py     # 文件管理
│   └── ...
├── modules/                # 业务模块
│   ├── hospital_manager/   # 医院管理
│   ├── visit_preparation/  # 拜访准备
│   ├── visit_record/       # 拜访记录
│   ├── customer_tracking/  # 客户追踪
│   └── ...
├── ui/                     # 用户界面
│   └── app.py             # NiceGUI 应用
├── data/                   # 数据存储目录
│   ├── hospitals/         # 医院数据
│   ├── doctors/           # 医生数据
│   ├── products/          # 产品数据
│   └── ...
└── outputs/                # 生成的报告
    └── reports/           # 访问报告
```

---

## 数据存储

所有数据均以 JSON 格式保存在本地 `data/` 目录下:

- **医院数据**: `data/hospitals/`
- **医生数据**: `data/doctors/`
- **产品数据**: `data/products/`
- **拜访记录**: `data/interactions/`
- **客户追踪**: `data/customer_tracking/`
- **知识库**: `data/knowledge/`
- **反思记录**: `data/reflections/`

**注意**: 建议定期备份 `data/` 目录,以防数据丢失。

---

## 隐私保护

标记为 `private` 的内容(如个人反思)将:
- 不会进入对外报告
- 不会进入工作汇报
- 不会进入医生总结

您的隐私数据完全由您自己掌控。

---

## 技术栈

- **前端框架**: [NiceGUI](https://nicegui.io/) - 现代 Python Web UI 框架
- **后端语言**: Python 3.8+
- **数据存储**: JSON 文件
- **AI 集成**: DeepSeek API / 小米 MiMo API

---

## 贡献指南

欢迎提交 Issue 和 Pull Request!

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

---

## 许可证

本项目仅供个人学习和使用。未经授权,不得用于商业用途。

---

## 联系方式

如有问题或建议,欢迎通过以下方式联系:

- 提交 [Issue](https://github.com/PeterWilsono/MSL-OS/issues)
- 发送邮件至 1206244538@qq.com

---

<div align="center">

**⭐ 如果这个项目对你有帮助,请给一个 Star! ⭐**

Made with ❤️ by 医药信息专员

</div>
