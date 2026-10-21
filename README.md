# AI-AGENT

**Harmage Virtual Enterprise & Hermes3D AI Office**

Autonomous AI enterprise platform featuring 10 active role-based NPCs in a virtual office, real-time shared token budget governance (Qwen + Gemini 2.0M daily token limit), YouTube Long-Form & Shorts production pipeline, and human-in-the-loop CEO governance.

---

## 🏛️ Architecture Overview

The system consists of five interconnected subsystems:

1. **Frontend Dashboard (`frontend/`)**:
   - Modern React 18, Vite, TypeScript, Tailwind CSS interface.
   - Live Token Budget Manager widget with gauge, provider breakdown, and countdown to midnight WIB reset.
   - Interactive YouTube Long-Form Production Studio (16:9), division management, task tracking, and CEO approvals.
   - Runs on `http://127.0.0.1:5173`.

2. **Backend API (`harmage/`)**:
   - High-performance FastAPI server running on Python 3.14 & Uvicorn.
   - Persistent SQLite storage in WAL mode (`harmage/data/harmage_operations.db`).
   - Shared AI Token Budget Manager (`harmage/token_budget.py`) with adaptive work modes (Normal, Efficient, Conservation, Ceiling Reached).
   - Real AI inference controller (`harmage/llm_brain.py`) powered by Qwen & Gemini ($0.00 cloud cost policy).
   - Local Cheat Clip PRO bridge (`harmage/creator/clipper_bridge.py`) and YouTube Long-Form 16:9 pipeline (`harmage/creator/longform_pipeline.py`).
   - Runs on `http://127.0.0.1:9200`.

3. **Virtual Office (`hermes-3d/`)**:
   - 3D Three.js immersive office and Gather-style 2D pixel canvas.
   - Anti-reset spawn persistence: NPCs maintain their exact desk coordinates across browser reloads via `sessionStorage`.
   - Background execution support: simulation continues seamlessly when the browser tab is blurred.
   - WebSocket Gateway Adapter (`server/demo-gateway-adapter.js`) running on port `18789`.
   - Runs on `http://localhost:3000/office`.

4. **Hermes Agent CLI Gateway**:
   - Direct Telegram bot integration connecting internal division workers to CEO forum topics.

5. **Creator & Video Production Pipeline**:
   - Autonomous YouTube Long-Form 16:9 explainer pipeline with 9-stage progression:
     `Topic Research → Fact Check → Script → Storyboard → Visual Assets → Editing → Render → QA → CEO Review`.
   - Offline Windows TTS voiceover, timed subtitle burning, ambient BGM synthesis, and FFmpeg loudnorm audio normalization.

---

## 🚀 Quick Start

### 1. Start Harmage FastAPI Backend
```bash
python -m uvicorn harmage.server:app --host 127.0.0.1 --port 9200
```

### 2. Start Hermes3D Gateway Adapter & Virtual Office
```bash
# Terminal 1: Gateway Adapter (Port 18789)
cd hermes-3d
node server/demo-gateway-adapter.js

# Terminal 2: Virtual Office (Port 3000)
cd hermes-3d
npm run dev -- -p 3000
```

### 3. Start Frontend Dashboard
```bash
cd frontend
npm run dev -- --host 127.0.0.1 --port 5173
```

---

## 🔒 Security & Governance

- **Zero-Cost Policy**: All AI models and render pipelines operate under a strict $0.00 budget policy.
- **CEO Governance Gate**: Automatic publishing to YouTube or TikTok requires explicit manual review and approval through the dashboard `/approvals` view.
