#!/bin/sh
# AiMentor - Start script for macOS and Linux
# Usage: ./start.sh
set -e

SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
cd "$SCRIPT_DIR"

VENV_PY="$SCRIPT_DIR/venv/bin/python3"
if [ ! -x "$VENV_PY" ]; then
    echo "Error: Python environment not found. Please run ./download.sh first."
    exit 1
fi

check_port() {
    "$VENV_PY" -c "
import socket
s = socket.socket()
s.settimeout(1)
exit(0 if s.connect_ex(('127.0.0.1', $1)) == 0 else 1)
"
}

# 1. Read config files (with defaults)
GPU_TYPE="cpu"
MODEL_SIZE="4B"
[ -f ".gpu_type" ] && GPU_TYPE=$(cat ".gpu_type" | xargs)
[ -f ".model_size" ] && MODEL_SIZE=$(cat ".model_size" | xargs)

# 2. Find model file
MODEL_DIR="$SCRIPT_DIR/models/gguf/$MODEL_SIZE"
MODEL_FILE=$(ls "$MODEL_DIR"/*.gguf 2>/dev/null | head -n 1)
if [ -z "$MODEL_FILE" ]; then
    echo "Error: Model file not found in $MODEL_DIR. Please run ./download.sh first."
    exit 1
fi

# 3. Set GPU params
if [ "$GPU_TYPE" = "cpu" ]; then
    NGL=0
    CTX=2048
    THREADS=2
    BATCH=64
else
    NGL=99
    CTX=4096
    THREADS=6
    BATCH=512
fi

# 4. Start llama-server if it is not already listening
LLAMA_EXE="$SCRIPT_DIR/bin/$GPU_TYPE/llama-server"
if [ ! -x "$LLAMA_EXE" ]; then
    echo "Error: llama-server executable not found at $LLAMA_EXE. Please run ./download.sh first."
    exit 1
fi

if check_port 8080; then
    echo "llama-server is already running on port 8080."
else
    echo "Starting llama-server..."
    nohup "$LLAMA_EXE" -m "$MODEL_FILE" --port 8080 -ngl $NGL -c $CTX -t $THREADS -cb -b $BATCH > server.log 2>&1 &
fi

# 5. Wait for server
sleep 3

# 6. Start streamlit if it is not already listening
if check_port 8501; then
    echo "Streamlit is already running on port 8501."
else
    echo "Starting Streamlit..."
    nohup "$SCRIPT_DIR/venv/bin/streamlit" run app.py --browser.gatherUsageStats false --server.headless true > app.log 2>&1 &
fi

# 7. Wait for Streamlit to initialize, then force-open browser
sleep 3
URL="http://localhost:8501"
echo "Opening browser to $URL ..."

if command -v open >/dev/null 2>&1; then
    open "$URL"
elif command -v xdg-open >/dev/null 2>&1; then
    xdg-open "$URL"
else
    echo "Please open $URL in your web browser."
fi
