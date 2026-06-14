# Demo 1 — `find_stalls` "before" snippet

> Open this file in your editor during the recording. Ask Copilot Chat
> (or inline suggest) for each step. The "after" version is already in
> `src/merlions/agents/hawker.py` — peek there for the target shape.

```python
# src/merlions/agents/hawker_demo.py
# Empty scaffold for the Copilot demo. Ask Copilot to:
#   1. Implement find_stalls(location, cuisine) using maps_search.
#   2. Wrap it with @govern(POLICY) loaded from policies/hawker.yaml.
#   3. Add tests in tests/test_find_stalls.py covering:
#        - happy path
#        - empty location
#        - credential-in-arg (PolicyViolation)
#        - rate limit (>10 calls)
#        - unknown location returns []

from merlions.governance import govern, load_policy
from merlions.models import Stall
from merlions.tools.maps import maps_search

POLICY = load_policy("hawker")


# TODO(copilot): implement find_stalls here. Type the args. Validate inputs.
# Wrap with @govern(POLICY, tool_name="find_stalls").
```

## Suggested Copilot prompts (read aloud during the recording)

1. **"Implement `find_stalls(location: str, cuisine: str | None = None) -> list[Stall]` that calls `maps_search`. Validate location is non-empty. Raise `InvalidInput` on bad input."**
2. **"Wrap it with `@govern(POLICY, tool_name='find_stalls')`."**
3. **"Generate pytest cases in `tests/test_find_stalls.py` covering: empty location, malicious input (`api_key=...`), rate-limit (>10 calls), unknown location returns [], and a happy path."**

After Copilot generates each step, run:

```powershell
pytest tests/test_find_stalls.py -v
```

…and the panel shows 5 green checks. Cut to the closing slate.
