"""Mock Maps tool — deterministic so demos are reproducible."""

from __future__ import annotations

from merlions.models import InvalidInput, Stall
from merlions.telemetry import span

_MOCK_DB: dict[str, list[Stall]] = {
    "marina bay": [
        Stall(
            name="Satay by the Bay",
            centre="Gardens by the Bay",
            cuisine="local",
            signature_dish="chilli stingray",
            distance_m=420,
            source="menu_index/satay-bay/2026-06-13",
        ),
        Stall(
            name="Makansutra Gluttons Bay",
            centre="Esplanade",
            cuisine="local",
            signature_dish="char kway teow",
            distance_m=680,
            source="menu_index/gluttons-bay/2026-06-13",
        ),
    ],
    "chinatown": [
        Stall(
            name="Tian Tian Hainanese Chicken Rice",
            centre="Maxwell Food Centre",
            cuisine="chinese",
            signature_dish="hainanese chicken rice",
            distance_m=120,
            source="menu_index/maxwell-tiantian/2026-06-13",
        ),
    ],
}


def maps_search(location: str, cuisine: str | None = None) -> list[Stall]:
    """Return nearby hawker stalls. Mocked for reproducibility."""

    if not location or not location.strip():
        raise InvalidInput("location is required")
    key = location.strip().lower()
    with span("tool.maps_search", location=key, cuisine=cuisine or ""):
        results = _MOCK_DB.get(key, [])
        if cuisine:
            results = [s for s in results if cuisine.lower() in s.cuisine.lower()]
        return list(results)
