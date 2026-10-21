---
name: graphify-workflow
description: Maps and explores a codebase using the installed Graphify CLI and its knowledge graph. Use before unfamiliar cross-file changes, architecture investigations, dependency tracing, or when repeated codebase exploration is wasting time.
---

# Graphify workflow

Use Graphify as a codebase navigation aid, not as a substitute for reading source or running tests.

1. Confirm the actual repository root. Do not assume the current directory is the repo root.
2. Check whether `graphify` exists and inspect supported commands with `graphify --help` and, if supported, `graphify --version`.
3. If missing, do not invent an install command or install an unrelated similarly named package. Refer to https://github.com/Graphify-Labs/graphify and follow its current Windows installation instructions.
4. Inspect CLI help and official instructions to determine how this version initializes, updates, queries, and reports the graph. Commands differ across versions; do not guess them.
5. Determine whether a project graph already exists and whether it is current enough. Use the documented update/refresh command when stale. Avoid rebuilding unnecessarily if incremental updates are supported.
6. Query the graph for relevant symbols, files, dependencies, callers, data flows, and tests. Keep queries focused.
7. Open actual source files for critical findings. Graph results are navigation hints, not proof of runtime behavior.
8. If Graphify fails, record the exact command and concise error. Fall back to targeted file search and source inspection.
9. After changes, update the graph using the documented command if needed and useful. Do not rebuild after every tiny edit without a reason.
10. Report evidence: command actually executed, relevant output, graph freshness, and source/tests additionally checked.

## Decision rule

- Use Graphify for cross-file changes, unfamiliar architecture, dependency tracing, large repositories, and repeated exploration.
- Skip it for simple one-line edits, isolated text changes, or when the tool is unavailable and setup costs more than targeted inspection.
- Prefer graph queries and targeted source reads over dumping the entire repository into context.

## Completion checklist

- [ ] Repository root verified
- [ ] CLI/version/help checked
- [ ] Graph existence/freshness checked
- [ ] Relevant graph queries executed or reason for fallback recorded
- [ ] Source code and tests inspected for critical claims
- [ ] No unsupported claim of Graphify usage
