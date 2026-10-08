import os
from pathlib import Path

import pytest

from jarvisd.engine import sdk_client
from jarvisd.engine.sdk_client import BillingEnvError, build_options, scrub_billing_env


def test_scrub_removes_api_key_and_keeps_others() -> None:
    env = {"ANTHROPIC_API_KEY": "sk-test", "HOME": "/home/x"}
    assert scrub_billing_env(env) == ["ANTHROPIC_API_KEY"]
    assert env == {"HOME": "/home/x"}


def test_scrub_noop_when_absent() -> None:
    env = {"HOME": "/home/x"}
    assert scrub_billing_env(env) == []
    assert env == {"HOME": "/home/x"}


def test_build_options_scrubs_process_environ(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test")
    options = build_options(tmp_path, model="sonnet")
    assert "ANTHROPIC_API_KEY" not in os.environ
    # Jangan bergantung pada options.env: SDK menimpakannya di atas os.environ.
    assert "ANTHROPIC_API_KEY" not in options.env
    assert options.cwd == tmp_path
    assert options.model == "sonnet"


def test_build_options_refuses_when_key_survives(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(sdk_client, "scrub_billing_env", lambda environ=None: [])
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test")
    with pytest.raises(BillingEnvError, match="ANTHROPIC_API_KEY"):
        build_options(tmp_path)


def test_build_options_appends_to_claude_code_preset(tmp_path: Path) -> None:
    options = build_options(tmp_path, system_prompt_append="Jawab dua kalimat.")
    assert options.system_prompt == {
        "type": "preset",
        "preset": "claude_code",
        "append": "Jawab dua kalimat.",
    }
    assert build_options(tmp_path).system_prompt is None
