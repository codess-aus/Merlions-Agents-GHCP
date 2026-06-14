# Recording the demos

> All three demos run locally with **no API keys** and **no network**.
> External calls (Maps, NEA PSI, LLM) are mocked so playback is reproducible
> on conference Wi-Fi.

## One-time setup

```powershell
# from repo root
uv venv
uv pip install -e ".[dev]"
pytest -q                  # sanity check — all tests green
```

## Demo 1 — Copilot scaffolds the safe parts (slide 5, ~3 min)

You're recording **your editor**, not the terminal.

1. Open `talk/demos/demo1-before.md` on screen so the audience sees the
   target shape, then close it.
2. Open a new file `src/merlions/agents/hawker_demo.py` empty.
3. Paste in only the imports + `POLICY = load_policy("hawker")` line.
4. Use Copilot Chat / inline to do each of the three steps (prompts in
   `demo1-before.md`). Accept the suggestions one by one.
5. Run `./talk/demos/demo1.ps1` — 5 green tests in the terminal pane.

If recording from scratch is risky, you can record the "happy path"
in advance: type the prompts, accept, run tests, save the clip.

## Demo 2 — Multi-agent composite question (slide 9, ~90s)

```powershell
./talk/demos/demo2.ps1
```

You'll see:
- The router classify intent and dispatch to all 3 agents.
- A composed reply with two cited factual claims + one un-cited pun.
- A `traces` table showing the parent span + child spans + durations.

## Demo 3 — Observability + eval loop (slide 11, ~2 min)

```powershell
./talk/demos/demo3.ps1
```

You'll see:
- A clean request (allow trace).
- A request containing `api_key=...` — the governance decorator denies it
  and the audit log records `matched_rule: blocked_patterns/...`.
- An audit table with one red `deny` row and several green `allow` rows.
- The eval suite running 5 hawker cases with a synthetic regression call-out.

> The "App Insights" portal shots on the slide can be screenshots of the
> `merlions traces` output zoomed in — works fine for the back row.

## Fallbacks

If A/V fails entirely, narrate over the `talk/demos/fallback/*.png`
screenshots you captured during rehearsal. The narration scripts in
`talk/demo-scripts.md` are timed to work with stills too.
