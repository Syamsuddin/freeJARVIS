from collections.abc import AsyncIterator
from pathlib import Path

import aiosqlite
import pytest

from jarvisd.store.db import connect
from jarvisd.store.migrate import apply_pending
from jarvisd.store.repositories import ProjectRepository, SessionRepository


@pytest.fixture
async def conn(tmp_path: Path) -> AsyncIterator[aiosqlite.Connection]:
    c = await connect(tmp_path / "jarvis.db")
    await apply_pending(c)
    yield c
    await c.close()


async def test_add_resolves_path_and_lookup_ignores_case(
    conn: aiosqlite.Connection, tmp_path: Path
) -> None:
    (tmp_path / "sipadi").mkdir()
    repo = ProjectRepository(conn)
    added = await repo.add("SIPADI", tmp_path / "x" / ".." / "sipadi")
    assert added.path == (tmp_path / "sipadi").resolve()
    found = await repo.get_by_name("sipadi")
    assert found == added
    assert found.resume_id is None


async def test_duplicate_name_rejected(conn: aiosqlite.Connection, tmp_path: Path) -> None:
    repo = ProjectRepository(conn)
    await repo.add("sipadi", tmp_path / "a")
    with pytest.raises(aiosqlite.IntegrityError):
        await repo.add("Sipadi", tmp_path / "b")


async def test_record_session_sets_resume_id(conn: aiosqlite.Connection, tmp_path: Path) -> None:
    projects = ProjectRepository(conn)
    sessions = SessionRepository(conn)
    p = await projects.add("sipadi", tmp_path)
    first = await sessions.record(p.id, "sess-1")
    assert await sessions.record(p.id, "sess-1") == first
    await sessions.record(p.id, "sess-2")
    reloaded = await projects.get(p.id)
    assert reloaded is not None
    assert reloaded.resume_id == "sess-2"


async def test_session_of_other_project_rejected(
    conn: aiosqlite.Connection, tmp_path: Path
) -> None:
    projects = ProjectRepository(conn)
    sessions = SessionRepository(conn)
    a = await projects.add("a", tmp_path / "a")
    b = await projects.add("b", tmp_path / "b")
    await sessions.record(a.id, "sess-a")
    with pytest.raises(ValueError, match="proyek lain"):
        await sessions.record(b.id, "sess-a")
    reloaded = await projects.get(b.id)
    assert reloaded is not None and reloaded.last_session_id is None


async def test_list_all_sorted(conn: aiosqlite.Connection, tmp_path: Path) -> None:
    repo = ProjectRepository(conn)
    await repo.add("zeta", tmp_path / "z")
    await repo.add("alfa", tmp_path / "a")
    assert [p.name for p in await repo.list_all()] == ["alfa", "zeta"]
