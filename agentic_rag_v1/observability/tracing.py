
from __future__ import annotations
import time, json, uuid, os
from contextlib import contextmanager

LOG_PATH = "data/agentic_traces.jsonl"

def _write(event: dict):
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(event) + "\n")

@contextmanager
def span(name: str, trace_id: str):
    start = time.time()
    eid = str(uuid.uuid4())
    _write({"trace_id": trace_id, "event":"start", "span": name, "id": eid, "ts": start})
    try:
        yield {"id": eid, "trace_id": trace_id}
        dur = time.time() - start
        _write({"trace_id": trace_id, "event":"end", "span": name, "id": eid, "dur_s": dur})
    except Exception as e:
        _write({"trace_id": trace_id, "event":"error", "span": name, "id": eid, "err": str(e)})
        raise

def new_trace_id() -> str:
    return str(uuid.uuid4())
