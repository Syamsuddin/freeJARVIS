"""Akses data eksplisit (SQL berparameter, tanpa ORM — docs/09)."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from pathlib import Path

import aiosqlite

from jarvisd.store.db import utc_now


@dataclass(frozen=True)
class Project:
    id: int
    name: str
    path: Path
    last_session_id: int | None
    # `sdk_session_id` dari `last_session_id`, untuk `resume`.
    resume_id: str | None


_PROJECT_SELECT = """
SELECT p.id, p.name, p.path, p.last_session_id, s.sdk_session_id
FROM projects p LEFT JOIN sessions s ON s.id = p.last_session_id
"""


def _project(row: aiosqlite.Row) -> Project:
    return Project(
        id=row[0],
        name=row[1],
        path=Path(row[2]),
        last_session_id=row[3],
        resume_id=row[4],
    )


class ProjectRepository:
    def __init__(self, conn: aiosqlite.Connection) -> None:
        self._conn = conn

    async def add(self, name: str, path: Path) -> Project:
        """Daftarkan proyek; path disimpan absolut & ter-resolve (docs/21)."""
        resolved = await asyncio.to_thread(lambda: path.expanduser().resolve())
        async with self._conn.execute(
            "INSERT INTO projects (name, path, created_at) VALUES (?, ?, ?) RETURNING id",
            (name, str(resolved), utc_now()),
        ) as cur:
            row = await cur.fetchone()
        await self._conn.commit()
        project = await self.get(int(row[0])) if row else None
        if project is None:
            raise RuntimeError(f"proyek {name} gagal disimpan")
        return project

    async def get(self, project_id: int) -> Project | None:
        async with self._conn.execute(_PROJECT_SELECT + " WHERE p.id = ?", (project_id,)) as cur:
            row = await cur.fetchone()
        return _project(row) if row else None

    async def get_by_name(self, name: str) -> Project | None:
        """Cocok persis tanpa membedakan huruf (kolom `COLLATE NOCASE`)."""
        async with self._conn.execute(_PROJECT_SELECT + " WHERE p.name = ?", (name,)) as cur:
            row = await cur.fetchone()
        return _project(row) if row else None

    async def list_all(self) -> list[Project]:
        async with self._conn.execute(_PROJECT_SELECT + " ORDER BY p.name") as cur:
            rows = await cur.fetchall()
        return [_project(row) for row in rows]

    async def mark_opened(self, project_id: int) -> None:
        await self._conn.execute(
            "UPDATE projects SET opened_at = ? WHERE id = ?", (utc_now(), project_id)
        )
        await self._conn.commit()


class SessionRepository:
    def __init__(self, conn: aiosqlite.Connection) -> None:
        self._conn = conn

    async def record(self, project_id: int, sdk_session_id: str) -> int:
        """Catat/sentuh sesi SDK dan jadikan sesi terakhir proyek; kembalikan `sessions.id`."""
        now = utc_now()
        await self._conn.execute(
            """
            INSERT INTO sessions (project_id, sdk_session_id, started_at, last_active_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT (sdk_session_id) DO UPDATE SET last_active_at = excluded.last_active_at
            """,
            (project_id, sdk_session_id, now, now),
        )
        async with self._conn.execute(
            "SELECT id, project_id FROM sessions WHERE sdk_session_id = ?", (sdk_session_id,)
        ) as cur:
            row = await cur.fetchone()
        if row is None:
            raise RuntimeError(f"sesi {sdk_session_id} gagal disimpan")
        if row[1] != project_id:
            await self._conn.rollback()
            raise ValueError(f"sesi {sdk_session_id} milik proyek lain")
        await self._conn.execute(
            "UPDATE projects SET last_session_id = ? WHERE id = ?", (row[0], project_id)
        )
        await self._conn.commit()
        return int(row[0])
