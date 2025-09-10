
from __future__ import annotations
from typing import List, Sequence, Tuple
try:
    from rapidfuzz import process, fuzz
    def _extract(query: str, keys: Sequence[str], scorer, limit: int):
        return process.extract(query, keys, scorer=scorer, limit=limit)
except Exception:
    import difflib
    class fuzz:
        @staticmethod
        def token_sort_ratio(a,b): 
            import difflib; aa=" ".join(sorted(a.lower().split())); bb=" ".join(sorted(b.lower().split()))
            return int(difflib.SequenceMatcher(None, aa, bb).ratio()*100)
        @staticmethod
        def WRatio(a,b):
            import difflib; return int(difflib.SequenceMatcher(None, a.lower(), b.lower()).ratio()*100)
        @staticmethod
        def partial_token_set_ratio(a,b):
            import difflib; return int(difflib.SequenceMatcher(None, a.lower(), b.lower()).ratio()*100)
    def _extract(query: str, keys: Sequence[str], scorer, limit: int):
        import difflib
        scored = []
        for k in keys:
            s = difflib.SequenceMatcher(None, query.lower(), k.lower()).ratio()*100
            scored.append((k, s, None))
        scored.sort(key=lambda x:x[1], reverse=True)
        return scored[:limit]

from core.contracts import SubQuery, RetrievedDoc

class MockFinanceRetriever:
    name="finance"
    DB={
        "Tesla revenue 2023":"Tesla reported ~US$97B revenue in 2023 (mock).",
        "BYD revenue 2023":"BYD reported ~US$83B revenue in 2023 (mock).",
    }
    def retrieve(self, subq: SubQuery, k: int=8) -> List[RetrievedDoc]:
        keys=list(self.DB.keys())
        matches=_extract(subq.text, keys, scorer=fuzz.token_sort_ratio, limit=min(k,len(keys)))
        out=[]
        for key,score,_ in matches:
            if score<40: continue
            out.append(RetrievedDoc(source="mock:finance", text=self.DB[key], score=score/100.0))
        return out

class MockPatentRetriever:
    name="patents"
    DB={
        "Tesla patents EU":"Tesla EP filings ~120 (mock).",
        "BYD patents EU":"BYD EP filings ~95 (mock).",
    }
    def retrieve(self, subq: SubQuery, k: int=8) -> List[RetrievedDoc]:
        keys=list(self.DB.keys())
        matches=_extract(subq.text, keys, scorer=fuzz.WRatio, limit=min(k,len(keys)))
        out=[]
        for key,score,_ in matches:
            if score<40: continue
            out.append(RetrievedDoc(source="mock:patents", text=self.DB[key], score=score/100.0))
        return out

class MockWebRetriever:
    name="web"
    DB={
        "Tesla history":"Tesla, Inc. is an American EV company (mock).",
        "BYD profile":"BYD Company Limited is a Chinese conglomerate (mock).",
        "European Union":"EU is a political and economic union (mock).",
    }
    def retrieve(self, subq: SubQuery, k: int=8) -> List[RetrievedDoc]:
        keys=list(self.DB.keys())
        matches=_extract(subq.text, keys, scorer=fuzz.partial_token_set_ratio, limit=min(k,len(keys)))
        out=[]
        for key,score,_ in matches:
            if score<35: continue
            out.append(RetrievedDoc(source="mock:web", text=self.DB[key], score=score/100.0))
        return out
