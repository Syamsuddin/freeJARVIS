"""FastAPI `POST /transcribe` + `GET /healthz` (kontrak: docs/27 §HTTP)."""

from __future__ import annotations

import asyncio
import json
import logging
import os
import time
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.concurrency import run_in_threadpool
from starlette.datastructures import UploadFile

from stt_server.auth import RateLimiter, bearer_matches
from stt_server.transcriber import AudioFormatError, Transcriber, WhisperTranscriber, parse_wav

# Di bawah ambang spool Starlette (1 MiB): unggahan tetap di memori, tak pernah ke disk.
MAX_BODY_BYTES = 1_000_000
MAX_PROMPT_CHARS = 800
RATE_LIMIT_PER_MIN = 60

log = logging.getLogger("stt_server")


@dataclass
class AppState:
    settings: Settings | None = None
    transcriber: Transcriber | None = None


@dataclass(frozen=True)
class Settings:
    model: str
    compute_type: str
    bearer_token: str
    max_audio_s: float

    @classmethod
    def from_env(cls) -> Settings:
        token = os.environ.get("STT_BEARER_TOKEN", "")
        if len(token) < 32:
            raise RuntimeError("STT_BEARER_TOKEN wajib diisi, minimal 32 karakter")
        return cls(
            model=os.environ.get("STT_MODEL", "large-v3-turbo"),
            compute_type=os.environ.get("STT_COMPUTE_TYPE", "int8"),
            bearer_token=token,
            max_audio_s=float(os.environ.get("STT_MAX_AUDIO_S", "8")),
        )


def error(status: int, code: str, message: str) -> JSONResponse:
    return JSONResponse(status_code=status, content={"error": {"code": code, "message": message}})


def log_event(level: int, event: str, **fields: object) -> None:
    log.log(level, json.dumps({"ts": time.time(), "event": event, **fields}))


def create_app(settings: Settings | None = None, transcriber: Transcriber | None = None) -> FastAPI:
    state = AppState()
    worker = asyncio.Semaphore(1)
    limiter = RateLimiter(RATE_LIMIT_PER_MIN)

    @asynccontextmanager
    async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
        cfg = settings or Settings.from_env()
        engine = transcriber or WhisperTranscriber(cfg.model, cfg.compute_type)
        await run_in_threadpool(engine.load)
        state.settings, state.transcriber = cfg, engine
        log_event(logging.INFO, "model_loaded", model=engine.model_name)
        yield

    app = FastAPI(lifespan=lifespan, docs_url=None, redoc_url=None, openapi_url=None)

    @app.get("/healthz")
    async def healthz() -> JSONResponse:
        if state.transcriber is None:
            return error(503, "not_ready", "Model belum siap")
        return JSONResponse({"status": "ok", "model": state.transcriber.model_name})

    @app.post("/transcribe")
    async def transcribe(request: Request) -> JSONResponse:
        cfg, engine = state.settings, state.transcriber
        if cfg is None or engine is None:
            return error(503, "not_ready", "Model belum siap")
        if not bearer_matches(request.headers.get("authorization"), cfg.bearer_token):
            return error(401, "unauthorized", "Token tidak valid")
        if not limiter.allow():
            return error(429, "rate_limited", "Terlalu banyak permintaan")
        length = request.headers.get("content-length")
        if length is None or not length.isdigit():
            return error(411, "length_required", "Content-Length wajib")
        if int(length) > MAX_BODY_BYTES:
            return error(413, "too_large", "Audio terlalu besar")

        form = await request.form(max_files=1, max_fields=3)
        audio = form.get("audio")
        prompt = form.get("prompt")
        language = form.get("language") or "id"
        if not isinstance(audio, UploadFile) or not isinstance(language, str):
            return error(400, "bad_request", "Field audio wajib berupa berkas WAV")
        if prompt is not None and (not isinstance(prompt, str) or len(prompt) > MAX_PROMPT_CHARS):
            return error(400, "bad_request", f"prompt maksimal {MAX_PROMPT_CHARS} karakter")
        try:
            pcm = parse_wav(await audio.read())
        except AudioFormatError as exc:
            return error(400, "bad_audio", str(exc))
        finally:
            await audio.close()
        if pcm.duration_s > cfg.max_audio_s:
            return error(413, "too_long", f"Audio lebih dari {cfg.max_audio_s:g} detik")

        async with worker:
            result = await run_in_threadpool(engine.transcribe, pcm, prompt, language)
        log_event(
            logging.INFO,
            "transcribed",
            request_id=request.headers.get("x-request-id"),
            audio_s=result.duration_s,
            infer_ms=result.infer_ms,
            model=result.model,
        )
        return JSONResponse(
            {
                "text": result.text,
                "duration_s": result.duration_s,
                "infer_ms": result.infer_ms,
                "model": result.model,
            }
        )

    return app


app = create_app()
