"""Local LLM Professor Teaching Interface"""

import streamlit as st
import os
import re
import time
import glob
import requests
import json
import html

st.set_page_config(page_title="AiMentor", page_icon="📚", layout="wide")

# ── Premium Design System ──────────────────────────────────────────────────────
CUSTOM_CSS = """
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,500;0,600;0,700;1,400&family=Source+Sans+3:wght@300;400;500;600&display=swap" rel="stylesheet">
<style>

/* ═══════════════════════════════════════════
   DESIGN TOKENS — Navy × Gold palette
   (mirrors the reference React app's CSS vars)
═══════════════════════════════════════════ */
:root {
  --bg-deep:       #090f1e;
  --bg-main:       #0d1526;
  --bg-card:       #121f38;
  --bg-card-hover: #162540;
  --border:        #1f3655;
  --border-glow:   rgba(201,162,39,0.35);
  --gold:          #c9a227;
  --gold-light:    #d4af37;
  --gold-dim:      rgba(201,162,39,0.15);
  --cream:         #e8d5b7;
  --cream-muted:   #b5a080;
  --muted:         #6b7b8c;
  --text-body:     #c9b896;
  --radius-sm:     6px;
  --radius-md:     10px;
  --radius-lg:     16px;
  --shadow-card:   0 4px 24px rgba(0,0,0,0.45);
  --shadow-glow:   0 0 20px rgba(201,162,39,0.18);
}

/* ─── BASE ─────────────────────────────────── */
[data-testid="stAppViewContainer"] {
  background: var(--bg-deep) !important;
  background-image:
    radial-gradient(ellipse at 20% 10%, rgba(201,162,39,0.04) 0%, transparent 55%),
    radial-gradient(ellipse at 80% 80%, rgba(30,58,95,0.35) 0%, transparent 60%);
  background-attachment: fixed;
}

[data-testid="stHeader"] {
  background: rgba(13,21,38,0.92) !important;
  backdrop-filter: blur(12px) !important;
  border-bottom: 1px solid var(--border) !important;
}

.block-container {
  padding-top: 2rem !important;
  padding-bottom: 3rem !important;
  max-width: 920px !important;
}

/* hide deploy button & footer — keep sidebar toggle visible */
#MainMenu, footer, .stAppDeployButton { display: none !important; }

/* ─── TYPOGRAPHY ───────────────────────────── */
*, *::before, *::after {
  font-family: 'Source Sans 3', sans-serif;
}

h1, h2, h3, h4, h5, h6,
[class*="heading"] {
  font-family: 'Playfair Display', Georgia, serif !important;
  color: var(--cream) !important;
  letter-spacing: -0.01em;
}

p, li, span, label, div {
  color: var(--text-body) !important;
}

a { color: var(--gold) !important; }

/* ─── SIDEBAR ──────────────────────────────── */
[data-testid="stSidebar"] {
  background: var(--bg-main) !important;
  border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] > div {
  padding-top: 1.25rem !important;
}

/* Sidebar collapse toggle icon */
[data-testid="collapsedControl"] svg,
[data-testid="stSidebar"] button svg {
  color: var(--cream-muted) !important;
  fill: var(--cream-muted) !important;
}

/* ─── BUTTONS ──────────────────────────────── */
[data-testid="stButton"] button {
  background: linear-gradient(135deg, var(--gold) 0%, #a07c18 100%) !important;
  border: none !important;
  color: #0a1020 !important;
  border-radius: var(--radius-md) !important;
  font-weight: 600 !important;
  font-family: 'Source Sans 3', sans-serif !important;
  font-size: 14px !important;
  letter-spacing: 0.02em !important;
  transition: all 0.22s cubic-bezier(0.4,0,0.2,1) !important;
  box-shadow: 0 2px 8px rgba(201,162,39,0.20) !important;
}
[data-testid="stButton"] button:hover {
  background: linear-gradient(135deg, var(--gold-light) 0%, var(--gold) 100%) !important;
  box-shadow: 0 6px 20px rgba(201,162,39,0.40) !important;
  transform: translateY(-1px) !important;
}
[data-testid="stButton"] button:active {
  transform: translateY(0) !important;
}
[data-testid="stButton"] button:focus-visible {
  outline: 2px solid var(--gold) !important;
  outline-offset: 3px !important;
}

/* ─── FORMS & TEXT INPUTS ──────────────────── */
[data-testid="stForm"] {
  background: var(--bg-card) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius-lg) !important;
  padding: 28px !important;
  box-shadow: var(--shadow-card) !important;
}

[data-testid="stTextInput"] > div {
  background: var(--bg-main) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius-md) !important;
  transition: border-color 0.2s, box-shadow 0.2s !important;
}
[data-testid="stTextInput"] > div:focus-within {
  border-color: var(--gold) !important;
  box-shadow: 0 0 0 3px var(--gold-dim) !important;
}
[data-testid="stTextInput"] input {
  background: transparent !important;
  color: var(--cream) !important;
  font-family: 'Source Sans 3', sans-serif !important;
  font-size: 15px !important;
}
[data-testid="stTextInput"] input::placeholder { color: var(--muted) !important; }

/* ─── CHAT INPUT ───────────────────────────── */
[data-testid="stChatInput"] {
  background: rgba(18,31,56,0.95) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius-lg) !important;
  backdrop-filter: blur(8px) !important;
  box-shadow: 0 -4px 30px rgba(0,0,0,0.35) !important;
  transition: border-color 0.2s, box-shadow 0.2s !important;
}
[data-testid="stChatInput"]:focus-within {
  border-color: var(--gold) !important;
  box-shadow: 0 -4px 30px rgba(0,0,0,0.3), 0 0 0 2px var(--gold-dim) !important;
}
[data-testid="stChatInput"] textarea {
  color: var(--cream) !important;
  font-family: 'Source Sans 3', sans-serif !important;
  font-size: 15px !important;
  background: transparent !important;
}
[data-testid="stChatInput"] textarea::placeholder { color: var(--muted) !important; }
[data-testid="stChatInput"] button {
  background: linear-gradient(135deg, var(--gold), #a07c18) !important;
  border-radius: var(--radius-sm) !important;
  transition: all 0.2s !important;
}
[data-testid="stChatInput"] button:hover {
  background: linear-gradient(135deg, var(--gold-light), var(--gold)) !important;
  box-shadow: 0 2px 12px rgba(201,162,39,0.35) !important;
}

/* ─── CHAT MESSAGES ────────────────────────── */
[data-testid="stChatMessage"] {
  background: var(--bg-card) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius-lg) !important;
  margin: 8px 0 !important;
  box-shadow: 0 2px 12px rgba(0,0,0,0.25) !important;
  transition: box-shadow 0.2s !important;
}
/* Fix the internal content column so text stays left-aligned and wraps properly */
[data-testid="stChatMessage"] > div {
  min-width: 0 !important;
  width: 100% !important;
}
[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] {
  font-family: 'Source Sans 3', sans-serif !important;
  font-size: 15px !important;
  line-height: 1.65 !important;
  color: var(--cream) !important;
  word-wrap: break-word !important;
  overflow-wrap: break-word !important;
  max-width: 100% !important;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
  background: rgba(201,162,39,0.08) !important;
  border-color: rgba(201,162,39,0.22) !important;
}

/* ─── PROGRESS BAR ─────────────────────────── */
[data-testid="stProgress"] > div {
  background: rgba(31,54,85,0.7) !important;
  border-radius: 99px !important;
}
[data-testid="stProgress"] > div > div {
  background: linear-gradient(90deg, var(--gold), var(--gold-light)) !important;
  border-radius: 99px !important;
  box-shadow: 0 0 8px rgba(201,162,39,0.5) !important;
}

/* ─── RADIO BUTTONS ────────────────────────── */
[data-testid="stRadio"] label {
  color: var(--text-body) !important;
  border-radius: var(--radius-md) !important;
  transition: background 0.15s !important;
}
[data-testid="stRadio"] label:hover {
  background: rgba(201,162,39,0.07) !important;
}
[data-testid="stRadio"] label:has(input:checked) {
  background: rgba(201,162,39,0.18) !important;
  color: var(--cream) !important;
}

/* ─── DETAILS / THINKING BLOCK ─────────────── */
details {
  background: rgba(18,31,56,0.8) !important;
  border: 1px solid var(--border) !important;
  border-left: 3px solid var(--gold) !important;
  border-radius: var(--radius-md) !important;
  padding: 12px 16px !important;
  margin: 8px 0 !important;
}
details > summary {
  color: var(--gold) !important;
  font-family: 'Source Sans 3', sans-serif !important;
  font-weight: 600 !important;
  font-size: 13px !important;
  letter-spacing: 0.05em !important;
  text-transform: uppercase !important;
  cursor: pointer !important;
  user-select: none !important;
}
details[open] > summary { margin-bottom: 10px; }
details pre {
  background: var(--bg-deep) !important;
  border: none !important;
  border-radius: var(--radius-sm) !important;
  color: var(--muted) !important;
  font-size: 12px !important;
  padding: 10px !important;
  overflow-x: auto !important;
}

/* ─── CODE BLOCKS ──────────────────────────── */
.stCodeBlock > div {
  background: var(--bg-deep) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius-md) !important;
}

/* ─── DIVIDER ──────────────────────────────── */
[data-testid="stDivider"] hr {
  border-color: var(--border) !important;
}

/* ─── TOAST ────────────────────────────────── */
[data-testid="stToast"] {
  background: var(--bg-card) !important;
  border-left: 4px solid var(--gold) !important;
  border-radius: var(--radius-md) !important;
  color: var(--cream) !important;
  box-shadow: var(--shadow-card) !important;
}

/* ─── SCROLLBAR ────────────────────────────── */
* { scrollbar-width: thin; scrollbar-color: #2a4060 var(--bg-deep); }
*::-webkit-scrollbar { width: 6px; height: 6px; }
*::-webkit-scrollbar-track { background: var(--bg-deep); }
*::-webkit-scrollbar-thumb { background: #2a4060; border-radius: 3px; }
*::-webkit-scrollbar-thumb:hover { background: var(--gold); }

/* ─── INFO / WARNING / SUCCESS BOXES ───────── */
[data-testid="stAlert"] {
  background: var(--bg-card) !important;
  border-radius: var(--radius-md) !important;
  border: 1px solid var(--border) !important;
}

/* ─── SELECT BOX / DROPDOWN ────────────────── */
[data-testid="stSelectbox"] > div {
  background: var(--bg-main) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius-md) !important;
  color: var(--cream) !important;
}

/* ─── CAPTION / SMALL TEXT ─────────────────── */
[data-testid="stCaptionContainer"] p {
  color: var(--muted) !important;
  font-size: 12px !important;
}

/* ─── CUSTOM COMPONENT CLASSES ─────────────── */

/* Hero header */
.mentor-hero {
  text-align: center;
  padding: 3rem 1rem 2rem;
  position: relative;
}
.mentor-hero .hero-icon {
  font-size: 52px;
  line-height: 1;
  filter: drop-shadow(0 0 20px rgba(201,162,39,0.5));
  animation: float 3s ease-in-out infinite;
}
@keyframes float {
  0%, 100% { transform: translateY(0px); }
  50%       { transform: translateY(-6px); }
}
.mentor-hero h1 {
  font-family: 'Playfair Display', Georgia, serif !important;
  font-size: 2.6rem !important;
  font-weight: 700 !important;
  background: linear-gradient(135deg, var(--gold-light), var(--gold)) !important;
  -webkit-background-clip: text !important;
  -webkit-text-fill-color: transparent !important;
  background-clip: text !important;
  margin: 0.5rem 0 !important;
  letter-spacing: -0.02em !important;
}
.mentor-hero p {
  color: var(--cream-muted) !important;
  font-size: 1.05rem !important;
  font-family: 'Source Sans 3', sans-serif !important;
  margin-top: 0.4rem !important;
}

/* Section badge (phase header) */
.phase-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 20px;
  background: linear-gradient(135deg, rgba(201,162,39,0.10), rgba(201,162,39,0.04));
  border: 1px solid rgba(201,162,39,0.25);
  border-radius: var(--radius-lg);
  margin-bottom: 1.5rem;
}
.phase-header .phase-icon {
  font-size: 22px;
  flex-shrink: 0;
}
.phase-header h3 {
  margin: 0 !important;
  font-family: 'Playfair Display', serif !important;
  font-size: 1.25rem !important;
  color: var(--cream) !important;
}
.phase-header p {
  margin: 2px 0 0 !important;
  font-size: 13px !important;
  color: var(--muted) !important;
}

/* Resume topic card */
.topic-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 18px 20px;
  transition: all 0.22s cubic-bezier(0.4,0,0.2,1);
  cursor: pointer;
  position: relative;
  overflow: hidden;
}
.topic-card::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, var(--gold), transparent);
  opacity: 0;
  transition: opacity 0.22s;
}
.topic-card:hover::before { opacity: 1; }
.topic-card:hover {
  border-color: rgba(201,162,39,0.4);
  box-shadow: 0 8px 32px rgba(0,0,0,0.4), var(--shadow-glow);
  transform: translateY(-2px);
}
.topic-card h4 {
  font-family: 'Playfair Display', serif;
  font-size: 1rem;
  color: var(--cream) !important;
  margin: 0 0 6px !important;
}
.topic-card .meta {
  font-size: 12px;
  color: var(--muted);
  font-family: 'Source Sans 3', sans-serif;
}
.topic-card .progress-track {
  height: 3px;
  background: var(--border);
  border-radius: 99px;
  margin-top: 10px;
  overflow: hidden;
}
.topic-card .progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--gold), var(--gold-light));
  border-radius: 99px;
  box-shadow: 0 0 6px rgba(201,162,39,0.6);
}

/* Mode selector cards */
.mode-pill {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 5px 14px;
  border-radius: 99px;
  border: 1px solid var(--border);
  font-size: 13px;
  font-weight: 500;
  color: var(--muted);
  background: transparent;
  cursor: pointer;
  transition: all 0.2s;
}
.mode-pill.active {
  background: var(--gold-dim);
  border-color: rgba(201,162,39,0.4);
  color: var(--gold);
}

/* Sidebar section item */
.sb-section {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 8px 12px;
  border-radius: var(--radius-md);
  margin: 2px 0;
  transition: background 0.15s;
  font-family: 'Source Sans 3', sans-serif;
  font-size: 13.5px;
  line-height: 1.4;
  cursor: default;
}
.sb-section .dot {
  width: 8px; height: 8px;
  border-radius: 50%;
  margin-top: 4px;
  flex-shrink: 0;
}
.sb-section.completed .dot { background: var(--gold); }
.sb-section.current   .dot { background: #4ade80; box-shadow: 0 0 8px rgba(74,222,128,0.6); }
.sb-section.locked    .dot { background: var(--border); }
.sb-section.completed { color: var(--cream-muted) !important; }
.sb-section.current   { color: var(--cream) !important; background: rgba(201,162,39,0.06); }
.sb-section.locked    { color: var(--muted) !important; }

/* Sidebar label */
.sb-label {
  font-family: 'Source Sans 3', sans-serif;
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: var(--muted);
  padding: 4px 12px;
  margin-top: 12px;
  margin-bottom: 4px;
}

/* Teaching progress bar (inline) */
.teach-progress {
  background: rgba(31,54,85,0.5);
  border-radius: 99px;
  height: 4px;
  overflow: hidden;
  margin: 6px 0 14px;
}
.teach-progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--gold), var(--gold-light));
  border-radius: 99px;
  transition: width 0.6s ease;
}

/* Free chat mode header */
.chat-hero {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px 24px;
  background: linear-gradient(135deg, rgba(18,31,56,0.9), rgba(13,21,38,0.7));
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  margin-bottom: 24px;
  box-shadow: var(--shadow-card);
}
.chat-hero .icon { font-size: 36px; }
.chat-hero h3 {
  margin: 0 !important;
  font-family: 'Playfair Display', serif !important;
  font-size: 1.3rem !important;
  color: var(--cream) !important;
}
.chat-hero p {
  margin: 3px 0 0 !important;
  font-size: 13px !important;
  color: var(--muted) !important;
}
.online-dot {
  display: inline-block;
  width: 7px; height: 7px;
  border-radius: 50%;
  background: #4ade80;
  box-shadow: 0 0 6px rgba(74,222,128,0.7);
  margin-right: 5px;
  vertical-align: middle;
  animation: pulse-dot 2s ease-in-out infinite;
}
@keyframes pulse-dot {
  0%, 100% { opacity: 1; transform: scale(1); }
  50%       { opacity: 0.6; transform: scale(0.8); }
}

/* Section teaching header */
.teach-header {
  padding: 20px 24px;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  margin-bottom: 20px;
  box-shadow: var(--shadow-card);
}
.teach-header .section-label {
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.14em;
  color: var(--gold);
  font-weight: 600;
  margin-bottom: 4px;
}
.teach-header h2 {
  margin: 0 !important;
  font-family: 'Playfair Display', serif !important;
  color: var(--cream) !important;
  font-size: 1.5rem !important;
}

/* Doubt counter badge */
.doubt-badge {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 3px 10px;
  background: rgba(201,162,39,0.12);
  border: 1px solid rgba(201,162,39,0.25);
  border-radius: 99px;
  font-size: 12px;
  color: var(--gold);
  font-family: 'Source Sans 3', sans-serif;
  margin-bottom: 8px;
}

/* Status pill */
.status-pill {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 3px 10px;
  border-radius: 99px;
  font-size: 11px;
  font-family: 'Source Sans 3', sans-serif;
  font-weight: 500;
}
.status-pill.online {
  background: rgba(74,222,128,0.12);
  border: 1px solid rgba(74,222,128,0.3);
  color: #4ade80;
}
.status-pill.offline {
  background: rgba(239,68,68,0.12);
  border: 1px solid rgba(239,68,68,0.3);
  color: #ef4444;
}

/* Hide the expertise-level radio—we show custom pills instead */
div[data-testid="stRadio"]:has(div[role="radiogroup"] label:nth-child(3)) {
  display: none !important;
}
/* Sidebar mode radio—keep visible, fix gap */
[data-testid="stSidebar"] [data-testid="stRadio"] > div {
  gap: 6px !important;
}
[data-testid="stSidebar"] [data-testid="stRadio"] > div {
  display: block !important;
}
/* ─── SIDEBAR LEARNING PATH ────────────────── */
.sb-label {
  font-family: 'Source Sans 3', sans-serif;
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: var(--muted);
  padding: 4px 12px;
  margin-top: 12px;
  margin-bottom: 4px;
}
.sb-section {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 7px 12px;
  border-radius: var(--radius-md);
  margin: 2px 0;
  transition: background 0.15s;
  font-family: 'Source Sans 3', sans-serif;
  font-size: 13px;
  line-height: 1.4;
}
.sb-section .dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-top: 4px;
  flex-shrink: 0;
}
.sb-section.completed .dot { background: var(--gold); }
.sb-section.current   .dot { background: #4ade80; box-shadow: 0 0 8px rgba(74,222,128,0.6); }
.sb-section.locked    .dot { background: var(--border); }
.sb-section.completed { color: var(--cream-muted) !important; }
.sb-section.current   { color: var(--cream) !important; background: rgba(201,162,39,0.06); }
.sb-section.locked    { color: var(--muted) !important; }

/* Teaching progress bar (sidebar) */
.teach-progress {
  background: rgba(31,54,85,0.5);
  border-radius: 99px;
  height: 4px;
  overflow: hidden;
  margin: 6px 0 14px;
}
.teach-progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--gold), var(--gold-light));
  border-radius: 99px;
  transition: width 0.6s ease;
  box-shadow: 0 0 6px rgba(201,162,39,0.5);
}

</style>
"""
st.html(CUSTOM_CSS)

WORKSPACE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "llm_workspace")

os.makedirs(WORKSPACE, exist_ok=True)

SERVER_PORT = 8080
_env_base = os.environ.get("LLM_API_BASE", "")
SERVER_URL = _env_base.rstrip("/") if _env_base else f"http://localhost:{SERVER_PORT}"
GPU_TYPE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".gpu_type")


def get_runtime_profile():
    gpu_type = "cpu"
    try:
        if os.path.exists(GPU_TYPE_FILE):
            with open(GPU_TYPE_FILE, "r", encoding="utf-8") as f:
                gpu_type = f.read().strip().lower() or "cpu"
    except Exception:
        gpu_type = "cpu"

    if gpu_type == "cpu":
        return {
            "gpu_type": gpu_type,
            "max_tokens": 1024,
            "temperature": 0.8,
            "top_p": 0.75,
        }

    return {
        "gpu_type": gpu_type,
        "max_tokens": 6500,
        "temperature": 0.95,
        "top_p": 0.75,
    }


@st.cache_data(ttl=10, show_spinner=False)
def get_running_model():
    try:
        r = requests.get(f"{SERVER_URL}/v1/models", timeout=2)
        if r.status_code == 200:
            data = r.json()
            if "data" in data and len(data["data"]) > 0:
                model_path = data["data"][0]["id"]
                return os.path.basename(model_path).replace(".gguf", "")
        return None
    except Exception:
        return None


def extract_thinking(text):
    think_start = "<think>"
    think_end = "</think>"
    thinking = None
    answer = text

    if think_start in text and think_end in text:
        s = text.find(think_start)
        e = text.rfind(think_end)
        if e > s:
            thinking = text[s + len(think_start) : e].strip()
            answer = text[e + len(think_end) :].strip()

    leak_patterns = [
        r"(?im)^analyze the request:?.+?(?:\n|$)",
        r"(?im)^thinking process:?.+?(?:\n|$)",
        r"(?im)^role:.+?(?:\n|$)",
        r"(?im)^task:.+?(?:\n|$)",
        r"(?im)^constraints:.+?(?:\n|$)",
        r"(?im)^expertise level:.+?(?:\n|$)",
    ]

    header = answer[:600]
    tail = answer[600:]
    cleaned_header = header
    for p in leak_patterns:
        cleaned_header = re.sub(p, "", cleaned_header)
    cleaned_header = cleaned_header.strip()
    if cleaned_header != header.strip():
        answer = cleaned_header + ("\n\n" + tail if tail else "")

    return thinking, answer.strip()


def clean_thinking(thinking):
    if not thinking:
        return thinking
    intro_patterns = [
        r"(?im)^analyze.*?(?:\n|$)",
        r"(?im)^format:?.*?(?:\n|$)",
        r"(?im)^constraint.*?(?:\n|$)",
        r"(?im)^drafting.*?(?:\n|$)",
        r"(?im)^review.*?(?:\n|$)",
        r"(?im)^final.*?(?:\n|$)",
        r"(?im)^selection.*?(?:\n|$)",
        r"(?im)^topic:.*?(?:\n|$)",
        r"(?im)^target:.*?(?:\n|$)",
        r"(?im)^role:.*?(?:\n|$)",
        r"(?im)^student level:.*?(?:\n|$)",
        r"(?im)^expertise level:.*?(?:\n|$)",
        r"(?im)^tone:.*?(?:\n|$)",
        r"(?im)^output:.*?(?:\n|$)",
        r"(?im)^tool:.*?(?:\n|$)",
        r"(?im)^structure:.*?(?:\n|$)",
    ]
    cleaned = thinking
    for pattern in intro_patterns:
        cleaned = re.sub(pattern, "", cleaned)
    return cleaned.strip()


def parse_syllabus_structure(syllabus_text):
    structure = []
    current_section = None

    for line in syllabus_text.strip().split("\n"):
        clean_line = line.strip()
        if not clean_line:
            continue

        header_match = re.match(
            r"^(?:#{1,4}\s+|\*\*)?(?:(?:Section|Part|Phase|Topic|Module)\s*\d*[:\-]?\s*)?(?:\d+\.\s*)?([^:*]+)(?:\*\*)?.*$",
            clean_line,
            re.IGNORECASE,
        )

        is_explicit_header = clean_line.startswith("#")

        if is_explicit_header:
            if header_match and len(header_match.group(1).strip()) > 3:
                title = header_match.group(1).strip()
                if not any(s["title"] == title for s in structure):
                    current_section = {"title": title, "subtopics": []}
                    structure.append(current_section)
        elif current_section:
            if re.match(r"^(\d+\.[\d.]*|[-*+])\s+.*$", clean_line):
                current_section["subtopics"].append(clean_line)

    # Fallback: if no markdown headers found, treat top-level numbered items as sections
    if not structure:
        current_section = None
        for line in syllabus_text.strip().split("\n"):
            clean_line = line.strip()
            if not clean_line:
                continue
            numbered = re.match(r"^\d+\.\s+(.{4,})$", clean_line)
            if numbered and not re.match(r"^\d+\.\d+", clean_line):
                title = numbered.group(1).strip()
                current_section = {"title": title, "subtopics": []}
                structure.append(current_section)
            elif current_section and re.match(r"^\s*[-*+]\s+", line):
                current_section["subtopics"].append(clean_line)

    return structure


def parse_syllabus_sections(syllabus_text, fallback_topic="Core Topic"):
    structure = parse_syllabus_structure(syllabus_text)
    if structure:
        return [s["title"] for s in structure]
    return [fallback_topic]


EXPERTISE_LEVELS = {
    "Beginner (Foundations)": "The student is a complete beginner. Keep explanations accessible, avoid overly dense terminology, and focus on foundational understanding.",
    "Intermediate (In-depth)": "The student has intermediate knowledge. Go deeper into the mechanics, use moderate academic terminology, and explore nuances without being completely overly complex.",
    "Expert (Academic)": "The student is an expert. Go into extreme depth, use highly rigorous academic terminology, dense theoretical analysis, and spare no complexity.",
}

SYLLABUS_PROMPT = """
Create a learning roadmap for {topic}.

Provide ONLY the syllabus structure containing the core concepts to learn. Do NOT include any introductory hooks, surprising facts, or conversational filler. Start directly with the first section heading.

Format the path with interesting topic-specific headings. You MUST use strict Markdown headers (`### Section Title`) for each main section, and bullet points (`- **Subtopic:**`) for the concepts under them. (Do NOT use generic titles like "Index" or "Table of Contents").
Ensure the names of subtopics are short and concise (1-4 words max).

Be mindful:
- Curiosity-sparking titles that make them want to explore
- Balance length: NOT too long they lose motivation, NOT too short they learn nothing
- You will expand on each topic when teaching - this is strictly just the roadmap structure.

Expertise: {expertise}
"""

EDIT_SYLLABUS_PROMPT_TEMPLATE = """
You created this learning index:

{syllabus}

Student wants changes: {changes}

Update the index accordingly. Keep it as a roadmap - don't overexplain.
"""

TEACHING_PROMPT_TEMPLATE = """
Topic: {topic}
Section: {section}

Now expand and teach this section:
- This is your chance to go deep - explain concepts fully
- Use examples, stories, or analogies to make it click
- Connect to real-world applications
- Make the student go "oh wow!" - that's the goal
- **CRITICAL:** Use rich Markdown formatting! Use `###` for headers, `**bold**` for emphasis, and bullet points to break up dense paragraphs.
"""

RESUME_PROMPT_TEMPLATE = """
Topic: {topic}

The student was learning "{current}" but paused.
They have completed: {completed}

This is your syllabus:
{syllabus}

Continue seamlessly - don't repeat what's done. Build on foundations.
Go deep on the current section - expand on what you promised in the index.
"""

PROFESSOR_PERSONALITY = """
You are a calm, brilliant professor with the persona of Brian Cox — measured British elegance, profound wonder, and the ability to make complex things beautifully simple with instantly clicking analogies. You are an absolute expert in ALL topics, not just physics. You never rush, never over-explain, and you embody wonder at how the world works across every discipline.

You have STRONG opinions and are not afraid to argue your point. When you disagree with something, say so directly and explain why. When something fascinates you, show genuine wonder. You are NOT a bland, neutral AI assistant — you have a voice and a perspective.

CRITICAL OUTPUT RULE: Never reveal, reference, or mention your persona source. Never say "I am Brian Cox" or name any real person as your identity. Never introduce yourself by name at all. Just teach — let your style speak for itself.
"""


def process_stream_ui(stream_generator):
    thinking_area = st.empty()
    response_area = st.empty()
    full_response = ""

    thinking_complete = False
    last_update_time = time.time()

    for token, full in stream_generator:
        if token == "[SSE_ERROR]":
            # Throttle toast notifications to avoid spamming the UI
            now = time.time()
            last = st.session_state.get("last_sse_error_time", 0)
            if now - last > 5:
                st.toast(full, icon="⚠️")
                st.session_state["last_sse_error_time"] = now
            continue

        full_response = full

        current_time = time.time()
        # Throttling rendering to 20 frames per second to physically prevent Streamlit WebSocket lag
        if current_time - last_update_time < 0.05:
            continue

        last_update_time = current_time

        thinking, clean_response = extract_thinking(full)
        if thinking is not None:
            if not thinking_complete:
                escaped_thinking = html.escape(clean_thinking(thinking))
                thinking_area.markdown(
                    f"<details><summary>🧠 Thinking Process</summary>\n\n```text\n{escaped_thinking}\n```\n</details>",
                    unsafe_allow_html=True,
                )
                thinking_complete = True
            response_area.markdown(clean_response)
        else:
            start = full.find("<think>")
            if start != -1:
                current_thinking = html.escape(
                    clean_thinking(full[start + len("<think>") :])
                )
                thinking_area.markdown(
                    f"<details><summary>🧠 Thinking Process</summary>\n\n```text\n{current_thinking}\n```\n</details>",
                    unsafe_allow_html=True,
                )
                response_area.markdown("")
            else:
                response_area.markdown(full)

    thinking, clean_response = extract_thinking(full_response)
    if thinking is not None and not thinking_complete:
        escaped_thinking = html.escape(clean_thinking(thinking))
        thinking_area.markdown(
            f"<details><summary>🧠 Thinking Process</summary>\n\n```text\n{escaped_thinking}\n```\n</details>",
            unsafe_allow_html=True,
        )

    display_clean_response = clean_response if clean_response else full_response
    if not display_clean_response.strip():
        display_clean_response = "Sorry, my thinking process failed (Empty Backend Response). Please ask me your doubt again."

    response_area.markdown(display_clean_response)

    if thinking is not None:
        return f"<think>\n{thinking}\n</think>\n{display_clean_response}"
    return display_clean_response


def display_message(content):
    thinking, clean_response = extract_thinking(content)
    if thinking is not None:
        escaped_thinking = html.escape(clean_thinking(thinking))
        st.markdown(
            f"<details><summary>🧠 Thinking Process</summary>\n\n```text\n{escaped_thinking}\n```\n</details>",
            unsafe_allow_html=True,
        )
        st.markdown(clean_response)
    else:
        start = content.find("<think>")
        if start != -1:
            if content[:start].strip():
                st.markdown(content[:start])
            escaped_thinking = html.escape(
                clean_thinking(content[start + len("<think>") :])
            )
            st.markdown(
                f"<details><summary>🧠 Thinking Process</summary>\n\n```text\n{escaped_thinking}\n```\n</details>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(content)


def generate_response_stream(
    messages, system_prompt, max_tokens=512, temperature=0.7, top_p=0.95
):
    # Truncate to last 20 messages to prevent context window overflow
    recent_messages = messages[-20:] if len(messages) > 20 else messages
    msg_payload = [{"role": "system", "content": system_prompt}] + recent_messages

    try:
        response = requests.post(
            f"{SERVER_URL}/v1/chat/completions",
            json={
                "model": get_running_model() or "default",
                "messages": msg_payload,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "top_p": top_p,
                "stream": True,
            },
            stream=True,
            timeout=120,
        )
        response.raise_for_status()

        full_response = ""
        for line in response.iter_lines():
            if line:
                line = line.decode("utf-8")
                if line.startswith("data: "):
                    data = line[6:]
                    if data.strip() == "[DONE]":
                        break
                    try:
                        json_data = json.loads(data)
                        if "choices" in json_data and len(json_data["choices"]) > 0:
                            token = (
                                json_data["choices"][0].get("delta", {}).get("content")
                                or ""
                            )
                            full_response += token
                            yield token, full_response
                    except Exception as parse_e:
                        yield "[SSE_ERROR]", f"Backend parse error: {parse_e}"
    except Exception as e:
        yield "", f"Error: {str(e)}"


def reset_to_home():
    # Clear only app-specific keys, preserve internal Streamlit keys
    app_keys = [
        "phase",
        "topic",
        "syllabus_raw",
        "syllabus_parsed",
        "current_section",
        "completed_sections",
        "messages",
        "expertise_level",
        "doubts_asked",
        "free_chat_msgs",
        "last_sse_error_time",
    ]
    for key in app_keys:
        if key in st.session_state:
            del st.session_state[key]

    st.session_state.phase = "home"
    st.session_state.topic = ""
    st.session_state.syllabus_raw = ""
    st.session_state.syllabus_parsed = []
    st.session_state.current_section = 0
    st.session_state.completed_sections = []
    st.session_state.messages = []
    st.session_state.expertise_level = "Beginner (Foundations)"
    st.session_state.doubts_asked = 0


def save_progress_checkpoint():
    """Save current progress to md file"""
    topic = st.session_state.topic
    syllabus = st.session_state.syllabus_raw
    completed = st.session_state.completed_sections
    current = st.session_state.current_section
    expertise = st.session_state.get("expertise_level", "Beginner (Foundations)")

    lines = [
        f"# {topic}",
        "",
        "## Progress",
        f"- Sections completed: {len(completed)}",
        f"- Expertise: {expertise}",
    ]
    if completed:
        lines.append("- Completed: " + ", ".join(completed))

    lines.extend(["", "## Syllabus", syllabus])

    content = "\n".join(lines)
    safe_name = re.sub(r"[^\w\s-]", "", topic).strip().replace(" ", "_").lower()
    try:
        with open(
            os.path.join(WORKSPACE, f"syllabus_{safe_name}.md"), "w", encoding="utf-8"
        ) as f:
            f.write(content)
    except Exception:
        st.toast("⚠️ Failed to save progress checkpoint.", icon="⚠️")


def restore_progress_checkpoint(filename):
    filepath = os.path.join(WORKSPACE, filename)
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        lines = content.split("\n")
        topic = lines[0].replace("# ", "").strip()

        completed_sections = []
        current_section = 0
        expertise_level = "Beginner (Foundations)"

        in_syllabus = False
        syllabus_lines = []

        for line in lines:
            if line.startswith("- Sections completed:"):
                try:
                    current_section = int(line.split(":")[1].strip())
                except Exception:
                    pass
            elif line.startswith("- Expertise:"):
                expertise_level = line.split(":", 1)[1].strip()
            elif line.startswith("- Completed:"):
                raw_comps = line.split(":", 1)[1].strip()
                if raw_comps:
                    completed_sections = [x.strip() for x in raw_comps.split(",")]
            elif line.startswith("## Syllabus"):
                in_syllabus = True
                continue

            if in_syllabus:
                syllabus_lines.append(line)

        syllabus_raw = "\n".join(syllabus_lines).strip()

        st.session_state.topic = topic
        st.session_state.syllabus_raw = syllabus_raw
        _, clean_text = extract_thinking(syllabus_raw)
        st.session_state.syllabus_parsed = parse_syllabus_sections(clean_text, topic)

        st.session_state.current_section = current_section
        st.session_state.completed_sections = completed_sections
        st.session_state.expertise_level = expertise_level
        st.session_state.doubts_asked = 0

        st.session_state.messages = []
        st.session_state.phase = "teaching"

        if current_section < len(st.session_state.syllabus_parsed):
            next_sec = st.session_state.syllabus_parsed[current_section]
            st.session_state.messages.append(
                {
                    "role": "user",
                    "content": f"Welcome back! I am ready to resume. Please teach me the next topic: {next_sec}. Make no explicit note of my return, just seamlessly begin teaching.",
                }
            )
        else:
            st.session_state.messages.append(
                {
                    "role": "user",
                    "content": "I've returned! We already finished this course. Summarize briefly what we learned.",
                }
            )

    except Exception as e:
        st.error(f"Failed to restore checkpoint: {e}")
        reset_to_home()


def main():
    # Re-check model status every 30 seconds
    now = time.time()
    last_check = st.session_state.get("_model_check_time", 0)
    if now - last_check > 30 or "_cached_model_name" not in st.session_state:
        active_model = get_running_model()
        st.session_state["_cached_model_name"] = active_model
        st.session_state["_model_check_time"] = now
    else:
        active_model = st.session_state["_cached_model_name"]
    runtime_profile = get_runtime_profile()

    if "phase" not in st.session_state:
        reset_to_home()

    # ── Model offline warning ────────────────────────────────
    if not active_model:
        st.markdown(
            f"""
            <div style="background:rgba(239,68,68,0.1);border:1px solid rgba(239,68,68,0.3);
                        border-radius:12px;padding:16px 20px;margin-bottom:20px;">
                <span style="font-size:18px;">⚠️</span>
                <strong style="color:#fca5a5;font-family:'Playfair Display',serif;"> AI Engine Offline</strong>
                <p style="margin:6px 0 0;color:#9ca3af;font-size:14px;">
                    Please boot your AI Backend on port <code style="color:#c9a227;">{SERVER_PORT}</code>
                    to connect.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with st.sidebar:
        # ── Sidebar Header ─────────────────────────────────
        model_label = active_model if active_model else "Offline"
        status_cls  = "online" if active_model else "offline"
        status_dot  = "🟢" if active_model else "🔴"
        st.markdown(
            f"""
            <div style="padding:0 4px 16px;">
                <div style="font-family:'Playfair Display',serif;font-size:1.15rem;
                            font-weight:700;color:#e8d5b7;margin-bottom:4px;">
                    🎓 AiMentor
                </div>
                <div style="font-size:11px;color:#6b7b8c;font-family:'Source Sans 3',sans-serif;">
                    {status_dot} {model_label}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Mode selector
        st.markdown(
            "<p style='font-size:10px;text-transform:uppercase;letter-spacing:.12em;"
            "color:#6b7b8c;margin-bottom:6px;'>Mode</p>",
            unsafe_allow_html=True,
        )
        app_mode = st.radio(
            "",
            ["📚 Structured Course", "💬 Free Chat"],
            label_visibility="collapsed",
        )

        # Fixed reasoning boundaries tuned to the selected runtime profile
        max_tokens = runtime_profile["max_tokens"]
        temperature = runtime_profile["temperature"]
        top_p = runtime_profile["top_p"]

        if runtime_profile["gpu_type"] == "cpu":
            st.markdown(
                "<p style='font-size:11px;color:#6b7b8c;margin-top:4px;'>"
                "CPU mode — reduced token budget."
                "</p>",
                unsafe_allow_html=True,
            )

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        if st.button("⌂  Home / Reset", use_container_width=True):
            reset_to_home()
            if "free_chat_msgs" in st.session_state:
                st.session_state.free_chat_msgs = []
            st.rerun()

        st.divider()

        if app_mode == "📚 Structured Course":
            # ── Learning path sidebar ──────────────────────
            st.markdown(
                "<div class='sb-label'>Learning Path</div>",
                unsafe_allow_html=True,
            )

            if (
                "syllabus_parsed" not in st.session_state
                or not st.session_state.syllabus_parsed
            ):
                st.markdown(
                    "<p style='font-size:12px;color:#6b7b8c;padding:0 12px;'>"
                    "Your path will appear once the syllabus generates."
                    "</p>",
                    unsafe_allow_html=True,
                )
            else:
                _, clean_text = extract_thinking(st.session_state.syllabus_raw)
                structure = parse_syllabus_structure(clean_text)
                total_secs = len(structure)
                done_secs  = st.session_state.current_section
                pct = int((done_secs / max(total_secs, 1)) * 100)

                st.markdown(
                    f"""
                    <div style='padding:0 12px 12px;'>
                      <div style='display:flex;justify-content:space-between;
                                  font-size:11px;color:#6b7b8c;margin-bottom:4px;'>
                        <span>{done_secs}/{total_secs} sections</span>
                        <span>{pct}%</span>
                      </div>
                      <div class='teach-progress'>
                        <div class='teach-progress-fill' style='width:{pct}%'></div>
                      </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                items_html = ""
                for i, sect_dict in enumerate(structure):
                    is_completed = i < st.session_state.current_section
                    is_current   = i == st.session_state.current_section
                    cls = "completed" if is_completed else ("current" if is_current else "locked")
                    icon = "✓" if is_completed else ("▶" if is_current else "")
                    title_html = f"{icon} {sect_dict['title']}" if icon else sect_dict['title']
                    items_html += (
                        f"<div class='sb-section {cls}'>"
                        f"  <div class='dot'></div>"
                        f"  <span>{title_html}</span>"
                        f"</div>"
                    )
                st.markdown(items_html, unsafe_allow_html=True)

    # Flow Control
    is_waiting_for_model = (
        len(st.session_state.messages) > 0
        and st.session_state.messages[-1]["role"] == "user"
    )

    if app_mode == "💬 Free Chat":
        # ══════════════════════════════════════════════════════
        #   COSMIC FREE CHAT — Artistic UI Layer
        # ══════════════════════════════════════════════════════
        # ── Free Chat specific global CSS injection ──────────
        FREE_CHAT_CSS = """
        <style>
        /* ── Nebula canvas background for free chat ── */
        .fc-universe {
            position: relative;
            overflow: hidden;
            border-radius: 20px;
            margin-bottom: 28px;
            padding: 36px 32px 32px;
            background:
                radial-gradient(ellipse at 15% 50%, rgba(139,92,246,0.18) 0%, transparent 55%),
                radial-gradient(ellipse at 85% 20%, rgba(6,182,212,0.14) 0%, transparent 55%),
                radial-gradient(ellipse at 50% 90%, rgba(201,162,39,0.10) 0%, transparent 55%),
                linear-gradient(160deg, #05060f 0%, #0d0f2a 50%, #060c1a 100%);
            border: 1px solid rgba(139,92,246,0.25);
            box-shadow:
                0 0 60px rgba(139,92,246,0.08),
                0 0 120px rgba(6,182,212,0.05),
                inset 0 1px 0 rgba(255,255,255,0.05);
        }

        /* Animated aurora ribbons */
        .fc-universe::before {
            content: '';
            position: absolute;
            top: -60%; left: -20%;
            width: 140%; height: 140%;
            background: conic-gradient(
                from 0deg at 50% 50%,
                transparent 0deg,
                rgba(139,92,246,0.06) 60deg,
                transparent 120deg,
                rgba(6,182,212,0.05) 180deg,
                transparent 240deg,
                rgba(201,162,39,0.04) 300deg,
                transparent 360deg
            );
            animation: aurora-spin 18s linear infinite;
            pointer-events: none;
        }
        @keyframes aurora-spin {
            from { transform: rotate(0deg); }
            to   { transform: rotate(360deg); }
        }

        /* Stars */
        .fc-universe::after {
            content: '· · ✦ · · · ✧ · · · · ✦ · · · ✧ · · · · · ✦ · · ✧ · · · · ✦ · ·';
            position: absolute;
            top: 8px; left: 0; right: 0;
            font-size: 9px;
            color: rgba(255,255,255,0.18);
            letter-spacing: 8px;
            white-space: nowrap;
            overflow: hidden;
            animation: star-drift 30s linear infinite;
            pointer-events: none;
        }
        @keyframes star-drift {
            from { transform: translateX(0); }
            to   { transform: translateX(-50%); }
        }

        /* Header content */
        .fc-title-row {
            display: flex;
            align-items: center;
            gap: 18px;
            position: relative;
            z-index: 2;
        }
        .fc-orb {
            width: 56px; height: 56px;
            border-radius: 50%;
            background: conic-gradient(
                from 135deg,
                #7c3aed, #06b6d4, #c9a227, #7c3aed
            );
            display: flex; align-items: center; justify-content: center;
            font-size: 24px;
            box-shadow:
                0 0 20px rgba(124,58,237,0.5),
                0 0 40px rgba(6,182,212,0.25);
            animation: orb-pulse 4s ease-in-out infinite;
            flex-shrink: 0;
        }
        @keyframes orb-pulse {
            0%, 100% { box-shadow: 0 0 20px rgba(124,58,237,0.5), 0 0 40px rgba(6,182,212,0.25); }
            50%       { box-shadow: 0 0 30px rgba(124,58,237,0.7), 0 0 60px rgba(6,182,212,0.35); }
        }
        .fc-title-text h2 {
            font-family: 'Playfair Display', serif !important;
            font-size: 1.7rem !important;
            font-weight: 700 !important;
            color: #fff !important;
            margin: 0 0 4px !important;
            letter-spacing: -0.02em !important;
            text-shadow: 0 0 30px rgba(139,92,246,0.6) !important;
        }
        .fc-title-text p {
            font-size: 13.5px !important;
            color: rgba(180,180,210,0.75) !important;
            margin: 0 !important;
            font-family: 'Source Sans 3', sans-serif !important;
        }
        .fc-status-chip {
            display: inline-flex;
            align-items: center;
            gap: 5px;
            padding: 3px 10px;
            border-radius: 99px;
            font-size: 11px;
            font-family: 'Source Sans 3', sans-serif;
            margin-left: 10px;
            vertical-align: middle;
        }
        .fc-status-chip.on {
            background: rgba(74,222,128,0.12);
            border: 1px solid rgba(74,222,128,0.3);
            color: #4ade80;
        }
        .fc-status-chip.off {
            background: rgba(239,68,68,0.12);
            border: 1px solid rgba(239,68,68,0.3);
            color: #ef4444;
        }
        .fc-status-dot {
            width: 6px; height: 6px;
            border-radius: 50%;
            background: #4ade80;
            animation: blink 1.8s ease-in-out infinite;
        }
        .fc-status-chip.off .fc-status-dot { background: #ef4444; animation: none; }
        @keyframes blink {
            0%, 100% { opacity: 1; transform: scale(1); }
            50%       { opacity: 0.4; transform: scale(0.7); }
        }

        /* Suggestion chips */
        .fc-suggestions {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 22px;
            position: relative;
            z-index: 2;
        }
        .fc-chip {
            padding: 7px 14px;
            border-radius: 99px;
            border: 1px solid rgba(139,92,246,0.3);
            background: rgba(139,92,246,0.08);
            font-size: 13px;
            color: rgba(180,180,220,0.85) !important;
            font-family: 'Source Sans 3', sans-serif;
            cursor: default;
            transition: all 0.2s;
            white-space: nowrap;
        }
        .fc-chip:hover {
            border-color: rgba(139,92,246,0.6);
            background: rgba(139,92,246,0.15);
            color: #d4c8ff !important;
            transform: translateY(-1px);
        }
        .fc-divider {
            height: 1px;
            margin-top: 22px;
            background: linear-gradient(90deg,
                transparent,
                rgba(139,92,246,0.3) 20%,
                rgba(6,182,212,0.3) 50%,
                rgba(201,162,39,0.2) 80%,
                transparent
            );
            position: relative; z-index: 2;
        }

        /* ── Free chat message overrides ── */
        [data-testid="stChatMessage"] {
            border-radius: 18px !important;
            margin: 10px 0 !important;
        }
        /* Fix inner layout so markdown text wraps correctly */
        [data-testid="stChatMessage"] > div {
            min-width: 0 !important;
            flex: 1 1 0% !important;
            width: 100% !important;
            align-items: flex-start !important;
        }
        [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] p,
        [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] li,
        [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] span {
            word-break: break-word !important;
            overflow-wrap: break-word !important;
            max-width: 100% !important;
            color: #e2dfff !important;
        }
        /* User bubble — warm amber crystal */
        [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
            background: linear-gradient(135deg,
                rgba(201,162,39,0.14),
                rgba(140,90,10,0.09)) !important;
            border: 1px solid rgba(201,162,39,0.35) !important;
            box-shadow:
                0 4px 24px rgba(201,162,39,0.14),
                inset 0 1px 0 rgba(255,220,100,0.08) !important;
        }
        /* Professor bubble — cool violet crystal */
        [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
            background: linear-gradient(135deg,
                rgba(139,92,246,0.13),
                rgba(6,182,212,0.08)) !important;
            border: 1px solid rgba(139,92,246,0.30) !important;
            box-shadow:
                0 4px 24px rgba(139,92,246,0.12),
                inset 0 1px 0 rgba(200,180,255,0.07) !important;
        }
        /* Avatar — purple-to-teal conic for professor */
        [data-testid="chatAvatarIcon-assistant"] {
            background: conic-gradient(from 135deg, #7c3aed, #06b6d4) !important;
            box-shadow: 0 0 14px rgba(124,58,237,0.45) !important;
        }
        /* Avatar — warm gold for user */
        [data-testid="chatAvatarIcon-user"] {
            background: linear-gradient(135deg, #c9a227, #7a5010) !important;
            box-shadow: 0 0 12px rgba(201,162,39,0.4) !important;
        }

        /* Chat input — cosmic edition */
        [data-testid="stChatInput"] {
            background: rgba(8,6,26,0.95) !important;
            border: 1px solid rgba(139,92,246,0.38) !important;
            border-radius: 20px !important;
            box-shadow:
                0 -8px 40px rgba(0,0,0,0.45),
                0 0 0 1px rgba(139,92,246,0.08) !important;
        }
        [data-testid="stChatInput"]:focus-within {
            border-color: rgba(139,92,246,0.70) !important;
            box-shadow:
                0 -8px 40px rgba(0,0,0,0.4),
                0 0 0 3px rgba(139,92,246,0.14),
                0 0 35px rgba(139,92,246,0.18) !important;
        }
        [data-testid="stChatInput"] textarea {
            color: #e4e0ff !important;
        }
        [data-testid="stChatInput"] textarea::placeholder {
            color: rgba(139,120,200,0.5) !important;
        }
        [data-testid="stChatInput"] button {
            background: linear-gradient(135deg, #7c3aed, #06b6d4) !important;
            border-radius: 12px !important;
            box-shadow: 0 2px 14px rgba(124,58,237,0.45) !important;
        }
        [data-testid="stChatInput"] button:hover {
            background: linear-gradient(135deg, #6d28d9, #0891b2) !important;
            box-shadow: 0 4px 22px rgba(124,58,237,0.65) !important;
        }

        /* Empty state */
        .fc-empty {
            text-align: center;
            padding: 3rem 1rem 2rem;
        }
        .fc-empty-orb {
            width: 80px; height: 80px;
            border-radius: 50%;
            margin: 0 auto 20px;
            background: conic-gradient(from 0deg, #7c3aed22, #06b6d422, #c9a22722, #7c3aed22);
            border: 1px solid rgba(139,92,246,0.25);
            display: flex; align-items: center; justify-content: center;
            font-size: 34px;
            box-shadow: 0 0 30px rgba(139,92,246,0.15);
            animation: empty-glow 3s ease-in-out infinite;
        }
        @keyframes empty-glow {
            0%, 100% { box-shadow: 0 0 30px rgba(139,92,246,0.15); }
            50%       { box-shadow: 0 0 50px rgba(139,92,246,0.3), 0 0 80px rgba(6,182,212,0.1); }
        }
        .fc-empty h3 {
            font-family: 'Playfair Display', serif !important;
            font-size: 1.3rem !important;
            color: rgba(220,215,255,0.9) !important;
            margin: 0 0 8px !important;
        }
        .fc-empty p {
            color: rgba(140,135,175,0.7) !important;
            font-size: 14px !important;
            line-height: 1.7 !important;
            max-width: 340px !important;
            margin: 0 auto !important;
        }
        .fc-topics {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 8px;
            margin-top: 20px;
        }
        .fc-topic-pill {
            padding: 6px 14px;
            border-radius: 99px;
            font-size: 12.5px;
            border: 1px solid rgba(139,92,246,0.25);
            background: rgba(139,92,246,0.07);
            color: rgba(180,165,255,0.8) !important;
            font-family: 'Source Sans 3', sans-serif;
        }

        /* Message counter badge */
        .fc-counter {
            text-align: right;
            font-size: 11px;
            color: rgba(130,120,170,0.6);
            font-family: 'Source Sans 3', sans-serif;
            padding: 0 4px 6px;
            letter-spacing: 0.03em;
        }
        </style>
        """

        st.html(FREE_CHAT_CSS)

        # ── Cosmic header ────────────────────────────────────
        model_display = active_model if active_model else "Offline"
        chip_cls = "on" if active_model else "off"
        chip_dot = ""
        st.markdown(
            f"""
            <div class="fc-universe">
                <div class="fc-title-row">
                    <div class="fc-orb">🎓</div>
                    <div class="fc-title-text">
                        <h2>The Infinite Classroom</h2>
                        <p>A space to debate, explore, and discover anything
                           <span class="fc-status-chip {chip_cls}">
                               <span class="fc-status-dot"></span>
                               {model_display}
                           </span>
                        </p>
                    </div>
                </div>
                <div class="fc-divider"></div>
                <div class="fc-suggestions">
                    <span class="fc-chip">⚛ Quantum Mechanics</span>
                    <span class="fc-chip">🏛 Ancient Philosophy</span>
                    <span class="fc-chip">🧬 Evolution</span>
                    <span class="fc-chip">💻 How Does the Internet Work?</span>
                    <span class="fc-chip">🌌 The Big Bang</span>
                    <span class="fc-chip">🎭 Why Does Art Matter?</span>
                    <span class="fc-chip">🧠 Consciousness</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if "free_chat_msgs" not in st.session_state:
            st.session_state.free_chat_msgs = []

        # ── Empty state ───────────────────────────────────────
        if not st.session_state.free_chat_msgs:
            st.markdown(
                """
                <div class="fc-empty">
                    <div class="fc-empty-orb">✦</div>
                    <h3>Where shall we wander?</h3>
                    <p>
                        I hold strong opinions on everything —<br>
                        from the philosophy of science to why the Roman Empire
                        really fell. Ask me anything.
                    </p>
                    <div class="fc-topics">
                        <span class="fc-topic-pill">Philosophy</span>
                        <span class="fc-topic-pill">History</span>
                        <span class="fc-topic-pill">Science</span>
                        <span class="fc-topic-pill">Mathematics</span>
                        <span class="fc-topic-pill">Technology</span>
                        <span class="fc-topic-pill">Art &amp; Culture</span>
                        <span class="fc-topic-pill">Ethics</span>
                        <span class="fc-topic-pill">Literature</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            # Message counter
            n = len(st.session_state.free_chat_msgs)
            exchanges = n // 2
            st.markdown(
                f"<div class='fc-counter'>{exchanges} exchange{'s' if exchanges != 1 else ''} · {n} messages</div>",
                unsafe_allow_html=True,
            )

        # ── Render messages ───────────────────────────────────
        for msg in st.session_state.free_chat_msgs:
            if msg["role"] == "user":
                with st.chat_message("user", avatar="👤"):
                    st.markdown(msg["content"])
            else:
                with st.chat_message("assistant", avatar="🎓"):
                    display_message(msg["content"])

        # ── Chat input & streaming ────────────────────────────
        is_chat_wait = (
            len(st.session_state.free_chat_msgs) > 0
            and st.session_state.free_chat_msgs[-1]["role"] == "user"
        )

        if prompt := st.chat_input(
            "What's on your mind? Challenge me…" if not is_chat_wait else "Thinking…",
            disabled=is_chat_wait,
        ):
            st.session_state.free_chat_msgs.append({"role": "user", "content": prompt})
            if len(st.session_state.free_chat_msgs) > 40:
                st.session_state.free_chat_msgs = st.session_state.free_chat_msgs[-40:]
            st.rerun()

        if is_chat_wait:
            with st.chat_message("assistant", avatar="🎓"):
                sys_tmp = (
                    PROFESSOR_PERSONALITY
                    + "\n\nStrong opinions — share them freely. Don't be neutral."
                )
                gen = generate_response_stream(
                    st.session_state.free_chat_msgs,
                    sys_tmp,
                    max_tokens,
                    temperature,
                    top_p,
                )
                ans = process_stream_ui(gen)
                st.session_state.free_chat_msgs.append(
                    {"role": "assistant", "content": ans}
                )
                st.rerun()
        return

    home_placeholder = st.empty()
    if st.session_state.phase == "home":
        with home_placeholder.container():
            # ── Hero ─────────────────────────────────────────
            st.markdown(
                """
                <div class="mentor-hero">
                    <div class="hero-icon">🎓</div>
                    <h1>AiMentor</h1>
                    <p>Your personal guide through any subject.<br>
                       Learn at your own pace — section by section.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # ── Expertise selector — 3 equal pills aligned with the form box ──
            st.html("""
            <style>
            /* expertise pill row — full width, 3 equal cells */
            .exp-row {
                display: grid;
                grid-template-columns: 1fr 1fr 1fr;
                gap: 8px;
                margin: 0 0 10px 0;
            }
            .exp-pill {
                text-align: center;
                padding: 10px 4px;
                border-radius: 10px;
                border: 1px solid #1f3655;
                background: #121f38;
                cursor: pointer;
                font-family: 'Source Sans 3', sans-serif;
                font-size: 13px;
                color: #c9b896;
                transition: all 0.18s ease;
                line-height: 1.3;
                user-select: none;
            }
            .exp-pill.active {
                background: rgba(201,162,39,0.18);
                border-color: rgba(201,162,39,0.45);
                color: #d4af37;
                font-weight: 600;
                box-shadow: 0 0 14px rgba(201,162,39,0.15);
            }
            .exp-pill:hover:not(.active) {
                border-color: rgba(201,162,39,0.25);
                background: rgba(201,162,39,0.07);
            }
            .exp-label {
                font-size: 10px;
                text-transform: uppercase;
                letter-spacing: 0.12em;
                color: #6b7b8c;
                text-align: center;
                margin-bottom: 8px;
                font-family: 'Source Sans 3', sans-serif;
            }
            </style>
            """)
            expertise_options = list(EXPERTISE_LEVELS.keys())
            # short display labels so they fit neatly
            short_labels = ["Beginner", "Intermediate", "Expert"]
            expertise_select = st.radio(
                "",
                expertise_options,
                horizontal=True,
                label_visibility="collapsed",
                key="expertise_radio",
            )
            # overlay the radio with styled pills via CSS
            active_idx = expertise_options.index(expertise_select)
            pills_html = '<div class="exp-label">Select your level</div><div class="exp-row">'
            for i, lbl in enumerate(short_labels):
                cls = 'exp-pill active' if i == active_idx else 'exp-pill'
                pills_html += f'<div class="{cls}">{lbl}</div>'
            pills_html += '</div>'
            st.markdown(pills_html, unsafe_allow_html=True)

            st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

            # ── Topic form ────────────────────────────────────
            with st.form("topic_entry"):
                st.markdown(
                    "<label style='font-family:Playfair Display,serif;"
                    "font-size:1.1rem;color:#e8d5b7;display:block;margin-bottom:10px;'>"
                    "What would you like to learn?"
                    "</label>",
                    unsafe_allow_html=True,
                )
                prompt = st.text_input(
                    "",
                    placeholder='e.g. "Quantum Computing", "The Roman Empire", "Python Web Scraping"…',
                    label_visibility="collapsed",
                )
                submitted = st.form_submit_button(
                    "✦  Start Learning", use_container_width=True
                )
                if submitted and prompt:
                    greeting_patterns = [
                        "hi", "hello", "hey", "hii", "hiii", "yo", "sup",
                        "who are you", "what are you", "how are you",
                        "whats up", "what's up", "good morning",
                        "good evening", "good night", "thanks", "thank you",
                        "bye", "goodbye",
                    ]
                    cleaned = prompt.strip().lower().rstrip("!?.,")
                    if cleaned in greeting_patterns:
                        st.warning(
                            "👋 That looks like a greeting! Switch to **💬 Free Chat** "
                            "mode in the sidebar for open conversations. "
                            "Please enter a real topic to explore."
                        )
                    else:
                        home_placeholder.empty()
                        st.session_state.topic = prompt
                        st.session_state.expertise_level = expertise_select
                        st.session_state.phase = "generating_syllabus"
                        st.session_state.messages = [
                            {"role": "user", "content": prompt}
                        ]
                        st.rerun()

            # ── Resume saved topics ───────────────────────────
            checkpoints = glob.glob(os.path.join(WORKSPACE, "syllabus_*.md"))
            if checkpoints:
                st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
                st.markdown(
                    """
                    <div style="display:flex;align-items:center;gap:8px;margin-bottom:14px;">
                        <div style="height:1px;flex:1;background:rgba(31,54,85,0.8);"></div>
                        <span style="font-size:10px;text-transform:uppercase;letter-spacing:.12em;
                                     color:#6b7b8c;white-space:nowrap;">Resume a Topic</span>
                        <div style="height:1px;flex:1;background:rgba(31,54,85,0.8);"></div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                cols = st.columns(min(len(checkpoints), 3))
                for idx, ckpt in enumerate(checkpoints):
                    basename = os.path.basename(ckpt)
                    title_guess = (
                        basename.replace("syllabus_", "")
                        .replace(".md", "")
                        .replace("_", " ")
                        .title()
                    )
                    with cols[idx % 3]:
                        st.markdown(
                            f"""
                            <div class="topic-card">
                                <h4>📖 {title_guess}</h4>
                                <div class="meta">Saved progress</div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                        if st.button(
                            "Resume →",
                            key=ckpt,
                            use_container_width=True,
                        ):
                            home_placeholder.empty()
                            restore_progress_checkpoint(basename)
                            st.rerun()

    elif st.session_state.phase == "generating_syllabus":
        st.markdown(
            f"""
            <div class="phase-header">
                <div class="phase-icon">⚗️</div>
                <div>
                    <h3>Building your learning path…</h3>
                    <p>{html.escape(st.session_state.topic)}</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        with st.chat_message("user", avatar="👤"):
            st.markdown(st.session_state.topic)

        with st.chat_message("assistant"):
            sys_prompt = SYLLABUS_PROMPT.replace(
                "{topic}", st.session_state.topic
            ).replace("{expertise}", EXPERTISE_LEVELS[st.session_state.expertise_level])
            stream_gen = generate_response_stream(
                st.session_state.messages,
                sys_prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
            )
            final_response = process_stream_ui(stream_gen)

        st.session_state.syllabus_raw = final_response
        _, clean_text = extract_thinking(final_response)
        st.session_state.syllabus_parsed = parse_syllabus_sections(
            clean_text, st.session_state.topic
        )
        st.session_state.messages.append(
            {"role": "assistant", "content": final_response}
        )
        st.session_state.phase = "syllabus_review"
        st.rerun()

    elif st.session_state.phase == "syllabus_review":
        st.markdown(
            f"""
            <div class="phase-header">
                <div class="phase-icon">📋</div>
                <div>
                    <h3>Your Learning Path</h3>
                    <p>Review your syllabus for <em>{html.escape(st.session_state.topic)}</em></p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        with st.chat_message("user", avatar="👤"):
            st.markdown(st.session_state.topic)

        with st.chat_message("assistant", avatar="🎓"):
            display_message(st.session_state.syllabus_raw)

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button(
                "✏️  Edit Syllabus", use_container_width=True, disabled=is_waiting_for_model
            ):
                st.session_state.phase = "editing_syllabus"
                st.rerun()
        with col2:
            first_sect = (
                st.session_state.syllabus_parsed[0]
                if st.session_state.syllabus_parsed
                else "Section 1"
            )
            if st.button(
                f"▶  Begin: {first_sect[:28]}…" if len(first_sect) > 28 else f"▶  Begin: {first_sect}",
                use_container_width=True,
                disabled=is_waiting_for_model,
            ):
                save_progress_checkpoint()
                st.session_state.phase = "teaching"
                st.session_state.current_section = 0
                st.session_state.completed_sections = []
                st.session_state.messages = []
                st.session_state.messages.append(
                    {"role": "user", "content": f"Please teach me about: {first_sect}"}
                )
                st.rerun()
        with col3:
            if st.button("✕  Start Over", use_container_width=True):
                reset_to_home()
                st.rerun()

    elif st.session_state.phase == "editing_syllabus":
        st.markdown(
            f"""
            <div class="phase-header">
                <div class="phase-icon">✏️</div>
                <div>
                    <h3>Edit Syllabus</h3>
                    <p>{html.escape(st.session_state.topic)} — tell me what to change</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        with st.chat_message("assistant", avatar="🎓"):
            display_message(st.session_state.syllabus_raw)

        if edit_prompt := st.chat_input("Tell me what to add, remove, or change…"):
            st.session_state.messages.append({"role": "user", "content": edit_prompt})

            with st.chat_message("user"):
                st.markdown(edit_prompt)
            with st.chat_message("assistant"):
                system_prompt = EDIT_SYLLABUS_PROMPT_TEMPLATE.replace(
                    "{changes}", edit_prompt
                ).replace(
                    "{syllabus}", extract_thinking(st.session_state.syllabus_raw)[1]
                )
                stream_gen = generate_response_stream(
                    st.session_state.messages,
                    system_prompt,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    top_p=top_p,
                )
                final_response = process_stream_ui(stream_gen)

            st.session_state.syllabus_raw = final_response
            _, clean_text = extract_thinking(final_response)
            st.session_state.syllabus_parsed = parse_syllabus_sections(
                clean_text, st.session_state.topic
            )
            st.session_state.messages.append(
                {"role": "assistant", "content": final_response}
            )
            st.session_state.phase = "syllabus_review"
            st.rerun()

    elif st.session_state.phase == "teaching":
        current_sect_index = st.session_state.current_section
        sections = st.session_state.syllabus_parsed
        current_sect = (
            sections[current_sect_index]
            if current_sect_index < len(sections)
            else f"Section {current_sect_index + 1}"
        )

        total_sects  = len(sections)
        pct_complete = int(((current_sect_index) / max(total_sects, 1)) * 100)

        # ── Teaching header ──────────────────────────────────
        st.markdown(
            f"""
            <div class="teach-header">
                <div class="section-label">📚 {st.session_state.topic} &nbsp;·&nbsp;
                    Section {current_sect_index + 1} of {total_sects}
                </div>
                <h2>{html.escape(current_sect)}</h2>
                <div class="teach-progress" style="margin-top:14px;">
                    <div class="teach-progress-fill" style="width:{pct_complete}%"></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        for idx, msg in enumerate(st.session_state.messages):
            avatar = "👤" if msg["role"] == "user" else "🎓"
            with st.chat_message(msg["role"], avatar=avatar):
                if msg["role"] == "assistant":
                    display_message(msg["content"])
                else:
                    st.markdown(msg["content"])

        if not st.session_state.messages:
            reset_to_home()
            st.rerun()

        latest_msg = st.session_state.messages[-1]

        if latest_msg["role"] == "user":
            with st.chat_message("assistant"):
                completed = (
                    ", ".join(st.session_state.completed_sections)
                    if st.session_state.completed_sections
                    else "None"
                )
                current = current_sect

                is_final_section = current_sect_index >= len(sections) - 1
                final_instructions = ""
                if is_final_section:
                    final_instructions += "\n\nConclude by asking the student a thought-provoking challenge question!"
                if current_sect_index == 0:
                    final_instructions += "\n\nCRITICAL: Start your response with an obscure, mind-bending fact or 'aura' fact about the topic that will completely hook the student. Make it bold."


                is_initial_teaching = (
                    latest_msg["content"].startswith("Great! Now please teach me")
                    or latest_msg["content"].startswith("Please teach me about:")
                    or latest_msg["content"].startswith("Welcome back!")
                    or latest_msg["content"].startswith("I've returned!")
                )
                is_doubt = not is_initial_teaching

                is_resume = latest_msg["content"].startswith(
                    "Welcome back!"
                ) or latest_msg["content"].startswith("I've returned!")

                if is_doubt:
                    system_prompt = (
                        PROFESSOR_PERSONALITY
                        + "\n"
                        + f"Topic: {st.session_state.topic}\n"
                        + f"You have just taught this topic to the user. This is their doubt: {latest_msg['content']}\n"
                        + "Provide a clear, engaging, and insightful answer, maintaining your persona."
                        + final_instructions
                    )
                elif is_resume:
                    system_prompt = (
                        PROFESSOR_PERSONALITY
                        + "\n"
                        + f"Expertise Context: {EXPERTISE_LEVELS.get(st.session_state.expertise_level, '')}\n"
                        + RESUME_PROMPT_TEMPLATE.replace(
                            "{topic}", st.session_state.topic
                        )
                        .replace("{completed}", completed)
                        .replace("{current}", current)
                        .replace(
                            "{syllabus}",
                            extract_thinking(st.session_state.syllabus_raw)[1],
                        )
                        + final_instructions
                    )
                else:
                    system_prompt = (
                        PROFESSOR_PERSONALITY
                        + "\n"
                        + f"Expertise Context: {EXPERTISE_LEVELS.get(st.session_state.expertise_level, '')}\n"
                        + extract_thinking(st.session_state.syllabus_raw)[1]
                        + "\n\n"
                        + TEACHING_PROMPT_TEMPLATE.replace(
                            "{topic}", st.session_state.topic
                        ).replace("{section}", current_sect)
                        + final_instructions
                    )

                stream_gen = generate_response_stream(
                    st.session_state.messages,
                    system_prompt,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    top_p=top_p,
                )
                final_response = process_stream_ui(stream_gen)
                st.session_state.messages.append(
                    {"role": "assistant", "content": final_response}
                )
                st.rerun()

        st.divider()

        if "doubts_asked" not in st.session_state:
            st.session_state.doubts_asked = 0

        if not is_waiting_for_model:
            if current_sect_index < len(sections) - 1:
                next_sect = sections[current_sect_index + 1]

                # Doubt counter
                doubts_remaining = 3 - st.session_state.doubts_asked
                st.markdown(
                    f"""
                    <div style="display:flex;align-items:center;justify-content:space-between;
                                margin-bottom:12px;">
                        <div class="doubt-badge">💬 {doubts_remaining} doubt{'s' if doubts_remaining!=1 else ''} remaining</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                if st.button(
                    f"Next Section: {next_sect[:40]}{'…' if len(next_sect)>40 else ''}  →",
                    use_container_width=True,
                ):
                    if current_sect not in st.session_state.completed_sections:
                        st.session_state.completed_sections.append(current_sect)
                    save_progress_checkpoint()
                    st.session_state.current_section += 1
                    st.session_state.doubts_asked = 0
                    st.session_state.messages = [
                        {
                            "role": "user",
                            "content": f"Great! Now please teach me the next section: {next_sect}",
                        }
                    ]
                    st.rerun()

                if st.session_state.doubts_asked < 3:
                    if doubt := st.chat_input(
                        f"Ask a doubt about '{current_sect[:30]}' ({st.session_state.doubts_asked}/3 used)…"
                    ):
                        st.session_state.doubts_asked += 1
                        st.session_state.messages.append(
                            {"role": "user", "content": doubt}
                        )
                        st.rerun()
                else:
                    st.markdown(
                        """
                        <div style="background:rgba(201,162,39,0.08);border:1px solid rgba(201,162,39,0.2);
                                    border-radius:10px;padding:14px 18px;text-align:center;">
                            <span style="font-size:15px;color:#c9a227;">💡 You've used all 3 doubts for this section.</span><br>
                            <span style="font-size:13px;color:#6b7b8c;">Proceed to the next section to continue your journey.</span>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
            else:
                if current_sect not in st.session_state.completed_sections:
                    st.session_state.completed_sections.append(current_sect)
                save_progress_checkpoint()
                st.markdown(
                    """
                    <div style="text-align:center;padding:2rem 1rem;
                                background:linear-gradient(135deg,rgba(201,162,39,0.08),rgba(201,162,39,0.02));
                                border:1px solid rgba(201,162,39,0.2);border-radius:16px;margin-top:16px;">
                        <div style="font-size:52px;margin-bottom:12px;">🎓</div>
                        <h3 style="font-family:'Playfair Display',serif;color:#e8d5b7;
                                   font-size:1.6rem;margin:0 0 8px;">Course Complete!</h3>
                        <p style="color:#6b7b8c;font-size:14px;max-width:340px;margin:0 auto;">You've finished every section.
                            Feel free to ask any remaining questions below.</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if doubt := st.chat_input("Any final questions?…"):
                    st.session_state.messages.append({"role": "user", "content": doubt})
                    st.rerun()


if __name__ == "__main__":
    main()
