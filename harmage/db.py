"""Persistent SQLite storage engine for Harmage Operations."""

import sqlite3
import threading
from pathlib import Path
from typing import Optional
from harmage.config import DB_PATH

_lock = threading.Lock()


def get_connection(db_path: Optional[Path] = None) -> sqlite3.Connection:
    """Get a thread-safe connection to SQLite with WAL mode enabled."""
    target_path = db_path or DB_PATH
    target_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(target_path), timeout=30.0)
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def initialize_database(db_path: Optional[Path] = None) -> None:
    """Initialize database tables with full constraints and indexes."""
    with _lock:
        conn = get_connection(db_path)
        cursor = conn.cursor()

        # 1. Tasks Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT,
            assignee TEXT NOT NULL,
            priority TEXT NOT NULL,
            status TEXT NOT NULL CHECK(status IN ('queued', 'in_progress', 'blocked', 'review', 'completed', 'failed')),
            deadline TEXT,
            dependencies TEXT,           -- JSON array of task IDs
            acceptance_criteria TEXT,    -- JSON array of criteria
            decision_log TEXT,           -- JSON array of decision IDs
            retry_count INTEGER DEFAULT 0,
            max_retries INTEGER DEFAULT 3,
            evidence TEXT,
            failure_reason TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tasks_assignee ON tasks(assignee);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tasks_priority ON tasks(priority);")

        # 2. Decisions Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS decisions (
            id TEXT PRIMARY KEY,
            task_id TEXT,
            decision_type TEXT NOT NULL,
            summary TEXT NOT NULL,
            rationale TEXT NOT NULL,
            risk_level TEXT NOT NULL,
            requires_approval INTEGER NOT NULL,
            approval_status TEXT NOT NULL CHECK(approval_status IN ('auto_approved', 'pending_approval', 'approved', 'rejected')),
            approver TEXT NOT NULL,
            impact TEXT,
            created_at TEXT NOT NULL
        );
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_decisions_task_id ON decisions(task_id);")

        # 3. Meetings Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS meetings (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            meeting_type TEXT NOT NULL CHECK(meeting_type IN ('internal_evaluation', 'multi_agent_session', 'simulated')),
            agenda TEXT NOT NULL,
            participants TEXT NOT NULL,
            discussion TEXT,
            action_items TEXT,
            created_at TEXT NOT NULL
        );
        """)

        # 4. Reports Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS reports (
            id TEXT PRIMARY KEY,
            report_type TEXT NOT NULL,
            title TEXT NOT NULL,
            summary TEXT NOT NULL,
            metrics TEXT,
            content_markdown TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        """)

        # 5. Approval Requests Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS approval_requests (
            id TEXT PRIMARY KEY,
            action_type TEXT NOT NULL,
            description TEXT NOT NULL,
            requested_by TEXT NOT NULL,
            status TEXT NOT NULL CHECK(status IN ('pending', 'approved', 'rejected')),
            ceo_notes TEXT,
            created_at TEXT NOT NULL,
            resolved_at TEXT
        );
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_approvals_status ON approval_requests(status);")

        # 6. Schedules Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS schedules (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            cron_expr TEXT,
            interval_type TEXT NOT NULL,
            target_role TEXT NOT NULL,
            action TEXT NOT NULL,
            next_run TEXT NOT NULL,
            last_run TEXT,
            enabled INTEGER DEFAULT 1,
            created_at TEXT NOT NULL
        );
        """)

        # 7. Activity Logs Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS activity_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            level TEXT NOT NULL CHECK(level IN ('INFO', 'WARN', 'ERROR', 'GOVERNANCE')),
            actor TEXT NOT NULL,
            action TEXT NOT NULL,
            details TEXT,
            created_at TEXT NOT NULL
        );
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_activity_created ON activity_logs(created_at DESC);")

        # 8. Token Budget Daily Windows (Asia/Jakarta boundary, 2M shared ceiling)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS token_budget_windows (
            window_id TEXT PRIMARY KEY,
            date_str TEXT NOT NULL,
            timezone TEXT NOT NULL DEFAULT 'Asia/Jakarta',
            window_start TEXT NOT NULL,
            window_end TEXT NOT NULL,
            daily_limit INTEGER NOT NULL DEFAULT 2000000,
            soft_limit INTEGER NOT NULL DEFAULT 1600000,
            conservation_limit INTEGER NOT NULL DEFAULT 1800000,
            safety_reserve INTEGER NOT NULL DEFAULT 50000,
            confirmed_tokens INTEGER NOT NULL DEFAULT 0,
            estimated_tokens INTEGER NOT NULL DEFAULT 0,
            reserved_tokens INTEGER NOT NULL DEFAULT 0,
            qwen_tokens INTEGER NOT NULL DEFAULT 0,
            gemini_tokens INTEGER NOT NULL DEFAULT 0,
            other_tokens INTEGER NOT NULL DEFAULT 0,
            mode TEXT NOT NULL DEFAULT 'NORMAL' CHECK(mode IN ('NORMAL', 'EFFICIENT', 'CONSERVATION', 'CEILING_REACHED')),
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_token_windows_date ON token_budget_windows(date_str);")

        # 9. Token Usage Events (Input/Output/Total audit breakdown per call)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS token_usage_events (
            id TEXT PRIMARY KEY,
            window_id TEXT NOT NULL,
            provider TEXT NOT NULL,
            model TEXT NOT NULL,
            agent_id TEXT,
            division TEXT,
            task_id TEXT,
            call_type TEXT NOT NULL,
            prompt_tokens INTEGER NOT NULL DEFAULT 0,
            completion_tokens INTEGER NOT NULL DEFAULT 0,
            total_tokens INTEGER NOT NULL DEFAULT 0,
            is_estimated INTEGER NOT NULL DEFAULT 0,
            confidence TEXT NOT NULL DEFAULT 'confirmed',
            created_at TEXT NOT NULL,
            FOREIGN KEY (window_id) REFERENCES token_budget_windows(window_id)
        );
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_token_events_window ON token_usage_events(window_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_token_events_provider ON token_usage_events(provider);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_token_events_agent ON token_usage_events(agent_id);")

        # 10. Token Reservations (Atomic in-flight allowance tracking)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS token_reservations (
            reservation_id TEXT PRIMARY KEY,
            window_id TEXT NOT NULL,
            agent_id TEXT,
            priority TEXT NOT NULL DEFAULT 'medium',
            estimated_tokens INTEGER NOT NULL DEFAULT 400,
            status TEXT NOT NULL DEFAULT 'RESERVED' CHECK(status IN ('RESERVED', 'RECONCILED', 'EXPIRED', 'CANCELLED')),
            created_at TEXT NOT NULL,
            expires_at TEXT NOT NULL
        );
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_token_res_window ON token_reservations(window_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_token_res_status ON token_reservations(status);")

        # 11. Token Deferred Queue (Persistent queue for tasks paused due to budget ceiling)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS token_deferred_queue (
            id TEXT PRIMARY KEY,
            task_id TEXT,
            agent_id TEXT,
            title TEXT NOT NULL,
            call_type TEXT NOT NULL,
            payload_preview TEXT,
            priority TEXT NOT NULL DEFAULT 'medium',
            deferral_reason TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'deferred' CHECK(status IN ('deferred', 'resumed', 'cancelled')),
            created_at TEXT NOT NULL
        );
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_token_def_status ON token_deferred_queue(status);")

        # 12. YouTube Long-Form Topic Backlog & Rubric Scoring
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS longform_topics (
            id TEXT PRIMARY KEY,
            category TEXT NOT NULL,
            title TEXT NOT NULL,
            hook_question TEXT NOT NULL,
            scores TEXT NOT NULL,        -- JSON object of rubric criteria
            total_score REAL NOT NULL,
            editorial_rationale TEXT,
            source_links TEXT,           -- JSON array of verified research sources
            status TEXT NOT NULL DEFAULT 'backlog' CHECK(status IN ('backlog', 'selected', 'in_production', 'produced', 'rejected')),
            last_used_at TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_longform_topics_status ON longform_topics(status);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_longform_topics_score ON longform_topics(total_score DESC);")

        # 13. YouTube Long-Form Productions (Stage progression & artifact manifest tracking)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS longform_productions (
            id TEXT PRIMARY KEY,
            topic_id TEXT NOT NULL,
            title TEXT NOT NULL,
            slug TEXT NOT NULL UNIQUE,
            stage TEXT NOT NULL DEFAULT 'topic_research' CHECK(stage IN (
                'topic_research', 'fact_check', 'script', 'storyboard',
                'visual_assets', 'editing', 'render', 'qa', 'ceo_review'
            )),
            assignee TEXT NOT NULL DEFAULT 'editor_longform',
            manifest_path TEXT,
            script_path TEXT,
            storyboard_path TEXT,
            ledger_path TEXT,
            output_video_path TEXT,
            preview_video_path TEXT,
            duration_seconds REAL DEFAULT 0.0,
            resolution TEXT DEFAULT '1920x1080',
            file_size_bytes INTEGER DEFAULT 0,
            qa_status TEXT DEFAULT 'pending',
            error_message TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (topic_id) REFERENCES longform_topics(id)
        );
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_longform_prod_stage ON longform_productions(stage);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_longform_prod_slug ON longform_productions(slug);")

        conn.commit()
        conn.close()


def log_activity(level: str, actor: str, action: str, details: str = "", db_path: Optional[Path] = None) -> None:
    """Record an audit trail activity log."""
    from datetime import datetime, timezone
    with _lock:
        conn = get_connection(db_path)
        conn.execute(
            "INSERT INTO activity_logs (level, actor, action, details, created_at) VALUES (?, ?, ?, ?, ?)",
            (level, actor, action, details, datetime.now(timezone.utc).isoformat())
        )
        conn.commit()
        conn.close()

