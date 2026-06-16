import subprocess
import json
import time
from dataclasses import dataclass

@dataclass
class LLMResponse:
    content: str
    latency_ms: float
    model: str

class OllamaClient:
    def __init__(self, model: str = "llama3.2"):
        self.model = model
        self._verify_connection()

    def _verify_connection(self):
        """Check Ollama is running and model is available."""
        try:
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if self.model not in result.stdout:
                raise RuntimeError(f"Model {self.model} not found. Run: ollama pull {self.model}")
            print(f"LLM client ready — model: {self.model}")
        except FileNotFoundError:
            raise RuntimeError("Ollama not found. Install from https://ollama.com")

    def complete(self, prompt: str, temperature: float = 0.7) -> LLMResponse:
        """Send a prompt and get a completion."""
        start = time.perf_counter()
        result = subprocess.run(
            ["ollama", "run", self.model, prompt],
            capture_output=True,
            text=True
        )
        latency_ms = (time.perf_counter() - start) * 1000

        return LLMResponse(
            content=result.stdout.strip(),
            latency_ms=round(latency_ms, 2),
            model=self.model
        )

    def complete_json(self, prompt: str) -> dict:
        """
        Send a prompt and parse response as JSON.
        Used when agent needs structured output.
        """
        json_prompt = prompt + "\n\nRespond ONLY with valid JSON. No explanation, no markdown, no backticks."
        response = self.complete(json_prompt)

        # Clean response and parse
        content = response.content.strip()
        # Remove markdown code blocks if present
        if "```" in content:
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]

        try:
            return json.loads(content)
        except json.JSONDecodeError:
            # Try to extract JSON from response
            start = content.find("{")
            end = content.rfind("}") + 1
            if start != -1 and end != 0:
                return json.loads(content[start:end])
            raise ValueError(f"Could not parse JSON from response: {content}")

if __name__ == "__main__":
    client = OllamaClient()

    print("\nTest 1 — Basic completion:")
    response = client.complete("What is 2 + 2? Answer in one word.")
    print(f"Response: {response.content}")
