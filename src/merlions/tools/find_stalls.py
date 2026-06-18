"""Tool: find_stalls — wraps the Maps API with input validation and governance."""

from __future__ import annotations

from merlions.governance import govern, load_policy
from merlions.models import InvalidInput, Stall
from merlions.tools.maps import maps_search


def find_stalls(location: str, cuisine: str | None = None) -> list[Stall]:
    if not location or not location.strip():
        raise InvalidInput("location is required")
    return maps_search(location=location, cuisine=cuisine)



