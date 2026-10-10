@echo off
chcp 65001 >nul
echo ================================
echo 医药信息专员助手 - 启动程序
echo ================================
echo.
echo [i] 正在启动程序...
echo.

python main.py

if errorlevel 1 (
    echo.
    echo [错误] 程序启动失败
    echo 请先运行 install.bat 安装依赖
    pause
)
