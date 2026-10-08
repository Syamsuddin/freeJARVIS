# 14 — Error Handling
Pemilik pola galat. Kalimat suara tetap: `jarvisd/jarvisd/voice/phrases.py`. Log: docs/15.

## Klasifikasi
| Kelas | Contoh | Ke pengguna (suara / layar) | Dicatat | Status |
|---|---|---|---|---|
| STT gagal | VPS timeout, 5xx, TLS | Sekali per putus: "Server suara tak terjangkau, pakai transkripsi lokal." | WARN | percakapan lanjut (fallback) |
| STT lokal juga gagal | binari/model hilang | "Saya tidak bisa mendengar saat ini. Silakan ketik." + kolom ketik difokuskan | ERROR | `idle` |
| SDK / Claude Code | proses mati, login kedaluwarsa | "Claude Code bermasalah: {alasan singkat}." + detail di tab Log | ERROR | job `failed` |
| Jatah habis | batas laju langganan | "Jatah Max habis, tersedia lagi {jam}." | INFO | job `failed` · jatah habis (bukan bug) |
| Izin kedaluwarsa | timeout docs/05 | "Izin kedaluwarsa, tindakan dibatalkan." | INFO | job kembali `running` dengan `deny` |
| Protokol | JSON rusak, `type` tak dikenal, versi beda | app: banner "Koneksi ke jarvisd bermasalah" | ERROR (keduanya) | koneksi ditutup, app reconnect |
| `jarvisd` mati | WS putus | app: pil "jarvisd terputus · menyambung ulang", orb abu | app log | reconnect backoff 0,5→8 s |
| Audio | izin mic ditolak, perangkat hilang | layar: petunjuk System Settings | ERROR | mic nonaktif |
| Proyek | `cwd` hilang / bukan repo git | "Folder proyek tidak ditemukan." | WARN | job `failed` |
| Tak terduga | exception lain di `jarvisd` | "Terjadi galat internal, detail di Log." | ERROR + traceback | job `failed`, daemon tetap hidup |

## Aturan
- Galat di satu job tidak mematikan `jarvisd`: handler puncak di `conversation/orchestrator.py` menangkap, mencatat, dan menandai job `failed` dengan `fail_reason`.
- Pesan suara ≤ 1 kalimat, tanpa traceback, path panjang, atau kode galat mentah. Detail → tab Log.
- Tak ada retry otomatis untuk `query` SDK (bisa menggandakan efek). Retry hanya untuk STT (1×, lalu fallback) dan reconnect WS.
- Galat dikirim ke app sebagai pesan `error` (docs/27), bukan teks bebas.
- Dilarang menelan exception tanpa log; dilarang `except Exception: pass`.
