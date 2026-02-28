# 🤖 Noelle — Local AI Agent (Personal Assistant)

A fully local, extensible AI assistant designed to behave less like a chatbot and more like a **thinking system you own**. It runs on your machine, respects your rules, adapts to your instructions, and evolves over time across **CLI and GUI** workflows.

This project is not about replacing humans.
It's about **amplifying one**.

---

## 🧠 Philosophy

The story starts with ownership. A local-first assistant that keeps data on your machine, follows your rules, and fails safely when the world gets messy. It is built to explain, not hallucinate; to reason, not ramble. It should feel like a system you can trust and reshape, not a black box.

Think of it as your *digital second brain*, not a toy chatbot.

---

## ✨ Current Features

### 1️⃣ Unified Mode — Noelle Persona + Agentic Tools

No mode switching needed. Noelle's personality is **always active** — she chats naturally during casual conversation and automatically handles agentic tasks when commanded.

* Single unified loop — persona never turns off
* Intent classification routes to the right tool automatically
* Tool results are relayed in-character (facts included, personality added)
* Noelle knows she is an AI agent and is honest about it
* Dedicated persona layer (`modules/chat_mode.py`)

---

### 2️⃣ Web Browsing Agent 🌐

The assistant can browse **any website** — navigate, search, interact with pages, and extract information.

* **Any site support** — Playwright-based browser with 14+ site shortcuts + LLM URL resolution for unknown sites
* **Generic page interaction** — scans capabilities (inputs, buttons, links) on any page using 6 detection strategies
* **Smart search** — 5 escalating fallback strategies to find and use search inputs on any site
* **Page summarization** — extracts and summarizes page content for the user
* **Approval-gated** — always asks before navigating or interacting
* **Lazy browser launch** — no blank tabs; browser only opens after approval
* Key files: `modules/web_browse.py`, `modules/browser_agent.py`, `modules/browser_capabilities.py`, `modules/action_agent.py`, `skills/generic.py`, `skills/web_search.py`

---

### 3️⃣ Local LLM Runtime

The assistant speaks through a local LLM runtime so you are not tethered to the cloud.

* Uses **Ollama** locally (`core/llm.py`)
* Default model: `deepseek-r1:8b`
* Context window: 8192 tokens
* No forced cloud dependency
* Supports offline operation with local models

---

### 4️⃣ Dual Interface: CLI + GUI

When you want speed, the CLI is immediate. When you want flow, the GUI turns it into a living interface.

* **CLI** unified loop with persona + tools (`main.py`)
* **GUI** built in CustomTkinter (`gui/app.py`)
* Multi-tab sessions, typing indicator, and clear-chat controls

---

### 5️⃣ Agent Loop + Planner

Behind the scenes, a planner breaks the goal into steps, selects tools, and checks when the job is done.

* Multi-step planning (`agent/planner.py`)
* Tool selection with 4 tools: `file_qa`, `coding`, `data_agent`, `browse` (`agent/loop.py`)
* Goal satisfaction checks and final synthesis
* Memory classification and long-term storage
* Toggle with `agent on` / `agent off` in CLI

---

### 6️⃣ Tooling: File QA + Semantic Search

When the question requires local knowledge, the assistant searches your files semantically and answers with context.

* Local file QA with FAISS index (`modules/file_qa.py`)
* Offline embeddings via SentenceTransformers
* Embedding rebuild script (`build_index.py`)

---

### 7️⃣ Tooling: Data Agent (CSV)

If the request is about data, a separate data agent locks in and returns hard facts.

* CSV analysis via pandas (`modules/data_agent.py`)
* Hard facts: rows, columns, missing values
* Safety lock so CSV requests stay in the data agent

---

### 8️⃣ Memory + Session Persistence

The assistant can remember what matters and keep conversations intact across GUI sessions.

* Long-term memory stored in `data/memory.json` (`core/memory.py`)
* GUI chat sessions stored in `data/sessions.json`
* Memory classification: FACT / PREFERENCE / IGNORE

---

### 9️⃣ Voice I/O (Optional)

When needed, it can listen and speak with lightweight local tools.

* **Speech-to-text** via Faster-Whisper (`voice/speech_to_text.py`)
* **Text-to-speech** via pyttsx3 (`voice/text_to_speech.py`)

---

### 🔟 System Actions

Simple system intents are supported for quick actions.

* Open Chrome or VS Code (`modules/system_control.py`)

---

### 1️⃣1️⃣ Intent Classification + Routing

Every request is classified, routed to the right tool, or handled by fallback chat.

* LLM-based intent detection (`core/intent_classifier.py`)
* 6 intents: `SYSTEM`, `FILE_QA`, `MEMORY`, `CODING`, `BROWSE`, `CHAT`
* Keyword safety overrides for reliable routing
* Safe fallback to chat mode

---

## 📁 Project Structure

```text
assistant/
├─ agent/
│  ├─ loop.py              # Agent loop (plan → tool → synthesize → memory)
│  ├─ planner.py           # Multi-step task planner
│  ├─ state.py             # Agent state tracker
│  └─ tools.py             # Tool registry (file_qa, coding, data_agent, browse)
├─ core/
│  ├─ intent_classifier.py # LLM intent classification (6 intents)
│  ├─ llm.py               # Ollama LLM runtime
│  ├─ memory.py            # Long-term memory (facts, preferences)
│  └─ router.py            # Keyword-based intent routing
├─ gui/
│  ├─ app.py               # CustomTkinter GUI
│  ├─ assistant_bridge.py  # GUI ↔ agent bridge
│  ├─ controller.py        # Chat controller (sessions, modes)
│  ├─ session.py           # Chat session model
│  ├─ session_store.py     # Session persistence
│  └─ widgets.py           # Custom UI widgets
├─ modules/
│  ├─ action_agent.py      # LLM-driven browser action planner
│  ├─ approval.py          # User approval gate for browser actions
│  ├─ browser_agent.py     # Playwright browser (lazy-init, persistent profile)
│  ├─ browser_capabilities.py # Generic page scanner (inputs, buttons, links)
│  ├─ chat.py              # Pure LLM chat call
│  ├─ chat_mode.py         # Noelle persona + system prompt
│  ├─ coding.py            # Code explanation / transformation
│  ├─ data_agent.py        # CSV / dataset analysis
│  ├─ embeddings.py        # SentenceTransformer embeddings
│  ├─ file_qa.py           # File-based Q&A
│  ├─ local_file.py        # Local file operations
│  ├─ semantic_search.py   # FAISS semantic search
│  ├─ system_control.py    # OS-level actions
│  └─ web_browse.py        # Unified web browsing handler
├─ skills/
│  ├─ amazon.py            # Amazon-specific skills
│  ├─ generic.py           # Generic page interactions (fill, click)
│  └─ web_search.py        # Google search skill
├─ voice/
│  ├─ speech_to_text.py    # Faster-Whisper STT
│  └─ text_to_speech.py    # pyttsx3 TTS
├─ data/
│  ├─ memory.json
│  ├─ sessions.json
│  └─ embeddings/
│     ├─ index.faiss
│     └─ meta.pkl
├─ browser_profile/        # Persistent Chromium profile
├─ build_index.py          # Rebuild FAISS embeddings
├─ main.py                 # CLI entry point (unified mode)
├─ requirements.txt
└─ readme.md
```

---

## � Getting Started

### Prerequisites

* Python 3.11+
* [Ollama](https://ollama.ai/) installed with `deepseek-r1:8b` model
* GPU: RTX 3050 or equivalent (8GB VRAM recommended)

### Installation

```bash
# Clone and enter the project
cd assistant

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Install Playwright browser
playwright install chromium

# Pull the LLM model
ollama pull deepseek-r1:8b
```

### Running

```bash
python main.py
```

### CLI Commands

| Command | Action |
|---|---|
| `agent on` / `agent off` | Toggle multi-step agent planning |
| `voice on` / `voice off` | Toggle voice replies |
| `listen` | Speak instead of typing |
| `exit` | Shut down |

---

## 🔁 How It Works

```text
User Input
    ↓
Intent Classification (SYSTEM / FILE_QA / MEMORY / CODING / BROWSE / CHAT)
    ↓
┌─────────────────────────────────────────────────────┐
│  BROWSE → web_browse.py (own pipeline)              │
│  SYSTEM → system_control.py                         │
│  FILE_QA → file_qa.py                               │
│  MEMORY → memory.py                                 │
│  CODING → coding.py                                 │
│  CHAT → direct LLM                                  │
│  (agent on) → planner → tool loop → synthesize      │
└─────────────────────────────────────────────────────┘
    ↓
Noelle Persona Wrapper (adds personality to ALL responses)
    ↓
User sees response
```

---

## 🛠 Tech Stack

* **Language**: Python 🐍
* **LLM Runtime**: Ollama (local, `deepseek-r1:8b`)
* **Web Browsing**: Playwright (Chromium)
* **Semantic Search**: FAISS + SentenceTransformers
* **Data Analysis**: pandas
* **GUI**: CustomTkinter
* **Voice**: Faster-Whisper + pyttsx3

---

## ⚠️ Current Limitations

### GUI Agent Mode

The **full agent loop** is currently **only available in the CLI**.

* ✅ **CLI**: Runs the complete pipeline (intent → tool → persona → response)
* ⚠️ **GUI**: Operates in chat / assistant wrapper mode only

The GUI integration for the unified mode is planned for a future update.

---

## 🚀 Planned Future Upgrades

### Short-Term
* GUI integration for unified Noelle + agent mode
* Multi-agent architecture (planner, executor, critic)
* Task management system with priorities

### Mid-Term
* Reasoning mode toggle (fast vs. deep analytical)
* Self-upgrading architecture
* Emotional context awareness

### Long-Term
* Fully personalized AI identity that evolves with usage

---

## ⚠️ Disclaimer

This project is **experimental**.

It prioritizes:

* Control over convenience
* Understanding over automation
* Ownership over dependency

Use it to **learn**, **build**, and **push boundaries**.

---

## 🧩 Final Note

This isn't an AI that replaces you.

It's an AI that:

> *thinks with you, not for you.*

And that's the point.

---

**Built locally. Controlled fully. Evolving constantly.** 🚀
