# 09 — Stack
Pemilik daftar teknologi & versi.

| Lapisan | Teknologi | Versi minimum |
|---|---|---|
| OS laptop | macOS (MacBook Pro 2019 Intel) | 13 Ventura |
| `app` | Swift, SwiftUI, `MenuBarExtra`, `AVAudioEngine` (`setVoiceProcessingEnabled(true)`), `AVSpeechSynthesizer`, `URLSessionWebSocketTask`, Carbon `RegisterEventHotKey` | Swift 5.9, Xcode 15 |
| VAD app | Silero VAD (ONNX Runtime Swift) [ASUMSI paket: `onnxruntime-swift-package-manager`] | — |
| `jarvisd` | Python, `claude-agent-sdk`, `asyncio`, `websockets`, `silero-vad`, `aiosqlite`, `pydantic` v2, `httpx` | Python 3.12 |
| STT fallback lokal | `whisper.cpp` model `small` (binari CLI dipanggil `jarvisd`) | — |
| `stt-server` | FastAPI, `uvicorn`, `faster-whisper` int8 `large-v3-turbo` (fallback `medium` bila 4 inti tak cukup) | Python 3.12 |
| VPS | Ubuntu, `systemd`, Caddy (TLS otomatis) | 22.04 |
| Penyimpanan | SQLite (WAL) | 3.37+ |
| Tooling Python | `uv`, `ruff`, `mypy`, `pytest`, `pytest-asyncio` | — |
| Tooling Swift | XCTest | — |
| Tahap 2 | `mcp` Python SDK, Streamable HTTP | — |
| Tahap 3 | openWakeWord; Azure Neural id-ID / ElevenLabs | — |

## Kebijakan model (per jenis giliran)
| Giliran | Model |
|---|---|
| Status / kemajuan | Tidak ada (dari peristiwa SDK, nol token) |
| Klarifikasi, konfirmasi, obrolan ringan | Sonnet (alias SDK `sonnet`) |
| Kerja kode, review, refactor | Opus (alias SDK `opus`), bawaan instruksi kerja |
| "pakai model X" | Sesuai permintaan, diumumkan Jarvis |

## Teknologi terlarang
| Terlarang | Alasan |
|---|---|
| Flutter, Electron, UI web | Butuh Swift untuk AEC sistem; dua lapis UI tanpa nilai |
| MLX, CoreML, apa pun yang butuh Neural Engine | Intel 2019 tak punya |
| API macOS 26 (SpeechAnalyzer, dll.) | Laptop tak mendapat pembaruan itu |
| `ANTHROPIC_API_KEY` di env `jarvisd` | SDK akan menagih API key, bukan langganan |
| Pustaka WebSocket/HTTP pihak ketiga di app | `URLSession` cukup |
| ORM di `jarvisd` | SQL eksplisit via `aiosqlite`; skema kecil |
