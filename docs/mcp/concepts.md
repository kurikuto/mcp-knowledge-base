---
title: MCP の基本概念
tags: [mcp, concepts]
---

# MCP の基本概念

## Tool

モデルが必要に応じて呼び出す操作です。`search_docs` は Tool として公開し、質問に関連するノートを探します。

## Resource

アプリケーション側が読むデータです。このサーバーは `knowledge://docs/{path}` で各 Markdown を Resource template として公開します。

## Transport

ローカル利用は **stdio** が基本です。サーバーをホストする場合は **Streamable HTTP** を使います。新規実装で旧 SSE を選ばないようにします。
