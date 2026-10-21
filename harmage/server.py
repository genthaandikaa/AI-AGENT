"""FastAPI backend server for Harmage Virtual Enterprise Admin Dashboard.

Provides RESTful endpoints for operational metrics, 2D NPC roster,
task management, schedules, approvals, meetings, reports, and activity logs.
"""

import json
import os
import sqlite3
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from harmage.config import DB_PATH, WORKSPACE_DIR
from harmage.db import get_connection, log_activity
from harmage.npc import build_npc_roster, NPCStatus
from harmage.models import TaskStatus, TaskPriority, RiskLevel, ActionType
from harmage.task_manager import TaskManager
from harmage.scheduler import get_all_schedules, trigger_heartbeat, toggle_schedule, add_schedule
from harmage.token_budget import token_budget_manager

app = FastAPI(title="Harmage Agents Executive Operations API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STATIC_DIR = Path(__file__).parent / "static"
STATIC_DIR.mkdir(parents=True, exist_ok=True)
(STATIC_DIR / "css").mkdir(exist_ok=True)
(STATIC_DIR / "js").mkdir(exist_ok=True)


# --- Pydantic Request Models ---
class TaskCreateRequest(BaseModel):
    title: str
    description: str = ""
    assignee: str
    priority: str = "medium"
    deadline: Optional[str] = None
    acceptance_criteria: Optional[List[str]] = None
    dependencies: Optional[List[str]] = None


class TaskStatusUpdateRequest(BaseModel):
    status: str
    evidence: Optional[str] = None
    failure_reason: Optional[str] = None


class ApprovalActionRequest(BaseModel):
    action: str  # "approved" or "rejected"
    ceo_notes: Optional[str] = None


class MeetingCreateRequest(BaseModel):
    title: str
    meeting_type: str = "internal_evaluation"
    agenda: str
    participants: List[str]
    discussion: Optional[str] = ""
    action_items: Optional[List[str]] = None


class ChatRequest(BaseModel):
    agent_id: str
    message: str
    history: Optional[List[Dict[str, str]]] = None


class BudgetConfigRequest(BaseModel):
    soft_limit: Optional[int] = None
    conservation_limit: Optional[int] = None
    safety_reserve: Optional[int] = None
    daily_limit: Optional[int] = None


class BudgetSimulateRequest(BaseModel):
    provider: str = "qwen"
    tokens: int = 500
    agent_id: str = "simulator"


class NPCScheduleRequest(BaseModel):
    period: str
    duration_minutes: int = 30


class NPCInteractRequest(BaseModel):
    initiator_id: Optional[str] = None
    recipient_id: Optional[str] = None


# --- REST Endpoints ---

@app.get("/api/overview")
def get_overview() -> Dict[str, Any]:
    """Retrieve high-level operational metrics and status summary."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row

    # Task metrics
    task_counts = {}
    for row in conn.execute("SELECT status, count(*) as cnt FROM tasks GROUP BY status").fetchall():
        task_counts[row["status"]] = row["cnt"]

    # Approvals pending
    pending_approvals = conn.execute("SELECT count(*) as cnt FROM approval_requests WHERE status = 'pending'").fetchone()["cnt"]

    # Totals
    total_decisions = conn.execute("SELECT count(*) as cnt FROM decisions").fetchone()["cnt"]
    total_meetings = conn.execute("SELECT count(*) as cnt FROM meetings").fetchone()["cnt"]
    total_reports = conn.execute("SELECT count(*) as cnt FROM reports").fetchone()["cnt"]

    # Recent activities (last 10)
    recent_logs = [dict(r) for r in conn.execute("SELECT * FROM activity_logs ORDER BY created_at DESC LIMIT 10").fetchall()]

    conn.close()

    # Roster status
    roster = build_npc_roster()
    active_npcs = sum(1 for n in roster.values() if n.status != NPCStatus.OFF_DUTY)

    budget_summary = token_budget_manager.get_status_summary()

    return {
        "status": "OPERATIONAL",
        "system_time": datetime.now(timezone.utc).isoformat(),
        "task_counts": task_counts,
        "total_tasks": sum(task_counts.values()),
        "pending_approvals": pending_approvals,
        "total_decisions": total_decisions,
        "total_meetings": total_meetings,
        "total_reports": total_reports,
        "active_npcs": active_npcs,
        "budget_spent_usd": 0.00,
        "budget_limit_usd": 0.00,
        "zero_cost_enforced": True,
        "token_budget": budget_summary,
        "recent_activities": recent_logs,
    }


NPC_ASSIGNEE_MAP = {
    "executive_manager": ["executive_manager", "alex_vance"],
    "treasurer": ["treasurer", "marcus_drake"],
    "executive_secretary": ["executive_secretary", "secretary", "sophia_chen"],
    "creator_pm": ["creator_pm", "diana_prince", "diana_pm"],
    "yt_shorts_specialist": ["yt_shorts_specialist", "leo_sparks", "video_editor", "leo_editor"],
    "yt_long_specialist": ["yt_long_specialist", "raka_pratama", "editor_longform"],
    "tiktok_specialist": ["tiktok_specialist", "maya_lin", "scriptwriter", "maya_script"],
    "tiktok_affiliate": ["tiktok_affiliate", "victor_sterling"],
    "quality_assurance": ["quality_assurance", "zackary_cross", "qa_sentinel"],
    "content_researcher": ["content_researcher", "ethan_cole", "researcher"],
    "quant_specialist": ["quant_specialist", "nova_vance"],
    "security_specialist": ["security_specialist", "kage_kuro"],
}


@app.get("/api/npcs")
def get_npcs() -> List[Dict[str, Any]]:
    """Retrieve the full 2D NPC roster with traits, system prompts, and SVG avatars."""
    roster = build_npc_roster()
    
    # Enrich with live active task if available
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    for npc_id, profile in roster.items():
        candidates = NPC_ASSIGNEE_MAP.get(npc_id, [npc_id])
        placeholders = ",".join("?" for _ in candidates)
        row = conn.execute(
            f"SELECT id, title, status FROM tasks WHERE assignee IN ({placeholders}) AND status = 'in_progress' LIMIT 1",
            candidates
        ).fetchone()
        if row:
            profile.status = NPCStatus.IN_PROGRESS
            profile.current_task = f"{row['id']}: {row['title']}"
    conn.close()

    results = []
    for p in roster.values():
        d = p.to_dict()
        b = npc_brain_manager.npc_states.get(p.id)
        if b:
            d["emotion"] = b.emotion
            d["morale"] = b.morale
            d["stress"] = b.stress
            d["energy"] = b.energy
            d["current_thought"] = b.current_thought
        results.append(d)
    return results


@app.get("/api/tasks")
def get_tasks(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    assignee: Optional[str] = None,
    limit: int = 100
) -> List[Dict[str, Any]]:
    """Query tasks with optional filtering."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    query = "SELECT * FROM tasks WHERE 1=1"
    params = []

    if status:
        query += " AND status = ?"
        params.append(status.lower())
    if priority:
        query += " AND priority = ?"
        params.append(priority.lower())
    if assignee:
        query += " AND assignee = ?"
        params.append(assignee)

    query += " ORDER BY CASE priority WHEN 'critical' THEN 1 WHEN 'high' THEN 2 WHEN 'medium' THEN 3 ELSE 4 END, created_at DESC LIMIT ?"
    params.append(limit)

    rows = conn.execute(query, params).fetchall()
    results = []
    for r in rows:
        d = dict(r)
        d["dependencies"] = json.loads(d["dependencies"]) if d.get("dependencies") else []
        d["acceptance_criteria"] = json.loads(d["acceptance_criteria"]) if d.get("acceptance_criteria") else []
        d["decision_log"] = json.loads(d["decision_log"]) if d.get("decision_log") else []
        results.append(d)
    conn.close()
    return results


@app.post("/api/tasks")
def create_task(req: TaskCreateRequest) -> Dict[str, Any]:
    """Create a new task in Harmage Task Manager."""
    tm = TaskManager()
    try:
        prio_enum = TaskPriority(req.priority.lower())
    except ValueError:
        prio_enum = TaskPriority.MEDIUM

    task = tm.intake_task(
        title=req.title,
        description=req.description,
        assignee=req.assignee,
        priority=prio_enum,
        deadline=req.deadline,
        acceptance_criteria=req.acceptance_criteria or [],
        dependencies=req.dependencies or []
    )
    log_activity("INFO", "task_manager", f"Created task {task.id}", f"Title: {task.title}, Assignee: {task.assignee}")
    return {"success": True, "task_id": task.id, "status": task.status.value}


@app.post("/api/tasks/{task_id}/status")
def update_task_status(task_id: str, req: TaskStatusUpdateRequest) -> Dict[str, Any]:
    """Transition task status with validation."""
    tm = TaskManager()
    try:
        status_enum = TaskStatus(req.status.lower())
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid status: {req.status}")

    try:
        task = tm.update_status(
            task_id=task_id,
            new_status=status_enum,
            evidence=req.evidence,
            failure_reason=req.failure_reason
        )
        log_activity("INFO", task.assignee, f"Task {task_id} transitioned to {status_enum.value}", req.evidence or req.failure_reason or "")
        return {"success": True, "task_id": task.id, "status": task.status.value}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/decisions")
def get_decisions(limit: int = 50) -> List[Dict[str, Any]]:
    """List recorded decisions and rationale."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM decisions ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()
    results = [dict(r) for r in rows]
    conn.close()
    return results


@app.get("/api/meetings")
def get_meetings(limit: int = 50) -> List[Dict[str, Any]]:
    """List historical internal meetings."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM meetings ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()
    results = []
    for r in rows:
        d = dict(r)
        d["participants"] = json.loads(d["participants"]) if d.get("participants") else []
        d["action_items"] = json.loads(d["action_items"]) if d.get("action_items") else []
        results.append(d)
    conn.close()
    return results


@app.post("/api/meetings")
def create_meeting(req: MeetingCreateRequest) -> Dict[str, Any]:
    """Record an internal company meeting."""
    import uuid
    meeting_id = f"MTG-{uuid.uuid4().hex[:8].upper()}"
    now = datetime.now(timezone.utc).isoformat()
    conn = get_connection()
    conn.execute(
        """
        INSERT INTO meetings (id, title, meeting_type, agenda, participants, discussion, action_items, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            meeting_id,
            req.title,
            req.meeting_type,
            req.agenda,
            json.dumps(req.participants),
            req.discussion or "",
            json.dumps(req.action_items or []),
            now
        )
    )
    conn.commit()
    conn.close()
    log_activity("INFO", "executive_secretary", f"Recorded meeting {meeting_id}: '{req.title}'")
    return {"success": True, "meeting_id": meeting_id}


@app.get("/api/reports")
def get_reports(limit: int = 30) -> List[Dict[str, Any]]:
    """List generated executive reports."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM reports ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()
    results = []
    for r in rows:
        d = dict(r)
        d["metrics"] = json.loads(d["metrics"]) if d.get("metrics") else {}
        results.append(d)
    conn.close()
    return results


@app.get("/api/approvals")
def get_approvals(status: Optional[str] = None) -> List[Dict[str, Any]]:
    """List governance approval requests."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    if status:
        rows = conn.execute("SELECT * FROM approval_requests WHERE status = ? ORDER BY created_at DESC", (status.lower(),)).fetchall()
    else:
        rows = conn.execute("SELECT * FROM approval_requests ORDER BY CASE status WHEN 'pending' THEN 1 ELSE 2 END, created_at DESC").fetchall()
    results = [dict(r) for r in rows]
    conn.close()
    return results


@app.post("/api/approvals/{approval_id}/act")
def act_on_approval(approval_id: str, req: ApprovalActionRequest) -> Dict[str, Any]:
    """CEO Approval Gate action (Approve or Reject)."""
    action = req.action.lower()
    if action not in ("approved", "rejected"):
        raise HTTPException(status_code=400, detail="Action must be 'approved' or 'rejected'")

    now = datetime.now(timezone.utc).isoformat()
    conn = get_connection()
    row = conn.execute("SELECT * FROM approval_requests WHERE id = ?", (approval_id,)).fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Approval request not found")

    conn.execute(
        "UPDATE approval_requests SET status = ?, ceo_notes = ?, resolved_at = ? WHERE id = ?",
        (action, req.ceo_notes or f"CEO {action}", now, approval_id)
    )
    conn.commit()
    conn.close()
    log_activity("GOVERNANCE", "CEO", f"Governance decision: {approval_id} -> {action.upper()}", req.ceo_notes or "")
    return {"success": True, "approval_id": approval_id, "status": action}


@app.get("/api/schedules")
def list_schedules() -> List[Dict[str, Any]]:
    """List all operational schedules."""
    return get_all_schedules()


@app.post("/api/schedules/heartbeat")
def execute_heartbeat() -> Dict[str, Any]:
    """Trigger an on-demand operational heartbeat check."""
    return trigger_heartbeat()


@app.post("/api/schedules/{schedule_id}/toggle")
def toggle_schedule_state(schedule_id: str, enabled: bool = Body(..., embed=True)) -> Dict[str, Any]:
    """Toggle persistent schedule active state."""
    res = toggle_schedule(schedule_id, enabled)
    return {"success": res, "schedule_id": schedule_id, "enabled": enabled}


@app.get("/api/activity")
def get_activity_logs(limit: int = 100) -> List[Dict[str, Any]]:
    """Retrieve activity and audit logs."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM activity_logs ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()
    results = [dict(r) for r in rows]
    conn.close()
    return results


@app.get("/api/integrations/status")
def get_integrations_status() -> Dict[str, Any]:
    """Audit status of local infrastructure, tools, and integrations."""
    ffmpeg_path = Path(r"C:\Users\genn\AppData\Local\hermes\tools\ffmpeg-9.0.1-win32-x64\ffmpeg.exe")
    ffmpeg_available = ffmpeg_path.exists()

    chrome_crx = Path(r"C:\Users\genn\AppData\Local\Google\Chrome\User Data\Default\Extensions\jambeljnbnfbkcpnoiaedcabbgmnnlcd\0.15.0_0")
    crx_installed = chrome_crx.exists()

    return {
        "ports": {
            "harmage_dashboard": {"port": 9200, "status": "ONLINE", "url": "http://localhost:9200"},
            "hermes_dashboard": {"port": 9119, "status": "ONLINE", "url": "http://localhost:9119"},
            "router_9router": {"port": 20128, "status": "ONLINE", "url": "http://127.0.0.1:20128"},
            "telegram_gateway": {"port": "PID 4020", "status": "ONLINE", "bot": "@weelsz_bot", "authorized_user": "8116783065"}
        },
        "tools": {
            "ffmpeg": {
                "installed": ffmpeg_available,
                "version": "9.0.1 (Windows x64)",
                "path": str(ffmpeg_path) if ffmpeg_available else None
            },
            "playwright_crx": {
                "installed": crx_installed,
                "version": "0.15.0",
                "path": str(chrome_crx) if crx_installed else None
            },
            "graphify": {
                "installed": True,
                "graph_json_nodes": 26887,
                "graph_json_edges": 54167,
                "html_exported": True
            }
        },
        "llm_stack": {
            "primary": "qwen/qwen3.8-max:free via xkiro ($0.00)",
            "fallback_1": "qwen/qwen3.8-omni-flash:free via xkiro ($0.00)",
            "fallback_2": "gemini-2.5-flash via Google ($0.00 free tier)",
            "zero_cost_policy": "STRICT_ENFORCED"
        }
    }


@app.post("/api/creator/produce")
def trigger_creator_pipeline() -> Dict[str, Any]:
    """Trigger the local Creator Division video production pipeline."""
    from harmage.creator.pipeline import CreatorPipeline
    pipeline = CreatorPipeline()
    result = pipeline.run_full_cycle()
    log_activity("INFO", "creator_pm", "Executed automated video production cycle", f"Task: {result.get('task_id')}")
    return result


# --- YouTube Long-Form (16:9) Endpoints ---

@app.get("/api/longform/topics")
def get_longform_topics(category: Optional[str] = None, status: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieve YouTube Long-Form topic discovery backlog with rubric scores."""
    from harmage.creator.topic_backlog import TopicBacklogEngine
    engine = TopicBacklogEngine()
    return engine.list_topics(category=category, status=status)


@app.post("/api/longform/topics")
def add_longform_topic(payload: Dict[str, Any] = Body(...)) -> Dict[str, Any]:
    """Score and add a new educational topic to the longform backlog."""
    from harmage.creator.topic_backlog import TopicBacklogEngine
    engine = TopicBacklogEngine()
    return engine.add_topic(
        category=payload.get("category", "counterfactual"),
        title=payload["title"],
        hook_question=payload.get("hook_question", ""),
        scores=payload.get("scores", {}),
        editorial_rationale=payload.get("editorial_rationale", ""),
        source_links=payload.get("source_links", [])
    )


@app.post("/api/longform/produce")
def trigger_longform_production(topic_id: Optional[str] = None) -> Dict[str, Any]:
    """Trigger autonomous 16:9 YouTube Long-Form educational video production."""
    from harmage.creator.longform_pipeline import LongFormProductionPipeline
    pipeline = LongFormProductionPipeline()
    result = pipeline.produce_pilot_longform(topic_id=topic_id)
    return result


@app.get("/api/longform/status")
def get_longform_production_status() -> Dict[str, Any]:
    """Get active stage progression, scene count, and artifact status for longform."""
    from harmage.creator.longform_pipeline import LongFormProductionPipeline
    pipeline = LongFormProductionPipeline()
    latest = pipeline.get_latest_production()
    return {"latest": latest}


@app.get("/api/longform/video/{slug}")
def stream_longform_video(slug: str):
    """Stream or download rendered 16:9 longform MP4."""
    target_mp4 = Path("E:/AI Agent/harmage/output/youtube-longform") / slug / "renders" / "final_longform_16x9.mp4"
    if not target_mp4.exists():
        target_mp4 = Path("E:/AI Agent/harmage/output/youtube-longform") / slug / "renders" / "preview_longform_proxy.mp4"
    if not target_mp4.exists():
        raise HTTPException(status_code=404, detail="Video render not found for slug")
    return FileResponse(str(target_mp4), media_type="video/mp4", filename="longform_16x9.mp4")


@app.post("/api/creator/clip")
def trigger_clipper(
    source_file: Optional[str] = None,
    title: Optional[str] = None,
    duration: float = 15.0
) -> Dict[str, Any]:
    """Trigger the Cheat Clip PRO local video clipper engine."""
    from harmage.creator.clipper_bridge import ClipperBridge
    bridge = ClipperBridge()
    default_src = str(WORKSPACE_DIR / "contoh-video-konten" / "tiktok-affiliate1.mp4")
    src = source_file or default_src
    out_name = f"clipped_export_{int(datetime.now().timestamp())}.mp4"
    result = bridge.produce_clip(
        source_video_path=src,
        output_filename=out_name,
        aspect_ratio="9:16",
        clip_duration=duration,
        title_text=title or "Harmage Auto-Clipped Video"
    )
    log_activity("INFO", "video_editor", "Clipped video via Cheat Clip PRO engine", f"Output: {result.get('output_path')}")
    return result


@app.post("/api/chat")
def handle_agent_chat(req: ChatRequest) -> Dict[str, Any]:
    """Execute live chat with NPC powered by real AI brain."""
    from harmage.llm_brain import query_agent_brain
    return query_agent_brain(req.agent_id, req.message, req.history)


@app.post("/api/standup")
def trigger_daily_standup() -> Dict[str, Any]:
    """Trigger the daily afternoon standup for Creator & Affiliate division and dispatch report to CEO."""
    from harmage.llm_brain import execute_afternoon_standup
    return execute_afternoon_standup()


# --- Shared Token Budget Endpoints ---

@app.get("/api/budget/status")
def get_budget_status() -> Dict[str, Any]:
    """Retrieve real-time Shared AI Token Budget metrics (Qwen + Gemini combined)."""
    return token_budget_manager.get_status_summary()


@app.get("/api/budget/deferred")
def get_deferred_tasks() -> List[Dict[str, Any]]:
    """Retrieve tasks deferred due to token conservation or daily ceiling."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute("SELECT * FROM token_deferred_queue ORDER BY created_at DESC LIMIT 50").fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


@app.get("/api/budget/history")
def get_budget_history() -> Dict[str, Any]:
    """Retrieve recent token events and daily windows."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    try:
        windows = [dict(r) for r in conn.execute("SELECT * FROM token_budget_windows ORDER BY window_start DESC LIMIT 7").fetchall()]
        recent_events = [dict(r) for r in conn.execute("SELECT * FROM token_usage_events ORDER BY created_at DESC LIMIT 50").fetchall()]
        return {"windows": windows, "recent_events": recent_events}
    finally:
        conn.close()


@app.post("/api/budget/config")
def update_budget_config(req: BudgetConfigRequest) -> Dict[str, Any]:
    """Update token budget limits and safety thresholds."""
    return token_budget_manager.update_config(
        soft_limit=req.soft_limit,
        conservation_limit=req.conservation_limit,
        safety_reserve=req.safety_reserve,
        daily_limit=req.daily_limit
    )


@app.post("/api/budget/simulate")
def simulate_budget_usage(req: BudgetSimulateRequest) -> Dict[str, Any]:
    """Simulate consumption for unit testing without spending real tokens."""
    return token_budget_manager.simulate_token_consumption(
        provider=req.provider,
        tokens=req.tokens,
        agent_id=req.agent_id
    )


@app.post("/api/budget/reset")
def reset_budget_window() -> Dict[str, Any]:
    """Reset active window counters (administrative/testing override)."""
    return token_budget_manager.reset_active_window()


# --- Autonomous AI NPC Brain & Simulation Endpoints ---

from harmage.npc_brain import npc_brain_manager


@app.get("/api/npc/brain/schedule")
def get_npc_schedule() -> Dict[str, Any]:
    """Retrieve current office schedule, WIB clock, and active period."""
    return npc_brain_manager.get_effective_schedule()


@app.post("/api/npc/brain/schedule")
def set_npc_schedule(req: NPCScheduleRequest) -> Dict[str, Any]:
    """Set manual office period override (e.g. LUNCH_BREAK, MORNING_WORK, STANDUP_MEETING, AUTO_WIB)."""
    if req.period.upper() in ("AUTO_WIB", "RESET", "CLEAR"):
        result = npc_brain_manager.clear_schedule_override()
    else:
        result = npc_brain_manager.set_schedule_override(req.period, req.duration_minutes)
    log_activity("INFO", "npc_brain", f"Schedule changed to {result['period']}", result.get("description", ""))
    return result


@app.get("/api/npc/brain/state")
def get_npc_brain_state() -> Dict[str, Any]:
    """Retrieve full autonomous emotional, energy, stress, and thought state for all 10 NPCs."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    tasks = [dict(r) for r in conn.execute("SELECT id, title, assignee, status FROM tasks").fetchall()]
    conn.close()
    states = npc_brain_manager.update_all_npcs(active_tasks=tasks)
    return {
        "schedule": npc_brain_manager.get_effective_schedule(),
        "npcs": states,
        "recent_dialogues": npc_brain_manager.recent_dialogues[:10]
    }


@app.post("/api/npc/brain/interact")
def trigger_npc_interaction(req: Optional[NPCInteractRequest] = None) -> Dict[str, Any]:
    """Trigger realistic autonomous dialogue and interaction between Harmage NPCs."""
    init_id = req.initiator_id if req else None
    recip_id = req.recipient_id if req else None
    dialogue = npc_brain_manager.trigger_interaction(init_id, recip_id)
    log_activity(
        "INFO",
        "npc_brain",
        f"Dialogue: {dialogue['initiator']['name']} -> {dialogue['recipient']['name']}",
        f"{dialogue['initiator']['name']}: \"{dialogue['initiator']['speech']}\" | {dialogue['recipient']['name']}: \"{dialogue['recipient']['speech']}\""
    )
    return dialogue


@app.get("/api/npc/brain/dialogues")
def get_npc_dialogues() -> List[Dict[str, Any]]:
    """Retrieve recent autonomous banter and communications between NPCs."""
    return npc_brain_manager.recent_dialogues



# Mount Static Files
FRONTEND_DIST = WORKSPACE_DIR / "frontend" / "dist"
if (FRONTEND_DIST / "assets").exists():
    app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIST / "assets")), name="react-assets")

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/")
def serve_index():
    """Serve the Single Page Dashboard."""
    if (FRONTEND_DIST / "index.html").exists():
        return FileResponse(FRONTEND_DIST / "index.html")
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {"message": "Harmage Operations Dashboard API Running. Index HTML loading..."}
