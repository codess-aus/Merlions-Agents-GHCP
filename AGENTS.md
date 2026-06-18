# AGENTS.md

## Merlions Repo Conventions

Use these conventions when adding or modifying agent-facing tools in this repository.

### Governed Tool Wrappers

For exported functions under `src/merlions/tools` that act as agent-callable tool entrypoints:

- Validate required string inputs in the wrapper before delegating.
- Treat empty and whitespace-only strings as invalid unless the existing API explicitly allows them.
- Raise `InvalidInput` with the exact message expected by existing tests and calling code.
- Keep the exported return type concrete and typed to the domain model, for example `list[Stall]`.
- Keep wrapper logic minimal and delegate the core lookup or retrieval work to the underlying tool implementation.

If the tool is governed by a repo policy:

- Load the matching policy with `load_policy` near module scope.
- Decorate the exported function with `@govern(policy, tool_name="...")`.
- Ensure the `tool_name` matches the policy allowlist entry.
- Prefer fail-closed behavior that is consistent with the existing governance model.

### Repo Patterns To Follow

- Reuse existing domain models from `merlions.models` instead of returning loose dictionaries.
- Reuse existing validation messages and exception types when a nearby tool already establishes the contract.
- Prefer small wrappers over duplicated business logic.
- Preserve append-only audit and least-privilege governance behavior.