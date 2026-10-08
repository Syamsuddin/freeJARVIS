import json
import stat
from pathlib import Path
from typing import Any

import pytest
from claude_agent_sdk import PermissionResultAllow, PermissionResultDeny, ToolPermissionContext

from jarvisd import diag
from jarvisd.diag import AskProbe, evaluate_ask, evaluate_auth, read_auth_status

MAX_STATUS = {"loggedIn": True, "authMethod": "claude.ai", "subscriptionType": "max"}


def test_auth_passes_for_subscription_without_api_key() -> None:
    ok, lines = evaluate_auth(MAX_STATUS, {})
    assert ok
    assert "auth=subscription" in lines
    assert "anthropic_api_key=absent" in lines
    assert "subscription_type=max" in lines


def test_auth_fails_when_api_key_in_env() -> None:
    ok, lines = evaluate_auth(MAX_STATUS, {"ANTHROPIC_API_KEY": "sk"})
    assert not ok
    assert "anthropic_api_key=present" in lines


def test_auth_fails_for_api_key_login() -> None:
    ok, lines = evaluate_auth({"loggedIn": True, "authMethod": "api_key"}, {})
    assert not ok
    assert "auth=api_key" in lines


def test_auth_fails_when_logged_out_or_unknown() -> None:
    assert evaluate_auth({"loggedIn": False, "authMethod": "none"}, {})[1][-1] == (
        "auth_method=none"
    )
    assert not evaluate_auth({"loggedIn": False}, {})[0]
    ok, lines = evaluate_auth(None, {})
    assert not ok
    assert lines[-1].startswith("auth=unknown")


def test_auth_reports_rerouting_env_without_failing() -> None:
    ok, lines = evaluate_auth(MAX_STATUS, {"ANTHROPIC_BASE_URL": "https://x"})
    assert ok
    assert any(line.startswith("anthropic_base_url=set") for line in lines)


def _fake_cli(tmp_path: Path, stdout: str) -> str:
    cli = tmp_path / "claude"
    cli.write_text(f"#!/bin/sh\ncat <<'JSON'\n{stdout}\nJSON\n")
    cli.chmod(cli.stat().st_mode | stat.S_IEXEC)
    return str(cli)


def test_read_auth_status_parses_cli_json(tmp_path: Path) -> None:
    assert read_auth_status(_fake_cli(tmp_path, json.dumps(MAX_STATUS))) == MAX_STATUS


def test_read_auth_status_returns_none_on_garbage(tmp_path: Path) -> None:
    assert read_auth_status(_fake_cli(tmp_path, "bukan json")) is None
    assert read_auth_status(str(tmp_path / "tidak-ada")) is None


def _context() -> ToolPermissionContext:
    return ToolPermissionContext(signal=None, suggestions=[])


async def test_probe_answers_ask_user_question() -> None:
    probe = AskProbe()
    questions: list[dict[str, Any]] = [{"question": diag.ASK_QUESTION, "options": []}]
    result = await probe.can_use_tool("AskUserQuestion", {"questions": questions}, _context())
    assert isinstance(result, PermissionResultAllow)
    assert result.updated_input == {
        "questions": questions,
        "answers": {diag.ASK_QUESTION: diag.ASK_ANSWER},
    }
    assert probe.tools_seen == ["AskUserQuestion"]


async def test_probe_denies_other_tools() -> None:
    probe = AskProbe()
    result = await probe.can_use_tool("Bash", {"command": "rm -rf /"}, _context())
    assert isinstance(result, PermissionResultDeny)
    assert probe.ask_input is None


def test_evaluate_ask_requires_tool_call_and_roundtrip() -> None:
    passed = AskProbe(
        tools_seen=["AskUserQuestion"], ask_input={"questions": []}, final_text="Biru"
    )
    assert evaluate_ask(passed)[0]
    no_roundtrip = AskProbe(ask_input={"questions": []}, final_text="Merah")
    ok, lines = evaluate_ask(no_roundtrip)
    assert not ok
    assert "answer_roundtrip=no" in lines
    ok, lines = evaluate_ask(AskProbe(final_text="Biru"))
    assert not ok
    assert "ask_via_can_use_tool=no" in lines


def test_main_dispatches_sdk(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(diag, "run_sdk_check", lambda: 7)
    assert diag.main(["sdk"]) == 7


@pytest.mark.live
def test_live_ask_roundtrip() -> None:
    assert diag.run_ask_check("haiku") == 0
