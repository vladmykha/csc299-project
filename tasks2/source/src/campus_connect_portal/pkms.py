"""Personal Knowledge Management System helpers."""

from __future__ import annotations

from difflib import SequenceMatcher
from typing import Iterable

from .models import KnowledgeEntry
from .storage import Storage


class KnowledgeBase:
    """CRUD, tagging, and search around Campus Connect notes."""

    def __init__(self, storage: Storage | None = None):
        self.storage = storage or Storage()

    def add_entry(
        self,
        *,
        title: str,
        content: str,
        tags: Iterable[str] | None = None,
        campus_area: str | None = None,
        source: str | None = None,
    ) -> KnowledgeEntry:
        entry = KnowledgeEntry(
            title=title.strip(),
            content=content.strip(),
            tags=list(tags or []),
            campus_area=campus_area or "Other",
            source=source,
        )
        self.storage.upsert_knowledge(entry.to_row())
        return entry

    def list_entries(self, limit: int = 20) -> list[KnowledgeEntry]:
        rows = self.storage.fetch_knowledge(limit=limit)
        return [KnowledgeEntry.from_row(row) for row in rows]

    def search(self, query: str, limit: int = 3) -> list[KnowledgeEntry]:
        query = query.strip()
        if not query:
            return []
        rows = self.storage.fetch_knowledge(limit=200)
        scored: list[tuple[float, KnowledgeEntry]] = []
        for row in rows:
            entry = KnowledgeEntry.from_row(row)
            score = self._score_entry(entry, query)
            if score > 0:
                scored.append((score, entry))
        scored.sort(key=lambda item: item[0], reverse=True)
        return [entry for _, entry in scored[:limit]]

    def _score_entry(self, entry: KnowledgeEntry, query: str) -> float:
        title_hit = 3.0 if query.lower() in entry.title.lower() else 0.0
        tag_hit = 2.0 if any(query.lower() in tag.lower() for tag in entry.tags) else 0.0
        matcher = SequenceMatcher(None, entry.content.lower(), query.lower())
        fuzz = matcher.ratio() * 2.0
        campus_bonus = 1.0 if entry.campus_area in ("Grades", "Financial Aid") else 0.0
        return title_hit + tag_hit + fuzz + campus_bonus
