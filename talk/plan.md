# Talk Plan — *Merlions, Agents & Copilot: Trustworthy Python on Azure*

**Length:** 30 minutes · **Slides:** 12 · **Audience:** Mixed devs + decision makers
**Demo style:** Pre-recorded clips, narrated live (safer for timing + Wi-Fi)

## Time budget (30:00)

| Block | Slides | Time | Cumulative |
|---|---|---|---|
| Hook + framing | 1–2 | 2:30 | 2:30 |
| Cast of agents | 3–4 | 3:00 | 5:30 |
| Copilot story + **Demo 1** | 5 | 4:30 | 10:00 |
| Trust pillars | 6 | 2:00 | 12:00 |
| Agent walkthroughs + **Demo 2** | 7–9 | 7:30 | 19:30 |
| Azure deployment | 10 | 3:00 | 22:30 |
| Observability + **Demo 3** | 11 | 4:00 | 26:30 |
| Call to action + Q&A buffer | 12 | 3:30 | 30:00 |

## Slide-by-slide talk track

### Slide 1 — Title (1:00)
- Open with a Singapore hook: *"Raise your hand if you've eaten at a hawker centre. Now keep it up if you've ever asked an AI to recommend dinner."*
- Frame the promise: **friendly, reliable, multi-agent Python on Azure** — with personality.
- One-line bio + why you care about trustworthy agents.

### Slide 2 — What we'll explore (1:30)
- Walk the 4 bullets fast — set expectations: *"You'll leave with a pattern, not just a demo."*
- Tell decision-makers what they get: trust patterns + Azure architecture.
- Tell devs what they get: Copilot workflow + code.

### Slide 3 — Meet our agents (1:30)
- Introduce the three personas like characters in a story.
- Land the why: **specialised agents beat one mega-agent** — smaller surface, clearer guardrails, easier eval.

### Slide 4 — Multiagent systems working together (1:30)
- Explain orchestration: a router/coordinator delegates to the right agent.
- Decision-maker line: *"This is how you scale capability without scaling risk — each agent has least-privilege tools."*

### Slide 5 — GitHub Copilot to the rescue (4:30) 🎬 **Demo 1**
- 60s talk: how Copilot accelerates agent dev (scaffolding tools, writing guardrails, generating tests).
- **Demo 1 (≈3 min, pre-recorded):** Copilot CLI / Chat scaffolding a new `agent_tool()` for the Hawker agent — show it generating the function, then **adding a guardrail** (input validation) and a **unit test** in the same flow.
- Close with: *"Copilot isn't writing the agent for you — it's writing the boring, safety-critical scaffolding so you can focus on behaviour."*

### Slide 6 — Trust is our architectural style (2:00)
- One sentence per pillar — Transparency, Safety, Reliability, Observability.
- Anchor: *"These aren't features we bolt on. They're the architectural style — like Peranakan tiles, the pattern runs through everything."*

### Slide 7 — Hawker Recommender Agent (2:30)
- Show the flow on slide: tool use (maps) → RAG (menu info) → trust (validate + cite).
- Call out: **grounded responses with citations** — the agent says *why* it picked Maxwell.
- Mention the safety check: refuses if location data is missing rather than hallucinating.

### Slide 8 — Haze Tracker Agent (2:30)
- Real Singapore context — PSI data from gov source.
- Pattern: **ingest → forecast → alert**. Highlight idempotent alerts (don't spam users at 3am).
- Decision-maker line: *"Same trust pattern, totally different domain. That's the point."*

### Slide 9 — Merlion Wisecracker Agent + 🎬 **Demo 2** (2:30)
- The fun one — but use it to teach **personality with guardrails**: tone is fun, content is safe and grounded.
- **Demo 2 (≈90s, pre-recorded):** Multi-agent run — user asks *"Dinner near Marina Bay, is the air ok, and make me laugh"* → router fans out to all 3 agents → composed answer with citations + a pun.
- Land: *"Personality is a product feature. Trust is what lets you ship it."*

### Slide 10 — From local to cloud: Azure deployment (3:00)
- Walk the 4 boxes:
  - **Container Apps** — serverless scale-to-zero, easy for agents.
  - **App Insights** — traces every tool call.
  - **Cosmos DB** — conversation state + RAG store.
  - **Key Vault** — no secrets in code, ever.
- Decision-maker line: *"Managed services so your team focuses on agent behaviour, not babysitting infra."*

### Slide 11 — Observe. Learn. Improve. + 🎬 **Demo 3** (4:00)
- The Collect → Understand → Improve loop.
- **Demo 3 (≈2 min, pre-recorded):** App Insights dashboard showing tool-call traces, a guardrail rejection, and a latency spike → quick view of the **eval feedback loop** updating the agent.
- Tagline from slide: *"Observable systems are trustworthy systems."* Repeat it. Let it land.

### Slide 12 — Call to action (2:00 + buffer for Q&A)
- Recap three takeaways:
  1. **Specialise** your agents.
  2. **Build trust in** — don't bolt it on.
  3. **Ship to Azure** with observability from day one.
- CTA: GitHub repo link, blog, or workshop signup.
- Singapore sign-off: *"Lah, let's build."* 🦁

## Demo suggestions (summary)

| # | Slide | Length | What to show | Why it works |
|---|---|---|---|---|
| 1 | 5 | ~3:00 | Copilot scaffolds `agent_tool` + guardrail + unit test | Proves Copilot speeds up the *safe* parts, not just the fun parts |
| 2 | 9 | ~1:30 | Multi-agent orchestration answering one composite question | Shows the whole system clicking together; pays off slides 3–4 |
| 3 | 11 | ~2:00 | App Insights traces + a guardrail rejection + eval loop | Makes "trust" tangible for decision makers |

**Optional 4th demo (cut if tight):** Azure Container Apps deploy from CLI (~45s) between slides 10 and 11 — only if you have margin.

## Recording tips for pre-recorded clips
- Record at **1080p, 24fps**, large terminal font (16pt+), light theme for stage projectors.
- Trim dead air; add a 1-frame title card so you know which clip is playing.
- Test audio routing — mute clip audio, narrate live (your voice is the through-line).
- Keep each clip ≤ stated length so you stay on the time budget.

## Risks / things to rehearse
- **Slide 9 demo** is the most complex — rehearse the narration over the clip twice.
- Have a **fallback static screenshot** for each demo in case video playback fails.
- Watch the clock at slides 7 and 11 — those are the most likely overrun points.
