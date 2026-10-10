@echo off
chcp 65001 >nul
echo ================================
echo 医药信息专员助手 - 安装程序
echo ================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python，请先安装 Python 3.8 或更高版本
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [√] Python 已安装
echo.

REM 安装依赖
echo [i] 正在安装依赖包...
pip install -r requirements.txt

if errorlevel 1 (
    echo [错误] 依赖安装失败，请检查网络连接
    pause
    exit /b 1
)

echo.
echo ================================
echo [√] 安装完成！
echo ================================
echo.
echo 运行程序请执行: python main.py
echo 或双击运行 start.bat
echo.

pause
