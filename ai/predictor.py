import ast
import json
import logging
import urllib.request
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

OLLAMA_API = "http://localhost:11434/api/generate"
MODEL = "llama2"


def _check_python_errors(code: str) -> str | None:
    """Use Python's own parser to detect syntax errors instantly."""
    try:
        ast.parse(code)
        return None
    except IndentationError as e:
        return f"IndentationError on line {e.lineno}: {e.msg}"
    except SyntaxError as e:
        msg = e.msg
        if "expected ':'" in msg:
            msg = "missing colon (':')"
        elif "unexpected EOF" in msg:
            msg = "unexpected end of file (missing parenthesis or block?)"
        elif "invalid syntax" in msg:
            msg = "invalid syntax"
            
        return f"SyntaxError on line {e.lineno}: {msg}"


def _get_error_line(code: str, lineno: int) -> str:
    """Extract the problematic line from the code."""
    lines = code.split("\n")
    if 0 < lineno <= len(lines):
        return lines[lineno - 1].strip()
    return ""


def predict_prompt(context: str) -> str:
    """
    Smart prediction based on FULL activity context:
    1. If Python code has errors -> instant specific fix prompts
    2. Otherwise -> LLM analyzes full activity timeline to predict intent
    """
    # Try to extract code from context
    lines = context.split("\n")
    filename = ""
    code_lines = []
    reading_code = False
    
    for line in lines:
        if line.startswith("Currently editing:"):
            filename = line.replace("Currently editing:", "").strip()
        elif line.strip() == "Code:":
            reading_code = True
        elif reading_code:
            code_lines.append(line)
    
    code = "\n".join(code_lines).strip()
    
    # ====== Python error detection (INSTANT) ======
    if code and filename.endswith(".py"):
        error = _check_python_errors(code)
        if error:
            try:
                lineno = int(error.split("line ")[1].split(":")[0])
                bad_line = _get_error_line(code, lineno)
            except (ValueError, IndexError):
                lineno = 0
                bad_line = ""
            
            logging.info(f"Python error detected: {error}")
            prompts = []
            prompts.append(f"Fix this Python error: {error}")
            if bad_line:
                prompts.append(f"What is wrong with this line: `{bad_line}` ?")
                prompts.append(f"I have a {error} in {filename}. The problematic code is: {bad_line}")
            else:
                prompts.append(f"Debug this Python file: {filename}")
                prompts.append(f"How to fix {error}?")
            return "\n".join(f"{i+1}. {p}" for i, p in enumerate(prompts))
    
    # ====== LLM-based prediction from activity timeline ======
    return _predict_from_activity(context)


def _predict_from_activity(context: str) -> str:
    """Use LLM to analyze the user's full activity timeline and predict intent."""
    prompt = f"""You are a smart prompt prediction tool. Analyze the developer's recent activity timeline below and predict exactly 3 short prompts they are most likely going to ask an AI assistant next.

CRITICAL RULES:
1. Heavily prioritize the MOST RECENT activities at the bottom of the timeline.
2. If they just searched Google for something (like "apple" or "grapes") or watched a YouTube video, the prompts MUST be related to that topic!
3. If they just edited a file, suggest a prompt about debugging or explaining that file.
4. Output ONLY 3 numbered prompts. Do not include any conversational text.

Activity Timeline:
{context.strip()[:800]}

Output ONLY 3 numbered prompts:"""

    return _call_ollama(prompt)


def _call_ollama(prompt: str) -> str:
    """Call Ollama API and return the response."""
    try:
        logging.info("Calling Ollama API for prediction...")
        
        payload = json.dumps({
            "model": MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_predict": 150,
                "temperature": 0.7
            }
        }).encode("utf-8")
        
        req = urllib.request.Request(
            OLLAMA_API,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        
        with urllib.request.urlopen(req, timeout=60) as response:
            result = json.loads(response.read().decode("utf-8"))
            output = result.get("response", "").strip()
        
        if output:
            logging.info("Prediction generated successfully.")
            return output
        
        return "1. How do I fix this bug?\n2. Explain this code\n3. How can I optimize this?"
        
    except Exception as e:
        logging.error(f"Prediction error: {e}")
        return "1. How do I fix this bug?\n2. Explain this code\n3. How can I optimize this?"
