"""
UI 样式模块 - 高级质感毛玻璃 2.0 设计系统
- 三层表面体系：glass-card（主表面）/ glass-card-secondary（嵌套表面）/ glass-list-item（条目）
- 中文优化字体栈 + 清晰文字层级
- 高可见度边框 + 顶部高光，解决"框架不清晰"问题
"""

# 全局 CSS 样式
GLASSMORPHISM_CSS = """
<style>
/* ==================== 设计变量 ==================== */
:root {
    --glass-bg: rgba(255, 255, 255, 0.055);
    --glass-bg-hover: rgba(255, 255, 255, 0.085);
    --glass-bg-secondary: rgba(255, 255, 255, 0.035);
    --glass-border: rgba(255, 255, 255, 0.15);
    --glass-border-soft: rgba(255, 255, 255, 0.09);
    --glass-shadow: rgba(0, 0, 0, 0.35);
    --accent-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    --accent-blue: #4facfe;
    --accent-purple: #764ba2;
    --text-primary: rgba(255, 255, 255, 0.96);
    --text-secondary: rgba(255, 255, 255, 0.72);
    --text-muted: rgba(255, 255, 255, 0.52);
    --font-stack: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC",
                  "HarmonyOS Sans SC", "Microsoft YaHei UI", "Microsoft YaHei",
                  "Source Han Sans SC", "Noto Sans CJK SC", sans-serif;
}

/* ==================== 字体与基础 ==================== */
html, body, .q-page, .q-layout, .q-field, .q-btn, .q-tab, .q-label {
    font-family: var(--font-stack) !important;
}

body {
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    letter-spacing: 0.01em;
}

body, .q-page, .q-layout {
    background: linear-gradient(135deg, #0f0c29 0%, #1a1a2e 42%, #24243e 100%) !important;
    min-height: 100vh;
}

/* ==================== 三层表面体系 ==================== */

/* 主表面：glass-card */
.glass-card {
    background: linear-gradient(160deg, rgba(255, 255, 255, 0.075) 0%, rgba(255, 255, 255, 0.045) 100%) !important;
    backdrop-filter: blur(24px) saturate(1.4) !important;
    -webkit-backdrop-filter: blur(24px) saturate(1.4) !important;
    border: 1px solid var(--glass-border) !important;
    border-radius: 18px !important;
    box-shadow:
        0 8px 32px rgba(0, 0, 0, 0.32),
        inset 0 1px 0 rgba(255, 255, 255, 0.14) !important;
    transition: border-color 0.25s ease, box-shadow 0.25s ease, transform 0.25s ease !important;
}

.glass-card:hover {
    border-color: rgba(255, 255, 255, 0.22) !important;
    transform: translateY(-1px);
    box-shadow:
        0 12px 40px rgba(0, 0, 0, 0.38),
        inset 0 1px 0 rgba(255, 255, 255, 0.18) !important;
}

/* 嵌套表面：glass-card-secondary（卡片内的小卡片/数据条目） */
.glass-card-secondary {
    background: linear-gradient(160deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.025) 100%) !important;
    backdrop-filter: blur(12px) !important;
    -webkit-backdrop-filter: blur(12px) !important;
    border: 1px solid var(--glass-border-soft) !important;
    border-radius: 14px !important;
    box-shadow:
        0 4px 16px rgba(0, 0, 0, 0.22),
        inset 0 1px 0 rgba(255, 255, 255, 0.08) !important;
    transition: border-color 0.2s ease, background 0.2s ease !important;
}

.glass-card-secondary:hover {
    border-color: rgba(255, 255, 255, 0.18) !important;
    background: linear-gradient(160deg, rgba(255, 255, 255, 0.07) 0%, rgba(255, 255, 255, 0.04) 100%) !important;
}

/* 条目表面：glass-list-item */
.glass-list-item {
    background: rgba(255, 255, 255, 0.04) !important;
    border: 1px solid var(--glass-border-soft) !important;
    border-radius: 12px !important;
    padding: 12px 16px !important;
    margin-bottom: 8px !important;
    transition: background 0.2s ease, border-color 0.2s ease !important;
}

.glass-list-item:hover {
    background: rgba(255, 255, 255, 0.075) !important;
    border-color: rgba(255, 255, 255, 0.16) !important;
    transform: translateX(4px);
}

/* ==================== 顶部导航栏 ==================== */
.glass-header {
    background: rgba(15, 15, 30, 0.88) !important;
    backdrop-filter: blur(24px) saturate(1.4) !important;
    -webkit-backdrop-filter: blur(24px) saturate(1.4) !important;
    border-bottom: 1px solid rgba(255, 255, 255, 0.12) !important;
    box-shadow: 0 4px 30px rgba(0, 0, 0, 0.35) !important;
}

/* ==================== 导航标签 ==================== */
.nav-tabs {
    display: flex;
    gap: 6px;
    padding: 6px;
    background: rgba(255, 255, 255, 0.04);
    border-radius: 14px;
    border: 1px solid var(--glass-border-soft);
}

.nav-tab {
    padding: 9px 18px !important;
    border-radius: 10px !important;
    font-weight: 500 !important;
    font-size: 13.5px !important;
    letter-spacing: 0.02em !important;
    color: rgba(255, 255, 255, 0.72) !important;
    background: transparent !important;
    border: none !important;
    transition: all 0.25s ease !important;
    position: relative;
}

.nav-tab:hover {
    color: rgba(255, 255, 255, 0.96) !important;
    background: rgba(255, 255, 255, 0.09) !important;
}

.nav-tab.active {
    color: white !important;
    background: linear-gradient(135deg, rgba(102, 126, 234, 0.65) 0%, rgba(118, 75, 162, 0.65) 100%) !important;
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4) !important;
}

/* ==================== 子导航面板 ==================== */
.sub-nav-panel {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    padding: 12px 14px;
    background: rgba(255, 255, 255, 0.035);
    border: 1px solid var(--glass-border-soft);
    border-radius: 16px;
    margin-bottom: 20px;
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
}

.sub-nav-item {
    padding: 10px 20px !important;
    border-radius: 12px !important;
    background: rgba(255, 255, 255, 0.06) !important;
    border: 1px solid var(--glass-border-soft) !important;
    color: rgba(255, 255, 255, 0.82) !important;
    font-weight: 500 !important;
    font-size: 13.5px !important;
    transition: all 0.25s ease !important;
    display: flex;
    align-items: center;
    gap: 8px;
}

.sub-nav-item:hover {
    background: rgba(255, 255, 255, 0.1) !important;
    border-color: rgba(255, 255, 255, 0.18) !important;
    transform: translateY(-1px);
}

.sub-nav-item.active {
    background: linear-gradient(135deg, rgba(102, 126, 234, 0.45) 0%, rgba(118, 75, 162, 0.45) 100%) !important;
    border-color: rgba(139, 122, 255, 0.55) !important;
    color: white !important;
    box-shadow: 0 4px 14px rgba(102, 126, 234, 0.3) !important;
}

/* ==================== 功能标记点 ==================== */
.nav-dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    display: inline-block;
    margin-right: 8px;
    box-shadow: 0 0 8px currentColor;
}

.dot-blue { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); color: #4facfe; }
.dot-purple { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: #667eea; }
.dot-green { background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); color: #38ef7d; }
.dot-orange { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: #f093fb; }
.dot-cyan { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); color: #4facfe; }

/* ==================== 输入框 ==================== */
.glass-input .q-field__control {
    background: rgba(255, 255, 255, 0.055) !important;
    border: 1px solid var(--glass-border-soft) !important;
    border-radius: 12px !important;
    transition: all 0.2s ease !important;
}

.glass-input .q-field__control:hover {
    border-color: rgba(255, 255, 255, 0.2) !important;
    background: rgba(255, 255, 255, 0.075) !important;
}

.glass-input .q-field__control:focus-within {
    border-color: rgba(139, 122, 255, 0.65) !important;
    background: rgba(255, 255, 255, 0.085) !important;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.16), 0 0 24px rgba(102, 126, 234, 0.14) !important;
}

.glass-input .q-field__label {
    color: rgba(255, 255, 255, 0.62) !important;
    font-weight: 500 !important;
}

.glass-input input, .glass-input textarea {
    color: rgba(255, 255, 255, 0.96) !important;
}

.glass-input textarea {
    line-height: 1.7 !important;
}

/* ==================== 按钮体系 ==================== */
.glass-btn {
    background: linear-gradient(135deg, rgba(102, 126, 234, 0.72) 0%, rgba(118, 75, 162, 0.72) 100%) !important;
    border: 1px solid rgba(255, 255, 255, 0.16) !important;
    border-radius: 12px !important;
    padding: 9px 22px !important;
    font-weight: 600 !important;
    letter-spacing: 0.02em !important;
    color: white !important;
    transition: all 0.25s ease !important;
    box-shadow: 0 4px 16px rgba(102, 126, 234, 0.28) !important;
}

.glass-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 28px rgba(102, 126, 234, 0.42) !important;
    background: linear-gradient(135deg, rgba(102, 126, 234, 0.9) 0%, rgba(118, 75, 162, 0.9) 100%) !important;
    border-color: rgba(255, 255, 255, 0.24) !important;
}

.glass-btn-secondary {
    background: rgba(255, 255, 255, 0.08) !important;
    border: 1px solid var(--glass-border) !important;
    border-radius: 12px !important;
    color: rgba(255, 255, 255, 0.9) !important;
    font-weight: 500 !important;
}

.glass-btn-secondary:hover {
    background: rgba(255, 255, 255, 0.13) !important;
    border-color: rgba(255, 255, 255, 0.24) !important;
}

/* ==================== 展开面板 ==================== */
.glass-expansion {
    background: rgba(255, 255, 255, 0.035) !important;
    border: 1px solid var(--glass-border-soft) !important;
    border-radius: 12px !important;
    margin-bottom: 8px !important;
}

.glass-expansion .q-expansion-item__container {
    background: transparent !important;
}

.glass-expansion .q-expansion-item__summary {
    min-height: 44px !important;
    color: rgba(255, 255, 255, 0.9) !important;
}

/* ==================== 选项卡 ==================== */
.glass-tabs {
    background: rgba(255, 255, 255, 0.035);
    border: 1px solid var(--glass-border-soft);
    border-radius: 14px;
    padding: 4px;
}

.glass-tabs .q-tab {
    border-radius: 10px !important;
    margin: 0 2px !important;
    min-height: 40px !important;
    font-weight: 500 !important;
    color: rgba(255, 255, 255, 0.65) !important;
    transition: all 0.2s ease !important;
}

.glass-tabs .q-tab:hover {
    color: rgba(255, 255, 255, 0.95) !important;
    background: rgba(255, 255, 255, 0.06) !important;
}

.glass-tabs .q-tab--active {
    background: linear-gradient(135deg, rgba(102, 126, 234, 0.5) 0%, rgba(118, 75, 162, 0.5) 100%) !important;
    color: white !important;
    box-shadow: 0 3px 12px rgba(102, 126, 234, 0.32) !important;
}

.glass-tabs .q-tab-panel {
    background: transparent !important;
    padding: 12px 4px !important;
}

/* ==================== 对话框 ==================== */
.glass-dialog .q-card {
    background: rgba(28, 28, 48, 0.96) !important;
    backdrop-filter: blur(24px) !important;
    -webkit-backdrop-filter: blur(24px) !important;
    border: 1px solid var(--glass-border) !important;
    border-radius: 18px !important;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5) !important;
}

/* 普通卡片内的对话框兜底（q-dialog 内非 glass-card 卡片） */
.q-dialog .q-card:not(.glass-card):not(.glass-card-secondary) {
    background: rgba(28, 28, 48, 0.97) !important;
    border: 1px solid var(--glass-border) !important;
    border-radius: 18px !important;
    color: var(--text-primary) !important;
}

/* ==================== 滚动条 ==================== */
::-webkit-scrollbar {
    width: 7px;
    height: 7px;
}

::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.03);
    border-radius: 4px;
}

::-webkit-scrollbar-thumb {
    background: rgba(255, 255, 255, 0.18);
    border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
    background: rgba(255, 255, 255, 0.3);
}

/* ==================== 动画 ==================== */
@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(16px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.animate-in {
    animation: fadeInUp 0.35s cubic-bezier(0.22, 1, 0.36, 1);
}

/* ==================== 状态徽章 ==================== */
.status-badge {
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 0.03em;
}

.status-active {
    background: linear-gradient(135deg, rgba(17, 153, 142, 0.35) 0%, rgba(56, 239, 125, 0.35) 100%);
    color: #38ef7d;
    border: 1px solid rgba(56, 239, 125, 0.4);
    box-shadow: 0 0 12px rgba(56, 239, 125, 0.18);
}

.status-inactive {
    background: rgba(255, 255, 255, 0.05);
    color: rgba(255, 255, 255, 0.5);
    border: 1px solid var(--glass-border-soft);
}

/* ==================== 标题体系 ==================== */

/* 页面标题：大号渐变 */
.page-title {
    font-size: 26px !important;
    font-weight: 700 !important;
    letter-spacing: 0.01em !important;
    background: linear-gradient(135deg, #ffffff 0%, rgba(255, 255, 255, 0.75) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 22px !important;
    line-height: 1.3 !important;
}

/* 区块标题：卡片头部，左侧渐变竖条 */
.section-title {
    position: relative;
    font-size: 16px !important;
    font-weight: 600 !important;
    color: var(--text-primary) !important;
    padding-left: 12px !important;
    margin-bottom: 14px !important;
    line-height: 1.4 !important;
}

.section-title::before {
    content: '';
    position: absolute;
    left: 0;
    top: 15%;
    bottom: 15%;
    width: 4px;
    border-radius: 2px;
    background: var(--accent-gradient);
    box-shadow: 0 0 10px rgba(102, 126, 234, 0.6);
}

/* ==================== 统计卡片 ==================== */
.stat-card {
    background: linear-gradient(160deg, rgba(255, 255, 255, 0.06) 0%, rgba(255, 255, 255, 0.03) 100%) !important;
    border: 1px solid var(--glass-border) !important;
    border-radius: 16px !important;
    padding: 20px !important;
    text-align: center;
    transition: all 0.3s ease !important;
}

.stat-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.28) !important;
    border-color: rgba(255, 255, 255, 0.2) !important;
}

.stat-number {
    font-size: 34px !important;
    font-weight: 700 !important;
    letter-spacing: 0.02em !important;
    background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.stat-label {
    color: var(--text-muted) !important;
    font-size: 13px !important;
    margin-top: 6px !important;
    font-weight: 500 !important;
}

/* ==================== Markdown 内容可读性 ==================== */
.q-markdown, .markdown-body {
    line-height: 1.75 !important;
    color: var(--text-primary) !important;
}

.q-markdown h1, .q-markdown h2, .q-markdown h3 {
    font-weight: 600 !important;
    color: white !important;
    border-bottom: 1px solid var(--glass-border-soft) !important;
    padding-bottom: 6px !important;
}

.q-markdown code {
    background: rgba(255, 255, 255, 0.08) !important;
    padding: 2px 6px !important;
    border-radius: 4px !important;
    font-size: 0.9em !important;
}

.q-markdown blockquote {
    border-left: 3px solid rgba(102, 126, 234, 0.6) !important;
    background: rgba(255, 255, 255, 0.03) !important;
    padding: 8px 14px !important;
    border-radius: 0 8px 8px 0 !important;
    color: var(--text-secondary) !important;
}

/* ==================== 允许文本选择 ==================== */
* {
    -webkit-user-select: text !important;
    -moz-user-select: text !important;
    -ms-user-select: text !important;
    user-select: text !important;
}

.q-markdown, .q-label, .markdown-body {
    -webkit-user-select: text !important;
    -moz-user-select: text !important;
    user-select: text !important;
}

/* ==================== 表格精修 ==================== */
.q-table {
    background: transparent !important;
    color: var(--text-primary) !important;
}

.q-table thead th {
    font-weight: 600 !important;
    color: var(--text-secondary) !important;
    border-bottom: 1px solid var(--glass-border) !important;
}

.q-table tbody td {
    border-bottom: 1px solid rgba(255, 255, 255, 0.06) !important;
}

/* ==================== 响应式 ==================== */
@media (max-width: 768px) {
    .nav-tabs {
        flex-wrap: wrap;
    }

    .sub-nav-panel {
        flex-direction: column;
    }

    .sub-nav-item {
        width: 100%;
        justify-content: center;
    }
}
</style>
"""


def inject_styles():
    """注入全局样式"""
    from nicegui import ui
    ui.add_head_html(GLASSMORPHISM_CSS)


# 导航配置 - 按工作流程组织
NAV_STRUCTURE = {
    "daily": {
        "label": "日常工作",
        "items": [
            ("home", "首页", "blue"),
            ("daily_action", "今日行动", "purple"),
        ]
    },
    "data": {
        "label": "数据管理",
        "items": [
            ("data_center", "数据中心", "cyan"),
            ("hospitals", "医院管理", "blue"),
            ("contacts", "联系人", "purple"),
            ("doctors", "医生档案", "orange"),
        ]
    },
    "customer": {
        "label": "客户管理",
        "items": [
            ("customer_tracking", "客户追踪", "green"),
        ]
    },
    "prepare": {
        "label": "拜访准备",
        "items": [
            ("preparation", "准备计划", "green"),
            ("knowledge", "知识库", "blue"),
        ]
    },
    "record": {
        "label": "拜访记录",
        "items": [
            ("visit", "交流记录", "blue"),
            ("reflection", "个人总结", "purple"),
        ]
    },
    "analysis": {
        "label": "分析成长",
        "items": [
            ("ai_chat", "AI 助手", "cyan"),
            ("ai_analysis", "AI 数据分析", "blue"),
            ("reports", "报告中心", "green"),
            ("smart_export", "周报月报", "purple"),
        ]
    },
    "system": {
        "label": "系统",
        "items": [
            ("settings", "设置", "orange"),
        ]
    }
}
