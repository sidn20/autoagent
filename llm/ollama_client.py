import subprocess
import json
import time
import re
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

    def complete(self, prompt: str) -> LLMResponse:
        start = time.perf_counter()
        result = subprocess.run(
            ["ollama", "run", self.model, prompt],
            capture_output=True,
            text=True
        )
        latency_ms = (time.perf_counter() - start) * 1000

        # Strip terminal escape codes from LLM output
        clean = re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', result.stdout)
        clean = re.sub(r'\x1b\[[\x00-\x1f]*', '', clean)

        return LLMResponse(
            content=clean.strip(),
            latency_ms=round(latency_ms, 2),
            model=self.model
        )

    def complete_json(self, prompt: str) -> dict:
        json_prompt = (
            prompt +
            "\n\nCRITICAL: respond with ONLY a JSON object containing ONLY the fields asked for. "
            "No extra fields. No explanation. No markdown. "
            "No newlines inside string values. "
            "Use this exact format: {\"steps\":[{\"step\":1,\"tool\":\"TOOL\",\"task\":\"TASK\"}]}"
        )
        response = self.complete(json_prompt)
        content = response.content.strip()

        # Remove markdown code blocks
        if "```" in content:
            parts = content.split("```")
            for part in parts:
                part = part.strip()
                if part.startswith("json"):
                    part = part[4:]
                if part.strip().startswith("{"):
                    content = part.strip()
                    break

        # Remove control characters
        content = re.sub(r'[\x00-\x1f\x7f]', ' ', content)

        # Find start of JSON
        start = content.find("{")
        if start == -1:
            raise ValueError(f"No JSON found in: {content}")

        # Find matching closing brace
        depth = 0
        end = -1
        for i, ch in enumerate(content[start:], start):
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    end = i + 1
                    break

        if end == -1:
            raise ValueError(f"Truncated JSON: {content[:200]}")

        json_str = content[start:end]

        try:
            result = json.loads(json_str)
            if "steps" in result:
                return {"steps": result["steps"]}
            return result
        except json.JSONDecodeError:
            # Try common fixes for malformed JSON
            fixed = json_str

            # Fix mismatched closing like }} instead of }]}
            fixed = re.sub(r'\}\}$', '}]}', fixed)
            fixed = re.sub(r'\}\s*\}\s*$', '}]}', fixed)

            # Fix missing closing bracket
            if '"steps"' in fixed and ']' not in fixed:
                fixed = fixed.rstrip('}') + ']}'

            try:
                result = json.loads(fixed)
                if "steps" in result:
                    return {"steps": result["steps"]}
                return result
            except json.JSONDecodeError as e:
                raise ValueError(f"Could not parse JSON: {e}\nContent: {json_str[:200]}")


if __name__ == "__main__":
    client = OllamaClient()

    print("\nTest 1 — Basic completion:")
    response = client.complete("What is 2 + 2? Answer in one word.")
    print(f"Response: {response.content}")
    print(f"Latency: {response.latency_ms:.0f}ms")

    print("\nTest 2 — JSON completion:")
    result = client.complete_json(
        'Return a JSON object with ONLY these keys: "name" and "type" describing Python.'
    )
    print(f"Parsed JSON: {result}")
