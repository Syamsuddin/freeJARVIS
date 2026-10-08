# 22 — Change Policy
Friksi sebanding irreversibilitas. Langkah rilis: docs/25.

## Git
- Satu branch per fitur/perbaikan dari `main` (`feat/…`, `fix/…`, `docs/…`); semua branch selalu di-merge ke `main`, tanpa branch jangka panjang lain. Tak ada commit langsung ke `main`.
- Merge ke `main` oleh Pak Syams setelah DoD (docs/24) terpenuhi.
- Commit kecil, pesan Conventional Commits (`feat(engine): …`). Perubahan protokol & dokumen 27 dalam commit yang sama.
- Blueprint berubah → perbarui dokumen pemilik + `docs/_MANIFEST.json` → `bash scripts/validate.sh`.

## Operasi irreversibel → gerbang manusia (tanya, tunggu "ya" eksplisit)
| Operasi | Prasyarat sebelum minta izin |
|---|---|
| Migrasi skema destruktif (drop/rename kolom/tabel) | backup DB (docs/11), migrasi diuji di salinan |
| Hapus DB / transkrip di luar retensi otomatis | sebut jumlah baris terdampak |
| Deploy `stt-server` ke VPS | tes `stt-server` hijau; versi sebelumnya bisa dikembalikan |
| Perubahan protokol yang breaking (hapus/ubah arti field atau pesan) | bump `protocol_version` docs/27; app & `jarvisd` diperbarui bersamaan |
| Mengubah klasifikasi tingkat persetujuan atau batas waktunya | diff tabel docs/05 ditunjukkan |
| Mengubah daftar terlarang docs/09 atau aturan docs/21 | alasan tertulis |
| Mengerjakan fitur tahap berikut sebelum gerbang (docs/03) | gerbang lolos atau pengecualian dari pengguna |

## Rollback
- Kode: `git revert` commit merge; jangan rewrite history `main`.
- DB: pulihkan berkas backup terakhir (docs/11), lalu turunkan app/`jarvisd` ke versi yang cocok.
- VPS: `deploy.sh` menyimpan rilis sebelumnya di `/opt/stt-server/releases/`; kembalikan symlink `current` + restart.
