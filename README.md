# AiMentor

A fully offline AI teaching assistant. One-command setup — no pre-installed tools required.

## Quick Start (Windows)

```powershell
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/AiMentor.git
cd AiMentor

# 2. Run setup (downloads everything automatically)
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\setup.ps1

# 3. Launch
.\start.bat
```

That's it. Setup auto-detects your hardware (NVIDIA/AMD/CPU), downloads the correct `llama-server` binary, downloads the Bonsai model from HuggingFace, and installs Python + Streamlit.

## What `setup.ps1` Does

| Step | What happens |
|------|-------------|
| 1 | Finds Python 3.11+ or installs it via `winget` |
| 2 | Creates a virtual environment, installs Streamlit + Requests |
| 3 | Auto-detects GPU: NVIDIA CUDA, AMD HIP/ROCm, Vulkan, or CPU |
| 4 | Downloads the correct pre-built `llama-server.exe` from [PrismML releases](https://github.com/PrismML-Eng/llama.cpp/releases) |
| 5 | Downloads the Bonsai GGUF model from HuggingFace |

### Choosing a Model Size

By default, setup downloads the **8B** model. To use a smaller model (faster, less RAM):

```powershell
$env:BONSAI_MODEL = "4B"    # Options: 8B (default), 4B, 1.7B
.\setup.ps1
```

## Features

- **Dual Mode**: Structured course generation with syllabus + sections, or free-form chat
- **Fully Offline**: Everything runs locally — no API keys, no cloud, no internet needed after setup
- **Auto Hardware Detection**: Automatically uses GPU acceleration if available, falls back to CPU
- **Checkpoint System**: Save and resume learning progress across sessions
- **Opinionated Mentor**: The AI has genuine opinions and a distinct teaching style

## Requirements

- **Windows 10/11** (macOS/Linux support coming later)
- **Internet** for first-time setup only (downloads ~2-5 GB depending on model)
- **RAM**: 4GB+ for 4B model, 8GB+ for 8B model
- **GPU** (optional): NVIDIA (CUDA), AMD (ROCm/HIP), or Vulkan — CPU works too, just slower

## File Structure

```
AiMentor/
├── setup.ps1          ← One-command setup (run this first)
├── start.bat          ← Smart launcher (run this to use)
├── app.py             ← Main application
├── requirements.txt   ← Python dependencies
├── bin/               ← Downloaded llama-server binaries (created by setup)
├── models/            ← Downloaded GGUF models (created by setup)
└── llm_workspace/     ← Saved checkpoints and progress
```
