@echo off
setlocal EnableDelayedExpansion

echo ==============================================
echo AiMentor Setup
echo ==============================================
echo.

set "CORE_DIR=%~dp0AiMentor_Core_DO_NOT_DELETE"

:: Check if already installed (venv exists)
if not exist "%CORE_DIR%\venv\Scripts\python.exe" goto :fresh_install

echo [INFO] AiMentor is already installed.
echo.
echo   [1] Reconfigure GPU / Re-download model
echo   [2] Exit (no changes)
echo.
set /p "CHOICE=Enter your choice (1/2): "

if /i "!CHOICE!"=="1" (
    echo.
    echo Starting reconfiguration...
    echo.
    powershell -NoProfile -ExecutionPolicy Bypass -File "%CORE_DIR%\download.ps1" -Reconfigure
    if errorlevel 1 (
        echo.
        echo [ERR] Reconfiguration failed.
        pause
        exit /b 1
    )
    pause
    exit /b 0
)

echo No changes made.
timeout /t 2 /nobreak >nul
exit /b 0

:fresh_install
echo Starting first-time setup in PowerShell...
echo.
powershell -NoProfile -ExecutionPolicy Bypass -File "%CORE_DIR%\download.ps1"
if errorlevel 1 (
    echo.
    echo [ERR] Setup failed.
    pause
    exit /b 1
)
pause
