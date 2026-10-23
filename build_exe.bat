@echo off
chcp 65001 >nul
echo ================================
echo MSL-OS - 打包为 Windows exe
echo ================================
echo.

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python，请先安装 Python 3.8+
    pause
    exit /b 1
)

REM 安装依赖（含打包工具）
echo [i] 正在安装依赖...
python -m pip install -r requirements.txt pyinstaller
if errorlevel 1 (
    echo [错误] 依赖安装失败
    pause
    exit /b 1
)

echo [i] 开始打包...
python -m PyInstaller --noconfirm --clean --onefile --windowed --name MSL-OS ^
  --collect-all nicegui ^
  --collect-all webview ^
  --collect-all clr_loader ^
  --collect-all pythonnet ^
  main.py

if errorlevel 1 (
    echo [错误] 打包失败
    pause
    exit /b 1
)

echo.
echo [√] 打包完成！exe 位于: dist\MSL-OS.exe
echo 该 exe 不包含任何个人数据，首次运行会自动创建 data、outputs 目录。
pause
