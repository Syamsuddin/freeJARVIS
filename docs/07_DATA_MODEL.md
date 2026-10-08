# 07 — Data Model
Sumber kebenaran skema SQLite `jarvisd`. Berkas: `~/Library/Application Support/FreeJarvis/jarvis.db`. Dokumen lain merujuk, tidak menyalin. Migrasi: berkas SQL bernomor di `jarvisd/jarvisd/store/migrations/`, versi di `PRAGMA user_version`. Semua waktu = TEXT ISO-8601 UTC. `PRAGMA foreign_keys=ON`, `journal_mode=WAL`.

## projects
| Kolom | Tipe | Constraint | Catatan |
|---|---|---|---|
| id | INTEGER | PK | |
| name | TEXT | NOT NULL, UNIQUE COLLATE NOCASE | nama ucapan, mis. "sipadi" |
| path | TEXT | NOT NULL, UNIQUE | absolut; `cwd` SDK |
| vocabulary | TEXT | NULL | JSON array; initial prompt STT, dibangun ulang saat proyek dibuka |
| last_session_id | INTEGER | NULL, FK→sessions.id ON DELETE SET NULL | |
| created_at / opened_at | TEXT | NOT NULL / NULL | |

## sessions
| Kolom | Tipe | Constraint | Catatan |
|---|---|---|---|
| id | INTEGER | PK | |
| project_id | INTEGER | NOT NULL, FK→projects.id ON DELETE CASCADE | |
| sdk_session_id | TEXT | NOT NULL, UNIQUE | untuk `resume` |
| started_at / last_active_at | TEXT | NOT NULL | |

## turns
| Kolom | Tipe | Constraint | Catatan |
|---|---|---|---|
| id | INTEGER | PK | |
| session_id | INTEGER | NOT NULL, FK→sessions.id ON DELETE CASCADE | |
| speaker | TEXT | NOT NULL CHECK IN ('user','jarvis') | |
| channel | TEXT | NOT NULL CHECK IN ('voice','text') | `text` = kolom ketik |
| text | TEXT | NOT NULL | hanya transkrip final; sementara tidak disimpan |
| screen_text | TEXT | NULL | bagian layar jawaban Jarvis |
| heard_until | INTEGER | NULL | posisi baca (indeks kalimat) bila disela |
| idempotency_key | TEXT | UNIQUE, NULL | giliran pengguna; cegah perintah ganda |
| created_at | TEXT | NOT NULL | retensi 30 hari (docs/21) |

## jobs
| Kolom | Tipe | Constraint | Catatan |
|---|---|---|---|
| id | INTEGER | PK | |
| session_id | INTEGER | NOT NULL, FK→sessions.id ON DELETE CASCADE | |
| turn_id | INTEGER | NOT NULL, FK→turns.id | giliran pemicu |
| state | TEXT | NOT NULL | nilai = status Pekerjaan docs/06; validasi di `conversation/job_state.py` |
| model | TEXT | NOT NULL | |
| fail_reason | TEXT | NULL | wajib bila `failed` |
| started_at / ended_at | TEXT | NOT NULL / NULL | |

## tool_events
| Kolom | Tipe | Constraint | Catatan |
|---|---|---|---|
| id | INTEGER | PK | |
| job_id | INTEGER | NOT NULL, FK→jobs.id ON DELETE CASCADE | |
| tool | TEXT | NOT NULL | `Edit`, `Bash`, … |
| summary | TEXT | NOT NULL | kalimat narator / ringkasan; sumber jawaban "sudah sampai mana" |
| file_path | TEXT | NULL | |
| tier | TEXT | NOT NULL CHECK IN ('auto','word','phrase','code') | tingkat docs/05 |
| decision | TEXT | NOT NULL CHECK IN ('auto','allowed','denied','expired') | |
| created_at | TEXT | NOT NULL | |

## pending_prompts
| Kolom | Tipe | Constraint | Catatan |
|---|---|---|---|
| id | TEXT | PK | UUID; = `approval.request.id` (docs/27) |
| job_id | INTEGER | NOT NULL, FK→jobs.id ON DELETE CASCADE | |
| kind | TEXT | NOT NULL CHECK IN ('approval','question') | |
| tier | TEXT | NULL CHECK IN ('word','phrase','code') | NULL untuk `question` |
| payload | TEXT | NOT NULL | JSON: alat+input, atau pertanyaan+pilihan |
| expected_phrase | TEXT | NULL | frasa aksi / kode layar; kode layar dihapus (NULL) setelah selesai |
| expires_at | TEXT | NOT NULL | |
| resolution | TEXT | NULL CHECK IN ('allowed','denied','expired','answered') | NULL = masih tertunda |
| answer | TEXT | NULL | |

## quota_snapshots
| Kolom | Tipe | Constraint | Catatan |
|---|---|---|---|
| id | INTEGER | PK | |
| window_remaining_pct | REAL | NULL | jendela 5 jam |
| credit_remaining_pct | REAL | NULL | kredit API bulanan |
| raw | TEXT | NOT NULL | JSON field batas laju `ResultMessage` apa adanya ([TERBUKA]: nama field) |
| created_at | TEXT | NOT NULL | |

## settings
| Kolom | Tipe | Constraint | Catatan |
|---|---|---|---|
| key | TEXT | PK | mis. `retention_days`, `hotkey`, `wake_word`, `tts_voice` |
| value | TEXT | NOT NULL | JSON |

Indeks: `turns(session_id, created_at)`, `turns(created_at)` (pembersihan retensi), `jobs(session_id, started_at)`, `tool_events(job_id, created_at)`, `pending_prompts(resolution)`.
Tak ada data rahasia di DB: token VPS di Keychain, token OAuth dikelola Claude Code (docs/21).
