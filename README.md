# AiMentor

A fully offline AI teaching assistant for Windows.

## Quick Start (Windows)

1. Clone or download the repo.
2. Run `setup.bat`.
3. Run `start.bat`.

That installs Python dependencies, downloads the selected `llama-server` build, downloads the Bonsai model, and launches the app locally.

If you prefer PowerShell directly:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\download.ps1
```

## What `download.ps1` Does

| Step | What happens |
|------|-------------|
| 1 | Finds Python 3.11+ or installs it via `winget` |
| 2 | Creates a virtual environment and installs dependencies from `requirements.txt` |
| 3 | Asks whether to use NVIDIA, AMD, or CPU mode |
| 4 | Downloads the matching `llama-server.exe` build from [PrismML releases](https://github.com/PrismML-Eng/llama.cpp/releases) |
| 5 | Downloads the Bonsai GGUF model from HuggingFace |

### Choosing a Model Size

Setup chooses a default model automatically:

- GPU mode: `8B`
- CPU mode: `4B`

You can override it manually before running setup:

```powershell
$env:BONSAI_MODEL = "4B"    # Supported: 8B, 4B
.\download.ps1
```

## Features

- **Dual Mode**: Structured course generation with syllabus + sections, or free-form chat
- **Fully Offline**: Everything runs locally after setup completes
- **Windows Setup Flow**: One setup script handles Python env, server binary, and model download
- **Checkpoint System**: Save and resume learning progress across sessions
- **Opinionated Mentor**: The AI has genuine opinions and a distinct teaching style

## Requirements

- **Windows 10/11** (macOS/Linux support coming later)
- **Internet** for first-time setup only

### Setup Time & Download Sizes
**GPU Setup (NVIDIA/AMD):**
- **Time:** 30-40 minutes
- **Download:** ~2.5-3 GB
- **Model:** Bonsai-8B (larger, higher quality)

**CPU Setup:**
- **Time:** 15-20 minutes  
- **Download:** ~1-1.5 GB
- **Model:** Bonsai-4B (smaller, optimized for CPU)

**Performance Comparison:**
- **CPU:** Extremely slow response times
  - Context Window: 2,048 tokens (server limit)
  - Max Output: ~1,024 tokens (application limit)
- **GPU:** Near-instant responses
  - Context Window: 4,096 tokens (server limit)
  - Max Output: ~6,500 tokens (application limit)

| Context Size | Est. Memory Usage |
|-------------|-----------------|
| 2,048 tokens (CPU context window) | ~1.5-2 GB |
| 4,096 tokens (GPU context window) | ~2.5-3.5 GB |

- **GPU** (optional): NVIDIA (CUDA), AMD (ROCm/HIP), or Vulkan — CPU works too, but is significantly slower

## File Structure

```
AiMentor/
├── setup.bat          ← Windows setup entry point
├── download.ps1       ← Downloads model + AI server
├── start.bat          ← Launcher
├── app.py             ← Main application
├── requirements.txt   ← Python dependencies
├── bin/               ← Downloaded llama-server binaries
├── models/            ← Downloaded GGUF models
├── assets/            ← Screenshots and media
│   └── screenshots/   ← UI screenshots
└── llm_workspace/     ← Saved checkpoints and progress
```

## Screenshots

![Course Generation - Syllabus Section](assets/screenshots/syllabus_section.png)
![Course Generation - Section 1](assets/screenshots/section_1.png)
![Course Generation - Generate Syllabus](assets/screenshots/generates_syllabus.png)
![Chat Interface](assets/screenshots/freechat.png)
![Chat Interface with Question](assets/screenshots/freechat_question.png)

*Add additional screenshots to the `assets/screenshots` directory and reference them above.*
