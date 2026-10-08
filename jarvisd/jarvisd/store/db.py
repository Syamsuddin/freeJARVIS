"""Koneksi SQLite: WAL + foreign key aktif di setiap koneksi (docs/07)."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import aiosqlite


def default_db_path() -> Path:
    return Path.home() / "Library" / "Application Support" / "FreeJarvis" / "jarvis.db"


def utc_now() -> str:
    """Waktu ISO-8601 UTC, format tunggal semua kolom waktu."""
    return datetime.now(UTC).isoformat(timespec="seconds")


async def connect(path: Path) -> aiosqlite.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = await aiosqlite.connect(path)
    conn.row_factory = aiosqlite.Row
    await conn.execute("PRAGMA foreign_keys=ON")
    await conn.execute("PRAGMA journal_mode=WAL")
    return conn
