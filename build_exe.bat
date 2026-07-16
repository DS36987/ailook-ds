@echo off
chcp 65001 > nul
title AI Look Windows 11 - 一键打包为 EXE 应用
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)
python build.py
pause
