"""Hawker Recommender Agent.

Full trust pattern demonstrated here:

    tool call (governed, typed)
    → retrieval  (similarity search over verified menu index)
    → grounding  (inject retrieved context into the LLM prompt)
    → LLM call   (retry-wrapped, answers ONLY from provided context)
    → cite       (source keys attached to every factual claim)

Copy this pattern into your own agents. The key guarantee:
every factual sentence in the reply is traceable to a source
your team controls.
"""

from __future__ import annotations

import time

from merlions.governance import govern, load_policy
from merlions.llm import HAWKER_SYSTEM, LLMResponse, complete, hawker_prompt
from merlions.models import AgentReply, InvalidInput
from merlions.reliability import FallbackChain
from merlions.telemetry import span
from merlions.tools.find_stalls import find_stalls
from merlions.tools.menu_index import menu_index_search

POLICY = load_policy("hawker")


@govern(POLICY, tool_name="menu_index_search")
def _governed_menu_search(query: str):
    return menu_index_search(query, top_k=1)


def recommend(location: str, cuisine: str | None = None) -> AgentReply:
    """Recommend a stall with a grounded, cited LLM response.

    Steps:
      1. find_stalls() — governed tool call for location data
      2. menu_index_search() — similarity search for verified menu context
      3. FallbackChain — if live tools fail, fall back to a safe message
      4. complete() — LLM call grounded in retrieved context, retry-wrapped
      5. Return AgentReply with citations from the retrieval step
    """
    started = time.perf_counter()

    with span("agent.hawker", location=location, cuisine=cuisine or ""):

        def _live() -> tuple[str, list[str]]:
            """Primary: tool call + RAG + LLM."""
            stalls = find_stalls(location=location, cuisine=cuisine)
            if not stalls:
                raise InvalidInput(f"no verified stall near {location!r}")

            top = stalls[0]
            query = f"{location} {cuisine or ''} {top.signature_dish}"
            snippets = _governed_menu_search(query=query)

            if not snippets:
                raise InvalidInput(f"no menu data for {top.name}")

            context = "\n".join(s.text for s in snippets)
            citations = [s.source for s in snippets]

            llm: LLMResponse = complete(
                system=HAWKER_SYSTEM,
                user=hawker_prompt(location, context),
                grounded_on=citations,
                agent_id="hawker",
            )
            return llm.text, llm.grounded_on

        def _unavailable() -> tuple[str, list[str]]:
            """Last resort: honest refusal — never hallucinate a stall."""
            return (
                f"I don't have a verified stall near {location!r} right now. "
                "Try a more specific area or check makansutra.com.",
                [],
            )

        summary, citations = FallbackChain(
            primary=_live,
            fallbacks=[_unavailable],
            label="hawker.recommend",
        ).run()

        return AgentReply(
            agent_id="hawker",
            summary=f"🍜 {summary}",
            citations=citations,
            latency_ms=int((time.perf_counter() - started) * 1000),
        )
