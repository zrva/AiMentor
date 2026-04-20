' Stop AiMentor completely hidden
Dim WshShell
Set WshShell = CreateObject("WScript.Shell")

' Kill llama-server
WshShell.Run "taskkill /F /IM llama-server.exe", 0, True

' Kill streamlit
WshShell.Run "taskkill /F /IM streamlit.exe", 0, True