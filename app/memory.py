# app/memory.py
import json
import os
from typing import List, Dict

LONG_TERM_MEMORY_FILE = "./data/long_term_memory.json"

# ── SHORT-TERM (in-memory list of message dicts) ──────────────────────────────

class ConversationMemory:
    def __init__(self, max_turns: int = 10):
        self.history: List[Dict] = []
        self.max_turns = max_turns  # Keep last N turns to avoid token overflow

    def add(self, role: str, content: str):
        self.history.append({"role": role, "content": content})
        # Trim to max_turns (each turn = 1 user + 1 assistant message)
        if len(self.history) > self.max_turns * 2:
            self.history = self.history[-(self.max_turns * 2):]

    def get_history(self) -> List[Dict]:
        return self.history

    def clear(self):
        self.history = []


# ── LONG-TERM (persisted JSON file) ──────────────────────────────────────────

def load_long_term_memory() -> Dict:
    """Load what the student has learned across sessions."""
    if os.path.exists(LONG_TERM_MEMORY_FILE):
        with open(LONG_TERM_MEMORY_FILE, "r") as f:
            return json.load(f)
    return {"learned_facts": [], "corrected_mistakes": [], "understood_topics": []}

def save_long_term_memory(memory: Dict):
    os.makedirs("./data", exist_ok=True)
    with open(LONG_TERM_MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=2)

def add_learned_fact(fact: str):
    """Call this when the student correctly explains something back."""
    mem = load_long_term_memory()
    if fact not in mem["learned_facts"]:
        mem["learned_facts"].append(fact)
    save_long_term_memory(mem)

def add_corrected_mistake(mistake: str, correction: str):
    """Call this when the user corrects the student."""
    mem = load_long_term_memory()
    mem["corrected_mistakes"].append({"mistake": mistake, "correction": correction})
    save_long_term_memory(mem)

def format_long_term_memory_for_prompt() -> str:
    """Inject long-term memory into the system prompt."""
    mem = load_long_term_memory()
    parts = []
    if mem["learned_facts"]:
        parts.append("Things I've already learned:\n- " + "\n- ".join(mem["learned_facts"][-10:]))
    if mem["corrected_mistakes"]:
        recent = mem["corrected_mistakes"][-5:]
        corrections = [f"I thought '{m['mistake']}' but was told: '{m['correction']}'" for m in recent]
        parts.append("Mistakes I've been corrected on:\n- " + "\n- ".join(corrections))
    return "\n\n".join(parts) if parts else "I'm just starting to learn this topic."