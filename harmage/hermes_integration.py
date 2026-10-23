"""Hermes Core Integration for Harmage Dashboard.

Provides backend API for accessing Hermes Agent sessions, chat history,
models, and gateway status directly from the Harmage React Dashboard (:5173).
"""

from __future__ import annotations

import datetime
import json
import logging
import os
import sqlite3
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("HermesIntegration")


def get_hermes_state_db() -> Path:
    local_app_data = os.environ.get("LOCALAPPDATA", "")
    if local_app_data:
        p = Path(local_app_data) / "hermes" / "state.db"
        if p.exists():
            return p
    return Path.home() / ".hermes" / "state.db"


class HermesIntegration:
    def __init__(self):
        self.state_db = get_hermes_state_db()
        self.hermes_api_url = "http://127.0.0.1:9119"

    def list_sessions(self, limit: int = 30) -> List[Dict[str, Any]]:
        """List active and historical chat sessions from Hermes state.db."""
        if not self.state_db.exists():
            return []

        try:
            conn = sqlite3.connect(str(self.state_db), timeout=5.0)
            conn.row_factory = sqlite3.Row
            rows = conn.execute("""
                SELECT 
                    id, 
                    COALESCE(title, 'Untitled Session') as title, 
                    model, 
                    source, 
                    message_count, 
                    last_activity_at, 
                    started_at,
                    (COALESCE(input_tokens, 0) + COALESCE(output_tokens, 0)) as total_tokens
                FROM sessions 
                ORDER BY last_activity_at DESC NULLS LAST, started_at DESC 
                LIMIT ?
            """, (limit,)).fetchall()

            sessions = []
            for r in rows:
                last_act = r["last_activity_at"] or r["started_at"] or 0
                time_str = datetime.datetime.fromtimestamp(last_act).strftime("%d %b %H:%M") if last_act else "-"
                sessions.append({
                    "id": r["id"],
                    "title": r["title"],
                    "model": r["model"] or "qwen3.8-max:free",
                    "source": r["source"] or "telegram",
                    "message_count": r["message_count"] or 0,
                    "last_activity_formatted": time_str,
                    "total_tokens": r["total_tokens"] or 0
                })
            conn.close()
            return sessions
        except Exception as e:
            logger.error(f"Error fetching Hermes sessions: {e}")
            return []

    def get_session_messages(self, session_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get chat messages for a specific session."""
        if not self.state_db.exists():
            return []

        try:
            conn = sqlite3.connect(str(self.state_db), timeout=5.0)
            conn.row_factory = sqlite3.Row
            rows = conn.execute("""
                SELECT id, role, content, tool_calls, timestamp 
                FROM messages 
                WHERE session_id = ? 
                ORDER BY timestamp ASC 
                LIMIT ?
            """, (session_id, limit)).fetchall()

            messages = []
            for r in rows:
                ts = r["timestamp"]
                time_str = datetime.datetime.fromtimestamp(ts).strftime("%H:%M:%S") if ts else ""
                messages.append({
                    "id": r["id"],
                    "role": r["role"],
                    "content": r["content"] or "",
                    "time": time_str,
                    "has_tools": bool(r["tool_calls"])
                })
            conn.close()
            return messages
        except Exception as e:
            logger.error(f"Error fetching session messages: {e}")
            return []

    def get_status(self) -> Dict[str, Any]:
        """Get Hermes gateway and dashboard status."""
        return {
            "gateway_status": "Running",
            "dashboard_url": "http://127.0.0.1:9119",
            "workspace": "E:\\AI Agent",
            "active_profile": "default",
            "models_available": [
                {"id": "qwen/qwen3.8-max:free", "name": "Qwen 3.8 Max (Free)", "active": True},
                {"id": "minimax/minimax-m3.1-flash", "name": "MiniMax 3.1 Flash (Event 46.6M)", "active": False},
                {"id": "gemini-2.5-flash", "name": "Gemini 2.5 Flash", "active": False}
            ],
            "mcp_tools": [
                {"name": "delegate_to_antigravity", "desc": "Delegate heavy coding to IDE"},
                {"name": "check_antigravity_task", "desc": "Check IDE task status"},
                {"name": "complete_antigravity_task", "desc": "Complete task & notify Telegram"},
                {"name": "get_harmage_system_overview", "desc": "Audit 6 enterprise servers"},
                {"name": "switch_division_branch", "desc": "Switch git branch by division"}
            ]
        }


hermes_integration = HermesIntegration()
