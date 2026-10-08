# 04 — Domain Model
Pemilik istilah & entitas konseptual. Skema fisik: docs/07_DATA_MODEL.md.

## Glosarium
| Istilah | Makna |
|---|---|
| Jarvis | Identitas suara aplikasi; juga kata panggil bawaan (bisa diganti, tahap 3) |
| Percakapan | Lapisan suara: mendengar, memproses, berbicara. Mesin statusnya terpisah dari Pekerjaan (docs/06) |
| Pekerjaan (Job) | Satu eksekusi Claude Code yang dipicu sebuah giliran instruksi kerja, dari `query` sampai `ResultMessage`/interrupt/gagal |
| Giliran (Turn) | Satu ucapan final pengguna, atau satu jawaban Jarvis. Membawa `idempotency_key` |
| Ucapan sementara | Transkrip parsial; hanya indikator layar, tak pernah memicu perintah |
| Turn detection | Keputusan bahwa pengguna selesai bicara: jeda adaptif ~700 ms, lebih lama bila ucapan menggantung ("terus…", "dan…") |
| Barge-in / selaan | Pengguna bicara saat TTS berbunyi. Keputusan berhenti diambil app (VAD lokal); tafsir maksud oleh `jarvisd` |
| Backchannel | "iya", "hmm", "oke" saat Jarvis bicara: tidak mengakhiri giliran Jarvis, bukan persetujuan |
| Posisi baca | Indeks kalimat TTS yang sudah terdengar saat disela |
| Lisan / layar | Dua keluaran jawaban: lisan ≤ 2 kalimat; layar = Viewer. Penanda pemisah dari model: `---layar---` |
| Narator | Komponen `jarvisd` yang mengubah peristiwa alat menjadi kalimat status pendek, tanpa token model |
| Viewer | Panel kanan tetap; 4 tab: Jawaban, Perubahan, Log, Pertanyaan |
| Tingkat persetujuan | Otomatis, Kata singkat, Frasa aksi, Kode layar (docs/05) |
| Frasa aksi | Ucapan yang menyebut nama tindakan, mis. "izinkan push" |
| Kode layar | Dua kata acak yang hanya tampil di Viewer, mis. "merpati tujuh" |
| Prompt tertunda | Pertanyaan `AskUserQuestion` atau permintaan izin `can_use_tool` yang menunggu jawaban |
| Jatah | Sisa jendela 5 jam langganan Max + sisa kredit API bulanan |
| Proyek | Direktori kerja (`cwd`) Claude Code; satu aktif sekaligus |
| Sesi | Sesi Agent SDK (`session_id`) yang bisa di-`resume` |

## Entitas & relasi konseptual
- Proyek 1—N Sesi; Proyek menyimpan sesi terakhir untuk "lanjutkan".
- Sesi 1—N Giliran; Sesi 1—N Pekerjaan.
- Pekerjaan 1—N Peristiwa alat (ToolEvent); Pekerjaan 1—N Prompt tertunda.
- Cuplikan jatah (QuotaSnapshot) dan Pengaturan berdiri sendiri.
