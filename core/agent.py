import sys
import os
sys.path.insert(0, os.path.expanduser("~/autoagent"))

from llm.ollama_client import OllamaClient
from llm.prompt_builder import build_react_prompt, parse_llm_response, AgentStep
from tools import calculator, file_tool, web_search, rag_tool

# Tool registry — maps tool names to their run() functions
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
        self.history: list[AgentStep] = []

    def _log(self, msg: str):
        if self.verbose:
            print(msg)

    def _run_tool(self, tool_name: str, action_input: str) -> str:
        """Run a tool and return its output."""
        tool_name = tool_name.lower().strip()

        if tool_name not in TOOLS:
            return f"Error: Unknown tool '{tool_name}'. Available: {list(TOOLS.keys())}"

        try:
            return TOOLS[tool_name](action_input)
        except Exception as e:
            return f"Tool error: {str(e)}"

    def run(self, goal: str) -> str:
        """
        Main ReAct loop:
        1. Build prompt with goal + history
        2. Get LLM response
        3. Parse response into thought/action/input
        4. Run the tool
        5. Add observation to history
        6. Repeat until Final Answer or max steps
        """
        self._log(f"\n{'='*55}")
        self._log(f"AGENT GOAL: {goal}")
        self._log(f"{'='*55}\n")

        self.history = []

        for step in range(self.max_steps):
            self._log(f"--- Step {step + 1}/{self.max_steps} ---")

            # Build prompt
            prompt = build_react_prompt(
                goal=goal,
                tools=TOOL_DESCRIPTIONS,
                history=self.history
            )

            # Get LLM response
            self._log("Thinking...")
            response = self.llm.complete(prompt)
            self._log(f"LLM Response:\n{response.content}\n")

            # Parse response
            agent_step = parse_llm_response(response.content)

            # Check if agent has final answer
            if agent_step.is_final:
                self._log(f"FINAL ANSWER: {agent_step.final_answer}")
                self.history.append(agent_step)
                return agent_step.final_answer

            # Validate action
            if not agent_step.action:
                self._log("Warning: No action found in response, retrying...")
                continue

            # Run the tool
            self._log(f"Running tool: {agent_step.action}")
            self._log(f"Input: {agent_step.action_input}")
            observation = self._run_tool(agent_step.action, agent_step.action_input)
            self._log(f"Observation: {observation}\n")

            # Add to history
            agent_step.observation = observation
            self.history.append(agent_step)

        return "Max steps reached without final answer."

if __name__ == "__main__":
    agent = Agent(max_steps=5, verbose=True)

    # Start with a simple test
    result = agent.run("Search the web for what Python is, then save a summary to a file called python_summary.txt") 
    print(f"\nFinal Result: {result}")
