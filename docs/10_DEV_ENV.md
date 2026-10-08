# 10 — Dev Environment
Perintah aktual: docs/11_COMMANDS.md.

## Prasyarat
| Mesin | Kebutuhan |
|---|---|
| Laptop | macOS 13+, Xcode 15, Python 3.12 via `uv`, Claude Code CLI ter-login akun Max (`claude` lalu `/login`), `git`, `whisper.cpp` + model `ggml-small.bin` (fallback) |
| Laptop (suara) | System Settings → Accessibility → Spoken Content → unduh suara Bahasa Indonesia (kualitas Enhanced bila ada); headset untuk uji tahap 0–1 |
| VPS | Ubuntu 22.04+, ≥ 4 inti, ≥ 8 GB RAM, domain mengarah ke VPS untuk TLS Caddy |

## Setup lokal (urutan)
1. Clone repo; `jarvisd/`: sinkronkan dependensi (docs/11).
2. Salin `jarvisd/.env.example` → `jarvisd/.env`; isi.
3. Simpan token VPS ke Keychain (docs/11 "simpan token VPS").
4. Pastikan `ANTHROPIC_API_KEY` TIDAK ada di shell (`env | grep ANTHROPIC` kosong).
5. Jalankan `jarvisd` di foreground dulu; pasang LaunchAgent setelah jalan.
6. Buka `app/FreeJarvis.xcodeproj`, jalankan; beri izin Mikrofon & Accessibility (hotkey).

## Variabel `jarvisd/.env` (nama saja)
| Nama | Isi |
|---|---|
| `JARVIS_WS_PORT` | port WebSocket lokal (bawaan: docs/27) |
| `JARVIS_STT_URL` | URL dasar `stt-server` (https) |
| `JARVIS_STT_TIMEOUT_S` | batas tunggu sebelum fallback lokal |
| `JARVIS_WHISPER_CPP_BIN` / `JARVIS_WHISPER_CPP_MODEL` | path fallback lokal |
| `JARVIS_DATA_DIR` | bawaan `~/Library/Application Support/FreeJarvis` |
| `JARVIS_LOG_LEVEL` | bawaan `INFO` |
Token VPS TIDAK di `.env` (Keychain, layanan `freejarvis.stt`).

## Variabel `stt-server/.env`
`STT_MODEL` (`large-v3-turbo`|`medium`), `STT_COMPUTE_TYPE` (`int8`), `STT_BEARER_TOKEN`, `STT_MAX_AUDIO_S` (8).
