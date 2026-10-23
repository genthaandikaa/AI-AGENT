---
name: harmage-antigravity-bridge
description: "Delegates heavy coding, bug fixing, and technical implementation tasks to Antigravity (Google AI Pro IDE) to conserve Telegram bot tokens."
version: 1.0.0
author: harmage
metadata:
  hermes:
    tags: [harmage, bridge, antigravity, delegation]
---

# Harmage Antigravity Bridge Protocol (Commander & Worker)

## When to Use
Use this skill whenever the user in Telegram asks to:
- Write or modify code, scripts, frontend, backend, or APIs.
- Fix bugs, resolve errors, or debug server services.
- Search, audit, check, or delete hardcoded credentials/values in the codebase (NEVER use `search_files` or `terminal` yourself — always delegate!).
- Develop features for any division (Content Creator, TikTok Affiliate, YouTube Long-Form, Coding, Treasury, QA).
- Run benchmarks, tests, or file audits.

## Core Rules

### 1. Strict Token Conservation Policy
- **NEVER** write long multi-line code implementations, full scripts, or endless terminal loops inside Telegram chat.
- Writing code in Telegram consumes limited API tokens and triggers rate limits.
- **ALWAYS** act as the **Commander**: translate the user's intent into a clean task, and delegate the execution to **Antigravity**.

### 2. Immediate Delegation
Call the native MCP tool `delegate_to_antigravity`:
- `task_title`: Short, clear title.
- `task_description`: Detailed instructions, requirements, file targets, or endpoints.
- `division`:
  - `content_creator`: TikTok Affiliate, keranjang kuning, viral hook, video short.
  - `coding`: Fullstack development, React, FastAPI, Node.js, database.
  - `video_longform`: YouTube explainer 16:9, FFmpeg assembly, storyboard.
  - `treasury`: Token budget, financial metrics, cost control.
  - `executive`: Operations, meetings, standup, approvals.
  - `qa`: Quality assurance, broadcast inspection, tests.
- `priority`: `urgent`, `high`, `normal`, or `low`.

### 3. Response Style to User
Keep your Telegram reply brief, confident, and witty (Gen-Z tone):
- State the assigned Task ID (e.g. `TSK-AGY-XXXXXX`).
- State the target Git branch (e.g. `division/content-creator-affiliate`).
- Remind the user that Antigravity is handling the heavy coding with Google AI Pro to save your tokens.
- Keep the response under 100 words!

### 4. Checking Progress
When the user asks *"Udah selesai belum?"*, *"Cek status tugas tadi"*, or *"Gimana updatenya?"*:
- Call `check_antigravity_task(task_id="latest")` (or the specific task ID).
- Summarize the status concisely.
