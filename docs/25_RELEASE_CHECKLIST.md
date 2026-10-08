# 25 — Release Checklist
Rilis = memasang versi baru di laptop (app + `jarvisd`) dan/atau VPS (`stt-server`). Berurutan; berhenti di langkah pertama yang gagal. Perintah: docs/11. Rollback: docs/22.

| # | Langkah | Lulus bila |
|---|---|---|
| 1 | Tes & lint semua paket yang berubah | exit 0 semua |
| 2 | `protocol_version` app == `jarvisd` (bila protokol berubah) | `pytest tests/ws/test_protocol.py` + XCTest decode hijau |
| 3 | Backup DB | berkas `FreeJarvis-backup-*.db` ada, `sqlite3 <berkas> "PRAGMA integrity_check"` → `ok` |
| 4 | Migrasi ⚠️ (bila ada) pada salinan DB lalu DB asli | `PRAGMA user_version` = nomor migrasi terakhir |
| 5 | Deploy `stt-server` ⚠️ (bila berubah) | smoke test `curl … /transcribe` mengembalikan teks; `GET /healthz` `ok` |
| 6 | Pasang `jarvisd` + restart LaunchAgent | `launchctl print gui/$UID/id.freejarvis.jarvisd` → `state = running`; `diag sdk` lulus |
| 7 | Build Release app → `/Applications` | app terbuka, `hello.ack` diterima (pil tidak "terputus") |
| 8 | Smoke test suara | AC-00 #1, #3, #5 (docs/23) lolos |
| 9 | Tag `vX.Y.Z` di `main` | tag terdorong |
Gagal di 5–8 → rollback sesuai docs/22, lalu catat di tab Log/issue.
