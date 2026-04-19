@echo off
echo ==============================================
echo AiMentor Setup
echo ==============================================
echo.
echo Starting setup in PowerShell...
echo.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0download.ps1"
if errorlevel 1 (
    echo.
    echo [ERR] Setup failed.
    pause
    exit /b 1
)
pause
