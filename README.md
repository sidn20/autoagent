# AutoAgent — Autonomous AI Agent Framework

An autonomous AI agent built from scratch in Python without LangChain or
LlamaIndex. Uses the ReAct (Reason + Act) loop to break down goals,
select tools, execute them, and iterate until the task is complete.

Powered by local Llama3.2 via Ollama — no API keys, no cloud required.

## What is a ReAct Agent?
Goal → Thought → Action → Observation → Thought → ... → Final Answer

The agent reasons about what to do, picks a tool, runs it, observes the
result, and repeats until it has enough information to answer.

## Architecture
autoagent/
├── core/
│   ├── agent.py       — ReAct loop, tool execution, main brain
│   ├── memory.py      — short term (session) + long term (persistent)
│   └── planner.py     — breaks goals into ordered steps
├── llm/
│   ├── ollama_client.py   — Llama3.2 client with JSON parsing
│   └── prompt_builder.py  — ReAct prompt construction and parsing
├── tools/
│   ├── calculator.py  — sandboxed math evaluation
│   ├── file_tool.py   — read/write/list files in workspace
│   ├── web_search.py  — DuckDuckGo live search, no API key
│   └── rag_tool.py    — semantic search via rag-system project
├── cli.py             — interactive terminal interface
└── api.py             — FastAPI REST interface

## Tools Available

| Tool | Description | Example Input |
|------|-------------|---------------|
| `calculator` | Sandboxed math | `sqrt(256)` or `25 * 4` |
| `web_search` | Live internet search | `what is FastAPI` |
| `file_tool` | Read/write workspace files | `write: notes.txt: content` |
| `rag_search` | Semantic search local docs | `machine learning algorithms` |

## Quick Start

```bash
# Install dependencies
pip3 install fastapi uvicorn sentence-transformers faiss-cpu

# Install Ollama and pull model
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3.2

# Run CLI
python3 cli.py

# Run API
python3 api.py
```

## CLI Usage
╔══════════════════════════════════════════════════╗
║           AutoAgent — AI Agent CLI               ║
║   Type your goal and watch the agent work        ║
║   Commands: 'memory', 'clear', 'quit'            ║
╚══════════════════════════════════════════════════╝
🤖 Goal > What is 15 * 8?
🤖 Goal > Search the web for what FastAPI is
🤖 Goal > memory
🤖 Goal > quit

## API Usage

```bash
# Health check
curl http://localhost:8001/health

# Run a goal
curl -X POST http://localhost:8001/run \
  -H "Content-Type: application/json" \
  -d '{"goal": "what is 99 * 11", "max_steps": 4}'

# View memory
curl http://localhost:8001/memory

# View metrics
curl http://localhost:8001/metrics
```

## Sample API Response

```json
{
  "goal": "what is 99 * 11",
  "result": "1089",
  "steps_taken": 2,
  "tools_used": ["calculator"],
  "latency_ms": 90731.18,
  "timestamp": "2026-06-17 04:26:09"
}
```

## Memory System

**Short-term memory** — tracks thoughts, actions, and observations
within the current session. Cleared on each new goal.

**Long-term memory** — persists across sessions as JSON. Stores goal,
summary, tools used, and success status. Agent recalls similar past
tasks at the start of each new goal.

```json
{
  "goal": "What is the square root of 256?",
  "summary": "The square root of 256 is 16.0.",
  "tools_used": ["calculator"],
  "timestamp": "2026-06-16T06:10:00",
  "success": true
}
```

## Integration with RAG System

The `rag_search` tool connects directly to the
[rag-system](https://github.com/sidn20/rag-system) project,
giving the agent semantic search over local documents.
## API Usage

```bash
# Health check
curl http://localhost:8001/health

# Run a goal
curl -X POST http://localhost:8001/run \
  -H "Content-Type: application/json" \
  -d '{"goal": "what is 99 * 11", "max_steps": 4}'

# View memory
curl http://localhost:8001/memory

# View metrics
curl http://localhost:8001/metrics
```

## Sample API Response

```json
{
  "goal": "what is 99 * 11",
  "result": "1089",
  "steps_taken": 2,
  "tools_used": ["calculator"],
  "latency_ms": 90731.18,
  "timestamp": "2026-06-17 04:26:09"
}
```

## Memory System

**Short-term memory** — tracks thoughts, actions, and observations
within the current session. Cleared on each new goal.

**Long-term memory** — persists across sessions as JSON. Stores goal,
summary, tools used, and success status. Agent recalls similar past
tasks at the start of each new goal.

```json
{
  "goal": "What is the square root of 256?",
  "summary": "The square root of 256 is 16.0.",
  "tools_used": ["calculator"],
  "timestamp": "2026-06-16T06:10:00",
  "success": true
}
```

## Integration with RAG System

The `rag_search` tool connects directly to the
[rag-system](https://github.com/sidn20/rag-system) project,
giving the agent semantic search over local documents.

## API Usage

```bash
# Health check
curl http://localhost:8001/health

# Run a goal
curl -X POST http://localhost:8001/run \
  -H "Content-Type: application/json" \
  -d '{"goal": "what is 99 * 11", "max_steps": 4}'

# View memory
curl http://localhost:8001/memory

# View metrics
curl http://localhost:8001/metrics
```

## Sample API Response

```json
{
  "goal": "what is 99 * 11",
  "result": "1089",
  "steps_taken": 2,
  "tools_used": ["calculator"],
  "latency_ms": 90731.18,
  "timestamp": "2026-06-17 04:26:09"
}
```

## Memory System

**Short-term memory** — tracks thoughts, actions, and observations
within the current session. Cleared on each new goal.

**Long-term memory** — persists across sessions as JSON. Stores goal,
summary, tools used, and success status. Agent recalls similar past
tasks at the start of each new goal.

```json
{
  "goal": "What is the square root of 256?",
  "summary": "The square root of 256 is 16.0.",
  "tools_used": ["calculator"],
  "timestamp": "2026-06-16T06:10:00",
  "success": true
}
```

## Integration with RAG System

The `rag_search` tool connects directly to the
[rag-system](https://github.com/sidn20/rag-system) project,
giving the agent semantic search over local documents.

## What I Learned

- ReAct agent architecture — the pattern behind ChatGPT plugins and AutoGPT
- Tool use and sandboxing — safe execution of LLM-selected actions
- Short and long term memory systems for persistent agents
- Robust JSON parsing from unreliable LLM output
- Prompt engineering for structured agent reasoning
- Connecting multiple projects into one unified system
- FastAPI REST interface for agent access
- Local LLM inference with Ollama — no API keys needed
