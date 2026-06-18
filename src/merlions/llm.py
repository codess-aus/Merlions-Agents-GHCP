"""LLM integration layer — Azure OpenAI with offline mock fallback.

Pattern for trustworthy grounded LLM calls:
  1. Retrieve factual data from a trusted source (tool call or RAG).
  2. Pass that data as context to the LLM prompt (grounding).
  3. Instruct the model to answer *only* from the provided context.
  4. Return the citation alongside the response so it's traceable.

When AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_KEY are set, calls the real
Azure OpenAI service. Otherwise returns deterministic mock responses so
all demos run offline — no API key, no Azure subscription required.

Environment variables:
    AZURE_OPENAI_ENDPOINT   e.g. https://<your-resource>.openai.azure.com
    AZURE_OPENAI_KEY        Your Azure OpenAI API key
    AZURE_OPENAI_DEPLOYMENT Model deployment name (default: gpt-4o)

Swap `urllib.request` for the `openai` SDK in production for streaming
support and richer error types — the pattern stays identical.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass

from merlions.reliability import retry
from merlions.telemetry import span

_ENDPOINT = os.environ.get("AZURE_OPENAI_ENDPOINT", "")
_KEY = os.environ.get("AZURE_OPENAI_KEY", "")
_DEPLOYMENT = os.environ.get("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")

# ---------------------------------------------------------------------------
# Deterministic mock responses — used when env vars are not set.
# Replace with real embeddings / LLM calls in production.
# ---------------------------------------------------------------------------
_MOCKS: dict[str, str] = {
    "hawker": (
        "Try Satay by the Bay at Gardens by the Bay — "
        "chilli stingray is a local favourite tonight."
    ),
    "haze": (
        "PSI is 58 (Moderate) and trending flat. "
        "A short walk is fine — hydrate after. Forecast confidence 84%."
    ),
    "wisecracker": (
        "Why do Python devs love the sea? "
        "Because they prefer high tide and high code quality."
    ),
    "default": "I don't have enough information to answer that confidently.",
}


@dataclass(frozen=True)
class LLMResponse:
    """A governed LLM response — always includes the grounding context used."""

    text: str
    grounded_on: list[str]
    model: str
    mock: bool


@retry(max_attempts=3, base_delay=0.5, exceptions=(urllib.error.URLError, TimeoutError))
def complete(
    *,
    system: str,
    user: str,
    grounded_on: list[str] | None = None,
    max_tokens: int = 300,
    temperature: float = 0.3,
    agent_id: str = "",
) -> LLMResponse:
    """Call Azure OpenAI chat completion (or return a mock if not configured).

    The `grounded_on` parameter is the list of citation keys for the context
    you injected into the prompt. Always pass it — it becomes part of the
    returned `LLMResponse` so callers can attach citations to their reply
    without having to track them separately.

    The function is retry-wrapped (3 attempts, exponential backoff) so
    transient API blips don't surface to the user.

    Governance is the caller's responsibility — call this inside a
    @govern-wrapped function, not raw.

    Args:
        system:       The system prompt. Should instruct the model to answer
                      *only* from the provided context and say 'I don't know'
                      if the context doesn't cover the question.
        user:         The user's question, usually with retrieved context
                      appended (see hawker agent for the pattern).
        grounded_on:  Citation keys for the context you injected.
        max_tokens:   Cap on completion length.
        temperature:  0.0–1.0. Lower = more deterministic (recommended for
                      factual agents like hawker and haze).
        agent_id:     Used to select the right mock response in offline mode.
    """
    with span(
        "llm.complete",
        agent_id=agent_id,
        mock=not bool(_ENDPOINT),
        model=_DEPLOYMENT,
    ):
        citations = grounded_on or []

        if not _ENDPOINT or not _KEY:
            # Offline / demo mode — deterministic, no network required.
            text = _MOCKS.get(agent_id, _MOCKS["default"])
            return LLMResponse(text=text, grounded_on=citations, model="mock", mock=True)

        url = (
            f"{_ENDPOINT}/openai/deployments/{_DEPLOYMENT}"
            f"/chat/completions?api-version=2024-02-01"
        )
        payload = json.dumps(
            {
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                "max_tokens": max_tokens,
                "temperature": temperature,
            }
        ).encode()

        req = urllib.request.Request(
            url,
            data=payload,
            headers={"api-key": _KEY, "Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = json.loads(resp.read())

        text = body["choices"][0]["message"]["content"].strip()
        model_name = body.get("model", _DEPLOYMENT)
        return LLMResponse(
            text=text, grounded_on=citations, model=model_name, mock=False
        )


# ---------------------------------------------------------------------------
# Grounded prompt builders — encapsulate the 'only answer from context' rule.
# ---------------------------------------------------------------------------

HAWKER_SYSTEM = """\
You are the Hawker Recommender — a friendly, knowledgeable Singapore food guide.
Answer ONLY from the provided context. If the context does not contain a clear
recommendation, say 'I don't have a verified option for that right now.'
Keep replies concise (2–3 sentences). Always end with the stall name."""

HAZE_SYSTEM = """\
You are the Haze Tracker — a safety-first air quality assistant for Singapore.
Answer ONLY from the provided PSI data. State the PSI value, the health band,
and one concrete action recommendation. Confidence below 70% must be mentioned.
Never invent a PSI number."""


def hawker_prompt(location: str, stall_info: str) -> str:
    return (
        f"Location: {location}\n\n"
        f"Verified stall data:\n{stall_info}\n\n"
        "Based only on the above, recommend the best dinner option."
    )


def haze_prompt(region: str, psi_info: str) -> str:
    return (
        f"Region: {region}\n\n"
        f"Current PSI data:\n{psi_info}\n\n"
        "Based only on the above, give a safety recommendation."
    )
