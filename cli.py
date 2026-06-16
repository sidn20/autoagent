import sys
import os
sys.path.insert(0, os.path.expanduser("~/autoagent"))

from core.agent import Agent
from core.memory import LongTermMemory

def print_banner():
    print("""
╔══════════════════════════════════════════════════╗
║           AutoAgent — AI Agent CLI               ║
║   Type your goal and watch the agent work        ║
║   Commands: 'memory', 'clear', 'quit'            ║
╚══════════════════════════════════════════════════╝
""")

def print_memory(ltm: LongTermMemory):
    entries = ltm.get_all()
    if not entries:
        print("No past sessions in memory.")
        return
    print(f"\n{'='*50}")
    print(f"Long-term Memory ({len(entries)} sessions)")
    print(f"{'='*50}")
    for e in entries[-5:]:
        status = "✅" if e.success else "❌"
        print(f"{status} [{e.timestamp[:16]}] {e.goal[:50]}")
        print(f"   Tools: {e.tools_used}")
        print(f"   Summary: {e.summary[:80]}")
    print(f"{'='*50}\n")

def main():
    print_banner()

    agent = Agent(max_steps=6, verbose=True)
    ltm = LongTermMemory()

    print("Agent ready! Type a goal to get started.\n")

    while True:
        try:
            goal = input("🤖 Goal > ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break

        if not goal:
            continue

        if goal.lower() == "quit":
            print("Goodbye!")
            break

        elif goal.lower() == "memory":
            print_memory(ltm)
            continue

        elif goal.lower() == "clear":
            os.system("clear")
            print_banner()
            continue

        elif goal.lower() == "help":
            print("\nCommands:")
            print("  memory  — show past sessions")
            print("  clear   — clear screen")
            print("  quit    — exit")
            print("  Or just type any goal!\n")
            continue

        # Run the agent
        print()
        result = agent.run(goal)
        print(f"\n{'='*55}")
        print(f"✅ DONE: {result}")
        print(f"{'='*55}\n")

if __name__ == "__main__":
    main()
