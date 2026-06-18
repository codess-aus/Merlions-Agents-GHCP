"""Haze Tracker Agent.

Reliability pattern demonstrated here:

    FallbackChain: live NEA data → cached snapshot → safe 'unavailable' reply
    @retry:        already applied inside nea_psi_current via the governed wrapper
    idempotency:   alert_dedupe() prevents duplicate notifications per band/day

The FallbackChain means the agent always returns *something* useful —
it never raises an unhandled exception to the user.
"""

from __future__ import annotations

import time

from merlions.governance import govern, load_policy
from merlions.llm import complete, haze_prompt, HAZE_SYSTEM
from merlions.models import AgentReply, PSIReading
from merlions.reliability import FallbackChain
from merlions.telemetry import span
from merlions.tools.nea import alert_dedupe, nea_psi_current, nea_psi_forecast

POLICY = load_policy("haze")


@govern(POLICY, tool_name="nea_psi_current")
def _governed_current(region: str):
    return nea_psi_current(region)  # type: ignore[arg-type]


@govern(POLICY, tool_name="nea_psi_forecast")
def _governed_forecast(region: str, hours_ahead: int):
    return nea_psi_forecast(region, hours_ahead=hours_ahead)  # type: ignore[arg-type]


@govern(POLICY, tool_name="alert_dedupe")
def _governed_dedupe(key: str) -> bool:
    return alert_dedupe(key)


# Cached snapshot — in production this would be a Redis or Cosmos read.
_CACHED_READINGS: dict[str, PSIReading | None] = {}


def check(region: str = "south", hours_ahead: int = 2) -> AgentReply:
    """Report PSI + forecast with a three-tier fallback chain.

    Tier 1 — Live NEA data + LLM-phrased safety recommendation.
    Tier 2 — Cached snapshot (stale data, explicitly flagged).
    Tier 3 — Safe 'unavailable' message (never invents a PSI number).
    """
    started = time.perf_counter()

    with span("agent.haze", region=region, hours_ahead=hours_ahead):

        def _live() -> AgentReply:
            current = _governed_current(region)
            forecast = _governed_forecast(region, hours_ahead)
            trend = (
                "rising" if forecast.psi > current.psi
                else "easing" if forecast.psi < current.psi
                else "flat"
            )
            alert_key = f"{region}:{current.band}:{current.timestamp.date()}"
            _governed_dedupe(alert_key)

            psi_info = (
                f"PSI: {current.psi} ({current.band}), trending {trend}. "
                f"2-hour forecast: {forecast.psi} (confidence {forecast.confidence:.0%})."
            )
            llm = complete(
                system=HAZE_SYSTEM,
                user=haze_prompt(region, psi_info),
                grounded_on=[current.source, forecast.source],
                agent_id="haze",
            )
            return AgentReply(
                agent_id="haze",
                summary=f"🌫️ {llm.text}",
                citations=llm.grounded_on,
                latency_ms=int((time.perf_counter() - started) * 1000),
            )

        def _cached() -> AgentReply:
            cached = _CACHED_READINGS.get(region)
            if cached is None:
                raise RuntimeError("no cached reading available")
            return AgentReply(
                agent_id="haze",
                summary=(
                    f"🌫️ [Cached] PSI was {cached.psi} ({cached.band}) "
                    f"as of {cached.timestamp.strftime('%H:%M')}. "
                    "Live data unavailable — check nea.gov.sg for current readings."
                ),
                citations=[cached.source],
                latency_ms=int((time.perf_counter() - started) * 1000),
            )

        def _unavailable() -> AgentReply:
            return AgentReply(
                agent_id="haze",
                summary=(
                    "🌫️ Air quality data is temporarily unavailable. "
                    "Check nea.gov.sg/weather/air/psi for current readings."
                ),
                citations=[],
                latency_ms=int((time.perf_counter() - started) * 1000),
            )

        return FallbackChain(
            primary=_live,
            fallbacks=[_cached, _unavailable],
            label="haze.check",
        ).run()
