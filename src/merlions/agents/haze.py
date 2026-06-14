"""Haze Tracker Agent.

Pattern: ingest → forecast → alert (with idempotency + fallback).
"""

from __future__ import annotations

import time

from merlions.governance import govern, load_policy
from merlions.models import AgentReply
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


def check(region: str = "south", hours_ahead: int = 2) -> AgentReply:
    """Report current PSI + a near-term forecast, with idempotent alerting."""

    started = time.perf_counter()
    with span("agent.haze", region=region, hours_ahead=hours_ahead):
        current = _governed_current(region)
        forecast = _governed_forecast(region, hours_ahead)

        trend = "rising" if forecast.psi > current.psi else (
            "easing" if forecast.psi < current.psi else "flat"
        )
        alert_key = f"{region}:{current.band}:{current.timestamp.date()}"
        is_new = _governed_dedupe(alert_key)

        bits = [
            f"🌫️ PSI is {current.psi} ({current.band}) and trending {trend}.",
        ]
        if current.band in {"Unhealthy", "Very Unhealthy", "Hazardous"} and is_new:
            bits.append("Mask up if heading out.")
        elif current.band == "Moderate":
            bits.append("A short walk is fine — hydrate after.")
        else:
            bits.append("Air quality is good.")
        bits.append(f"Forecast confidence {forecast.confidence:.0%}.")

        return AgentReply(
            agent_id="haze",
            summary=" ".join(bits),
            citations=[current.source, forecast.source],
            latency_ms=int((time.perf_counter() - started) * 1000),
        )
