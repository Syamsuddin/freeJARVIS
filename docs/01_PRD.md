# 01 — PRD
Pemilik fitur & user story. Kriteria terima: docs/23_ACCEPTANCE_CRITERIA.md. Tahap: docs/03_ROADMAP.md.

## Daftar fitur
| ID | Fitur | Deskripsi | Prioritas |
|---|---|---|---|
| F01 | Push-to-talk | Hotkey global (bawaan ⌥Space) + tombol "Bicara"; tahan untuk bicara | MVP |
| F02 | STT | Potongan ucapan pasca-VAD (2–8 s) ditranskripsi `stt-server` di VPS; fallback `whisper.cpp small` lokal bila VPS putus | MVP |
| F03 | Jawaban suara | TTS `AVSpeechSynthesizer` id-ID; mic tetap aktif selama TTS | MVP |
| F04 | Pemisah lisan/layar | Lisan ≤ 2 kalimat; teks setelah `---layar---`, kode, tabel, log → Viewer | MVP |
| F05 | Interupsi & koreksi | Barge-in VAD lokal; tafsir selaan (jeda, ringkas, koreksi, batal, backchannel) | MVP |
| F06 | Pembatalan | `interrupt()` → batal sah setelah stream berhenti → `git status --short` ke Viewer | MVP |
| F07 | Proyek & sesi | Pilih proyek (`cwd`), lanjutkan sesi (`resume`), ringkasan proyek di Viewer kosong | MVP |
| F08 | Persetujuan berjenjang | 4 tingkat lewat suara (docs/05_USER_ROLE.md), klik sebagai cadangan | MVP |
| F09 | Viewer | Tab Jawaban, Perubahan, Log, Pertanyaan; tombol Bacakan/Salin/Buka di editor; perintah suara Viewer | MVP |
| F10 | Narator status | Peristiwa alat → kalimat pendek ≤ 1×/10 s; pertanyaan status dijawab tanpa model | MVP |
| F11 | Panel jatah | Sisa jendela langganan + kredit API; peringatan suara di 10% | MVP |
| F12 | Kolom ketik | Masukan teks (path, pesan galat) bercampur dengan suara | MVP |
| F13 | Kebijakan model | Sonnet untuk giliran ringan, Opus untuk kerja kode, tanpa model untuk status; "pakai model X" | MVP |
| F20 | MCP server `:8765` + hook CLI | Sesi `claude` di terminal bisa bicara/bertanya lewat Jarvis | Nanti (tahap 2) |
| F21 | Channels | Menyuntik ucapan ke sesi terminal | Nanti (tahap 2, eksperimen) |
| F30 | Kata panggil | openWakeWord "Jarvis" | Nanti (tahap 3) |
| F31 | TTS cloud | Azure Neural id-ID / ElevenLabs lewat `TTSProvider` | Nanti (tahap 3) |

## User story (MVP)
- F01/F02/F03: Sebagai pengguna, saya ingin menahan hotkey lalu bicara agar instruksi sampai ke Claude Code tanpa mengetik.
- F04: Sebagai pengguna, saya ingin jawaban lisan singkat dan detail di layar agar tidak mendengarkan kode dibacakan.
- F05: Sebagai pengguna, saya ingin menyela Jarvis kapan saja agar bisa mengoreksi arah tanpa menunggu.
- F06: Sebagai pengguna, saya ingin berkata "batalkan pekerjaan" agar Claude berhenti dan saya tahu berkas mana yang sudah berubah.
- F07: Sebagai pengguna, saya ingin berkata "buka proyek SIPADI" agar sesi kemarin dilanjutkan di direktori yang benar.
- F08: Sebagai pengguna, saya ingin menyetujui tindakan berisiko dengan suara, dengan ucapan yang makin mahal untuk tindakan yang makin berbahaya.
- F09: Sebagai pengguna, saya ingin melihat diff, log, dan pertanyaan di panel tetap agar tidak kehilangan konteks.
- F10: Sebagai pengguna, saya ingin bertanya "sudah sampai mana?" dan mendapat jawaban jujur dari peristiwa nyata.
- F11/F13: Sebagai pengguna, saya ingin Jarvis hemat jatah Max dan memperingatkan saya sebelum habis.
- F12: Sebagai pengguna, saya ingin menempelkan path atau pesan galat yang sulit diucapkan.

## Kebutuhan non-fungsional
| Aspek | Ketentuan |
|---|---|
| Latensi | Metrik di docs/00_EXECUTIVE_SUMMARY.md |
| Bahasa | UI dan suara Bahasa Indonesia; kode/identifier Inggris |
| Perangkat | MacBook Pro 2019 Intel, tanpa Neural Engine (docs/09_STACK.md) |
| Privasi | docs/21_SECURITY_RULES.md |
| Kejujuran status | Status pekerjaan hanya dari peristiwa SDK; tanpa peristiwa → "masih menunggu laporan" |
