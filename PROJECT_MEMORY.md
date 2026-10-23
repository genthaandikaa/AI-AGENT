# PROJECT_MEMORY — Harmage Agents

> Memori persisten arsitektur, integrasi, dan keputusan teknis Harmage Virtual Enterprise.

## Project Identity
- **Repository Root:** `E:\AI Agent`
- **Main Framework / Stack:**
  - **Frontend:** React 18, Vite, TypeScript, Tailwind CSS, Lucide Icons (`E:\AI Agent\frontend`)
  - **Backend API:** FastAPI, Uvicorn, Python 3.14, SQLite WAL mode (`E:\AI Agent\harmage`)
  - **Office Engine:** Hermes3D (Next.js 15, Phaser 3, React 19) (`E:\AI Agent\hermes-3d`)
  - **Gateway Adapter:** Node.js WebSocket Server on port 18789 (`E:\AI Agent\hermes-3d\server\demo-gateway-adapter.js`)
  - **Video Clipper:** Cheat Clip PRO & local FFmpeg (`E:\cheat-clip-pro` & `harmage/creator/clipper_bridge.py`)
- **Port Allocations:**
  - `5173`: React Vite Frontend Dashboard
  - `9119`: Hermes Agent Web Dashboard (CLI config, sessions, API keys)
  - `9200`: Harmage FastAPI Backend Server
  - `3000`: Hermes3D Virtual Office
  - `18789`: WebSocket Gateway Adapter
  - `8000`: Cheat Clip PRO Video Clipper UI & API
- **Last Verified Date:** 21 Oktober 2026 (WIB)

---

## Architecture Map & Subsystems
- **Dashboard (`frontend/`):**
  - Grouped sidebar (Overview, Dashboard, Divisions, Tasks & Projects, Schedule, Meetings, Reports, Integrations, Activity Logs, Approvals, Settings).
  - Clean white & purple theme (#7c3aed primary) with dark text and white background.
  - Live token budget widget and countdown to midnight WIB reset.
- **Backend API (`harmage/`):**
  - Database: `harmage/data/harmage_operations.db` with tables: `tasks`, `decisions`, `meetings`, `reports`, `approval_requests`, `schedules`, `activity_logs`, `token_budget_windows`, `token_usage_events`, `token_reservations`, `token_deferred_queue`.
  - Token Budget Manager (`harmage/token_budget.py`): Shared 2,000,000 token combined daily ceiling (Qwen + Gemini) resetting midnight `Asia/Jakarta`.
  - LLM Brain Controller (`harmage/llm_brain.py`): Real AI completion with Gen-Z toxic/sassy tone and adaptive prompt sizing (Normal, Efficient, Conservation, Ceiling Reached).
  - Video Clipper Bridge (`harmage/creator/clipper_bridge.py`): Bridges into `E:\cheat-clip-pro\backend\video_engine.py` for automated vertical 9:16 video generation.
- **Hermes3D Office (`hermes-3d/`):**
  - 10 active NPCs with role-based identities, system prompts, and workspaces.
  - 5 standard agent markdown files populated: `IDENTITY.md`, `SOUL.md`, `AGENTS.md`, `USER.md`, `TOOLS.md`.
  - Full task integration (`tasks.list`, `tasks.create`, `tasks.update`, `tasks.delete`) mapped to Harmage SQLite tasks.
  - Background tab execution fix: `pauseOnBlur: false` in Phaser and multi-step dt catchup in `agentSimulation.ts`.

---

## Tools and Skills
- **Graphify:** Installed globally, version `0.9.58`.
- **Skills Available:**
  - `graphify-workflow`: Pemetaan kode dan investigasi dependensi terverifikasi.
  - `project-memory`: Pemeliharaan memori persisten proyek.
  - `skill-auditor`: Audit ketersediaan dan eksekusi skill.
  - `verify-before-done`: Verifikasi perubahan dan bukti pengujian sebelum selesai.
- **Playwright:** Configured with installed Google Chrome (`C:\Program Files\Google\Chrome\Application\chrome.exe`).

---
–
## Verified Decisions and Constraints
1. **Zero-Cost Cloud Policy:** Strict $0 budget. No paid cloud APIs, no subscriptions without explicit CEO approval.
2. **Shared AI Budget:** 2.000.000 token per hari gabungan Qwen + Gemini. Zona waktu reset: `Asia/Jakarta` (WIB).
3. **Office Persistence:** Jika token AI habis (mode Ceiling Reached), animasi kantor 3D/2D, render lokal, dan dashboard tetep berjalan tanpa freeze.
4. **Single Implementation Report:** Satu file laporan terpadu di `E:\AI Agent\HARMAGE_IMPLEMENTATION_REPORT.md`.

---

## Change Log
- 2026-10-21: Setup Harmage Antigravity Improvement Pack (`.agents`, rules, 4 skills, `PROJECT_MEMORY.md`, `TASK_STATE.md`).
- 2026-10-21: Fixed Hermes3D tasks integration (`result.tasks is not iterable` resolved).
- 2026-10-21: Fixed Hermes3D agent file generation (`IDENTITY.md`, `SOUL.md`, `AGENTS.md`, `USER.md`, `TOOLS.md`).
- 2026-10-21: Fixed background tab pause issue (`pauseOnBlur: false` and `agentSimulation` multi-step catchup).
- 2026-10-21: Implemented Shared AI Token Budget Manager (Qwen + Gemini 2M tokens) in SQLite and FastAPI.
- 2026-10-21: Resolved Hermes3D gateway connection timeout and "No local gateway found" (dual adapterType support, interactive status button, lastKnownGood persistence).
- 2026-10-21: Implemented frontend visual Token Budget Manager widget (gauge, mode badge, countdown to midnight WIB, breakdown Qwen + Gemini) and verified with Playwright test.
- 2026-10-21: Fixed NPC spawn point reset on browser refresh (anti-spawn reset): implemented direct desk seat spawning for working agents and continuous sessionStorage coordinate tracking in 2D (`agentSimulation.ts`) and 3D (`RetroOffice3D.tsx`). Verified with automated Playwright browser reload test.
- 2026-10-21: Implemented YouTube Long-Form Original Animated Explainer Pipeline (16:9): Topic Backlog & Rubric Scoring (`topic_backlog.py`), Factual Integrity & Source Ledger (`source_ledger.py`), 8-Stage Explainer Script Engine (`script_engine.py`), Per-Scene 16:9 Visual Renderer (`scene_renderer.py`), Full Assembly Pipeline (`longform_pipeline.py`), CEO Approval Gate integration, and Interactive Workbench in `DivisionsView.tsx`. 100% test suite verified with real 1920x1080 47.0s MP4 output.
- 2026-10-21: Unified Git Repository & Remote Configuration: Disconnected nested git repositories (`hermes-3d/.git` & `hermes-agent/.git`), initialized single unified root Git repository at `E:\AI Agent`, configured `.gitignore` (ignoring node_modules, .next, dist, pycache, .env, upstream test fixtures, and large binary media), committed 13,862 files, and successfully pushed clean `main` branch to remote `https://github.com/genthaandikaa/AI-AGENT.git`.
- 2026-10-21: Resolved Skills Catalog Crash: Defensively guarded `.trim()` in `catalog.ts` and `marketplace.ts` in `hermes-3d` to prevent TypeError on undefined skillKey/name.
- 2026-10-21: Resolved Telegram 429 Rate-Limit / Context Deadlock: Diagnosed that Telegram thread #1 had accumulated 343 messages (~372,437 tokens), exceeding Google AI Studio free tier 250k input limit. Released stale session leases, cleared thread #1 routing in Hermes `state.db` to route new prompts to a fresh session, and configured Gemini 2.5 Flash + multi-model fallback ladder.
- 2026-10-21: Synchronized All 10 Division NPCs to Active Working State: Mapped full assignee aliases in `harmage/server.py` (`NPC_ASSIGNEE_MAP`) and `hermes-3d/server/demo-gateway-adapter.js` (`ASSIGNEE_ALIASES`), seeded active `in_progress` tasks across all 10 roles in SQLite, verified real-time backend synchronization and lifecycle start events, placing all 10 avatars at their desks with typing animations and live task badges. Tested via Playwright with 0 errors.
- 2026-10-21: Permanent No-Demo Hermes Production Runtime & Continuous Work Fix: Eliminated demo mode and demo adapter branding. Adapter strictly returns `adapterType: "hermes"` with server identifier "Hermes Enterprise Production Gateway" and UI pill `HERMES • CONNECTED`. Resolved the 10-second work timeout bug by binding desk seating directly to `taskBoard.cardsByStatus.working` and sending continuous activity heartbeats every 2.5s. Agents now work continuously at their desks until their tasks are completed, and only rest when tasks are finished or during scheduled break times.
- 2026-10-21: Autonomous AI NPC Complex Brain & Simulation Engine (`harmage/npc_brain.py`): Implemented dynamic emotional simulation (morale, energy, stress, thoughts), schedule management based on WIB time (Morning Focus, Lunch Break, Afternoon Production, Standup Meeting, Free Rest), and autonomous inter-agent banter dialogue broadcast as `office.speech` bubbles. Created and registered dedicated skill `harmage-hermes-runtime` locally and globally.
- 2026-10-21: Purged All Hardcoded Dialogue Pools & Interaction Pairs: Refactored `harmage/npc_brain.py` to eliminate all static dialogue pools and canned if-else interaction pairs. Directly wired into `harmage.npc.build_npc_roster()` for dynamic persona souls, added persistent SQLite tables `npc_brain_memories` and `npc_brain_interactions`, integrated AI LLM completion with circuit breaker, and implemented dynamic procedural synthesis grounded in live SQLite tasks, actual token metrics, and real persona vocabulary ($0 cost fallback). Enhanced gateway adapter to stream speech bubbles to both 2D Pixel Office and 3D Retro Office. 100% verified via automated test suite.
- 2026-10-22: Dynamic xKiro API Key Hot-Reloading & Live Hermes Gateway Hardening: Integrated runtime key auto-reloading (`_load_env_key()`) into `harmage/llm_brain.py` so newly added API keys in `.env` take effect immediately without backend reboots. Hardened gateway adapter (`hermes-3d/server/demo-gateway-adapter.js`) to continuously stream all 10 agent live statuses and SQLite active task titles. Verified all 5 enterprise daemons running concurrently (Port 9200 FastAPI, Port 18789 Hermes Adapter, Port 3000 Next.js Office, Port 5173 Vite Dashboard, and host Telegram daemon) with 10/10 working agents seated at their respective desks. Changes cleanly committed and pushed to GitHub main branch.
- 2026-10-22: MiniMax 50M Event Token Pool Integration & Reasoning Architecture: Integrated xKiro 50M MiniMax Welcome Drop event token pool (`minimax/minimax-m3.1-flash` & `minimax/minimax-m3`) into `harmage/llm_brain.py` with custom reasoning token handling and fallback protection. Configured Hermes CLI `config.yaml` and `.env` with active xKiro key and MiniMax fallback. All 4 services verified live (9200, 3000, 5173, 18789) with 10/10 working agents. Cleanly committed and pushed to GitHub main branch.
- 2026-10-24: Jarvis-to-Antigravity MCP Bridge & Telegram Delegation Architecture: Implemented official stdio Model Context Protocol (MCP) server `harmage/mcp_bridge.py` and core bridge engine `harmage/bridge_engine.py`. Registered `antigravity_bridge` in Hermes CLI `config.yaml` with 4 native tools: `delegate_to_antigravity`, `check_antigravity_task`, `get_harmage_system_overview`, `switch_division_branch`. Created dedicated Hermes persona skill `harmage-antigravity-bridge` enforcing strict token conservation by delegating coding tasks from Telegram to Antigravity (Google AI Pro IDE). Added REST bridge endpoints to FastAPI (`/api/bridge/delegate`, `/api/bridge/tasks`, etc.). Cleanly verified with automated MCP discovery and live Telegram daemon polling.
- 2026-10-24: Codebase Hardcode Audit, Dynamic Configuration & Provider Stabilization: Audited entire repository for hardcoded secrets (0 found; all use `.env`). Eliminated hardcoded ports and URLs in `hermes-3d/server/demo-gateway-adapter.js`, `frontend/src/components/Hermes3DViewer.tsx`, `frontend/src/views/IntegrationsView.tsx`, and `harmage/server.py`, replacing them with dynamic environment variables (`process.env`, `window.location`, and `os.getenv`). Fixed Hermes Google Gemini 429 quota exhaustion (exceeded 20 req/day on free tier) by configuring `provider: "xkiro"` with `default: "qwen/qwen3.8-max:free"` in `config.yaml`. Updated `SOUL.md` to strictly prohibit `search_files` in `C:\Users\genn` for repo files and enforce instant delegation via `delegate_to_antigravity` whenever users ask to audit or remove hardcode. Pruned stale sessions in `state.db`. Verified live delegation test `TSK-AGY-B75ABA` completed via MCP bridge in 0.9s.
- 2026-10-24: Bidirectional Completion & Telegram Real-Time Notification: Built automatic bidirectional notification bridge (`complete_task()`, `send_telegram_notification()` in `bridge_engine.py`, `/api/bridge/complete` in FastAPI, and `complete_antigravity_task` MCP tool). When Antigravity completes tasks, it captures the origin chat/thread and immediately sends rich completion cards to Telegram via the bot without burning any Telegram LLM tokens. Live verified with messages #210 and #211 delivered to the user's supergroup.
- 2026-10-24: 3D Isometric Agent HQ Engine Rebuild (`TSK-AGY-220712`): Replaced 2D Phaser view with immersive 3D Isometric "Agent HQ" (Three.js & React Three Fiber). Created central hub "THE BRAIN" with pulsating concentric cyan neon rings, hologram beam, and shared memories counter, surrounded by 8 department island rooms (Research, Scripts & Coding, Social, Creative, Analytics, Trading & Shop, Dev & SysOps, Executive & HQ) connected by glowing laser pathways and animated data stream particles. Features seated low-poly avatars with live typing animations, room status billboards, and a full HUD overlay matching the reference screenshot (top nav, search `/`, live status pill, analytics toast, minimap radar). 100% verified with Playwright at 60 FPS, 0 console errors, and notified back to Telegram.
- 2026-10-24: Harmage Backend <-> Hermes Native Kanban (:9119) Sync Bridge (`TSK-AGY-231AF7`): Solved the disparate task boards dilemma by developing `harmage/kanban_sync_bridge.py`. It polls Harmage FastAPI backend (`:9200`) every 10s and synchronizes all tasks to Hermes Native Kanban SQLite (`%LOCALAPPDATA%\hermes\kanban.db`), mapping status (Queued->Todo, In Progress->Running, Completed->Done, Blocked->Blocked) and priority integers (0-3). Built-in reverse sync immediately propagates any card status changes made on `:9119` back to Harmage via `POST /api/tasks/{task_id}/status`. Verified live with Playwright on `http://127.0.0.1:9119/kanban?profile=default`, showing all 19 tasks populated, and sent rich completion card to Telegram.
- 2026-10-24: Unified Single-Port Dashboard (:5173), Full Programmer Division & Real-Time Token Pool: Reorganized entire workforce into a dedicated 5-role Software Engineering Division (David Kim - PIC/Tech Lead, Maya Lin - Frontend FE, Alex Vance - Backend BE, Sarah Jenkins - QA Sentinel, Chloe Bennett - UI/UX Designer). Auto-detected and connected authentic provider token pools in `harmage/realtime_tokens.py` based on user's actual xKiro account metrics (46.6M MiniMax Welcome Drop, 8.7M Token Bonus, 1.0M Qwen Free Daily Tier, 26.3M 30-day cumulative usage, $0.00 zero-cost). Synchronized Hermes native dashboard (:9119) into Harmage React dashboard (:5173) via `harmage/hermes_integration.py` and `HermesCoreView.tsx` with live session history and chat console. Unified separate port projects into port 5173 using Vite reverse proxy (Cheat Clip PRO :8000 embedded in `VideoStudioView.tsx`, Hermes3D :3000 embedded in `VirtualOfficeView.tsx`). 100% verified via automated Playwright test suite with 0 page errors.
