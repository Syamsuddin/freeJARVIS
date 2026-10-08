"""Buka proyek & lanjutkan sesi (F07, docs/06 Alur E).

Nama proyek hanya dicocokkan ke daftar `projects`, tidak pernah dipakai sebagai path
(docs/21). Satu klien SDK aktif pada satu waktu (docs/02).
"""

from __future__ import annotations

import asyncio
import difflib
import re
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Protocol

from claude_agent_sdk import ClaudeAgentOptions

from jarvisd.engine.sdk_client import build_options, create_client
from jarvisd.store.repositories import Project, ProjectRepository, SessionRepository
from jarvisd.voice import phrases

MAX_CANDIDATES = 5
_OPEN_COMMAND = re.compile(r"^(?:jarvis\W+)?buka\s+proyek\s+(?P<name>.+)$", re.IGNORECASE)
_EDGE_PUNCT = re.compile(r"^[\s\W_]+|[\s\W_]+$")


class AgentClient(Protocol):
    async def connect(self) -> None: ...
    async def disconnect(self) -> None: ...


ClientFactory = Callable[[ClaudeAgentOptions], AgentClient]


class OpenOutcome(StrEnum):
    OPENED = "opened"
    ALREADY_OPEN = "already_open"
    CANDIDATES = "candidates"
    FOLDER_MISSING = "folder_missing"
    JOB_RUNNING = "job_running"


@dataclass(frozen=True)
class OpenResult:
    outcome: OpenOutcome
    speech: str
    project: Project | None = None
    candidates: list[str] = field(default_factory=list)


def normalize_name(spoken: str) -> str:
    return _EDGE_PUNCT.sub("", spoken).strip()


def parse_open_command(text: str) -> str | None:
    """'Jarvis, buka proyek SIPADI.' → 'SIPADI'; selain itu None."""
    match = _OPEN_COMMAND.match(text.strip())
    if match is None:
        return None
    return normalize_name(match.group("name")) or None


def _candidates(spoken: str, names: list[str]) -> list[str]:
    lowered = {name.lower(): name for name in names}
    key = spoken.lower()
    close = difflib.get_close_matches(key, list(lowered), n=MAX_CANDIDATES, cutoff=0.5)
    partial = [n for n in lowered if n not in close and (key in n or n in key)]
    picked = [lowered[n] for n in [*close, *partial][:MAX_CANDIDATES]]
    return picked or sorted(names)[:MAX_CANDIDATES]


class ProjectSwitcher:
    def __init__(
        self,
        projects: ProjectRepository,
        sessions: SessionRepository,
        *,
        job_running: Callable[[], bool],
        client_factory: ClientFactory = create_client,
    ) -> None:
        self._projects = projects
        self._sessions = sessions
        self._job_running = job_running
        self._client_factory = client_factory
        self.active: Project | None = None
        self.client: AgentClient | None = None

    async def open(self, spoken_name: str) -> OpenResult:
        name = normalize_name(spoken_name)
        project = await self._projects.get_by_name(name)
        if project is None:
            names = [p.name for p in await self._projects.list_all()]
            if not names:
                return OpenResult(OpenOutcome.CANDIDATES, phrases.PROJECT_NONE_REGISTERED)
            return OpenResult(
                OpenOutcome.CANDIDATES,
                phrases.PROJECT_CANDIDATES.format(name=name),
                candidates=_candidates(name, names),
            )
        if self.active is not None and self.active.id == project.id:
            return OpenResult(
                OpenOutcome.ALREADY_OPEN,
                phrases.PROJECT_ALREADY_OPEN.format(name=project.name),
                project=project,
            )
        if self._job_running():
            # Tanya dulu (docs/06 Alur E); cwd tidak disentuh sampai pengguna memutuskan.
            return OpenResult(
                OpenOutcome.JOB_RUNNING, phrases.PROJECT_SWITCH_JOB_RUNNING, project=project
            )
        if not await asyncio.to_thread(project.path.is_dir):
            return OpenResult(
                OpenOutcome.FOLDER_MISSING, phrases.PROJECT_FOLDER_MISSING, project=project
            )

        options = build_options(project.path, resume=project.resume_id)
        if self.client is not None:
            # Lepas klien lama dulu: tak pernah ada dua klien SDK hidup bersamaan.
            old, self.client, self.active = self.client, None, None
            await old.disconnect()
        client = self._client_factory(options)
        await client.connect()
        self.client = client
        self.active = project
        await self._projects.mark_opened(project.id)
        template = (
            phrases.PROJECT_OPENED_RESUMED if project.resume_id else phrases.PROJECT_OPENED_NEW
        )
        return OpenResult(OpenOutcome.OPENED, template.format(name=project.name), project=project)

    async def remember_session(self, sdk_session_id: str) -> None:
        """Simpan `session_id` dari peristiwa SDK sebagai sesi terakhir proyek aktif."""
        if self.active is None:
            raise RuntimeError("tidak ada proyek aktif")
        await self._sessions.record(self.active.id, sdk_session_id)
        refreshed = await self._projects.get(self.active.id)
        if refreshed is not None:
            self.active = refreshed
