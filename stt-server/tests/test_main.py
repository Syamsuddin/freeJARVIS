import pytest
from fastapi.testclient import TestClient

from stt_server.auth import RateLimiter, bearer_matches
from stt_server.main import RATE_LIMIT_PER_MIN, Settings
from stt_server.transcriber import AudioFormatError, parse_wav
from tests.conftest import TOKEN, FakeTranscriber, make_wav

AUTH = {"Authorization": f"Bearer {TOKEN}"}


def post(client: TestClient, audio: bytes, headers: dict[str, str] | None = None, **data: str):
    return client.post(
        "/transcribe",
        headers=AUTH if headers is None else headers,
        files={"audio": ("u.wav", audio, "audio/wav")},
        data={"language": "id", **data},
    )


def test_transcribe_ok_passes_prompt_and_language(
    client: TestClient, fake: FakeTranscriber
) -> None:
    response = post(client, make_wav(2.5), prompt="LoginController SsoService")
    assert response.status_code == 200
    assert response.json() == {
        "text": "periksa modul login",
        "duration_s": 2.5,
        "infer_ms": 120,
        "model": "fake-turbo",
    }
    assert fake.calls == [(2.5, "LoginController SsoService", "id")]


def test_healthz_reports_model(client: TestClient, fake: FakeTranscriber) -> None:
    assert fake.loaded
    assert client.get("/healthz").json() == {"status": "ok", "model": "fake-turbo"}


@pytest.mark.parametrize(
    "headers", [{}, {"Authorization": "Bearer salah"}, {"Authorization": TOKEN}]
)
def test_rejects_bad_token(
    client: TestClient, fake: FakeTranscriber, headers: dict[str, str]
) -> None:
    response = post(client, make_wav(1), headers=headers)
    assert response.status_code == 401
    assert response.json() == {"error": {"code": "unauthorized", "message": "Token tidak valid"}}
    assert fake.calls == []


def test_rejects_wrong_format(client: TestClient) -> None:
    response = post(client, make_wav(1, rate=8_000))
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "bad_audio"


def test_rejects_garbage_audio(client: TestClient) -> None:
    assert post(client, b"bukan wav").json()["error"]["code"] == "bad_audio"


def test_rejects_too_long_audio(client: TestClient, fake: FakeTranscriber) -> None:
    response = post(client, make_wav(8.5))
    assert response.status_code == 413
    assert response.json()["error"]["code"] == "too_long"
    assert fake.calls == []


def test_rejects_body_over_spool_threshold(client: TestClient) -> None:
    response = post(client, make_wav(33))  # 33 s ≈ 1,06 MB
    assert response.status_code == 413
    assert response.json()["error"]["code"] == "too_large"


def test_rejects_long_prompt(client: TestClient) -> None:
    response = post(client, make_wav(1), prompt="x" * 801)
    assert response.status_code == 400


def test_rejects_missing_audio(client: TestClient) -> None:
    response = client.post("/transcribe", headers=AUTH, data={"language": "id"})
    assert response.status_code == 400


def test_rate_limit(client: TestClient) -> None:
    for _ in range(RATE_LIMIT_PER_MIN):
        assert post(client, make_wav(0.2)).status_code == 200
    response = post(client, make_wav(0.2))
    assert response.status_code == 429
    assert response.json()["error"]["code"] == "rate_limited"


def test_settings_require_long_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("STT_BEARER_TOKEN", "pendek")
    with pytest.raises(RuntimeError, match="STT_BEARER_TOKEN"):
        Settings.from_env()
    monkeypatch.setenv("STT_BEARER_TOKEN", TOKEN)
    monkeypatch.setenv("STT_MODEL", "medium")
    assert Settings.from_env().model == "medium"


def test_parse_wav_duration_and_errors() -> None:
    assert parse_wav(make_wav(1.5)).duration_s == 1.5
    with pytest.raises(AudioFormatError, match="mono"):
        parse_wav(make_wav(1, channels=2))
    with pytest.raises(AudioFormatError):
        parse_wav(b"RIFF")


def test_bearer_and_rate_limiter_units() -> None:
    assert bearer_matches(f"Bearer {TOKEN}", TOKEN)
    assert not bearer_matches(None, TOKEN)
    limiter = RateLimiter(2, window_s=60)
    assert limiter.allow(0) and limiter.allow(1)
    assert not limiter.allow(2)
    assert limiter.allow(60.5)
