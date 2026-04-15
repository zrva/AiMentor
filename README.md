# Local LLM Chat Interface

A ChatGPT/Claude-style chat interface using local inference with llama.cpp.

## Requirements

- **Hardware**: RTX 3050 (4GB VRAM), 8GB RAM
- **Model**: Qwen3.5-4B.Q4_K_M.gguf (quantized for efficiency)

## Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Ensure model is in place**:
   The model should be at: `C:\Users\SAMAY\Desktop\llms\Qwen3.5-4B.Q4_K_M.gguf`

3. **Run the application**:
   ```bash
   streamlit run app.py
   ```

## Features

- **GPU Acceleration**: Uses CUDA via llama-cpp-python with cublas
- **Adjustable Parameters**:
  - Temperature (creativity vs determinism)
  - Max tokens (response length)
  - Top P (nucleus sampling)
- **Chat History**: Persists within session
- **Modern UI**: Clean, responsive interface

## Tips for RTX 3050

- `n_gpu_layers=35` is set for optimal VRAM usage
- Q4_K_M quantization balances quality and memory
- 4GB VRAM is sufficient for this model configuration
