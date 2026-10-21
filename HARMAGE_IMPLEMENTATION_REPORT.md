# HARMAGE AGENTS — CONSOLIDATED IMPLEMENTATION REPORT
**Project:** Harmage Agents / Genn Enterprise  
**Workspace:** `E:\AI Agent`  
**Date:** 2026-10-21  
**Status:** Operational (Verified & Tested)

---

## 1. EXECUTIVE SUMMARY & EXISTING ARCHITECTURE DISCOVERED

An end-to-end audit and implementation across the Harmage Agents platform was conducted, verifying and connecting all requested components into a functioning AI virtual office enterprise.

### 1.1 Architecture & Services Matrix
| Component / Service | Technology Stack | Port / Protocol | Runtime Status | Verification Evidence |
| :--- | :--- | :--- | :--- | :--- |
| **Admin Dashboard UI** | React 18, Vite 8, Tailwind CSS, Lucide, TSX | `http://127.0.0.1:5173` | `Implemented` & `Tested` | Playwright test passed; screenshots captured in `qa_screenshots/` |
| **Hermes 3D Virtual Office** | Next.js 16, React 19, Three.js, R3F, Phaser | `http://127.0.0.1:3000` | `Implemented` & `Tested` | Embedded via iframe; CSP `frame-ancestors` configured |
| **Hermes Gateway Adapter** | Node.js WebSocket Server | `ws://127.0.0.1:18789` | `Implemented` & `Tested` | Dispatches 10 Harmage agent identities to 3D office |
| **Harmage Core Backend** | Python 3.14, FastAPI, SQLite WAL, Uvicorn | `http://127.0.0.1:9200` | `Implemented` & `Tested` | REST API with `/api/chat`, `/api/standup`, `/api/creator/clip` |
| **Video Clipper Engine** | Cheat Clip PRO (`E:\cheat-clip-pro`) + FFmpeg | Python Module & REST | `Implemented` & `Tested` | Rendered 11.93 MB MP4 clip via `render_clip_to_mp4()` |
| **Telegram Bot Gateway** | Python Hermes Gateway (`@weelsz_bot`) | Telegram to `8116783065` | `Implemented` & `Tested` | Automated standup reports dispatched to CEO |
| **AI Brain LLM Stack** | Qwen 3.8 Max Free (xkiro) + Gemini Fallback | Cloud Inference ($0.00) | `Implemented` & `Tested` | Live chat verified with authentic toxic Gen-Z Indonesian slang |

---

## 2. HERMES 3D INTEGRATION (PHASE 2)

### 2.1 Installation & Configuration
* **Location:** `E:\AI Agent\hermes-3d`
* **Version:** Next.js 16.1.7, React 19.2.3, Three.js 0.185.1, Phaser 3.90.0
* **Cross-Origin Configuration:** Updated `hermes-3d/next.config.ts` to allow framing from `http://localhost:5173`, `http://localhost:9200`, `http://127.0.0.1:5173`, and `http://127.0.0.1:9200`. Removed `X-Frame-Options: SAMEORIGIN` to enable seamless embedding inside the React dashboard.
* **Environment File:** `E:\AI Agent\hermes-3d\.env.local` configured with:
  ```env
  NEXT_PUBLIC_GATEWAY_URL=ws://localhost:18789
  HERMES3D_GATEWAY_URL=ws://localhost:18789
  HERMES3D_GATEWAY_ADAPTER_TYPE=demo
  DEMO_ADAPTER_PORT=18789
  PORT=3000
  HOST=127.0.0.1
  DEBUG=false
  ```

### 2.2 Dashboard Embedding
* The former fake 2D canvas (`Office2DCanvas.tsx`) with hardcoded speeches was **completely deleted**.
* Created `frontend/src/components/Hermes3DViewer.tsx` inside `frontend/src/views/OverviewView.tsx` with live iframe embedding, fullscreen toggle, reload button, and direct tab opening shortcut.

---

## 3. REAL AI WORKERS & GEN-Z PERSONA SYSTEM (PHASE 3 & 4)

### 3.1 AI Inference Runtime
* **Primary LLM:** `qwen/qwen3.8-max:free` via `https://api.xkiro.com/v1/chat/completions`.
* **Fallback LLM:** `gemini-2.5-flash` via Google Generative AI free tier.
* **Backend Module:** `harmage/llm_brain.py` implementing `query_agent_brain()` and `execute_afternoon_standup()`.
* **Cost:** Strictly $0.00 cloud API cost.

### 3.2 Configured & Executable Agent Roster
| Agent ID | Name | Role Title | Division | Gen-Z Tone & Slang Persona | Authorized Tools |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `executive_manager` | Alex Vance | Executive Manager & Director | Executive Suite | Sarcastic, impatient with chaos, "sipaling manager", fr fr, no cap | Task delegator, scheduler, standup organizer |
| `treasurer` | Marcus Drake | Treasurer & Finance Controller | Executive Suite | Extreme hawk on $0 budget, suspicious of API credit burn, "sipaling hemat" | DB auditor, revenue tracker, budget blocker |
| `secretary` | Sophia Chen | Executive Secretary | Executive Suite | Subtly sassy notulen, organizes archives, reminds deadlines | Meeting minutes recorder, task logger |
| `creator_pm` | Diana Prince | PIC Divisi Konten & Affiliate | Creator Hub | Energetic, direct, hates delays, leads daily 17:00 standup | Pipeline runner, standup dispatcher, telegram reporter |
| `video_editor` | Leo Sparks | Shorts Video Editor (9:16) | Creator Hub | Opinionated about pacing & FFmpeg hardware acceleration | Cheat Clip PRO engine, local FFmpeg renderer |
| `editor_longform`| Raka Pratama | Long-Form Editor (16:9) | Creator Hub | Focused on 3-act storytelling, sound effects, pacing | Narrative outline generator, asset assembler |
| `scriptwriter` | Maya Lin | TikTok Viral Scriptwriter | Creator Hub | Trend-obsessed, 3-second hook specialist, meme literate | Viral script drafter, caption optimizer |
| `tiktok_affiliate`| Victor Sterling | TikTok Affiliate Lead | Affiliate Hub | Cuan hunter, evaluates winning products & yellow cart conversion | Commission tracker, outfit trend analyst |
| `qa_sentinel` | Zackary Cross | QA Quality Sentinel | Governance | Nitpicky, roasts unreadable typography and broken audio | Artifact validator, QA pass/fail decider |
| `researcher` | Ethan Cole | Content Trend Researcher | Creator Hub | Fast fact-checker, uncovers viral podcast topics | Topic researcher, audience analyzer |

---

## 4. LOCAL VIDEO CLIPPER INTEGRATION (PHASE 6)

### 4.1 Discovery & Verification
* **Location Found:** `E:\cheat-clip-pro`
* **Core Engine:** `E:\cheat-clip-pro\backend\video_engine.py` (149 KB) containing native FFmpeg clipping, face detection, subtitle burning, and rendering.
* **Hardware Detection:** Utilizes local CPU and GPU encoders with fallback to `libx264`.

### 4.2 Harmage Integration Bridge
* **Module Created:** `harmage/creator/clipper_bridge.py`
* **API Route:** `POST /api/creator/clip` in `harmage/server.py`
* **Test Execution Evidence:**
  * **Command:** `Invoke-RestMethod -Uri "http://127.0.0.1:9200/api/creator/clip" -Method Post`
  * **Input Source:** `E:\AI Agent\contoh-video-konten\tiktok-affiliate1.mp4`
  * **Output Artifact:** `E:\AI Agent\harmage\output\clipped_renders\clipped_export_1792533750.mp4`
  * **Output File Size:** 11.93 MB (12,506,435 bytes)
  * **Aspect Ratio:** 9:16 (576x1024)
  * **Verification Status:** `Tested` & verified valid MP4 (`is_valid_mp4 = True`).

---

## 5. REFERENCE VIDEO AUDIT (`contoh-video-konten`) (PHASE 7)

### 5.1 Media Inspection (`ffprobe`)
Inspection conducted on the exact reference folder `E:\AI Agent\contoh-video-konten`:

| File Name | Duration | Resolution | Aspect Ratio | Video/Audio Codec | Bitrate | Production Classification |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `tiktok-affiliate1.mp4` | 16.20s | 576x1024 | 9:16 Vertical | h264 / AAC 44.1kHz | 1,390 kbps | TikTok Affiliate (Streetwear Tee) |
| `tiktok-affiliate2.mp4` | 23.77s | 1024x576 | Landscape rotated | h264 / AAC 44.1kHz | 1,259 kbps | TikTok Affiliate (Oriental Zip Hoodie) |
| `yotube-long1.mp4` | 398.97s (6.65 min) | 1920x1072 | 16:9 Landscape | h264 / AAC 48.0kHz | 493 kbps | YouTube Long-Form (Kok Bisa style history) |
| `youtube-long2.mp4` | 242.65s (4.04 min) | 1920x1080 | 16:9 Landscape | h264 / AAC 44.1kHz | 1,491 kbps | YouTube Long-Form (Animated science explainer) |

### 5.2 Production Specifications Derived
1. **TikTok Affiliate (Clothing & Outfits)**:
   * **Hook (0-2s):** Immediate on-body display or wooden hanger presentation showing texture and collar detail.
   * **Pacing (2-12s):** Rapid 2-second cuts alternating between front view, back typography, fabric stretch, and styling with pants.
   * **Text Overlay:** Centered emoji reaction (`🥶🔥💙`) and product title without obstructing the garment.
   * **Call To Action (12-16s):** Direct gesture toward the yellow shopping cart icon with scarcity messaging ("Checkout sebelum kehabisan").
2. **YouTube Long-Form (Animated Explainer)**:
   * **Hook (0-15s):** Intriguing question ("Bagaimana orang mesir kuno...", "Apa jadinya jika...") paired with high-contrast character animation.
   * **Progression:** 3-Act narrative structured as: Myth/Misconception -> Scientific/Historical evidence -> Modern relevance.
   * **Audio:** Warm, articulate Indonesian narration backed by dynamic acoustic/lo-fi background music and pop sound effects on visual reveals.

---

## 6. DAILY MEETINGS & PIC TELEGRAM REPORTING (PHASE 9)

### 6.1 Daily Afternoon Review (17:00 Standup)
* **Trigger Endpoint:** `POST /api/standup`
* **Participants:** Diana Prince (PIC), Leo Sparks (Editor), Maya Lin (Scriptwriter), Victor Sterling (Affiliate Lead), Zackary Cross (QA Sentinel), Sophia Chen (Notulen).
* **Automated Workflow:**
  1. Convenes division members via real LLM inference.
  2. Synthesizes daily output metrics (video renders, QA passes, affiliate drafts).
  3. Records notulen to SQLite `meetings` table.
  4. Generates an executive briefing into SQLite `reports` table.
  5. Dispatches formatted message via Hermes Telegram gateway to CEO Gentha (`8116783065`).

---

## 7. FINANCIAL MONITORING & $0 BUDGET ENFORCEMENT (PHASE 10)

### 7.1 Financial Hawk Controls
* **Enforcer:** Marcus Drake (Bendahara).
* **Cloud API Expenditure:** $0.00 (Hard limit enforced; no paid OpenAI, Anthropic, or ElevenLabs keys active).
* **Rendering Cost:** $0.00 (100% executed locally via FFmpeg and CPU/GPU hardware).
* **Storage Footprint:** Automatic cleanup of intermediate render files older than 24 hours.

---

## 8. AUTOMATED TESTING & PLAYWRIGHT QA EVIDENCE (PHASE 12)

Automated browser testing was executed using Google Chrome (`C:\Program Files\Google\Chrome\Application\chrome.exe`):

| Test Suite / Step | View Checked | Action Verified | Evidence Captured | Result |
| :--- | :--- | :--- | :--- | :--- |
| **01 Dashboard** | `/` (Dashboard) | Verified 4 KPI cards, quick action buttons, live chat | `qa_screenshots/01_dashboard_clean.png` | `Tested` (PASS) |
| **02 Overview** | `/` (Overview) | Verified Hermes 3D virtual office iframe & NPC roster | `qa_screenshots/02_overview_hermes3d.png` | `Tested` (PASS) |
| **03 Divisions** | `/` (Divisions) | Verified 4 sub-divisions, standup & render buttons | `qa_screenshots/03_divisions_clean.png` | `Tested` (PASS) |
| **04 Tasks** | `/` (Tasks) | Verified 5 Kanban columns (Queued, In Progress, Blocked, Review, Completed) | `qa_screenshots/04_tasks_kanban.png` | `Tested` (PASS) |
| **05 Approvals**| `/` (Approvals) | Verified CEO Governance Gate & Approve/Reject buttons | `qa_screenshots/05_approvals_gate.png` | `Tested` (PASS) |
| **06 Meetings** | `/` (Meetings) | Verified meeting minutes, transcript, and action items | `qa_screenshots/06_meetings_sync.png` | `Tested` (PASS) |

---

## 9. CHANGELOG OF FILES MODIFIED / CREATED

* `frontend/src/App.tsx`: Reorganized navigation; set Dashboard as primary view; fixed header and collapsible sidebar.
* `frontend/src/components/Sidebar.tsx`: Grouped into 4 functional categories (`UTAMA`, `OPERASIONAL`, `TATA KELOLA`, `SISTEM`); added icon-only minimize mode with hover expansion.
* `frontend/src/components/Hermes3DViewer.tsx`: Created embedded 3D office container pointing to `http://localhost:3000/office`.
* `frontend/src/components/AgentChatDrawer.tsx`: Connected to `POST /api/chat` with dynamic agent selector and Gen-Z AI brain.
* `frontend/src/views/DashboardView.tsx`: Built clean, minimalist dashboard with real KPIs, SQLite task queue, and live chat.
* `frontend/src/views/OverviewView.tsx`: Integrated Hermes 3D viewer and real AI NPC roster.
* `frontend/src/views/DivisionsView.tsx`: Built simplified Creator & Affiliate division view with one-click standup and render actions.
* `frontend/src/views/ApprovalsView.tsx`: Built CEO Governance Gate with one-click Approve/Reject endpoints.
* `frontend/src/views/MeetingsView.tsx`: Built standup minutes and action item viewer.
* `frontend/src/views/ReportsView.tsx`: Built daily executive report viewer.
* `frontend/src/views/ActivityView.tsx`: Built audit log stream with level filtering.
* `hermes-3d/next.config.ts`: Configured CSP frame-ancestors to permit localhost embedding.
* `hermes-3d/server/demo-gateway-adapter.js`: Configured 10 Harmage agent profiles and connected chat to Harmage backend.
* `hermes-3d/.env.local`: Configured ports and gateway parameters for plug-and-play operation.
* `harmage/creator/clipper_bridge.py`: Created bridge importing `cheat-clip-pro` video engine.
* `harmage/server.py`: Added `POST /api/creator/clip` endpoint.
* `harmage/tests/verify_ui_v2.py`: Automated Playwright test suite using local Google Chrome.

---

## 11. HARMAGE ANTIGRAVITY IMPROVEMENT PACK & PERSISTENT MEMORY

### 11.1 Installed Skills & Discovery
The repository root (`E:\AI Agent`) and global Antigravity configuration (`~/.gemini/config/skills`) now incorporate the 4 specialized engineering skills:
1. `graphify-workflow`: Real CLI knowledge graph exploration before modifying unfamiliar codebase areas.
2. `project-memory`: Durable, verified facts maintenance in `PROJECT_MEMORY.md` and `TASK_STATE.md`.
3. `skill-auditor`: Assistant tool diagnostics preventing unguided full-codebase audits.
4. `verify-before-done`: Mandatory test suite and screenshot verification before reporting tasks as completed.

### 11.2 Graphify CLI Verification (`graphify 0.9.58`)
* **Installed Version:** `graphify 0.9.58`
* **Knowledge Graph Evidence:** `graphify-out/graph.json` contains 26,887 nodes and 34,912 edges.
* **Hub Discovery:** `graphify god-nodes` successfully identified top structural hubs (`ContextCompressor`, `tool_error`, `ProcessRegistry`, `load_config`, `_process_tool_call`).
* **Query Execution:** `graphify query "how does task execution work"` traversed 26,887 nodes and returned exact callpaths for agent tool dispatching.

---

## 12. SHARED AI TOKEN BUDGET MANAGER (QWEN + GEMINI 2.0M TOKENS/DAY WIB)

### 12.1 Token Ceiling & Zero-Cost Architecture
To ensure strict adherence to the **$0.00 zero-cost cloud policy** while providing maximum throughput for video scripting and office banter, a shared daily quota of **2,000,000 tokens** is managed jointly across Qwen 3.8 Max (Primary Brain) and Gemini 2.5 Flash (Support/Fallback).

* **Timezone Boundary:** `Asia/Jakarta` (WIB). Every midnight (00:00:00 WIB), the token window atomically archives and a fresh 2M token allowance is initialized.
* **Database Tables (`harmage/db.py`):**
  * `token_budget_windows`: Historical daily token usage and status records.
  * `token_usage_events`: Granular event log with timestamps, agent IDs, providers, input/output tokens, and cost (\$0.00).
  * `token_reservations`: Atomic in-flight token locks preventing race conditions across simultaneous agent turns.
  * `token_deferred_queue`: Low-priority tasks parked during high-utilization modes.

### 12.2 Four Adaptive Work Modes
1. **Mode 1: Normal (0% – 80% / 0 – 1.6M tokens)**:
   * Full context retention and uncompressed reasoning prompts.
2. **Mode 2: Efficient (80% – 90% / 1.6M – 1.8M tokens)**:
   * Context compressor activated; max output capped at 400 tokens; background batching enabled.
3. **Mode 3: Conservation (90% – 100% / 1.8M – 1.95M tokens)**:
   * Non-critical creative tasks queued; fallback to ultra-light Gemini Flash prompts; strict token gating.
4. **Mode 4: Ceiling Reached (100% / 2.0M tokens)**:
   * AI inferences paused until 00:00 WIB reset; local office 3D/2D animation, local FFmpeg video rendering, and SQLite dashboard operations continue unaffected.

### 12.3 REST Endpoints & UI Visual Widget
* **FastAPI Backend Endpoints (`harmage/server.py`):**
  * `GET /api/budget/status`: Real-time consumption, percent used, active mode, provider breakdown, WIB countdown.
  * `GET /api/budget/history`: 30-day token consumption log.
  * `GET /api/budget/deferred`: Deferred task queue inspector.
  * `POST /api/budget/reset`: Manual emergency administrative reset.
* **Frontend Widget (`TokenBudgetWidget.tsx`):**
  * Embedded in `frontend/src/views/DashboardView.tsx` with dynamic gauge, Qwen vs Gemini breakdown, active mode pill, and live midnight WIB reset timer.
  * Header pill in `TopHeader.tsx` displaying `2.0M TOKEN/DAY (WIB)`.
  * Production bundle built successfully (`tsc -b && vite build`) and verified via Playwright screenshot.

---

## 13. HERMES 3D NPC ROLE EXECUTION, BACKGROUND EXECUTION & GATEWAY FIX

### 13.1 Root Cause & Bug Resolutions
1. **NPC Role Idleness & `result.tasks is not iterable`**:
   * Resolved by implementing `tasks.list`, `tasks.create`, `tasks.update`, `tasks.delete` in `hermes-3d/server/demo-gateway-adapter.js`.
   * Pre-populated all 5 standard markdown configuration files (`IDENTITY.md`, `SOUL.md`, `AGENTS.md`, `USER.md`, `TOOLS.md`) for all 10 NPCs with their Gen-Z toxic/sassy personalities, divisions, and tool permissions.
2. **Background Tab Pausing**:
   * Disabled Phaser canvas auto-pausing via `pauseOnBlur: false` in `hermes-3d/src/features/pixel-office/PixelOffice2D.tsx`.
   * Removed blur event listeners in `PixelOfficeScene.ts` and introduced multi-step delta time catchup in `agentSimulation.ts`.
3. **Gateway Timeout & "No local gateway found" Resolution**:
   * Root cause: UI was selecting `adapterType: "hermes"` which expected an OpenClaw/Hermes HTTP gateway on port 8642 with an auth token, while the running server was the Harmage Enterprise Gateway on port 18789.
   * Fixed by adding dual-adapter compatibility (`demo` and `hermes`) to `server/demo-gateway-adapter.js` so it accepts connections regardless of which backend is selected in the UI.
   * Converted status indicators in `PixelOffice2D.tsx` and `RetroOffice3D.tsx` into interactive buttons for one-click manual connection.
   * Saved `adapterType: "demo"` with `lastKnownGood` in `~/.hermes/hermes3d/settings.json`.
4. **Hermes Agent Telegram Integration**:
   * Verified that Hermes Agent (Process ID 4020, `hermes_cli.main gateway run`) runs in parallel, connected to Telegram DC (`149.154.166.110:443`), serving the human CEO while Hermes3D visualizes the 10 internal office staff.

### 13.2 NPC Spawn Point Reset Fix on Browser Reload (F5 Anti-Spawn Reset)
* **Status**: `Implemented` and `Tested` with automated Playwright browser session tests.
* **Problem Statement**: Every time the virtual office page was refreshed (`F5`), all NPCs snapped back to the initial spawn point (the doorway entrance at `tx: 8, ty: 37` in 2D or `pickSpawnPoint` doorway in 3D) and had to walk across the room again.
* **Root Cause**:
  1. React re-mount destroyed all in-memory coordinates in `agentsRef` and `PixelOfficeScene`.
  2. Agent instantiation previously initialized working agents at the door coordinates and only then calculated a walk path to their desk.
* **Resolution**:
  1. **Direct Desk Spawning (`agentSimulation.ts` & `RetroOffice3D.tsx`)**:
     * Working agents with an assigned desk are now spawned directly at their desk seat (`chairTx, chairTy` in 2D, `deskPos.x, deskPos.y` in 3D) with `isAlreadyAtTarget: true` and `path: []`.
  2. **Continuous Session Coordinate Persistence (`sessionStorage`)**:
     * Both 2D simulation tick loop and 3D `syncRenderAgentUi` (every 250ms) persist real-time agent positions to `sessionStorage` (`hermes3d:pixel:pos:${agent.id}` and `hermes3d:3d:agent:pos:${agent.id}`).
     * On reload, the simulation first attempts to restore exact coordinates from `sessionStorage`, ensuring agents stay exactly where they were even mid-walk or during meetings.
* **Automated Playwright Evidence**:
  * Evaluated across browser reloads on `http://localhost:3000/office`.
  * Verified 10 out of 10 working agents maintained their exact desk coordinates post-reload without returning to the door:
    * `executive_manager`: x=286, y=487
    * `treasurer`: x=353, y=316
    * `secretary`: x=681, y=137
    * `creator_pm`: x=459, y=206
    * `tiktok_affiliate`: x=622, y=365
    * `video_editor`: x=865, y=333
    * `scriptwriter`: x=663, y=369
    * `editor_longform`: x=403, y=532
    * `researcher`: x=500, y=579
    * `qa_sentinel`: x=783, y=158
  * Verified screenshot artifacts: `qa_screenshots_3d_before_reload.png` and `qa_screenshots_3d_after_reload.png`.

---

## 14. REMAINING LIMITATIONS & APPROVALS REQUIRED

1. **Social Media Publishing (TikTok / YouTube)**:
   * Automatic public posting is deliberately held behind the **CEO Governance Gate** (`ApprovalsView`). Public publishing requires manual review of the generated MP4 artifacts.
2. **Affiliate Sales Analytics**:
   * Live TikTok Affiliate commission tracking requires official TikTok Shop Creator API credentials or manual periodic CSV export uploads.
3. **Budget Policy**:
   * Strict $0 cloud policy is maintained. Upgrading to high-throughput cloud LLMs or ElevenLabs voices will require owner approval and budget adjustment in `SettingsView`.

---

## 15. YOUTUBE LONG-FORM ORIGINAL ANIMATED EXPLAINER PIPELINE (16:9)

### 15.1 Architectural Scope & Implementation Audit
* **Scope**: Dedicated YouTube Long-Form (16:9 landscape) educational explainer production pipeline. Backward-compatible with existing TikTok/Shorts and Clipper infrastructure.
* **Lead Agent**: `editor_longform` (Raka Pratama) assisted by `content_researcher`.
* **Zero-Cost Cloud API Adherence**: Confirmed $0 cloud spend policy. Google Veo / Google Flow checked: no paid API credentials configured. Fallback Ladder Option 2 & 4 activated (original generated 16:9 motion canvas and kinetic graphic scenes via local FFmpeg).

### 15.2 Components Implemented & Tested
1. **Topic Discovery & Rubric Scoring (`harmage/creator/topic_backlog.py`)**:
   * SQLite table `longform_topics` storing backlog, editorial rationale, and source links.
   * Transparent scoring algorithm (7 criteria minus risk penalty, max 70.0 points):
     $$\text{total} = \text{curiosity} + \text{education} + \text{evidence} + \text{visual} + \text{relevance} + \text{novelty} + \text{feasibility} - \text{risk}$$
   * Curated candidates pre-seeded across counterfactual science, biology, space physics, history, comparative religion, and thought experiments.
2. **Research & Source Ledger (`harmage/creator/source_ledger.py`)**:
   * Machine-readable `source_ledger.json` mapping script claims to verifiable institutions (NASA, USGS, Encyclopaedia Britannica).
   * Distinguishes established science from thought experiment assumptions with caveat notes.
   * Automated integrity QA validator ensuring no unverified or fabricated claims.
3. **8-Stage Explainer Script Engine (`harmage/creator/script_engine.py`)**:
   * Decomposes topic into the required 8 educational phases:
     1. Cold Open (5–15s hook)
     2. Curiosity Gap
     3. Promise & Boundaries
     4. Progressive Explanation
     5. Mid-Video Reset
     6. Nuance & Correction
     7. Payoff
     8. Closing & CTA
   * Decomposes into scene-by-scene storyboard (`S001` - `S00N`) with speech duration estimation at natural Indonesian pacing (~135 words/minute).
4. **Scene Visual Production & Asset Manifest (`harmage/creator/scene_renderer.py`)**:
   * Generates individual 1920x1080 16:9 scene clips with dynamic graphic cards, headline banners, technical callouts, and animated progress lines.
   * Structured `manifest.json` recording scene IDs, narration segments, durations, aspect ratio, and technical specs.
5. **Assembly, Audio Mixing & Render Pipeline (`harmage/creator/longform_pipeline.py`)**:
   * Offline Windows TTS voiceover generation (`System.Speech`).
   * Timed subtitle generation with bottom-centered safe margins.
   * Harmonic ambient drone BGM bed synthesis via FFmpeg.
   * Audio ducking (-18dB under voice) and EBU R128 audio normalization (`loudnorm`).
   * Low-resolution proxy preview (`preview_longform_proxy.mp4`) and high-resolution master MP4 (`final_longform_16x9.mp4`).
6. **CEO Governance Review Gate**:
   * Automatically registers an entry in `approval_requests` with status `pending` so no video is uploaded publicly without manual CEO review.
7. **Dashboard Integration (`frontend/src/views/DivisionsView.tsx`)**:
   * Interactive YouTube Long-Form Production Studio panel.
   * Real-time 9-stage progression stepper: `Topic Research → Fact Check → Script → Storyboard → Visual Assets → Editing → Render → QA → CEO Review`.
   * Topic Backlog table with scores and one-click production dispatch.
   * Embedded HTML5 video player streaming `/api/longform/video/{slug}`.

### 15.3 Verification & Test Evidence
* **Automated Test Suite (`harmage/tests/test_longform_pipeline.py`)**:
  * 5 out of 5 tests passed 100%:
    1. Topic Backlog & Rubric Scoring: `PASS` (evaluated 9 topics, top candidate score 64.4/70.0).
    2. Source Ledger Integrity: `PASS` (verified claims and source mappings).
    3. 8-Stage Explainer Script & Storyboard: `PASS` (generated 6 scenes, est. duration 47.0s).
    4. Google Veo & Fallback Ladder: `PASS` (Option 2 fallback properly verified).
    5. End-to-End Pilot Render & Media Validation: `PASS`.
* **ffprobe Validation Evidence**:
  * Output Path: `E:\AI Agent\harmage\output\youtube-longform\20261021_075610_apa_yang_terjadi_jika_oksigen_di_bumi_le\renders\final_longform_16x9.mp4`
  * Resolution: `1920x1080` (16:9 aspect ratio verified: 1.78)
  * Actual Duration: `47.00 seconds`
  * Video Codec: `h264`, Audio Codec: `aac`
  * File Size: `2,213,911 bytes (~2.21 MB)`
* **CEO Approval Request Registered**:
  * ID: `APP-LF-7FFFF8`
  * Requester: `editor_longform`
  * Action Type: `content_publishing`
  * Status: `pending`
* **Frontend UI Build & Verification**:
  * Production bundle built successfully (`tsc -b && vite build` in 12.00s, 0 errors).
  * Playwright verification screenshot captured: `qa_screenshots_youtube_longform_ui.png`.
