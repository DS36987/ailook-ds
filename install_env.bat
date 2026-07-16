@echo off
chcp 65001 > nul
title AI Look Windows 11 - 虚拟环境与依赖一键安装
echo ========================================================
echo        AI Look Desktop System 依赖一键配置脚本
echo ========================================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python，请先安装 Python 3.10 或以上版本。
    pause
    exit /b 1
)

echo [1/3] 正在创建 Python 虚拟环境 (venv)...
python -m venv venv

echo [2/3] 激活虚拟环境并升级 pip...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip

echo [3/3] 安装 requirements.txt 中指定的全部类库 (PySide6, mss, Pillow, edge-tts等)...
python -m pip install -r requirements.txt

echo.
echo ========================================================
echo ✅ 安装全部完成！现在您可以通过双击 `start_ailook.bat` 运行系统。
echo ========================================================
pause
