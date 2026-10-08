# 18 — Repair Rules
Pemilik aturan perbaikan bug. Jebakan yang sering menjadi akar masalah: docs/16.

## Alur
1. **Reproduksi** dengan tes yang gagal (docs/13). Untuk bug suara/latensi: rekam ulang dengan `jarvisd.bench` atau fixture WAV, bukan "coba bicara lagi".
2. **Akar masalah**: sebutkan berkas + baris + kenapa. Bedakan lapisan: app (audio/UI), `jarvisd` (logika), VPS, SDK.
3. **Perbaikan minimal** di lapisan yang salah. Bug logika diperbaiki di Python, bukan ditambal di Swift.
4. **Tes regresi** hijau + seluruh suite paket terkait hijau.
5. Bug akibat skema → rute "Ubah skema DB" (INDEX), bukan menambal data.

## Larangan
- Perbaikan tidak melebar di luar scope bug; refactor terpisah, dengan izin.
- Dilarang "memperbaiki" dengan melonggarkan tingkat persetujuan, menonaktifkan narator throttle, menaikkan timeout tanpa ukur, atau menambahkan `ANTHROPIC_API_KEY`.
- Dilarang menghapus/men-skip tes yang gagal agar hijau.
- Bug latensi: tanpa angka sebelum/sesudah, perbaikan tidak dianggap selesai.
