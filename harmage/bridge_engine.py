"""Bridge Engine connecting Hermes Agent (Telegram / Jarvis) to Antigravity (Google AI Pro IDE).

Enables Jarvis to act as the Mobile Commander while Antigravity acts as the Unlimited
Execution Engineer, saving Telegram LLM token quota by delegating heavy coding tasks.
"""

import json
import os
import sqlite3
import subprocess
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional

from harmage.config import DB_PATH, WORKSPACE_DIR
from harmage.db import get_connection, log_activity

JAKARTA_TZ = timezone.utc  # or WIB offset

DIVISION_BRANCH_MAP = {
    "content_creator": "division/content-creator-affiliate",
    "affiliate": "division/content-creator-affiliate",
    "tiktok": "division/content-creator-affiliate",
    "creator": "division/content-creator-affiliate",
    "coding": "division/coding-engineering",
    "engineering": "division/coding-engineering",
    "developer": "division/coding-engineering",
    "frontend": "division/coding-engineering",
    "backend": "division/coding-engineering",
    "video_longform": "division/video-longform",
    "youtube": "division/video-longform",
    "longform": "division/video-longform",
    "treasury": "division/treasury-token-budget",
    "finance": "division/treasury-token-budget",
    "budget": "division/treasury-token-budget",
    "executive": "division/executive-operations",
    "manager": "division/executive-operations",
    "operations": "division/executive-operations",
    "qa": "division/qa-sentinel",
    "quality": "division/qa-sentinel",
    "sentinel": "division/qa-sentinel",
}

DIVISION_ASSIGNEE_MAP = {
    "division/content-creator-affiliate": "creator_pm",
    "division/coding-engineering": "antigravity_engineer",
    "division/video-longform": "editor_longform",
    "division/treasury-token-budget": "treasurer",
    "division/executive-operations": "executive_manager",
    "division/qa-sentinel": "qa_sentinel",
}

DELEGATED_LOG_FILE = WORKSPACE_DIR / "harmage" / "data" / "delegated_tasks.json"


def _resolve_division(division_input: str) -> tuple[str, str]:
    """Map natural language division input to git branch and assignee."""
    norm = division_input.lower().strip().replace("-", "_").replace(" ", "_")
    for key, branch in DIVISION_BRANCH_MAP.items():
        if key in norm:
            return branch, DIVISION_ASSIGNEE_MAP.get(branch, "antigravity_engineer")
    return "division/coding-engineering", "antigravity_engineer"


def _read_delegated_log() -> List[Dict[str, Any]]:
    if not DELEGATED_LOG_FILE.exists():
        return []
    try:
        with open(DELEGATED_LOG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def _save_delegated_log(tasks: List[Dict[str, Any]]):
    DELEGATED_LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(DELEGATED_LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=2, ensure_ascii=False)


def delegate_task(
    title: str,
    description: str = "",
    division: str = "coding",
    priority: str = "high",
    requested_by: str = "Jarvis (Telegram)"
) -> Dict[str, Any]:
    """
    Delegate a coding or operational task from Jarvis to Antigravity.
    
    Inserts into SQLite tasks table, marks git branch, and prepares Antigravity queue.
    """
    branch, assignee = _resolve_division(division)
    short_hash = uuid.uuid4().hex[:6].upper()
    task_id = f"TSK-AGY-{short_hash}"
    now_iso = datetime.now(timezone.utc).isoformat()

    conn = get_connection(DB_PATH)
    try:
        conn.execute(
            """
            INSERT INTO tasks (
                id, title, description, assignee, priority, status, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, 'in_progress', ?, ?)
            """,
            (
                task_id,
                f"[{branch.split('/')[-1].upper()}] {title}",
                f"{description}\n\n[Delegated by {requested_by} | Git Branch: {branch}]",
                assignee,
                priority.lower(),
                now_iso,
                now_iso
            )
        )
        conn.commit()
    finally:
        conn.close()

    # Append to JSON ledger
    tasks = _read_delegated_log()
    task_record = {
        "task_id": task_id,
        "title": title,
        "description": description,
        "division": division,
        "git_branch": branch,
        "assignee": assignee,
        "priority": priority,
        "requested_by": requested_by,
        "status": "queued_for_antigravity",
        "created_at": now_iso,
        "completed_at": None,
        "result_summary": None
    }
    tasks.insert(0, task_record)
    _save_delegated_log(tasks[:100])

    log_activity(
        "INFO",
        "BridgeEngine",
        f"Delegated {task_id} to Antigravity ({branch})",
        f"Requested by {requested_by}: {title}"
    )

    return {
        "success": True,
        "task_id": task_id,
        "title": title,
        "git_branch": branch,
        "assignee": assignee,
        "status": "queued_for_antigravity",
        "message": (
            f"Tugas [{task_id}] berhasil didelegasikan ke Antigravity!\n"
            f"Divisi / Branch: {branch}\n"
            f"Antigravity akan mengeksekusi kode menggunakan kuota Google AI Pro tanpa memakan token Telegram Anda."
        )
    }


def get_task_status(task_id: str = "latest") -> Dict[str, Any]:
    """Retrieve the status and outcome of a delegated task."""
    tasks = _read_delegated_log()
    if not tasks:
        return {"found": False, "message": "Belum ada tugas yang didelegasikan ke Antigravity."}

    target = None
    if task_id.lower() in ("latest", "last"):
        target = tasks[0]
    else:
        for t in tasks:
            if t["task_id"].lower() == task_id.lower():
                target = t
                break

    if not target:
        return {"found": False, "message": f"Tugas {task_id} tidak ditemukan."}

    # Cross check SQLite for live status updates
    conn = get_connection(DB_PATH)
    try:
        cur = conn.cursor()
        cur.execute("SELECT status, updated_at FROM tasks WHERE id = ?", (target["task_id"],))
        row = cur.fetchone()
        if row:
            db_status, updated_at = row
            target["live_db_status"] = db_status
            target["last_updated"] = updated_at
    except Exception:
        pass
    finally:
        conn.close()

    return {"found": True, "task": target}


def list_delegated_tasks(limit: int = 10) -> List[Dict[str, Any]]:
    """List recent delegated tasks."""
    return _read_delegated_log()[:limit]


def switch_division_branch(division: str) -> Dict[str, Any]:
    """Switch workspace git branch based on division."""
    branch, _ = _resolve_division(division)
    try:
        res = subprocess.run(
            ["git", "checkout", branch],
            cwd=str(WORKSPACE_DIR),
            capture_output=True,
            text=True,
            check=False
        )
        if res.returncode == 0:
            return {
                "success": True,
                "current_branch": branch,
                "message": f"Berhasil berpindah ke branch {branch}."
            }
        else:
            return {
                "success": False,
                "error": res.stderr.strip() or res.stdout.strip(),
                "message": f"Gagal berpindah branch: {res.stderr.strip()}"
            }
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_system_overview() -> Dict[str, Any]:
    """Return health of all 6 servers and current token metrics."""
    import socket
    import urllib.request

    ports_to_check = {
        9119: "Hermes Agent Web Dashboard",
        5173: "Harmage React Operations Dashboard",
        3000: "Hermes3D Virtual Office",
        9200: "Harmage FastAPI Backend",
        8000: "Cheat Clip PRO Video Engine",
        18789: "Hermes Enterprise Gateway Adapter",
    }

    port_status = {}
    for p, name in ports_to_check.items():
        s = socket.socket()
        s.settimeout(0.5)
        try:
            s.connect(("127.0.0.1", p))
            s.close()
            port_status[p] = {"name": name, "online": True}
        except Exception:
            port_status[p] = {"name": name, "online": False}

    # Check token metrics from SQLite
    token_stats = {"mode": "NORMAL", "confirmed_tokens": 0, "daily_limit": 2000000}
    try:
        conn = get_connection(DB_PATH)
        cur = conn.cursor()
        cur.execute(
            "SELECT confirmed_tokens, qwen_tokens, gemini_tokens, other_tokens, mode, daily_limit "
            "FROM token_budget_windows ORDER BY window_id DESC LIMIT 1"
        )
        row = cur.fetchone()
        if row:
            token_stats = {
                "confirmed_tokens": row[0],
                "qwen_tokens": row[1],
                "gemini_tokens": row[2],
                "minimax_event_tokens": row[3],
                "mode": row[4],
                "daily_limit": row[5],
                "minimax_event_pool": 50000000
            }
        conn.close()
    except Exception:
        pass

    return {
        "services": port_status,
        "token_metrics": token_stats,
        "active_divisions": [
            "division/content-creator-affiliate",
            "division/coding-engineering",
            "division/video-longform",
            "division/treasury-token-budget",
            "division/executive-operations",
            "division/qa-sentinel"
        ]
    }
