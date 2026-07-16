@echo off
chcp 65001 > nul
title AI Look Windows 11 - 虚拟环境与依赖一键安装
:: 强制切到批处理所在目录
cd /d "%~dp0"

echo ========================================================
echo        AI Look Desktop System 依赖一键配置脚本
echo        安装位置: %CD%
echo ========================================================
echo.

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
    echo [错误] 未检测到 Python，请先安装 Python 3.10 或以上版本并勾选 "Add Python to PATH"！
    pause
    exit /b 1
)

echo [检测到 Python] %PY_CMD%
echo.

echo [1/3] 正在建立独立 Python 虚拟环境 (venv)...
%PY_CMD% -m venv venv
if errorlevel 1 (
    echo [警告] venv 创建失败，将直接尝试使用系统的 pip 环境...
)

if exist "venv\Scripts\activate.bat" (
    echo [2/3] 激活虚拟环境...
    call "venv\Scripts\activate.bat"
    set PY_CMD=python
) else (
    echo [2/3] 使用全局系统 Python 准备安装...
)

echo [3/3] 正在升级 pip 并安装 requirements.txt 依赖包...
%PY_CMD% -m pip install --upgrade pip
%PY_CMD% -m pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo ❌ [错误] 依赖安装过程中出现网络或权限异常！请检查网络连接或以管理员身份运行。
    pause
    exit /b 1
)

echo.
echo ========================================================
echo ✅ 全部配置完成！现在您可以双击 `start_ailook.bat` 运行主程序。
echo ========================================================
pause
