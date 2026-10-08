# 06 — Business Process
Pemilik alur & dua mesin status. Pesan antar-proses: docs/27_API_CONTRACT.md. Tingkat izin: docs/05_USER_ROLE.md.

## Mesin status
Dua mesin terpisah; app selalu menampilkan keduanya sebagai dua pil. Prioritas: bila bicara bersamaan, pengguna menang.

**Percakapan** (`state.conversation`)
| Status | Label UI | Masuk dari → pemicu |
|---|---|---|
| `idle` | siap | awal; `speaking` selesai; `paused` + "lanjut" |
| `listening` | mendengarkan | PTT ditekan / VAD mulai bicara (dari status mana pun kecuali `paused`) |
| `processing` | memproses | turn detection menyatakan giliran selesai |
| `speaking` | berbicara | `tts.play` pertama dari `jarvisd` |
| `paused` | dijeda | selaan "sebentar"/"tunggu"; TTS dihentikan, pekerjaan tetap jalan |
| `awaiting_reply` | menunggu jawaban / menunggu frasa | prompt tertunda dibacakan |

**Pekerjaan** (`state.job`)
| Status | Label UI | Masuk dari → pemicu |
|---|---|---|
| `idle` | menganggur | awal; setelah status akhir dilaporkan |
| `running` | bekerja · {aktivitas} | `query` dikirim |
| `awaiting_approval` | menunggu izin · {tingkat} | `can_use_tool` untuk alat ≥ Kata singkat, atau `AskUserQuestion` |
| `cancelling` | membatalkan | `interrupt()` dipanggil; BELUM dianggap batal |
| `done` | selesai | `ResultMessage` sukses |
| `cancelled` | dibatalkan | stream benar-benar berhenti setelah `interrupt()` |
| `failed` | gagal · {alasan} | galat SDK, jatah habis, `cwd` hilang |

## Alur A — Giliran instruksi kerja
1. PTT/VAD → `audio.chunk` → potong per ucapan → STT → `transcript.final`.
2. Turn detection selesai → klasifikasi giliran (status / ringan / kerja; model per docs/09).
3. Status → dijawab dari peristiwa tersimpan, selesai. Lainnya → `query` ke `ClaudeSDKClient` dengan `cwd` proyek.
4. Stream: `ToolUseBlock` → narator (≤ 1×/10 s) + Viewer (diff/log); teks → pemisah lisan/layar.
5. `ResultMessage` → jawaban lisan ≤ 2 kalimat + `quota.update`; job `done`.
- Gagal: VPS tak terjangkau → STT fallback lokal + umumkan sekali. Jatah habis → job `failed` beralasan. Pesan ulang dengan `idempotency_key` sama → diabaikan.

## Alur B — Selaan
1. App: VAD lokal mendeteksi suara saat `speaking` → hentikan audio sendiri (≤ 300 ms) → kirim `audio.vad{start}` + `tts.position`.
2. `jarvisd`: buang antrean TTS, tandai kalimat yang sudah terdengar, tunggu transkrip selaan.
3. Tafsir:
| Ucapan | Aksi |
|---|---|
| "sebentar", "tunggu" | Percakapan → `paused`; job tak disentuh |
| "ringkas saja", "intinya" | Potong lisan; sisa ke Viewer |
| "bukan itu, maksud saya …" | `interrupt()` → tunggu berhenti → giliran baru berawalan "Koreksi dari pengguna: …" |
| "batalkan pekerjaan" | Alur C |
| backchannel | Lanjutkan TTS dari posisi baca |
| "iya" saat `awaiting_reply` | Jawaban → Alur D |

## Alur C — Pembatalan
1. `interrupt()` → job `cancelling` → Jarvis tidak bilang "dibatalkan" dulu.
2. Stream berhenti → job `cancelled` → `git status --short` di `cwd` → tab Perubahan → "Dibatalkan. Ada N berkas berubah, lihat di layar."
- Gagal: stream tak berhenti dalam 10 s → tetap `cancelling`, umumkan "masih menghentikan", catat galat (docs/14).

## Alur D — Persetujuan & pertanyaan
1. `can_use_tool(tool, input)` → klasifikasi tingkat (docs/05) → Otomatis: izinkan + log.
2. Lainnya → `PendingPrompt` + `approval.request` → kartu di transkrip & tab Pertanyaan → Jarvis menyebut ucapan yang diharapkan.
3. Ucapan dicocokkan sesuai tingkat → `allow`/`deny` → job kembali `running`.
4. `AskUserQuestion` → pertanyaan dibacakan utuh, pilihan dibacakan bila ≤ 3 → jawaban suara/klik dikembalikan lewat jalur yang sama.
- Gagal: habis waktu → `deny` + "Izin kedaluwarsa, tindakan dibatalkan."; ucapan tidak cocok → ulangi sekali, lalu tetap menunggu.

## Alur E — Buka proyek & resume
"buka proyek X" → cocokkan nama dengan daftar `projects` → `cwd` → `resume=<last_session_id>` bila ada → Viewer kosong menampilkan ringkasan. Nama tak cocok → tampilkan kandidat di Viewer, tanya.
- Berganti proyek saat job `running` → tanya dulu: batalkan atau tunggu.
