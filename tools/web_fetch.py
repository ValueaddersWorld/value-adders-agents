"""Utility tools for Value Adders agents."""

from __future__ import annotations

import re
from html import unescape
from html.parser import HTMLParser
from typing import Iterable

import requests


class _TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._chunks: list[str] = []
        self._ignore_stack: list[str] = []

    def handle_starttag(self, tag: str, attrs: Iterable[tuple[str, str | None]]) -> None:  # noqa: ARG002
        if tag in {"script", "style", "noscript"}:
            self._ignore_stack.append(tag)

    def handle_endtag(self, tag: str) -> None:
        if self._ignore_stack and self._ignore_stack[-1] == tag:
            self._ignore_stack.pop()

    def handle_data(self, data: str) -> None:
        if not self._ignore_stack:
            cleaned = data.strip()
            if cleaned:
                self._chunks.append(cleaned)

    def text(self) -> str:
        return " ".join(self._chunks)


def web_fetch(url: str, query: str | None = None, max_chars: int = 2000) -> str:
    """Fetch a web page and return a cleaned text excerpt.

    Args:
        url: Full URL to retrieve (http/https).
        query: Optional keyword or comma-separated keywords to keep in the excerpt.
        max_chars: Character limit for the returned snippet.

    Returns:
        A cleaned text extract truncated to `max_chars` characters. In case of errors,
        the error message is returned instead.
    """

    try:
        response = requests.get(url, timeout=20)
        response.raise_for_status()
    except Exception as exc:  # noqa: BLE001
        return f"Failed to fetch {url}: {exc}"

    parser = _TextExtractor()
    parser.feed(response.text)
    text = unescape(parser.text())
    text = re.sub(r"\s+", " ", text)

    if query:
        keywords = [kw.strip().lower() for kw in query.split(",") if kw.strip()]
        if keywords:
            sentences = re.split(r"(?<=[.!?])\s+", text)
            filtered: list[str] = []
            for sentence in sentences:
                lower = sentence.lower()
                if any(kw in lower for kw in keywords):
                    filtered.append(sentence)
            if filtered:
                text = " ".join(filtered)

    if len(text) > max_chars:
        text = text[: max_chars - 3].rstrip() + "..."

    return text or "No readable text content detected."


__all__ = ["web_fetch"]
