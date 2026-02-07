# 🤖 Local AI Agent (Personal assistant)

A fully local, extensible AI assistant designed to behave less like a chatbot and more like a **thinking system you own**. It runs on your machine, respects your rules, adapts to your instructions, and evolves over time across **CLI and GUI** workflows.

This project is not about replacing humans.
It’s about **amplifying one**.

---

## 🧠 Philosophy

The story starts with ownership. A local-first assistant that keeps data on your machine, follows your rules, and fails safely when the world gets messy. It is built to explain, not hallucinate; to reason, not ramble. It should feel like a system you can trust and reshape, not a black box.

Think of it as your *digital second brain*, not a toy chatbot.

---

## ✨ Current Features (Implemented)

### 1️⃣ Local LLM Runtime

The assistant speaks through a local LLM runtime so you are not tethered to the cloud.

* Uses **Ollama** locally (`core/llm.py`)
* No forced cloud dependency
* Supports offline operation with local models

---

### 2️⃣ Dual Interface: CLI + GUI

When you want speed, the CLI is immediate. When you want flow, the GUI turns it into a living interface.

* **CLI** loop with mode switching (`main.py`)
* **GUI** built in CustomTkinter (`gui/app.py`)
* Multi-tab sessions, typing indicator, and clear-chat controls

---

## ⚠️ Current Limitation (Important)

### Agent Mode Availability

At the moment, the **full agent loop (planner → tools → synthesis)** is **only available in the CLI**.

* ✅ **CLI**: Runs the complete agent pipeline (planning, step execution, tool routing, memory decisions)
* ⚠️ **GUI**: Currently operates in **chat / assistant wrapper mode only**

  * The GUI is **not yet fully wired** to the agent loop
  * Agent-style multi-step execution is **intentionally disabled** in the GUI for now

This is a **known and deliberate limitation**, not a bug.

The GUI integration for agent mode is actively planned and will be added in a future update once:

* logging is streamed safely,
* step-by-step visibility is refined,
* and failure handling is polished for a visual interface.

> **TL;DR**
> If you want the *real* agent experience today, use the **CLI**.
> The GUI will catch up soon.

---

### 3️⃣ Agent Loop + Planner

Behind the scenes, a planner breaks the goal into steps, selects tools, and checks when the job is done.

* Multi-step planning (`agent/planner.py`)
* Tool selection (`agent/loop.py`)
* Goal satisfaction checks and final synthesis

---

### 4️⃣ Tooling: File QA + Semantic Search

When the question requires local knowledge, the assistant searches your files semantically and answers with context.

* Local file QA with FAISS index (`modules/file_qa.py`)
* Offline embeddings via SentenceTransformers
* Embedding rebuild script (`build_index.py`)

---

### 5️⃣ Tooling: Data Agent (CSV)

If the request is about data, a separate data agent locks in and returns hard facts.

* CSV analysis via pandas (`modules/data_agent.py`)
* Hard facts: rows, columns, missing values
* Safety lock so CSV requests stay in the data agent

---

### 6️⃣ Memory + Session Persistence

The assistant can remember what matters and keep conversations intact across GUI sessions.

* Long-term memory stored in `data/memory.json` (`core/memory.py`)
* GUI chat sessions stored in `data/sessions.json`

---

### 7️⃣ Voice I/O (Optional)

When needed, it can listen and speak with lightweight local tools.

* **Speech-to-text** via Faster-Whisper (`voice/speech_to_text.py`)
* **Text-to-speech** via pyttsx3 (`voice/text_to_speech.py`)

---

### 8️⃣ System Actions (Basic)

Simple system intents are supported for quick actions.

* Open Chrome or VS Code (`modules/system_control.py`)

---

### 9️⃣ Personality Chat Mode (Noelle)

A dedicated companion mode keeps its own emotional thread and optional voice replies.

* Dedicated persona layer (`modules/chat_mode.py`)
* Separate memory for chat mode
* Optional voice replies

---

### 🔟 Intent Classification + Routing

Every request is classified, routed to the right tool, or handled by fallback chat.

* LLM-based intent detection (`core/intent_classifier.py`)
* Safe routing to tools and fallback chat

---

## 📁 Project Structure

```text
assistant/
├─ agent/
│  ├─ loop.py
│  ├─ planner.py
│  ├─ state.py
│  └─ tools.py
├─ core/
│  ├─ intent_classifier.py
│  ├─ llm.py
│  ├─ memory.py
│  └─ router.py
├─ gui/
│  ├─ app.py
│  ├─ assistant_bridge.py
│  ├─ controller.py
│  ├─ session.py
│  ├─ session_store.py
│  └─ widgets.py
├─ modules/
│  ├─ chat.py
│  ├─ chat_mode.py
│  ├─ coding.py
│  ├─ data_agent.py
│  ├─ embeddings.py
│  ├─ file_qa.py
│  ├─ local_file.py
│  ├─ semantic_search.py
│  └─ system_control.py
├─ voice/
│  ├─ speech_to_text.py
│  └─ text_to_speech.py
├─ data/
│  ├─ memory.json
│  ├─ sessions.json
│  └─ embeddings/
│     ├─ index.faiss
│     └─ meta.pkl
├─ build_index.py
├─ main.py
├─ requirements.txt
└─ readme.md
```

---

## 🔁 Workflow (High-Level)

### CLI Flow (`main.py`)

The CLI is the fastest path from a question to a tool-backed answer.

* User input
* Intent classification
* Route to tool (system, file QA, memory, coding)
* Fallback to local chat if no tool applies

---

### GUI Flow (`gui/app.py`)

The GUI wraps the same assistant in a conversational workspace with modes and tabs.

* User input in chat window
* Mode toggle: **CHAT** or **assistant**
* CHAT mode uses persona + optional voice
* assistant mode runs the agent loop and returns final answer

---

## 🛠 Tech Stack

* **Language**: Python 🐍
* **LLM Runtime**: Ollama (local)
* **Semantic Search**: FAISS + SentenceTransformers
* **Data Analysis**: pandas
* **GUI**: CustomTkinter
* **Voice**: Faster-Whisper + pyttsx3

---

## 🚀 Planned Future Upgrades

### 🔮 Short-Term Upgrades

#### 🔹 Modular Skill System

* Plug-and-play skills:

  * File analysis
  * Code review
  * Writing assistant
  * Debugging helper

#### 🔹 Tool Invocation Layer

* Agent decides **when** to:

  * Run scripts
  * Open files
  * Query local data

---

### 🧠 Mid-Term Upgrades

#### 🔹 Reasoning Mode Toggle

* Switch between:

  * Fast responses
  * Deep analytical thinking

#### 🔹 Multi-Agent Architecture

* Specialized sub-agents:

  * Planner
  * Executor
  * Critic

#### 🔹 Task Management System

* To-do tracking
* Priority handling
* Time-aware reminders

---

### 🌌 Long-Term Vision

#### 🔹 Self-Upgrading Architecture

* Agent suggests its own improvements
* Flags inefficiencies in its logic

#### 🔹 Emotional Context Awareness

* Detects frustration, confusion, or urgency
* Adjusts tone and depth accordingly

#### 🔹 Fully Personalized AI Identity

* Name, personality, response style fully customizable
* Evolves with usage, not presets

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

This isn’t an AI that replaces you.

It’s an AI that:

> *thinks with you, not for you.*

And that’s the point.

---

**Built locally. Controlled fully. Evolving constantly.** 🚀
