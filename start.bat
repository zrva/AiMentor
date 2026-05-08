@echo off
echo Starting AiMentor...
cd /d "%~dp0"
powershell -ExecutionPolicy Bypass -WindowStyle Hidden -File "%~dp0AiMentor_Core_DO_NOT_DELETE\help.ps1"
exit