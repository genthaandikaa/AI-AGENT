"""Harmage Executive Manager (Director of Operations) Controller."""

import json
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from harmage.config import ACTIVE_ROLES, ROLES
from harmage.db import get_connection
from harmage.governance import GovernanceEngine
from harmage.models import (
    ActionType,
    ApprovalRequest,
    MeetingRecord,
    MeetingType,
    ReportRecord,
    Task,
    TaskPriority,
    TaskStatus,
)
from harmage.task_manager import TaskManager


class ExecutiveManager:
    def __init__(self, db_path=None):
        self.db_path = db_path
        from harmage.db import initialize_database
        initialize_database(db_path)
        self.task_manager = TaskManager(db_path=db_path)
        self.governance = GovernanceEngine(db_path=db_path)

    # ─────────────────────────────────────────────────────────────────────────
    # A. Work Intake & Decomposition
    # ─────────────────────────────────────────────────────────────────────────

    def intake_goal(
        self,
        goal_title: str,
        goal_description: str,
        priority: TaskPriority = TaskPriority.P1,
        subtasks_data: Optional[List[Dict[str, Any]]] = None,
    ) -> List[Task]:
        """Decompose a business goal into concrete, actionable tasks with dependencies."""
        created_tasks: List[Task] = []

        # Record autonomous operational decision
        self.governance.evaluate_action(
            action_type=ActionType.ROUTINE_OPERATIONAL,
            description=f"Decomposing business goal: {goal_title}",
            rationale="Executive Manager autonomous work breakdown and priority assignment.",
            requested_by="executive_manager",
        )

        if not subtasks_data:
            # Create a single unified intake task
            task = self.task_manager.create_task(
                title=goal_title,
                description=goal_description,
                assignee="executive_manager",
                priority=priority,
                acceptance_criteria=[
                    "Objective requirements analyzed",
                    "Execution evidence produced",
                    "Final deliverable verified",
                ],
            )
            created_tasks.append(task)
            return created_tasks

        # Multi-task decomposition with sequential or explicit dependencies
        id_map: Dict[str, str] = {}  # local alias to real task ID

        for i, sub in enumerate(subtasks_data):
            # Resolve dependencies
            raw_deps = sub.get("dependencies", [])
            resolved_deps = [id_map.get(d, d) for d in raw_deps]

            # Assignee check: only assign to active roles; default to executive_manager
            requested_assignee = sub.get("assignee", "executive_manager")
            actual_assignee = (
                requested_assignee
                if requested_assignee in ACTIVE_ROLES
                else "executive_manager"
            )

            task = self.task_manager.create_task(
                title=sub.get("title", f"{goal_title} - Step {i+1}"),
                description=sub.get("description", ""),
                assignee=actual_assignee,
                priority=sub.get("priority", priority),
                deadline=sub.get("deadline"),
                dependencies=resolved_deps,
                acceptance_criteria=sub.get("acceptance_criteria", []),
                max_retries=sub.get("max_retries", 3),
            )
            alias = sub.get("alias", f"step_{i+1}")
            id_map[alias] = task.id
            created_tasks.append(task)

        return created_tasks

    # ─────────────────────────────────────────────────────────────────────────
    # B. Delegation & Execution Gate
    # ─────────────────────────────────────────────────────────────────────────

    def dispatch_action(
        self,
        task_id: str,
        action_type: ActionType,
        action_description: str,
        rationale: str,
    ) -> Tuple[bool, str]:
        """Check authority before executing an action for a task.

        Returns:
            (can_proceed: bool, message: str)
        """
        allowed, decision, approval_req = self.governance.evaluate_action(
            action_type=action_type,
            description=action_description,
            rationale=rationale,
            requested_by="executive_manager",
            task_id=task_id,
        )

        self.task_manager.attach_decision(task_id, decision.id)

        if not allowed and approval_req:
            # Action is high risk: cannot proceed without CEO approval
            task = self.task_manager.get_task(task_id)
            if task:
                task.status = TaskStatus.BLOCKED
                task.failure_reason = (
                    f"Blocked pending CEO approval for: {approval_req.description} "
                    f"(Approval ID: {approval_req.id})"
                )
                self.task_manager._update_task(task)
            return False, f"Action held. Pending CEO approval: {approval_req.id}"

        return True, f"Action authorized autonomously: {decision.id}"

    # ─────────────────────────────────────────────────────────────────────────
    # C. Internal Meetings & Evaluation
    # ─────────────────────────────────────────────────────────────────────────

    def hold_internal_evaluation(
        self,
        title: str,
        agenda: str,
        evaluation_notes: str,
        action_items: Optional[List[str]] = None,
    ) -> MeetingRecord:
        """Conduct an internal operational evaluation.

        Strictly categorized as 'internal_evaluation' when single agent.
        """
        meeting_id = f"MTG-{uuid.uuid4().hex[:8].upper()}"
        record = MeetingRecord(
            id=meeting_id,
            title=title,
            meeting_type=MeetingType.INTERNAL_EVALUATION,
            agenda=agenda,
            participants=["executive_manager"],
            discussion=evaluation_notes,
            action_items=action_items or [],
            created_at=datetime.now(timezone.utc).isoformat(),
        )

        conn = get_connection(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO meetings (id, title, meeting_type, agenda, participants, discussion, action_items, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                record.id,
                record.title,
                record.meeting_type.value,
                record.agenda,
                json.dumps(record.participants),
                record.discussion,
                json.dumps(record.action_items),
                record.created_at,
            ),
        )
        conn.commit()
        conn.close()
        return record

    # ─────────────────────────────────────────────────────────────────────────
    # D. CEO Reporting
    # ─────────────────────────────────────────────────────────────────────────

    def generate_ceo_report(self, report_title: str = "Harmage Operations Briefing") -> ReportRecord:
        """Compile a concise, decision-oriented CEO executive report from persistent data."""
        tasks = self.task_manager.list_tasks(limit=500)

        # Calculate metrics
        total = len(tasks)
        completed = [t for t in tasks if t.status == TaskStatus.COMPLETED]
        in_progress = [t for t in tasks if t.status == TaskStatus.IN_PROGRESS]
        queued = [t for t in tasks if t.status == TaskStatus.QUEUED]
        blocked = [t for t in tasks if t.status == TaskStatus.BLOCKED]
        failed = [t for t in tasks if t.status == TaskStatus.FAILED]

        # Fetch pending approvals
        conn = get_connection(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM approval_requests WHERE status = 'pending'")
        pending_approvals = [ApprovalRequest.from_row(r) for r in cursor.fetchall()]
        conn.close()

        metrics = {
            "total_tasks": total,
            "completed": len(completed),
            "in_progress": len(in_progress),
            "queued": len(queued),
            "blocked": len(blocked),
            "failed": len(failed),
            "pending_approvals": len(pending_approvals),
        }

        # Build Markdown Content
        lines = [
            f"# {report_title}",
            f"*Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}*",
            "",
            "## 1. Executive Summary",
            f"- **System State**: Operational (Phase 1: Executive Manager)",
            f"- **Active Roles**: {', '.join(ACTIVE_ROLES)}",
            f"- **Work Completion Rate**: {len(completed)}/{total} ({round(len(completed)/total*100, 1) if total > 0 else 0}%)",
            f"- **Action Items Awaiting CEO**: {len(pending_approvals)} item(s)",
            "",
            "## 2. Work Stream Overview",
            "| Task ID | Title | Priority | Status | Assignee | Proof / Reason |",
            "| :--- | :--- | :--- | :--- | :--- | :--- |",
        ]

        for t in tasks[:15]:
            note = (t.evidence or t.failure_reason or "-")[:60]
            lines.append(f"| `{t.id}` | {t.title} | {t.priority.value} | `{t.status.value}` | {t.assignee} | {note} |")

        if len(tasks) > 15:
            lines.append(f"| ... | *(+{len(tasks)-15} additional tasks in database)* | | | | |")

        lines.extend([
            "",
            "## 3. Matters Requiring CEO Approval",
        ])

        if pending_approvals:
            for apr in pending_approvals:
                lines.append(f"- **[APPROVAL NEEDED: `{apr.id}`]** {apr.action_type.value}: {apr.description} *(Requested by {apr.requested_by})*")
        else:
            lines.append("- *No high-risk actions currently pending approval.*")

        lines.extend([
            "",
            "## 4. Next Operational Priorities",
            "- Validate Phase 1 Executive Manager local test suite.",
            "- Finalize Creator Division Community MCP evaluation and security matrix.",
            "- Await CEO authorization before initiating any external publishing or tool installations.",
        ])

        markdown_body = "\n".join(lines)
        report_id = f"RPT-{uuid.uuid4().hex[:8].upper()}"

        record = ReportRecord(
            id=report_id,
            report_type="daily_ceo",
            title=report_title,
            summary=f"Total: {total} | Completed: {len(completed)} | Blocked: {len(blocked)} | Pending Approvals: {len(pending_approvals)}",
            metrics=metrics,
            content_markdown=markdown_body,
            created_at=datetime.now(timezone.utc).isoformat(),
        )

        conn = get_connection(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO reports (id, report_type, title, summary, metrics, content_markdown, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (
                record.id,
                record.report_type,
                record.title,
                record.summary,
                json.dumps(record.metrics),
                record.content_markdown,
                record.created_at,
            ),
        )
        conn.commit()
        conn.close()
        return record
