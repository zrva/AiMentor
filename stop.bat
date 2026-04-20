@echo off
echo Stopping AiMentor...
taskkill /F /IM llama-server.exe 2>NUL
taskkill /F /IM streamlit.exe 2>NUL
echo All services stopped.