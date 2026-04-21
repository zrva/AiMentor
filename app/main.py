"""Local LLM Professor Teaching Interface"""

import streamlit as st
import os
import re
import time
import glob
import requests
import json
import html
from datetime import datetime

st.set_page_config(page_title="AiMentor", page_icon="📚", layout="wide")

CUSTOM_CSS = """
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;600;700&family=Source+Sans+3:wght@300;400;500;600&display=swap" rel="stylesheet">
<style>
    /* Professor AI Dark Theme - Navy with Gold */
    
    /* Main Background - Navy Dark */
    [data-testid="stAppViewContainer"] {
        background-color: #0B162C !important;
    }
    [data-testid="stHeader"] {
        background-color: #0D1B2A !important;
        border-bottom: 1px solid #1E3A5F !important;
    }
    [data-testid="stSidebar"] {
        background-color: #0D1B2A !important;
        border-right: 1px solid #1E3A5F !important;
    }
    
    /* Sidebar toggle */
    [data-testid="collapsedControl"] svg, [data-testid="stSidebar"] button svg {
        color: #E8D5B7 !important;
        fill: #E8D5B7 !important;
    }
    
    /* Global Text Colors - Cream */
    h1, h2, h3 {
        color: #E8D5B7 !important;
        font-family: 'Playfair Display', 'Georgia', serif !important;
    }
    h4, h5, h6 {
        color: #E8D5B7 !important;
        font-family: 'Playfair Display', serif !important;
    }
    p, li, span, label, div {
        color: #C9B896 !important;
    }
    
    /* Links - Gold */
    a {
        color: #C9A227 !important;
    }
    
    /* Buttons - Gold */
    [data-testid="stButton"] button {
        background: linear-gradient(135deg, #C9A227 0%, #B8962F 100%) !important;
        border: none !important;
        color: #0B162C !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-family: 'Source Sans 3', sans-serif !important;
        transition: all 0.2s ease-in-out;
    }
    [data-testid="stButton"] button:hover {
        background: linear-gradient(135deg, #D4AF37 0%, #C9A227 100%) !important;
        box-shadow: 0 4px 12px rgba(201, 162, 39, 0.3) !important;
    }
    [data-testid="stButton"] button:focus {
        outline: 2px solid #C9A227 !important;
        outline-offset: 2px;
    }
    
    /* Input Fields */
    [data-testid="stTextInput"] input, [data-testid="stChatInput"] input, [data-testid="stChatInput"] textarea {
        background-color: #1E3A5F !important;
        color: #E8D5B7 !important;
        border: 1px solid #2D4A6F !important;
        border-radius: 8px !important;
        font-family: 'Source Sans 3', sans-serif !important;
    }
    [data-testid="stTextInput"] input:focus, [data-testid="stChatInput"] textarea:focus {
        border-color: #C9A227 !important;
        box-shadow: 0 0 0 2px rgba(201, 162, 39, 0.2) !important;
    }
    [data-testid="stTextInput"] input::placeholder, [data-testid="stChatInput"] input::placeholder, [data-testid="stChatInput"] textarea::placeholder {
        color: #6B7B8C !important;
    }
    
    /* Thinking Block */
    details {
        background-color: #1E3A5F !important;
        border: 1px solid #2D4A6F !important;
        padding: 12px;
        border-radius: 8px;
    }
    details summary {
        color: #C9A227 !important;
        font-weight: 500;
        font-family: 'Playfair Display', serif !important;
    }
    
    /* Code blocks */
    .stCodeBlock > div {
        background-color: #0D1B2A !important;
        border: 1px solid #2D4A6F !important;
        border-radius: 8px;
    }
    
    /* Streamlit dividers */
    [data-testid="stDivider"] {
        border-top: 1px solid #2D4A6F !important;
    }
    
    /* Form containers */
    [data-testid="stForm"] {
        background-color: #0D1B2A !important;
        border: 1px solid #1E3A5F !important;
        border-radius: 12px !important;
        padding: 24px !important;
    }
    
    /* Progress bar */
    [data-testid="stProgress"] > div > div {
        background: linear-gradient(90deg, #C9A227, #D4AF37) !important;
    }
    [data-testid="stProgress"] > div {
        background-color: #1E3A5F !important;
    }
    
    /* Radio buttons - Expertise selector alignment */
    [data-testid="stRadio"] > div {
        display: flex !important;
        justify-content: flex-start !important;
        gap: 8px !important;
    }
    [data-testid="stRadio"] div[role="radiogroup"] {
        display: flex !important;
        flex-direction: row !important;
        justify-content: flex-start !important;
        width: 100% !important;
    }
    [data-testid="stRadio"] div[role="radiogroup"] > label {
        color: #C9B896 !important;
        flex: 1 1 0 !important;
        text-align: left !important;
        margin: 0 !important;
        padding: 10px 12px !important;
        min-width: 0 !important;
        display: flex !important;
        justify-content: flex-start !important;
        align-items: center !important;
    }
    [data-testid="stRadio"] div[role="radiogroup"] > label span {
        display: block !important;
        text-align: left !important;
    }
    [data-testid="stRadio"] div[role="radiogroup"] > label p {
        text-align: left !important;
        margin: 0 !important;
    }
    [data-testid="stRadio"] div[role="radiogroup"] > label:has(input:checked) {
        background-color: rgba(201, 162, 39, 0.2) !important;
        border-radius: 6px;
    }
    [data-testid="stRadio"] div[role="radiogroup"] label input {
        position: relative !important;
        z-index: 1 !important;
        pointer-events: auto !important;
    }
    
    /* Toasts */
    [data-testid="stToast"] {
        border-left: 4px solid #C9A227 !important;
    }
    
    /* Streamlit containers - max-width for scaling */
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 1.5rem !important;
        max-width: 900px !important;
    }
    
    /* Chat message styling - target inner content for proper text alignment */
    [data-testid="stChatMessage"] {
        background-color: #1E3A5F !important;
        border-radius: 12px !important;
        padding: 0 !important;
    }
    [data-testid="stChatMessageContent"] {
        background-color: #1E3A5F !important;
        border-radius: 12px !important;
        padding: 12px 16px !important;
        text-align: left !important;
    }
    
    /* Tabs */
    [data-testid="stTabs"] button[aria-selected="true"] {
        color: #C9A227 !important;
        border-bottom: 2px solid #C9A227 !important;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

WORKSPACE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "llm_workspace")

os.makedirs(WORKSPACE, exist_ok=True)

SERVER_PORT = 8080
_env_base = os.environ.get("LLM_API_BASE", "")
SERVER_URL = _env_base.rstrip("/") if _env_base else f"http://localhost:{SERVER_PORT}"
CONFIG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config")
GPU_TYPE_FILE = os.path.join(CONFIG_DIR, ".gpu_type")


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
            "max_tokens": 384,
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
        is_bold_header = clean_line.startswith("**") and not re.match(
            r"^\*\*(.+?)\*\*:", clean_line
        )

        if is_explicit_header or is_bold_header:
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
Create a learning path for {topic}.

Start with a surprising fact (use Markdown **bold** or `###` large headings) that pulls the user in - NO labels like "Hook:"

Format the path with interesting topic-specific headings. Use strict Markdown headers (`### Section Title`) and bold bullet points (`- **Subtopic:**`) so it renders beautifully. (NOT generic "Index" or "Table of Contents")
Ensure the names of subtopics are very short and concise (1-4 words max).

Be mindful:
- Curiosity-sparking titles that make them want to click
- Balance length: NOT too long they lose motivation, NOT too short they learn nothing
- You expand on each topic when teaching - this is just the roadmap

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


def save_free_chat():
    """Save free chat conversation to md file"""
    if not st.session_state.get("free_chat_msgs"):
        return
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    lines = ["# Free Chat Conversation", "", "## Messages"]
    for msg in st.session_state.free_chat_msgs:
        role_label = "User" if msg["role"] == "user" else "Assistant"
        lines.extend(["", f"### {role_label}", "", msg["content"]])
    content = "\n".join(lines)
    filename = f"freechat_{timestamp}.md"
    try:
        with open(os.path.join(WORKSPACE, filename), "w", encoding="utf-8") as f:
            f.write(content)
        return filename
    except Exception:
        return None


def restore_free_chat(filename):
    """Restore free chat from saved md file"""
    filepath = os.path.join(WORKSPACE, filename)
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        lines = content.split("\n")
        msgs = []
        current_role = None
        current_content = []
        for line in lines:
            if line.startswith("### User"):
                if current_role and current_content:
                    msgs.append(
                        {
                            "role": current_role,
                            "content": "\n".join(current_content).strip(),
                        }
                    )
                current_role = "user"
                current_content = []
            elif line.startswith("### Assistant"):
                if current_role and current_content:
                    msgs.append(
                        {
                            "role": current_role,
                            "content": "\n".join(current_content).strip(),
                        }
                    )
                current_role = "assistant"
                current_content = []
            elif line.startswith("# ") or line.startswith("## "):
                continue
            else:
                current_content.append(line)
        if current_role and current_content:
            msgs.append(
                {"role": current_role, "content": "\n".join(current_content).strip()}
            )
        st.session_state.free_chat_msgs = msgs
    except Exception:
        st.toast("⚠️ Failed to restore chat.", icon="⚠️")


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
    st.markdown(
        """
        <style>
            .reportview-container {
                margin-top: -2em;
            }
            #MainMenu {visibility: hidden;}
            .stAppDeployButton {display:none;}
            footer {visibility: hidden;}
            #stDecoration {display:none;}

            /* Input Fields - Light Theme */
            div[data-baseweb="input"] > div {
                border: 1px solid #E5E5E5 !important;
                background-color: #FFFFFF !important;
                border-radius: 8px !important;
            }
            div[data-baseweb="input"] > div:focus-within {
                border-color: #D4AF37 !important;
                box-shadow: 0 0 0 2px rgba(212, 175, 55, 0.1) !important;
            }
            
            /* Chat Input Bar */
            [data-testid="stChatInput"] {
                border: 1px solid #2D4A6F !important;
                background-color: #1E3A5F !important;
                border-radius: 8px !important;
            }
            [data-testid="stChatInput"]:focus-within {
                border-color: #C9A227 !important;
                box-shadow: 0 0 0 2px rgba(201, 162, 39, 0.2) !important;
            }
            
            /* Form Container */
            [data-testid="stForm"] {
                background-color: #0D1B2A !important;
                border: 1px solid #1E3A5F !important;
                border-radius: 12px !important;
                padding: 24px !important;
            }
        </style>
    """,
        unsafe_allow_html=True,
    )

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

    st.title("🤖 AiMentor")
    st.caption(
        f"Active Workspace: {WORKSPACE} | Model Engine: {active_model if active_model else 'Offline'}"
    )

    if "phase" not in st.session_state:
        reset_to_home()

    if not active_model:
        st.warning(
            f"⚠️ **AI Engine Offline:** Please boot your AI Backend (e.g. `llama-server`) on port {SERVER_PORT} to connect!"
        )

    with st.sidebar:
        st.header("Settings")
        app_mode = st.radio(
            "Application Mode", ["📚 Structured Course", "💬 Free Chat"]
        )

        # Fixed reasoning boundaries tuned to the selected runtime profile
        max_tokens = runtime_profile["max_tokens"]
        temperature = runtime_profile["temperature"]
        top_p = runtime_profile["top_p"]

        if runtime_profile["gpu_type"] == "cpu":
            st.caption(
                "CPU mode: reduced output budget for lower memory use and faster replies."
            )

        if st.button("🏠 Home / Clear Chat", use_container_width=True):
            reset_to_home()
            if "free_chat_msgs" in st.session_state:
                st.session_state.free_chat_msgs = []
            st.rerun()

        st.divider()
        if app_mode == "📚 Structured Course":
            st.subheader("🗺️ Learning Path")

            if (
                "syllabus_parsed" not in st.session_state
                or not st.session_state.syllabus_parsed
            ):
                st.caption("Your path will appear here once the syllabus generates.")
            else:
                _, clean_text = extract_thinking(st.session_state.syllabus_raw)
                structure = parse_syllabus_structure(clean_text)

                for i, sect_dict in enumerate(structure):
                    is_completed = i < st.session_state.current_section
                    is_current = i == st.session_state.current_section

                    if is_completed:
                        st.markdown(f"**✅ {sect_dict['title']}**")
                        for sub in sect_dict["subtopics"]:
                            st.caption(f"&nbsp;&nbsp;✓ {sub}", unsafe_allow_html=True)
                    elif is_current:
                        st.markdown(f"**🟢 {sect_dict['title']}**")
                        for sub in sect_dict["subtopics"]:
                            st.caption(f"&nbsp;&nbsp;▶ {sub}", unsafe_allow_html=True)
                    else:
                        st.markdown(f"**🔒 ~{sect_dict['title']}~**")

    # Flow Control
    is_waiting_for_model = (
        len(st.session_state.messages) > 0
        and st.session_state.messages[-1]["role"] == "user"
    )

    if app_mode == "💬 Free Chat":
        st.markdown("### 💬 Free Chat Mode")
        st.caption("Discuss topics directly with the AI without structured milestones.")

        if "free_chat_msgs" not in st.session_state:
            st.session_state.free_chat_msgs = []

        past_chats = glob.glob(os.path.join(WORKSPACE, "freechat_*.md"))
        if past_chats and len(st.session_state.free_chat_msgs) == 0:
            st.markdown("**Past Conversations:**")
            past_cols = st.columns(3)
            for idx, chat_file in enumerate(
                sorted(past_chats, key=os.path.getmtime, reverse=True)[:3]
            ):
                basename = os.path.basename(chat_file)
                date_str = basename.replace("freechat_", "").replace(".md", "")
                try:
                    date_fmt = datetime.strptime(date_str, "%Y%m%d_%H%M%S").strftime(
                        "%b %d, %H:%M"
                    )
                except Exception:
                    date_fmt = date_str
                with past_cols[idx % 3]:
                    if st.button(
                        f"💬 {date_fmt}",
                        key=f"restore_{basename}",
                        use_container_width=True,
                    ):
                        restore_free_chat(basename)
                        st.rerun()
            st.divider()

        for msg in st.session_state.free_chat_msgs:
            with st.chat_message(msg["role"]):
                if msg["role"] == "assistant":
                    display_message(msg["content"])
                else:
                    st.markdown(msg["content"])

        is_chat_wait = (
            len(st.session_state.free_chat_msgs) > 0
            and st.session_state.free_chat_msgs[-1]["role"] == "user"
        )

        if prompt := st.chat_input("Type your message...", disabled=is_chat_wait):
            st.session_state.free_chat_msgs.append({"role": "user", "content": prompt})
            # Cap free chat history to prevent unbounded growth
            if len(st.session_state.free_chat_msgs) > 40:
                st.session_state.free_chat_msgs = st.session_state.free_chat_msgs[-40:]
            st.rerun()

        if is_chat_wait:
            with st.chat_message("assistant"):
                sys_tmp = (
                    PROFESSOR_PERSONALITY
                    + "\n\nStrong opinions - share them freely. Don't be neutral."
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
                save_free_chat()
                st.rerun()
        return

    home_placeholder = st.empty()
    if st.session_state.phase == "home":
        with home_placeholder.container():
            st.markdown("### What would you like to learn today?")

            expertise_select = st.radio(
                "What is your current expertise level on this topic?",
                list(EXPERTISE_LEVELS.keys()),
                horizontal=True,
            )

            with st.form("topic_entry"):
                prompt = st.text_input(
                    "Enter a topic (e.g., Quantum Computing, Python Web Scraping)..."
                )
                submitted = st.form_submit_button(
                    "Start Learning", use_container_width=True
                )
                if submitted and prompt:
                    # Guard: detect greetings / chitchat instead of real topics
                    greeting_patterns = [
                        "hi",
                        "hello",
                        "hey",
                        "hii",
                        "hiii",
                        "yo",
                        "sup",
                        "who are you",
                        "what are you",
                        "how are you",
                        "whats up",
                        "what's up",
                        "good morning",
                        "good evening",
                        "good night",
                        "thanks",
                        "thank you",
                        "bye",
                        "goodbye",
                    ]
                    cleaned = prompt.strip().lower().rstrip("!?.,")
                    if cleaned in greeting_patterns:
                        st.warning(
                            "👋 That looks like a greeting! Switch to **💬 Free Chat** "
                            "mode in the sidebar to have open conversations. "
                            "Please enter a valid topic you'd like to explore and learn."
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

            checkpoints = glob.glob(os.path.join(WORKSPACE, "syllabus_*.md"))
            if checkpoints:
                st.markdown("### Continue from where you left off:")

                # Display responsive grid layout for resume buttons
                cols = st.columns(3)
                for idx, ckpt in enumerate(checkpoints):
                    basename = os.path.basename(ckpt)
                    title_guess = (
                        basename.replace("syllabus_", "")
                        .replace(".md", "")
                        .replace("_", " ")
                        .title()
                    )

                    with cols[idx % 3]:
                        if st.button(
                            f"🔄 Resume: {title_guess}",
                            key=ckpt,
                            use_container_width=True,
                        ):
                            home_placeholder.empty()
                            restore_progress_checkpoint(basename)
                            st.rerun()

    elif st.session_state.phase == "generating_syllabus":
        st.markdown(f"### Generating syllabus for: **{st.session_state.topic}**")
        with st.chat_message("user"):
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
        st.markdown(f"### Syllabus: **{st.session_state.topic}**")
        with st.chat_message("user"):
            st.markdown(st.session_state.topic)

        with st.chat_message("assistant"):
            display_message(st.session_state.syllabus_raw)

        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button(
                "🖊️ Edit", use_container_width=True, disabled=is_waiting_for_model
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
                f"▶️ Continue ({first_sect})",
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
            if st.button("🗑️ Clear Input", use_container_width=True):
                reset_to_home()
                st.rerun()

    elif st.session_state.phase == "editing_syllabus":
        st.markdown(f"### Syllabus: **{st.session_state.topic}**")
        with st.chat_message("assistant"):
            display_message(st.session_state.syllabus_raw)

        if edit_prompt := st.chat_input("Tell me what to add or remove..."):
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

        st.markdown(f"### Teaching: {current_sect}")

        for idx, msg in enumerate(st.session_state.messages):
            with st.chat_message(msg["role"]):
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
                    final_instructions = "\n\nConclude by asking the student a thought-provoking challenge question!"

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

                if st.button(f"▶️ Next Section: {next_sect}", use_container_width=True):
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
                        f"Type your doubt ({st.session_state.doubts_asked}/3 used)..."
                    ):
                        st.session_state.doubts_asked += 1
                        st.session_state.messages.append(
                            {"role": "user", "content": doubt}
                        )
                        st.rerun()
                else:
                    st.info(
                        "⚠️ You've reached the 3-doubt limit for this section! Please proceed to the next section to continue your path."
                    )
            else:
                if current_sect not in st.session_state.completed_sections:
                    st.session_state.completed_sections.append(current_sect)
                save_progress_checkpoint()
                st.success("Course Completed!")
                if doubt := st.chat_input("Type your final doubts here..."):
                    st.session_state.messages.append({"role": "user", "content": doubt})
                    st.rerun()


if __name__ == "__main__":
    main()
