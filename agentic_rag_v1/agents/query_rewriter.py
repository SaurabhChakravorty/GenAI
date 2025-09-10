
from __future__ import annotations
from core.contracts import SubQuery, Target

EXPANSIONS = {
    "revenue": ["sales", "turnover"],
    "patent": ["EP filings", "European Patent"],
    "EU": ["European Union", "Europe"],
}

def rewrite(subq: SubQuery) -> SubQuery:
    text = subq.text
    for k, vals in EXPANSIONS.items():
        if k.lower() in text.lower():
            text += " " + " ".join(vals[:1])
    # escalate router to web if local/patents/finance failed previously
    new_target = subq.target
    if subq.round >= 1 and subq.target in (Target.finance, Target.patents):
        new_target = Target.web
    return SubQuery(text=text, entities=subq.entities, intent=subq.intent, target=new_target, round=subq.round+1)
