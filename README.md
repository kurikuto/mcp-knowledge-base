# MCP Knowledge Base Starter

Obsidian で日々書く Markdown を、次の 2 つの入口からそのまま利用するための最小構成です。

1. **Zensical**: 人間がブラウザーで読む静的ドキュメントサイト
2. **Knowledge MCP**: AI クライアントが検索・閲覧するローカル MCP サーバー

Markdown の正本は `docs/` だけです。Obsidian ではこのリポジトリを Vault として開いてください。Zensical の生成物 `site/` と Obsidian の設定 `.obsidian/` は Git の対象外です。

## すぐに試す

前提: Python 3.11 以上と [uv](https://docs.astral.sh/uv/) をインストール済みであること。

```powershell
uv sync
uv run zensical serve
```

表示された `http://127.0.0.1:8000` を開きます。静的ファイルを作るだけなら `uv run zensical build` です（出力先: `site/`）。

## MCP サーバー

ローカルの AI クライアントには、次の起動定義を登録します。`C:/path/to/...` は、このリポジトリの絶対パスに置き換えてください。

```json
{
  "mcpServers": {
    "knowledge-base": {
      "command": "uv",
      "args": ["run", "python", "server/knowledge_server.py"],
      "cwd": "C:/path/to/mcp-knowledge-base"
    }
  }
}
```

サーバーは stdio を使います。直接 `uv run python server/knowledge_server.py` を実行すると、何も表示されず入力待ちになるのが正常です。動作確認には次を使えます（Node.js / `npx` が必要です）。

```powershell
uv run mcp dev server/knowledge_server.py
```

公開用には同じサーバーを Streamable HTTP でも起動できます。

```powershell
uv run python server/knowledge_server.py --transport streamable-http --port 8000
```

エンドポイントは `http://127.0.0.1:8000/mcp` です。公開する場合は認証・TLS・ネットワーク制限を別途必ず設定してください。

### MCP Inspector で確認する

MCP の tools / resources をブラウザーから確認するには、リポジトリのルートで次を実行します。Node.js と `npx` が必要です。

```bash
npx @modelcontextprotocol/inspector .venv/bin/python ./server/knowledge_server.py
```

表示された Inspector の URL をブラウザーで開き、`search_docs`、`get_document`、`list_documents` などを実行できます。先に `uv sync` を実行して `.venv` を作成してください。

### テストを実行する

リポジトリのルートで次を実行します。

```bash
uv run pytest
```

テスト対象は `tests/` 配下です。

### 提供する機能

- `search_docs(query, tag?, limit?)`: タイトル・本文・front matter のタグを検索
- `get_document(path)`: `docs/` からの相対パスで本文を取得
- `list_documents(directory?)`: Markdown の一覧を取得
- `knowledge://docs/{path}`: 個別 Markdown の Resource template

検索は依存を増やさない単純な全文検索です。ノート量が大きくなったら、SQLite FTS やベクトル検索の実装に差し替えられます。

## ノートの書き方

```markdown
---
title: MCP Python SDK 2.x のメモ
tags: [mcp, python, sdk]
---

# MCP Python SDK 2.x のメモ

観察したこと、再現条件、解決方法を追記する。
```

`docs/notes/` に日付単位、`docs/mcp/` に再利用する知見という分け方を推奨します。Obsidian 固有の `[[wikilink]]` は Web 側でリンクとして解決されないことがあるため、共有したいリンクには通常の Markdown リンクを使ってください。

## MCP SDK 2.x について

このサンプルは `mcp>=2,<3` を対象に、`from mcp.server import MCPServer` と `mcp.run()` を使用します。旧 SDK 1.x の `FastMCP` / `mcp.server.fastmcp` は使いません。ツールの型ヒントから入力スキーマが生成されます。

## Git と公開

```powershell
git init
git add .
git commit -m "Create knowledge base"
```

`main` ブランチへ push すると GitHub Actions が Zensical をビルドし、GitHub Pages にデプロイします。最初にリポジトリの **Settings → Pages → Build and deployment → Source** を **GitHub Actions** に変更してください。`zensical.toml` の `site_url` も実際の Pages URL に更新します。

## 構成

```text
docs/                 # Obsidian / Zensical / MCP で共有する正本
server/knowledge_server.py
zensical.toml
pyproject.toml
.github/workflows/docs.yml
```

## ライセンス

必要に応じて、このテンプレートに組織のライセンスを追加してください。
