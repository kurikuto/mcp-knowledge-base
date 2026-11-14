from server import knowledge_server as server
from server.knowledge_server import _make_excerpt


def test_search_finds_sdk_note() -> None:
    matches = server.search_docs("MCP SDK", tag="python")
    assert any(match["path"] == "mcp/python-sdk-v2.md" for match in matches)


def test_get_document_rejects_traversal() -> None:
    try:
        server.get_document("../../README.md")
    except ValueError as error:
        assert "inside the docs directory" in str(error)
    else:
        raise AssertionError("directory traversal must be rejected")


def test_excerpt_matching_line():
    body = """
# 認証設計

この文書はシステム設計について説明します。

ユーザー認証にはOAuth 2.0を使用します。
"""

    result = _make_excerpt(body, ["認証"])

    assert result == "ユーザー認証にはOAuth 2.0を使用します。"


def test_excerpt_fallback():
    body = """
# 設計

最初の説明文です。
次の説明文です。
"""

    result = _make_excerpt(body, ["存在しない"])

    assert result == "最初の説明文です。"


def test_excerpt_empty_body():
    result = _make_excerpt("", ["python"])

    assert result == ""
