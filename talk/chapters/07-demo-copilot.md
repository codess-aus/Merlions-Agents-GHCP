# Chapter 7: Walkthrough: Copilot Scaffolds the Safe Parts

**Runner:** [`talk/demos/demo1.ps1`](../demos/demo1.ps1)

---

This is Chapter 5's idea made concrete. In a few minutes, GitHub Copilot can
scaffold a new tool for the Hawker agent, add a guardrail, and write the tests.
Follow along step by step.

## Step by step

**1. Scaffold a typed tool.** Prompt Copilot for a function with a typed
signature, input validation, and a Pydantic return type:

```text
Add find_stalls(location: str, cuisine: str | None = None) -> list[Stall]
that calls the Maps API tool. Use the Stall pydantic model from models.py.
Validate location is non-empty. Type the return. Raise InvalidInput on bad input.
```

Result lives in [`tools/menu_index.py`](../../src/merlions/tools/menu_index.py)
and [`models.py`](../../src/merlions/models.py).

**2. Add a guardrail (policy as configuration).** Wrap the tool with the
governance decorator so the policy is loaded from YAML, not hardcoded:

```python
from merlions.governance import govern, load_policy

@govern(load_policy("hawker"))
def find_stalls(location: str, cuisine: str | None = None) -> list[Stall]:
    ...
```

The policy ([`policies/hawker.yaml`](../../src/merlions/policies/hawker.yaml))
sets the allowlist, blocked patterns, a call limit, and `require_citation`.
**Your security team can change it without a code change or deployment.**

**3. Generate the unhappy-path tests first.** Ask Copilot for empty input,
malicious input (an API key in an argument), tool failure with retry, and a
happy path. See [`tests/test_find_stalls.py`](../../tests/test_find_stalls.py).
Run them:

```bash
pytest tests/test_find_stalls.py -v   # all green
```

## The lesson

> Copilot didn't write the agent. It wrote the scaffolding so you could focus on
> agent behaviour.

Notice the order: **unhappy paths first.** That is what catches the bugs that
ship to production, including the **fail-closed** assertion that an ambiguous
policy match denies the call.

## Key terms

- **`@govern` decorator**: wraps a tool so every call is checked against the
  policy and audit-logged. See [`governance.py`](../../src/merlions/governance.py).
- **Fail-closed test**: a test that proves the system denies when uncertain.
- **Mock**: a stand-in for an external API so tests are fast and deterministic.

## Do this next

1. Run the walkthrough yourself: `./talk/demos/demo1.ps1` (no API keys, no
   network).
2. Recreate the flow on one of your own tools: signature → validation →
   `@govern` → unhappy-path tests.
3. Make "unhappy paths first" your default prompt to Copilot.

> 📺 **Build 2026 grounding:** **LTG405** (*Better tests, faster*) and
> **ODSP912** (*Build agentic testing systems to validate AI-generated code*).
