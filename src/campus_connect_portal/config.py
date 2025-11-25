"""Central configuration for the Campus Connect portal assistant."""

from __future__ import annotations

from pathlib import Path
import os

APP_NAME = "campus_connect_portal"

STATE_DIR = Path(
    os.getenv("CAMPUS_CONNECT_STATE_DIR", Path.home() / ".campus_connect_portal")
)
STATE_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = STATE_DIR / "state.db"

DEFAULT_CHAT_MODEL = os.getenv("CAMPUS_CONNECT_CHAT_MODEL", "gpt-4o-mini")
MAX_CHAT_CONTEXT = int(os.getenv("CAMPUS_CONNECT_MAX_CHAT_CONTEXT", "5"))

TASK_STATUSES = ("todo", "in_progress", "blocked", "done")
TASK_PRIORITIES = ("low", "medium", "high", "critical")

KNOWLEDGE_CAMPUS_AREAS = (
    "Grades",
    "Financial Aid",
    "Advising",
    "Registration",
    "Student Accounts",
    "Other",
)
