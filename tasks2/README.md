# Task 2 – PKMS & Task Manager Foundations

Task 2 demonstrates the first working prototype: a Python package with models, SQLite storage, and domain services for knowledge entries and tasks. Everything is still terminal-driven but now persists data across runs.

## Goals
- Define dataclasses for knowledge entries, tasks, chat logs, and portal records.
- Implement SQLite migrations plus CRUD helpers.
- Provide service layers for the PKMS (`KnowledgeBase`) and task tracking (`TaskManager`).

## Key Artifacts

| Deliverable | Location | Notes |
| --- | --- | --- |
| Package metadata | `pyproject.toml` | Declares CLI entry point and optional OpenAI dependency. |
| Configuration | `src/campus_connect_portal/config.py` | Centralizes DB path, task enums, chat defaults. |
| Data models | `src/campus_connect_portal/models.py` | Slots-based dataclasses with helper serializers. |
| Storage | `src/campus_connect_portal/storage.py` | Handles migrations + CRUD for knowledge, tasks, chat logs, portal snapshots. |
| PKMS service | `src/campus_connect_portal/pkms.py` | Adds list/search logic with fuzzy scoring. |
| Task manager | `src/campus_connect_portal/tasks.py` | Validates status/priority, auto-creates follow-ups from portal records. |

## Manual test script
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
PYTHONPATH=src python3 - <<'PY'
from campus_connect_portal.pkms import KnowledgeBase
kb = KnowledgeBase()
entry = kb.add_entry(title="CSC 299 Feedback", content="Document AI workflow", tags=["csc299"])
print(entry)
PY
```

## Verification checklist
- [x] SQLite database initializes automatically under `~/.campus_connect_portal/`.
- [x] PKMS adds/list/search works in-memory and on disk.
- [x] Task manager enforces valid statuses/priorities and auto-creates follow-ups.
