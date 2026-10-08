# 12 — Project Structure
Pemilik struktur & penamaan.

```
freeJARVIS/
├── CLAUDE.md · INDEX.md
├── docs/                         # blueprint 00–27; docs/_design/ = prototipe, logo, dosir asal
├── scripts/                      # validate.sh, token_ledger.py
├── app/                          # Xcode project: FreeJarvis.app
│   ├── FreeJarvis.xcodeproj
│   ├── FreeJarvis/
│   │   ├── App/                  # FreeJarvisApp.swift (MenuBarExtra + jendela), AppState.swift
│   │   ├── Audio/                # AudioEngine.swift (VPIO), LocalVAD.swift, TTSPlayer.swift
│   │   ├── IPC/                  # JarvisClient.swift (WebSocket), Messages.swift (Codable, cermin docs/27)
│   │   ├── UI/Conversation/      # OrbView, StatusPills, TranscriptView, ControlBar, TextInput
│   │   ├── UI/Viewer/            # ViewerView, AnswerTab, ChangesTab, LogTab, QuestionsTab, ProjectSummary
│   │   ├── UI/Components/        # Button, Pill, Card, DiffBlock, CodeBlock, ApprovalCard (docs/26)
│   │   ├── Design/               # Tokens.swift — SATU-SATUNYA rumah nilai warna/ukuran di kode
│   │   └── Resources/            # Assets.xcassets (AppIcon, MenuBarIcon), Fonts/
│   └── FreeJarvisTests/
├── jarvisd/
│   ├── pyproject.toml · .env.example · scripts/install-launchagent.sh
│   ├── jarvisd/
│   │   ├── __main__.py · cli.py · config.py · bench.py · diag.py
│   │   ├── ws/                   # server.py, messages.py (pydantic, cermin docs/27)
│   │   ├── conversation/         # conversation_state.py, job_state.py, interruption.py, turn_detection.py, project_switch.py, orchestrator.py
│   │   ├── engine/               # sdk_client.py, permissions.py (klasifikasi tingkat), hooks.py, narrator.py, model_policy.py, quota.py
│   │   ├── voice/                # vad.py, stt_client.py (STTProvider + fallback), tts_router.py, splitter.py (lisan|layar), phrases.py
│   │   ├── mcp/                  # tahap 2 — kosong di MVP
│   │   └── store/                # db.py, repositories.py, migrations/NNN_nama.sql, migrate.py, retention.py
│   └── tests/                    # cermin struktur paket: tests/conversation/test_*.py, …
└── stt-server/
    ├── pyproject.toml · deploy.sh · stt-server.service · Caddyfile
    ├── stt_server/               # main.py (FastAPI), transcriber.py, auth.py, bench.py
    └── tests/ (+ fixtures/*.wav)
```

## Konvensi
| Hal | Aturan |
|---|---|
| Python | modul `snake_case.py`, kelas `PascalCase`, async di seluruh `jarvisd`; tipe lengkap (mypy strict) |
| Swift | satu tipe per berkas, nama berkas = nama tipe; View berakhiran `View` |
| Pesan protokol | `type` bertitik huruf kecil (`tts.play`); field `snake_case` di kedua sisi (Swift memakai `CodingKeys`) |
| Logika | Semua keputusan (status, tafsir, tingkat izin) di `jarvisd`. Swift hanya menampilkan dan memutar |
| Nilai UI | Hanya dari `Design/Tokens.swift`, yang mencerminkan docs/26 |
| Teks UI & suara | Bahasa Indonesia; kalimat suara tetap Jarvis di `jarvisd/jarvisd/voice/phrases.py` (satu rumah) |
| Migrasi | `NNN_deskripsi.sql`, maju saja; tidak mengedit migrasi yang sudah di-merge |
