"""`merlions` CLI — drives the demos from a terminal."""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Make stdout UTF-8 so emoji render on Windows code page 1252 consoles.
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
        sys.stderr.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    except Exception:
        pass

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from merlions.agents.router import handle
from merlions.telemetry import TRACE_DIR

app = typer.Typer(help="Merlions — trustworthy multi-agent Python on Azure")
console = Console()


def _print_reply(prompt: str) -> None:
    reply = handle(prompt)
    console.rule("[bold cyan]Merlions reply")
    for part in reply.parts:
        body = Text(part.summary)
        cite_str = "\n".join(f"  [dim]· {c}[/dim]" for c in part.citations) if part.citations else "  [dim](no citation — opinion only)[/dim]"
        console.print(Panel.fit(body, title=f"[bold]{part.agent_id}[/bold]  ·  {part.latency_ms}ms", border_style="cyan"))
        console.print(cite_str)
    console.print(f"\n[green]✓[/green] trace_id=[bold]{reply.trace_id}[/bold]  total={reply.total_latency_ms}ms")


@app.command()
def ask(prompt: str = typer.Argument(..., help="What do you want to ask the Merlions?")) -> None:
    """Send a single prompt to the router and print the composed reply."""

    _print_reply(prompt)


@app.command()
def demo() -> None:
    """Run the canonical Demo 2 composite question end-to-end."""

    prompt = "Dinner near Marina Bay, is the air OK to walk there, and make me laugh."
    console.print(Panel.fit(f"[italic]{prompt}[/italic]", title="User asks", border_style="magenta"))
    _print_reply(prompt)


@app.command()
def traces(last: int = typer.Option(10, help="How many of the most recent trace records to show.")) -> None:
    """Show the most recent App Insights-style trace records."""

    path = TRACE_DIR / "traces.jsonl"
    if not path.exists():
        console.print("[yellow]No traces yet — run `merlions demo` first.[/yellow]")
        raise typer.Exit(code=0)
    lines = path.read_text(encoding="utf-8").splitlines()[-last:]
    table = Table(title="Recent traces", show_lines=False)
    for col in ("name/event", "duration_ms", "trace_id", "span_id", "parent_id", "dims"):
        table.add_column(col, overflow="fold")
    for raw in lines:
        rec = json.loads(raw)
        name = rec.get("name") or rec.get("event", "")
        dur = str(rec.get("duration_ms", ""))
        dims = json.dumps(rec.get("custom_dimensions", {}), separators=(",", ":"))
        table.add_row(
            name,
            dur,
            rec.get("trace_id", "") or "",
            rec.get("span_id", "") or "",
            rec.get("parent_id", "") or "",
            dims,
        )
    console.print(table)


@app.command()
def audit(last: int = typer.Option(10, help="How many audit records to show.")) -> None:
    """Show the most recent governance audit decisions."""

    path = Path(".audit/audit.jsonl")
    if not path.exists():
        console.print("[yellow]No audit records yet — run `merlions demo` first.[/yellow]")
        raise typer.Exit(code=0)
    lines = path.read_text(encoding="utf-8").splitlines()[-last:]
    table = Table(title="Recent governance decisions")
    for col in ("policy", "tool", "decision", "matched_rule"):
        table.add_column(col, overflow="fold")
    for raw in lines:
        rec = json.loads(raw)
        decision = rec["decision"]
        colour = "green" if decision == "allow" else "red"
        table.add_row(rec["policy"], rec["tool"], f"[{colour}]{decision}[/{colour}]", rec.get("matched_rule") or "")
    console.print(table)


@app.command()
def evals(suite: str = typer.Option("hawker"), since: str = typer.Option("yesterday")) -> None:
    """Run the eval suite (synthetic — for demo recording only)."""

    from merlions.evals.runner import run_suite

    run_suite(suite=suite, since=since)


@app.command("harvest-evals")
def harvest_evals() -> None:
    """Convert real policy.deny trace events into regression eval cases."""

    from merlions.evals.from_traces import harvest

    harvest()


@app.command("call-tool")
def call_tool(
    tool: str = typer.Argument(..., help="Tool name, e.g. find_stalls"),
    arg: list[str] = typer.Option([], "--arg", help="Repeatable key=value tool arg, e.g. --arg location=\"marina bay\""),
) -> None:
    """Call a governed tool directly with raw args. Used by Demo 3 to trigger a policy.deny."""

    from merlions.agents import hawker  # noqa: F401  — registers find_stalls

    registry = {
        "find_stalls": hawker.find_stalls,
    }
    if tool not in registry:
        console.print(f"[red]Unknown tool:[/red] {tool}. Known: {list(registry)}")
        raise typer.Exit(code=2)

    kwargs: dict[str, str] = {}
    for pair in arg:
        if "=" not in pair:
            console.print(f"[red]Invalid --arg (need key=value):[/red] {pair}")
            raise typer.Exit(code=2)
        k, v = pair.split("=", 1)
        kwargs[k] = v

    try:
        result = registry[tool](**kwargs)
        console.print(Panel.fit(str(result), title=f"[green]allow[/green] · {tool}", border_style="green"))
    except Exception as exc:  # noqa: BLE001 — demo intentionally surfaces all denials
        console.print(Panel.fit(f"{type(exc).__name__}: {exc}", title=f"[red]deny[/red] · {tool}", border_style="red"))
        raise typer.Exit(code=1) from None


@app.command()
def banner() -> None:
    """Print the Merlions banner (setup shot for demos)."""
    console.print(Panel.fit(
        "[bold cyan]🦁🐟  Merlions[/bold cyan]\n"
        "[dim]Trustworthy multi-agent Python on Azure[/dim]",
        border_style="cyan",
        padding=(1, 4),
    ))


if __name__ == "__main__":
    app()
