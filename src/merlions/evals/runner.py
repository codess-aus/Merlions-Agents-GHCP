"""Eval runner — drives cases.jsonl against the live agent stack."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import typer
from rich.console import Console
from rich.table import Table

from merlions.agents.hawker import recommend
from merlions.governance import PolicyViolation, reset_call_counter
from merlions.models import InvalidInput

app = typer.Typer(help="Merlions eval runner — real traces become regression tests.")
console = Console()

CASES_FILE = Path(__file__).parent / "cases.jsonl"


def _run_case(case: dict[str, Any]) -> tuple[bool, str]:
    """Run one eval case. Returns (passed, detail)."""

    reset_call_counter()
    inputs = case.get("input", {})
    expect = case.get("expect", {})

    try:
        reply = recommend(**inputs)
    except InvalidInput as exc:
        if expect.get("raises") == "InvalidInput":
            return True, "raises InvalidInput ✓"
        return False, f"unexpected InvalidInput: {exc}"
    except PolicyViolation as exc:
        if expect.get("raises") == "PolicyViolation":
            return True, "raises PolicyViolation ✓"
        return False, f"unexpected PolicyViolation: {exc}"
    except Exception as exc:
        return False, f"unexpected {type(exc).__name__}: {exc}"

    if expected_exc := expect.get("raises"):
        return False, f"expected {expected_exc} but got a reply"

    if cite_fragment := expect.get("cite_contains"):
        if not any(cite_fragment in c for c in reply.citations):
            return False, f"no citation containing '{cite_fragment}'"

    if summary_fragment := expect.get("summary_contains"):
        if summary_fragment.lower() not in reply.summary.lower():
            return False, f"summary missing '{summary_fragment}'"

    if p95 := expect.get("p95_ms"):
        if reply.latency_ms > p95:
            trace_ref = case.get("source_trace", "?")
            return False, f"latency {reply.latency_ms}ms > p95 {p95}ms — see trace/{trace_ref}"

    return True, "ok"


@app.command()
def run(
    suite: str = typer.Option("hawker", help="Which agent suite to evaluate."),
    since: str = typer.Option(None, help="Filter to cases added since this date (e.g. 'yesterday')."),  # noqa: ARG001
) -> None:
    """Run the eval suite against the live agent stack and report regressions."""

    if not CASES_FILE.exists():
        console.print(f"[red]Cases file not found: {CASES_FILE}[/red]")
        raise typer.Exit(code=1)

    all_cases = [
        json.loads(line)
        for line in CASES_FILE.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    suite_cases = [c for c in all_cases if c.get("expect", {}).get("agent", "hawker") == suite]
    if not suite_cases:
        console.print(f"[yellow]No cases found for suite '{suite}'.[/yellow]")
        raise typer.Exit(code=0)

    table = Table(title=f"{suite.title()} eval suite", show_header=True, show_lines=False)
    table.add_column("id", style="dim")
    table.add_column("result")
    table.add_column("detail", overflow="fold")

    passed = 0
    regression_messages: list[str] = []

    for case in suite_cases:
        case_id = case.get("id", "?")
        ok, detail = _run_case(case)
        if ok:
            passed += 1
            table.add_row(case_id, "[green]pass[/green]", detail)
        else:
            regression_messages.append(f"{case_id}: {detail}")
            table.add_row(case_id, "[red]FAIL[/red]", detail)

    console.print(table)
    total = len(suite_cases)
    fail_count = total - passed
    regression_word = "regression" if fail_count == 1 else "regressions"
    summary = f"{suite.title()} eval suite · {total} cases · {passed} pass · {fail_count} {regression_word}"

    if fail_count:
        console.print(f"\n[red]{summary}[/red]")
        for msg in regression_messages:
            console.print(f"  Regression: {msg}")
        raise typer.Exit(code=1)
    else:
        console.print(f"\n[green]{summary}[/green]")