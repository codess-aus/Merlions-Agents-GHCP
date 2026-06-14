# Recording the demos — step-by-step walkthrough

> Up front: **nothing needs to be deployed to Azure.** Every external call
> (Maps, NEA PSI, menu lookup, LLM) is mocked, so the demos run locally
> with zero cloud spend and zero Wi-Fi risk on stage. Azure shows up only
> as *talking points* on slides 10 and 11.

---

## Phase 0 — Local setup (one time, ~5 minutes)

Open PowerShell in the repo root.

```powershell
# 1. Pull latest (skip if you cloned fresh)
cd <repo>
git pull

# 2. Create a virtual env with uv
uv venv

# 3. Install the package + dev tools (editable)
uv pip install -e ".[dev]"

# 4. Sanity check — all 15 tests should be green
.venv\Scripts\python -m pytest -q
```

If you see `15 passed`, you're done. **No Azure resources required.**

> If you ever want to show real Azure later, the slide-10 architecture is
> Azure Container Apps + Cosmos DB + Key Vault + Application Insights.
> For the talk demos as designed, none of it is needed.

---

## Phase 1 — Smoke-test all three demos before recording (~3 minutes)

```powershell
.\talk\demos\demo1.ps1
.\talk\demos\demo2.ps1
.\talk\demos\demo3.ps1
```

If PowerShell complains about execution policy, set it once for your user:

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

If all three print output without a stack trace, you're ready to record.

---

## 🎬 DEMO 1 — Copilot scaffolds a tool + guardrail + tests
**Slide 5 · ~3 min · Record your editor (not just the terminal)**

The finished code already lives in `src/merlions/agents/hawker.py` — the
recording shows Copilot writing the equivalent into a *new* file beside it.

### Before you hit record
1. Open VS Code at the repo root.
2. Open `talk/demos/demo1-before.md` in a side pane — it has the three Copilot prompts you'll read aloud.
3. Confirm Copilot Chat is signed in and responsive (test once with any prompt).
4. Open a terminal pane at the bottom of VS Code so the test run is visible without app-switching.
5. Bump editor + terminal font to **16pt+**, use a light theme for projector contrast.
6. Hide notifications, Slack, calendar pop-ups, etc.

### Step-by-step recording

**Step A — Set the stage (10s)**
Show the file tree on the left. Briefly hover over `src/merlions/agents/hawker.py` and `tests/test_find_stalls.py` so the audience sees the structure.

**Step B — Create the empty file (15s)**
- Right-click `src/merlions/agents/` → New File → `hawker_demo.py`
- Paste only this seed:
  ```python
  from merlions.governance import govern, load_policy
  from merlions.models import Stall
  from merlions.tools.maps import maps_search

  POLICY = load_policy("hawker")
  ```

**Step C — Ask Copilot to write the tool (45s)**
- Open Copilot Chat inline (Ctrl+I) inside the new file.
- Type **prompt #1** from `demo1-before.md`:
  > *"Implement `find_stalls(location: str, cuisine: str | None = None) -> list[Stall]` that calls `maps_search`. Validate location is non-empty. Raise `InvalidInput` on bad input."*
- Accept the suggestion. Pause on screen so the audience reads the typed signature.

**Step D — Add the guardrail (45s)**
- Inline **prompt #2**:
  > *"Wrap it with `@govern(POLICY, tool_name='find_stalls')`."*
- Accept. Open `src/merlions/policies/hawker.yaml` in a split pane for ~5 seconds — proves the policy lives in YAML, not in code.

**Step E — Generate the tests (60s)**
- Either open `tests/test_find_stalls.py` and scroll to the bottom to add a new test, OR create `tests/test_find_stalls_demo.py` for a clean recording surface.
- Inline **prompt #3**:
  > *"Generate pytest cases covering: empty location, malicious input (`api_key=...`), rate-limit (>10 calls), unknown location returns [], and a happy path."*
- Accept the suggestions.

**Step F — Prove it works (30s)**
- In the terminal pane:
  ```powershell
  .\talk\demos\demo1.ps1
  ```
- 5 green checks. End the recording on that frame.

### Cleanup after recording
Delete `hawker_demo.py` and any duplicate test file you created during the take — the canonical versions in the repo should stay clean. Commit nothing from the recording session.

---

## 🎬 DEMO 2 — Multi-agent composite question
**Slide 9 · ~90 sec · Record the terminal only**

### Before you hit record
1. Open a fresh PowerShell window. **Pre-activate** the venv off-camera so the prompt is clean, or let the script use the full path (it does).
2. Maximise the window. Set font ≥16pt.
3. `Clear-Host`

### Step-by-step recording

**Step A — Show the prompt the user is asking (5s)**
The script prints the composite question in a magenta panel. Let it sit for a beat.

**Step B — Run the script (5s)**
```powershell
.\talk\demos\demo2.ps1
```

**Step C — Let the output render (40s)**
You'll see three cyan panels — `hawker`, `haze`, `wisecracker` — each with its summary, citations underneath, and a latency. Pause on each panel so the audience reads the citation line. The trace_id and total latency print at the bottom.

**Step D — Trace table (30s)**
The script then calls `merlions traces --last 12` and prints a table of spans with `name`, `duration_ms`, `trace_id`, `span_id`, `parent_id`. Highlight one parent + three children so the audience sees the orchestration tree.

**Step E — End the take (10s)**
End on the trace table. That's the punch line — *one request, three agents, fully traced*.

---

## 🎬 DEMO 3 — Observability + guardrail rejection + eval loop
**Slide 11 · ~2 min · Record the terminal only**

### Before you hit record
```powershell
# Wipe previous artefacts so the audit table starts clean and short
Remove-Item -Recurse -Force .audit, .traces -ErrorAction SilentlyContinue
Clear-Host
```

### Step-by-step recording

```powershell
.\talk\demos\demo3.ps1
```

Four sections will print in order:

**Step 1 — A normal request (~15s)**
A green-trim panel: hawker recommends Satay by the Bay with a citation. *"Happy path. Allow trace."*

**Step 2 — A malicious request triggers `policy.deny` (~20s)**
The script calls `merlions call-tool find_stalls --arg "cuisine=api_key=AKIA-fake-please-deny"`. A **red-trim panel** prints `PolicyViolation: hawker denied find_stalls: blocked_patterns/...` and the script prints `(expected refusal — exit code 1)`. *"The decorator caught it. The audit log captured the matched rule, not the user's content."*

**Step 3 — Audit table (~30s)**
`merlions audit --last 8` prints a table with one **green `allow`** row and one **red `deny`** row, with the matched rule visible on the deny row. **Hold this frame** — it's the money shot for decision-makers.

**Step 4 — Eval suite (~15s)**
`merlions evals --suite hawker --since yesterday` prints:
```
Hawker eval suite · 5 cases · 5 pass · 0 regressions · 0.02s
```
*"Real rejections become tomorrow's eval cases. The agent gets measurably better, week over week."*

End the take.

---

## Recording mechanics (applies to all three)

| Setting | Value |
|---|---|
| Resolution | 1080p |
| Frame rate | 24 fps |
| Audio | **Mute the clip**, narrate live on stage |
| Terminal font | ≥ 16pt |
| Theme | Light (better for projectors) |
| Tool | OBS Studio / ScreenPal / Camtasia — any MP4 exporter |
| Trim | Aggressively — cut every second of dead air |
| First frame | 1-frame title slate (`Demo 1`, `Demo 2`, `Demo 3`) so you know which clip is loaded |

After each take, do a 10-second playback at the resolution the venue projector uses (ask AV in advance) to confirm the text is legible from the back row.

## Fallback safety net

Take **one screenshot per visible state** during your rehearsal:

- **Demo 1:** green pytest output (5 passes)
- **Demo 2:** composed reply panels + trace table
- **Demo 3:** red deny panel + audit table + eval summary

Save them under `talk\demos\fallback\demo1\`, `\demo2\`, `\demo3\`. If a clip stutters on stage, switch to the screenshots and narrate the same beats from `talk/demo-scripts.md`.

---

## TL;DR cheat sheet

```powershell
# One-time setup
uv venv
uv pip install -e ".[dev]"
pytest -q

# Smoke test
.\talk\demos\demo1.ps1
.\talk\demos\demo2.ps1
.\talk\demos\demo3.ps1

# Record (in this order):
# Demo 1 → editor + Copilot Chat, end with demo1.ps1 green
# Demo 2 → terminal only, demo2.ps1
# Demo 3 → terminal only, demo3.ps1 (after wiping .audit and .traces)
```
