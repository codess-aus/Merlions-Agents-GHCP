"""Lightweight eval runner used by the Demo 3 narrative.

This is intentionally simple — the point of the demo is the *loop*
(real traces → eval cases → CI build), not a sophisticated runner.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

from rich.console import Console

from merlions.agents import hawker
from merlions.governance import reset_call_counter
from merlions.models import InvalidInput

CASES = Path(__file__).parent / "cases.jsonl"

console = Console()


def run_suite(suite: str = "hawker", since: str = "yesterday") -> None:
    """Run the suite, print a CI-style summary, exit non-zero on regressions."""

    cases = [json.loads(line) for line in CASES.read_text(encoding="utf-8").splitlines() if line.strip()]
    cases = [c for c in cases if c["id"].startswith(suite)]
    passed = 0
    regressions: list[str] = []

    started = time.perf_counter()
    for case in cases:
        reset_call_counter()
        expect = case["expect"]
        try:
            reply = hawker.recommend(**case["input"])
        except InvalidInput:
            if expect.get("raises") == "InvalidInput":
                passed += 1
                continue
            regressions.append(f"{case['id']}: unexpected InvalidInput")
            continue

        ok = True
        if (frag := expect.get("cite_contains")) and not any(frag in c for c in reply.citations):
            ok = False
        if (frag := expect.get("summary_contains")) and frag not in reply.summary:
            ok = False
        if (cap := expect.get("p95_ms")) and reply.latency_ms > cap:
            regressions.append(
                f"{case['id']}: latency {reply.latency_ms}ms exceeds cap {cap}ms"
                + (f" (see trace/{case['source_trace']})" if case.get("source_trace") else "")
            )
            ok = False
        if ok:
            passed += 1

    total = len(cases)
    elapsed = round(time.perf_counter() - started, 2)
    console.print(
        f"\n[bold]Hawker eval suite[/bold] · {total} cases · "
        f"[green]{passed} pass[/green] · "
        f"[red]{len(regressions)} regressions[/red] · {elapsed}s"
    )
    for r in regressions:
        console.print(f"  [red]Regression:[/red] {r}")
