---
name: verify-before-done
description: Verifies coding changes, integrations, and bug fixes with targeted tests and evidence before reporting completion. Use before finishing any non-trivial implementation or claiming something works.
---

# Verify before done

1. Read acceptance criteria and identify observable evidence for each.
2. Inspect Git diff and changed files; preserve unrelated user changes.
3. Select narrow useful checks first: formatter/linter, type check, focused tests, integration tests, then broad tests only when justified.
4. Discover actual project scripts and test commands from manifests/docs. Do not invent commands.
5. Run tests when safe and feasible. Ask for authorization before risky, expensive, destructive, or externally visible actions.
6. For integrations, verify the complete real path—not only a successful page load. Check runtime response, persisted state, artifacts, and error handling where applicable.
7. Report criteria as `Implemented`, `Tested`, `Partially implemented`, `Blocked`, or `Not verified`.
8. Include exact test commands and concise results. Do not hide failures or imply an unrun test passed.
9. Update project memory and task state with durable verified facts.
10. Stop when the requested scope is met; avoid unrelated refactors.
