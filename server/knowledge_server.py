"""Read-only MCP access to the Markdown files in ../docs.

Designed for MCP Python SDK 2.x.  The server deliberately uses only the public
MCPServer decorators, making it easy to keep current as the SDK evolves.
"""

from __future__ import annotations

import argparse
import os
import re
from pathlib import Path
from typing import Any
from urllib.parse import unquote

from mcp.server import MCPServer

DEFAULT_DOCS_DIR = Path(__file__).resolve().parents[1] / "docs"
DOCS_DIR = Path(os.environ.get("KNOWLEDGE_DOCS_DIR", DEFAULT_DOCS_DIR)).resolve()
mcp = MCPServer(
    "Knowledge Base",
    instructions="Search and read the project's Markdown knowledge base. "
    "Use search_docs before requesting a document when its path is unknown.",
)


def _markdown_files(directory: Path | None = None) -> list[Path]:
    """Return only Markdown files beneath DOCS_DIR, in stable order."""
    root = directory or DOCS_DIR
    if not root.is_dir():
        return []
    return sorted(path for path in root.rglob("*.md") if path.is_file())


def _safe_path(relative_path: str) -> Path:
    """Resolve a docs-relative path without permitting directory traversal."""
    candidate = (DOCS_DIR / unquote(relative_path).lstrip("/")).resolve()
    try:
        candidate.relative_to(DOCS_DIR)
    except ValueError as exc:
        raise ValueError("path must stay inside the docs directory") from exc
    if candidate.suffix.lower() != ".md":
        raise ValueError("only Markdown (.md) documents are available")
    if not candidate.is_file():
        raise FileNotFoundError(f"document not found: {relative_path}")
    return candidate


def _metadata_and_body(text: str) -> tuple[dict[str, Any], str]:
    """Extract the small YAML front matter subset used by this starter."""
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n?", text, flags=re.DOTALL)
    if not match:
        return {}, text
    metadata: dict[str, Any] = {}
    for line in match.group(1).splitlines():
        key, separator, value = line.partition(":")
        if not separator:
            continue
        value = value.strip().strip('"\'')
        if key.strip() == "tags":
            metadata["tags"] = [tag.strip().strip('"\'') for tag in value.strip("[]").split(",") if tag.strip()]
        else:
            metadata[key.strip()] = value
    return metadata, text[match.end() :]


def _summary(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    metadata, body = _metadata_and_body(text)
    heading = next((line[2:].strip() for line in body.splitlines() if line.startswith("# ")), path.stem)
    return {
        "path": path.relative_to(DOCS_DIR).as_posix(),
        "title": metadata.get("title", heading),
        "tags": metadata.get("tags", []),
    }


def _make_excerpt(body: str, words: list[str]) -> str:
    """Return a line containing a search word, or the first body line."""

    lines = [
        line.strip()
        for line in body.splitlines()
        if line.strip() and not line.startswith("#")
    ]

    for line in lines:
        if any(word in line.casefold() for word in words):
            return line[:240]

    return lines[0][:240] if lines else ""


@mcp.tool()
def search_docs(query: str, tag: str | None = None, limit: int = 10) -> list[dict[str, Any]]:
    """Search Markdown by words in its path, title, tags, and body.

    Args:
        query: One or more words to find. All words must appear somewhere.
        tag: Optional exact tag filter, for example "mcp" or "python".
        limit: Maximum number of results (1 to 50).
    """
    if not query.strip():
        raise ValueError("query must not be empty")
    if not 1 <= limit <= 50:
        raise ValueError("limit must be between 1 and 50")

    words = [word.casefold() for word in query.split()]
    requested_tag = tag.casefold() if tag else None
    results: list[dict[str, Any]] = []
    for path in _markdown_files():
        text = path.read_text(encoding="utf-8")
        metadata, body = _metadata_and_body(text)
        tags = metadata.get("tags", [])
        haystack = " ".join((path.relative_to(DOCS_DIR).as_posix(), str(metadata.get("title", "")), " ".join(tags), body)).casefold()
        if not all(word in haystack for word in words):
            continue
        if requested_tag and requested_tag not in {item.casefold() for item in tags}:
            continue
        summary = _summary(path)
        # excerpt = next((line.strip() for line in body.splitlines() if line.strip() and not line.startswith("#")), "")
        excerpt = _make_excerpt(body, words)
        results.append({**summary, "excerpt": excerpt})
        if len(results) >= limit:
            break
    return results


@mcp.tool()
def get_document(path: str) -> str:
    """Return one Markdown document using its path relative to docs/, e.g. mcp/concepts.md."""
    return _safe_path(path).read_text(encoding="utf-8")


@mcp.tool()
def list_documents(directory: str = "") -> list[dict[str, Any]]:
    """List available Markdown documents, optionally below a docs-relative directory."""
    requested = (DOCS_DIR / directory).resolve()
    try:
        requested.relative_to(DOCS_DIR)
    except ValueError as exc:
        raise ValueError("directory must stay inside the docs directory") from exc
    if not requested.is_dir():
        raise FileNotFoundError(f"directory not found: {directory or '.'}")
    return [_summary(path) for path in _markdown_files(requested)]


@mcp.resource("knowledge://docs/{path}")
def document_resource(path: str) -> str:
    """Read a Markdown document by resource URI, e.g. knowledge://docs/mcp/concepts.md."""
    return get_document(path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Serve the Markdown knowledge base over MCP.")
    parser.add_argument("--transport", choices=["stdio", "streamable-http"], default="stdio")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    if args.transport == "stdio":
        mcp.run()
    else:
        mcp.run(transport="streamable-http", host=args.host, port=args.port)


if __name__ == "__main__":
    main()
