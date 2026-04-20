' Stop AiMentor - Double-click to stop the app
CreateObject("WScript.Shell").Run "powershell -WindowStyle Hidden -File stop-internal.ps1", 0
MsgBox "AiMentor stopped.", 64, "AiMentor"