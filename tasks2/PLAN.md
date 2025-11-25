# Task 2 Plan – PKMS & Task Manager Foundations

## Objective
Move from planning to executable Python modules that persist knowledge entries and tasks, satisfying the assignment’s requirement for stateful PKMS and task management.

## Inputs
- Task 1 artifacts (vision, data model, sample data).
- SQLite mandate (JSON/SQLite/Neo4J allowed; SQLite chosen for portability).

## Steps
1. Define configuration constants (paths, enums) in `config.py`.
2. Implement dataclasses for knowledge entries, tasks, chat messages, and portal records (`models.py`).
3. Build `Storage` with SQLite migrations and CRUD helpers.
4. Create the `KnowledgeBase` service for add/list/search (with fuzzy scoring).
5. Create the `TaskManager` service for CRUD + follow-up generation.
6. Smoke test by adding entries/tasks directly via Python shell.

## Deliverables
- `src/campus_connect_portal/config.py`
- `src/campus_connect_portal/models.py`
- `src/campus_connect_portal/storage.py`
- `src/campus_connect_portal/pkms.py`
- `src/campus_connect_portal/tasks.py`

## Evidence
Running a short Python snippet (documented in the README) successfully inserts and fetches entries/tasks from SQLite, confirming the persistence layer works before the CLI is added.
