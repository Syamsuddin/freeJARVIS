# 20 — Guardrails
Larangan operasional keras untuk agen. Aturan keamanan rinci: docs/21. Gerbang manusia: docs/22.

JANGAN:
1. Menyetel, membaca, atau menambahkan `ANTHROPIC_API_KEY` di mana pun pada `jarvisd`.
2. Membuat `jarvisd` mendengarkan selain `127.0.0.1`, atau membuka port baru tanpa lewat docs/22.
3. Menyimpan audio ke disk, di laptop maupun di VPS, termasuk untuk debug.
4. Menurunkan tingkat persetujuan alat, menghapus batas waktu izin, atau menerima "ya" untuk Frasa aksi/Kode layar.
5. Mengizinkan aksi atas dasar transkrip sementara atau backchannel.
6. Membuat Jarvis melaporkan kemajuan yang tidak berasal dari peristiwa SDK.
7. Menambah pesan/field protokol di kode tanpa memperbarui docs/27 di commit yang sama.
8. Menulis nilai warna/ukuran/font di luar `Design/Tokens.swift` (docs/26).
9. Mengubah `~/.claude/settings.json` atau `.claude/` proyek pengguna; hook hanya lewat opsi SDK.
10. Menambah dependensi tanpa alasan tertulis di pesan commit; dependensi di daftar terlarang docs/09 tidak boleh sama sekali.
11. Memindahkan logika keputusan ke Swift.
12. Menjalankan deploy VPS, migrasi destruktif, atau menghapus DB tanpa konfirmasi (docs/22).
13. Mengerjakan fitur tahap 2–3 sebelum gerbangnya (docs/03).
