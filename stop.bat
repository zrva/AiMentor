@echo off
echo Stopping AiMentor...
powershell -ExecutionPolicy Bypass -Command "Stop-Process -Name llama-server -Force -ErrorAction SilentlyContinue; Get-CimInstance Win32_Process -Filter \"Name = 'python.exe'\" | Where-Object { $_.CommandLine -match 'streamlit run app.py' } | Invoke-CimMethod -MethodName Terminate | Out-Null"
echo AiMentor stopped.
timeout /t 2 /nobreak >nul
exit