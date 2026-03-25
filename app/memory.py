import json
import os
from typing import List, Dict


class ConversationMemory:
    """Short-term memory: stores the current conversation history."""

    def __init__(self, max_turns: int = 10):
        self.history: List[Dict] = []
        self.max_turns = max_turns

    def add(self, role: str, content: str):
        self.history.append({"role": role, "content": content})
        # Keep only the last N turns to avoid token overflow
        if len(self.history) > self.max_turns * 2:
            self.history = self.history[-(self.max_turns * 2):]

    def get_history(self) -> List[Dict]:
        return self.history

    def clear(self):
        self.history = []


def load_long_term_memory(memory_file: str) -> Dict:
    """Long-term memory: what the student has learned across sessions."""
    if os.path.exists(memory_file):
        with open(memory_file, "r") as f:
            return json.load(f)
    return {"learned_facts": [], "corrected_mistakes": []}


def save_long_term_memory(memory_file: str, memory: Dict):
    with open(memory_file, "w") as f:
        json.dump(memory, f, indent=2)


def format_memory_for_prompt(memory_file: str) -> str:
    """Format long-term memory into text for the system prompt."""
    mem = load_long_term_memory(memory_file)
    parts = []
    if mem["learned_facts"]:
        parts.append("Things I have already learned:\n- " + "\n- ".join(mem["learned_facts"][-10:]))
    if mem["corrected_mistakes"]:
        recent = mem["corrected_mistakes"][-5:]
        lines = [
            "I thought '" + m["mistake"] + "' but was corrected: '" + m["correction"] + "'"
            for m in recent
        ]
        parts.append("Mistakes I was corrected on:\n- " + "\n- ".join(lines))
    return "\n\n".join(parts) if parts else "I am just starting to learn this topic."