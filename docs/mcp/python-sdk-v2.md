---
title: Python MCP SDK 2.x
tags: [mcp, python, sdk, migration]
---

# Python MCP SDK 2.x

SDK 2.x では、高レベルサーバーの名前が `FastMCP` から `MCPServer` になりました。

```python
from mcp.server import MCPServer

mcp = MCPServer("Knowledge Base")

@mcp.tool()
def hello(name: str) -> str:
    return f"Hello, {name}!"

if __name__ == "__main__":
    mcp.run()  # stdio が既定
```

## 移行時の確認点

| SDK 1.x | SDK 2.x |
| --- | --- |
| `from mcp.server.fastmcp import FastMCP` | `from mcp.server import MCPServer` |
| `FastMCP(...)` | `MCPServer(...)` |
| `mcp.server.fastmcp.*` | `mcp.server.mcpserver.*` |

起動方法（transport、port など）は `MCPServer(...)` のコンストラクタではなく `mcp.run(...)` に渡します。
