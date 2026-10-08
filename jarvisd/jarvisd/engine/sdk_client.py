"""Pembungkus Claude Agent SDK.

Jebakan (docs/16): SDK menggabungkan `ClaudeAgentOptions.env` DI ATAS `os.environ`,
jadi membuang `ANTHROPIC_API_KEY` dari `options.env` tidak berefek. Key harus
dibuang dari `os.environ` proses jarvisd sebelum klien SDK dibuat.
"""

from __future__ import annotations

import os
from collections.abc import MutableMapping
from pathlib import Path

from claude_agent_sdk import CanUseTool, ClaudeAgentOptions, ClaudeSDKClient
from claude_agent_sdk.types import SystemPromptPreset

# Membuat SDK menagih API key, bukan langganan Max (docs/20 #1).
BILLING_ENV_KEYS: tuple[str, ...] = ("ANTHROPIC_API_KEY",)
# Mengalihkan autentikasi/endpoint; tidak dibuang otomatis, tetapi dilaporkan diag.
REROUTING_ENV_KEYS: tuple[str, ...] = ("ANTHROPIC_AUTH_TOKEN", "ANTHROPIC_BASE_URL")


class BillingEnvError(RuntimeError):
    """Variabel penagihan API masih terlihat oleh subprocess Claude Code."""


def scrub_billing_env(environ: MutableMapping[str, str] | None = None) -> list[str]:
    """Buang variabel penagihan API dari lingkungan proses; kembalikan nama yang dibuang."""
    env = os.environ if environ is None else environ
    removed = [key for key in BILLING_ENV_KEYS if key in env]
    for key in removed:
        del env[key]
    return removed


def build_options(
    cwd: Path,
    *,
    can_use_tool: CanUseTool | None = None,
    model: str | None = None,
    resume: str | None = None,
    tools: list[str] | None = None,
    system_prompt_append: str | None = None,
    max_turns: int | None = None,
) -> ClaudeAgentOptions:
    """Bangun opsi SDK; menolak jalan bila variabel penagihan API masih ada."""
    scrub_billing_env()
    leaked = [key for key in BILLING_ENV_KEYS if key in os.environ]
    if leaked:
        raise BillingEnvError(", ".join(leaked))
    system_prompt: SystemPromptPreset | None = (
        {"type": "preset", "preset": "claude_code", "append": system_prompt_append}
        if system_prompt_append
        else None
    )
    return ClaudeAgentOptions(
        cwd=cwd,
        can_use_tool=can_use_tool,
        model=model,
        resume=resume,
        tools=tools,
        system_prompt=system_prompt,
        max_turns=max_turns,
    )


def create_client(options: ClaudeAgentOptions) -> ClaudeSDKClient:
    """Satu-satunya tempat `ClaudeSDKClient` dibuat; opsi wajib lewat `build_options`."""
    return ClaudeSDKClient(options=options)
