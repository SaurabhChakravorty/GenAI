
from __future__ import annotations
from typing import List, Dict
from core.contracts import SubQuery, RetrievedDoc
from ranking.hybrid import bm25_score, jaccard

class LocalIndexRetriever:
    name="local"
    def __init__(self, index: List[Dict]):
        self.index = index  # list of {'text':..., 'meta':..., 'source':...}
    def retrieve(self, subq: SubQuery, k: int=8) -> List[RetrievedDoc]:
        scored = []
        for row in self.index:
            s = 0.7*bm25_score(subq.text, row["text"]) + 0.3*jaccard(subq.text, row["text"])
            scored.append((s, row))
        scored.sort(key=lambda x:x[0], reverse=True)
        out=[]
        for s,row in scored[:k]:
            out.append(RetrievedDoc(source=row.get("source","local:index"), text=row["text"], score=float(s), metadata=row.get("meta",{})))
        return out
