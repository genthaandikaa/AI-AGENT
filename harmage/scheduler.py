"""Persistent scheduling system for Harmage Virtual Enterprise.

Manages recurring operational heartbeats, cron intervals, standup sessions,
and publishing queues stored persistently in SQLite.
"""

import sqlite3
import uuid
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional
from harmage.db import get_connection, log_activity


DEFAULT_SCHEDULES = [
    {
        "id": "SCH-STANDUP-DAILY",
        "title": "Morning Operations Standup",
        "interval_type": "daily",
        "cron_expr": "0 8 * * *",
        "target_role": "executive_manager",
        "action": "convene_daily_standup",
        "enabled": 1,
    },
    {
        "id": "SCH-VIDEO-BATCH",
        "title": "Short-Form Video Production Pipeline",
        "interval_type": "daily",
        "cron_expr": "0 10 * * *",
        "target_role": "creator_pm",
        "action": "trigger_video_production_batch",
        "enabled": 1,
    },
    {
        "id": "SCH-QA-RENDER",
        "title": "Local FFmpeg QA & Subtitle Inspection",
        "interval_type": "daily",
        "cron_expr": "0 14 * * *",
        "target_role": "quality_assurance",
        "action": "verify_rendered_assets",
        "enabled": 1,
    },
    {
        "id": "SCH-AFFILIATE-SYNC",
        "title": "Affiliate Funnel & Link Health Sync",
        "interval_type": "daily",
        "cron_expr": "0 16 * * *",
        "target_role": "affiliate_lead",
        "action": "sync_partner_metrics",
        "enabled": 1,
    },
    {
        "id": "SCH-CEO-BRIEFING",
        "title": "Evening CEO Executive Briefing & $0 Budget Audit",
        "interval_type": "daily",
        "cron_expr": "0 20 * * *",
        "target_role": "executive_manager",
        "action": "compile_evening_executive_report",
        "enabled": 1,
    },
    {
        "id": "SCH-SECURITY-SCAN",
        "title": "Hourly Port & Secret Leak Watchdog",
        "interval_type": "hourly",
        "cron_expr": "0 * * * *",
        "target_role": "security_specialist",
        "action": "audit_ports_and_git_secrets",
        "enabled": 1,
    },
]


def seed_default_schedules() -> None:
    """Ensure default operational schedules exist in database."""
    conn = get_connection()
    now = datetime.now(timezone.utc)
    for s in DEFAULT_SCHEDULES:
        existing = conn.execute("SELECT id FROM schedules WHERE id = ?", (s["id"],)).fetchone()
        if not existing:
            # calculate initial next run (tomorrow or next hour)
            next_run = (now + timedelta(hours=1 if s["interval_type"] == "hourly" else 24)).isoformat()
            conn.execute(
                """
                INSERT INTO schedules (id, title, cron_expr, interval_type, target_role, action, next_run, last_run, enabled, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    s["id"],
                    s["title"],
                    s["cron_expr"],
                    s["interval_type"],
                    s["target_role"],
                    s["action"],
                    next_run,
                    None,
                    s["enabled"],
                    now.isoformat(),
                )
            )
    conn.commit()
    conn.close()


def get_all_schedules() -> List[Dict[str, Any]]:
    """Retrieve all schedules from SQLite."""
    seed_default_schedules()
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM schedules ORDER BY next_run ASC").fetchall()
    results = [dict(row) for row in rows]
    conn.close()
    return results


def add_schedule(title: str, interval_type: str, cron_expr: str, target_role: str, action: str, next_run_hours: int = 24) -> str:
    """Add a new custom persistent schedule."""
    schedule_id = f"SCH-{uuid.uuid4().hex[:8].upper()}"
    now = datetime.now(timezone.utc)
    next_run = (now + timedelta(hours=next_run_hours)).isoformat()
    conn = get_connection()
    conn.execute(
        """
        INSERT INTO schedules (id, title, cron_expr, interval_type, target_role, action, next_run, enabled, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, 1, ?)
        """,
        (schedule_id, title, cron_expr, interval_type, target_role, action, next_run, now.isoformat())
    )
    conn.commit()
    conn.close()
    log_activity("INFO", "scheduler", f"Created schedule '{title}'", f"Target: {target_role}, Next run: {next_run}")
    return schedule_id


def toggle_schedule(schedule_id: str, enabled: bool) -> bool:
    """Enable or disable a schedule."""
    conn = get_connection()
    conn.execute("UPDATE schedules SET enabled = ? WHERE id = ?", (1 if enabled else 0, schedule_id))
    conn.commit()
    conn.close()
    log_activity("INFO", "scheduler", f"Toggled schedule {schedule_id} to enabled={enabled}")
    return True


def trigger_heartbeat() -> Dict[str, Any]:
    """Execute operational heartbeat: check due schedules and record heartbeats."""
    seed_default_schedules()
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    now = datetime.now(timezone.utc)
    now_iso = now.isoformat()

    # Find due schedules
    due = conn.execute(
        "SELECT * FROM schedules WHERE enabled = 1 AND next_run <= ? ORDER BY next_run ASC",
        (now_iso,)
    ).fetchall()

    executed = []
    for item in due:
        s_id = item["id"]
        action = item["action"]
        interval = item["interval_type"]
        
        # Advance next run
        delta = timedelta(hours=1) if interval == "hourly" else timedelta(days=1)
        next_dt = now + delta
        
        conn.execute(
            "UPDATE schedules SET last_run = ?, next_run = ? WHERE id = ?",
            (now_iso, next_dt.isoformat(), s_id)
        )
        executed.append({
            "id": s_id,
            "title": item["title"],
            "action": action,
            "target_role": item["target_role"],
            "executed_at": now_iso
        })
        log_activity("INFO", item["target_role"], f"Heartbeat triggered: {item['title']}", f"Action executed: {action}")

    conn.commit()
    conn.close()
    return {
        "timestamp": now_iso,
        "due_count": len(due),
        "executed": executed
    }
