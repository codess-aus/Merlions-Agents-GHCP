# Demo Scripts — Commands + Narration Cues

> Each demo is a **pre-recorded clip** that you narrate live.
> Format below: what to record, what to say over it, on-screen markers.
> Record at 1080p, 24fps, terminal font ≥16pt, light theme for projectors.
> **Mute clip audio** — your voice is the through-line. Add a 1-frame slate at the start.

---

## 🎬 DEMO 1 — Copilot scaffolds a tool, a guardrail, and a test
**Slide:** 5 · **Length:** ~3:00 · **Goal:** Show Copilot accelerates the *safe* parts

### What to record (in this order)

**Setup shot (5s)** — VS Code or Copilot CLI open in the `agents/hawker/` folder. Tree view visible. Briefly highlight `agent.py` and `tools/` so the audience sees the structure.

**Step 1 — Scaffold a new tool (45s)**
- Open `tools/find_stalls.py` (empty).
- Copilot Chat / inline prompt:
  ```
  Add a function find_stalls(location: str, cuisine: str | None = None) -> list[Stall]
  that calls the Maps API tool. Use the Stall pydantic model from models.py.
  Validate location is non-empty. Type the return. Raise InvalidInput on bad input.
  ```
- Accept the suggestion. Show the typed signature, the validation, the pydantic return type.
- **On-screen callout (text overlay):** *"Typed signature + input validation"*

**Step 2 — Add a guardrail (45s)**
- Same file, new prompt:
  ```
  Wrap find_stalls with the @govern(policy=hawker_policy) decorator.
  Make sure the policy is loaded from policies/hawker.yaml, not hardcoded.
  ```
- Accept. Show `policies/hawker.yaml` opening in a split — `allowed_tools: [maps_search]`, `max_calls_per_request: 10`, `blocked_patterns: ["(?i)(api_key|password)"]`.
- **On-screen callout:** *"Policy as configuration — not in code"*

**Step 3 — Generate the unhappy-path test (60s)**
- Open `tests/test_find_stalls.py`. Prompt:
  ```
  Generate pytest cases for find_stalls covering:
  empty location, malicious input (API key in arg), Maps tool failure with retry,
  and a happy path with a mocked response.
  ```
- Accept. Show four test cases, including the **fail-closed assertion** that an ambiguous policy match denies the call.
- Run `pytest tests/test_find_stalls.py -v` in the terminal — green.
- **On-screen callout:** *"4 tests · unhappy paths first · all green"*

**Closing shot (15s)** — Zoom out to the tree view. Three new/edited files highlighted. End on a 1-frame title card: *"~3 min · 1 tool · 1 guardrail · 4 tests"*.

### Narration script (read live over the clip)

> *(0:00–0:10)* "Here's the Hawker agent's tool folder. Empty. Let's add a new tool the right way."
>
> *(0:10–0:55)* "I'm asking Copilot for a typed function with input validation. Notice — I'm not asking for validation explicitly the second time. Copilot sees the pattern in the surrounding code and applies it. **Conventions are contagious — in a good way.**"
>
> *(0:55–1:40)* "Now the guardrail. Single decorator. The policy itself lives in YAML — so my security team can update the allowlist or the blocked patterns *without a code change or a deployment*. That's a big deal."
>
> *(1:40–2:40)* "And the tests. I asked for the unhappy paths first — empty input, malicious input, tool failure — because that's what catches the bugs that ship to production. Copilot generates the mocks, generates the assertions, including the fail-closed check that an ambiguous policy denies the call. Pytest, green."
>
> *(2:40–3:00)* "Three minutes. One new tool. One guardrail. Four tests. **Copilot didn't write my agent. It wrote the scaffolding so I could focus on agent behaviour.** That's the workflow."

### Fallback if the clip won't play
Static screenshots in this order: (1) empty tool file, (2) generated typed function, (3) hawker.yaml policy file, (4) pytest green output. Narrate the same beats.

---

## 🎬 DEMO 2 — Multi-agent orchestration on one composite question
**Slide:** 9 · **Length:** ~1:30 · **Goal:** Show all three agents collaborating

### What to record

**Setup shot (5s)** — Terminal running the `merlions` CLI. Logo or banner visible.

**Step 1 — The composite ask (10s)**
- Type slowly so the audience reads it:
  ```
  > Dinner near Marina Bay, is the air OK to walk there, and make me laugh.
  ```
- Hit enter.

**Step 2 — Router fans out (20s)**
- Live trace prints (or simulated for the clip):
  ```
  [router] intent: food + air-quality + humour
  [router] dispatch → hawker, haze, wisecracker  (parallel)
  [hawker]     tool: maps_search("Marina Bay", "dinner")  ✓ 240ms
  [hawker]     rag:  menu_index.search(...)               ✓ 110ms
  [haze]       tool: nea_psi.current("south")             ✓ 90ms
  [haze]       forecast: 2h-ahead, confidence=0.82        ✓
  [wisecrack]  policy: humour, safe-tone                  ✓
  ```
- **On-screen callout:** *"3 agents · parallel · each least-privilege"*

**Step 3 — Composed answer (30s)**
- The final reply renders, with citations inline:
  ```
  🍜 Try Satay by the Bay — chilli stingray is a local favourite tonight
     [source: menu_index/satay-bay/2026-06-13].
  🌫️ PSI is 58 (Moderate) and trending flat — a 10-min walk is fine,
     hydrate after [source: nea.gov.sg/psi/2026-06-14T11:00].
  😎 And remember: a good Python dev is like the Merlion —
     half lion, half fish, *fully* type-hinted.
  ```
- Cursor pause on each citation for half a second.

**Step 4 — Trace pop-out (20s)**
- Toggle to a side panel showing the App Insights trace tree for this request — one parent span, three child spans, total latency ~600ms.
- **On-screen callout:** *"One request · three agents · fully traced"*

**Closing slate (5s)** — *"Cited. Safe. On time."*

### Narration script

> *(0:00–0:15)* "One composite question. Three concerns — food, safety, humour. Watch what happens."
>
> *(0:15–0:40)* "The router classifies the intent and **dispatches to all three agents in parallel**. Each agent only uses the tools on its own allowlist. The Hawker agent can't read PSI data. The Haze agent can't tell jokes. Least privilege, by design."
>
> *(0:40–1:10)* "Composed answer. **Every factual claim has a citation.** The pun is the only thing without one — and that's intentional, because the humour policy is opinion, not fact."
>
> *(1:10–1:30)* "And here's the trace. One parent span, three children, six hundred milliseconds end-to-end. **Personality is a product feature. Trust is what lets you ship it.**"

### Fallback
Four screenshots: composite prompt, router log, final cited answer, App Insights trace tree.

---

## 🎬 DEMO 3 — App Insights traces, guardrail rejection, and the eval loop
**Slide:** 11 · **Length:** ~2:00 · **Goal:** Make trust *tangible* for decision makers

### What to record

**Setup shot (5s)** — Azure portal, App Insights resource open on the agent's workspace.

**Step 1 — Live trace of a normal request (30s)**
- Open the **End-to-end transaction** view of the last hawker request.
- Expand the tree — show the tool call, the RAG call, the LLM call, total latency 380ms.
- Highlight the custom dimensions: `agent_id=hawker`, `policy=hawker-v3`, `decision=allow`, `tools_used=[maps_search, menu_index]`.
- **On-screen callout:** *"Every tool call · every decision · every policy version"*

**Step 2 — A guardrail rejection (40s)**
- Switch to a saved query in **Logs**:
  ```kusto
  traces
  | where customDimensions.event == "policy.deny"
  | where timestamp > ago(24h)
  | project timestamp, customDimensions.agent_id, customDimensions.matched_rule,
            customDimensions.evidence, customDimensions.user_redacted_id
  | take 10
  ```
- Run it. Show a recent row — `matched_rule: blocked_patterns/api_key_in_arg`, evidence is the *redacted* pattern match (not the user's content).
- **On-screen callout:** *"Audit logs decisions and rules — never raw prompts"*

**Step 3 — The eval loop (40s)**
- Switch to VS Code, `evals/cases.jsonl`. Show a new case appended overnight, autogenerated from yesterday's rejection traces.
- Run:
  ```
  uv run python -m merlions.evals run --suite hawker --since yesterday
  ```
- Output:
  ```
  Hawker eval suite · 142 cases · 138 pass · 4 regressions
  Regression: maps_search latency p95 1.4s (was 0.9s) — see trace/abc123
  ```
- **On-screen callout:** *"Real traces → eval cases → next build"*

**Closing slate (5s)** — *"Observable systems are trustworthy systems."*

### Narration script

> *(0:00–0:30)* "This is App Insights showing one real request to the Hawker agent. Three hundred and eighty milliseconds end-to-end. **Every tool call, every decision, every policy version** is right here as structured data. No grep. No log diving."
>
> *(0:30–1:10)* "Here's something more interesting. A guardrail rejection. The agent refused a request — and notice what got logged. **The matched rule. The evidence. The redacted user ID.** What did *not* get logged? The user's raw prompt. **We log decisions, not content.** That's how you keep your audit trail useful and your privacy review happy."
>
> *(1:10–1:50)* "And the loop closes. Last night's real rejection became this morning's eval case. The eval suite runs every CI build — caught a latency regression on the maps tool overnight. **The agent gets measurably better, week over week.** That's the whole game."
>
> *(1:50–2:00)* "Say it with me — *observable systems are trustworthy systems*."

### Fallback
Four screenshots: end-to-end transaction tree, Kusto query result, `cases.jsonl` diff, eval run output.

---

## Cross-cutting recording checklist

- [ ] Terminal font 16pt+, light theme, no other tabs visible
- [ ] Hide notifications, Slack, calendar pop-ups
- [ ] Pre-warm any API call so latency on the clip looks realistic, not cold-start
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
