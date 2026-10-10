"""
医药信息专员个人职业操作系统
程序入口
"""
import sys
from pathlib import Path

# 确保项目根目录在路径中
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.file_manager import file_manager
from core.decision_engine import decision_engine


def check_first_run():
    """检查是否首次运行"""
    doctors = file_manager.list_files(file_manager.doctors_dir)
    if not doctors:
        print("=" * 50)
        print("欢迎使用医药信息专员个人职业操作系统！")
        print("这是您的首次运行。")
        print("请在界面中配置您的 DeepSeek API Key 以启用 AI 功能。")
        print("=" * 50)


def check_daily_action():
    """检查今日行动单"""
    if decision_engine.should_generate_new_action():
        print("将在启动后生成今日行动单...")


def main():
    """主函数"""
    print("正在启动医药信息专员助手...")
    
    # 初始化检查
    check_first_run()
    check_daily_action()
    
    # 启动 UI
    print("正在加载用户界面...")
    
    from nicegui import ui
    from ui.app import create_app
    
    create_app()
    
    ui.run(
        title='医药信息专员助手',
        dark=True,
        native=True,  # 桌面应用模式
        window_size=(1400, 900),
        reload=False
    )


if __name__ == "__main__":
    main()
