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
- Any compatible GPU is acceptable for GPU mode
- Internet access only during the first setup step

## Installation

1. Clone or download this repository.
2. Run `setup.bat`.

During setup, select the option that matches your hardware:

- `CPU` mode uses a smaller model and lower context size so it can run on CPU systems.
- `NVIDIA` and `AMD` modes use larger models and higher thread/context settings for GPU systems.

The setup script downloads and prepares:

- a Python virtual environment in `venv`
- Python package dependencies from `requirements.txt`
- the appropriate native `llama-server` binaries
- the Bonsai GGUF model for the selected mode

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

- After cloning or downloading the repository, just run `setup.bat` and then `start.bat`.
- CPU mode requires at least 8 GB of RAM and downloads about 1.5 GB of model data.
- GPU mode is optimized to work on any compatible GPU and downloads about 2.5 GB of model data.
- Setup takes approximately 20–25 minutes for CPU mode and 30–35 minutes for GPU mode.
- The CPU mode uses a smaller model and smaller context size so the model can run on CPU hardware.
- The NVIDIA and AMD modes use larger models and higher thread/context settings for GPU systems.
- If Python is not already installed, the setup script installs Python 3.11 automatically.

## License

This repository is licensed under GPLv3.
