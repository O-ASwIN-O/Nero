# Nero-AI - Full Activity Prompt Predictor

Nero is a background AI assistant that quietly monitors your development activity and **pre-generates the prompts** you are most likely to ask a global LLM (like ChatGPT, Claude, or Gemini).
Instead of typing out long context, Nero instantly gives you precise prompts combined with your actual code the second you open an AI chat site!

## 🚀 Features
- **Comprehensive Activity Tracking:** Monitors your Google searches, Stack Overflow reads, YouTube videos, and active VS Code files.
- **Global Code File Monitoring:** Watches all your hard drives (C:\, D:\, etc.) for code edits.
- **Instant Python Syntax Checking:** Analyzes Python errors instantly and translates cryptic AST errors into plain English.
- **Context-Aware Prompts:** Uses `llama2` (or your preferred local Ollama model) to predict exactly what you are about to ask.
- **Rich Clipboard Support:** The "Copy to Clipboard" button grabs **both the generated prompt AND your buggy code/context**, so you can instantly paste it into ChatGPT with zero effort!

## 🛠️ Requirements

1. **Python 3.10+**
2. **Ollama**: Download from [ollama.com](https://ollama.com) and keep it running in the background.

## 📦 Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/O-ASwIN-O/Nero.git
   cd Nero/nero-ai
   ```
2. Pull the initial LLM model (`llama2` or `qwen2.5`):
   ```bash
   ollama run llama2
   ```
3. Install the required Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## 🏃 Usage
Simply run `main.py` in your terminal or command prompt (make sure your Conda/venv is activated if you use one!):

```bash
python main.py
```

Nero will start running silently in the background. 
**How to trigger it:** Make a file edit, search for something on Google, or watch a coding video. Then **open ChatGPT or Gemini in your browser**. A floating widget will appear instantly with 3 tailored prompt suggestions!
