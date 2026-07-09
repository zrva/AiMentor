#!/bin/sh
# AiMentor - One-Command Setup for macOS and Linux
# Usage: ./download.sh
set -e

# Model will be auto-selected based on GPU detection unless user overrides
USER_MODEL_OVERRIDE="${BONSAI_MODEL:-}"
RELEASE_TAG="prism-b9570-0ad1dab"
BASE_URL="https://github.com/PrismML-Eng/llama.cpp/releases/download/$RELEASE_TAG"

SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
VENV_DIR="$SCRIPT_DIR/venv"
VENV_PY="$VENV_DIR/bin/python3"
REQUIREMENTS_FILE="$SCRIPT_DIR/requirements.txt"

echo ""
echo "==========================================="
echo "   AiMentor - Full Setup (macOS/Linux)"
echo "==========================================="
echo ""

# ── 1. Python & Virtual Environment ──
echo "==> [1/6] Checking Python ..."
if ! command -v python3 >/dev/null 2>&1; then
    echo "[ERR] python3 not found. Please install Python 3.11+."
    exit 1
fi
echo "[OK] python3 found."

echo "==> [2/6] Setting up Python environment ..."
if [ -d "$VENV_DIR" ] && [ -x "$VENV_PY" ]; then
    echo "[OK] Virtual environment already exists."
else
    python3 -m venv "$VENV_DIR" || { echo "[ERR] Failed to create venv."; exit 1; }
    echo "[OK] Created virtual environment."
fi

echo "==> Installing Python dependencies ..."
"$VENV_PY" -m pip install --upgrade pip -q
if [ -f "$REQUIREMENTS_FILE" ]; then
    "$VENV_PY" -m pip install -r "$REQUIREMENTS_FILE" -q
else
    "$VENV_PY" -m pip install streamlit requests -q
fi
echo "[OK] Python dependencies installed."

# ── Helpers for GPU Detection (From Unsloth) ──
_has_usable_nvidia_gpu() {
    _nvsmi=""
    if command -v nvidia-smi >/dev/null 2>&1; then _nvsmi="nvidia-smi"
    elif [ -x "/usr/bin/nvidia-smi" ]; then _nvsmi="/usr/bin/nvidia-smi"
    fi
    if [ -n "$_nvsmi" ]; then
        if "$_nvsmi" -L 2>/dev/null | awk '/^GPU[[:space:]]+[0-9]+:/{found=1} END{exit !found}'; then
            return 0
        fi
    fi
    if [ -d /proc/driver/nvidia/gpus ] && [ -n "$(ls -A /proc/driver/nvidia/gpus 2>/dev/null)" ]; then
        return 0
    fi
    return 1
}

_has_amd_rocm_gpu() {
    if command -v rocminfo >/dev/null 2>&1 && rocminfo 2>/dev/null | awk '/Name:[[:space:]]*gfx[1-9][0-9]/{found=1} END{exit !found}'; then
        return 0
    elif command -v amd-smi >/dev/null 2>&1 && amd-smi list 2>/dev/null | awk '/^GPU[[:space:]]*[:\[][[:space:]]*[0-9]/{ found=1 } END{ exit !found }'; then
        return 0
    elif [ -e /dev/kfd ] && awk 'FNR==1{ gpu=0; amd=0 } /gpu_id/{ gpu=($2+0>0) } /vendor_id/{ amd=($2==4098) } gpu && amd { found=1 } END{ exit !found }' /sys/class/kfd/kfd/topology/nodes/*/properties 2>/dev/null; then
        return 0
    fi
    return 1
}

# ── 3. GPU Detection ──
echo "==> [3/6] Hardware Detection ..."

OS_NAME=$(uname -s | tr '[:upper:]' '[:lower:]')
ARCH_NAME=$(uname -m | tr '[:upper:]' '[:lower:]')

GPU_TYPE="cpu"
if [ "$OS_NAME" = "darwin" ]; then
    if [ "$ARCH_NAME" = "arm64" ]; then
        echo "[OK] macOS Apple Silicon (arm64) detected."
        GPU_TYPE="mac-arm"
    else
        echo "[OK] macOS Intel (x86_64) detected."
        GPU_TYPE="cpu"
    fi
else
    # Linux
    if _has_usable_nvidia_gpu; then
        echo "[OK] NVIDIA GPU detected -> CUDA"
        GPU_TYPE="cuda"
    elif _has_amd_rocm_gpu; then
        echo "[OK] AMD GPU detected -> ROCm/HIP"
        GPU_TYPE="hip"
    else
        echo "[OK] No supported dedicated GPU found -> CPU"
        GPU_TYPE="cpu"
    fi
fi

# ── Auto-select model size based on hardware ──
if [ -n "$USER_MODEL_OVERRIDE" ]; then
    BONSAI_MODEL="$USER_MODEL_OVERRIDE"
    echo "[INFO] Using user-specified model: Bonsai-$BONSAI_MODEL"
elif [ "$GPU_TYPE" = "cpu" ]; then
    BONSAI_MODEL="4B"
    echo "[INFO] CPU mode -> downloading lighter Bonsai-4B model (faster on CPU)"
else
    BONSAI_MODEL="8B"
    echo "[INFO] GPU mode -> downloading full Bonsai-8B model"
fi

if [ "$BONSAI_MODEL" = "8B" ]; then
    MODEL_URL="https://huggingface.co/prism-ml/Ternary-Bonsai-8B-gguf/resolve/main/Ternary-Bonsai-8B-Q2_0.gguf"
    MODEL_FILE="Ternary-Bonsai-8B-Q2_0.gguf"
elif [ "$BONSAI_MODEL" = "4B" ]; then
    MODEL_URL="https://huggingface.co/prism-ml/Bonsai-4B-gguf/resolve/main/Bonsai-4B.gguf"
    MODEL_FILE="Bonsai-4B.gguf"
else
    echo "[ERR] Unsupported BONSAI_MODEL '$BONSAI_MODEL'. Supported values: 8B, 4B"
    exit 1
fi

# ── 4. Download llama-server binaries ──
echo "==> [4/6] Downloading llama-server binaries ..."

BIN_DIR="$SCRIPT_DIR/bin/$GPU_TYPE"
VERSION_FILE="$BIN_DIR/.llama_version"
NEEDS_UPDATE=true

FOUND_BIN=$(find "$BIN_DIR" -name "llama-server" -type f 2>/dev/null | head -n 1)
if [ -n "$FOUND_BIN" ] && [ -x "$FOUND_BIN" ] && [ -f "$VERSION_FILE" ]; then
    if [ "$(cat "$VERSION_FILE" | xargs)" = "$RELEASE_TAG" ]; then
        NEEDS_UPDATE=false
    fi
fi

if [ "$NEEDS_UPDATE" = "false" ]; then
    echo "[OK] Binaries ($RELEASE_TAG) already present in $BIN_DIR"
else
    echo "    Downloading binaries to $RELEASE_TAG ..."
    rm -rf "$BIN_DIR"
    mkdir -p "$BIN_DIR"

    ASSET_NAME=""
    if [ "$OS_NAME" = "darwin" ]; then
        if [ "$ARCH_NAME" = "arm64" ]; then
            ASSET_NAME="llama-$RELEASE_TAG-bin-macos-arm64.tar.gz"
        else
            ASSET_NAME="llama-$RELEASE_TAG-bin-macos-x64.tar.gz"
        fi
    else
        # Linux
        if [ "$GPU_TYPE" = "cuda" ]; then
            ASSET_NAME="llama-$RELEASE_TAG-bin-linux-cuda-12.4-x64.tar.gz"
        elif [ "$GPU_TYPE" = "hip" ]; then
            ASSET_NAME="llama-$RELEASE_TAG-bin-ubuntu-rocm-7.2-x64.tar.gz"
        else
            # CPU
            if [ "$ARCH_NAME" = "aarch64" ] || [ "$ARCH_NAME" = "arm64" ]; then
                ASSET_NAME="llama-$RELEASE_TAG-bin-ubuntu-arm64.tar.gz"
            else
                ASSET_NAME="llama-$RELEASE_TAG-bin-ubuntu-x64.tar.gz"
            fi
        fi
    fi

    TARBALL_URL="$BASE_URL/$ASSET_NAME"
    TARBALL_PATH="$SCRIPT_DIR/$ASSET_NAME"

    echo "    Fetching $TARBALL_URL ..."
    if command -v curl >/dev/null 2>&1; then
        curl -L -o "$TARBALL_PATH" "$TARBALL_URL"
    else
        wget -O "$TARBALL_PATH" "$TARBALL_URL"
    fi

    echo "    Extracting ..."
    tar -xzf "$TARBALL_PATH" -C "$BIN_DIR"
    rm -f "$TARBALL_PATH"
    
    echo "$RELEASE_TAG" > "$VERSION_FILE"
    echo "[OK] Binaries updated."
fi

# ── 5. Download Model ──
echo "==> [5/6] Downloading model $BONSAI_MODEL ..."
MODEL_DIR="$SCRIPT_DIR/models/gguf/$BONSAI_MODEL"
MODEL_PATH="$MODEL_DIR/$MODEL_FILE"

mkdir -p "$MODEL_DIR"
if [ -f "$MODEL_PATH" ]; then
    echo "[OK] Model $MODEL_FILE already present in $MODEL_DIR"
else
    echo "    Downloading model (this may take a while) ..."
    if command -v curl >/dev/null 2>&1; then
        curl -L -o "$MODEL_PATH" "$MODEL_URL"
    else
        wget -O "$MODEL_PATH" "$MODEL_URL"
    fi
    echo "[OK] Model downloaded."
fi

# ── 6. Write configs for start.sh ──
echo "==> [6/6] Finalizing setup ..."
echo "$GPU_TYPE" > "$SCRIPT_DIR/.gpu_type"
echo "$BONSAI_MODEL" > "$SCRIPT_DIR/.model_size"

echo "==========================================="
echo "[SUCCESS] AiMentor is ready to launch."
echo "To start the app, run:"
echo "    ./start.sh"
echo "==========================================="
