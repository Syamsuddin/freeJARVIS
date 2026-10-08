# CLAUDE.md
File ini selalu aktif. Untuk hal di luar ini → buka INDEX.md.

## Proyek
freeJARVIS — percakapan suara full-duplex di macOS untuk mengendalikan Claude Code lewat Agent SDK (satu pengguna). Detail: docs/00_EXECUTIVE_SUMMARY.md. Scope: docs/02_SCOPE.md. Tahap & gerbang: docs/03_ROADMAP.md.

## Prinsip kerja agen (non-negotiable)
1. Friksi sebanding irreversibilitas.
2. Lapisan deterministik (validasi, constraint, tes) di bawah penalaran.
3. Human-in-the-loop untuk high-stakes (migrasi DB, hapus data, keamanan, rilis).
4. Jangan refactor keputusan yang disengaja diam-diam.
5. Hormati scope (docs/02). Out-of-scope → berhenti & tanya.

## Stack  (sumber: docs/09)
`app/` Swift 5.9 + SwiftUI (macOS 13, Intel) · `jarvisd/` Python 3.12 + claude-agent-sdk + SQLite · `stt-server/` FastAPI + faster-whisper (VPS) — Terlarang: Flutter/Electron/web UI, MLX/CoreML, API macOS 26, `ANTHROPIC_API_KEY`.

## Struktur & konvensi  (sumber: docs/12)
Semua logika keputusan di `jarvisd`; Swift hanya audio + UI. Nilai UI hanya dari `Design/Tokens.swift` (docs/26). Protokol antar-proses hanya dari docs/27; rute INDEX "Endpoint/API baru" berarti pesan protokol → tambah docs/27. Kalimat suara tetap di `voice/phrases.py`.

## Perintah penting  (sumber: docs/11)
test: `cd jarvisd && uv run pytest -q` · lint: `cd jarvisd && uv run ruff check . && uv run mypy jarvisd` · app: `xcodebuild … test` (docs/11) · migrasi ⚠️: `cd jarvisd && uv run python -m jarvisd.store.migrate`

## Guardrail inti  (penuh: docs/20, 21, 22)
Jangan pernah pakai `ANTHROPIC_API_KEY` · `jarvisd` hanya 127.0.0.1 · jangan simpan audio · jangan longgarkan tingkat persetujuan · status hanya dari peristiwa SDK · protokol berubah = docs/27 di commit yang sama · deploy VPS/migrasi destruktif = tanya dulu.

## Alur per-task  (penuh: docs/17, 19)
Baca INDEX.md → muat dokumen relevan → konfirmasi scope → vertical slice → tes (docs/13) → DoD (docs/24). Branch per fitur, selalu merge ke `main` (docs/22).

## Definisi selesai (ringkas; penuh: docs/24)
Kriteria docs/23 + blok verifikasinya lulus · suite hijau · lint bersih · angka latensi bila menyentuh audio.

## Untuk apa pun di luar ini → INDEX.md
