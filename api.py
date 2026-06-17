import sys
import os
sys.path.insert(0, os.path.expanduser("~/autoagent"))

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from core.agent import Agent
from core.memory import LongTermMemory
from datetime import datetime
import time

app = FastAPI(
    title="AutoAgent API",
    description="Autonomous AI Agent with ReAct loop, tools, and memory",
    version="1.0.0"
)

class GoalRequest(BaseModel):
    goal: str
    max_steps: int = 6
    verbose: bool = False

class GoalResponse(BaseModel):
    goal: str
    result: str
    steps_taken: int
    tools_used: list[str]
    latency_ms: float
    timestamp: str

agent = None
ltm = None
start_time = time.time()
request_log = []

@app.on_event("startup")
async def startup():
    global agent, ltm
    print("Loading AutoAgent...")
    agent = Agent(max_steps=6, verbose=False)
    ltm = LongTermMemory()
    print("AutoAgent ready.")

@app.get("/health")
def health():
    return {
        "status": "ok",
        "uptime_seconds": round(time.time() - start_time, 2),
        "total_requests": len(request_log),
        "memory_sessions": len(ltm.get_all()) if ltm else 0
    }

@app.post("/run", response_model=GoalResponse)
def run_goal(request: GoalRequest):
    if not request.goal.strip():
        raise HTTPException(status_code=400, detail="Goal cannot be empty")

    start = time.perf_counter()
    agent.max_steps = request.max_steps
    result = agent.run(request.goal)
    latency_ms = (time.perf_counter() - start) * 1000

    tools_used = agent.short_term.get_tools_used()
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    request_log.append({
        "goal": request.goal,
        "result": result,
        "tools_used": tools_used,
        "latency_ms": round(latency_ms, 2),
        "timestamp": timestamp
    })

    return GoalResponse(
        goal=request.goal,
        result=result,
        steps_taken=len(agent.history),
        tools_used=tools_used,
        latency_ms=round(latency_ms, 2),
        timestamp=timestamp
    )

@app.get("/memory")
def get_memory():
    entries = ltm.get_all()
    return {
        "total_sessions": len(entries),
        "sessions": [
            {
                "goal": e.goal,
                "summary": e.summary,
                "tools_used": e.tools_used,
                "timestamp": e.timestamp,
                "success": e.success
            }
            for e in entries[-10:]
        ]
    }

@app.get("/metrics")
def metrics():
    if not request_log:
        return {"message": "No requests yet"}
    latencies = [r["latency_ms"] for r in request_log]
    return {
        "total_requests": len(request_log),
        "avg_latency_ms": round(sum(latencies) / len(latencies), 2),
        "min_latency_ms": round(min(latencies), 2),
        "max_latency_ms": round(max(latencies), 2),
        "recent_requests": request_log[-5:]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
