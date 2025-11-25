# Campus Connect Grading Portal Interface

Terminal-first personal knowledge management system (PKMS), task tracker, and AI-assisted chat interface designed to help DePaul students keep tabs on Campus Connect updates, grading events, and administrative to-dos.

> **Course link**: https://fpl.cs.depaul.edu/cpitcher/courses/csc299/worksheets/project.html

## Task breakdown

The repo mirrors the five-task structure from the CSC 299 example (`tasks1` … `tasks5`). Each folder documents what changed, why, and how to verify it. See `SUMMARY.md` for a quick index.

## Why this project exists

Campus Connect centralizes grades, registration, and tuition alerts, but it is cumbersome to use on the go. This project provides a portable workflow that:
- Mirrors the information a student normally pulls from Campus Connect.
- Lets the student capture their own notes, advisement summaries, or screenshots as structured PKMS entries.
- Generates and tracks follow-up tasks (e.g., "appeal grade", "meet advisor", "download unofficial transcript").
- Offers a terminal chat interface where AI agents surface the most relevant knowledge/task context and draft responses or study plans.

Everything runs in Python 3.11+, stores state in a local SQLite database, and works on Windows, macOS, and Linux.

## Feature map

- **Personal Knowledge Management System (PKMS)**  
  Add/search/list rich notes tagged by course, professor, quarter, or campus office. Entries store the original source (Campus Connect page, email, advising meeting) and can be exported.

- **Personal Task Management System**  
  Create tasks with statuses (`todo`, `in_progress`, `blocked`, `done`), due dates, priorities, and links back to knowledge entries.

- **Terminal chat interface**  
  `campus-connect-cli chat` launches a conversation loop. The agent retrieves top knowledge/task matches and either calls the OpenAI API (if `OPENAI_API_KEY` is set) or falls back to an offline summarizer.

- **AI agents over knowledge/tasks**  
  - `KnowledgeAgent`: semantic keyword search plus prioritization rules (grade changes, deadlines).  
  - `TaskAgent`: filters actionable tasks, escalates blocked items, and can auto-generate next steps.  
  - `CampusConnectAgent`: orchestrates the above, blends in LLM output, and stores chat transcripts in SQLite for auditability.

- **Campus Connect sync stubs**  
  Import mock grading snapshots (JSON) or your own exports to keep the terminal database aligned with the official portal.

## Project structure

```
.
├── LICENSE
├── README.md
├── pyproject.toml
├── data/
│   └── campus_connect_sample.json
├── docs/
│   ├── PROJECT_PLAN.md
│   ├── MOBILE_LOGIN_MOCK.md
│   └── USAGE.md
└── src/
    └── campus_connect_portal/
        ├── __init__.py
        ├── agents.py
        ├── chat.py
        ├── cli.py
        ├── config.py
        ├── llm.py
        ├── models.py
        ├── pkms.py
        ├── sample_data/
        │   └── campus_connect_sample.json
        ├── storage.py
        └── tasks.py
```

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[llm]"
campus-connect-cli init-db
campus-connect-cli seed --sample
campus-connect-cli list-notes
campus-connect-cli chat
```

Set `OPENAI_API_KEY` if you want live LLM completions. Without it, the chat agent still responds using local heuristics, citing the notes/tasks that matched your query.

See `docs/USAGE.md` for more detailed workflows and a regression checklist. Preview the mobile-first login experience (Pulse-style Campus Connect handoff) in `docs/MOBILE_LOGIN_MOCK.md`.

## Assignment alignment

Requirement | Implementation
:--|:--
Plan/spec via AI tooling | Project plan in `docs/PROJECT_PLAN.md`, generated with GPT-5.1 Codex workflow.
PKMS | `KnowledgeBase` in `pkms.py` with SQLite persistence.
Task manager | `TaskManager` in `tasks.py`.
Terminal chat | `chat.py` + `cli.py chat`.
AI agents over state | `agents.py`, `llm.py`.
Portable Python | Tested with Python 3.11+, standard library only (OpenAI optional).
State in JSON/SQLite/Neo4J | SQLite database at `~/.campus_connect_portal/state.db`.

## Current status

- [x] Repository scaffolded with packaging metadata and MIT License.
- [ ] Core modules implemented.
- [ ] Sample data + CLI workflows verified.
- [ ] Additional polish (tests, docs) as the course project evolves.

Pull requests, issues, and course feedback are welcome!
