@echo off
chcp 65001 > nul
title AI Look Windows 11 - 一键打包为 EXE 应用
cd /d "%~dp0"

set PY_CMD=python
if exist "venv\Scripts\activate.bat" (
    call "venv\Scripts\activate.bat"
    set PY_CMD=python
) else (
    python --version >nul 2>&1
    if errorlevel 1 (
        py -3 --version >nul 2>&1
        if not errorlevel 1 (
            set PY_CMD=py -3
        ) else (
            set PY_CMD=python3
        )
    )
)

echo 正在开始编译和打包...
%PY_CMD% build.py
pause
