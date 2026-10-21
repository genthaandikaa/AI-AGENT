---
trigger: always_on
description: "Persistent workflow for Harmage engineering: reuse project memory, use Graphify when relevant, discover skills honestly, verify work, and avoid repeated audits."
---

# Harmage persistent engineering workflow

- Start by identifying the actual repository root and checking Git status, existing project instructions, `PROJECT_MEMORY.md`, `TASK_STATE.md`, and relevant existing documentation.
- Reuse verified, current findings. Do not repeat a full audit if a smaller targeted check is sufficient.
- For codebase mapping, invoke the `graphify-workflow` skill when relevant. Verify the installed CLI and its supported commands first. Never claim Graphify ran without command/output evidence.
- Discover and use relevant installed skills when their documented purpose matches the task. If a skill or tool is unavailable, state that and use a safe, explicit fallback.
- Before substantial edits, inspect the relevant source and tests, define a small plan, and preserve existing user changes and architecture.
- After meaningful work, update `PROJECT_MEMORY.md` only with durable, verified knowledge and update `TASK_STATE.md` with the exact next action.
- Do not save credentials, API keys, cookies, access tokens, private personal data, or raw `.env` contents in project memory.
- Avoid repeated full-file reads, repeated broad searches, unnecessary agent calls, and redundant reasoning. Read only relevant context and expand when evidence requires it.
- For every result, distinguish `Implemented`, `Tested`, `Partially implemented`, `Blocked`, and `Not verified`.
- Never claim a tool ran, a test passed, a file was inspected, or an integration works without evidence.
- Before finishing: inspect the diff, run the narrowest relevant tests, record failures and evidence, and leave the project resumable.
- Never run destructive commands, overwrite existing memory, change security boundaries, or perform paid/irreversible actions without appropriate authorization.
