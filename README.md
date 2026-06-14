# Merlions, Agents & Copilot: Trustworthy Python on Azure

## Developer Engagement Lead ANZ & Asia - Microsoft, Michelle Mei Ling Sandford

Building real-world multiagent systems in Python doesn't have to be dry or mysterious! In this lively 30-minute session, you'll meet a cast of Singaporean-inspired Python agents: recommend hawker fare, track haze, and liven things up with a wisecracking Merlion. See how GitHub Copilot can supercharge development, while practical trust patterns and Azure deployment ensure your code stays friendly, robust, and observable, even when things don’t go as planned. Whether you're new to multiagent systems, exploring GitHub Copilot, or eager to represent Singapore in your code, you'll learn strategies for transparency and reliability that are as fun as they are practical.

## What's in this repo

| Path | Purpose |
|---|---|
| `talk/` | Plan, speaker notes, demo scripts, stage cue card |
| `talk/demos/` | Runnable demo scripts + `demo1-before.md` Copilot scaffolding starter |
| `src/merlions/` | The agents — hawker, haze, wisecracker, router |
| `src/merlions/governance.py` | `@govern(policy)` decorator + YAML-loaded policies (fail-closed, audit-logged) |
| `src/merlions/telemetry.py` | App Insights-shaped JSON-lines tracing |
| `src/merlions/policies/*.yaml` | Per-agent allowlists, blocked patterns, rate limits |
| `src/merlions/evals/` | Eval runner + `cases.jsonl` (the "real traces → next build" loop) |
| `tests/` | `pytest` suite covering tools, governance, agents, router |

## Quickstart

```powershell
uv venv
uv pip install -e ".[dev]"
pytest -q                       # 15 tests, all green
merlions demo                   # runs the canonical composite question
merlions audit --last 10        # shows governance decisions
merlions traces --last 12       # shows App Insights-style trace records
```

## Reproduce the talk demos

```powershell
.\talk\demos\demo1.ps1   # green pytest run for find_stalls
.\talk\demos\demo2.ps1   # multi-agent composite question + traces
.\talk\demos\demo3.ps1   # clean trace · policy.deny · audit · evals
```

No API keys, no Azure subscription, no LLM required — all external dependencies are mocked so the demos are reproducible on stage Wi-Fi. Swap the mocks for real services when you're ready to ship.

## Design principles encoded here

- **Fail closed** — ambiguous or unknown → deny, not allow.
- **Policy as configuration** — `policies/*.yaml`, not Python code.
- **Least privilege** — each agent has its own allowlist and rate limit.
- **Audit everything** — every decision logged; raw user content never logged.
- **Refusal is a feature** — agents say "I don't know" instead of hallucinating.
