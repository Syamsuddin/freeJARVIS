from collections.abc import AsyncIterator
from pathlib import Path

import aiosqlite
import pytest
from claude_agent_sdk import ClaudeAgentOptions

from jarvisd.conversation.project_switch import (
    OpenOutcome,
    ProjectSwitcher,
    parse_open_command,
)
from jarvisd.store.db import connect
from jarvisd.store.migrate import apply_pending
from jarvisd.store.repositories import ProjectRepository, SessionRepository
from jarvisd.voice import phrases


class FakeClient:
    def __init__(self, options: ClaudeAgentOptions) -> None:
        self.options = options
        self.connected = False
        self.disconnected = False

    async def connect(self) -> None:
        self.connected = True

    async def disconnect(self) -> None:
        self.disconnected = True


class Env:
    def __init__(self, conn: aiosqlite.Connection, root: Path) -> None:
        self.root = root
        self.projects = ProjectRepository(conn)
        self.sessions = SessionRepository(conn)
        self.running = False
        self.created: list[FakeClient] = []
        self.switcher = ProjectSwitcher(
            self.projects,
            self.sessions,
            job_running=lambda: self.running,
            client_factory=self._factory,
        )

    def _factory(self, options: ClaudeAgentOptions) -> FakeClient:
        client = FakeClient(options)
        self.created.append(client)
        return client

    async def add(self, name: str) -> int:
        path = self.root / name
        path.mkdir()
        return (await self.projects.add(name, path)).id


@pytest.fixture
async def env(tmp_path: Path) -> AsyncIterator[Env]:
    conn = await connect(tmp_path / "jarvis.db")
    await apply_pending(conn)
    yield Env(conn, tmp_path)
    await conn.close()


async def test_open_resumes_last_session_in_project_cwd(env: Env) -> None:
    pid = await env.add("sipadi")
    await env.sessions.record(pid, "sess-kemarin")

    result = await env.switcher.open("SIPADI.")

    assert result.outcome is OpenOutcome.OPENED
    assert result.speech == phrases.PROJECT_OPENED_RESUMED.format(name="sipadi")
    [client] = env.created
    assert client.connected
    assert client.options.cwd == (env.root / "sipadi").resolve()
    assert client.options.resume == "sess-kemarin"
    assert env.switcher.active is not None and env.switcher.active.id == pid


async def test_open_without_session_starts_fresh(env: Env) -> None:
    await env.add("sipadi")
    result = await env.switcher.open("sipadi")
    assert result.speech == phrases.PROJECT_OPENED_NEW.format(name="sipadi")
    assert env.created[0].options.resume is None


async def test_unmatched_name_lists_candidates_and_keeps_cwd(env: Env) -> None:
    await env.add("sipadi")
    await env.add("simpeg")
    await env.add("kasir")
    await env.switcher.open("kasir")

    result = await env.switcher.open("sipadu")

    assert result.outcome is OpenOutcome.CANDIDATES
    assert result.candidates[0] == "sipadi"
    assert "kasir" not in result.candidates
    assert len(env.created) == 1
    assert env.switcher.active is not None and env.switcher.active.name == "kasir"
    assert not env.created[0].disconnected


async def test_unmatched_with_no_projects(env: Env) -> None:
    result = await env.switcher.open("apa saja")
    assert result.outcome is OpenOutcome.CANDIDATES
    assert result.speech == phrases.PROJECT_NONE_REGISTERED
    assert result.candidates == []


async def test_switch_while_job_running_asks_first(env: Env) -> None:
    await env.add("kasir")
    await env.add("sipadi")
    await env.switcher.open("kasir")
    env.running = True

    result = await env.switcher.open("sipadi")

    assert result.outcome is OpenOutcome.JOB_RUNNING
    assert result.speech == phrases.PROJECT_SWITCH_JOB_RUNNING
    assert len(env.created) == 1
    assert not env.created[0].disconnected
    assert env.switcher.active is not None and env.switcher.active.name == "kasir"


async def test_switch_disconnects_previous_client(env: Env) -> None:
    await env.add("kasir")
    await env.add("sipadi")
    await env.switcher.open("kasir")
    await env.switcher.open("sipadi")
    first, second = env.created
    assert first.disconnected and second.connected and not second.disconnected


async def test_reopen_active_project_is_noop(env: Env) -> None:
    await env.add("sipadi")
    await env.switcher.open("sipadi")
    result = await env.switcher.open("Sipadi")
    assert result.outcome is OpenOutcome.ALREADY_OPEN
    assert len(env.created) == 1


async def test_missing_folder_reported_without_client(env: Env) -> None:
    await env.add("sipadi")
    (env.root / "sipadi").rmdir()
    result = await env.switcher.open("sipadi")
    assert result.outcome is OpenOutcome.FOLDER_MISSING
    assert result.speech == phrases.PROJECT_FOLDER_MISSING
    assert env.created == []
    assert env.switcher.active is None


async def test_remember_session_feeds_next_resume(env: Env) -> None:
    await env.add("kasir")
    await env.add("sipadi")
    await env.switcher.open("sipadi")
    await env.switcher.remember_session("sess-baru")
    await env.switcher.open("kasir")
    await env.switcher.open("sipadi")
    assert env.created[-1].options.resume == "sess-baru"


async def test_remember_session_requires_active_project(env: Env) -> None:
    with pytest.raises(RuntimeError):
        await env.switcher.remember_session("sess")


@pytest.mark.parametrize(
    ("text", "name"),
    [
        ("Jarvis, buka proyek SIPADI.", "SIPADI"),
        ("buka proyek sipadi", "sipadi"),
        ("Buka  Proyek  kasir toko!", "kasir toko"),
        ("periksa modul login", None),
        ("buka proyek ...", None),
    ],
)
def test_parse_open_command(text: str, name: str | None) -> None:
    assert parse_open_command(text) == name
