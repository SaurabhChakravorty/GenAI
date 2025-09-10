
from __future__ import annotations
from typing import List
from core.contracts import DraftAnswer, Evidence, Critique
from policies.grounding import has_sufficient_evidence, enforce_grounding

def review(draft: DraftAnswer, evidence: List[Evidence]) -> Critique:
    issues = []
    ok_ev = has_sufficient_evidence(evidence, min_docs=1)
    if not ok_ev:
        issues.append("Insufficient evidence.")
    ok_cit = enforce_grounding(draft)
    if not ok_cit:
        issues.append("Insufficient citations for the claims.")
    ok = ok_ev and ok_cit and draft.confidence >= 0.5
    return Critique(ok=ok, issues=issues, need_more_retrieval=(not ok_ev))
