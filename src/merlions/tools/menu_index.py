"""Mock RAG menu index — returns grounded menu snippets for citation."""

from __future__ import annotations

from dataclasses import dataclass

from merlions.telemetry import span


@dataclass(frozen=True)
class MenuSnippet:
    stall_source: str
    text: str


_INDEX: list[MenuSnippet] = [
    MenuSnippet(
        stall_source="menu_index/satay-bay/2026-06-13",
        text="Satay by the Bay tonight: chilli stingray, satay platter, chendol.",
    ),
    MenuSnippet(
        stall_source="menu_index/maxwell-tiantian/2026-06-13",
        text="Tian Tian Hainanese Chicken Rice — open 10am-7:30pm, signature poached chicken.",
    ),
    MenuSnippet(
        stall_source="menu_index/gluttons-bay/2026-06-13",
        text="Gluttons Bay features char kway teow, sambal stingray, oyster omelette.",
    ),
]


def menu_index_search(stall_source: str) -> MenuSnippet | None:
    """Look up the verified menu snippet for a stall source key."""

    with span("tool.menu_index_search", stall_source=stall_source):
        for snippet in _INDEX:
            if snippet.stall_source == stall_source:
                return snippet
        return None
