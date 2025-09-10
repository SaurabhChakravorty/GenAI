
from __future__ import annotations
from fastapi import FastAPI
from pydantic import BaseModel
import asyncio
from orchestrator.engine import run_pipeline
from core.contracts import Budget

app = FastAPI(title="Agentic RAG API")

class AskReq(BaseModel):
    query: str
    max_rounds: int = 2
    max_time_s: float = 5.0

@app.post("/ask")
async def ask(req: AskReq):
    draft, critique, subqs, trace_id = await run_pipeline(req.query, budget=Budget(max_rounds=req.max_rounds, max_time_s=req.max_time_s))
    return {
        "trace_id": trace_id,
        "subqueries": [s.model_dump() for s in subqs],
        "answer": draft.model_dump(),
        "critique": critique.model_dump(),
    }
