"""Harmage Agents Command Line Interface."""

import argparse
import sys
from harmage.db import initialize_database
from harmage.executive_manager import ExecutiveManager
from harmage.models import TaskPriority, TaskStatus


def main():
    parser = argparse.ArgumentParser(description="Harmage Agents Management CLI")
    subparsers = parser.add_subparsers(dest="command")

    # init
    subparsers.add_parser("init", help="Initialize the Harmage database")

    # tasks
    task_p = subparsers.add_parser("tasks", help="Manage tasks")
    task_sub = task_p.add_subparsers(dest="task_command")

    task_list = task_sub.add_parser("list", help="List all tasks")
    task_list.add_argument("--status", choices=[s.value for s in TaskStatus])

    task_intake = task_sub.add_parser("intake", help="Intake a new goal")
    task_intake.add_argument("title", help="Goal or task title")
    task_intake.add_argument("--desc", default="", help="Description")
    task_intake.add_argument("--priority", choices=["P0", "P1", "P2", "P3"], default="P2")

    # report
    subparsers.add_parser("report", help="Generate and view CEO executive report")

    # approvals
    appr_p = subparsers.add_parser("approvals", help="Manage CEO approvals")
    appr_sub = appr_p.add_subparsers(dest="appr_command")
    appr_sub.add_parser("list", help="List pending approvals")

    resolve_p = appr_sub.add_parser("resolve", help="Approve or reject a request")
    resolve_p.add_argument("id", help="Approval ID")
    resolve_p.add_argument("--approve", action="store_true", help="Approve the action")
    resolve_p.add_argument("--reject", action="store_true", help="Reject the action")
    resolve_p.add_argument("--notes", default="", help="CEO notes")

    args = parser.parse_args()

    if args.command == "init":
        initialize_database()
        print("Harmage Operations database initialized successfully.")

    elif args.command == "tasks":
        em = ExecutiveManager()
        if args.task_command == "list":
            tasks = em.task_manager.list_tasks(
                status=TaskStatus(args.status) if args.status else None
            )
            print(f"Total tasks: {len(tasks)}")
            for t in tasks:
                print(f"[{t.status.value.upper()}] {t.id} - {t.title} ({t.priority.value}) -> {t.assignee}")
        elif args.task_command == "intake":
            tasks = em.intake_goal(args.title, args.desc, priority=TaskPriority(args.priority))
            print(f"Intake complete. Created {len(tasks)} task(s):")
            for t in tasks:
                print(f"  {t.id}: {t.title}")

    elif args.command == "report":
        em = ExecutiveManager()
        rpt = em.generate_ceo_report()
        print(rpt.content_markdown)

    elif args.command == "approvals":
        em = ExecutiveManager()
        if args.appr_command == "list":
            conn = em.governance.db_path and em.task_manager.db_path
            from harmage.db import get_connection
            conn = get_connection(em.db_path)
            cur = conn.cursor()
            cur.execute("SELECT * FROM approval_requests WHERE status = 'pending'")
            rows = cur.fetchall()
            conn.close()
            from harmage.models import ApprovalRequest
            apprs = [ApprovalRequest.from_row(r) for r in rows]
            print(f"Pending approvals: {len(apprs)}")
            for a in apprs:
                print(f"[{a.id}] {a.action_type.value}: {a.description} (by {a.requested_by})")
        elif args.appr_command == "resolve":
            if not args.approve and not args.reject:
                print("Error: Specify either --approve or --reject")
                sys.exit(1)
            res = em.governance.resolve_approval(args.id, approved=args.approve, ceo_notes=args.notes)
            if res:
                print(f"Approval {args.id} resolved: {res.status}")
            else:
                print(f"Approval {args.id} not found.")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
