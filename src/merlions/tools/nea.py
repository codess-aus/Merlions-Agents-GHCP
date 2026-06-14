"""Mock NEA PSI tool — deterministic readings + fallback chain."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal

from merlions.models import InvalidInput, PSIReading
from merlions.telemetry import span

Region = Literal["north", "south", "east", "west", "central"]

_BANDS = [
    (50, "Good"),
    (100, "Moderate"),
    (200, "Unhealthy"),
    (300, "Very Unhealthy"),
    (10_000, "Hazardous"),
]


def _band(psi: int) -> str:
    for ceiling, name in _BANDS:
        if psi <= ceiling:
            return name
    return "Hazardous"


_MOCK_READINGS: dict[str, int] = {
    "north": 48,
    "south": 58,
    "east": 62,
    "west": 71,
    "central": 55,
}


def nea_psi_current(region: Region) -> PSIReading:
    """Current PSI for a region. Mocked."""

    if region not in _MOCK_READINGS:
        raise InvalidInput(f"unknown region: {region}")
    with span("tool.nea_psi_current", region=region):
        psi = _MOCK_READINGS[region]
        return PSIReading(
            region=region,
            psi=psi,
            band=_band(psi),  # type: ignore[arg-type]
            timestamp=datetime.now(timezone.utc),
            confidence=1.0,
            source=f"nea.gov.sg/psi/{datetime.now(timezone.utc).isoformat(timespec='minutes')}",
        )


def nea_psi_forecast(region: Region, hours_ahead: int = 2) -> PSIReading:
    """Simple synthetic forecast with explicit confidence."""

    if hours_ahead < 1 or hours_ahead > 12:
        raise InvalidInput("hours_ahead must be 1..12")
    current = nea_psi_current(region)
    with span("tool.nea_psi_forecast", region=region, hours_ahead=hours_ahead):
        # Trend assumption: small uniform drift, lower confidence further out.
        projected = max(0, current.psi + (hours_ahead - 1))
        confidence = max(0.4, 1.0 - 0.08 * hours_ahead)
        return PSIReading(
            region=region,
            psi=projected,
            band=_band(projected),  # type: ignore[arg-type]
            timestamp=current.timestamp,
            confidence=round(confidence, 2),
            source=current.source + f"#forecast+{hours_ahead}h",
        )


_seen_alerts: set[str] = set()


def alert_dedupe(key: str) -> bool:
    """Return True if this alert is new (and remember it). Idempotency hook."""

    if not key:
        raise InvalidInput("dedupe key required")
    with span("tool.alert_dedupe", key=key):
        if key in _seen_alerts:
            return False
        _seen_alerts.add(key)
        return True


def reset_alert_dedupe() -> None:
    _seen_alerts.clear()
