# 📖 Chapters: *Merlions, Agents & Copilot: Trustworthy Python on Azure*

> **A standalone guide to building trustworthy Python agents on Azure.**
> Read it cover to cover, or jump to the chapter you need. Each chapter pairs a
> concept with clear, copyable instructions so you can build the same patterns
> yourself, no presentation required.
>
> Everything here is grounded in current Microsoft Build 2026 guidance
> (see [`talk/context.md`](../context.md)) and in the working code in
> [`src/merlions/`](../../src/merlions).

## How to use these chapters

- **Developers:** follow the *Do this next* sections. They reference real files
  in this repo so you can read the implementation, not just the idea.
- **Decision makers:** read the *Why it matters* and *Key terms* sections. They
  give you the vocabulary to ask your teams the right questions.
- **Everyone:** the *Build 2026 grounding* boxes point you to the official
  Microsoft Build sessions that go deeper on each topic.

## Chapter index

| # | Chapter | Theme |
|---|---|---|
| 1 | [Why trust](01-title.md) | Framing |
| 2 | [What we'll explore](02-agenda.md) | Framing |
| 3 | [Meet our agents](03-agents.md) | Cast |
| 4 | [Multi-agent systems](04-multiagent.md) | Architecture |
| 5 | [GitHub Copilot to the rescue](05-github-copilot.md) | Tooling |
| 6 | [Trust is our architectural style](06-trust.md) | Pattern |
| 7 | [Walkthrough: Copilot scaffolds the safe parts](07-demo-copilot.md) | Hands-on |
| 8 | [Hawker Recommender agent](08-hawker-agent.md) | Agent |
| 9 | [Haze Tracker agent](09-haze-agent.md) | Agent |
| 10 | [Merlion Wisecracker agent](10-wisecracker-agent.md) | Agent |
| 11 | [From local to cloud: Azure](11-azure-deploy.md) | Deployment |
| 12 | [Observe. Evaluate. Improve.](12-observe.md) | Operations |
| 13 | [Where to go from here](13-call-to-action.md) | Close |

## The one-paragraph version

Build **small, specialised agents** instead of one mega-agent. Give each one
**least-privilege tools, grounded retrieval, and citations**. Make
**transparency, safety, reliability, and observability** the architectural
style, designed in, not bolted on. Use **GitHub Copilot** to generate the
boring, safety-critical scaffolding. Ship to **Azure** with **OpenTelemetry**
tracing and **continuous evaluation** from day one. The Build 2026 mantra:
*Observe. Evaluate. Improve. Roll out safely. Repeat.*
