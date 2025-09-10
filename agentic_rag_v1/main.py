from __future__ import annotations
import os, asyncio
from typing import List

# Pipelines (build/load local index)
from pipelines.indexer import build_local_index

# Orchestrator (decompose → retrieve → aggregate → write → review with spans)
from orchestrator.engine import run_pipeline

# Contracts (budgets, messages)
from core.contracts import Budget, Message, MessageRole

# Memory
from memory.store import ShortTermMemory, VectorMemory

# Observability (top-level span + trace id shown)
from observability.tracing import span, new_trace_id

# MCP tools (demo binding)
from tools_mcp.bindings import REGISTRY


CORPUS_DIR = "data/corpus"
INDEX_PATH = "data/corpus_index.json"
TRACE_LOG = "data/agentic_traces.jsonl"


def ensure_corpus():
    os.makedirs(CORPUS_DIR, exist_ok=True)

    tesla_p = os.path.join(CORPUS_DIR, "tesla.txt")
    byd_p = os.path.join(CORPUS_DIR, "byd.txt")

    if not os.path.exists(tesla_p):
        with open(tesla_p, "w") as f:
            f.write(
                "In 2023, Tesla expanded production capacity and continued growth in Europe. "
                "Tesla patents in the EU focus on battery management and charging systems. "
                "Tesla EP filings increased in 2023."
            )

    if not os.path.exists(byd_p):
        with open(byd_p, "w") as f:
            f.write(
                "BYD reported strong sales growth in 2023, with expansion in European markets. "
                "BYD patents in the EU include innovations in blade batteries and EV platforms."
            )

    # Build (or rebuild) the local index
    build_local_index(CORPUS_DIR, INDEX_PATH)


def tail_trace(file_path: str, n: int = 8) -> List[str]:
    if not os.path.exists(file_path):
        return []
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    return [ln.strip() for ln in lines[-n:]]


async def main():
    # 0) Prepare indexable data
    ensure_corpus()

    # 1) Set up memory
    stm = ShortTermMemory(maxlen=50)
    vmem = VectorMemory()

    # Prime vector memory with a prior Q/A
    vmem.add("Prior: Compare Tesla revenue 2022 and BYD revenue 2022. Answer: Tesla higher than BYD (mock).")

    # 2) Define the user turn and add to memory
    user_query = "Compare Tesla revenue 2023 and BYD revenue 2023, and find EU patents for Tesla"
    stm.add(Message(role=MessageRole.user, content=user_query))

    # Query vector memory for related context
    related = vmem.query(user_query, k=3)

    # 3) Observability trace around the whole request
    trace_id = new_trace_id()
    with span("request", trace_id):
        budget = Budget(max_rounds=2, max_time_s=5.0)

        # Demo MCP tool binding
        mcp_demo = REGISTRY.call("search_web", query="Tesla 2023 revenue site:example.com")

        # Run the orchestrator pipeline
        draft, critique, subqs, inner_trace = await run_pipeline(user_query, budget=budget)

    # 4) Persist assistant response to memory & vector memory
    stm.add(Message(role=MessageRole.agent, content=draft.text))
    vmem.add(f"Q: {user_query}\nA: {draft.text}")

    # 5) Show a compact report
    print("\n=== Agentic RAG (main) ===")
    print("User query:", user_query)

    print("\nRelated memory hits:")
    for r in related:
        print("-", r[:120], "...")

    print("\nSub-queries:")
    for s in subqs:
        print(f"- {s.text} | target={s.target} | round={s.round}")

    print("\nDraft answer:\n", draft.text)
    print("\nCritique:", critique.model_dump())
    print("Trace ID:", inner_trace, "(top-level:", trace_id, ")")
    print("MCP demo:", mcp_demo)

    # 6) Show tail of trace log
    print("\nTrace tail (last few events):")
    for ln in tail_trace(TRACE_LOG, n=10):
        print(ln)


if __name__ == "__main__":
    asyncio.run(main())
