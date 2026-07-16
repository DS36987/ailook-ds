@echo off
chcp 65001 > nul
title AI Look Windows 11 智能视觉识别系统 - 一键启动器
echo ========================================================
echo        AI Look Desktop System (Windows 11 Edition)
echo ========================================================
echo.

:: 检查 Python 是否已安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未在系统环境变量 PATH 中检测到 Python 3.10+。
    echo 请前往 https://www.python.org/downloads/ 下载并勾选 "Add Python to PATH" 安装。
    pause
    exit /b 1
)

:: 如果存在 venv 虚拟环境则激活
if exist "venv\Scripts\activate.bat" (
    echo [提示] 检测到虚拟环境，正在激活 venv...
    call venv\Scripts\activate.bat
) else (
    echo [提示] 未检测到独立虚拟环境，检查依赖包...
    python -m pip install --upgrade pip >nul 2>&1
    python -m pip install -r requirements.txt
)

echo.
echo [启动] 正在打开 AI Look 主操作界面与独立分离窗口系统...
start "" pythonw main.py
exit /b 0
