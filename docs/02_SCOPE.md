# 02 — Scope
Gerbang anti scope-creep. Permintaan di luar daftar In-scope → berhenti & tanya.

## In-scope (MVP = tahap 0–1)
- Fitur F01–F13 (docs/01_PRD.md).
- Tiga paket monorepo: `app/`, `jarvisd/`, `stt-server/` (docs/12_PROJECT_STRUCTURE.md).
- Satu proyek aktif pada satu waktu; berganti proyek diperbolehkan.
- Protokol antar-proses di docs/27_API_CONTRACT.md.

## Out-of-scope
- **Multi-proyek paralel**: hanya satu `ClaudeSDKClient` aktif.
- **Agen selain Claude Code** (Hermes, OpenClaw, Codex): tidak ada abstraksi multi-agen.
- **Mobile, web, Flutter, Electron**: UI hanya SwiftUI macOS.
- **Multi-pengguna**: tanpa akun, login, atau berbagi token OAuth.
- **Menyimpan audio mentah**, di laptop maupun di VPS.
- **API macOS 26** (SpeechAnalyzer) dan apa pun yang butuh Neural Engine/MLX/CoreML.
- **Tahap 2–3 sebelum gerbangnya**: MCP `:8765`, hook CLI, Channels, kata panggil, TTS cloud (F20–F31). Antarmuka `TTSProvider`/`STTProvider` boleh dibuat; implementasi cloud tidak.

## Asumsi & batasan
- Langganan Claude Max; Agent SDK ditarik dari batas langganan (kebijakan per 8 Okt 2026, dipantau).
- VPS milik sendiri tersedia, ≥ 4 inti CPU.
- Tiga hal masih [TERBUKA] dan diverifikasi di tahap 0 (docs/03_ROADMAP.md, G0).
