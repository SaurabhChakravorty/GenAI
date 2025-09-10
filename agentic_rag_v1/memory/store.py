
from __future__ import annotations
from collections import deque
from typing import List, Tuple
from core.contracts import Message
import math, re

class ShortTermMemory:
    def __init__(self, maxlen=30): self.buf = deque(maxlen=maxlen)
    def add(self, msg: Message): self.buf.append(msg)
    def get(self) -> List[Message]: return list(self.buf)

class VectorMemory:
    def __init__(self): self.vectors: List[Tuple[str, dict]] = []  # (text, bow)
    def _tok(self, t: str): return re.findall(r"[a-z0-9]+", t.lower())
    def _vec(self, t: str):
        bow = {}
        for w in self._tok(t): bow[w] = bow.get(w,0)+1
        return bow
    def add(self, text: str):
        self.vectors.append((text, self._vec(text)))
    def _cos(self, a: dict, b: dict) -> float:
        dot = sum(a.get(k,0)*b.get(k,0) for k in set(a)|set(b))
        na = math.sqrt(sum(v*v for v in a.values())); nb = math.sqrt(sum(v*v for v in b.values()))
        if na==0 or nb==0: return 0.0
        return dot/(na*nb)
    def query(self, text: str, k: int=5) -> List[str]:
        qv = self._vec(text)
        scored = [(self._cos(qv, v), t) for (t,v) in self.vectors]
        scored.sort(reverse=True)
        return [t for s,t in scored[:k]]
