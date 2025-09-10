
from __future__ import annotations
from typing import List, Dict
import re

SAFE_SOURCES_ALLOW = {"mock:finance","mock:patents","mock:web","local:index"}

PROFANITY = {"badword"}  # placeholder

def apply_content_filters(text: str) -> str:
    # very simple profanity mask
    for w in PROFANITY:
        text = re.sub(rf"\b{re.escape(w)}\b", "***", text, flags=re.I)
    return text

def source_allowed(source: str) -> bool:
    return source in SAFE_SOURCES_ALLOW

def redact_pii(text: str) -> str:
    # trivial email/phone redaction
    text = re.sub(r"[\w\.-]+@[\w\.-]+", "[redacted_email]", text)
    text = re.sub(r"\+?\d[\d\- ]{7,}\d", "[redacted_phone]", text)
    return text
