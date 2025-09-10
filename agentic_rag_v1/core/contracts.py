
from __future__ import annotations
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
import uuid, time

class MessageRole(str, Enum):
    user = "user"
    agent = "agent"
    tool = "tool"

class Intent(str, Enum):
    lookup = "lookup"
    compare = "compare"
    summarize = "summarize"
    verify = "verify"

class Target(str, Enum):
    finance = "finance"
    patents = "patents"
    web = "web"
    local = "local"   # local KB

class Message(BaseModel):
    role: MessageRole
    content: str
    meta: Dict[str, Any] = Field(default_factory=dict)

class SubQuery(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    text: str
    entities: List[str] = Field(default_factory=list)
    intent: Intent = Intent.lookup
    target: Target = Target.web
    round: int = 0

class RetrievedDoc(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source: str
    url: Optional[str] = None
    text: str = ""
    score: float = 0.0
    metadata: Dict[str, Any] = Field(default_factory=dict)

class Evidence(BaseModel):
    subquery_id: str
    docs: List[RetrievedDoc]

class Citation(BaseModel):
    doc_id: str
    span: str

class DraftAnswer(BaseModel):
    text: str
    citations: List[Citation] = Field(default_factory=list)
    confidence: float = 0.0
    rationale: Dict[str, Any] = Field(default_factory=dict)  # structured reasoning traces

class Critique(BaseModel):
    ok: bool
    issues: List[str] = Field(default_factory=list)
    need_more_retrieval: bool = False

class Budget(BaseModel):
    max_rounds: int = 2
    max_time_s: float = 5.0
    started_at: float = Field(default_factory=time.time)

    def time_left(self) -> float:
        return self.max_time_s - (time.time() - self.started_at)
