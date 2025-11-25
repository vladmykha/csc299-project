# Usage & Testing Guide

This document captures the daily-driver workflows for the Campus Connect Grading Portal Interface plus quick manual tests you can run to verify each feature.

## Environment setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[llm]"  # or pip install -e .
export PYTHONPATH=src  # optional when running directly from the repo
```

Set `OPENAI_API_KEY` if you want the chat agent to call OpenAI. Otherwise it falls back to the deterministic summarizer.

## Initialize the state database

```bash
python3 -m campus_connect_portal.cli init-db
```

This creates `~/.campus_connect_portal/state.db` with tables for knowledge entries, tasks, chat transcripts, and portal records.

## Seed the database (optional)

Load the bundled sample dataset:

```bash
python3 -m campus_connect_portal.cli seed --sample
```

Or import your own JSON export:

```bash
python3 -m campus_connect_portal.cli seed --file path/to/export.json
```

The seed command:
- Stores the raw portal records.
- Creates knowledge entries for each record.
- Generates follow-up tasks for items flagged `needs_follow_up: true`.

## PKMS workflows

### Add a note

```bash
python3 -m campus_connect_portal.cli add-note \
  --title "CSC 299 Project Feedback" \
  --content "Remember to document AI planning steps." \
  --tags "csc299,grades" \
  --campus-area "Grades" \
  --source "Campus Connect > Grades > Fall 2025"
```

### List or search notes

```bash
python3 -m campus_connect_portal.cli list-notes --limit 5
python3 -m campus_connect_portal.cli search-notes --query "financial aid" --limit 2
```

## Task workflows

```bash
python3 -m campus_connect_portal.cli add-task \
  --title "Appeal CSC 394 rubric change" \
  --description "Email Prof. Chastain with concerns" \
  --priority high \
  --due-date 2025-11-30

python3 -m campus_connect_portal.cli list-tasks --status todo
python3 -m campus_connect_portal.cli update-task TASK_ID --status in_progress
```

## Chat interface

Run the REPL:

```bash
python3 -m campus_connect_portal.cli chat
```

Example session (offline mode):

```
you> What should I follow up on before finals?
assistant> Knowledge insights: [CSC394] Assignment 4 (Grades): instructor flagged rubric change ..., Suggested tasks: Follow up: Assignment 4 — todo / medium.
actions:
  - Advance task 'Follow up: Loan Entrance Counseling' (status: todo)
  - Advance task 'Follow up: Assignment 4' (status: todo)
citations: 0722d38a-c4cc-4781-b29c-344a89f8baf6, a5b8fdeb-d614-44eb-a937-cdd85472d34d, 2e73ecf3-9038-49ad-8b34-f295850c0978
```

## Regression checklist

- `init-db` completes without errors.
- `seed --sample` reports three records, two tasks.
- `list-notes` shows the imported notes.
- `list-tasks` surfaces the generated follow-ups.
- `add-note` + `list-notes --limit 1` shows the new entry.
- `add-task` + `update-task` reflect changes.
- `chat` displays responses (OpenAI-backed or fallback).

Document successful runs in your course log or GitHub issue tracker.
