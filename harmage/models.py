"""Data models for Harmage Agents operations."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
import json


class TaskStatus(str, Enum):
    QUEUED = "queued"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    REVIEW = "review"
    COMPLETED = "completed"
    FAILED = "failed"


class TaskPriority(str, Enum):
    P0 = "P0"  # Critical / Blocker
    P1 = "P1"  # High
    P2 = "P2"  # Medium
    P3 = "P3"  # Low

    @classmethod
    def from_value(cls, val: Any) -> "TaskPriority":
        if isinstance(val, TaskPriority):
            return val
        s = str(val).lower()
        if s in ("p0", "critical", "blocker"):
            return cls.P0
        if s in ("p1", "high"):
            return cls.P1
        if s in ("p2", "medium"):
            return cls.P2
        if s in ("p3", "low"):
            return cls.P3
        try:
            return cls(val)
        except (ValueError, TypeError):
            return cls.P2


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ApprovalStatus(str, Enum):
    AUTO_APPROVED = "auto_approved"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"


class MeetingType(str, Enum):
    INTERNAL_EVALUATION = "internal_evaluation"
    MULTI_AGENT_SESSION = "multi_agent_session"
    SIMULATED = "simulated"


class ActionType(str, Enum):
    FINANCIAL_EXPENSE = "financial_expense"
    BILLING_CHANGE = "billing_change"
    PUBLIC_PUBLISH = "public_publish"
    MASS_MESSAGING = "mass_messaging"
    DESTRUCTIVE_DB = "destructive_db"
    CREDENTIAL_CHANGE = "credential_change"
    INSTALL_MCP = "install_mcp"
    SECURITY_LOWERING = "security_lowering"
    OTHER_HIGH_RISK = "other_high_risk"
    ROUTINE_OPERATIONAL = "routine_operational"


@dataclass
class Task:
    id: str
    title: str
    description: str
    assignee: str = "executive_manager"
    priority: TaskPriority = TaskPriority.P2
    status: TaskStatus = TaskStatus.QUEUED
    deadline: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    acceptance_criteria: List[str] = field(default_factory=list)
    decision_log: List[str] = field(default_factory=list)
    retry_count: int = 0
    max_retries: int = 3
    evidence: Optional[str] = None
    failure_reason: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "assignee": self.assignee,
            "priority": self.priority.value if isinstance(self.priority, TaskPriority) else self.priority,
            "status": self.status.value if isinstance(self.status, TaskStatus) else self.status,
            "deadline": self.deadline,
            "dependencies": json.dumps(self.dependencies),
            "acceptance_criteria": json.dumps(self.acceptance_criteria),
            "decision_log": json.dumps(self.decision_log),
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "evidence": self.evidence,
            "failure_reason": self.failure_reason,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_row(cls, row: tuple) -> "Task":
        return cls(
            id=row[0],
            title=row[1],
            description=row[2],
            assignee=row[3],
            priority=TaskPriority.from_value(row[4]),
            status=TaskStatus(row[5]),
            deadline=row[6],
            dependencies=json.loads(row[7]) if row[7] else [],
            acceptance_criteria=json.loads(row[8]) if row[8] else [],
            decision_log=json.loads(row[9]) if row[9] else [],
            retry_count=row[10],
            max_retries=row[11],
            evidence=row[12],
            failure_reason=row[13],
            created_at=row[14],
            updated_at=row[15],
        )


@dataclass
class Decision:
    id: str
    task_id: Optional[str]
    decision_type: str
    summary: str
    rationale: str
    risk_level: RiskLevel
    requires_approval: bool
    approval_status: ApprovalStatus
    approver: str
    impact: str = ""
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "task_id": self.task_id,
            "decision_type": self.decision_type,
            "summary": self.summary,
            "rationale": self.rationale,
            "risk_level": self.risk_level.value if isinstance(self.risk_level, RiskLevel) else self.risk_level,
            "requires_approval": 1 if self.requires_approval else 0,
            "approval_status": self.approval_status.value if isinstance(self.approval_status, ApprovalStatus) else self.approval_status,
            "approver": self.approver,
            "impact": self.impact,
            "created_at": self.created_at,
        }

    @classmethod
    def from_row(cls, row: tuple) -> "Decision":
        return cls(
            id=row[0],
            task_id=row[1],
            decision_type=row[2],
            summary=row[3],
            rationale=row[4],
            risk_level=RiskLevel(row[5]),
            requires_approval=bool(row[6]),
            approval_status=ApprovalStatus(row[7]),
            approver=row[8],
            impact=row[9] or "",
            created_at=row[10],
        )


@dataclass
class MeetingRecord:
    id: str
    title: str
    meeting_type: MeetingType
    agenda: str
    participants: List[str]
    discussion: str
    action_items: List[str]
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "meeting_type": self.meeting_type.value if isinstance(self.meeting_type, MeetingType) else self.meeting_type,
            "agenda": self.agenda,
            "participants": json.dumps(self.participants),
            "discussion": self.discussion,
            "action_items": json.dumps(self.action_items),
            "created_at": self.created_at,
        }

    @classmethod
    def from_row(cls, row: tuple) -> "MeetingRecord":
        return cls(
            id=row[0],
            title=row[1],
            meeting_type=MeetingType(row[2]),
            agenda=row[3],
            participants=json.loads(row[4]) if row[4] else [],
            discussion=row[5] or "",
            action_items=json.loads(row[6]) if row[6] else [],
            created_at=row[7],
        )


@dataclass
class ReportRecord:
    id: str
    report_type: str
    title: str
    summary: str
    metrics: Dict[str, Any]
    content_markdown: str
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "report_type": self.report_type,
            "title": self.title,
            "summary": self.summary,
            "metrics": json.dumps(self.metrics),
            "content_markdown": self.content_markdown,
            "created_at": self.created_at,
        }

    @classmethod
    def from_row(cls, row: tuple) -> "ReportRecord":
        return cls(
            id=row[0],
            report_type=row[1],
            title=row[2],
            summary=row[3],
            metrics=json.loads(row[4]) if row[4] else {},
            content_markdown=row[5],
            created_at=row[6],
        )


@dataclass
class ApprovalRequest:
    id: str
    action_type: ActionType
    description: str
    requested_by: str
    status: str = "pending"
    ceo_notes: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    resolved_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "action_type": self.action_type.value if isinstance(self.action_type, ActionType) else self.action_type,
            "description": self.description,
            "requested_by": self.requested_by,
            "status": self.status,
            "ceo_notes": self.ceo_notes,
            "created_at": self.created_at,
            "resolved_at": self.resolved_at,
        }

    @classmethod
    def from_row(cls, row: tuple) -> "ApprovalRequest":
        return cls(
            id=row[0],
            action_type=ActionType(row[1]),
            description=row[2],
            requested_by=row[3],
            status=row[4],
            ceo_notes=row[5],
            created_at=row[6],
            resolved_at=row[7],
        )
