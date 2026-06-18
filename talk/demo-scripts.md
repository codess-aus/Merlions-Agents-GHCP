# Demo Scripts — Commands + Narration Cues

> Each demo is a **pre-recorded clip** that you narrate live.
> Format below: what to record, what to say over it, on-screen markers.
> Record at 1080p, 24fps, terminal font ≥16pt, light theme for projectors.
> **Mute clip audio** — your voice is the through-line. Add a 1-frame slate at the start.
>
> **How to run the demos:** Copy-paste the commands shown below directly into your terminal.
> Do not run the `.ps1` files — they are kept for reference only.

---

## 🎬 DEMO 1 — Copilot scaffolds a tool, a guardrail, and a test
**Slide:** 5 · **Length:** ~3:00 · **Goal:** Show Copilot accelerates the *safe* parts

Typed signature + input validation"*

**Step 2 — Add the guardrail (45s)**

New Copilot Chat prompt in the same file:

```
Add a module-level policy loader: _POLICY = load_policy("hawker").
Then decorate find_stalls with @govern(_POLICY, tool_name="find_stalls").
```

Accept. Open `src/merlions/policies/hawker.yaml` in a split pane. Show:

After this edit, the module should look like:

```python
"""Tool: find_stalls — wraps the Maps API with input validation and governance."""

from __future__ import annotations

from merlions.governance import govern, load_policy
from merlions.models import InvalidInput, Stall
from merlions.tools.maps import maps_search

_POLICY = load_policy("hawker")


@govern(_POLICY, tool_name="find_stalls")
def find_stalls(location: str, cuisine: str | None = None) -> list[Stall]:
    """Search for hawker stalls near a location."""
    if not location or not location.strip():
        raise InvalidInput("location is required")
    return maps_search(location, cuisine)
```

```yaml
name: hawker
allowed_tools:
  - maps_search
  - menu_index_search
  - find_stalls
blocked_patterns:
  - "(?i)(api[_-]?key|password|secret|bearer\\s+[a-z0-9]+)\\s*[:=]?"
  - "(?i)ignore\\s+previous\\s+instructions"
max_calls_per_request: 10
require_citation: true
```

Point out: the allowlist, the cap, the blocked patterns. No code change needed to update any of these.
**On-screen callout:** *"Policy as configuration — not in code"*

**Step 3 — Generate the unhappy-path tests (60s)**

Open `tests/test_find_stalls.py`. Copilot Chat prompt:

```
Generate pytest cases for find_stalls (imported from merlions.tools.find_stalls) covering:
1. Happy path — marina bay returns a non-empty list of Stall, each with a source citation.
2. Empty location — raises InvalidInput.
3. Credential string in the location arg — governance raises PolicyViolation.
4. Rate limit — after 10 calls the 11th raises PolicyViolation (cap is max_calls_per_request: 10 in hawker.yaml).
5. Unknown but non-empty location — returns an empty list without raising.
Use a reset_call_counter() autouse fixture between tests.
```

Accept. Show all five test cases in the editor. Then copy-paste this command into the terminal:

```bash
pytest tests/test_find_stalls.py -vv -o addopts=
```

Expected output — all green:

```
tests/test_find_stalls.py::test_happy_path_marina_bay_returns_stalls PASSED
tests/test_find_stalls.py::test_empty_location_raises_invalid_input PASSED
tests/test_find_stalls.py::test_credential_in_location_raises_policy_violation PASSED
tests/test_find_stalls.py::test_rate_limit_raises_policy_violation_on_11th_call PASSED
tests/test_find_stalls.py::test_unknown_location_returns_empty_list PASSED

5 passed in 0.xx s
```

**On-screen callout:** *"5 tests · unhappy paths first · all green"*

**Closing shot (15s)** — Zoom out to the tree view. Three files highlighted: `find_stalls.py`, `hawker.yaml`, `test_find_stalls.py`. End on a 1-frame title card: *"~3 min · 1 tool · 1 guardrail · 5 tests"*.

---

### Narration script (read live over the clip)

> *(0:00–0:10)* "Here's the tool file. Imports only — no logic yet. Let's add it the right way."
>
> *(0:10–0:55)* "I'm asking Copilot for a typed function with input validation. Notice — I didn't say 'validate the input'. Copilot sees the `InvalidInput` import and the pattern from the surrounding codebase and applies it. **Conventions are contagious — in a good way.**"
>
> *(0:55–1:40)* "Now the guardrail. One decorator, one policy name. The policy itself is YAML — so my security team can add a blocked pattern, change the call cap, update the allowlist — **without a code change, without a deployment**. That's the whole point."
>
> *(1:40–2:40)* "The tests. I asked for the unhappy paths first — empty input, credential injection, rate limit exceeded — because those are the bugs that ship to production. Copilot generates the fixture, the assertions, and the fail-closed check that a credential string in an argument gets *denied by the policy*, not just validated by the function. Five tests. Pytest. Green."
>
> *(2:40–3:00)* "Three minutes. One tool. One guardrail. Five tests. **Copilot didn't write my agent. It wrote the scaffolding so I could focus on agent behaviour.** That's the workflow."

### Fallback if the clip won't play
Show in this order: (1) `find_stalls.py` with imports only, (2) completed function with `@govern` decorator, (3) `hawker.yaml` with allowlist and blocked patterns, (4) pytest terminal output — all green. Narrate the same beats.

---

## 🎬 DEMO 2 — Multi-agent orchestration on one composite question
**Slide:** 9 · **Length:** ~1:30 · **Goal:** Show all three agents collaborating

### What to record

**Setup shot (5s)** — Terminal open in the project root. The `merlions` CLI is installed.

**Step 1 — The composite ask (10s)**

Type slowly so the audience reads it, then hit Enter:

```bash
merlions ask "Dinner near Marina Bay, is the air OK to walk there, and make me laugh."
```

**Step 2 — Composed answer with citations (30s)**

The CLI renders three Rich panels — one per agent — with citations inline. The actual output:

```
╭─────────────────────────── hawker  ·  2ms ───────────────────────────╮
│ 🍜 Try Satay by the Bay at Gardens by the Bay — chilli stingray is a │
│ local favourite tonight.                                              │
╰───────────────────────────────────────────────────────────────────────╯
  · menu_index/satay-bay/2026-06-13

╭──────────────────────────── haze  ·  3ms ────────────────────────────╮
│ 🌫️ PSI is 58 (Moderate) and trending rising. A short walk is fine —  │
│ hydrate after. Forecast confidence 84%.                               │
╰───────────────────────────────────────────────────────────────────────╯
  · nea.gov.sg/psi/...
  · nea.gov.sg/psi/...#forecast+2h

╭─────────────────────────── wisecracker  ·  2ms ──────────────────────╮
│ 😎 I told my agent a joke about recursion. It told it back to me…    │
│ and back to me… and back…                                            │
╰───────────────────────────────────────────────────────────────────────╯
  (no citation — opinion only)

✓ trace_id=dd3212ca41b14298  total=5ms
```

Pause the cursor on each citation for half a second. Point out the wisecracker has no citation — that's intentional.
**On-screen callout:** *"3 agents · parallel dispatch · each least-privilege"*

**Step 3 — Trace tree (20s)**

```bash
merlions traces --last 10
```

Show the table. Point out: `policy.allow` rows for each agent tool call, the `tool.maps_search` and `tool.menu_index_search` child spans under `agent.hawker`, and the `trace_id` tying everything together.
**On-screen callout:** *"Every tool call · every policy decision · one trace ID"*

**Closing slate (5s)** — *"Cited. Safe. On time."*

---

### Narration script

> *(0:00–0:15)* "One composite question. Three concerns — food, safety, humour. One command."
>
> *(0:15–0:45)* "The router classifies the intent and **dispatches all three agents in parallel** using a thread pool. Each agent only has the tools on its own allowlist. The Hawker agent cannot read PSI data. The Haze agent cannot tell jokes. Least privilege, enforced by the policy decorator — not by trust."
>
> *(0:45–1:10)* "Composed answer. **Every factual claim has a citation.** The pun has none — and that's intentional. The humour policy is opinion, not fact. The system knows the difference."
>
> *(1:10–1:30)* "And here's the trace. Every tool call, every governance decision — `allow` or `deny` — with the same trace ID tying them together. **Personality is a product feature. Trust is what lets you ship it.**"

### Fallback
Four screenshots: the `merlions ask` command typed, the three Rich panels with citations, the wisecracker panel showing `(no citation — opinion only)`, the `merlions traces` table. Narrate the same beats.

---

## 🎬 DEMO 3 — Traces, a guardrail rejection, and the eval loop
**Slide:** 11 · **Length:** ~2:00 · **Goal:** Make trust *tangible* for decision makers

### What to record

**Setup shot (5s)** — Terminal open in the project root.

**Step 1 — Live trace of a normal request (30s)**

First, generate a fresh trace:

```bash
merlions ask "Dinner near Marina Bay"
```

Then show the trace records:

```bash
merlions traces --last 5
```

Walk through the output table. Point out: the `agent.hawker` span, child spans `tool.maps_search` and `tool.menu_index_search`, the `policy.allow` event with `"tool":"find_stalls"`. These are the same JSON fields Azure Monitor exports to App Insights — swap the sink and this same data appears in the portal.
**On-screen callout:** *"Every tool call · every decision · every policy version"*

**Step 2 — A guardrail rejection (40s)**

Trigger a deliberate policy denial and show the audit record:

```bash
python3 -c "
from merlions.tools.find_stalls import find_stalls
from merlions.governance import PolicyViolation
try:
    find_stalls('api_key=AKIA_DEMO')
except PolicyViolation as e:
    print('DENIED:', e)
"
```

Then inspect the audit log:

```bash
python3 -c "
import json, pathlib
for line in pathlib.Path('.audit/audit.jsonl').read_text().splitlines():
    r = json.loads(line)
    if r['decision'] == 'deny':
        print(json.dumps(r, indent=2))
" | tail -12
```

Show the output — point out what IS logged:

```json
{
  "timestamp": 1781737133.67,
  "policy": "hawker",
  "tool": "find_stalls",
  "decision": "deny",
  "matched_rule": "blocked_patterns/(?i)(api[_-]?key|password|...)"
}
```

Point out what is NOT there: no raw argument value, no user content.
**On-screen callout:** *"Logs decisions and rules — never raw prompts"*

**Step 3 — The eval loop (40s)**

Open `src/merlions/evals/cases.jsonl` in VS Code. Show `hawker-deny-9357-from-audit` — a case auto-generated from a real audit denial. Then run the suite:

```bash
python -m merlions.evals --suite hawker
```

Expected output:

```
              Hawker eval suite
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ id                          ┃ result ┃ detail                   ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ hawker-001                  │ pass   │ ok                       │
│ hawker-002                  │ pass   │ ok                       │
│ hawker-003                  │ pass   │ raises InvalidInput ✓    │
│ hawker-004                  │ pass   │ ok                       │
│ hawker-005-regression       │ pass   │ ok                       │
│ hawker-deny-9357-from-audit │ pass   │ raises PolicyViolation ✓ │
└─────────────────────────────┴────────┴──────────────────────────┘

Hawker eval suite · 6 cases · 6 pass · 0 regressions
```

**On-screen callout:** *"Real traces → eval cases → next build"*

**Closing slate (5s)** — *"Observable systems are trustworthy systems."*

---

### Narration script

> *(0:00–0:30)* "One request to the Hawker agent. Every tool call, every governance decision is structured data — same JSON shape that Azure Monitor writes to App Insights. In production you'd swap the file sink for the exporter and see this same tree in the portal. No grep, no log diving."
>
> *(0:30–1:10)* "Here's something more interesting — a guardrail rejection. I deliberately sent a credential-looking string as an argument. The policy caught it before the tool ran. And look at what got written to the audit log: the matched rule, the policy name, the decision. What is **not** there is the raw argument value. **We log decisions, not content.** That's how you keep your audit trail useful and your privacy review happy."
>
> *(1:10–1:50)* "And the loop closes. That denial became a test case — `hawker-deny-9357-from-audit`. The eval suite runs every CI build. Six cases today, all green. When the latency spikes or a new pattern sneaks through, this is what catches it. **The agent gets measurably better, build over build.** That's the whole game."
>
> *(1:50–2:00)* "Say it with me — *observable systems are trustworthy systems*."

### Fallback
Four screenshots: `merlions traces` table, the deliberate denial terminal output, the audit JSON block showing `"decision": "deny"` with no raw prompt, the eval table — all green. Narrate the same beats.

---

## Cross-cutting recording checklist

- [ ] Terminal font 16pt+, light theme, no other tabs visible
- [ ] Hide notifications, Slack, calendar pop-ups
- [ ] Reset `find_stalls.py` and `test_find_stalls.py` to stub state before recording Demo 1
- [ ] Run `merlions ask "Dinner near Marina Bay"` once before recording Demo 3 so `.audit/audit.jsonl` has at least one denial entry (from the test suite run)
- [ ] Each clip ≤ stated length — trim aggressively
- [ ] 1-frame slate at start = clip name, so you know which one is playing
- [ ] Export with **muted audio track** — narrate live
- [ ] Save fallback screenshots in `demos/fallback/<demo-N>/`
- [ ] Test playback on the *venue's* projector resolution, not just your laptop

## Rehearsal protocol

1. Practise each demo narration **with the clip muted** twice. Get the timing in your body.
2. Practise transitioning *out* of each clip — first sentence after the clip is the hardest.
3. Time the full deck end-to-end **twice**. Adjust word counts if you drift past 30 min.
4. Have a hard cut planned for each demo if A/V fails — the fallback screenshots make this safe.
