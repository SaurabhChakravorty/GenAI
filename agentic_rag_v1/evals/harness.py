
from __future__ import annotations
import asyncio, json, time
from orchestrator.engine import run_pipeline
from core.contracts import Budget

EVALS = [
    {"q": "Compare Tesla revenue 2023 and BYD revenue 2023", "must": ["Tesla reported", "BYD reported"]},
    {"q": "Find EU patents for Tesla", "must": ["Tesla EP filings"]},
]

async def run_evals():
    results = []
    for item in EVALS:
        draft, critique, _, trace = await run_pipeline(item["q"], budget=Budget(max_rounds=2, max_time_s=5))
        ok = all(m in draft.text for m in item["must"])
        results.append({"query": item["q"], "ok": ok, "critique": critique.model_dump(), "trace_id": trace})
    return results

if __name__ == "__main__":
    out = asyncio.run(run_evals())
    print(json.dumps(out, indent=2))
