"""Harmage Backend <-> Hermes Native Kanban (:9119) Sync Bridge.

Provides bidirectional synchronization between:
1. Harmage Backend (FastAPI on port 9200, GET/POST /api/tasks)
2. Hermes Native Kanban Dashboard (port 9119, SQLite kanban.db)

Ensures that all autonomous agent tasks from Harmage appear seamlessly
on the Hermes Agent Kanban board in real time, preventing disparate state.
"""

from __future__ import annotations

import argparse
import datetime
import json
import logging
import os
import secrets
import signal
import sqlite3
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import urllib.request
import urllib.error

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [KanbanSyncBridge] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("KanbanSyncBridge")

# Status mapping tables
HARMAGE_TO_HERMES_STATUS = {
    "queued": "todo",
    "in_progress": "running",
    "completed": "done",
    "blocked": "blocked",
    "review": "review",
    "triage": "triage"
}

HERMES_TO_HARMAGE_STATUS = {
    "triage": "queued",
    "todo": "queued",
    "ready": "queued",
    "running": "in_progress",
    "blocked": "blocked",
    "review": "review",
    "done": "completed"
}

PRIORITY_MAP = {
    "critical": 3,
    "urgent": 3,
    "high": 2,
    "p1": 2,
    "medium": 1,
    "p2": 1,
    "normal": 1,
    "low": 0,
    "p3": 0
}


def get_default_kanban_db_path() -> Path:
    """Resolve the default Hermes kanban.db path."""
    env_override = os.environ.get("HERMES_KANBAN_DB")
    if env_override:
        return Path(env_override)
    local_app_data = os.environ.get("LOCALAPPDATA", "")
    if local_app_data:
        default_path = Path(local_app_data) / "hermes" / "kanban.db"
        if default_path.parent.exists():
            return default_path
    # Fallback to ~/.hermes/kanban.db
    return Path.home() / ".hermes" / "kanban.db"


class KanbanSyncBridge:
    def __init__(
        self,
        harmage_api_url: Optional[str] = None,
        kanban_db_path: Optional[Path] = None,
        sync_interval: int = 10,
        enable_reverse_sync: bool = True
    ):
        self.harmage_api_url = (harmage_api_url or os.environ.get("HARMAGE_API_URL", "http://127.0.0.1:9200")).rstrip("/")
        self.kanban_db_path = Path(kanban_db_path) if kanban_db_path else get_default_kanban_db_path()
        self.sync_interval = sync_interval
        self.enable_reverse_sync = enable_reverse_sync
        self.running = True

        logger.info(f"Initialized KanbanSyncBridge:")
        logger.info(f" - Harmage API: {self.harmage_api_url}")
        logger.info(f" - Kanban DB:   {self.kanban_db_path}")
        logger.info(f" - Interval:    {self.sync_interval}s")

    def _get_kanban_connection(self) -> sqlite3.Connection:
        """Establish connection to SQLite kanban.db with WAL mode."""
        self.kanban_db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(self.kanban_db_path), timeout=10.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        return conn

    def fetch_harmage_tasks(self) -> List[Dict[str, Any]]:
        """Fetch all tasks from Harmage FastAPI backend with SQLite fallback."""
        url = f"{self.harmage_api_url}/api/tasks"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "HarmageKanbanSyncBridge/1.0"})
            with urllib.request.urlopen(req, timeout=5.0) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode("utf-8"))
                    return data
        except Exception as e:
            logger.warning(f"HTTP fetch to {url} failed ({e}), checking SQLite fallback...")

        # Fallback to direct DB read
        db_file = Path("harmage") / "data" / "harmage_operations.db"
        if db_file.exists():
            try:
                conn = sqlite3.connect(str(db_file))
                conn.row_factory = sqlite3.Row
                rows = conn.execute("SELECT * FROM tasks").fetchall()
                tasks = []
                for r in rows:
                    tasks.append({
                        "id": r["id"],
                        "title": r["title"],
                        "description": r["description"],
                        "assignee": r["assignee"],
                        "status": r["status"],
                        "priority": r["priority"],
                        "created_at": r["created_at"],
                        "updated_at": r["updated_at"]
                    })
                conn.close()
                return tasks
            except Exception as dbe:
                logger.error(f"Fallback SQLite read failed: {dbe}")

        return []

    def update_harmage_task_status(self, task_id: str, new_status: str, evidence: str = "Updated via Hermes Kanban") -> bool:
        """Push status update back to Harmage backend."""
        url = f"{self.harmage_api_url}/api/tasks/{task_id}/status"
        payload = json.dumps({
            "status": new_status,
            "evidence": evidence
        }).encode("utf-8")
        try:
            req = urllib.request.Request(
                url,
                data=payload,
                headers={"Content-Type": "application/json", "User-Agent": "HarmageKanbanSyncBridge/1.0"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=5.0) as resp:
                return resp.status == 200
        except Exception as e:
            logger.error(f"Failed to push status to Harmage for {task_id}: {e}")
            return False

    def sync_once(self) -> Dict[str, int]:
        """Perform a single bidirectional sync pass."""
        stats = {
            "harmage_total": 0,
            "created_in_kanban": 0,
            "updated_in_kanban": 0,
            "deleted_in_kanban": 0,
            "pushed_to_harmage": 0
        }

        harmage_tasks = self.fetch_harmage_tasks()
        stats["harmage_total"] = len(harmage_tasks)

        now_ts = int(time.time())
        conn = self._get_kanban_connection()

        try:
            # 1. Forward Sync: Harmage -> Hermes Kanban
            existing_kanban_tasks = {}
            for row in conn.execute("SELECT id, idempotency_key, status, title, body, assignee, priority FROM tasks WHERE tenant = 'harmage'").fetchall():
                key = row["idempotency_key"]
                if key:
                    existing_kanban_tasks[key] = dict(row)

            # Prune tasks that no longer exist in Harmage
            harmage_task_ids = {t["id"] for t in harmage_tasks if t.get("id")}
            for k_key, k_val in existing_kanban_tasks.items():
                if k_key not in harmage_task_ids:
                    conn.execute("DELETE FROM tasks WHERE id = ?", (k_val["id"],))
                    conn.execute("DELETE FROM task_events WHERE task_id = ?", (k_val["id"],))
                    conn.execute("DELETE FROM task_comments WHERE task_id = ?", (k_val["id"],))
                    conn.execute("DELETE FROM task_runs WHERE task_id = ?", (k_val["id"],))
                    stats["deleted_in_kanban"] += 1

            for h_task in harmage_tasks:
                task_id = h_task.get("id")
                if not task_id:
                    continue

                title = h_task.get("title") or f"Task {task_id}"
                desc = h_task.get("description") or ""
                assignee = h_task.get("assignee") or "agent"
                raw_status = (h_task.get("status") or "queued").lower()
                target_status = HARMAGE_TO_HERMES_STATUS.get(raw_status, "todo")

                raw_pri = str(h_task.get("priority") or "medium").lower()
                priority_int = PRIORITY_MAP.get(raw_pri, 1)

                body = f"{desc}\n\n---\n**Harmage ID:** `{task_id}` | **Priority:** `{raw_pri.upper()}` | **Source:** Harmage Autonomous Backend"

                if task_id not in existing_kanban_tasks:
                    # Create new card in Hermes Kanban
                    new_id = f"t_{secrets.token_hex(4)}"
                    conn.execute("""
                        INSERT INTO tasks (
                            id, title, body, assignee, status, priority,
                            created_by, created_at, started_at, completed_at,
                            workspace_kind, tenant, idempotency_key, consecutive_failures,
                            goal_mode, block_recurrences
                        ) VALUES (
                            ?, ?, ?, ?, ?, ?,
                            ?, ?, ?, ?,
                            'scratch', 'harmage', ?, 0,
                            0, 0
                        )
                    """, (
                        new_id,
                        title,
                        body,
                        assignee,
                        target_status,
                        priority_int,
                        "harmage_bridge",
                        now_ts,
                        now_ts if target_status == "running" else None,
                        now_ts if target_status == "done" else None,
                        task_id
                    ))

                    # Record event
                    conn.execute("""
                        INSERT INTO task_events (task_id, kind, payload, created_at)
                        VALUES (?, 'created', ?, ?)
                    """, (new_id, json.dumps({"source": "harmage_sync", "harmage_id": task_id}), now_ts))

                    stats["created_in_kanban"] += 1
                else:
                    # Check for updates
                    k_task = existing_kanban_tasks[task_id]
                    k_id = k_task["id"]
                    k_status = k_task["status"]

                    needs_update = False
                    fields_to_update = []
                    params = []

                    # If Harmage status changed
                    if k_status != target_status:
                        fields_to_update.append("status = ?")
                        params.append(target_status)
                        if target_status == "done":
                            fields_to_update.append("completed_at = ?")
                            params.append(now_ts)
                        elif target_status == "running":
                            fields_to_update.append("started_at = COALESCE(started_at, ?)")
                            params.append(now_ts)
                        needs_update = True

                    if k_task["title"] != title:
                        fields_to_update.append("title = ?")
                        params.append(title)
                        needs_update = True

                    if k_task["assignee"] != assignee:
                        fields_to_update.append("assignee = ?")
                        params.append(assignee)
                        needs_update = True

                    if needs_update:
                        params.append(k_id)
                        conn.execute(f"UPDATE tasks SET {', '.join(fields_to_update)} WHERE id = ?", params)

                        conn.execute("""
                            INSERT INTO task_events (task_id, kind, payload, created_at)
                            VALUES (?, 'status_sync', ?, ?)
                        """, (k_id, json.dumps({"harmage_status": raw_status, "kanban_status": target_status}), now_ts))

                        stats["updated_in_kanban"] += 1

            # 2. Reverse Sync: Hermes Kanban manual edits -> Harmage
            if self.enable_reverse_sync:
                harmage_task_map = {t["id"]: t for t in harmage_tasks}
                for row in conn.execute("SELECT id, idempotency_key, status FROM tasks WHERE tenant = 'harmage'").fetchall():
                    tid = row["idempotency_key"]
                    k_stat = row["status"]
                    if tid in harmage_task_map:
                        h_task = harmage_task_map[tid]
                        h_stat = h_task.get("status", "queued").lower()
                        mapped_h_stat = HERMES_TO_HARMAGE_STATUS.get(k_stat)
                        if mapped_h_stat and mapped_h_stat != h_stat:
                            # Avoid feedback loop if already matching semantic phase
                            if not (h_stat == "in_progress" and mapped_h_stat == "queued"):
                                ok = self.update_harmage_task_status(
                                    tid,
                                    mapped_h_stat,
                                    evidence=f"Hermes Kanban user moved card to {k_stat}"
                                )
                                if ok:
                                    stats["pushed_to_harmage"] += 1

            conn.commit()
        finally:
            conn.close()

        return stats

    def run_daemon(self):
        """Run continuous sync loop."""
        logger.info("Starting KanbanSyncBridge background daemon...")

        def _handle_signal(sig, frame):
            logger.info("Received termination signal, shutting down gracefully...")
            self.running = False

        signal.signal(signal.SIGINT, _handle_signal)
        signal.signal(signal.SIGTERM, _handle_signal)

        while self.running:
            try:
                stats = self.sync_once()
                if stats["created_in_kanban"] > 0 or stats["updated_in_kanban"] > 0 or stats["pushed_to_harmage"] > 0:
                    logger.info(
                        f"Sync pass completed: "
                        f"Harmage={stats['harmage_total']} | "
                        f"Created={stats['created_in_kanban']} | "
                        f"Updated={stats['updated_in_kanban']} | "
                        f"PushedBack={stats['pushed_to_harmage']}"
                    )
            except Exception as e:
                logger.error(f"Error during sync pass: {e}", exc_info=True)

            # Sleep in increments for prompt shutdown
            for _ in range(self.sync_interval):
                if not self.running:
                    break
                time.sleep(1.0)

        logger.info("KanbanSyncBridge daemon stopped cleanly.")


def main():
    parser = argparse.ArgumentParser(description="Harmage <-> Hermes Kanban Sync Bridge")
    parser.add_argument("--once", action="store_true", help="Run a single sync pass and exit")
    parser.add_argument("--interval", type=int, default=10, help="Sync loop interval in seconds (default: 10)")
    parser.add_argument("--harmage-url", type=str, default="http://127.0.0.1:9200", help="Harmage API URL")
    parser.add_argument("--kanban-db", type=str, default=None, help="Hermes kanban.db path")
    parser.add_argument("--no-reverse", action="store_true", help="Disable reverse sync from Hermes to Harmage")

    args = parser.parse_args()

    bridge = KanbanSyncBridge(
        harmage_api_url=args.harmage_url,
        kanban_db_path=Path(args.kanban_db) if args.kanban_db else None,
        sync_interval=args.interval,
        enable_reverse_sync=not args.no_reverse
    )

    if args.once:
        stats = bridge.sync_once()
        print(json.dumps(stats, indent=2))
        sys.exit(0)
    else:
        bridge.run_daemon()


if __name__ == "__main__":
    main()
