"""Dataclasses shared across the Campus Connect assistant modules."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Sequence
from uuid import uuid4


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _coerce_tags(raw_tags: Sequence[str] | str | None) -> list[str]:
    if raw_tags is None:
        return []
    if isinstance(raw_tags, str):
        tokens = [part.strip() for part in raw_tags.split(",")]
    else:
        tokens = [str(part).strip() for part in raw_tags]
    return sorted({token for token in tokens if token})


@dataclass(slots=True)
class KnowledgeEntry:
    """Structured note captured from Campus Connect or related sources."""

    title: str
    content: str
    tags: list[str] = field(default_factory=list)
    campus_area: str = "Other"
    source: str | None = None
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: str = field(default_factory=_now_iso)
    updated_at: str = field(default_factory=_now_iso)

    def to_row(self) -> tuple:
        return (
            self.id,
            self.title,
            self.content,
            ",".join(self.tags),
            self.campus_area,
            self.source,
            self.created_at,
            self.updated_at,
        )

    @classmethod
    def from_row(cls, row) -> "KnowledgeEntry":
        return cls(
            id=row["id"],
            title=row["title"],
            content=row["content"],
            tags=_coerce_tags(row["tags"]),
            campus_area=row["campus_area"],
            source=row["source"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )


@dataclass(slots=True)
class Task:
    """Task tracked alongside knowledge entries."""

    title: str
    description: str
    status: str = "todo"
    priority: str = "medium"
    due_date: str | None = None
    related_entry_id: str | None = None
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: str = field(default_factory=_now_iso)
    updated_at: str = field(default_factory=_now_iso)

    def to_row(self) -> tuple:
        return (
            self.id,
            self.title,
            self.description,
            self.status,
            self.priority,
            self.due_date,
            self.related_entry_id,
            self.created_at,
            self.updated_at,
        )

    @classmethod
    def from_row(cls, row) -> "Task":
        return cls(
            id=row["id"],
            title=row["title"],
            description=row["description"],
            status=row["status"],
            priority=row["priority"],
            due_date=row["due_date"],
            related_entry_id=row["related_entry_id"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )


@dataclass(slots=True)
class ChatMessage:
    """Message belonging to a chat session."""

    session_id: str
    role: str
    content: str
    citations: list[str] = field(default_factory=list)
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: str = field(default_factory=_now_iso)

    def to_row(self) -> tuple:
        citations_str = ",".join(self.citations)
        return (
            self.id,
            self.session_id,
            self.role,
            self.content,
            citations_str,
            self.created_at,
        )


@dataclass(slots=True)
class PortalRecord:
    """Raw Campus Connect snapshot entry."""

    record_id: str
    course: str | None
    component: str
    grade: str | None
    points: str | None
    campus_area: str
    needs_follow_up: bool
    notes: str | None = None
    updated_at: str = field(default_factory=_now_iso)
    id: str = field(default_factory=lambda: str(uuid4()))

    def to_row(self) -> tuple:
        return (
            self.id,
            self.record_id,
            self.course,
            self.component,
            self.grade,
            self.points,
            self.campus_area,
            int(self.needs_follow_up),
            self.notes,
            self.updated_at,
        )

    @classmethod
    def from_dict(cls, payload: dict) -> "PortalRecord":
        return cls(
            record_id=payload["record_id"],
            course=payload.get("course"),
            component=payload["component"],
            grade=payload.get("grade"),
            points=payload.get("points"),
            campus_area=payload.get("campus_area", "Grades"),
            needs_follow_up=bool(payload.get("needs_follow_up", False)),
            notes=payload.get("notes"),
            updated_at=payload.get("updated_at", _now_iso()),
        )
