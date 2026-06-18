"""Reliability patterns: @retry with exponential backoff and FallbackChain.

These two building blocks cover the 'Reliability' pillar of trustworthy AI:
  - @retry: transient external-service failures shouldn't surface to the user
  - FallbackChain: multiple data sources, tried in order, logged on each miss

Copy these into your own project — they are framework-agnostic.

Usage examples:

    # Retry an unstable API call, 3 attempts, exponential backoff + jitter
    @retry(max_attempts=3, exceptions=(TimeoutError, ConnectionError))
    def call_maps_api(location: str) -> dict: ...

    # Try live data → cached data → hardcoded safe default
    result = FallbackChain(
        primary=lambda: nea_live(),
        fallbacks=[lambda: nea_cached(), lambda: nea_unavailable_message()],
        label="nea_psi",
    ).run()
"""

from __future__ import annotations

import functools
import random
import time
from collections.abc import Callable, Sequence
from typing import Any, TypeVar

F = TypeVar("F", bound=Callable[..., Any])


def retry(
    max_attempts: int = 3,
    base_delay: float = 0.5,
    max_delay: float = 10.0,
    backoff: float = 2.0,
    jitter: float = 0.1,
    exceptions: tuple[type[Exception], ...] = (Exception,),
) -> Callable[[F], F]:
    """Retry with exponential backoff and additive jitter.

    Args:
        max_attempts:  Maximum total calls (including the first one).
        base_delay:    Wait time after the first failure, in seconds.
        max_delay:     Cap on the wait time before jitter, in seconds.
        backoff:       Multiplier applied on each subsequent failure.
        jitter:        Fraction of the delay added as random noise to avoid
                       thundering-herd when many callers retry simultaneously.
        exceptions:    Only retry on these exception types. Anything else
                       propagates immediately (fail-closed for surprises).

    The effective wait before attempt N (0-indexed) is:
        delay = min(base_delay * backoff**N, max_delay)
        delay += uniform(0, jitter * delay)
    """

    def decorator(fn: F) -> F:
        @functools.wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exc: Exception | None = None
            for attempt in range(max_attempts):
                try:
                    return fn(*args, **kwargs)
                except exceptions as exc:
                    last_exc = exc
                    if attempt == max_attempts - 1:
                        break
                    delay = min(base_delay * (backoff**attempt), max_delay)
                    delay += random.uniform(0, jitter * delay)
                    time.sleep(delay)
            assert last_exc is not None
            raise last_exc

        return wrapper  # type: ignore[return-value]

    return decorator


class FallbackChain:
    """Try callables in order; return the first that succeeds.

    Each miss is logged as a structured event so you can see in App Insights
    how often you're falling back and why. The final fallback should always
    succeed (e.g. a hardcoded safe default) to prevent unhandled exceptions.

    Args:
        primary:    First callable to try (e.g. live API call).
        fallbacks:  Ordered sequence of alternatives (e.g. cached data, then
                    a hardcoded 'unavailable' message).
        label:      Identifies this chain in telemetry (e.g. 'nea_psi').

    Example — three-tier PSI data chain:

        def _live() -> PSIReading:
            return nea_api.get_current(region)

        def _cached() -> PSIReading:
            return cache.get(f"psi:{region}")  # may also raise

        def _unavailable() -> PSIReading:
            return PSIReading(..., psi=0, band="Unknown", source="unavailable")

        reading = FallbackChain(_live, [_cached, _unavailable], label="psi").run()
    """

    def __init__(
        self,
        primary: Callable[[], Any],
        fallbacks: Sequence[Callable[[], Any]],
        *,
        label: str = "",
    ) -> None:
        self._chain: list[Callable[[], Any]] = [primary, *fallbacks]
        self.label = label

    def run(self) -> Any:
        from merlions.telemetry import emit_event

        last_exc: Exception | None = None
        for tier, fn in enumerate(self._chain):
            try:
                result = fn()
                if tier > 0:
                    emit_event("fallback.success", label=self.label, tier=tier)
                return result
            except Exception as exc:  # noqa: BLE001
                last_exc = exc
                emit_event(
                    "fallback.miss",
                    label=self.label,
                    tier=tier,
                    reason=type(exc).__name__,
                )
        # All options exhausted — re-raise the last error.
        assert last_exc is not None
        raise last_exc
