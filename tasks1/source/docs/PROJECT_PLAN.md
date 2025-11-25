# Campus Connect Grading Portal Interface — Project Plan

_Last updated: Nov 25, 2025_

## Vision

Build a portable, AI-assisted command line tool that helps DePaul students keep Campus Connect grades, advising notes, and administrative tasks organized from any terminal. The experience should feel like a lightweight personal CRM that:

- Captures structured knowledge from portal screenshots, advisor emails, or transcripts.
- Turns important portal updates into actionable tasks.
- Lets the student chat about their data (“What courses still have missing grades?”) and get answers that cite stored knowledge/tasks.
- Provides hooks for future automation (browser automation, email triage) without requiring them yet.

## Scope & deliverables

Deliverable | Details
:--|:--
Python package | `campus_connect_portal` package published in this repo (no external services required to run).
PKMS | CRUD operations, tagging, search, and CSV/JSON export powered by SQLite.
Task manager | Kanban-friendly statuses, due dates, priority, reminders derived from knowledge entries.
Terminal chat | REPL accessible through `campus-connect-cli chat`, streams responses, cites sources.
AI agents | KnowledgeAgent, TaskAgent, and CampusConnectAgent orchestrated by `llm.py`, optional OpenAI integration.
State storage | SQLite database at `~/.campus_connect_portal/state.db` plus JSON import/export utilities.
Documentation | README, this plan, sample data walkthrough.

## Architecture

Component | Responsibility
:--|:--
`config.py` | Path management, constants (DB path, default tags).
`models.py` | Dataclasses (`KnowledgeEntry`, `Task`, `ChatMessage`, `PortalRecord`).
`storage.py` | SQLite connection pool, migrations, helpers for CRUD queries.
`pkms.py` | KnowledgeBase service layer (validation, tagging, search scoring).
`tasks.py` | TaskManager service layer (status transitions, reminders).
`llm.py` | Abstract LLM client (OpenAI + heuristic fallback).
`agents.py` | Domain-specific agents that fetch context and craft prompts.
`chat.py` | Chat session orchestration, transcript logging.
`cli.py` | Typer/argparse-based entry point with subcommands.

## Data model

Table | Columns | Notes
:--|:--|:--
`knowledge_entries` | `id`, `title`, `content`, `tags`, `campus_area`, `source`, `created_at`, `updated_at` | Tags stored as comma-separated string; campus_area enumerates modules (Grades, Financial Aid, Advising, Registration).
`tasks` | `id`, `title`, `description`, `status`, `priority`, `due_date`, `related_entry_id`, `created_at`, `updated_at` | `status` constrained to `todo`, `in_progress`, `blocked`, `done`.
`chat_messages` | `id`, `session_id`, `role`, `content`, `citations`, `created_at` | `citations` = JSON array of knowledge/task ids used in the response.
`portal_records` | `id`, `course`, `component`, `grade`, `updated_at`, `notes` | Optional sync table for raw Campus Connect dumps.

## Key workflows

1. **Capture note from Campus Connect**
   1. Student copies grade-table snippet into clipboard.
   2. Runs `campus-connect-cli add-note --title "CSC 394 Midterm" --tags "grades,csc394" --content "$(pbpaste)"`.
   3. CLI validates tags, saves to SQLite, optionally links to existing task.

2. **Auto-create task from new grade record**
   1. `campus-connect-cli sync --source-file data/campus_connect_sample.json`.
   2. Sync job inserts/updates rows in `portal_records`.
   3. For each record flagged `needs_follow_up`, TaskManager creates `Task` pointing back to the knowledge entry.

3. **Chat about outstanding grades**
   1. User runs `campus-connect-cli chat`.
   2. Query routed through KnowledgeAgent (top 3 entries) and TaskAgent (top incomplete tasks).
   3. Prompt assembled and passed to LLM client.
   4. Response printed with citations; transcript stored.

## AI integration strategy

- Default to deterministic heuristic summarizer (extract key sentences, highlight deadlines).
- When `OPENAI_API_KEY` is available, call OpenAI Responses API (model default: `gpt-4o-mini`).
- Agents craft prompts like:

```
You are a DePaul student success coach. Combine the knowledge entries and tasks below to answer the user's question.
- Highlight deadlines and grade risks.
- Suggest one actionable next step.
Return JSON with `answer` and `suggested_actions`.
```

## Milestones

1. **Scaffold (today)** — repo setup, docs, packaging ✅
2. **Core services** — storage, models, PKMS, tasks
3. **Chat experience** — agents, LLM integration, REPL
4. **Campus Connect sync** — JSON import, sample dataset
5. **Polish** — tests, CI, expanded docs

## Risks & mitigations

- **No official API access** → rely on manual exports and provide hooks for browser automation later.
- **LLM unavailability** → heuristic summarizer ensures offline functionality.
- **Data privacy** → state file stays local; CLI warns before using remote AI providers.
- **Time constraints** → prioritize CLI workflows first, leave GUI or browser automation for stretch goals.

## Next steps

- Implement storage/models (Milestone 2).
- Create CLI subcommands for PKMS + tasks.
- Build chat session + AI fallback.
- Validate sample sync path end-to-end.
