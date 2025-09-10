
from __future__ import annotations
import asyncio, time
from typing import Dict, List, Tuple
from core.contracts import SubQuery, DraftAnswer, Critique, Budget
from agents.decomposer import decompose
from agents.aggregator import aggregate
from agents.answer_writer import write_answer
from agents.reviewer import review
from agents.query_rewriter import rewrite
from retrieval.mocks import MockFinanceRetriever, MockPatentRetriever, MockWebRetriever
from retrieval.local_index import LocalIndexRetriever
from pipelines.indexer import load_local_index
from observability.tracing import span, new_trace_id
from policies.guardrails import apply_content_filters, redact_pii, source_allowed

# Load local index if exists
LOCAL_INDEX_PATH = "data/corpus_index.json"
_local_rows = load_local_index(LOCAL_INDEX_PATH)
local_retr = LocalIndexRetriever(index=_local_rows) if _local_rows else None

RETRIEVERS = {
    "finance": MockFinanceRetriever(),
    "patents": MockPatentRetriever(),
    "web": MockWebRetriever(),
    "local": local_retr,
}

async def _retrieve_one(sq: SubQuery, trace_id: str):
    with span("retrieve", trace_id):
        retriever = RETRIEVERS.get(sq.target.value) or RETRIEVERS["web"]
        docs = retriever.retrieve(sq) if retriever else []
        # guardrail: filter sources
        docs = [d for d in docs if source_allowed(d.source)]
        # sanitize
        for d in docs:
            d.text = apply_content_filters(redact_pii(d.text))
        return sq.id, docs

async def run_pipeline(user_query: str, budget: Budget|None=None) -> Tuple[DraftAnswer, Critique, List[SubQuery], str]:
    trace_id = new_trace_id()
    if budget is None: budget = Budget()

    with span("decompose", trace_id):
        subqueries = decompose(user_query)

    rounds = 0
    evidence = None
    draft = None
    critique = None
    current_subqs = subqueries

    while rounds <= budget.max_rounds and budget.time_left() > 0:
        rounds += 1
        # RETRIEVE
        tasks = [_retrieve_one(sq, trace_id) for sq in current_subqs]
        pairs = await asyncio.gather(*tasks)
        by_subq = {sid: docs for sid, docs in pairs}

        # AGGREGATE
        with span("aggregate", trace_id):
            evidence = aggregate(current_subqs, by_subq)

        # WRITE
        with span("write_answer", trace_id):
            draft = write_answer(evidence)

        # REVIEW
        with span("review", trace_id):
            critique = review(draft, evidence)

        if critique.ok:
            break

        # CONDITIONAL EDGE: if need more retrieval, rewrite & loopback
        if critique.need_more_retrieval and rounds <= budget.max_rounds:
            with span("rewrite", trace_id):
                current_subqs = [rewrite(sq) for sq in current_subqs]
            continue
        else:
            break

    return draft, critique, current_subqs, trace_id
