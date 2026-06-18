# Chapter 6: Trust Is Our Architectural Style

**Code:** [`src/merlions/governance.py`](../../src/merlions/governance.py)

---

Think of trust as four pillars. Like the load-bearing walls of a Peranakan
shophouse, they are not decoration added at the end. Trust is the *style* that
runs through every wall.

| Pillar | What it means | In this repo |
|---|---|---|
| **Transparency** | The agent explains its decisions and cites sources | `require_citation` in [policies](../../src/merlions/policies) |
| **Safety** | Guardrails, validation, allowlists, content checks (**fail closed**) | [`governance.py`](../../src/merlions/governance.py) |
| **Reliability** | Retries, fallbacks, idempotency | Haze fallback chain, dedupe keys |
| **Observability** | Logs, metrics, traces for every decision | [`telemetry.py`](../../src/merlions/telemetry.py) |

## Each pillar, concretely

- **Transparency**: "Why this hawker stall? Because of these reviews, this
  distance, this menu match." Never "because the model said so."
- **Safety**: input validation, output filtering, tool allowlists, content
  checks. **Fail closed:** if a check errors or is ambiguous, deny the action.
- **Reliability**: if the maps API is down, fall back to cached data and *say
  so*. If the user asks twice, do not double-book. Boring. Critical.
- **Observability**: every tool call, every guardrail decision, every refusal.
  *If you can't see it, you can't trust it.*

## This is now an industry standard

The four pillars line up with the Build 2026 throughline:

- **Trace** with **OpenTelemetry's GenAI semantic conventions**.
- **Enforce** with the new **Agent Control Specification**, a universal runtime
  standard that turns agent safety from best-effort into *deterministic
  control* (tool allowlists, content filters, rate limits, human-in-the-loop).
- **Improve** with **continuous evaluation** on every agent action.

## Why it matters (for decision makers)

These four words are also how you have a sensible conversation with security and
compliance. Instead of "it's AI, it's magic," you can say: *"here's the
allowlist, here are the traces, here's the eval suite."*

> If a vendor pitches you an agent and can't show you all four pillars, walk
> away. If you are a developer, design them in from line one. Retrofitting
> trust is ten times more expensive.

## Key terms

- **Fail closed**: when uncertain, deny. The safe default.
- **Policy as configuration**: guardrails live in YAML
  ([`policies/`](../../src/merlions/policies)), not hardcoded, so they can change
  without a redeploy.
- **Audit trail**: a durable, queryable record of what the agent decided and
  why.

## Do this next

1. Read [`governance.py`](../../src/merlions/governance.py) and note how a
   malformed policy raises (fails closed) rather than allowing everything.
2. Open a policy file like
   [`policies/hawker.yaml`](../../src/merlions/policies/hawker.yaml) and see the
   allowlist, blocked patterns, call limit, and citation requirement.
3. For your project, write the four pillars into your design doc *before* you
   write the agent.

> 📺 **Build 2026 grounding:** **BRK250** (observe and control agents across any
> framework) and **LTG430** (Agent Control Specification).
