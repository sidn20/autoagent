import sys
import os
sys.path.insert(0, os.path.expanduser("~/autoagent"))
from llm.ollama_client import OllamaClient

class Planner:
    def __init__(self, llm: OllamaClient = None):
        self.llm = llm or OllamaClient()

    def plan(self, goal: str) -> list[dict]:
        prompt = (
            f'Break this task into 1-3 steps.\n'
            f'Task: {goal}\n'
            f'Available tools: calculator, web_search, file_tool, rag_search\n'
            f'Return ONLY this JSON with ONLY the steps key:\n'
            f'{{"steps":[{{"step":1,"tool":"TOOL_NAME","task":"brief task description"}}]}}'
        )
        try:
            result = self.llm.complete_json(prompt)
            steps = result.get("steps", [])
            valid = []
            for s in steps:
                if isinstance(s, dict) and "tool" in s and "task" in s:
                    valid.append({
                        "step": s.get("step", len(valid) + 1),
                        "tool": s["tool"].lower(),
                        "task": s["task"]
                    })
            return valid if valid else self._fallback(goal)
        except Exception as e:
            print(f"Planner error: {e}")
            return self._fallback(goal)

    def _fallback(self, goal: str) -> list[dict]:
        return [{"step": 1, "tool": "web_search", "task": goal}]

    def format_plan(self, steps: list[dict]) -> str:
        if not steps:
            return "No plan generated."
        lines = ["Plan:"]
        for s in steps:
            lines.append(f"  Step {s['step']}: [{s['tool']}] {s['task']}")
        return "\n".join(lines)


if __name__ == "__main__":
    planner = Planner()
    goals = [
        "What is 25 * 4?",
        "Search the web for what Docker is and save a summary to docker_notes.txt",
        "Find machine learning info from local docs then save a combined report",
    ]
    print("Planner Tests:")
    print("=" * 55)
    for goal in goals:
        print(f"\nGoal: {goal}")
        steps = planner.plan(goal)
        print(planner.format_plan(steps))
        print("-" * 40)
