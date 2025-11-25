"""SQLite-backed persistence for the Campus Connect assistant."""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterable, Iterator, Sequence

from .config import DB_PATH


class Storage:
    """Lightweight wrapper around SQLite with helper queries."""

    def __init__(self, db_path: Path | str = DB_PATH):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._migrate()

    @contextmanager
    def connection(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def _migrate(self) -> None:
        with self.connection() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS knowledge_entries (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    tags TEXT,
                    campus_area TEXT,
                    source TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS tasks (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    status TEXT NOT NULL,
                    priority TEXT NOT NULL,
                    due_date TEXT,
                    related_entry_id TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (related_entry_id) REFERENCES knowledge_entries(id) ON DELETE SET NULL
                );

                CREATE TABLE IF NOT EXISTS chat_messages (
                    id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    citations TEXT,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS portal_records (
                    id TEXT PRIMARY KEY,
                    record_id TEXT NOT NULL,
                    course TEXT,
                    component TEXT NOT NULL,
                    grade TEXT,
                    points TEXT,
                    campus_area TEXT,
                    needs_follow_up INTEGER NOT NULL DEFAULT 0,
                    notes TEXT,
                    updated_at TEXT NOT NULL
                );
                """
            )

    # Knowledge helpers -------------------------------------------------

    def upsert_knowledge(self, entry_row: Sequence) -> None:
        with self.connection() as conn:
            conn.execute(
                """
                INSERT INTO knowledge_entries (
                    id, title, content, tags, campus_area, source, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    title=excluded.title,
                    content=excluded.content,
                    tags=excluded.tags,
                    campus_area=excluded.campus_area,
                    source=excluded.source,
                    created_at=excluded.created_at,
                    updated_at=excluded.updated_at;
                """,
                entry_row,
            )

    def fetch_knowledge(self, limit: int = 50) -> list[sqlite3.Row]:
        with self.connection() as conn:
            cur = conn.execute(
                """
                SELECT * FROM knowledge_entries
                ORDER BY updated_at DESC
                LIMIT ?
                """,
                (limit,),
            )
            return list(cur.fetchall())

    def fetch_knowledge_by_ids(self, ids: Sequence[str]) -> list[sqlite3.Row]:
        if not ids:
            return []
        placeholders = ",".join("?" for _ in ids)
        with self.connection() as conn:
            cur = conn.execute(
                f"SELECT * FROM knowledge_entries WHERE id IN ({placeholders})",
                tuple(ids),
            )
            rows = cur.fetchall()
        rows_by_id = {row["id"]: row for row in rows}
        return [rows_by_id[row_id] for row_id in ids if row_id in rows_by_id]

    # Task helpers ------------------------------------------------------

    def upsert_task(self, task_row: Sequence) -> None:
        with self.connection() as conn:
            conn.execute(
                """
                INSERT INTO tasks (
                    id, title, description, status, priority, due_date,
                    related_entry_id, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    title=excluded.title,
                    description=excluded.description,
                    status=excluded.status,
                    priority=excluded.priority,
                    due_date=excluded.due_date,
                    related_entry_id=excluded.related_entry_id,
                    created_at=excluded.created_at,
                    updated_at=excluded.updated_at;
                """,
                task_row,
            )

    def fetch_tasks(self, status: str | None = None, limit: int = 50) -> list[sqlite3.Row]:
        query = """
            SELECT * FROM tasks
        """
        params: list = []
        if status:
            query += " WHERE status = ?"
            params.append(status)
        query += " ORDER BY updated_at DESC LIMIT ?"
        params.append(limit)
        with self.connection() as conn:
            cur = conn.execute(query, tuple(params))
            return list(cur.fetchall())

    def fetch_task(self, task_id: str):
        with self.connection() as conn:
            cur = conn.execute(
                "SELECT * FROM tasks WHERE id = ?",
                (task_id,),
            )
            return cur.fetchone()

    def fetch_task_by_title(self, title: str):
        with self.connection() as conn:
            cur = conn.execute(
                "SELECT * FROM tasks WHERE title = ?",
                (title,),
            )
            return cur.fetchone()

    # Chat logging ------------------------------------------------------

    def insert_chat_message(self, message_row: Sequence) -> None:
        with self.connection() as conn:
            conn.execute(
                """
                INSERT INTO chat_messages (
                    id, session_id, role, content, citations, created_at
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                message_row,
            )

    def fetch_chat_history(self, session_id: str, limit: int = 20) -> list[sqlite3.Row]:
        with self.connection() as conn:
            cur = conn.execute(
                """
                SELECT * FROM chat_messages
                WHERE session_id = ?
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (session_id, limit),
            )
            return list(cur.fetchall())

    # Portal sync -------------------------------------------------------

    def upsert_portal_records(self, record_rows: Iterable[Sequence]) -> int:
        count = 0
        with self.connection() as conn:
            conn.executemany(
                """
                INSERT INTO portal_records (
                    id, record_id, course, component, grade, points,
                    campus_area, needs_follow_up, notes, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    record_id=excluded.record_id,
                    course=excluded.course,
                    component=excluded.component,
                    grade=excluded.grade,
                    points=excluded.points,
                    campus_area=excluded.campus_area,
                    needs_follow_up=excluded.needs_follow_up,
                    notes=excluded.notes,
                    updated_at=excluded.updated_at;
                """,
                list(record_rows),
            )
            count = conn.total_changes
        return count
