@echo off
echo ==============================================
echo Starting AiMentor...
echo ==============================================

:: ── Find GPU type from setup ──
set "GPU_TYPE=cpu"
if exist ".gpu_type" (
    set /p GPU_TYPE=<.gpu_type
)

:: ── Find model size from setup ──
set "MODEL_SIZE=8B"
if exist ".model_size" (
    set /p MODEL_SIZE=<.model_size
)

:: ── Locate llama-server binary ──
set "SERVER_BIN="
if /I "%GPU_TYPE%"=="cuda" if exist "bin\cuda\llama-server.exe" set "SERVER_BIN=bin\cuda\llama-server.exe"
if /I "%GPU_TYPE%"=="hip" if exist "bin\hip\llama-server.exe" set "SERVER_BIN=bin\hip\llama-server.exe"
if /I "%GPU_TYPE%"=="vulkan" if exist "bin\vulkan\llama-server.exe" set "SERVER_BIN=bin\vulkan\llama-server.exe"
if /I "%GPU_TYPE%"=="cpu" if exist "bin\cpu\llama-server.exe" set "SERVER_BIN=bin\cpu\llama-server.exe"
if "%SERVER_BIN%"=="" if exist "bin\cuda\llama-server.exe" set "SERVER_BIN=bin\cuda\llama-server.exe"
if "%SERVER_BIN%"=="" if exist "bin\hip\llama-server.exe" set "SERVER_BIN=bin\hip\llama-server.exe"
if "%SERVER_BIN%"=="" if exist "bin\vulkan\llama-server.exe" set "SERVER_BIN=bin\vulkan\llama-server.exe"
if "%SERVER_BIN%"=="" if exist "bin\cpu\llama-server.exe" set "SERVER_BIN=bin\cpu\llama-server.exe"
REM Legacy fallback: binary in root folder
if "%SERVER_BIN%"=="" if exist "llama-server.exe" set "SERVER_BIN=llama-server.exe"

if "%SERVER_BIN%"=="" (
    echo [ERR] llama-server.exe not found!
    echo       Run setup first:  setup.bat
    pause
    exit /b 1
)

:: ── Locate GGUF model file ──
set "MODEL_FILE="
for %%f in ("models\gguf\%MODEL_SIZE%\*.gguf") do set "MODEL_FILE=%%f"
REM Legacy fallback: model in root folder
if "%MODEL_FILE%"=="" (
    for %%f in ("*.gguf") do set "MODEL_FILE=%%f"
)

if "%MODEL_FILE%"=="" (
    echo [ERR] No .gguf model found!
    echo       Run setup first:  setup.bat
    pause
    exit /b 1
)

:: ── Determine GPU layers ──
set "NGL=0"
set "CTX=4096"
set "THREADS=6"
set "BATCH=512"
if "%GPU_TYPE%"=="cuda" set "NGL=99"
if "%GPU_TYPE%"=="hip" set "NGL=99"
if "%GPU_TYPE%"=="vulkan" set "NGL=99"
if /I "%GPU_TYPE%"=="cpu" (
    set "CTX=512"
    set "THREADS=1"
    set "BATCH=32"
)

echo.
echo   Binary : %SERVER_BIN%
echo   Model  : %MODEL_FILE%
echo   GPU    : %GPU_TYPE% (ngl=%NGL%)
echo   Context: %CTX%
echo   Threads: %THREADS%
echo   Batch  : %BATCH%
echo.

:: ── Launch LLM Backend ──
echo Starting Llama Backend...
start "AiMentor LLM Engine" cmd /k ""%SERVER_BIN%" -m "%MODEL_FILE%" --port 8080 -ngl %NGL% -c %CTX% -t %THREADS% -cb -b %BATCH%"

echo Waiting for server to initialize (10 seconds)...
timeout /t 10 /nobreak >nul

:: ── Launch Streamlit ──
echo Starting Streamlit Web Interface...
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else (
    echo WARNING: Virtual environment not found. Run setup.bat first.
)
streamlit run app.py

pause
