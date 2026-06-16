import json
import os
from datetime import datetime
from dataclasses import dataclass, asdict

MEMORY_FILE = os.path.expanduser("~/autoagent/memory_store.json")

@dataclass
class MemoryEntry:
    goal: str
    summary: str
    tools_used: list
    timestamp: str
    success: bool

class ShortTermMemory:
    """
    Holds the current session's conversation.
    Lives only while the agent is running — cleared on each new goal.
    """
    def __init__(self):
        self.steps = []
        self.goal = ""

    def set_goal(self, goal: str):
        self.goal = goal
        self.steps = []

    def add_step(self, thought: str, action: str, observation: str):
        self.steps.append({
            "thought": thought,
            "action": action,
            "observation": observation
        })

    def get_context(self) -> str:
        """Returns readable summary of what happened so far this session."""
        if not self.steps:
            return "No steps taken yet."
        lines = []
        for i, s in enumerate(self.steps, 1):
            lines.append(f"Step {i}: Used '{s['action']}' → {s['observation'][:100]}")
        return "\n".join(lines)

    def get_tools_used(self) -> list:
        return list(set(s["action"] for s in self.steps))


class LongTermMemory:
    """
    Persists across sessions as a JSON file.
    Stores what goals the agent completed, what tools it used, and summaries.
    """
    def __init__(self):
        self.entries: list[MemoryEntry] = []
        self._load()

    def _load(self):
        if os.path.exists(MEMORY_FILE):
            try:
                with open(MEMORY_FILE) as f:
                    data = json.load(f)
                self.entries = [MemoryEntry(**e) for e in data]
                print(f"Long-term memory loaded: {len(self.entries)} past sessions")
            except Exception as e:
                print(f"Memory load warning: {e}")
                self.entries = []
        else:
            self.entries = []

    def _save(self):
        with open(MEMORY_FILE, "w") as f:
            json.dump([asdict(e) for e in self.entries], f, indent=2)

    def remember(self, goal: str, summary: str, tools_used: list, success: bool):
        """Save a completed session to long-term memory."""
        entry = MemoryEntry(
            goal=goal,
            summary=summary,
            tools_used=tools_used,
            timestamp=datetime.now().isoformat(),
            success=success
        )
        self.entries.append(entry)
        self._save()
        print(f"Saved to long-term memory: '{goal[:50]}'")

    def recall_similar(self, goal: str, max_results: int = 3) -> str:
        """
        Find past sessions relevant to the current goal.
        Simple keyword match — good enough for now.
        """
        if not self.entries:
            return "No past memory found."

        goal_words = set(goal.lower().split())
        scored = []

        for entry in self.entries:
            entry_words = set(entry.goal.lower().split())
            overlap = len(goal_words & entry_words)
            if overlap > 0:
                scored.append((overlap, entry))

        scored.sort(reverse=True, key=lambda x: x[0])
        top = scored[:max_results]

        if not top:
            return "No similar past tasks found."

        lines = ["Relevant past sessions:"]
        for score, entry in top:
            lines.append(
                f"- [{entry.timestamp[:10]}] Goal: '{entry.goal[:60]}'\n"
                f"  Summary: {entry.summary[:120]}\n"
                f"  Tools used: {entry.tools_used}"
            )
        return "\n".join(lines)

    def get_all(self) -> list:
        return self.entries


if __name__ == "__main__":
    print("=== Short-Term Memory Test ===")
    stm = ShortTermMemory()
    stm.set_goal("Find what Python is and save it")
    stm.add_step("I need to search the web", "web_search", "Python is a high-level language...")
    stm.add_step("Now save the result", "file_tool", "Successfully wrote 200 chars to python.txt")
    print(stm.get_context())
    print("Tools used:", stm.get_tools_used())

    print("\n=== Long-Term Memory Test ===")
    ltm = LongTermMemory()
    ltm.remember(
        goal="Find what Python is and save it",
        summary="Searched web for Python, got Wikipedia summary, saved to python_summary.txt",
        tools_used=["web_search", "file_tool"],
        success=True
    )
    ltm.remember(
        goal="Calculate compound interest for a loan",
        summary="Used calculator to compute 5% interest over 10 years",
        tools_used=["calculator"],
        success=True
    )

    print("\nRecalling similar to 'search for Python tutorials':")
    print(ltm.recall_similar("search for Python tutorials"))
