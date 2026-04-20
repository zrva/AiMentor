# run.ps1 - Start AiMentor completely hidden, open browser automatically

# 1. Read config files
$GPU_TYPE = (Get-Content ".gpu_type" -Raw).Trim()
$MODEL_SIZE = (Get-Content ".model_size" -Raw).Trim()

# 2. Find model file
$modelFile = Get-ChildItem "models\gguf\$MODEL_SIZE\*.gguf" | Select-Object -First 1 | ForEach-Object { $_.FullName }

# 3. Set GPU params
if ($GPU_TYPE -eq "cpu") {
    $NGL = 0; $CTX = 512; $THREADS = 1; $BATCH = 32
} else {
    $NGL = 99; $CTX = 4096; $THREADS = 6; $BATCH = 512
}

# 4. Activate venv
& ".\venv\Scripts\Activate.ps1"

# 5. Start llama-server HIDDEN
$llamaArgs = @("-m", $modelFile, "--port 8080", "-ngl $NGL", "-c $CTX", "-t $THREADS", "-cb", "-b $BATCH")
Start-Process ".\bin\$GPU_TYPE\llama-server.exe" -ArgumentList $llamaArgs -WindowStyle Hidden

# 6. Wait for server
Start-Sleep 5

# 7. Start streamlit HIDDEN
Start-Process "streamlit" -ArgumentList "run", "app\main.py" -WindowStyle Hidden

# 8. OPEN BROWSER automatically
Start-Process "http://localhost:8501"
