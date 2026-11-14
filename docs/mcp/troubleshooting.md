---
title: MCP トラブルシュート
tags: [mcp, troubleshooting]
---

# MCP トラブルシュート

## `ModuleNotFoundError: mcp.server.fastmcp`

### 原因

SDK 2.x では旧 `FastMCP` の import パスが削除されています。

### 解決

`from mcp.server import MCPServer` に変更し、`FastMCP(...)` を `MCPServer(...)` に置き換えます。

## サーバーを起動したのに何も表示されない

stdio transport では標準入出力が MCP の通信路です。サーバーはホストからの要求を待っているため、無表示で待機するのが正常です。`uv run mcp dev server/knowledge_server.py` で Inspector を使って確認します。

## JSON が壊れる

stdio サーバーでは `print()` を使わず、診断出力には `logging`（stderr）を使います。
