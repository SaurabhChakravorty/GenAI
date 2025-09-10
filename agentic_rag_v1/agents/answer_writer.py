
from __future__ import annotations
from typing import List, Dict, Any
from core.contracts import DraftAnswer, Evidence, Citation

def write_answer(evidence: List[Evidence]) -> DraftAnswer:
    lines: List[str] = []
    citations: List[Citation] = []
    rationale: Dict[str, Any] = {"steps": []}

    for ev in evidence:
        step = {"subquery_id": ev.subquery_id, "docs_used": 0}
        for doc in ev.docs:
            lines.append(f"- {doc.text} [source: {doc.source}]")
            citations.append(Citation(doc_id=doc.id, span=doc.text[:80]))
            step["docs_used"] += 1
        rationale["steps"].append(step)

    text = "Based on evidence:\n" + "\n".join(lines) if lines else "No evidence available."
    confidence = 0.6 if lines else 0.1
    return DraftAnswer(text=text, citations=citations, confidence=confidence, rationale=rationale)
