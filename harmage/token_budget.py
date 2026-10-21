"""Shared AI Token Budget Manager (Qwen + Gemini) for Harmage Agents.

Enforces a strict 2,000,000 token combined daily ceiling resetting at midnight
Asia/Jakarta (WIB, UTC+7), with atomic pre-call reservations, post-call reconciliation,
and 4 adaptive work modes (Normal, Efficient, Conservation, Ceiling Reached).
"""

import json
import uuid
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from zoneinfo import ZoneInfo
from pathlib import Path

from harmage.db import get_connection, log_activity

JAKARTA_TZ = ZoneInfo("Asia/Jakarta")
DEFAULT_DAILY_LIMIT = 2_000_000
DEFAULT_SOFT_LIMIT = 1_600_000       # 80%
DEFAULT_CONSERVATION_LIMIT = 1_800_000 # 90%
DEFAULT_SAFETY_RESERVE = 50_000      # 1.95M hard admission stop

MODE_NORMAL = "NORMAL"
MODE_EFFICIENT = "EFFICIENT"
MODE_CONSERVATION = "CONSERVATION"
MODE_CEILING_REACHED = "CEILING_REACHED"


class TokenBudgetManager:
    """Thread-safe central token ledger and admission controller."""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path
        self._lock = threading.Lock()

    def get_jakarta_now(self) -> datetime:
        """Get current timestamp in Asia/Jakarta timezone."""
        return datetime.now(JAKARTA_TZ)

    def get_window_boundaries(self, dt: Optional[datetime] = None) -> Tuple[str, datetime, datetime]:
        """Compute the window date_str, start, and end (midnight to midnight WIB)."""
        ref = dt.astimezone(JAKARTA_TZ) if dt else self.get_jakarta_now()
        start = ref.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1) - timedelta(microseconds=1)
        date_str = start.strftime("%Y-%m-%d")
        return date_str, start, end

    def get_or_create_active_window(self, conn=None) -> Dict[str, Any]:
        """Fetch or initialize the current day's token accounting window."""
        date_str, start_dt, end_dt = self.get_window_boundaries()
        window_id = f"WINDOW_{date_str}_WIB"
        close_conn = False

        if conn is None:
            conn = get_connection(self.db_path)
            close_conn = True

        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT window_id, date_str, timezone, window_start, window_end, daily_limit, soft_limit, "
                "conservation_limit, safety_reserve, confirmed_tokens, estimated_tokens, reserved_tokens, "
                "qwen_tokens, gemini_tokens, other_tokens, mode, created_at, updated_at "
                "FROM token_budget_windows WHERE window_id = ?",
                (window_id,)
            )
            row = cursor.fetchone()

            if not row:
                now_iso = self.get_jakarta_now().isoformat()
                cursor.execute(
                    """
                    INSERT INTO token_budget_windows (
                        window_id, date_str, timezone, window_start, window_end,
                        daily_limit, soft_limit, conservation_limit, safety_reserve,
                        confirmed_tokens, estimated_tokens, reserved_tokens,
                        qwen_tokens, gemini_tokens, other_tokens, mode,
                        created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 0, 0, 0, 0, 0, ?, ?, ?)
                    """,
                    (
                        window_id,
                        date_str,
                        "Asia/Jakarta",
                        start_dt.isoformat(),
                        end_dt.isoformat(),
                        DEFAULT_DAILY_LIMIT,
                        DEFAULT_SOFT_LIMIT,
                        DEFAULT_CONSERVATION_LIMIT,
                        DEFAULT_SAFETY_RESERVE,
                        MODE_NORMAL,
                        now_iso,
                        now_iso
                    )
                )
                conn.commit()
                # Check for deferred work to resume in new window
                self._resume_deferred_tasks(conn)

                return {
                    "window_id": window_id,
                    "date_str": date_str,
                    "timezone": "Asia/Jakarta",
                    "window_start": start_dt.isoformat(),
                    "window_end": end_dt.isoformat(),
                    "daily_limit": DEFAULT_DAILY_LIMIT,
                    "soft_limit": DEFAULT_SOFT_LIMIT,
                    "conservation_limit": DEFAULT_CONSERVATION_LIMIT,
                    "safety_reserve": DEFAULT_SAFETY_RESERVE,
                    "confirmed_tokens": 0,
                    "estimated_tokens": 0,
                    "reserved_tokens": 0,
                    "qwen_tokens": 0,
                    "gemini_tokens": 0,
                    "other_tokens": 0,
                    "mode": MODE_NORMAL,
                    "created_at": now_iso,
                    "updated_at": now_iso,
                }

            return {
                "window_id": row[0],
                "date_str": row[1],
                "timezone": row[2],
                "window_start": row[3],
                "window_end": row[4],
                "daily_limit": row[5],
                "soft_limit": row[6],
                "conservation_limit": row[7],
                "safety_reserve": row[8],
                "confirmed_tokens": row[9],
                "estimated_tokens": row[10],
                "reserved_tokens": row[11],
                "qwen_tokens": row[12],
                "gemini_tokens": row[13],
                "other_tokens": row[14],
                "mode": row[15],
                "created_at": row[16],
                "updated_at": row[17],
            }
        finally:
            if close_conn:
                conn.close()

    def determine_mode(self, total_committed: int, daily_limit: int, soft_limit: int,
                       conservation_limit: int, safety_reserve: int) -> str:
        """Determine adaptive work mode based on consumed and reserved tokens."""
        effective_stop = max(0, daily_limit - safety_reserve)
        if total_committed >= effective_stop:
            return MODE_CEILING_REACHED
        if total_committed >= conservation_limit:
            return MODE_CONSERVATION
        if total_committed >= soft_limit:
            return MODE_EFFICIENT
        return MODE_NORMAL

    def reserve_tokens(
        self,
        estimated_tokens: int = 400,
        agent_id: str = "unknown",
        priority: str = "medium",
        call_type: str = "chat",
        task_id: Optional[str] = None,
        title: Optional[str] = None
    ) -> Tuple[bool, str, Optional[str], str]:
        """
        Atomically reserve token allowance before calling LLM.
        
        Returns:
            (allowed: bool, reason: str, reservation_id: Optional[str], mode: str)
        """
        with self._lock:
            conn = get_connection(self.db_path)
            try:
                window = self.get_or_create_active_window(conn)
                daily_limit = window["daily_limit"]
                soft_limit = window["soft_limit"]
                cons_limit = window["conservation_limit"]
                safety_reserve = window["safety_reserve"]
                
                # Active in-flight + confirmed + estimated
                total_current = window["confirmed_tokens"] + window["estimated_tokens"] + window["reserved_tokens"]
                current_mode = self.determine_mode(total_current, daily_limit, soft_limit, cons_limit, safety_reserve)

                # Check Hard Ceiling
                if current_mode == MODE_CEILING_REACHED and priority != "critical_ceo":
                    defer_id = f"DEF-{uuid.uuid4().hex[:8]}"
                    reason = f"Combined daily ceiling reached ({total_current:,}/{daily_limit:,} tokens in Asia/Jakarta). Deferred to preserve office stability."
                    conn.execute(
                        """
                        INSERT INTO token_deferred_queue (
                            id, task_id, agent_id, title, call_type, payload_preview, priority, deferral_reason, status, created_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'deferred', ?)
                        """,
                        (
                            defer_id,
                            task_id,
                            agent_id,
                            title or f"Inference for {agent_id} ({call_type})",
                            call_type,
                            f"Estimated {estimated_tokens} tokens",
                            priority,
                            reason,
                            self.get_jakarta_now().isoformat()
                        )
                    )
                    conn.commit()
                    log_activity("WARN", "TokenBudgetManager", f"Call refused for {agent_id} [{call_type}]: Ceiling reached", reason)
                    return False, reason, None, MODE_CEILING_REACHED

                # Check Conservation Mode for routine chatter
                if current_mode == MODE_CONSERVATION and priority in ("low", "routine_chatter"):
                    defer_id = f"DEF-{uuid.uuid4().hex[:8]}"
                    reason = "Conservation mode active (>=90% budget): non-essential AI chatter deferred."
                    conn.execute(
                        """
                        INSERT INTO token_deferred_queue (
                            id, task_id, agent_id, title, call_type, payload_preview, priority, deferral_reason, status, created_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'deferred', ?)
                        """,
                        (
                            defer_id,
                            task_id,
                            agent_id,
                            title or f"Routine chatter for {agent_id}",
                            call_type,
                            f"Estimated {estimated_tokens} tokens",
                            priority,
                            reason,
                            self.get_jakarta_now().isoformat()
                        )
                    )
                    conn.commit()
                    log_activity("INFO", "TokenBudgetManager", f"Chatter deferred for {agent_id}: Conservation mode", reason)
                    return False, reason, None, MODE_CONSERVATION

                # Check if this specific reservation pushes over safety reserve or hard limit
                effective_limit = max(0, daily_limit - safety_reserve) if priority != "critical_ceo" else daily_limit
                if (total_current + estimated_tokens) > effective_limit and priority != "critical_ceo":
                    defer_id = f"DEF-{uuid.uuid4().hex[:8]}"
                    reason = f"Reservation of {estimated_tokens} tokens would breach safety threshold ({effective_limit:,}/{daily_limit:,} tokens)."
                    conn.execute(
                        """
                        INSERT INTO token_deferred_queue (
                            id, task_id, agent_id, title, call_type, payload_preview, priority, deferral_reason, status, created_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'deferred', ?)
                        """,
                        (
                            defer_id,
                            task_id,
                            agent_id,
                            title or f"Inference for {agent_id}",
                            call_type,
                            f"Estimated {estimated_tokens} tokens",
                            priority,
                            reason,
                            self.get_jakarta_now().isoformat()
                        )
                    )
                    conn.commit()
                    return False, reason, None, MODE_CEILING_REACHED

                # Reservation Approved
                res_id = f"RES-{uuid.uuid4().hex[:10]}"
                now_dt = self.get_jakarta_now()
                expires_dt = now_dt + timedelta(minutes=5)

                conn.execute(
                    """
                    INSERT INTO token_reservations (
                        reservation_id, window_id, agent_id, priority, estimated_tokens, status, created_at, expires_at
                    ) VALUES (?, ?, ?, ?, ?, 'RESERVED', ?, ?)
                    """,
                    (res_id, window["window_id"], agent_id, priority, estimated_tokens, now_dt.isoformat(), expires_dt.isoformat())
                )

                new_reserved = window["reserved_tokens"] + estimated_tokens
                new_mode = self.determine_mode(
                    window["confirmed_tokens"] + window["estimated_tokens"] + new_reserved,
                    daily_limit, soft_limit, cons_limit, safety_reserve
                )

                conn.execute(
                    "UPDATE token_budget_windows SET reserved_tokens = ?, mode = ?, updated_at = ? WHERE window_id = ?",
                    (new_reserved, new_mode, now_dt.isoformat(), window["window_id"])
                )
                conn.commit()

                return True, "Reservation granted", res_id, new_mode
            finally:
                conn.close()

    def reconcile_usage(
        self,
        reservation_id: Optional[str],
        actual_prompt: Optional[int] = None,
        actual_completion: Optional[int] = None,
        actual_total: Optional[int] = None,
        provider: str = "qwen",
        model: str = "qwen3.8-max",
        agent_id: str = "unknown",
        division: Optional[str] = None,
        task_id: Optional[str] = None,
        call_type: str = "chat",
        fallback_char_count: int = 0
    ) -> Dict[str, Any]:
        """
        Reconcile reservation against exact provider usage metadata.
        Falls back to conservative estimation if provider metadata is missing.
        """
        with self._lock:
            conn = get_connection(self.db_path)
            try:
                window = self.get_or_create_active_window(conn)
                now_iso = self.get_jakarta_now().isoformat()

                # 1. Determine reserved tokens to release
                reserved_to_deduct = 0
                if reservation_id:
                    cursor = conn.cursor()
                    cursor.execute("SELECT estimated_tokens, status FROM token_reservations WHERE reservation_id = ?", (reservation_id,))
                    row = cursor.fetchone()
                    if row and row[1] == "RESERVED":
                        reserved_to_deduct = row[0]
                        conn.execute("UPDATE token_reservations SET status = 'RECONCILED' WHERE reservation_id = ?", (reservation_id,))

                # 2. Determine actual or conservative tokens
                is_estimated = 0
                confidence = "confirmed"
                if actual_total is not None and actual_total > 0:
                    total_tokens = actual_total
                    p_tokens = actual_prompt or int(total_tokens * 0.7)
                    c_tokens = actual_completion or (total_tokens - p_tokens)
                elif actual_prompt is not None and actual_completion is not None:
                    p_tokens = actual_prompt
                    c_tokens = actual_completion
                    total_tokens = p_tokens + c_tokens
                else:
                    # Conservative estimate: ~3.5 chars per token + safety margin
                    is_estimated = 1
                    confidence = "estimated_conservative"
                    chars = max(100, fallback_char_count)
                    total_tokens = int(chars / 3.2) + 20
                    p_tokens = int(total_tokens * 0.6)
                    c_tokens = total_tokens - p_tokens
                    log_activity("WARN", "TokenBudgetManager", "Missing provider usage data", f"Using conservative estimate: {total_tokens} tokens")

                # 3. Log Token Usage Event
                event_id = f"EVT-{uuid.uuid4().hex[:10]}"
                conn.execute(
                    """
                    INSERT INTO token_usage_events (
                        id, window_id, provider, model, agent_id, division, task_id,
                        call_type, prompt_tokens, completion_tokens, total_tokens,
                        is_estimated, confidence, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        event_id,
                        window["window_id"],
                        provider.lower(),
                        model,
                        agent_id,
                        division,
                        task_id,
                        call_type,
                        p_tokens,
                        c_tokens,
                        total_tokens,
                        is_estimated,
                        confidence,
                        now_iso
                    )
                )

                # 4. Update Window Totals
                new_reserved = max(0, window["reserved_tokens"] - reserved_to_deduct)
                new_confirmed = window["confirmed_tokens"] + (total_tokens if not is_estimated else 0)
                new_estimated = window["estimated_tokens"] + (total_tokens if is_estimated else 0)

                qwen_add = total_tokens if "qwen" in provider.lower() else 0
                gemini_add = total_tokens if "gemini" in provider.lower() else 0
                other_add = total_tokens if (qwen_add == 0 and gemini_add == 0) else 0

                new_qwen = window["qwen_tokens"] + qwen_add
                new_gemini = window["gemini_tokens"] + gemini_add
                new_other = window["other_tokens"] + other_add

                total_committed = new_confirmed + new_estimated + new_reserved
                new_mode = self.determine_mode(
                    total_committed,
                    window["daily_limit"],
                    window["soft_limit"],
                    window["conservation_limit"],
                    window["safety_reserve"]
                )

                conn.execute(
                    """
                    UPDATE token_budget_windows SET
                        confirmed_tokens = ?,
                        estimated_tokens = ?,
                        reserved_tokens = ?,
                        qwen_tokens = ?,
                        gemini_tokens = ?,
                        other_tokens = ?,
                        mode = ?,
                        updated_at = ?
                    WHERE window_id = ?
                    """,
                    (
                        new_confirmed,
                        new_estimated,
                        new_reserved,
                        new_qwen,
                        new_gemini,
                        new_other,
                        new_mode,
                        now_iso,
                        window["window_id"]
                    )
                )
                conn.commit()

                return {
                    "event_id": event_id,
                    "provider": provider,
                    "model": model,
                    "total_tokens": total_tokens,
                    "mode": new_mode,
                    "confirmed_tokens": new_confirmed,
                    "reserved_tokens": new_reserved
                }
            finally:
                conn.close()

    def _resume_deferred_tasks(self, conn) -> int:
        """Mark deferred items as resumed when a new day's budget window opens."""
        cursor = conn.cursor()
        cursor.execute("UPDATE token_deferred_queue SET status = 'resumed' WHERE status = 'deferred'")
        resumed_count = cursor.rowcount
        if resumed_count > 0:
            log_activity("INFO", "TokenBudgetManager", "Daily window reset", f"Resumed {resumed_count} deferred tasks for Asia/Jakarta midnight reset.")
        return resumed_count

    def get_status_summary(self) -> Dict[str, Any]:
        """Produce real-time metrics for UI dashboard and API consumption."""
        conn = get_connection(self.db_path)
        try:
            window = self.get_or_create_active_window(conn)
            daily_limit = window["daily_limit"]
            confirmed = window["confirmed_tokens"]
            estimated = window["estimated_tokens"]
            reserved = window["reserved_tokens"]
            total_used = confirmed + estimated + reserved
            remaining = max(0, daily_limit - total_used)
            pct_used = round((total_used / daily_limit) * 100, 2) if daily_limit > 0 else 0.0

            # Next reset time in Asia/Jakarta
            now_wib = self.get_jakarta_now()
            next_midnight = (now_wib + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            seconds_until_reset = max(0, int((next_midnight - now_wib).total_seconds()))
            hours = seconds_until_reset // 3600
            minutes = (seconds_until_reset % 3600) // 60

            # Deferred count
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM token_deferred_queue WHERE status = 'deferred'")
            deferred_count = cursor.fetchone()[0]

            # Top Agent Usage
            cursor.execute(
                """
                SELECT agent_id, SUM(total_tokens) as agent_total
                FROM token_usage_events
                WHERE window_id = ?
                GROUP BY agent_id
                ORDER BY agent_total DESC
                LIMIT 6
                """,
                (window["window_id"],)
            )
            agent_breakdown = [{"agent_id": row[0], "tokens": row[1]} for row in cursor.fetchall()]

            # Active Alerts
            alerts = []
            if window["mode"] == MODE_EFFICIENT:
                alerts.append(f"Soft limit reached ({window['soft_limit']:,} tokens): compact prompts & rule routing enabled.")
            elif window["mode"] == MODE_CONSERVATION:
                alerts.append(f"Conservation mode active ({window['conservation_limit']:,} tokens): bounding outputs & deferring low-priority chatter.")
            elif window["mode"] == MODE_CEILING_REACHED:
                alerts.append("Hard daily inference ceiling reached (2M tokens): non-critical AI calls deferred. Office 3D & local operations active.")

            if estimated > 0:
                alerts.append(f"Notice: {estimated:,} tokens estimated due to missing provider usage metadata.")

            return {
                "window_id": window["window_id"],
                "date_str": window["date_str"],
                "timezone": "Asia/Jakarta",
                "daily_limit": daily_limit,
                "soft_limit": window["soft_limit"],
                "conservation_limit": window["conservation_limit"],
                "safety_reserve": window["safety_reserve"],
                "confirmed_tokens": confirmed,
                "estimated_tokens": estimated,
                "reserved_tokens": reserved,
                "total_consumed": total_used,
                "remaining_tokens": remaining,
                "percent_used": pct_used,
                "mode": window["mode"],
                "provider_breakdown": {
                    "qwen": window["qwen_tokens"],
                    "gemini": window["gemini_tokens"],
                    "other": window["other_tokens"]
                },
                "agent_breakdown": agent_breakdown,
                "deferred_queue_count": deferred_count,
                "next_reset_iso": next_midnight.isoformat(),
                "seconds_until_reset": seconds_until_reset,
                "countdown_display": f"{hours}h {minutes}m",
                "alerts": alerts
            }
        finally:
            conn.close()

    def update_config(self, soft_limit: Optional[int] = None, conservation_limit: Optional[int] = None,
                      safety_reserve: Optional[int] = None, daily_limit: Optional[int] = None) -> Dict[str, Any]:
        """Update configurable thresholds for the active window."""
        with self._lock:
            conn = get_connection(self.db_path)
            try:
                window = self.get_or_create_active_window(conn)
                new_daily = daily_limit or window["daily_limit"]
                new_soft = soft_limit or window["soft_limit"]
                new_cons = conservation_limit or window["conservation_limit"]
                new_reserve = safety_reserve or window["safety_reserve"]

                total_current = window["confirmed_tokens"] + window["estimated_tokens"] + window["reserved_tokens"]
                new_mode = self.determine_mode(total_current, new_daily, new_soft, new_cons, new_reserve)

                conn.execute(
                    """
                    UPDATE token_budget_windows SET
                        daily_limit = ?,
                        soft_limit = ?,
                        conservation_limit = ?,
                        safety_reserve = ?,
                        mode = ?,
                        updated_at = ?
                    WHERE window_id = ?
                    """,
                    (new_daily, new_soft, new_cons, new_reserve, new_mode, self.get_jakarta_now().isoformat(), window["window_id"])
                )
                conn.commit()
                log_activity("INFO", "TokenBudgetManager", "Budget configuration updated", f"Daily: {new_daily}, Soft: {new_soft}, Cons: {new_cons}")
                return self.get_status_summary()
            finally:
                conn.close()

    def simulate_token_consumption(self, provider: str, tokens: int, agent_id: str = "simulator") -> Dict[str, Any]:
        """Safe test method to simulate token usage without burning real provider quota."""
        allowed, reason, res_id, mode = self.reserve_tokens(
            estimated_tokens=tokens,
            agent_id=agent_id,
            priority="medium",
            call_type="test_simulation"
        )
        if not allowed:
            return {"allowed": False, "reason": reason, "mode": mode}
        
        reconciliation = self.reconcile_usage(
            reservation_id=res_id,
            actual_total=tokens,
            provider=provider,
            model=f"{provider}-simulated",
            agent_id=agent_id,
            call_type="test_simulation"
        )
        return {"allowed": True, "reconciliation": reconciliation, "mode": reconciliation["mode"]}

    def reset_active_window(self) -> Dict[str, Any]:
        """Administrative reset for test harnesses or explicit owner override."""
        with self._lock:
            conn = get_connection(self.db_path)
            try:
                window = self.get_or_create_active_window(conn)
                now_iso = self.get_jakarta_now().isoformat()
                conn.execute(
                    """
                    UPDATE token_budget_windows SET
                        daily_limit = ?,
                        soft_limit = ?,
                        conservation_limit = ?,
                        safety_reserve = ?,
                        confirmed_tokens = 0,
                        estimated_tokens = 0,
                        reserved_tokens = 0,
                        qwen_tokens = 0,
                        gemini_tokens = 0,
                        other_tokens = 0,
                        mode = 'NORMAL',
                        updated_at = ?
                    WHERE window_id = ?
                    """,
                    (
                        DEFAULT_DAILY_LIMIT,
                        DEFAULT_SOFT_LIMIT,
                        DEFAULT_CONSERVATION_LIMIT,
                        DEFAULT_SAFETY_RESERVE,
                        now_iso,
                        window["window_id"]
                    )
                )
                conn.execute("UPDATE token_deferred_queue SET status = 'resumed' WHERE status = 'deferred'")
                conn.commit()
                log_activity("WARN", "TokenBudgetManager", "Administrative budget reset executed", f"Window {window['window_id']}")
                return self.get_status_summary()
            finally:
                conn.close()


# Global Singleton Instance
token_budget_manager = TokenBudgetManager()
