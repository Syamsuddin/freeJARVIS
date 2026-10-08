from pathlib import Path

import aiosqlite
import pytest

from jarvisd.store.db import connect
from jarvisd.store.migrate import apply_pending, current_version, discover

TABLES = {
    "projects",
    "sessions",
    "turns",
    "jobs",
    "tool_events",
    "pending_prompts",
    "quota_snapshots",
    "settings",
}


async def test_fresh_db_gets_full_schema(tmp_path: Path) -> None:
    conn = await connect(tmp_path / "jarvis.db")
    try:
        assert await apply_pending(conn) == [1]
        assert await current_version(conn) == 1
        async with conn.execute("SELECT name FROM sqlite_master WHERE type='table'") as cur:
            names = {row[0] for row in await cur.fetchall()}
        assert names >= TABLES
        async with conn.execute("PRAGMA journal_mode") as cur:
            assert (await cur.fetchone())[0] == "wal"  # type: ignore[index]
    finally:
        await conn.close()


async def test_second_run_is_noop(tmp_path: Path) -> None:
    conn = await connect(tmp_path / "jarvis.db")
    try:
        await apply_pending(conn)
        assert await apply_pending(conn) == []
        assert await current_version(conn) == 1
    finally:
        await conn.close()


async def test_check_constraint_enforced(tmp_path: Path) -> None:
    conn = await connect(tmp_path / "jarvis.db")
    try:
        await apply_pending(conn)
        with pytest.raises(aiosqlite.IntegrityError):
            await conn.execute("INSERT INTO quota_snapshots (raw, created_at) VALUES (NULL, 'x')")
    finally:
        await conn.close()


def test_discover_rejects_gap(tmp_path: Path) -> None:
    (tmp_path / "001_a.sql").write_text("")
    (tmp_path / "003_c.sql").write_text("")
    with pytest.raises(ValueError, match="berurutan"):
        discover(tmp_path)


def test_discover_rejects_bad_name(tmp_path: Path) -> None:
    (tmp_path / "1_init.sql").write_text("")
    with pytest.raises(ValueError, match="tidak sah"):
        discover(tmp_path)
