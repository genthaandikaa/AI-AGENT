---
name: project-memory
description: Maintains durable, concise project memory and task-resumption state so Antigravity can reuse verified discoveries and avoid repeating audits or solved debugging work.
---

# Project memory and task continuity

## Files
Prefer an existing project memory/tracker if present. Otherwise use:
- `PROJECT_MEMORY.md`: durable facts and decisions.
- `TASK_STATE.md`: current task and immediate next steps.

Do not create duplicates such as `PROJECT_MEMORY_v2.md`, `FINAL_MEMORY_NEW.md`, or multiple competing task-state files.

## Before work
1. Verify repository root.
2. Read relevant project instructions and memory.
3. Check current Git status and task state.
4. Validate time-sensitive claims (installed versions, commands, paths, service status).
5. Inspect source for important assumptions.

## Durable memory should include
- Verified project structure and major subsystems.
- Architecture decisions, constraints, and rationale.
- Verified setup/build/test commands and prerequisites.
- Root causes of resolved issues and regression tests.
- Important integration contracts and actual endpoint/module locations.
- Known blockers, limitations, and unresolved risks.
- Graphify/skill availability and verified usage notes.

## Do not store
Secrets, `.env` values, API keys, cookies, access tokens, private user data, unverified guesses, huge logs, whole-file dumps, or temporary noise.

## After meaningful work
Update memory only when a fact is durable and verified. Keep it concise and remove obsolete facts when superseded. Record supporting evidence for important claims.

Update `TASK_STATE.md` with:
- Goal and scope.
- Completed steps with evidence.
- Files changed.
- Tests run and results.
- Blockers and assumptions.
- One clear next action.

## Resume protocol
When asked to continue, read `TASK_STATE.md`, verify the reported state against the working tree and artifacts, continue from the next unfinished action, and avoid repeating completed steps unless new evidence invalidates them.

Never claim the model has been trained or permanently improved merely because a note was written.
