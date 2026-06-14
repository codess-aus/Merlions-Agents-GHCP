Here's the observability architecture a Python developer should have, grounded in Build 2026 announcements and current best practices:

----------------------------------------------------------------------------------

🔭 Observability Architecture for Python Apps (Post-Build 2026)

1. Traces — OpenTelemetry is the standard

The Build 2026 message is clear: OpenTelemetry is the canonical tracing standard, now extended with GenAI semantic conventions for agent/LLM workloads.

 # pip install azure-monitor-opentelemetry opentelemetry-sdk
 from azure.monitor.opentelemetry import configure_azure_monitor
 
 configure_azure_monitor(
     connection_string="InstrumentationKey=...",
     enable_live_metrics=True,
 )

What to trace:

 - Model calls — input/output tokens, latency, model ID, cost
 - Tool calls — function name, arguments, success/failure, duration
 - Agent decisions — routing choices, handoffs between agents
 - End-to-end request spans — correlate user request → agent → tools → response

 📺 DEM341 — Any agent, any cloud: Standardized tracing with Foundry+OpenTelemetry — walks through the exact setup for framework-agnostic GenAI tracing.

----------------------------------------------------------------------------------

2. Metrics — Token cost, latency, quality scores

Key metrics to collect via OpenTelemetry + Azure Monitor:

┌────────────────────────────────────────────────────┬─────────────────┐
│ Metric                                             │ Why             │
├────────────────────────────────────────────────────┼─────────────────┤
│ Token consumption (input/output)                   │ Cost control    │
├────────────────────────────────────────────────────┼─────────────────┤
│ Latency (p50, p95, p99)                            │ User experience │
├────────────────────────────────────────────────────┼─────────────────┤
│ Error rate by model/tool                           │ Reliability     │
├────────────────────────────────────────────────────┼─────────────────┤
│ Quality scores (relevance, coherence, fluency)     │ Output quality  │
├────────────────────────────────────────────────────┼─────────────────┤
│ Cost per request                                   │ Business ROI    │
└────────────────────────────────────────────────────┴─────────────────┘

The Build 2026 theme from BRK252 (From observability to ROI for AI agents): connect agent behavior to business outcomes — track not just "is it working?" but "is it delivering value?"

----------------------------------------------------------------------------------

3. Dashboards — Foundry Observability + Azure Workbooks

Microsoft Foundry's built-in Observability dashboard (announced at Build) provides:

 - Token consumption trends
 - Latency distribution
 - Exception tracking
 - Quality/safety metrics from continuous evaluation
 - Trace-linked drill-down for debugging

For custom views, the dashboard is backed by Azure Monitor Workbooks with KQL queries — fully customizable and shareable. You can also set up Azure Alerts on any KQL query for proactive monitoring.

----------------------------------------------------------------------------------

4. Feedback Loops — Continuous Evaluation (the big Build 2026 push)

This is where Build 2026 pushes hardest. The continuous improvement loop from the Enterprise Agent Platform announcement:

 "Every agent action generates signal: trajectories, outcomes, feedback. The system captures it, refines it, and feeds it back. Observe. Evaluate. Improve. Roll out safely. Repeat."

Implementation in Python:

 from azure.ai.projects import AIProjectClient
 from azure.ai.projects.models import (
     AgentEvaluationRequest, EvaluatorIds,
     AgentEvaluationSamplingConfiguration,
 )
 
 # Set up continuous evaluation on agent runs
 evaluators = {
     "Relevance": {"Id": EvaluatorIds.Relevance.value},
     "Fluency":   {"Id": EvaluatorIds.Fluency.value},
     "Coherence": {"Id": EvaluatorIds.Coherence.value},
 }
 
 sampling = AgentEvaluationSamplingConfiguration(
     name=agent.id,
     samplingPercent=100,   # 0-100
     maxRequestRate=250,    # max 1000/hr
 )
 
 project_client.evaluation.create_agent_evaluation(
     AgentEvaluationRequest(
         thread=thread.id, run=run.id,
         evaluators=evaluators,
         samplingConfiguration=sampling,
         appInsightsConnectionString=conn_str,
     )
 )

The feedback loop architecture:

 User Request → Agent → Traces (OTel) → App Insights
                                             ↓
                                    Continuous Eval
                                    (quality + safety)
                                             ↓
                                    Dashboard + Alerts
                                             ↓
                               Prompt/routing refinement
                               or Frontier Tuning (RL)
                                             ↓
                                    Improved Agent ←─┘

----------------------------------------------------------------------------------

5. Key Python Packages

 azure-monitor-opentelemetry    # OTel distro for Azure
 opentelemetry-sdk              # Core OTel SDK
 azure-ai-projects              # Foundry agents + eval
 azure-monitor-query            # KQL queries for eval results
 azure-identity                 # Auth

----------------------------------------------------------------------------------

📺 Recommended Build 2026 Sessions

┌────────────────────┬───────────────────────────────┬────────────────────────────┐
│ Code               │ Title                         │ Why                        │
├────────────────────┼───────────────────────────────┼────────────────────────────┤
│ BRK252             │ From observability to ROI for │ Cross-framework tracing,   │
│                    │ AI agents                     │ evals, ROI measurement     │
├────────────────────┼───────────────────────────────┼────────────────────────────┤
│ DEM341             │ Standardized tracing with     │ Hands-on OTel setup for    │
│                    │ Foundry+OpenTelemetry         │ GenAI                      │
├────────────────────┼───────────────────────────────┼────────────────────────────┤
│ LAB540/LAB540D     │ Observe, optimize and protect │ Hands-on lab: eval suites  │
│                    │ hosted agents                 │ + continuous eval          │
├────────────────────┼───────────────────────────────┼────────────────────────────┤
│ TT640              │ Any agent, any cloud:         │ Practical checklist for    │
│                    │ Observability patterns        │ your stack                 │
├────────────────────┼───────────────────────────────┼────────────────────────────┤
│ ODSP909            │ AI agents from prototype to   │ Multi-agent tracing +      │
│                    │ production with OTel          │ CI/CD quality gates        │
├────────────────────┼───────────────────────────────┼────────────────────────────┤
│ ODSP933            │ Agentic infrastructure needs  │ Forward-looking:           │
│                    │ agentic observability         │ agent-driven telemetry     │
└────────────────────┴───────────────────────────────┴────────────────────────────┘

----------------------------------------------------------------------------------

TL;DR: Instrument with azure-monitor-opentelemetry, trace model+tool calls via OpenTelemetry GenAI conventions, wire up continuous evaluation for quality/safety scoring, visualize in Foundry's dashboard, and close the loop by feeding eval results back into prompt/routing improvements. The Build 2026 mantra: "If you can't measure it, you can't improve it."

1. 🧪 Agentic Testing — Validate AI-Generated Code

Build 2026's big message: "vibe coding lacks rigor" — you need autonomous test agents to validate autonomous systems.

What to do in your Python project:

 # Use Copilot for TDD-style development:
 # 1. Write tests FIRST (Copilot helps generate edge cases)
 # 2. Let Copilot implement against those tests
 # 3. Run in CI before merge
 
 # GitHub Copilot testing patterns (LTG405):
 # - Generate test suites from existing code
 # - Catch edge cases via agent-generated scenarios
 # - Validate AI-generated code in CI gates before merge
 # - Unit tests → integration tests → load tests

 📺 LTG405 — Better tests, faster. GitHub Copilot does the heavy lifting
 📺 ODSP912 — Build agentic testing systems to validate AI-generated code

----------------------------------------------------------------------------------

2. 📐 Teach Copilot Your Standards — Custom Instructions & Rules

From LTG402 (Why GitHub Copilot misses context): Out of the box, Copilot doesn't know your conventions. Fix it with:

┌───────────────────────────────────┬─────────────────────────────────┬───────────┐
│ Mechanism                         │ What it does                    │ Where     │
├───────────────────────────────────┼─────────────────────────────────┼───────────┤
│ .github/copilot-instructions.md   │ Repo-level instructions all     │ Repo root │
│                                   │ Copilot interactions follow     │           │
├───────────────────────────────────┼─────────────────────────────────┼───────────┤
│ Rules files (.github/copilot/*.md │ Topic-specific rules (security, │ Repo      │
│ )                                 │ testing, architecture)          │           │
├───────────────────────────────────┼─────────────────────────────────┼───────────┤
│ Prompt files (                    │ Reusable prompts for common     │ Repo      │
│ .github/copilot/prompts/*.md)     │ workflows                       │           │
├───────────────────────────────────┼─────────────────────────────────┼───────────┤
│ Custom agents & skills            │ Org-specific workflows Copilot  │ Org-level │
│                                   │ can execute                     │           │
└───────────────────────────────────┴─────────────────────────────────┴───────────┘

For trustworthy Python apps, put these in your instructions:

 - "Always use type hints"
 - "Validate inputs with Pydantic models"
 - "Never log PII or secrets"
 - "Use structured logging with correlation IDs"
 - "All AI outputs must include confidence scores"

----------------------------------------------------------------------------------

3. 🔒 Agent Control Specification — Runtime Guardrails

A new open standard announced at Build 2026 (LTG430):

 "Introduces a universal runtime standard that adds enforceable guardrails across frameworks, models, and clouds — turning agent safety from best effort into deterministic control."

Key principles for your Python architecture:

 # Policy-as-configuration (not hardcoded!)
 # agent-policy.yaml
 """
 name: my-python-agent
 allowed_tools: [search, summarize, calculate]
 blocked_patterns:
   - "(?i)(api_key|password|secret)\\s*[:=]"
 max_calls_per_request: 25
 require_human_approval: [send_email, delete_record, deploy]
 """

 - Tool allowlists — explicit list of what the agent can call
 - Content filters — scan inputs AND tool arguments for sensitive patterns
 - Human-in-the-loop — require approval for high-impact actions
 - Rate limits — prevent infinite loops and cost runaway

----------------------------------------------------------------------------------

4. 🎯 Rubric-Based Evaluation — Turn Requirements into Tests

From LTG427: translate natural-language requirements into testable artifacts:

 from azure.ai.projects.models import EvaluatorIds
 
 # Built-in evaluators for trustworthiness:
 evaluators = {
     "Relevance":    {"Id": EvaluatorIds.Relevance.value},
     "Groundedness": {"Id": EvaluatorIds.Groundedness.value},
     "Coherence":    {"Id": EvaluatorIds.Coherence.value},
     "Fluency":      {"Id": EvaluatorIds.Fluency.value},
 }
 
 # Risk & safety evaluators (from Learn docs):
 # - Protected materials (copyright detection)
 # - Code vulnerability (security scanning)
 # - Jailbreak detection
 # - Hate/violence/self-harm/sexual content
 # - Indirect attack detection

The workflow:

 1. Define requirements in natural language
 2. Generate concrete test behaviors + test cases
 3. Run evaluation suites (locally + in CI)
 4. Collect evidence of pass/fail per requirement
 5. Feed failures back into prompt refinement

----------------------------------------------------------------------------------

5. 🔴 AI Red Teaming Agent — Adversarial Testing

New at Build 2026 (from TT682 and ASSERT announcement):

 - ASSERT: open-source project for policy-driven safety evaluation
 - AI Red Teaming Agent: automatically probes your agent for jailbreaks, prompt injection, data exfiltration
 - Adaptive red teaming in LAB540: continuously stress-test in production

Python integration:

 # pip install azure-ai-evaluation
 from azure.ai.evaluation import AdversarialSimulator
 
 # Simulate attacks against your agent
 simulator = AdversarialSimulator(project_client)
 results = await simulator.run(
     target=your_agent_callback,
     scenario="jailbreak",  # or "prompt_injection", "data_exfil"
     max_conversations=50,
 )

----------------------------------------------------------------------------------

6. 🔐 Agent Security Stack (Entra + Defender + Purview)

Build 2026 introduced Agent 365 — unified governance for all agents:

┌───────────────┬──────────────────────────┬──────────────────────────────────────┐
│ Layer         │ What it does             │ Python relevance                     │
├───────────────┼──────────────────────────┼──────────────────────────────────────┤
│ Entra         │ Agent identity + auth    │ DefaultAzureCredential() for         │
│               │                          │ agent-to-service auth                │
├───────────────┼──────────────────────────┼──────────────────────────────────────┤
│ Defender      │ 100+ agents finding      │ Scans your deployed agents for       │
│ (MDASH)       │ exploitable bugs         │ vulnerabilities                      │
├───────────────┼──────────────────────────┼──────────────────────────────────────┤
│ Purview       │ Data governance +        │ Ensures agents don't leak sensitive  │
│               │ compliance               │ data                                 │
├───────────────┼──────────────────────────┼──────────────────────────────────────┤
│ Agent 365 SDK │ Enterprise control plane │ Register your agent, set policies,   │
│               │                          │ monitor behavior                     │
└───────────────┴──────────────────────────┴──────────────────────────────────────┘

----------------------------------------------------------------------------------

7. 🔄 GitHub Agentic Workflows — CI/CD for Agent-Era Code

From DEM350: Your repo can improve itself via GitHub Actions + AI agents:

 # .github/workflows/agent.yml — Agentic workflow
 # Copilot agents can:
 # - Triage issues automatically
 # - Fix CI failures and submit PRs
 # - Update docs when code changes
 # - Generate/improve tests
 # All sandboxed, all require human review before merge

The "Agentic SDLC" pattern:

 Plan → Delegate to Copilot → Agent generates PR
   → Automated tests + evals run in CI
   → Human reviews with full trace context
   → Merge with confidence

----------------------------------------------------------------------------------

8. 📦 Key Python Packages for Trustworthy Apps

 # Core AI
 azure-ai-projects          # Foundry agents, eval, tracing
 azure-identity             # Managed identity (DefaultAzureCredential)
 
 # Evaluation & Safety
 azure-ai-evaluation        # Local eval SDK, red teaming, built-in evaluators
 
 # Observability (from previous answer)
 azure-monitor-opentelemetry
 opentelemetry-sdk
 
 # Application Security
 pydantic                   # Input validation, schema enforcement
 structlog                  # Structured logging with correlation
 
 # Testing
 pytest                     # Test framework
 pytest-asyncio             # Async agent testing

----------------------------------------------------------------------------------

📺 Build 2026 Sessions — Trustworthy Python Development

┌─────────────┬──────────────────────────────────┬────────────────────────────────┐
│ Code        │ Title                            │ Key Takeaway                   │
├─────────────┼──────────────────────────────────┼────────────────────────────────┤
│ BRK250      │ Observe and control agents       │ End-to-end governance          │
│             │ across any framework             │ blueprint with open-source     │
│             │                                  │ tools                          │
├─────────────┼──────────────────────────────────┼────────────────────────────────┤
│ LTG402      │ Why GitHub Copilot misses        │ Rules, skills, prompt files,   │
│             │ context (and how to fix it)      │ custom agents                  │
├─────────────┼──────────────────────────────────┼────────────────────────────────┤
│ LTG405      │ Better tests, faster — GitHub    │ TDD-style agent development,   │
│             │ Copilot does the heavy lifting   │ CI quality gates               │
├─────────────┼──────────────────────────────────┼────────────────────────────────┤
│ LTG427      │ Rubric-Based Evaluation for Real │ Requirements → testable        │
│             │ World AI Systems                 │ artifacts → evidence           │
├─────────────┼──────────────────────────────────┼────────────────────────────────┤
│ LTG430      │ Agent Control Specification      │ Universal runtime guardrails   │
│             │                                  │ standard                       │
├─────────────┼──────────────────────────────────┼────────────────────────────────┤
│ DEM369      │ Responsible AI in Action         │ Safety filters + policies in   │
│             │                                  │ engineering workflows          │
├─────────────┼──────────────────────────────────┼────────────────────────────────┤
│ TT682       │ Trusted AI Built for Production  │ Risk thresholds, golden        │
│             │                                  │ datasets, CI/CD eval           │
│             │                                  │ integration                    │
├─────────────┼──────────────────────────────────┼────────────────────────────────┤
│ DEM350      │ GitHub Agentic Workflows         │ Repo automation that triages,  │
│             │                                  │ fixes, and tests               │
├─────────────┼──────────────────────────────────┼────────────────────────────────┤
│ ODSP912     │ Build agentic testing systems    │ Autonomous test agents for     │
│             │                                  │ autonomous code                │
├─────────────┼──────────────────────────────────┼────────────────────────────────┤
│ DEM303      │ Late to agentic coding? Don't    │ Planning, delegating,          │
│             │ panic, build.                    │ reviewing AI PRs with          │
│             │                                  │ guardrails                     │
└─────────────┴──────────────────────────────────┴────────────────────────────────┘

----------------------------------------------------------------------------------

🏗️ Architecture Summary — The Trust Stack

 ┌─────────────────────────────────────────────────────┐
 │  GitHub Copilot + Custom Instructions               │  ← Dev-time
 │  (rules, prompt files, skills for your standards)   │
 ├─────────────────────────────────────────────────────┤
 │  Agent Control Specification                        │  ← Runtime
 │  (tool allowlists, content filters, rate limits)    │
 ├─────────────────────────────────────────────────────┤
 │  Evaluation SDK + Red Teaming Agent                 │  ← Test-time
 │  (rubric evals, adversarial probing, CI gates)      │
 ├─────────────────────────────────────────────────────┤
 │  OpenTelemetry + Continuous Eval                    │  ← Production
 │  (traces, quality scores, feedback loops)           │
 ├─────────────────────────────────────────────────────┤
 │  Agent 365 + Entra + Defender + Purview             │  ← Governance
 │  (identity, threat detection, data compliance)      │
 └─────────────────────────────────────────────────────┘

The Build 2026 mantra: "Observe. Evaluate. Improve. Roll out safely. Repeat." — applied at every layer, with humans in the loop for high-stakes decisions.