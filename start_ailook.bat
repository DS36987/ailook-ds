@echo off
chcp 65001 > nul
title AI Look Windows 11 智能视觉识别系统 - 启动控制台
:: 强制将工作目录切换为本批处理所在所在的绝对路径 (极重要，修复以管理员或从快捷方式运行时的路径找不到问题)
cd /d "%~dp0"

echo ========================================================
echo        AI Look Desktop System (Windows 11 Edition)
echo        当前工作目录: %CD%
echo ========================================================
echo.

:: 探测系统的 Python 解释器命令
set PY_CMD=
python --version >nul 2>&1
if not errorlevel 1 (
    set PY_CMD=python
) else (
    py -3 --version >nul 2>&1
    if not errorlevel 1 (
        set PY_CMD=py -3
    ) else (
        python3 --version >nul 2>&1
        if not errorlevel 1 (
            set PY_CMD=python3
        )
    )
)

if "%PY_CMD%"=="" (
    echo [错误] 未在系统环境变量 PATH 中检测到 Python。
    echo 请前往 https://www.python.org/downloads/ 下载 Python 3.10+ 安装，并在安装时务必勾选 "Add Python to PATH"！
    echo.
    pause
    exit /b 1
)

echo [检查] 检测到 Python 解释器: %PY_CMD%

:: 如果存在 venv 虚拟环境则激活并优先使用虚拟环境中的 Python
if exist "venv\Scripts\activate.bat" (
    echo [启动] 发现已建立的虚拟环境 (venv)，正在激活...
    call "venv\Scripts\activate.bat"
    set PY_CMD=python
) else (
    echo [检查] 未检测到独立虚拟环境，检查依赖环境是否齐全...
    %PY_CMD% -c "import PySide6, mss, PIL, edge_tts, pyttsx3, requests, pygame" >nul 2>&1
    if errorlevel 1 (
        echo [提示] 尚未完整安装依赖项！正在尝试为您自动安装 requirements.txt 依赖包...
        %PY_CMD% -m pip install --upgrade pip
        %PY_CMD% -m pip install -r requirements.txt
    )
)

echo.
echo [运行] 正在启动 AI Look 主系统与控制后台...
echo [提示] 运行中控制台将实时输出诊断信息，关闭此黑窗口即可终止系统。
echo ========================================================
%PY_CMD% main.py

if errorlevel 1 (
    echo.
    echo ========================================================
    echo [警告] 应用程序发生异常退出 (Error Level: %errorlevel%)！
    echo 请检查上方控制台报错信息或查看 `logs/` 目录下的崩溃日志。
    echo ========================================================
    pause
)
