# Speaker Notes — *Merlions, Agents & Copilot: Trustworthy Python on Azure*

> Read these as if speaking. Bold = land it. *Italic* = optional aside. `[beat]` = pause.
> Word counts target ~150 wpm so timings hold.

---

## Slide 1 — Title (1:00 · ~150 words)

"Good morning, Singapore. `[beat]` Raise your hand if you've eaten at a hawker centre this week. `[smile]` Keep it up if you've ever asked an AI to recommend dinner. `[beat]`

That little tension — between *trusting a local uncle* and *trusting a chatbot* — is what this talk is about.

I'm <NAME>, and I spend my days building AI agents. Today I want to show you how to build agents you can actually trust — in Python, on Azure, with GitHub Copilot riding shotgun.

We're going to meet three little agents inspired by Singapore. We're going to give them personality. And — more importantly — we're going to give them **guardrails, observability, and a path to production**. `[beat]`

By the end, devs will leave with a pattern they can copy on Monday. Decision makers will leave knowing what 'trustworthy' actually looks like in an architecture diagram. `[beat]` Let's go."

---

## Slide 2 — What we'll explore (1:30 · ~220 words)

"Here's the map for the next 30 minutes.

**One.** Three Singaporean-inspired Python agents — a hawker recommender, a haze tracker, and a Merlion that tells dad jokes. Don't worry, the puns are grounded in evidence. `[beat]`

**Two.** GitHub Copilot superpowers — not Copilot writing your app for you, but Copilot writing the *boring, safety-critical scaffolding* so you can focus on behaviour.

**Three.** Trust and transparency patterns — the architectural style that runs through all three agents like the tiles on a Peranakan shophouse.

**Four.** Azure deployment and observability — how this leaves your laptop and survives contact with real users.

If you're a developer, you'll get code patterns, a Copilot workflow, and three working demos to copy. If you're a decision maker, you'll get a vocabulary — transparency, safety, reliability, observability — and you'll see what each one costs and what each one buys you.

One promise: I'm not going to show you a magic mega-agent that does everything. I'm going to show you **small, specialised, well-governed agents that collaborate**. Because that's the pattern that actually ships. `[beat]` Let's meet the cast."

---

## Slide 3 — Meet our agents (1:30 · ~220 words)

"Three agents. Three jobs. Three very different risk profiles.

**Hawker Recommender** — finds tasty local delights. Risk: hallucinated restaurants, stale opening hours. Mitigation: tool use for real maps data, RAG over verified menu info, and every answer cites its source.

**Haze Tracker** — watches PSI and air quality. Risk: missing an alert, or worse, alert fatigue. Mitigation: idempotent alerts, fallback data sources, and a forecast confidence score.

**Merlion Wisecracker** — brings puns and perspective. Risk: tone going off the rails. Mitigation: a content guardrail, a personality prompt with explicit do's and don'ts, and a refusal path when the input gets weird. `[beat]`

Why three agents instead of one? `[beat]` Because **a smaller agent has a smaller blast radius**. Each one has its own tools, its own prompts, its own evals, and its own permissions. When something goes wrong — and at scale, something always goes wrong — you know exactly which agent to fix.

This is the same principle as microservices, but for cognition. Specialise, govern, compose. `[beat]` Speaking of composing — let's see how they work together."

---

## Slide 4 — Multiagent systems working together (1:30 · ~220 words)

"Here's the orchestration. A user asks a question. A **router** — sometimes called a coordinator or supervisor — decides which agents to call. The agents do their work. The router composes the final answer.

Think of it like a kopitiam. `[beat]` You order, the auntie at the till routes your order to the right stall — chicken rice here, laksa there, kopi over there. Each stall is an expert. Nobody tries to do everything. `[beat]`

For developers: the router is just another agent, with one job — routing. Its tools are *the other agents*. That keeps the system composable. You can add a fourth agent next week without rewriting the first three.

For decision makers: this is how you **scale capability without scaling risk**. Each agent has least-privilege tool access. The Hawker agent can't read government haze data. The Haze agent can't tell jokes. The Wisecracker can't book a table. They each do one thing, they each have their own audit trail, and they each have their own kill switch. `[beat]`

The Python ecosystem — frameworks like PydanticAI, CrewAI, LangGraph, AutoGen — all support this pattern. Pick the one your team likes. The *pattern* is what matters. `[beat]` Now, how do we build all this without losing our weekends?"

---

## Slide 5 — GitHub Copilot to the rescue (4:30 · ~180 words spoken + 3 min demo)

"Honest moment: building a multi-agent system used to be a weekend-eater. Tools, schemas, guardrails, tests, traces — it's a lot of plumbing. `[beat]`

GitHub Copilot changes the economics. Not because it writes the *agent* for you — your domain expertise still matters — but because it writes the **scaffolding** for you, fast and consistently.

Watch this. I'm going to ask Copilot to scaffold a new tool for the Hawker agent, add a guardrail, and write a unit test. `[beat]`

`[🎬 PLAY DEMO 1 — narrate over the clip; see demo-scripts.md]` `[3:00]`

`[After clip lands]` Three things to notice. **One** — the function signature is typed and validated. **Two** — Copilot added input validation *before* I asked, because the surrounding code had that pattern. **Three** — the unit test covers the unhappy path. `[beat]`

That's the workflow: Copilot accelerates the safe parts, so I can spend my brain on the interesting parts — agent behaviour and user experience. `[beat]` Which brings us to trust."

---

## Slide 6 — Trust is our architectural style (2:00 · ~290 words)

"Four pillars. I want you to leave today with these four words. `[beat]`

**Transparency.** The agent explains its decisions. Why this hawker stall? Because of these reviews, this distance, this menu match. Not 'because the model said so.'

**Safety.** Guardrails and validation. Input validation, output filtering, tool allowlists, content checks. **Fail closed** — if a check errors or is ambiguous, deny the action. Never assume.

**Reliability.** Retries, fallbacks, idempotency. If the maps API is down, fall back to cached data and tell the user. If the user asks twice, don't double-book. Boring. Critical.

**Observability.** Logs, metrics, traces. Every tool call. Every guardrail decision. Every refusal. If you can't see it, you can't trust it. `[beat]`

These aren't features we bolt on at the end. They're the **architectural style** — like the tiles on a Peranakan shophouse, the pattern runs through every wall. `[beat]`

For decision makers: if a vendor pitches you an agent and can't show you all four of these, walk away. For developers: design these in from line one. Retrofitting trust is ten times more expensive than building it in. `[beat]`

One more thing — these pillars are also how you have a sensible conversation with your security and compliance teams. Instead of *'it's AI, it's magic'*, you can say *'here's the allowlist, here are the traces, here's the eval suite'*. That conversation goes a lot better. `[beat]`

Right. Let's see all four pillars in real agents."

---

## Slide 7 — Hawker Recommender Agent (2:30 · ~370 words)

"Hawker Recommender. User says *'recommend dinner near me.'* Agent says *'Hainanese chicken rice at Maxwell today.'* Looks simple. Underneath, three things happened. `[beat]`

**One — tool use.** The agent called a maps tool to find nearby hawker centres. The tool is on an allowlist. It can read locations. It cannot write, cannot pay, cannot book. **Least privilege.**

**Two — RAG.** Retrieval-augmented generation over a verified menu dataset. The agent isn't *guessing* what Maxwell serves. It's *retrieving* what Maxwell serves and then phrasing it nicely. **Grounded.**

**Three — trust.** Every claim is validated against the retrieved source, and every answer cites which stall, which review, which date. If the agent can't find a citation, it says *'I'm not sure — here's what I do know'*. **Honest about uncertainty.** `[beat]`

For devs: this is the pattern — *tool → retrieve → ground → cite*. Implementing it in Python is maybe 100 lines on top of your agent framework. It is the single highest-leverage change you can make to an LLM app. `[beat]`

For decision makers: this is what the word 'grounded' actually means. It means the agent's output is *traceable to a source you control*. Which means when a user complains about a bad recommendation, you can debug it. You can fix the data. You can add a test. It's an engineering problem, not a mystery. `[beat]`

And notice what we *didn't* do — we didn't fine-tune a model on hawker data. We didn't need to. Tool use plus retrieval gets you 90% of the value at 10% of the cost. Keep that in your back pocket the next time someone pitches an expensive fine-tune. `[beat]`

One safety call-out — if the user shares no location and no preference, the Hawker agent **refuses** and asks for one. It doesn't pick a random stall. Refusal is a feature. `[beat]` Next agent."

---

## Slide 8 — Haze Tracker Agent (2:30 · ~370 words)

"Haze Tracker. PSI eighty-two, moderate. *'Take care, drink water, stay indoors.'* `[beat]`

Anyone who's lived through a Singapore haze season knows this isn't a toy. People need this information to decide whether to send kids to school, whether to run outside, whether to mask up. **The cost of a wrong answer is real.** `[beat]`

Same three pillars, different shape.

**Ingest.** The agent pulls from NEA's public data feed. Tool use, allowlisted, read-only.

**Forecast.** A small forecasting model — could be classical, could be an LLM-augmented one — projects the next six hours and attaches a **confidence score**. Low confidence? The agent says so. It doesn't fake certainty.

**Alert.** This is the interesting part. Alerts are **idempotent**. If the PSI crosses into 'unhealthy' at 7am, you get one alert. Not five. Not one every refresh. The agent remembers what it told you, and it doesn't spam you at 3am unless something truly changed. `[beat]`

For devs: idempotency is the most under-rated property in agent design. It's the difference between a useful assistant and a creepy stalker. Implement a dedupe key on every external side-effect. `[beat]`

For decision makers: the Hawker agent and the Haze agent are **the same trust pattern applied to different domains**. Same vocabulary — ingest, ground, validate, trace. Same observability. Same kill switch. *That's* the power of an architectural style. You're not buying three bespoke products. You're buying one pattern, applied three times. `[beat]`

This also means the third agent — coming up — uses the exact same pattern, even though it tells jokes. Personality is just another behaviour layer on top of the same trustworthy foundation. `[beat]`

Quick safety note — the Haze agent has a **fallback chain**. NEA feed first, cached data second, a clear *'data unavailable, please check nea.gov.sg'* message third. It never invents a PSI number. Failing visibly beats failing silently. Every time. `[beat]` On to the fun one."

---

## Slide 9 — Merlion Wisecracker Agent + Demo 2 (2:30 · ~150 words + 90s demo)

"The Merlion Wisecracker. *'Why do Python devs love the sea? Because they prefer high tide and high code quality.'* `[wait for groan]` Exactly the reaction I wanted. `[beat]`

But look at the bottom of the slide — personality, safe by design, grounded responses. The joke is fun. The system around it is serious. `[beat]`

Let me show you all three agents working together on one composite question. `[beat]`

`[🎬 PLAY DEMO 2 — narrate over the clip; see demo-scripts.md]` `[1:30]`

`[After clip lands]` What you just saw — one user question, router fans out to three agents, three grounded answers composed into one reply with a pun on the end. **Cited. Safe. On time.** `[beat]`

The takeaway: **personality is a product feature. Trust is what lets you ship it.** Without the guardrails, you'd never let this agent talk to a real customer. With them, you can. `[beat]` So how do we get this off our laptops?"

---

## Slide 10 — From local to cloud: Azure deployment (3:00 · ~450 words)

"Four Azure services. That's it. You don't need a Kubernetes cluster. You don't need a platform team. `[beat]`

**Azure Container Apps.** Your agents, containerised, serverless, scale-to-zero. Pay for what you use. Great fit for spiky agent workloads. Built-in revisions for safe rollouts and instant rollback.

**Azure Application Insights.** Every tool call traced. Every guardrail decision logged. Every latency spike charted. This is where 'observability' becomes a dashboard you can actually point at.

**Azure Cosmos DB.** Conversation state, RAG store, eval datasets. Multi-region, low latency, fits the agent access pattern. *You can start cheap and scale.*

**Azure Key Vault.** Secrets out of code. Forever. API keys, model endpoints, database connection strings — none of it lives in your repo, none of it lives in a `.env` you accidentally commit. Managed identity does the rest. `[beat]`

For devs: this stack deploys from a single `az containerapp up` command once you've set up the basics. You can have a Python agent in production this afternoon. `[beat]`

For decision makers: every service on this slide is **managed**. Microsoft handles patching, scaling, redundancy. Your team focuses on agent behaviour and user experience — which is the *only* place your competitive advantage lives. Don't pay your engineers to babysit Postgres. `[beat]`

One pattern worth naming — **separate the agent runtime from the data plane**. Container Apps for the agent. Cosmos for state. Key Vault for secrets. App Insights for telemetry. When you separate concerns like this, you can upgrade any one piece without breaking the others. That's how you survive eighteen months of model upgrades and framework churn. `[beat]`

Couple of practical tips. **One** — turn on Application Insights from day one, not day ninety. Retro-fitting traces is painful. **Two** — use managed identity between your Container App and Cosmos and Key Vault. No secrets to rotate. **Three** — put your prompts and policies in config, not code. You want to update a guardrail without redeploying. `[beat]`

And critically — every one of these services has a **regional presence in Southeast Asia**. Your data stays close. Latency stays low. Compliance teams stay happy. `[beat]` Speaking of staying happy — observability."

---

## Slide 11 — Observe. Learn. Improve. + Demo 3 (4:00 · ~200 words + 2 min demo)

"Three steps. **Collect. Understand. Improve.** `[beat]`

**Collect** — logs, metrics, traces. Every tool call, every guardrail decision, every refusal, every latency. Default on.

**Understand** — dashboards and alerts. What's slow? What's failing? Which guardrails are firing — and are they firing too much, or not enough?

**Improve** — feedback loops and evals. Take real traces, turn them into eval cases, run them every CI build. The agent gets measurably better, week over week. `[beat]`

Let me show you what this looks like in App Insights. `[beat]`

`[🎬 PLAY DEMO 3 — narrate over the clip; see demo-scripts.md]` `[2:00]`

`[After clip lands]` You just saw three things. **One** — a real tool-call trace, top to bottom, with timings. **Two** — a guardrail rejection logged with the matched rule and the evidence. **Three** — that rejection flowing into an eval dataset that runs against the next build. `[beat]`

That loop is the difference between an agent that *demos well* and an agent that *gets better in production*. `[beat]`

Say it with me: **observable systems are trustworthy systems.** `[beat]` Closing thought."

---

## Slide 12 — Call to action (2:00 + Q&A buffer · ~290 words)

"Three takeaways. Write these down. `[beat]`

**One. Specialise your agents.** Small, focused, governed. Not one mega-agent. Three little ones that collaborate.

**Two. Build trust *in*, not *on*.** Transparency, safety, reliability, observability — designed in from line one. Retrofitting trust is ten times more expensive.

**Three. Ship to Azure with observability from day one.** Container Apps, Cosmos, Key Vault, Application Insights. Boring stack. Reliable outcomes. `[beat]`

If you're a developer — clone the repo, run the demos, ship one tool, add one guardrail, write one eval. That's a week of work and it changes how you build forever.

If you're a decision maker — go back to your team and ask three questions. *Where are our agents' guardrails? Where are our traces? Where are our evals?* If you don't get clear answers, you've found your roadmap. `[beat]`

Singapore taught me something I want to leave you with. `[beat]` This city works because everyone respects the system — the queue at the hawker stall, the rules of the MRT, the **trust** that makes a million strangers cooperate every day. `[beat]`

Our agents need the same thing. Personality, yes. Speed, absolutely. But **trust** is what makes them useful at scale. `[beat]`

So — go build agents that are friendly, fast, *and* trustworthy. Singapore style. `[beat]`

The repo, the slides, and the demo clips are at the link on screen. I'll be at the back for the rest of the session — come say hi, tell me your favourite hawker stall, I'll fight you about it. `[smile]` `[beat]`

**Lah, let's build.** Thank you. `[beat — wait for applause, then take Q&A]`"

---

## Total spoken word count: ~3,000 words ≈ 20 min @ 150 wpm
## Plus 6.5 min of demo clips + ~3.5 min for pauses, laughs, Q&A buffer = **~30 min**
