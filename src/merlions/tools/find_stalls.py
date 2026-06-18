"""Tool: find_stalls — wraps the Maps API with input validation and governance."""

from __future__ import annotations

from merlions.governance import govern, load_policy
from merlions.models import InvalidInput, Stall
from merlions.tools.maps import maps_search

_POLICY = load_policy("hawker")


@govern(_POLICY, tool_name="find_stalls")
def find_stalls(location: str, cuisine: str | None = None) -> list[Stall]:
    """Search for hawker stalls near a location. Governed by the hawker policy."""

    if not location or not location.strip():
        raise InvalidInput("location is required")
    return maps_search(location, cuisine)
