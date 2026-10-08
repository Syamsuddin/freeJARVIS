# 11 — Commands
Satu-satunya rumah perintah. Jalankan dari root repo kecuali disebut lain. ⚠️ = perlu konfirmasi (docs/22).

## jarvisd
| Tujuan | Perintah |
|---|---|
| Sinkron dependensi | `cd jarvisd && uv sync` |
| Jalankan (foreground) | `cd jarvisd && uv run python -m jarvisd` |
| Mode CLI tahap 0 (tanpa app) | `cd jarvisd && uv run python -m jarvisd.cli --project <path>` |
| Tes | `cd jarvisd && uv run pytest -q` |
| Tes satu berkas | `cd jarvisd && uv run pytest -q tests/<berkas>.py` |
| Lint + tipe | `cd jarvisd && uv run ruff check . && uv run ruff format --check . && uv run mypy jarvisd` |
| Migrasi DB ⚠️ | `cd jarvisd && uv run python -m jarvisd.store.migrate` (backup dulu, docs/25) |
| Backup DB | `sqlite3 ~/Library/Application\ Support/FreeJarvis/jarvis.db ".backup '$HOME/FreeJarvis-backup-$(date +%Y%m%d%H%M).db'"` |
| Pasang LaunchAgent | `cd jarvisd && ./scripts/install-launchagent.sh` (menulis `~/Library/LaunchAgents/id.freejarvis.jarvisd.plist`, `launchctl bootstrap gui/$UID …`) |
| Restart daemon | `launchctl kickstart -k gui/$UID/id.freejarvis.jarvisd` |
| Simpan token VPS | `security add-generic-password -s freejarvis.stt -a jarvisd -w` (diminta interaktif) |
| Ukur latensi (otomatis, audio rekaman) | `cd jarvisd && uv run python -m jarvisd.bench latency --runs 50` |
| Rekap latensi dari log (p50/p95) | `cd jarvisd && uv run python -m jarvisd.bench report --since 1d` |
| Uji koneksi SDK | `cd jarvisd && uv run python -m jarvisd.diag sdk` (cek login, tanpa API key, versi SDK) |
| Uji `AskUserQuestion` (G0) | `cd jarvisd && uv run python -m jarvisd.diag ask` |

## app
| Tujuan | Perintah |
|---|---|
| Build | `xcodebuild -project app/FreeJarvis.xcodeproj -scheme FreeJarvis -configuration Debug build` |
| Tes | `xcodebuild -project app/FreeJarvis.xcodeproj -scheme FreeJarvis -destination 'platform=macOS' test` |
| Rilis lokal | `xcodebuild -project app/FreeJarvis.xcodeproj -scheme FreeJarvis -configuration Release -derivedDataPath build` lalu salin `build/Build/Products/Release/FreeJarvis.app` ke `/Applications` |

## stt-server
| Tujuan | Perintah |
|---|---|
| Sinkron | `cd stt-server && uv sync` |
| Jalankan lokal | `cd stt-server && uv run uvicorn stt_server.main:app --host 127.0.0.1 --port 8080` |
| Tes | `cd stt-server && uv run pytest -q` |
| Ukur kecepatan (G0) | `cd stt-server && uv run python -m stt_server.bench --samples tests/fixtures/id-*.wav` (laporkan RTF) |
| Deploy ⚠️ | `cd stt-server && ./deploy.sh <host>` (rsync → `uv sync` → `systemctl restart stt-server`) |
| Smoke test VPS | `curl -fsS -H "Authorization: Bearer $TOKEN" -F audio=@tests/fixtures/id-halo.wav https://<host>/transcribe` |
| Log VPS | `ssh <host> journalctl -u stt-server -n 100 --no-pager` |

## Paket blueprint
| Tujuan | Perintah |
|---|---|
| Validasi blueprint | `bash scripts/validate.sh` |
