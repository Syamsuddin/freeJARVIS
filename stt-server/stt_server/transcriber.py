"""Validasi WAV di memori + transkripsi faster-whisper. Audio tidak pernah ditulis ke disk."""

from __future__ import annotations

import io
import os
import time
import wave
from dataclasses import dataclass
from typing import Any, Protocol

SAMPLE_RATE = 16_000
SAMPLE_WIDTH_BYTES = 2
CHANNELS = 1


class AudioFormatError(ValueError):
    """WAV bukan PCM s16 16 kHz mono."""


@dataclass(frozen=True)
class Pcm:
    frames: bytes
    duration_s: float


@dataclass(frozen=True)
class Transcript:
    text: str
    duration_s: float
    infer_ms: int
    model: str


class Transcriber(Protocol):
    model_name: str

    def load(self) -> None: ...

    def transcribe(self, pcm: Pcm, prompt: str | None, language: str) -> Transcript: ...


def parse_wav(data: bytes) -> Pcm:
    try:
        with wave.open(io.BytesIO(data), "rb") as wav:
            params = (wav.getframerate(), wav.getsampwidth(), wav.getnchannels())
            if params != (SAMPLE_RATE, SAMPLE_WIDTH_BYTES, CHANNELS):
                raise AudioFormatError(
                    f"butuh WAV 16 kHz s16 mono, diterima rate={params[0]} "
                    f"width={params[1]} channels={params[2]}"
                )
            frames = wav.readframes(wav.getnframes())
    except (wave.Error, EOFError) as exc:
        raise AudioFormatError(f"WAV tidak valid: {exc}") from exc
    return Pcm(frames=frames, duration_s=len(frames) / (SAMPLE_RATE * SAMPLE_WIDTH_BYTES))


class WhisperTranscriber:
    """faster-whisper di CPU. Dimuat sekali saat startup; satu pekerja (main.py)."""

    def __init__(self, model_name: str, compute_type: str = "int8") -> None:
        self.model_name = model_name
        self.compute_type = compute_type
        self._model: Any = None

    def load(self) -> None:
        from faster_whisper import WhisperModel

        self._model = WhisperModel(
            self.model_name,
            device="cpu",
            compute_type=self.compute_type,
            cpu_threads=os.cpu_count() or 4,
        )

    def transcribe(self, pcm: Pcm, prompt: str | None, language: str) -> Transcript:
        import numpy as np

        if self._model is None:
            raise RuntimeError("model belum dimuat")
        audio = np.frombuffer(pcm.frames, dtype=np.int16).astype(np.float32) / 32768.0
        started = time.perf_counter()
        segments, _info = self._model.transcribe(
            audio,
            language=language,
            initial_prompt=prompt or None,
            beam_size=1,
            condition_on_previous_text=False,
            without_timestamps=True,
        )
        text = " ".join(segment.text.strip() for segment in segments).strip()
        infer_ms = round((time.perf_counter() - started) * 1000)
        return Transcript(text, round(pcm.duration_s, 3), infer_ms, self.model_name)
