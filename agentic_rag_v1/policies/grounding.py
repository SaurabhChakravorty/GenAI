
from __future__ import annotations
from typing import List
from core.contracts import Evidence, DraftAnswer

def has_sufficient_evidence(evidence: List[Evidence], min_docs: int=1) -> bool:
    return any(len(ev.docs) >= min_docs for ev in evidence)

def enforce_grounding(draft: DraftAnswer) -> bool:
    # ensure at least one citation per 2 lines of output (simple rule of thumb)
    n_lines = max(1, draft.text.count("\n"))
    return len(draft.citations) >= max(1, n_lines//2)
