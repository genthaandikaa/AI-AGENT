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


def _get_telegram_config() -> Dict[str, str]:
    """Load Telegram credentials and channel configuration from hermes environment."""
    env_file = Path(r"C:\Users\genn\AppData\Local\hermes\.env")
    cfg = {}
    if env_file.exists():
        try:
            with open(env_file, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        cfg[k.strip()] = v.strip()
        except Exception:
            pass
    return cfg


def _detect_telegram_origin() -> tuple[Optional[str], Optional[int]]:
    """Try to detect the active Telegram chat_id and thread_id from Hermes state.db."""
    state_db = Path(r"C:\Users\genn\AppData\Local\hermes\state.db")
    if not state_db.exists():
        return None, None
    try:
        conn = sqlite3.connect(str(state_db))
        c = conn.cursor()
        c.execute("SELECT chat_id, thread_id FROM sessions WHERE source = 'telegram' ORDER BY rowid DESC LIMIT 1")
        row = c.fetchone()
        conn.close()
        if row:
            chat_id = str(row[0]) if row[0] else None
            thread_id = int(row[1]) if row[1] and str(row[1]).isdigit() else None
            return chat_id, thread_id
    except Exception:
        pass
    return None, None


def send_telegram_notification(
    text: str,
    chat_id: Optional[str] = None,
    thread_id: Optional[int] = None,
    parse_mode: str = "Markdown"
) -> Dict[str, Any]:
    """Send a notification message via Telegram bot."""
    import urllib.request
    import urllib.error

    cfg = _get_telegram_config()
    token = cfg.get("TELEGRAM_BOT_TOKEN")
    if not token:
        return {"success": False, "error": "TELEGRAM_BOT_TOKEN not found in environment."}

    target_chat = chat_id or cfg.get("TELEGRAM_HOME_CHANNEL") or cfg.get("TELEGRAM_ALLOWED_USERS")
    if not target_chat:
        return {"success": False, "error": "No target Telegram chat_id configured."}

    payload: Dict[str, Any] = {
        "chat_id": target_chat,
        "text": text,
        "parse_mode": parse_mode
    }
    if thread_id is not None and int(thread_id) > 1:
        payload["message_thread_id"] = int(thread_id)

    req = urllib.request.Request(
        f"https://api.telegram.org/bot{token}/sendMessage",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return {"success": True, "result": data.get("result", {})}
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8", errors="ignore")
        # Fallback: if topic thread rejected, send to channel or direct user
        if "message_thread_id" in payload:
            del payload["message_thread_id"]
            try:
                req_fb = urllib.request.Request(
                    f"https://api.telegram.org/bot{token}/sendMessage",
                    data=json.dumps(payload).encode("utf-8"),
                    headers={"Content-Type": "application/json"}
                )
                with urllib.request.urlopen(req_fb, timeout=10) as resp_fb:
                    data_fb = json.loads(resp_fb.read().decode("utf-8"))
                    return {"success": True, "result": data_fb.get("result", {}), "fallback": "no_thread"}
            except Exception:
                pass
        return {"success": False, "error": f"HTTP {e.code}: {err_msg}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


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
    origin_chat, origin_thread = _detect_telegram_origin()

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
        "origin_chat_id": origin_chat,
        "origin_thread_id": origin_thread,
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


def complete_task(
    task_id: str,
    result_summary: str,
    git_commit_hash: Optional[str] = None,
    notify_telegram: bool = True
) -> Dict[str, Any]:
    """
    Mark a delegated task as COMPLETED by Antigravity and proactively notify Telegram.
    """
    tasks = _read_delegated_log()
    target = None
    for t in tasks:
        if t["task_id"].lower() == task_id.lower() or (task_id.lower() in ("latest", "last") and t == tasks[0]):
            target = t
            break

    if not target:
        return {"success": False, "message": f"Task {task_id} not found."}

    now_iso = datetime.now(timezone.utc).isoformat()
    target["status"] = "completed"
    target["completed_at"] = now_iso
    target["result_summary"] = result_summary
    if git_commit_hash:
        target["git_commit"] = git_commit_hash

    _save_delegated_log(tasks)

    # Update SQLite database
    conn = get_connection(DB_PATH)
    try:
        conn.execute(
            "UPDATE tasks SET status = 'completed', updated_at = ? WHERE id = ?",
            (now_iso, target["task_id"])
        )
        conn.commit()
    finally:
        conn.close()

    log_activity(
        "INFO",
        "BridgeEngine",
        f"Task {target['task_id']} completed by Antigravity",
        result_summary[:200]
    )

    telegram_res = None
    if notify_telegram:
        commit_info = f"\n📦 *Git Commit:* `{git_commit_hash}`" if git_commit_hash else ""
        msg_text = (
            f"🚀 *[TUGAS SELESAI] Antigravity x Jarvis*\n\n"
            f"📌 *Task ID:* `{target['task_id']}`\n"
            f"🎯 *Judul:* {target['title']}\n"
            f"🌿 *Branch:* `{target['git_branch']}`\n"
            f"👤 *Eksekutor:* Antigravity (Google AI Pro IDE){commit_info}\n\n"
            f"📝 *Hasil Pengerjaan:*\n{result_summary}\n\n"
            f"💡 *Token Telegram lu 100% aman (0 token terbuang untuk coding). Kode sudah rapi dan tersinkronisasi.* 🗿"
        )
        chat_id = target.get("origin_chat_id")
        thread_id = target.get("origin_thread_id")
        telegram_res = send_telegram_notification(msg_text, chat_id=chat_id, thread_id=thread_id)

    return {
        "success": True,
        "task_id": target["task_id"],
        "status": "completed",
        "completed_at": now_iso,
        "result_summary": result_summary,
        "telegram_notification": telegram_res
    }


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        cmd = sys.argv[1].lower()
        if cmd == "complete" and len(sys.argv) >= 4:
            tid = sys.argv[2]
            summary = sys.argv[3]
            commit = sys.argv[4] if len(sys.argv) > 4 else None
            res = complete_task(tid, summary, git_commit_hash=commit)
            print(json.dumps(res, indent=2))
        elif cmd == "notify" and len(sys.argv) >= 3:
            msg = sys.argv[2]
            target_chat = sys.argv[3] if len(sys.argv) > 3 else None
            target_thread = int(sys.argv[4]) if len(sys.argv) > 4 else None
            res = send_telegram_notification(msg, chat_id=target_chat, thread_id=target_thread)
            print(json.dumps(res, indent=2))
        elif cmd == "status":
            tid = sys.argv[2] if len(sys.argv) > 2 else "latest"
            print(json.dumps(get_task_status(tid), indent=2))
        elif cmd == "overview":
            print(json.dumps(get_system_overview(), indent=2))
        else:
            print("Usage: python -m harmage.bridge_engine [complete <task_id> <summary> [commit] | notify <msg> [chat] [thread] | status [task_id] | overview]")

