"""Command-line interface for the Campus Connect assistant."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

from .chat import ChatSession
from .models import PortalRecord
from .pkms import KnowledgeBase
from .storage import Storage
from .tasks import TaskManager


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="campus-connect-cli",
        description="Campus Connect PKMS, task manager, and AI chat interface.",
    )
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("init-db", help="Initialize the SQLite database.")

    add_note = sub.add_parser("add-note", help="Create a knowledge entry.")
    add_note.add_argument("--title", required=True)
    add_note.add_argument("--content", help="Raw content string.")
    add_note.add_argument("--from-file", type=Path, help="Path to a file containing the note.")
    add_note.add_argument("--tags", default="", help="Comma-separated tags.")
    add_note.add_argument("--campus-area", default="Other")
    add_note.add_argument("--source", help="e.g., Campus Connect > Grades > Fall 2025.")

    list_notes = sub.add_parser("list-notes", help="List stored knowledge entries.")
    list_notes.add_argument("--limit", type=int, default=10)

    search_notes = sub.add_parser("search-notes", help="Search within knowledge entries.")
    search_notes.add_argument("--query", required=True)
    search_notes.add_argument("--limit", type=int, default=3)

    add_task = sub.add_parser("add-task", help="Create a task.")
    add_task.add_argument("--title", required=True)
    add_task.add_argument("--description", required=True)
    add_task.add_argument("--status", default="todo")
    add_task.add_argument("--priority", default="medium")
    add_task.add_argument("--due-date")
    add_task.add_argument("--related-entry-id")

    list_tasks = sub.add_parser("list-tasks", help="List tasks.")
    list_tasks.add_argument("--status", choices=["todo", "in_progress", "blocked", "done"])
    list_tasks.add_argument("--limit", type=int, default=10)

    update_task = sub.add_parser("update-task", help="Update a task.")
    update_task.add_argument("task_id")
    update_task.add_argument("--title")
    update_task.add_argument("--description")
    update_task.add_argument("--status")
    update_task.add_argument("--priority")
    update_task.add_argument("--due-date")

    sub.add_parser("chat", help="Start the terminal chat interface.")

    seed = sub.add_parser("seed", help="Import Campus Connect sample data.")
    seed.add_argument("--file", type=Path, help="Path to JSON file exported from Campus Connect.")
    seed.add_argument(
        "--sample",
        action="store_true",
        help="Load the built-in sample dataset instead of providing a file.",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    command = args.command
    if not command:
        parser.print_help()
        return 1
    try:
        handler = COMMANDS[command]
    except KeyError:
        parser.error(f"Unknown command: {command}")
        return 1
    return handler(args)


def cmd_init_db(_: argparse.Namespace) -> int:
    Storage()  # instantiation ensures migrations run
    print("Database ready at ~/.campus_connect_portal/state.db")
    return 0


def cmd_add_note(args: argparse.Namespace) -> int:
    content = _resolve_content(args)
    kb = KnowledgeBase()
    entry = kb.add_entry(
        title=args.title,
        content=content,
        tags=[tag.strip() for tag in args.tags.split(",") if tag.strip()],
        campus_area=args.campus_area,
        source=args.source,
    )
    print(f"Created entry {entry.id} with tags {entry.tags or ['untagged']}")
    return 0


def cmd_list_notes(args: argparse.Namespace) -> int:
    kb = KnowledgeBase()
    entries = kb.list_entries(limit=args.limit)
    if not entries:
        print("No knowledge entries yet. Add one with `add-note`.")
        return 0
    for entry in entries:
        print(f"[{entry.id}] {entry.title} — tags: {', '.join(entry.tags) or 'untagged'}")
    return 0


def cmd_search_notes(args: argparse.Namespace) -> int:
    kb = KnowledgeBase()
    entries = kb.search(args.query, limit=args.limit)
    if not entries:
        print("No matching knowledge entries. Try adding more context.")
        return 0
    for entry in entries:
        preview = entry.content[:120].replace("\n", " ")
        print(f"[{entry.id}] {entry.title}: {preview}...")
    return 0


def cmd_add_task(args: argparse.Namespace) -> int:
    manager = TaskManager()
    task = manager.add_task(
        title=args.title,
        description=args.description,
        status=args.status,
        priority=args.priority,
        due_date=args.due_date,
        related_entry_id=args.related_entry_id,
    )
    print(f"Created task {task.id} (status={task.status}, priority={task.priority})")
    return 0


def cmd_list_tasks(args: argparse.Namespace) -> int:
    manager = TaskManager()
    tasks = manager.list_tasks(status=args.status, limit=args.limit)
    if not tasks:
        print("No tasks found.")
        return 0
    for task in tasks:
        print(
            f"[{task.id}] {task.title} — {task.status} / {task.priority}"
            + (f" (due {task.due_date})" if task.due_date else "")
        )
    return 0


def cmd_update_task(args: argparse.Namespace) -> int:
    manager = TaskManager()
    task = manager.update_task(
        task_id=args.task_id,
        title=args.title,
        description=args.description,
        status=args.status,
        priority=args.priority,
        due_date=args.due_date,
    )
    print(f"Updated task {task.id}: status={task.status}, priority={task.priority}")
    return 0


def cmd_chat(_: argparse.Namespace) -> int:
    session = ChatSession()
    session.interact()
    return 0


def cmd_seed(args: argparse.Namespace) -> int:
    data = _load_seed_data(args)
    records = [PortalRecord.from_dict(item) for item in data]
    storage = Storage()
    storage.upsert_portal_records(record.to_row() for record in records)
    kb = KnowledgeBase(storage=storage)
    manager = TaskManager(storage=storage)
    for record in records:
        kb.add_entry(
            title=f"{record.component} ({record.campus_area})",
            content=record.notes or "Imported from Campus Connect snapshot.",
            tags=[
                slugify(record.campus_area),
                slugify(record.course or "general"),
            ],
            campus_area=record.campus_area,
            source="Campus Connect import",
        )
    created_tasks = manager.ensure_follow_up_tasks(records)
    print(f"Imported {len(records)} records and created {len(created_tasks)} tasks.")
    return 0


def _resolve_content(args: argparse.Namespace) -> str:
    if args.content:
        return args.content
    if args.from_file:
        return args.from_file.read_text(encoding="utf-8")
    raise SystemExit("Either --content or --from-file must be provided.")


def _load_seed_data(args: argparse.Namespace) -> list[dict[str, Any]]:
    if args.sample:
        import importlib.resources as resources

        sample = resources.files("campus_connect_portal.sample_data").joinpath(
            "campus_connect_sample.json"
        )
        return json.loads(sample.read_text(encoding="utf-8"))
    if args.file and args.file.exists():
        return json.loads(args.file.read_text(encoding="utf-8"))
    raise SystemExit("Provide --file PATH or --sample.")


def slugify(value: str) -> str:
    return value.lower().replace(" ", "-")


COMMANDS = {
    "init-db": cmd_init_db,
    "add-note": cmd_add_note,
    "list-notes": cmd_list_notes,
    "search-notes": cmd_search_notes,
    "add-task": cmd_add_task,
    "list-tasks": cmd_list_tasks,
    "update-task": cmd_update_task,
    "chat": cmd_chat,
    "seed": cmd_seed,
}


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
