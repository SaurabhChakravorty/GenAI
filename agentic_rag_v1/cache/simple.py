
from __future__ import annotations
from functools import lru_cache

# Exemplary usage placeholder; in real use you'd key by normalized query.
@lru_cache(maxsize=256)
def cached_result(key: str) -> str:
    return key[::-1]  # dummy
