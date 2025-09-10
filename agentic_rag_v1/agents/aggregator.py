
from __future__ import annotations
from typing import Dict, List
from core.contracts import Evidence, RetrievedDoc, SubQuery
from ranking.hybrid import hybrid_rank, dedup

def aggregate(subqueries: List[SubQuery], by_subq: Dict[str, List[RetrievedDoc]]) -> List[Evidence]:
    evidences: List[Evidence] = []
    for sq in subqueries:
        docs = by_subq.get(sq.id, [])
        docs = hybrid_rank(sq.text, docs)
        docs = dedup(docs)
        evidences.append(Evidence(subquery_id=sq.id, docs=docs[:3]))
    return evidences
