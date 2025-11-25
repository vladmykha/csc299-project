# Task 3 Plan – CLI Workflows & Sample Data

## Objective
Expose the PKMS/task services through a friendly CLI, bundle sample data, and document workflows so instructors can exercise the system easily.

## Inputs
- Task 2 storage/services.
- Sample Campus Connect JSON from Task 1.

## Steps
1. Design CLI command surface that mirrors assignment requirements.
2. Implement `cli.py` using `argparse` (preferred for zero dependencies).
3. Add subcommands for init, note CRUD, task CRUD, seeding, and chat launcher stub.
4. Package the sample dataset via `importlib.resources`.
5. Write `docs/USAGE.md` covering environment setup, seeding, PKMS, tasks, and chat.
6. Run CLI smoke tests (init-db, seed, list commands).

## Deliverables
- `src/campus_connect_portal/cli.py`
- `src/campus_connect_portal/sample_data/campus_connect_sample.json`
- `docs/USAGE.md`

## Evidence
Executing the smoke test script (see README and tasks3 README) produces the expected console output: DB creation, seed summary, populated note/task lists.
