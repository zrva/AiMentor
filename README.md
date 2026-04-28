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
- At least 2 GB RAM for CPU mode
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

During setup, you will be prompted to select CPU or GPU mode. The script also downloads the following:

- a compatible Python runtime or uses an existing one
- a virtual environment in `venv`
- the `streamlit` and `requests` packages
- native `llama-server` binaries for your platform
- a Bonsai GGUF model (`4B` for CPU or `8B` for GPU by default)

## Launching the app

Run the launcher:

```powershell
.\start.bat
```

This starts the local model server, launches Streamlit in the background, and opens the app at `http://localhost:8501`.

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

- The application workflow is designed for Windows and uses native binaries from `download.ps1`.
- GPU mode offers better performance; CPU mode is supported but slower.
- If Python is not already installed, the setup uses `winget` to install Python 3.11.

## License

This repository is licensed under GPLv3.
