"""Diagnosa gerbang G0 (docs/23): `python -m jarvisd.diag sdk|ask`.

Keluaran berupa baris `kunci=nilai` agar bisa dicocokkan mesin; exit 0 = lulus.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import shutil
import subprocess
import sys
import tempfile
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import claude_agent_sdk
from claude_agent_sdk import (
    AssistantMessage,
    ClaudeSDKClient,
    PermissionResultAllow,
    PermissionResultDeny,
    ResultMessage,
    TextBlock,
    ToolPermissionContext,
)

from jarvisd.engine.sdk_client import (
    BILLING_ENV_KEYS,
    REROUTING_ENV_KEYS,
    build_options,
)

# Metode auth Claude Code yang ditagih ke langganan, bukan API key.
SUBSCRIPTION_AUTH_METHODS = frozenset({"claude.ai", "oauth_token"})

ASK_QUESTION = "Warna apa yang dipilih pengguna?"
ASK_ANSWER = "Biru"
ASK_PROMPT = (
    "Ini uji diagnosa. Panggil alat AskUserQuestion tepat satu kali dengan satu pertanyaan "
    f'"{ASK_QUESTION}", header "Warna", dua pilihan berlabel "Merah" dan "{ASK_ANSWER}", '
    "multiSelect false. Setelah alat menjawab, balas hanya dengan label yang dipilih."
)
ASK_TIMEOUT_S = 180


def find_cli() -> str | None:
    """CLI yang dipakai SDK: binari bawaan paket dulu, lalu `claude` di PATH."""
    bundled = Path(claude_agent_sdk.__file__).parent / "_bundled" / "claude"
    if bundled.is_file():
        return str(bundled)
    return shutil.which("claude")


def evaluate_auth(
    status: Mapping[str, Any] | None, environ: Mapping[str, str]
) -> tuple[bool, list[str]]:
    """Nilai status auth CLI + lingkungan; kembalikan (lulus, baris laporan)."""
    lines: list[str] = []
    ok = True
    for key in BILLING_ENV_KEYS:
        present = key in environ
        lines.append(f"{key.lower()}={'present' if present else 'absent'}")
        ok = ok and not present
    for key in REROUTING_ENV_KEYS:
        if key in environ:
            lines.append(f"{key.lower()}=set (periksa: mengalihkan autentikasi/endpoint)")
    if status is None:
        return False, [*lines, "auth=unknown (claude auth status gagal)"]
    method = str(status.get("authMethod", "none"))
    logged_in = bool(status.get("loggedIn"))
    if logged_in and method in SUBSCRIPTION_AUTH_METHODS:
        lines.append("auth=subscription")
    else:
        lines.append(f"auth={method if logged_in else 'logged_out'}")
        ok = False
    if "subscriptionType" in status:
        lines.append(f"subscription_type={status['subscriptionType']}")
    lines.append(f"auth_method={method}")
    return ok, lines


def read_auth_status(cli: str) -> dict[str, Any] | None:
    try:
        proc = subprocess.run(  # noqa: S603 - argumen tetap, bukan masukan pengguna
            [cli, "auth", "status", "--json"],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        parsed: dict[str, Any] = json.loads(proc.stdout)
    except (OSError, subprocess.TimeoutExpired, json.JSONDecodeError):
        return None
    return parsed


def run_sdk_check() -> int:
    lines = [f"sdk_version={claude_agent_sdk.__version__}"]
    cli = find_cli()
    if cli is None:
        print("\n".join([*lines, "cli=not_found"]))
        return 1
    lines.append(f"cli={cli}")
    ok, auth_lines = evaluate_auth(read_auth_status(cli), os.environ)
    lines.extend(auth_lines)
    lines.append(f"result={'PASS' if ok else 'FAIL'}")
    print("\n".join(lines))
    return 0 if ok else 1


@dataclass
class AskProbe:
    """Rekaman apa yang diterima can_use_tool selama uji."""

    tools_seen: list[str] = field(default_factory=list)
    ask_input: dict[str, Any] | None = None
    final_text: str = ""

    async def can_use_tool(
        self, tool_name: str, tool_input: dict[str, Any], _context: ToolPermissionContext
    ) -> PermissionResultAllow | PermissionResultDeny:
        self.tools_seen.append(tool_name)
        if tool_name != "AskUserQuestion":
            return PermissionResultDeny(message="Uji diagnosa: hanya AskUserQuestion.")
        self.ask_input = tool_input
        questions = tool_input.get("questions") or []
        answers = {str(q.get("question", "")): ASK_ANSWER for q in questions}
        return PermissionResultAllow(updated_input={**tool_input, "answers": answers})


def evaluate_ask(probe: AskProbe) -> tuple[bool, list[str]]:
    via = probe.ask_input is not None
    roundtrip = via and ASK_ANSWER.lower() in probe.final_text.lower()
    keys = ",".join(sorted(probe.ask_input)) if probe.ask_input else "-"
    lines = [
        f"ask_via_can_use_tool={'yes' if via else 'no'}",
        f"answer_roundtrip={'yes' if roundtrip else 'no'}",
        f"ask_input_keys={keys}",
        f"tools_seen={','.join(probe.tools_seen) or '-'}",
    ]
    return via and roundtrip, lines


async def probe_ask(model: str) -> AskProbe:
    probe = AskProbe()
    with tempfile.TemporaryDirectory(prefix="jarvisd-diag-") as tmp:
        options = build_options(
            Path(tmp),
            can_use_tool=probe.can_use_tool,
            model=model,
            tools=["AskUserQuestion"],
            max_turns=4,
        )
        async with ClaudeSDKClient(options=options) as client:
            await client.query(ASK_PROMPT)
            async for message in client.receive_response():
                if isinstance(message, AssistantMessage):
                    for block in message.content:
                        if isinstance(block, TextBlock):
                            probe.final_text += block.text
                elif isinstance(message, ResultMessage) and message.result:
                    probe.final_text += message.result
    return probe


def run_ask_check(model: str) -> int:
    try:
        probe = asyncio.run(asyncio.wait_for(probe_ask(model), ASK_TIMEOUT_S))
    except (TimeoutError, claude_agent_sdk.ClaudeSDKError) as exc:
        print(f"ask_via_can_use_tool=unknown\nerror={type(exc).__name__}: {exc}")
        return 1
    ok, lines = evaluate_ask(probe)
    lines.append(f"result={'PASS' if ok else 'FAIL'}")
    print("\n".join(lines))
    return 0 if ok else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m jarvisd.diag")
    sub = parser.add_subparsers(dest="check", required=True)
    sub.add_parser("sdk", help="cek login langganan, tanpa API key, versi SDK")
    ask = sub.add_parser("ask", help="cek AskUserQuestion lewat can_use_tool (memakai jatah)")
    ask.add_argument("--model", default="haiku")
    args = parser.parse_args(argv)
    if args.check == "sdk":
        return run_sdk_check()
    return run_ask_check(args.model)


if __name__ == "__main__":
    sys.exit(main())
