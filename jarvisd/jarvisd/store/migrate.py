"""Penerap migrasi bernomor `migrations/NNN_nama.sql`; versi di `PRAGMA user_version`.

⚠️ Terhadap DB nyata: backup dulu (docs/11, docs/25).
"""

from __future__ import annotations

import argparse
import asyncio
import re
from dataclasses import dataclass
from pathlib import Path

import aiosqlite

from jarvisd.store.db import connect, default_db_path

MIGRATIONS_DIR = Path(__file__).parent / "migrations"
_NAME = re.compile(r"^(\d{3})_[a-z0-9_]+\.sql$")


@dataclass(frozen=True)
class Migration:
    version: int
    path: Path


def discover(directory: Path = MIGRATIONS_DIR) -> list[Migration]:
    found: list[Migration] = []
    for path in directory.glob("*.sql"):
        match = _NAME.match(path.name)
        if match is None:
            raise ValueError(f"nama migrasi tidak sah: {path.name}")
        found.append(Migration(int(match.group(1)), path))
    found.sort(key=lambda m: m.version)
    versions = [m.version for m in found]
    if versions != list(range(1, len(found) + 1)):
        raise ValueError(f"nomor migrasi harus berurutan dari 001: {versions}")
    return found


async def current_version(conn: aiosqlite.Connection) -> int:
    async with conn.execute("PRAGMA user_version") as cur:
        row = await cur.fetchone()
    return int(row[0]) if row else 0


async def apply_pending(conn: aiosqlite.Connection, directory: Path = MIGRATIONS_DIR) -> list[int]:
    """Terapkan migrasi yang belum ada; tiap berkas dalam satu transaksi."""
    applied: list[int] = []
    version = await current_version(conn)
    for migration in discover(directory):
        if migration.version <= version:
            continue
        sql = migration.path.read_text(encoding="utf-8")
        await conn.executescript(
            f"BEGIN;\n{sql}\nPRAGMA user_version = {migration.version};\nCOMMIT;"
        )
        applied.append(migration.version)
    return applied


async def _main(db_path: Path) -> None:
    conn = await connect(db_path)
    try:
        applied = await apply_pending(conn)
        version = await current_version(conn)
    finally:
        await conn.close()
    done = ", ".join(f"{v:03d}" for v in applied) or "tidak ada"
    print(f"db={db_path} applied={done} user_version={version}")


def main() -> None:
    parser = argparse.ArgumentParser(prog="jarvisd.store.migrate")
    parser.add_argument("--db", type=Path, default=default_db_path())
    args = parser.parse_args()
    asyncio.run(_main(args.db))


if __name__ == "__main__":
    main()
