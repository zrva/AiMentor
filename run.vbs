' Run AiMentor completely hidden (no cmd window)
Option Explicit
Dim WshShell, fso, GPU_TYPE, MODEL_SIZE, SERVER_BIN, MODEL_FILE, NGL, CTX, THREADS, BATCH, line

Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

' Find GPU type
GPU_TYPE = "cpu"
If fso.FileExists(".gpu_type") Then
    Dim ts: Set ts = fso.OpenTextFile(".gpu_type", 1)
    If Not ts.AtEndOfStream Then GPU_TYPE = ts.ReadLine
    ts.Close
End If

' Find model size
MODEL_SIZE = "8B"
If fso.FileExists(".model_size") Then
    Dim ts2: Set ts2 = fso.OpenTextFile(".model_size", 1)
    If Not ts2.AtEndOfStream Then MODEL_SIZE = ts2.ReadLine
    ts2.Close
End If

' Locate llama-server
SERVER_BIN = ""
If LCase(GPU_TYPE) = "cuda" And fso.FileExists("bin\cuda\llama-server.exe") Then SERVER_BIN = "bin\cuda\llama-server.exe"
If SERVER_BIN = "" And LCase(GPU_TYPE) = "hip" And fso.FileExists("bin\hip\llama-server.exe") Then SERVER_BIN = "bin\hip\llama-server.exe"
If SERVER_BIN = "" And LCase(GPU_TYPE) = "vulkan" And fso.FileExists("bin\vulkan\llama-server.exe") Then SERVER_BIN = "bin\vulkan\llama-server.exe"
If SERVER_BIN = "" And LCase(GPU_TYPE) = "cpu" And fso.FileExists("bin\cpu\llama-server.exe") Then SERVER_BIN = "bin\cpu\llama-server.exe"
If SERVER_BIN = "" And fso.FileExists("bin\cuda\llama-server.exe") Then SERVER_BIN = "bin\cuda\llama-server.exe"
If SERVER_BIN = "" And fso.FileExists("bin\hip\llama-server.exe") Then SERVER_BIN = "bin\hip\llama-server.exe"
If SERVER_BIN = "" And fso.FileExists("bin\vulkan\llama-server.exe") Then SERVER_BIN = "bin\vulkan\llama-server.exe"
If SERVER_BIN = "" And fso.FileExists("bin\cpu\llama-server.exe") Then SERVER_BIN = "bin\cpu\llama-server.exe"

If SERVER_BIN = "" Then
    WScript.Echo "llama-server.exe not found! Run setup first."
    WScript.Quit 1
End If

' Locate model
MODEL_FILE = ""
Dim folder: Set folder = fso.GetFolder("models\gguf\" & MODEL_SIZE)
For Each line In folder.Files
    If LCase(fso.GetExtensionName(line.Name)) = "gguf" Then
        MODEL_FILE = line.Path
        Exit For
    End If
Next

If MODEL_FILE = "" Then
    WScript.Echo "No .gguf model found! Run setup first."
    WScript.Quit 1
End If

' Set GPU params
NGL = 0: CTX = 4096: THREADS = 6: BATCH = 512
If LCase(GPU_TYPE) = "cuda" Then NGL = 99
If LCase(GPU_TYPE) = "hip" Then NGL = 99
If LCase(GPU_TYPE) = "vulkan" Then NGL = 99
If LCase(GPU_TYPE) = "cpu" Then CTX = 512: THREADS = 1: BATCH = 32

' Activate venv if exists
If fso.FileExists("venv\Scripts\activate.bat") Then
    WshShell.Run "cmd /c venv\Scripts\activate.bat", 0, False
End If

' Start llama-server in background
WshShell.Run "cmd /c start "" /b """ & SERVER_BIN & """ -m """ & MODEL_FILE & """ --port 8080 -ngl " & NGL & " -c " & CTX & " -t " & THREADS & " -cb -b " & BATCH, 0, False

' Wait 5 seconds
WScript.Sleep 5000

' Start streamlit
WshShell.Run "cmd /c streamlit run app\main.py", 1, False