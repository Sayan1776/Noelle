# core/memory.py
import json
from pathlib import Path
from typing import Literal, Dict, List

MEMORY_PATH = Path("data/memory.json")

MemoryType = Literal["fact", "preference"]

def load_memory() -> Dict[str, List[str]]:
    if not MEMORY_PATH.exists():
        return {"facts": [], "preferences": []}

    with open(MEMORY_PATH, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {"facts": [], "preferences": []}

def save_memory(memory: Dict[str, List[str]]):
    MEMORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(MEMORY_PATH, "w", encoding="utf-8") as f:
        json.dump(memory, f, indent=2)

def add_fact(entry: str):
    memory = load_memory()
    if entry not in memory["facts"]:
        memory["facts"].append(entry)
    save_memory(memory)

def add_preference(entry: str):
    memory = load_memory()
    if entry not in memory["preferences"]:
        memory["preferences"].append(entry)
    save_memory(memory)

def recall_facts() -> str:
    memory = load_memory()
    return "\n".join(f"- {m}" for m in memory["facts"])

def recall_preferences() -> str:
    memory = load_memory()
    return "\n".join(f"- {m}" for m in memory["preferences"])

# --- Public memory API used by the agent ---

def add_memory(entry: str):
    """
    Default memory write.
    For now, treat generic 'remember' as a fact.
    """
    add_fact(entry)

def recall_memory() -> str:
    """
    Default memory recall.
    Returns both facts and preferences.
    """
    facts = recall_facts()
    prefs = recall_preferences()

    if not facts and not prefs:
        return "I don't have anything saved yet."

    out = []
    if facts:
        out.append("Facts:\n" + facts)
    if prefs:
        out.append("Preferences:\n" + prefs)

    return "\n\n".join(out)
