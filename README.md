# AiMentor

AiMentor is a local AI teacher for Windows, not a general-purpose assistant.

The project is built around a simple constraint: when you ask an LLM to teach a topic in a long conversation, it often starts strong, then drifts, hallucinates, or loses the structure of the subject. AiMentor reduces that drift by forcing the model to create a syllabus first, then teach section by section along that path.

It also includes a separate Free Chat mode for open-ended conversation when structure is not the goal.

## Why this exists

Most AI chat tools are reactive. They answer the latest message well enough, but over time they can:

- drift away from the original learning objective
- skip foundations and jump into disconnected details
- lose a coherent teaching sequence
- behave more like a chat assistant than an actual tutor

AiMentor is designed to behave more like a teacher. Before teaching begins, it generates a learning roadmap for the chosen topic. The student can review or edit that roadmap, and only then does the model start teaching.

## Core idea

The structured course flow is:

1. Enter a topic.
2. Choose an expertise level.
3. Let the model generate a syllabus first.
4. Review or edit the syllabus.
5. Learn one section at a time.
6. Ask doubts within the current section.
7. Move to the next section only after finishing the current one.

This keeps the session anchored to the original topic and gives the model a fixed path to follow instead of letting the conversation sprawl indefinitely.

## Features

- Syllabus-first learning flow
- Topic-specific roadmap generation in Markdown
- Editable syllabus before teaching starts
- Section-by-section teaching with progress tracking
- Resume support for saved structured-course sessions
- Separate Free Chat mode for unstructured conversations
- Runs locally on your machine with a local `llama-server` backend
- No external AI API calls during normal use after setup

## Modes

### 1. Structured Course

This is the main product experience.

For a given topic, AiMentor:

- generates a syllabus first
- asks you to review it before teaching
- teaches the current section in depth
- lets you ask follow-up doubts for that section
- advances through the syllabus in order
- saves progress so you can resume later

This mode is intended for actual learning, where sequence matters.

### 2. Free Chat

Free Chat is intentionally separate from the teaching flow.

Use it when you want:

- casual conversation
- brainstorming
- quick questions
- open-ended discussion not tied to a fixed syllabus

This keeps the structured teaching experience clean instead of mixing it with general assistant behavior.

## How AiMentor teaches

AiMentor does not immediately start explaining the topic. It first creates a roadmap, then uses that roadmap as the teaching contract for the rest of the session.

That means:

- the topic stays anchored
- the model has a defined sequence to follow
- the student can inspect the plan before learning begins
- long sessions remain more coherent than normal chat-based tutoring

In short, the model is constrained to teach, not just respond.

## Requirements

- Windows 10 or Windows 11
- Internet access during first-time setup

AiMentor is designed to run efficiently on a wide range of hardware, including lower-end GPUs. During setup, you choose the runtime profile that matches your system so the local model and launch settings are configured appropriately.

## Installation

On first run, clone or download this repository and run `setup.bat`.

This first-run setup is important because it lets you choose the hardware mode that matches your machine:

- `CPU` for lower-resource systems
- `NVIDIA` for NVIDIA GPUs
- `AMD` for AMD GPUs

AiMentor is tuned to work efficiently and quickly even on lower-end GPUs, so choosing the correct mode during setup helps the app use the right model, runtime settings, and binaries for the best experience.

The setup process prepares:

- a Python virtual environment
- Python dependencies
- local `llama-server` binaries
- the required GGUF model files

## Run the app

After setup is complete, use `start.bat` to launch AiMentor.

This will:

- start the local model server
- launch the Streamlit app
- open the interface at `http://localhost:8501`

To stop the local processes, use `stop.bat`.

## Project structure

- `README.md` - project overview and usage
- `setup.bat` - setup entry point
- `start.bat` - app launcher
- `stop.bat` - stops background processes
- `AiMentor_Core_DO_NOT_DELETE/app.py` - Streamlit application and teaching flow
- `AiMentor_Core_DO_NOT_DELETE/download.ps1` - installation and model download logic
- `AiMentor_Core_DO_NOT_DELETE/help.ps1` - local startup orchestration
- `AiMentor_Core_DO_NOT_DELETE/requirements.txt` - Python dependencies

## Current behavior

The current implementation includes:

- expertise-level selection before syllabus generation
- syllabus review and syllabus editing
- section progress tracking
- saved structured-course checkpoints
- saved Free Chat history
- fully local runtime after installation

## Positioning

AiMentor should be described as:

- an AI teacher
- a syllabus-driven tutor
- a structured learning interface for local LLMs

It should not be described as:

- a generic chatbot
- a general assistant
- an open-ended tutoring chat without structure

## License

This repository is licensed under GPLv3.
