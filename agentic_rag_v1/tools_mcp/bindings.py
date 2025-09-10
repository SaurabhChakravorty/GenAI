
from __future__ import annotations
from typing import Callable, Dict, Any

class MCPToolRegistry:
    def __init__(self):
        self._tools: Dict[str, Callable[..., Any]] = {}
    def register(self, name: str, fn: Callable[..., Any]):
        self._tools[name] = fn
    def call(self, name: str, **kwargs):
        if name not in self._tools:
            raise KeyError(f"Tool {name} not registered")
        return self._tools[name](**kwargs)

# Example binding
REGISTRY = MCPToolRegistry()

def tool_search_web(query: str) -> str:
    # placeholder; integrate with your MCP server/client later
    return f"[MCP] would search web for: {query}"

REGISTRY.register("search_web", tool_search_web)
