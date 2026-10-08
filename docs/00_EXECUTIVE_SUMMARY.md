# 00 — Executive Summary

## Masalah
Mengendalikan Claude Code berarti duduk di depan terminal: mengetik instruksi, membaca keluaran panjang, dan menjawab prompt izin. Pengguna tidak bisa bekerja sambil bicara, menyela di tengah jalan, atau membatalkan dengan cepat.

## Solusi
freeJARVIS adalah aplikasi menu bar macOS untuk bercakap suara full-duplex dengan "Jarvis", satu identitas suara yang menjalankan Claude Code lewat Claude Agent SDK. Mikrofon tetap aktif saat Jarvis bicara, sehingga pengguna bisa menyela, mengoreksi, dan membatalkan kapan saja. Jawaban lisan dibatasi dua kalimat; kode, diff, log, dan pertanyaan tampil di panel Viewer. Persetujuan tindakan berisiko diberikan lewat suara dengan tingkat ucapan yang sebanding dengan risikonya.

## Metrik sukses (gerbang tahap 1, terukur)
| Metrik | Target |
|---|---|
| Barge-in: VAD mendeteksi suara pengguna → audio TTS berhenti | p95 < 300 ms |
| Akhir ucapan → suara pertama Jarvis (giliran ringan) | p50 < 2,5 s |
| 5 skenario acuan (docs/23_ACCEPTANCE_CRITERIA.md, AC-00) | lolos tanpa menyentuh terminal |

## Pengguna sasaran
Satu pengguna: Pak Syams, di MacBook Pro 2019 Intel, berlangganan Claude Max. Untuk pemakaian pribadi.

## Status & cakupan
Greenfield. MVP = tahap 0–1 (docs/03_ROADMAP.md). MCP, Channels, kata panggil, dan TTS cloud menyusul di tahap 2–3.
