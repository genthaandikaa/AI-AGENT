"""Persistent Task Management Engine for Harmage Agents."""

import json
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from harmage.db import get_connection
from harmage.models import Task, TaskPriority, TaskStatus


class TaskManager:
    def __init__(self, db_path=None):
        self.db_path = db_path

    def create_task(
        self,
        title: str,
        description: str,
        assignee: str = "executive_manager",
        priority: TaskPriority = TaskPriority.P2,
        deadline: Optional[str] = None,
        dependencies: Optional[List[str]] = None,
        acceptance_criteria: Optional[List[str]] = None,
        max_retries: int = 3,
    ) -> Task:
        """Create and persist a new task in QUEUED status."""
        task_id = f"TSK-{uuid.uuid4().hex[:8].upper()}"
        task = Task(
            id=task_id,
            title=title,
            description=description,
            assignee=assignee,
            priority=priority,
            status=TaskStatus.QUEUED,
            deadline=deadline,
            dependencies=dependencies or [],
            acceptance_criteria=acceptance_criteria or [],
            decision_log=[],
            retry_count=0,
            max_retries=max_retries,
            evidence=None,
            failure_reason=None,
            created_at=datetime.now(timezone.utc).isoformat(),
            updated_at=datetime.now(timezone.utc).isoformat(),
        )
        self._persist_task(task)
        return task

    def get_task(self, task_id: str) -> Optional[Task]:
        """Retrieve a task by ID."""
        conn = get_connection(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        row = cursor.fetchone()
        conn.close()
        return Task.from_row(row) if row else None

    def list_tasks(
        self,
        status: Optional[TaskStatus] = None,
        assignee: Optional[str] = None,
        limit: int = 100,
    ) -> List[Task]:
        """List tasks with optional status and assignee filter."""
        conn = get_connection(self.db_path)
        cursor = conn.cursor()
        query = "SELECT * FROM tasks WHERE 1=1"
        params: List[Any] = []
        if status:
            query += " AND status = ?"
            params.append(status.value if isinstance(status, TaskStatus) else status)
        if assignee:
            query += " AND assignee = ?"
            params.append(assignee)
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        return [Task.from_row(r) for r in rows]

    def update_status(
        self,
        task_id: str,
        new_status: TaskStatus,
        evidence: Optional[str] = None,
        failure_reason: Optional[str] = None
    ) -> Task:
        """Update a task's status with evidence or failure reason."""
        if new_status == TaskStatus.IN_PROGRESS:
            return self.start_task(task_id)
        elif new_status == TaskStatus.COMPLETED:
            return self.complete_task(task_id, evidence or "Completed via API")
        elif new_status == TaskStatus.REVIEW:
            return self.request_review(task_id, evidence or "Ready for review")
        elif new_status in (TaskStatus.FAILED, TaskStatus.BLOCKED):
            task = self.get_task(task_id)
            if not task:
                raise ValueError(f"Task {task_id} not found.")
            task.status = new_status
            task.failure_reason = failure_reason or f"Marked as {new_status.value}"
            task.updated_at = datetime.now(timezone.utc).isoformat()
            self._update_task(task)
            return task
        else:
            task = self.get_task(task_id)
            if not task:
                raise ValueError(f"Task {task_id} not found.")
            task.status = new_status
            task.updated_at = datetime.now(timezone.utc).isoformat()
            self._update_task(task)
            return task

    def start_task(self, task_id: str) -> Task:
        """Attempt to start a task. Validates dependencies.

        If dependencies are not completed, marks task as BLOCKED.
        Otherwise transitions to IN_PROGRESS.
        """
        task = self.get_task(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found.")

        # Check dependencies
        if task.dependencies:
            unresolved = []
            for dep_id in task.dependencies:
                dep_task = self.get_task(dep_id)
                if not dep_task or dep_task.status != TaskStatus.COMPLETED:
                    unresolved.append(dep_id)

            if unresolved:
                task.status = TaskStatus.BLOCKED
                task.failure_reason = f"Blocked by uncompleted dependencies: {', '.join(unresolved)}"
                task.updated_at = datetime.now(timezone.utc).isoformat()
                self._update_task(task)
                return task

        task.status = TaskStatus.IN_PROGRESS
        task.failure_reason = None
        task.updated_at = datetime.now(timezone.utc).isoformat()
        self._update_task(task)
        return task

    def complete_task(self, task_id: str, evidence: str) -> Task:
        """Mark a task as COMPLETED with verifiable evidence."""
        task = self.get_task(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found.")

        task.status = TaskStatus.COMPLETED
        task.evidence = evidence
        task.failure_reason = None
        task.updated_at = datetime.now(timezone.utc).isoformat()
        self._update_task(task)

        # Unblock any dependent tasks if their blockers are now clear
        self._check_and_unblock_dependents(task_id)
        return task

    def request_review(self, task_id: str, preliminary_evidence: str) -> Task:
        """Transition task to REVIEW status for evaluation."""
        task = self.get_task(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found.")

        task.status = TaskStatus.REVIEW
        task.evidence = preliminary_evidence
        task.updated_at = datetime.now(timezone.utc).isoformat()
        self._update_task(task)
        return task

    def fail_or_retry(self, task_id: str, reason: str, allow_retry: bool = True) -> Task:
        """Handle task failure.

        Checks retry limits. If retries remain, increments retry_count
        and resets to QUEUED. If retries exceeded or forbidden, marks FAILED.
        """
        task = self.get_task(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found.")

        if allow_retry and task.retry_count < task.max_retries:
            task.retry_count += 1
            task.status = TaskStatus.QUEUED
            task.failure_reason = f"Retry {task.retry_count}/{task.max_retries} queued. Reason: {reason}"
        else:
            task.status = TaskStatus.FAILED
            task.failure_reason = f"Max retries ({task.max_retries}) exceeded or fatal failure: {reason}"

        task.updated_at = datetime.now(timezone.utc).isoformat()
        self._update_task(task)
        return task

    def attach_decision(self, task_id: str, decision_id: str) -> None:
        """Append a decision reference to the task's decision log."""
        task = self.get_task(task_id)
        if task:
            if decision_id not in task.decision_log:
                task.decision_log.append(decision_id)
                task.updated_at = datetime.now(timezone.utc).isoformat()
                self._update_task(task)

    def _check_and_unblock_dependents(self, completed_task_id: str) -> None:
        """Scan blocked tasks and unblock them if all dependencies are satisfied."""
        blocked_tasks = self.list_tasks(status=TaskStatus.BLOCKED)
        for b_task in blocked_tasks:
            if completed_task_id in b_task.dependencies:
                still_blocked = False
                for dep_id in b_task.dependencies:
                    dep = self.get_task(dep_id)
                    if not dep or dep.status != TaskStatus.COMPLETED:
                        still_blocked = True
                        break
                if not still_blocked:
                    b_task.status = TaskStatus.QUEUED
                    b_task.failure_reason = None
                    b_task.updated_at = datetime.now(timezone.utc).isoformat()
                    self._update_task(b_task)

    def _persist_task(self, task: Task) -> None:
        conn = get_connection(self.db_path)
        cursor = conn.cursor()
        d = task.to_dict()
        cursor.execute(
            """
            INSERT INTO tasks (id, title, description, assignee, priority, status, deadline, dependencies, acceptance_criteria, decision_log, retry_count, max_retries, evidence, failure_reason, created_at, updated_at)
            VALUES (:id, :title, :description, :assignee, :priority, :status, :deadline, :dependencies, :acceptance_criteria, :decision_log, :retry_count, :max_retries, :evidence, :failure_reason, :created_at, :updated_at)
        """,
            d,
        )
        conn.commit()
        conn.close()

    def _update_task(self, task: Task) -> None:
        conn = get_connection(self.db_path)
        cursor = conn.cursor()
        d = task.to_dict()
        cursor.execute(
            """
            UPDATE tasks SET
                title = :title,
                description = :description,
                assignee = :assignee,
                priority = :priority,
                status = :status,
                deadline = :deadline,
                dependencies = :dependencies,
                acceptance_criteria = :acceptance_criteria,
                decision_log = :decision_log,
                retry_count = :retry_count,
                max_retries = :max_retries,
                evidence = :evidence,
                failure_reason = :failure_reason,
                updated_at = :updated_at
            WHERE id = :id
        """,
            d,
        )
        conn.commit()
        conn.close()
