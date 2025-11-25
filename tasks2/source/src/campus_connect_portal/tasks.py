"""Personal task management utilities."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Iterable

from .config import TASK_PRIORITIES, TASK_STATUSES
from .models import PortalRecord, Task
from .storage import Storage


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class TaskManager:
    """CRUD and automation around Campus Connect follow-up tasks."""

    def __init__(self, storage: Storage | None = None):
        self.storage = storage or Storage()

    def add_task(
        self,
        *,
        title: str,
        description: str,
        status: str = "todo",
        priority: str = "medium",
        due_date: str | None = None,
        related_entry_id: str | None = None,
    ) -> Task:
        self._validate_status(status)
        self._validate_priority(priority)
        task = Task(
            title=title.strip(),
            description=description.strip(),
            status=status,
            priority=priority,
            due_date=due_date,
            related_entry_id=related_entry_id,
        )
        self.storage.upsert_task(task.to_row())
        return task

    def list_tasks(self, status: str | None = None, limit: int = 20) -> list[Task]:
        rows = self.storage.fetch_tasks(status=status, limit=limit)
        return [Task.from_row(row) for row in rows]

    def update_task(
        self,
        task_id: str,
        *,
        title: str | None = None,
        description: str | None = None,
        status: str | None = None,
        priority: str | None = None,
        due_date: str | None = None,
    ) -> Task:
        row = self.storage.fetch_task(task_id)
        if not row:
            raise ValueError(f"Task {task_id} not found")
        task = Task.from_row(row)
        if title:
            task.title = title.strip()
        if description:
            task.description = description.strip()
        if status:
            self._validate_status(status)
            task.status = status
        if priority:
            self._validate_priority(priority)
            task.priority = priority
        if due_date is not None:
            task.due_date = due_date
        task.updated_at = _now_iso()
        self.storage.upsert_task(task.to_row())
        return task

    def ensure_follow_up_tasks(self, records: Iterable[PortalRecord]) -> list[Task]:
        """Create TODOs for portal records that require action."""
        created: list[Task] = []
        for record in records:
            if not record.needs_follow_up:
                continue
            title = f"Follow up: {record.component}"
            existing = self.storage.fetch_task_by_title(title)
            if existing:
                continue
            description = record.notes or f"Review {record.course or 'record'} in Campus Connect."
            task = Task(
                title=title,
                description=description,
                status="todo",
                priority="high" if record.campus_area == "Financial Aid" else "medium",
            )
            self.storage.upsert_task(task.to_row())
            created.append(task)
        return created

    def _validate_status(self, value: str) -> None:
        if value not in TASK_STATUSES:
            raise ValueError(f"Status must be one of {TASK_STATUSES}")

    def _validate_priority(self, value: str) -> None:
        if value not in TASK_PRIORITIES:
            raise ValueError(f"Priority must be one of {TASK_PRIORITIES}")
