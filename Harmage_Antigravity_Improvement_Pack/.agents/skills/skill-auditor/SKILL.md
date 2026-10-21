---
name: skill-auditor
description: Diagnoses why an AI coding assistant is not using Graphify, installed skills, scripts, or project rules. Use when tools are ignored, skills are not discovered, or workflows repeatedly start from scratch.
---

# Skill and tool audit

Determine whether a capability is installed, discoverable, callable, relevant, and actually executed. Do not confuse these stages.

1. Identify assistant surface/version and actual workspace root.
2. Inspect supported skill locations and current project/global instructions. Antigravity workspace skills: `.agents/skills/<name>/SKILL.md`; legacy `.agent/skills` may be supported; global skills: `~/.gemini/config/skills/<name>/SKILL.md`.
3. Validate `SKILL.md` frontmatter: valid folder name, `name`, and useful `description`. Keep `SKILL.md` directly inside the skill folder.
4. Check whether the skill appears in the assistant's discoverable skill list if exposed. If not, reopen/reload the workspace and check again.
5. Verify the executable independently. For CLI tools, inspect `--help` and version rather than assuming syntax.
6. Check whether the task matches the skill description.
7. Run a small harmless test and record evidence.
8. Categorize failure: not installed; installed but not discovered; discovered but not selected; selected but failed; executed but output not reused; or memory not persisted/re-read.
9. Fix only the identified cause. Do not reinstall blindly or overwrite existing config.
10. Summarize diagnosis, evidence, fix, and one next verification step.

Never read or output `.env` secrets. If config already exists, preserve it and propose a minimal diff.
