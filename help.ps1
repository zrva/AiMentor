# help.ps1 - Start AiMentor completely hidden

# Set working directory to where script is located
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

# 1. Read config files (with defaults)
$GPU_TYPE = "cpu"
$MODEL_SIZE = "4B"
if (Test-Path ".gpu_type") { $GPU_TYPE = (Get-Content ".gpu_type" -Raw).Trim() }
if (Test-Path ".model_size") { $MODEL_SIZE = (Get-Content ".model_size" -Raw).Trim() }

# 2. Find model file
$modelFile = Get-ChildItem "models\gguf\$MODEL_SIZE\*.gguf" -ErrorAction SilentlyContinue | Select-Object -First 1 | ForEach-Object { $_.FullName }
if (-not $modelFile) { exit 1 }

# 3. Set GPU params
if ($GPU_TYPE -eq "cpu") {
    $NGL = 0; $CTX = 2048; $THREADS = 2; $BATCH = 64
} else {
    $NGL = 99; $CTX = 4096; $THREADS = 6; $BATCH = 512
}

# 4. Start llama-server
$llamaExe = Join-Path $PSScriptRoot "bin\$GPU_TYPE\llama-server.exe"
if (-not (Test-Path $llamaExe)) { exit 1 }

$llamaArgs = @("-m", $modelFile, "--port", "8080", "-ngl", $NGL, "-c", $CTX, "-t", $THREADS, "-cb", "-b", $BATCH)
Start-Process $llamaExe -ArgumentList $llamaArgs -WindowStyle Hidden

# 5. Wait for server
Start-Sleep 5

# 6. Start streamlit
$streamlitCmd = Join-Path $PSScriptRoot "venv\Scripts\Activate.bat"
Start-Process "cmd.exe" -ArgumentList "/c", "$streamlitCmd && streamlit run app.py" -WindowStyle Hidden -WorkingDirectory $ScriptDir

# 7. Open browser (Streamlit does this automatically)
# Start-Process "http://localhost:8501"