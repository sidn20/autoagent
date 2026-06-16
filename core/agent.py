import sys
import os
sys.path.insert(0, os.path.expanduser("~/autoagent"))

from llm.ollama_client import OllamaClient
from llm.prompt_builder import build_react_prompt, parse_llm_response, AgentStep
from core.memory import ShortTermMemory, LongTermMemory
from tools import calculator, file_tool, web_search, rag_tool

TOOLS = {
    "calculator": calculator.calculate,
    "file_tool": file_tool.run,
    "web_search": web_search.run,
    "rag_search": rag_tool.run,
}

TOOL_DESCRIPTIONS = [
    "calculator: perform math calculations. Input: math expression like '2 + 2' or 'sqrt(144)'",
    "file_tool: read/write files. Input: 'write: filename: content' or 'read: filename' or 'list'",
    "web_search: search the internet. Input: search query",
    "rag_search: search local documents. Input: search query",
]

class Agent:
    def __init__(self, max_steps: int = 10, verbose: bool = True):
        self.llm = OllamaClient()
        self.max_steps = max_steps
        self.verbose = verbose
        self.short_term = ShortTermMemory()
        self.long_term = LongTermMemory()
        self.history: list[AgentStep] = []

    def _log(self, msg: str):
        if self.verbose:
            print(msg)

    def _run_tool(self, tool_name: str, action_input: str) -> str:
        tool_name = tool_name.lower().strip()
        if tool_name not in TOOLS:
            return f"Error: Unknown tool '{tool_name}'. Available: {list(TOOLS.keys())}"
        try:
            return TOOLS[tool_name](action_input)
        except Exception as e:
            return f"Tool error: {str(e)}"

    def run(self, goal: str) -> str:
        self._log(f"\n{'='*55}")
        self._log(f"AGENT GOAL: {goal}")
        self._log(f"{'='*55}\n")

        # Set up short-term memory for this session
        self.short_term.set_goal(goal)
        self.history = []

        # Check long-term memory for relevant past sessions
        past_context = self.long_term.recall_similar(goal)
        if "No similar" not in past_context:
            self._log(f"[Memory] {past_context}\n")

        final_answer = "Max steps reached without final answer."
        success = False

        for step in range(self.max_steps):
            self._log(f"--- Step {step + 1}/{self.max_steps} ---")

            prompt = build_react_prompt(
                goal=goal,
                tools=TOOL_DESCRIPTIONS,
                history=self.history
            )

            self._log("Thinking...")
            response = self.llm.complete(prompt)
            self._log(f"LLM Response:\n{response.content}\n")

            agent_step = parse_llm_response(response.content)

            if agent_step.is_final:
                self._log(f"FINAL ANSWER: {agent_step.final_answer}")
                self.history.append(agent_step)
                final_answer = agent_step.final_answer
                success = True
                break

            if not agent_step.action:
                self._log("Warning: No action found, retrying...")
                continue

            self._log(f"Running tool: {agent_step.action}")
            self._log(f"Input: {agent_step.action_input}")
            observation = self._run_tool(agent_step.action, agent_step.action_input)
            self._log(f"Observation: {observation}\n")

            # Record in short-term memory
            self.short_term.add_step(
                thought=agent_step.thought,
                action=agent_step.action,
                observation=observation
            )

            agent_step.observation = observation
            self.history.append(agent_step)

        # Save to long-term memory
        self.long_term.remember(
            goal=goal,
            summary=final_answer[:200],
            tools_used=self.short_term.get_tools_used(),
            success=success
        )

        return final_answer


if __name__ == "__main__":
    agent = Agent(max_steps=6, verbose=True)

    # First run — agent has no memory of this
    result = agent.run("What is the square root of 256?")
    print(f"\nResult: {result}")

    print("\n" + "="*55 + "\n")

    # Second run — agent will recall the first session
    result = agent.run("Calculate the square root of 144 and save it to math_results.txt")
    print(f"\nResult: {result}")
