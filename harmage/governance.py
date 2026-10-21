"""Governance and Authority Boundary Enforcement for Harmage Agents."""

import uuid
from datetime import datetime, timezone
from typing import Optional, Tuple
from harmage.db import get_connection
from harmage.models import (
    ActionType,
    ApprovalRequest,
    ApprovalStatus,
    Decision,
    RiskLevel,
)

# Actions that STRICTLY require human CEO approval per Section 3
HIGH_RISK_ACTIONS = {
    ActionType.FINANCIAL_EXPENSE,
    ActionType.BILLING_CHANGE,
    ActionType.PUBLIC_PUBLISH,
    ActionType.MASS_MESSAGING,
    ActionType.DESTRUCTIVE_DB,
    ActionType.CREDENTIAL_CHANGE,
    ActionType.INSTALL_MCP,
    ActionType.SECURITY_LOWERING,
    ActionType.OTHER_HIGH_RISK,
}


class GovernanceEngine:
    def __init__(self, db_path=None):
        self.db_path = db_path

    def evaluate_action(
        self,
        action_type: ActionType,
        description: str,
        rationale: str,
        requested_by: str = "executive_manager",
        task_id: Optional[str] = None,
        impact: str = "",
    ) -> Tuple[bool, Decision, Optional[ApprovalRequest]]:
        """Evaluate an action against governance boundaries.

        Returns:
            (allowed_to_execute: bool, decision: Decision, approval_request: Optional[ApprovalRequest])
        """
        requires_approval = action_type in HIGH_RISK_ACTIONS
        decision_id = f"DEC-{uuid.uuid4().hex[:8].upper()}"

        if requires_approval:
            approval_id = f"APR-{uuid.uuid4().hex[:8].upper()}"
            approval_req = ApprovalRequest(
                id=approval_id,
                action_type=action_type,
                description=description,
                requested_by=requested_by,
                status="pending",
                created_at=datetime.now(timezone.utc).isoformat(),
            )
            decision = Decision(
                id=decision_id,
                task_id=task_id,
                decision_type=action_type.value,
                summary=description,
                rationale=rationale,
                risk_level=RiskLevel.HIGH if action_type != ActionType.FINANCIAL_EXPENSE else RiskLevel.CRITICAL,
                requires_approval=True,
                approval_status=ApprovalStatus.PENDING_APPROVAL,
                approver="ceo",
                impact=impact or "Requires explicit CEO confirmation before execution.",
                created_at=datetime.now(timezone.utc).isoformat(),
            )
            self._persist_decision_and_approval(decision, approval_req)
            return False, decision, approval_req
        else:
            decision = Decision(
                id=decision_id,
                task_id=task_id,
                decision_type=action_type.value,
                summary=description,
                rationale=rationale,
                risk_level=RiskLevel.LOW,
                requires_approval=False,
                approval_status=ApprovalStatus.AUTO_APPROVED,
                approver=requested_by,
                impact=impact or "Routine autonomous operational action.",
                created_at=datetime.now(timezone.utc).isoformat(),
            )
            self._persist_decision(decision)
            return True, decision, None

    def resolve_approval(
        self, approval_id: str, approved: bool, ceo_notes: str = ""
    ) -> Optional[ApprovalRequest]:
        """Human CEO resolves a pending approval request."""
        conn = get_connection(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM approval_requests WHERE id = ?", (approval_id,)
        )
        row = cursor.fetchone()
        if not row:
            conn.close()
            return None

        req = ApprovalRequest.from_row(row)
        req.status = "approved" if approved else "rejected"
        req.ceo_notes = ceo_notes
        req.resolved_at = datetime.now(timezone.utc).isoformat()

        cursor.execute(
            """
            UPDATE approval_requests 
            SET status = ?, ceo_notes = ?, resolved_at = ?
            WHERE id = ?
        """,
            (req.status, req.ceo_notes, req.resolved_at, req.id),
        )

        # Update matching decision
        decision_status = (
            ApprovalStatus.APPROVED.value
            if approved
            else ApprovalStatus.REJECTED.value
        )
        cursor.execute(
            """
            UPDATE decisions
            SET approval_status = ?, approver = 'ceo'
            WHERE summary = ? AND requires_approval = 1
        """,
            (decision_status, req.description),
        )

        conn.commit()
        conn.close()
        return req

    def _persist_decision(self, decision: Decision) -> None:
        conn = get_connection(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO decisions (id, task_id, decision_type, summary, rationale, risk_level, requires_approval, approval_status, approver, impact, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                decision.id,
                decision.task_id,
                decision.decision_type,
                decision.summary,
                decision.rationale,
                decision.risk_level.value,
                1 if decision.requires_approval else 0,
                decision.approval_status.value,
                decision.approver,
                decision.impact,
                decision.created_at,
            ),
        )
        conn.commit()
        conn.close()

    def _persist_decision_and_approval(
        self, decision: Decision, approval_req: ApprovalRequest
    ) -> None:
        conn = get_connection(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO decisions (id, task_id, decision_type, summary, rationale, risk_level, requires_approval, approval_status, approver, impact, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                decision.id,
                decision.task_id,
                decision.decision_type,
                decision.summary,
                decision.rationale,
                decision.risk_level.value,
                1 if decision.requires_approval else 0,
                decision.approval_status.value,
                decision.approver,
                decision.impact,
                decision.created_at,
            ),
        )
        cursor.execute(
            """
            INSERT INTO approval_requests (id, action_type, description, requested_by, status, ceo_notes, created_at, resolved_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                approval_req.id,
                approval_req.action_type.value,
                approval_req.description,
                approval_req.requested_by,
                approval_req.status,
                approval_req.ceo_notes,
                approval_req.created_at,
                approval_req.resolved_at,
            ),
        )
        conn.commit()
        conn.close()
