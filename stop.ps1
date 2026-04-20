# stop.ps1 - Stop AiMentor
Stop-Process -Name llama-server -Force -ErrorAction SilentlyContinue
Stop-Process -Name streamlit -Force -ErrorAction SilentlyContinue
