# 21 — Security Rules
Pemilik aturan keamanan & privasi. Aktor & tingkat: docs/05. Skema: docs/07.

## Jaringan & autentikasi
| Kanal | Aturan |
|---|---|
| app ↔ `jarvisd` | WebSocket hanya di `127.0.0.1:8764`. Handshake membawa token sesi lokal acak 32 byte yang ditulis `jarvisd` ke `~/Library/Application Support/FreeJarvis/ws.token` (mode 0600) dan dibaca app; tanpa token → koneksi ditutup (kode: docs/27) |
| `jarvisd` → `stt-server` | HTTPS saja (TLS Caddy), header `Authorization: Bearer <token>`; token di Keychain (`freejarvis.stt`); verifikasi sertifikat wajib |
| `stt-server` | Bandingkan token dengan `hmac.compare_digest`; tolak tanpa Content-Length (411), > 1 MB (413; di bawah ambang spool Starlette 1 MiB agar audio tetap di memori) atau > `STT_MAX_AUDIO_S` (413); rate limit 60 permintaan/menit per token (429); uvicorn hanya di 127.0.0.1 di belakang Caddy |
| Claude | OAuth langganan Max milik Pak Syams; tak pernah disalin ke mesin lain. Bila dibagikan, tiap pemakai login sendiri |

## Persetujuan (penegakan teknis)
- Klasifikasi tingkat di `engine/permissions.py` adalah satu-satunya rumah aturan; diuji per baris docs/05.
- Kode layar dibangkitkan dengan `secrets.choice` dari daftar kata Indonesia ≥ 256 kata × angka 1–99; hanya dikirim ke app dalam `approval.request` dan tidak pernah diucapkan TTS atau dicatat di log.
- Persetujuan terikat pada `pending_prompt.id`; jawaban untuk id yang sudah selesai atau kedaluwarsa diabaikan.
- Berkas di luar `cwd`: path di-resolve (`Path.resolve()`, ikuti symlink) sebelum dibandingkan.

## Privasi data
| Data | Aturan |
|---|---|
| Audio | Tak pernah disimpan. Buffer `stt-server` di memori, dibuang setelah respons. Fallback lokal memakai berkas temp yang dihapus di `finally` |
| Transkrip | SQLite lokal; retensi bawaan 30 hari (`settings.retention_days`); `store/retention.py` menghapus `turns` lebih tua saat startup dan tiap 24 jam |
| Mikrofon | Indikator selalu terlihat di menu bar; tombol bisu menghentikan `AVAudioEngine` input (bukan hanya UI) |
| Rahasia | Tak ada di repo, DB, log, atau `.env` app. `.env` & `*.db` ada di `.gitignore` |
| `ANTHROPIC_API_KEY` | dibuang dari `os.environ` proses (`scrub_billing_env()`) sebelum membuat klien SDK — bukan dari `options.env` (docs/16); `diag sdk` gagal bila masih terlihat |

## Validasi input
- Semua pesan WS divalidasi model pydantic (docs/27); pesan tak valid → `error` + log, tidak diproses.
- `text.input` dari kolom ketik diperlakukan sama dengan ucapan (lewat persetujuan yang sama), panjang maks 8.000 karakter.
- Nama proyek diambil dari daftar `projects`, bukan path bebas dari ucapan.
