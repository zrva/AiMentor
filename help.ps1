# help.ps1 - Start AiMentor (debug version shows errors)

# Set working directory to where script is located
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir
Write-Host "Working dir: $ScriptDir"

# 1. Read config files (with defaults)
$GPU_TYPE = "cpu"
$MODEL_SIZE = "4B"
if (Test-Path ".gpu_type") { $GPU_TYPE = (Get-Content ".gpu_type" -Raw).Trim() }
if (Test-Path ".model_size") { $MODEL_SIZE = (Get-Content ".model_size" -Raw).Trim() }
Write-Host "GPU: $GPU_TYPE, Model: $MODEL_SIZE"

# 2. Find model file
$modelFile = Get-ChildItem "models\gguf\$MODEL_SIZE\*.gguf" -ErrorAction SilentlyContinue | Select-Object -First 1 | ForEach-Object { $_.FullName }
Write-Host "Model file: $modelFile"
if (-not $modelFile) {
    Write-Host "[ERR] Model not found: models\gguf\$MODEL_SIZE\*.gguf"
    exit 1
}

# 3. Set GPU params
if ($GPU_TYPE -eq "cpu") {
    $NGL = 0; $CTX = 512; $THREADS = 1; $BATCH = 32
} else {
    $NGL = 99; $CTX = 4096; $THREADS = 6; $BATCH = 512
}

# 4. Get venv python path
$VenvPy = Join-Path $PSScriptRoot "venv\Scripts\python.exe"
Write-Host "Venv Python: $VenvPy"

# 5. Start llama-server HIDDEN with correct argument format
$llamaExe = Join-Path $PSScriptRoot "bin\$GPU_TYPE\llama-server.exe"
Write-Host "llama-server: $llamaExe"
if (-not (Test-Path $llamaExe)) {
    Write-Host "[ERR] llama-server not found: $llamaExe"
    exit 1
}

Write-Host "Starting llama-server..."
$llamaArgs = @("-m", $modelFile, "--port", "8080", "-ngl", $NGL, "-c", $CTX, "-t", $THREADS, "-cb", "-b", $BATCH)
Start-Process $llamaExe -ArgumentList $llamaArgs -WindowStyle Hidden

# 6. Wait for server to start
Start-Sleep 5

# 7. Start streamlit - use cmd /c to activate venv and run streamlit
$streamlitCmd = ".\venv\Scripts\Activate.ps1; streamlit run app\main.py"
Start-Process "cmd.exe" -ArgumentList "/c", $streamlitCmd -WindowStyle Hidden -WorkingDirectory $ScriptDir

# 8. OPEN BROWSER automatically
Start-Process "http://localhost:8501"