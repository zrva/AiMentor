@echo off
echo Stopping AiMentor...
powershell -Command "Stop-Process -Name llama-server -Force -ErrorAction SilentlyContinue; Stop-Process -Name streamlit -Force -ErrorAction SilentlyContinue"
echo AiMentor stopped.
timeout /t 2 /nobreak >nul
exit