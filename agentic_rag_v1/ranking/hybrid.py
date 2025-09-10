
from __future__ import annotations
from typing import List
from core.contracts import RetrievedDoc
import math, re
from collections import Counter

def _tokenize(t: str) -> List[str]:
    return re.findall(r"[a-z0-9]+", t.lower())

def bm25_score(query: str, doc: str, avgdl: float = 100.0, k1: float = 1.5, b: float = 0.75) -> float:
    # extremely simplified BM25 using only term frequency; no corpus-wide IDF
    q = Counter(_tokenize(query))
    d = Counter(_tokenize(doc))
    dl = sum(d.values())
    score = 0.0
    for term, qf in q.items():
        tf = d.get(term, 0)
        if tf == 0: continue
        idf = 1.5  # constant placeholder
        denom = tf + k1*(1 - b + b*dl/avgdl)
        score += idf * (tf*(k1+1))/denom
    return score

def jaccard(query: str, doc: str) -> float:
    q = set(_tokenize(query)); d = set(_tokenize(doc))
    if not q or not d: return 0.0
    return len(q & d) / len(q | d)

def hybrid_rank(query: str, docs: List[RetrievedDoc]) -> List[RetrievedDoc]:
    rescored = []
    for d in docs:
        s_bm25 = bm25_score(query, d.text)
        s_jac = jaccard(query, d.text)
        s = 0.7*s_bm25 + 0.3*s_jac + 0.05*d.score  # add original score lightly
        rescored.append((s, d))
    rescored.sort(key=lambda x: x[0], reverse=True)
    return [d for s, d in rescored]

def dedup(docs: List[RetrievedDoc]) -> List[RetrievedDoc]:
    seen = set(); out = []
    for d in docs:
        key = (d.source, re.sub(r"\s+"," ", d.text.strip().lower())[:120])
        if key in seen: continue
        seen.add(key); out.append(d)
    return out
