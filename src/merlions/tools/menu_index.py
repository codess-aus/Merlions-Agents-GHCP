"""RAG menu index — grounded snippet retrieval with similarity ranking.

In production, replace _score() with cosine similarity over real embeddings
(e.g. Azure AI Search, pgvector, or Chroma). The interface stays identical —
the rest of the system doesn't know or care how ranking works.

Pattern:
    snippets = menu_index_search("chilli stingray Marina Bay", top_k=2)
    context = "\\n".join(s.text for s in snippets)
    citations = [s.source for s in snippets]
    # → pass context + citations to the LLM prompt
"""

from __future__ import annotations

from dataclasses import dataclass

from merlions.telemetry import span


@dataclass(frozen=True)
class MenuSnippet:
    source: str   # citation key — always returned with the snippet
    text: str


_INDEX: list[MenuSnippet] = [
    MenuSnippet(
        source="menu_index/satay-bay/2026-06-13",
        text="Satay by the Bay tonight: chilli stingray, satay platter, chendol. "
             "Located at Gardens by the Bay, open until 10pm.",
    ),
    MenuSnippet(
        source="menu_index/maxwell-tiantian/2026-06-13",
        text="Tian Tian Hainanese Chicken Rice at Maxwell Food Centre — "
             "open 10am-7:30pm, signature poached chicken, famous queue.",
    ),
    MenuSnippet(
        source="menu_index/gluttons-bay/2026-06-13",
        text="Makansutra Gluttons Bay at Esplanade: char kway teow, "
             "sambal stingray, oyster omelette. Outdoor seating by the bay.",
    ),
]


def _score(query: str, text: str) -> float:
    """Word-overlap (Jaccard) similarity.

    Swap this for cosine similarity over embeddings in production:

        import numpy as np
        q_vec = embed(query)       # float32 array from your embedding model
        t_vec = embed(text)
        return float(np.dot(q_vec, t_vec) /
                     (np.linalg.norm(q_vec) * np.linalg.norm(t_vec)))
    """
    q_words = set(query.lower().split())
    t_words = set(text.lower().split())
    if not q_words or not t_words:
        return 0.0
    return len(q_words & t_words) / len(q_words | t_words)


def menu_index_search(query: str, *, top_k: int = 2) -> list[MenuSnippet]:
    """Return the top-k most relevant snippets for a free-text query.

    Every returned snippet includes a `source` citation key.
    Pass those keys through to `AgentReply.citations` so the response is
    traceable back to a verified data source.
    """
    with span("tool.menu_index_search", query=query, top_k=top_k):
        ranked = sorted(_INDEX, key=lambda s: _score(query, s.text), reverse=True)
        return ranked[:top_k]


def menu_index_get(source: str) -> MenuSnippet | None:
    """Exact lookup by citation key — use when you already know the source."""
    with span("tool.menu_index_get", source=source):
        return next((s for s in _INDEX if s.source == source), None)
