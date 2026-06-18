# GitHub Copilot workspace instructions for Merlions-Agents-GHCP
#
# These instructions are loaded automatically by GitHub Copilot in any editor
# open to this repository. They encode the project conventions so Copilot
# enforces them as you write code — not just in this repo, but as a template
# for your own trustworthy agent projects.
#
# To use this pattern in a new project:
#   1. Copy this file to .github/copilot-instructions.md
#   2. Copy src/merlions/governance.py and src/merlions/reliability.py
#   3. Write your policies in policies/*.yaml
#   4. Every tool function gets @govern(policy, tool_name=...)
#   5. Every external call gets @retry or a FallbackChain

## Project: Merlions — trustworthy multi-agent Python on Azure

This codebase demonstrates four pillars of trustworthy AI in Python:
**Transparency, Safety, Reliability, Observability.**

---

## Conventions Copilot must always follow

### 1. Every agent tool function must be governed

```python
# GOOD — governed, policy loaded from YAML, tool name explicit
from merlions.governance import govern, load_policy

POLICY = load_policy("hawker")  # reads policies/hawker.yaml

@govern(POLICY, tool_name="find_stalls")
def find_stalls(location: str, cuisine: str | None = None) -> list[Stall]:
    ...

# BAD — no governance, no audit trail, no rate limit
def find_stalls(location: str) -> list[Stall]:
    ...
```

### 2. Every tool must validate inputs and raise InvalidInput — never return None silently

```python
# GOOD
from merlions.models import InvalidInput

def find_stalls(location: str, ...) -> list[Stall]:
    if not location or not location.strip():
        raise InvalidInput("location is required")
    ...

# BAD — silent None, caller doesn't know why it failed
def find_stalls(location: str, ...) -> list[Stall] | None:
    if not location:
        return None
```

### 3. Policies live in YAML — never hardcode rules in Python

```yaml
# policies/my_agent.yaml
name: my_agent
allowed_tools:
  - tool_one
  - tool_two
blocked_patterns:
  - "(?i)(api[_-]?key|password|secret)\\s*[:=]?"
max_calls_per_request: 10
```

```python
# GOOD
policy = load_policy("my_agent")   # from YAML

# BAD
policy = Policy(name="my_agent", allowed_tools=["tool_one"], ...)  # hardcoded
```

### 4. Every factual LLM response must be grounded and cited

```python
# GOOD — retrieve then inject context into prompt, then cite
snippets = menu_index_search(query)
context = "\n".join(s.text for s in snippets)
citations = [s.source for s in snippets]

llm = complete(
    system=HAWKER_SYSTEM,          # instructs model to answer ONLY from context
    user=hawker_prompt(location, context),
    grounded_on=citations,         # attached to the reply automatically
    agent_id="hawker",
)
return AgentReply(summary=llm.text, citations=llm.grounded_on)

# BAD — ungrounded, no citation, model can hallucinate freely
response = llm.chat("Recommend dinner near Marina Bay")
return AgentReply(summary=response, citations=[])
```

### 5. Every external call must be retry-wrapped or inside a FallbackChain

```python
# GOOD — transient failures are retried; caller never sees a network blip
from merlions.reliability import retry, FallbackChain

@retry(max_attempts=3, exceptions=(TimeoutError, ConnectionError))
def call_api(url: str) -> dict: ...

# GOOD — multiple data sources, always returns something safe
result = FallbackChain(
    primary=lambda: live_data(),
    fallbacks=[lambda: cached_data(), lambda: safe_default()],
    label="my_fallback",
).run()

# BAD — one failure and the user gets an unhandled exception
def call_api(url: str) -> dict:
    return requests.get(url).json()
```

### 6. Refusal is a feature — agents say "I don't know" instead of hallucinating

```python
# GOOD
if not stalls:
    return AgentReply(
        agent_id="hawker",
        summary="I don't have a verified stall near that location right now.",
        citations=[],
    )

# BAD — fabricating a stall that wasn't retrieved
return AgentReply(summary=f"Try {random.choice(GUESSED_STALLS)}", citations=[])
```

### 7. Audit trail logs decisions, never raw user content

```python
# GOOD — log the decision and the rule, not the user's words
emit_event("policy.deny", policy="hawker", tool="find_stalls",
           matched_rule="blocked_patterns/api_key")

# BAD — PII or prompt injection evidence in the log
emit_event("policy.deny", user_input=user_text, ...)
```

### 8. Tests must cover unhappy paths first

When generating tests, always include:
- Empty / missing required input raises `InvalidInput`
- Credential-like argument raises `PolicyViolation`
- Rate limit exceeded raises `PolicyViolation`
- Tool / service unavailable returns safe fallback (no exception reaches caller)
- Happy path last

### 9. All return types must be typed Pydantic models

```python
# GOOD
class Stall(BaseModel):
    name: str
    centre: str
    source: str   # citation key — always required

# BAD
def find_stalls(...) -> dict:   # untyped, unchecked, no citation field
```

### 10. Azure observability: swap local JSON-lines for Azure Monitor in production

```python
# Local (dev/demo) — already wired in telemetry.py:
#   writes to .traces/traces.jsonl

# Production — add this to your app startup:
from azure.monitor.opentelemetry import configure_azure_monitor
configure_azure_monitor(
    connection_string=os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"]
)
# Then replace span() calls with OpenTelemetry spans — see telemetry.py header.
```

---

## File layout

```
src/merlions/
├── governance.py     # @govern decorator — copy this
├── reliability.py    # @retry + FallbackChain — copy this
├── llm.py            # LLM integration (Azure OpenAI + mock fallback) — copy this
├── telemetry.py      # JSON-lines tracing, swap for Azure Monitor in prod
├── models.py         # Shared Pydantic models
├── policies/         # YAML policies — one per agent
├── agents/           # hawker, haze, wisecracker, router
├── tools/            # maps, nea, menu_index
└── evals/            # cases.jsonl + runner + from_traces.py
```

## Generating a new agent

Ask Copilot:
> "Add a new agent called `transit` that checks MRT disruptions.
>  Follow the project conventions: governed tools, typed models,
>  FallbackChain with a safe default, LLM call grounded on retrieved data,
>  and tests covering empty input, credential injection, and happy path."

Copilot will read these instructions and apply all 10 conventions automatically.
