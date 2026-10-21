"""Automated verification test suite for Harmage Executive Manager."""

import os
import tempfile
import unittest
from pathlib import Path

from harmage.db import initialize_database
from harmage.executive_manager import ExecutiveManager
from harmage.governance import GovernanceEngine
from harmage.models import (
    ActionType,
    ApprovalStatus,
    TaskPriority,
    TaskStatus,
)
from harmage.task_manager import TaskManager


class TestHarmageExecutiveManager(unittest.TestCase):
    def setUp(self):
        # Create an isolated temporary SQLite database for clean test execution
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_harmage.db"
        initialize_database(self.db_path)
        self.em = ExecutiveManager(db_path=self.db_path)
        self.tm = self.em.task_manager
        self.gov = self.em.governance

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_01_work_intake_creates_persistent_tasks(self):
        """Test that work intake properly creates and persists tasks in SQLite."""
        tasks = self.em.intake_goal(
            goal_title="Setup Content Strategy Q4",
            goal_description="Research and create content pipeline",
            priority=TaskPriority.P1,
        )
        self.assertEqual(len(tasks), 1)
        task = tasks[0]
        self.assertTrue(task.id.startswith("TSK-"))
        self.assertEqual(task.status, TaskStatus.QUEUED)
        self.assertEqual(task.priority, TaskPriority.P1)
        self.assertEqual(task.assignee, "executive_manager")

        # Verify persistence directly from DB
        retrieved = self.tm.get_task(task.id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.title, "Setup Content Strategy Q4")

    def test_02_task_state_transitions(self):
        """Test proper state transitions: queued -> in_progress -> review -> completed."""
        task = self.tm.create_task(
            title="Produce Pilot Video Script",
            description="Write 60-second tech script",
            priority=TaskPriority.P2,
        )
        self.assertEqual(task.status, TaskStatus.QUEUED)

        # Start task
        started = self.tm.start_task(task.id)
        self.assertEqual(started.status, TaskStatus.IN_PROGRESS)

        # Request review
        under_review = self.tm.request_review(task.id, preliminary_evidence="Draft v1 written")
        self.assertEqual(under_review.status, TaskStatus.REVIEW)
        self.assertEqual(under_review.evidence, "Draft v1 written")

        # Complete task
        completed = self.tm.complete_task(task.id, evidence="Script approved and stored at /scripts/pilot.md")
        self.assertEqual(completed.status, TaskStatus.COMPLETED)
        self.assertIn("/scripts/pilot.md", completed.evidence)

    def test_03_dependency_handling_and_auto_unblock(self):
        """Test that dependent tasks are blocked until parent is completed, then auto-unblocked."""
        # Task A: Parent
        task_a = self.tm.create_task(title="Record Raw Voiceover", description="Audio recording")
        # Task B: Child (depends on Task A)
        task_b = self.tm.create_task(
            title="Mix Background Music",
            description="Audio mixing",
            dependencies=[task_a.id],
        )

        # Attempt to start Task B before Task A is done -> must be BLOCKED
        attempt_b = self.tm.start_task(task_b.id)
        self.assertEqual(attempt_b.status, TaskStatus.BLOCKED)
        self.assertIn("Blocked by uncompleted dependencies", attempt_b.failure_reason)

        # Now complete Task A
        self.tm.start_task(task_a.id)
        self.tm.complete_task(task_a.id, evidence="voiceover.wav produced")

        # Check Task B -> must now be auto-unblocked to QUEUED
        unblocked_b = self.tm.get_task(task_b.id)
        self.assertEqual(unblocked_b.status, TaskStatus.QUEUED)
        self.assertIsNone(unblocked_b.failure_reason)

        # Now starting Task B should succeed to IN_PROGRESS
        started_b = self.tm.start_task(task_b.id)
        self.assertEqual(started_b.status, TaskStatus.IN_PROGRESS)

    def test_04_retry_limits_prevent_infinite_loops(self):
        """Test that task failure retries up to max_retries and then terminates as FAILED."""
        task = self.tm.create_task(
            title="Render 4K Visual Effects",
            description="Heavy rendering job",
            max_retries=2,
        )
        self.tm.start_task(task.id)

        # Retry 1
        r1 = self.tm.fail_or_retry(task.id, reason="GPU OOM error")
        self.assertEqual(r1.status, TaskStatus.QUEUED)
        self.assertEqual(r1.retry_count, 1)

        # Retry 2
        r2 = self.tm.fail_or_retry(task.id, reason="GPU OOM error second time")
        self.assertEqual(r2.status, TaskStatus.QUEUED)
        self.assertEqual(r2.retry_count, 2)

        # Retry 3 -> Exceeds max_retries (2) -> must transition to FAILED
        r3 = self.tm.fail_or_retry(task.id, reason="GPU OOM third time")
        self.assertEqual(r3.status, TaskStatus.FAILED)
        self.assertEqual(r3.retry_count, 2)
        self.assertIn("Max retries (2) exceeded", r3.failure_reason)

    def test_05_autonomous_decisions_vs_mandatory_ceo_approvals(self):
        """Test authority boundaries: routine actions are auto-approved; high-risk actions are gated."""
        # 1. Routine Operational Action (e.g. prioritize task) -> Auto approved
        allowed, dec_routine, req_routine = self.gov.evaluate_action(
            action_type=ActionType.ROUTINE_OPERATIONAL,
            description="Reorder sprint task priority",
            rationale="Milestone due in 2 days",
        )
        self.assertTrue(allowed)
        self.assertIsNone(req_routine)
        self.assertEqual(dec_routine.approval_status, ApprovalStatus.AUTO_APPROVED)

        # 2. Financial Expense -> Blocked, Pending CEO approval
        allowed_fin, dec_fin, req_fin = self.gov.evaluate_action(
            action_type=ActionType.FINANCIAL_EXPENSE,
            description="Purchase Canva Pro License $12.99",
            rationale="Needed for template export",
        )
        self.assertFalse(allowed_fin)
        self.assertIsNotNone(req_fin)
        self.assertEqual(dec_fin.approval_status, ApprovalStatus.PENDING_APPROVAL)
        self.assertEqual(req_fin.status, "pending")

        # 3. Public Publishing -> Blocked, Pending CEO approval
        allowed_pub, dec_pub, req_pub = self.gov.evaluate_action(
            action_type=ActionType.PUBLIC_PUBLISH,
            description="Publish video to TikTok account @harmage",
            rationale="Scheduled post",
        )
        self.assertFalse(allowed_pub)
        self.assertIsNotNone(req_pub)
        self.assertEqual(dec_pub.approval_status, ApprovalStatus.PENDING_APPROVAL)

        # 4. CEO Approves the request
        resolved = self.gov.resolve_approval(req_pub.id, approved=True, ceo_notes="Verified by CEO")
        self.assertEqual(resolved.status, "approved")
        self.assertEqual(resolved.ceo_notes, "Verified by CEO")

    def test_06_delegation_restricted_to_active_roles(self):
        """Test that work intake does not claim delegation to non-existent roles."""
        subtasks = [
            {"title": "Write Script", "assignee": "scriptwriter"},  # Planned role, not active
            {"title": "Executive Review", "assignee": "executive_manager"},  # Active role
        ]
        tasks = self.em.intake_goal(
            goal_title="Produce Episode 1",
            goal_description="Full production pipeline",
            subtasks_data=subtasks,
        )
        # Verify scriptwriter is safely mapped to executive_manager because scriptwriter is not active yet
        self.assertEqual(tasks[0].assignee, "executive_manager")
        self.assertEqual(tasks[1].assignee, "executive_manager")

    def test_07_internal_meetings_transparency(self):
        """Test that single-agent evaluation is accurately logged as 'internal_evaluation'."""
        meeting = self.em.hold_internal_evaluation(
            title="Q4 Sprint Retrospective",
            agenda="Review task throughput and bottlenecks",
            evaluation_notes="Single agent operational review. All tasks on schedule.",
            action_items=["Refine FFmpeg export presets"],
        )
        self.assertEqual(meeting.meeting_type.value, "internal_evaluation")
        self.assertEqual(meeting.participants, ["executive_manager"])

    def test_08_ceo_report_matches_actual_database_metrics(self):
        """Test that CEO executive report accurately reflects SQLite database metrics."""
        # Create 2 completed, 1 blocked, 1 queued
        t1 = self.tm.create_task("Task 1", "Desc")
        self.tm.start_task(t1.id)
        self.tm.complete_task(t1.id, "Proof 1")

        t2 = self.tm.create_task("Task 2", "Desc")
        self.tm.start_task(t2.id)
        self.tm.complete_task(t2.id, "Proof 2")

        t3 = self.tm.create_task("Task 3", "Desc", dependencies=["NON-EXISTENT"])
        self.tm.start_task(t3.id)  # Will be blocked

        t4 = self.tm.create_task("Task 4", "Desc")  # Queued

        # Create 1 pending approval
        self.gov.evaluate_action(
            action_type=ActionType.INSTALL_MCP,
            description="Install new MCP connector",
            rationale="Testing",
        )

        report = self.em.generate_ceo_report("Daily Executive Briefing")
        self.assertIsNotNone(report)
        self.assertEqual(report.metrics["total_tasks"], 4)
        self.assertEqual(report.metrics["completed"], 2)
        self.assertEqual(report.metrics["blocked"], 1)
        self.assertEqual(report.metrics["queued"], 1)
        self.assertEqual(report.metrics["pending_approvals"], 1)
        self.assertIn("Work Completion Rate**: 2/4 (50.0%)", report.content_markdown)
        self.assertIn("Matters Requiring CEO Approval", report.content_markdown)


if __name__ == "__main__":
    unittest.main()
