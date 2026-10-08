# 05 — User Role
Satu pengguna manusia. "Peran" di sini = aktor + tingkat persetujuan. Penegakan teknis: docs/21_SECURITY_RULES.md.

## Aktor
| Aktor | Boleh | Tidak boleh |
|---|---|---|
| Pengguna (Pak Syams) | Semua perintah suara/teks; menyetujui keempat tingkat; mengubah pengaturan | — |
| Claude Code (via SDK) | Alat tingkat Otomatis tanpa tanya; meminta izin lewat `can_use_tool`; bertanya lewat `AskUserQuestion` | Menjalankan alat tingkat ≥ Kata singkat tanpa persetujuan yang sah |
| `jarvisd` | Menjawab status dari peristiwa tersimpan; `interrupt()`; `git status --short` pasca-batal | Mengarang kemajuan; meneruskan pertanyaan status ke model; menyetujui atas nama pengguna |

## Matriks tingkat persetujuan
Persetujuan terikat pada satu tindakan, satu sesi, dan batas waktu. Habis waktu → ditolak.

| Tingkat | Alat / kondisi | Ucapan yang sah | Klik cadangan | Batas waktu |
|---|---|---|---|---|
| Otomatis | `Read`, `Grep`, `Glob`, perintah tes proyek (docs/11) | — (dicatat di log) | — | — |
| Kata singkat | `Edit`, `Write` di dalam `cwd` | "ya", "lanjut"; backchannel saat Jarvis masih bicara diabaikan | Izinkan/Tolak | 60 s |
| Frasa aksi | `git push`, akses jaringan, `Bash` berisi `rm`, berkas di luar `cwd` | Nama tindakan: "izinkan push", "izinkan hapus", "izinkan jaringan", "izinkan luar proyek". "ya" saja diabaikan | Izinkan/Tolak | 120 s |
| Kode layar | `rm -rf`, `push --force`, drop tabel, menyentuh kunci API atau `.env` | Dua kata acak yang tampil hanya di Viewer; Touch ID opsional sebagai pengganti | Touch ID | 120 s |
| (semua) | — | "tolak" / "batal" selalu menolak | Tolak | — |

Aturan klasifikasi: ambil tingkat TERTINGGI yang cocok. Perintah `Bash` yang tak dikenali → Frasa aksi (bukan Otomatis).
