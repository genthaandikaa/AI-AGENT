---
name: harmage-hermes-runtime
description: Enforces production Hermes Enterprise Gateway runtime integration with Harmage backend, preventing fallback to demo mode and guaranteeing continuous office task execution.
---

# Harmage Hermes Runtime & AI NPC Office Skill

This skill documents and enforces the strict production runtime architecture for the Harmage Virtual Enterprise and Hermes3D office.

## 1. Absolute No-Demo Policy
- **Never use demo mode, demo mock data, or demo adapter branding.**
- The WebSocket gateway adapter (`hermes-3d/server/demo-gateway-adapter.js`) runs in strict production mode:
  - `adapterType: "hermes"`
  - Server name: `"Hermes Enterprise Production Gateway"`
  - Status pill must always display: `HERMES • CONNECTED`
- Persisted configuration at `~/.hermes/hermes3d/settings.json` must always specify:
  ```json
  "gateway": {
    "url": "ws://localhost:18789",
    "token": "",
    "adapterType": "hermes"
  }
  ```

## 2. Continuous Desk Work (Anti-10s Timeout)
- In a real office, employees work at their desks until their assigned tasks are finished.
- An agent must **never** be kicked to idle/wander after 5 or 10 seconds while their task is `in_progress` / `working`.
- **Implementation Mechanism**:
  1. `OfficeScreen.tsx`: checks `taskBoard.cardsByStatus.working` for assigned tasks. If an agent has an active working task, `hasWorkingTask` is `true`, keeping `effectiveAgent.status = "running"` and `officeAgent.status = "working"` indefinitely.
  2. `demo-gateway-adapter.js`: transmits continuous activity heartbeats every 2.5s for every agent in `workingSet` to keep client-side activity latches active.
  3. When an agent's task is marked `completed` / `done`, the agent stands up, is relieved, and is free to relax, drink coffee, or wander to the lounge (`idle`).

## 3. Autonomous AI NPC Brain & Office Schedule (WIB)
- The Harmage NPC Brain (`harmage/npc_brain.py`) manages:
  - **WIB Schedule (Asia/Jakarta)**:
    - `MORNING_WORK` (09:00 - 12:00 WIB): Deep Work at desks.
    - `LUNCH_BREAK` (12:00 - 13:00 WIB): Break time! Lounge, pantry, coffee.
    - `AFTERNOON_WORK` (13:00 - 17:00 WIB): Production execution.
    - `STANDUP_MEETING` (17:00 - 17:30 WIB): Daily meeting in Meeting Room.
    - `FREE_REST` (17:30 - 09:00 WIB): Rest / off-duty / standby.
  - **Dynamic Emotions & Morale**:
    - Tracks `morale`, `energy`, `stress`, `emotion`, and `current_thought` for all 10 personas.
  - **Autonomous Dialogue**:
    - Generates realistic in-character inter-agent banter broadcast via `office.speech` to 2D and 3D office bubbles.

## 4. Port Topology
- `3000`: Hermes3D Virtual Office (Next.js 15, Phaser 3)
- `5173`: Harmage React Dashboard
- `9200`: Harmage FastAPI Backend Server
- `18789`: Hermes Enterprise Gateway Adapter
