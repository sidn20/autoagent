from dataclasses import dataclass

@dataclass
class AgentStep:
    thought: str
    action: str
    action_input: str
    observation: str = ""
    is_final: bool = False
    final_answer: str = ""

SYSTEM_PROMPT = """You are an autonomous AI agent. You solve tasks step by step using available tools.

You must ALWAYS respond in this exact format:

Thought: [your reasoning about what to do next]
Action: [tool name to use, must be one of the available tools]
Action Input: [input to pass to the tool]

OR if you have the final answer:

Thought: [your reasoning]
Final Answer: [your complete answer]

Available tools:
{tools}

Important rules:
- Always think before acting
- Use tools when you need information or to perform tasks
- Never make up information — use tools to find real answers
- Stop when you have enough information to answer the original question
"""

def build_react_prompt(goal: str, tools: list[str], history: list[AgentStep]) -> str:
    """Build a ReAct prompt with goal, tools, and conversation history."""
    tools_str = "\n".join(f"- {t}" for t in tools)
    prompt = SYSTEM_PROMPT.format(tools=tools_str)
    prompt += f"\nTask: {goal}\n\n"

    # Add history
    for step in history:
        prompt += f"Thought: {step.thought}\n"
        if step.is_final:
            prompt += f"Final Answer: {step.final_answer}\n"
        else:
            prompt += f"Action: {step.action}\n"
            prompt += f"Action Input: {step.action_input}\n"
            if step.observation:
                prompt += f"Observation: {step.observation}\n\n"

    return prompt

def parse_llm_response(response: str) -> AgentStep:
    """
    Parse LLM response into an AgentStep.
    Handles messy LLM output gracefully.
    """
    lines = response.strip().split("\n")

    thought = ""
    action = ""
    action_input = ""
    final_answer = ""
    is_final = False

    for i, line in enumerate(lines):
        line = line.strip()
        if line.startswith("Thought:"):
            thought = line[len("Thought:"):].strip()
        elif line.startswith("Action:"):
            action = line[len("Action:"):].strip().lower()
        elif line.startswith("Action Input:"):
            action_input = line[len("Action Input:"):].strip()
        elif line.startswith("Final Answer:"):
            final_answer = line[len("Final Answer:"):].strip()
            is_final = True

    return AgentStep(
        thought=thought,
        action=action,
        action_input=action_input,
        is_final=is_final,
        final_answer=final_answer
    )

if __name__ == "__main__":
    # Test the prompt builder
    tools = ["calculator", "web_search", "file_writer", "rag_search"]

    history = [
        AgentStep(
            thought="I need to calculate something",
            action="calculator",
            action_input="2 + 2",
            observation="4"
        )
    ]

    prompt = build_react_prompt(
        goal="What is 2+2 and save the result to a file?",
        tools=tools,
        history=history
    )

    print("=== BUILT PROMPT ===")
    print(prompt)

    print("\n=== PARSE TEST ===")
    sample_response = """Thought: I have the calculation result, now I need to save it
Action: file_writer
Action Input: result.txt: 2+2=4"""

    step = parse_llm_response(sample_response)
    print(f"Thought: {step.thought}")
    print(f"Action: {step.action}")
    print(f"Action Input: {step.action_input}")
    print(f"Is Final: {step.is_final}")
