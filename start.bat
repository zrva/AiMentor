@echo off
echo Starting AiMentor...
cd /d "%~dp0"
powershell -ExecutionPolicy Bypass -WindowStyle Hidden -File "help.ps1"
exit