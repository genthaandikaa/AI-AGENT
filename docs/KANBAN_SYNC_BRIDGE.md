# Harmage Backend <-> Hermes Native Kanban Sync Bridge

## 1. Overview
The **Harmage Kanban Sync Bridge** (`harmage/kanban_sync_bridge.py`) synchronizes autonomous AI tasks between:
* **Harmage Autonomous Backend**: Port `9200` (`http://127.0.0.1:9200/api/tasks`)
* **Hermes Native Kanban Dashboard**: Port `9119` (`http://127.0.0.1:9119/kanban`, SQLite `kanban.db`)
* **Hermes3D Virtual Office**: Port `3000` (`http://localhost:3000/office`)

This guarantees a single source of truth across all dashboards and platforms without duplicate cards or desynchronized task statuses.

---

## 2. Status & Priority Mapping

### Status Matrix
| Harmage Status | Hermes Native Kanban Column | Semantic Meaning |
| :--- | :--- | :--- |
| `queued` / `triage` | `Todo` / `Triage` | In queue, awaiting worker dispatch |
| `in_progress` | `Running` (In Progress) | Actively being executed by assigned agent |
| `completed` | `Done` | Completed with verification evidence |
| `blocked` | `Blocked` | Awaiting human approval or dependencies |
| `review` | `Review` | Execution finished, undergoing inspection |

### Priority Matrix
| Harmage Priority | Kanban Priority Integer |
| :--- | :--- |
| `critical` / `urgent` | `3` (Critical) |
| `high` / `p1` | `2` (High) |
| `medium` / `p2` / `normal` | `1` (Normal) |
| `low` / `p3` | `0` (Low) |

---

## 3. How to Run

### Run Once (Ad-hoc check)
```bash
python -m harmage.kanban_sync_bridge --once
```

### Run as Persistent Background Daemon
```bash
python -m harmage.kanban_sync_bridge --interval 10
```

### Options
* `--interval <seconds>`: Poll interval (default: 10s)
* `--harmage-url <url>`: Harmage API URL (default: `http://127.0.0.1:9200`)
* `--kanban-db <path>`: Hermes SQLite database path (default: `%LOCALAPPDATA%\hermes\kanban.db`)
* `--no-reverse`: Disable reverse synchronization from Hermes Kanban to Harmage

---

## 4. Key Architectural Guarantees
1. **Idempotency**: All tasks are linked via `idempotency_key = <Harmage Task ID>` (e.g. `TSK-AGI-xxxxxx`, `TSK-TT-01`). Restarting the daemon never creates duplicates.
2. **Reverse Sync**: If an operator manually moves a card on the `:9119` Kanban UI to `Done` or `Blocked`, the bridge automatically notifies Harmage backend via `POST /api/tasks/{task_id}/status`.
3. **Resilience**: If the FastAPI backend is temporarily unreachable, the bridge falls back directly to `harmage_operations.db`.
