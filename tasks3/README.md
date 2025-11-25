# Task 3 – CLI Workflows & Sample Data

Task 3 bundles the storage-backed services into an installable CLI that mirrors Campus Connect workflows and seeds the database with realistic data.

## Goals
- Provide a Typer/argparse-style CLI entry point (`campus-connect-cli`).
- Cover commands for PKMS, task tracking, seeding, and chat.
- Package sample JSON data and usage docs so graders can run the tool quickly.

## Key Artifacts

| Deliverable | Location | Notes |
| --- | --- | --- |
| CLI entry point | `src/campus_connect_portal/cli.py` | Subcommands: `init-db`, `add-note`, `list-notes`, `search-notes`, `add-task`, `list-tasks`, `update-task`, `seed`, `chat`. |
| Sample dataset | `src/campus_connect_portal/sample_data/campus_connect_sample.json` | Bundled via `tool.setuptools.package-data`. |
| Usage guide | `docs/USAGE.md` | Step-by-step setup, workflows, and regression checklist. |
| Seed script | `campus-connect-cli seed --sample` | Imports dataset, creates knowledge entries, auto-generates follow-up tasks. |

## Smoke test
```bash
PYTHONPATH=src python3 -m campus_connect_portal.cli init-db
PYTHONPATH=src python3 -m campus_connect_portal.cli seed --sample
PYTHONPATH=src python3 -m campus_connect_portal.cli list-notes
PYTHONPATH=src python3 -m campus_connect_portal.cli list-tasks
```

## Verification checklist
- [x] CLI help shows all subcommands.
- [x] Seeding prints “Imported 3 records and created 2 tasks.”
- [x] `list-notes`/`list-tasks` output matches the sample dataset.
- [x] Usage guide documents all workflows and manual tests.
