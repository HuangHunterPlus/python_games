@echo off
chcp 65001 >nul
cd /d "%~dp0"
if exist "dist\AIPet.exe" (
    echo 启动 AI 桌面宠物（EXE）...
    start "" "dist\AIPet.exe"
) else (
    echo 启动 AI 桌面宠物（Python）...
    python main.py
)
