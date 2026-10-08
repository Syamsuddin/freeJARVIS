# 08 — Architecture
Teknologi & versi: docs/09_STACK.md. Pesan antar-proses: docs/27_API_CONTRACT.md.

## Komponen
```
 MacBook (127.0.0.1)                                         VPS (TLS + Bearer)
┌────────────────────────┐  WebSocket JSON  ┌─────────────────────────────┐  HTTPS   ┌──────────────┐
│ FreeJarvis.app (Swift) │ ◄──────────────► │ jarvisd (Python, launchd)   │ ───────► │ stt-server   │
│ mic/speaker VPIO + AEC │  127.0.0.1:8764  │ conversation · engine ·     │ /transcribe│ faster-whisper│
│ VAD lokal (barge-in)   │                  │ voice · store(SQLite) · ws  │ ◄─────── │ int8         │
│ TTS + posisi baca · UI │                  │      │ Agent SDK (subprocess)│          └──────────────┘
└────────────────────────┘                  │      ▼                      │
                                            │ Claude Code (cwd proyek)    │
                                            └ ─ ─ mcp/ :8765 (tahap 2) ─ ─┘
```

## Tanggung jawab
| Komponen | Memegang | TIDAK memegang |
|---|---|---|
| `app` | `AVAudioEngine` Voice Processing I/O, VAD lokal untuk barge-in, pemutar TTS + posisi baca, orb, transkrip, Viewer, hotkey, mute | Logika percakapan, panggilan model, STT, SQLite |
| `jarvisd` | Dua mesin status, Agent SDK, `can_use_tool`, hook, narator, pemisah lisan/layar, turn detection, klien STT + fallback, router TTS, SQLite | Audio mentah dari/ke perangkat, rendering UI |
| `stt-server` | `POST /transcribe` (WAV 16 kHz mono + initial prompt) → teks; antrean satu pekerja | Deteksi giliran, barge-in, penyimpanan audio |
| Claude Code | Eksekusi kerja di `cwd`, `AskUserQuestion`, hook | Suara |

## Lapisan `jarvisd`
`ws/` (I/O protokol, validasi pydantic) → `conversation/` (mesin status, tafsir selaan, turn detection) → `engine/` (SDK client, `can_use_tool`, hook, narator, kebijakan model) & `voice/` (VAD, klien STT, router TTS, pemisah lisan/layar) → `store/` (SQLite). Arah dependensi hanya ke bawah; `engine` dan `voice` tidak saling impor, keduanya dipanggil `conversation`.

## Keputusan arsitektural kunci
| Keputusan | Alasan |
|---|---|
| Agent SDK (Python `ClaudeSDKClient`) sebagai inti, bukan `claude -p`/MCP | Satu-satunya jalur dengan `interrupt()`, `resume`, `can_use_tool`, model per giliran |
| Barge-in diputuskan di app oleh VAD lokal | Tak boleh bergantung jaringan/IPC; target < 300 ms |
| STT di VPS, bukan lokal | Intel 2019 tanpa Neural Engine; CPU laptop tetap lega untuk Claude Code |
| Python memegang seluruh logika, Swift hanya kulit | Keahlian utama pengguna; logika teruji dengan pytest tanpa Xcode |
| Status pekerjaan hanya dari peristiwa SDK | Jarvis tak boleh mengarang kemajuan |
| Pemisah lisan/layar tiga lapis: system prompt → narator → penjaga panjang | Model tidak selalu patuh; lapis deterministik di bawah penalaran |
| Hook dipasang lewat opsi `hooks` SDK, bukan `settings.json` | Tidak mengubah konfigurasi Claude Code global pengguna |
| MCP & Channels bukan fondasi | Tahap 2; Channels masih research preview |
| `STTProvider` / `TTSProvider` sebagai antarmuka | Naik kelas ke cloud tanpa ubah `conversation/` |
| Tanpa split paket; protokol di satu dokumen (docs/27) | Satu pengguna, satu repo; seremoni split tak terbayar |

## Integrasi eksternal
| Integrasi | Arah | Catatan |
|---|---|---|
| Claude Agent SDK | `jarvisd` → Claude Code CLI lokal | login Max (OAuth), tanpa `ANTHROPIC_API_KEY` |
| `stt-server` | `jarvisd` → VPS | docs/27 §HTTP |
| Hook SDK `PostToolUse`, `Stop`, `Notification` | SDK → `jarvisd` in-process | narator + diff |
