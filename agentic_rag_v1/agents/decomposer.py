
from __future__ import annotations
from typing import List
import re
try:
    import spacy
    _NLP = spacy.load("en_core_web_sm")
except Exception:
    _NLP = None

from core.contracts import SubQuery, Intent, Target

ALIAS = {"EU":"European Union","BYD Co":"BYD"}

def _extract_entities_rule(text: str) -> List[str]:
    cands = re.findall(r"[A-Z][A-Za-z0-9&\.\- ]+", text)
    seen=set(); out=[]
    for c in cands:
        c = ALIAS.get(c.strip(), c.strip())
        if c not in seen:
            out.append(c); seen.add(c)
    return out

def _extract_entities_spacy(text: str) -> List[str]:
    doc = _NLP(text); ents=[]
    for e in doc.ents: ents.append(ALIAS.get(e.text,e.text))
    for ch in doc.noun_chunks:
        if ch.text and ch.text[0].isupper(): ents.append(ALIAS.get(ch.text,ch.text))
    seen=set(); out=[]
    for e in ents:
        if e not in seen: out.append(e); seen.add(e)
    return out

def extract_entities(text: str) -> List[str]:
    if _NLP is not None:
        try: return _extract_entities_spacy(text)
        except Exception: pass
    return _extract_entities_rule(text)

def tag_intent(text: str) -> Intent:
    t = text.lower()
    if "compare" in t or " vs " in t: return Intent.compare
    if "verify" in t or "true" in t or "check if" in t: return Intent.verify
    if any(w in t for w in ["summarize","overview","recap","brief"]): return Intent.summarize
    return Intent.lookup

def router_hint(text: str) -> Target:
    t = text.lower()
    if any(w in t for w in ["revenue","sales","10-k","income","ebitda"]): return Target.finance
    if "patent" in t or "ep" in t or "epo" in t: return Target.patents
    if "local" in t or "knowledge base" in t: return Target.local
    return Target.web

def decompose(user_query: str) -> List[SubQuery]:
    parts = re.split(r"\b(?:and|;| vs )\b|,", user_query, flags=re.I)
    subs: List[SubQuery] = []
    for p in map(str.strip, parts):
        if not p: continue
        subs.append(SubQuery(text=p, entities=extract_entities(p), intent=tag_intent(p), target=router_hint(p)))
    return subs
