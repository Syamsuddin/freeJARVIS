import io
import wave
from dataclasses import dataclass, field

import pytest
from fastapi.testclient import TestClient

from stt_server.main import Settings, create_app
from stt_server.transcriber import Pcm, Transcript

TOKEN = "t" * 40


def make_wav(seconds: float, rate: int = 16_000, width: int = 2, channels: int = 1) -> bytes:
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wav:
        wav.setnchannels(channels)
        wav.setsampwidth(width)
        wav.setframerate(rate)
        wav.writeframes(b"\x00" * int(seconds * rate) * width * channels)
    return buffer.getvalue()


@dataclass
class FakeTranscriber:
    model_name: str = "fake-turbo"
    loaded: bool = False
    calls: list[tuple[float, str | None, str]] = field(default_factory=list)

    def load(self) -> None:
        self.loaded = True

    def transcribe(self, pcm: Pcm, prompt: str | None, language: str) -> Transcript:
        self.calls.append((pcm.duration_s, prompt, language))
        return Transcript("periksa modul login", pcm.duration_s, 120, self.model_name)


@pytest.fixture
def fake() -> FakeTranscriber:
    return FakeTranscriber()


@pytest.fixture
def client(fake: FakeTranscriber) -> TestClient:
    settings = Settings(model="fake", compute_type="int8", bearer_token=TOKEN, max_audio_s=8)
    with TestClient(create_app(settings, fake)) as test_client:
        yield test_client
