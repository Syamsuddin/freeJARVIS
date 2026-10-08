# 15 — Observability
Pemilik logging & metrik.

## Log
| Sumber | Lokasi | Format |
|---|---|---|
| `jarvisd` | `~/Library/Logs/FreeJarvis/jarvisd.log` (rotasi 5 × 10 MB) + stderr saat foreground | JSON per baris: `ts`, `level`, `component`, `event`, `job_id?`, `turn_id?`, `ms?` |
| `app` | `os.Logger` subsystem `id.freejarvis.app` (Console.app) | kategori `audio`, `ipc`, `ui` |
| `stt-server` | journald `stt-server` | JSON per baris: `ts`, `level`, `audio_s`, `infer_ms`, `model` |

Level: DEBUG (alur rinci, mati bawaan) · INFO (transisi status, keputusan izin) · WARN (fallback, retry) · ERROR (docs/14).

## Wajib dicatat
- Tiap transisi dua mesin status (`event=state`, dari→ke, pemicu).
- Tiap keputusan izin: alat, tingkat, keputusan, lama menunggu (TANPA kode layar).
- Latensi per giliran: `vad_to_stop_ms` (dilaporkan app), `eos_to_stt_ms`, `stt_ms`, `stt_to_first_tts_ms`.
- Peristiwa `ResultMessage`: model, durasi, biaya/batas laju mentah.

## Dilarang dicatat
Audio; isi transkrip pada level di atas DEBUG; token; isi `.env`; kode layar; input alat `Edit`/`Write` (cukup path).

## Metrik
Tanpa server metrik. perintah "Rekap latensi" (docs/11) membaca log dan mencetak p50/p95 latensi di atas — inilah sumber angka gerbang G1. Dasbor: [TERBUKA], pasca-MVP.
