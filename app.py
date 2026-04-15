"""Local LLM Chat Interface with Code Execution"""

import streamlit as st
import os
import re
import signal
import subprocess
import threading
from llama_cpp import Llama

st.set_page_config(page_title="Local LLM Chat", page_icon="🤖", layout="wide")

MODEL_PATH = r"C:\Users\SAMAY\Desktop\llms\Qwen3.5-4B.Q4_K_M.gguf"
WORKSPACE = "./llm_workspace/"

os.makedirs(WORKSPACE, exist_ok=True)

TIMEOUT_SECONDS = 10


@st.cache_resource
def load_model():
    if not os.path.exists(MODEL_PATH):
        st.error(f"Model not found at: {MODEL_PATH}")
        st.stop()

    return Llama(
        model_path=MODEL_PATH,
        n_ctx=16384,
        n_threads=4,
        n_gpu_layers=35,
        use_mlock=True,
        verbose=False,
    )


class ExecutionTimeout(Exception):
    pass


def timeout_handler(signum, frame):
    raise ExecutionTimeout("Code execution timed out")


def execute_python(code, workspace=WORKSPACE):
    import sys
    import io

    output = {"stdout": "", "error": ""}

    if not os.path.exists(workspace):
        os.makedirs(workspace, exist_ok=True)

    original_dir = os.getcwd()

    # Fix paths - we're running in workspace directory, so strip './llm_workspace/'
    exec_code = code.replace("./llm_workspace/", "")
    exec_code = exec_code.replace("./workspace/", "")

    def run_code():
        old_stdout = sys.stdout
        captured = io.StringIO()
        try:
            sys.stdout = captured
            exec_globals = {"__name__": "__main__", "workspace": workspace}
            exec(exec_code, exec_globals)
            output["stdout"] = captured.getvalue()
        except ExecutionTimeout:
            output["error"] = "Execution timed out (10 second limit)"
        except Exception as e:
            output["error"] = str(e)
        finally:
            sys.stdout = old_stdout

    os.chdir(workspace)

    thread = threading.Thread(target=run_code)
    thread.start()
    thread.join(timeout=TIMEOUT_SECONDS)

    os.chdir(original_dir)

    if thread.is_alive():
        output["error"] = "Execution timed out (10 second limit)"

    return output


PROFESSOR_PROMPT = """You are a highly knowledgeable and engaging university professor. You explain complex topics in a clear, structured, and easy-to-understand manner. Your teaching style is:

1. **Clear Explanations**: Break down complex concepts into simple, digestible parts
2. **Real-world Examples**: Use practical examples to illustrate abstract concepts
3. **Structured Approach**: Organize your answers with proper headings, bullet points, and numbered lists when appropriate
4. **Encouraging**: Be supportive and patient, encouraging curiosity and further learning
5. **Accurate**: Provide factually correct information and acknowledge limitations when uncertain

IMPORTANT - Code Execution Tool:
You have access to a Python code execution environment. You can use it to:
- Write and save code files (text, python, markdown, json, etc.)
- Read files
- Execute Python code and show results
- Save checkpoints or notes
- Create and manage files in your workspace

To execute code, write it between special markers:
```python
# Your code here
```

The code will run with:
- 10 second timeout
- Files are saved to ./llm_workspace/
- IMPORTANT: Use simple filenames like "square.py", NOT "./llm_workspace/square.py"
- Use just: open("myfile.py", "w") - NOT open("./llm_workspace/myfile.py", "w")
- Standard output captured and displayed

For file operations, use Python's open() function with relative paths (files are in ./llm_workspace/)

Use this tool whenever it helps explain concepts, run examples, or save information."""


def format_prompt(messages):
    prompt = ""
    prompt += f"<|im_start|>system\n{PROFESSOR_PROMPT}<|im_end|>\n"

    for msg in messages:
        role = msg["role"]
        content = msg["content"]
        if role == "user":
            prompt += f"<|im_start|>user\n{content}<|im_end|>\n"
        elif role == "assistant":
            prompt += f"<|im_start|>assistant\n{content}<|im_end|>\n"

    prompt += "<|im_start|>assistant\n"
    return prompt


def generate_response_stream(
    llm, messages, max_tokens=512, temperature=0.7, top_p=0.95
):
    prompt = format_prompt(messages)
    try:
        stream = llm(
            prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            stop=["<|im_end|>", "<|endoftext|>"],
            echo=False,
            stream=True,
        )
        full_response = ""
        for chunk in stream:
            token = chunk["choices"][0]["text"]
            full_response += token
            yield token, full_response
    except Exception as e:
        yield "", f"Error generating response: {str(e)}"


def extract_thinking(text):
    think_start = "<think>"
    think_end = "</think>"
    if think_start in text and think_end in text:
        s = text.find(think_start)
        e = text.find(think_end)
        if e > s:
            thinking = text[s + len(think_start) : e]
            answer = text[e + len(think_end) :]
            return thinking.strip(), answer.strip()
    return None, text


def clean_thinking(thinking):
    if not thinking:
        return thinking

    intro_patterns = [
        r"(?i)^let me think.*?(?:about|through|of).*?\.\s*",
        r"(?i)^i need to think.*?about.*?\.\s*",
        r"(?i)^the user is asking.*?(?:\.|$)",
        r"(?i)^they've provided.*?(?:\.|$)",
        r"(?i)^they also want.*?(?:\.|$)",
        r"(?i)^they want me.*?(?:\.|$)",
    ]

    cleaned = thinking
    for pattern in intro_patterns:
        cleaned = re.sub(pattern, "", cleaned, flags=re.DOTALL).strip()

    return cleaned


def extract_code_blocks(text):
    pattern = r"```python\n(.*?)```"
    return re.findall(pattern, text, re.DOTALL)


def execute_code_blocks(text):
    code_blocks = extract_code_blocks(text)
    if not code_blocks:
        return text

    results = []
    for i, code in enumerate(code_blocks):
        result = execute_python(code)
        output = ""
        if result["stdout"]:
            output = f"**Output {i + 1}:**\n```\n{result['stdout']}```"
        elif result["error"]:
            output = f"**Error {i + 1}:**\n```\n{result['error']}```"
        if output:
            results.append(output)

    if results:
        return text + "\n\n" + "\n\n".join(results)
    return text


def main():
    st.title("🤖 Local LLM Chat with Code Execution")
    st.caption(
        f"Model: Qwen3.5-4B | Code Timeout: {TIMEOUT_SECONDS}s | Workspace: {WORKSPACE}"
    )

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "model" not in st.session_state:
        with st.spinner("Loading model..."):
            try:
                st.session_state.model = load_model()
                st.success("Model loaded!")
            except Exception as e:
                st.error(f"Failed: {str(e)}")
                return

    with st.sidebar:
        st.header("Settings")
        temperature = st.slider("Temperature", 0.0, 2.0, 0.7, 0.1)
        max_tokens = st.slider("Max Tokens", 128, 2048, 512, 64)
        top_p = st.slider("Top P", 0.0, 1.0, 0.95, 0.05)

        if st.button("Clear Chat"):
            st.session_state.messages = []
            st.rerun()

        st.divider()
        st.subheader("Workspace Files")
        if os.path.exists(WORKSPACE):
            files = os.listdir(WORKSPACE)
            if files:
                for f in files:
                    st.text(f"📄 {f}")
            else:
                st.caption("No files yet")
        else:
            st.caption("Workspace not created")

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            _, text = extract_thinking(msg["content"])
            st.markdown(text)

    if prompt := st.chat_input("Type your message..."):
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("assistant"):
            with st.expander("Thinking", expanded=True):
                thinking_area = st.empty()

            response_area = st.empty()
            full_response = ""
            in_thinking = False

            for token, full in generate_response_stream(
                st.session_state.model,
                st.session_state.messages,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
            ):
                full_response = full

                start = full.find("<think>")
                end = full.find("</think>")

                if start != -1 and end == -1:
                    in_thinking = True
                    current_thinking = clean_thinking(full[start + 8 :])
                    thinking_area.markdown(current_thinking)
                    response_area.markdown("")
                elif start != -1 and end != -1:
                    if in_thinking:
                        current_thinking = clean_thinking(full[start + 8 : end])
                        answer = full[end + 4 :]
                        thinking_area.markdown(current_thinking)
                        response_area.markdown(answer)
                        in_thinking = False
                    else:
                        thinking, answer = extract_thinking(full)
                        if thinking:
                            thinking_area.markdown(clean_thinking(thinking))
                            response_area.markdown(answer)
                        else:
                            response_area.markdown(full)
                else:
                    if in_thinking:
                        response_area.markdown(full)
                    else:
                        thinking, answer = extract_thinking(full)
                        if thinking:
                            thinking_area.markdown(clean_thinking(thinking))
                            response_area.markdown(answer)
                        else:
                            response_area.markdown(full)

            thinking, clean_response = extract_thinking(full_response)
            if thinking:
                thinking_area.markdown(clean_thinking(thinking))
                response_area.markdown(clean_response)

            final_response = clean_response if clean_response else full_response
            final_response = execute_code_blocks(final_response)
            response_area.markdown(final_response)

        st.session_state.messages.append(
            {"role": "assistant", "content": final_response}
        )


if __name__ == "__main__":
    main()
