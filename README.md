# AiMentor

AiMentor is a local teaching assistant for Windows that pairs a Streamlit interface with a local LLM backend. It runs entirely on your machine after setup and does not require external AI service calls during normal use.

## Overview

- `app.py` runs the Streamlit user interface.
- `help.ps1` and `start.bat` launch the local `llama-server` process and open the web interface.
- `download.ps1` installs Python, dependencies, model weights, and native binaries.
- `requirements.txt` declares the Python dependencies used by the app.

## Requirements

- Windows 10 or Windows 11
- Python 3.11 or newer (setup installs it if missing)
- At least 8 GB RAM for CPU mode
- Dedicated GPU recommended for faster performance
- Internet access only during the first setup step

## Installation

1. Clone the repository.
2. Open PowerShell.
3. Run the setup file:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\setup.bat
```

During setup, you will be prompted to select one of the supported modes: CPU, NVIDIA, or AMD. Choose the option that matches your system, because the NVIDIA and AMD modes download a larger model and use higher thread/context settings that are not suitable for a normal CPU.

The setup script downloads:

- a compatible Python runtime or uses an existing installation
- a virtual environment in `venv`
- the `streamlit` and `requests` packages
- native `llama-server` binaries for the selected runtime
- the appropriate Bonsai GGUF model and supporting files

## Launching the app

Run the launcher:

```powershell
.\start.bat
```

This starts the local model server, launches Streamlit in the background, and opens the app at `http://localhost:8501`.

To stop the background model server, run:

```powershell
.\stop.bat
```

## Directory structure

- `app.py` — Streamlit interface
- `download.ps1` — setup and download logic
- `start.bat` — launcher for the app
- `setup.bat` — wrapper to invoke the setup script
- `help.ps1` — background startup for the model server and Streamlit
- `requirements.txt` — Python package requirements
- `bin/` — downloaded `llama-server` binaries
- `models/` — downloaded GGUF model weights
- `assets/screenshots/` — interface screenshots

## Configuration

- The setup script respects the `BONSAI_MODEL` environment variable if set before installation.
- Runtime settings are stored in `.gpu_type` and `.model_size` so `start.bat` can use the correct binary and model file.

## Dependencies

- `streamlit>=1.28.0`
- `requests>=2.31.0`

## Notes

- After cloning or downloading the repository, run `setup.bat` to install dependencies and download the correct model and binaries.
- The CPU mode uses a smaller model and smaller context size so the model can run on CPU hardware.
- The NVIDIA and AMD modes use larger models and higher thread/context settings; do not select these options unless you have a compatible GPU.
- If Python is not already installed, the setup uses `winget` to install Python 3.11.

## License

This repository is licensed under GPLv3.
